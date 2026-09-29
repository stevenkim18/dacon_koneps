#!/usr/bin/env python3
"""클라우드 int8 원본 출력으로 '규칙 판정기'와 'LLM 직접 판정'의 항목별 조합을 고른다(GPU 불필요).

입력: `cloud/run_exp.sh`가 저장한 raw 폴더(main·item·model·sme·region·perf·goods·judge·judge_rag .jsonl).
비교하는 판정원:
  rule        제출 후보 판정기(본·품목·모델명·기업규모·지역 호출)
  rule+perf   + 실적 전용 호출            rule+goods  + 물품 품목 호출
  judge       LLM 직접 판정                judge_rag   LLM 직접 판정 + 비슷한 dev 사례 2건(자기 자신 제외)
  or·and      rule과 judge(또는 judge_rag)의 항목별 OR·AND
출력:
  1) dev 200 항목별 F1(판정원별)과 macro
  2) 항목별 선택의 교차검증(dev 절반에서 고르고 다른 절반에서 채점, 양방향 평균) — 선택 낙관을 뺀 값
  3) 무라벨 750: 판정원별 양성 수, 규칙 대비 새 양성, 손라벨(항목 단위) 쌍의 정밀도

  python scripts/judge_combine.py --raw runs/cloud_int8_exp/raw [--script cloud/script_dump.py]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = [f"v{i}" for i in range(1, 25)]
LABEL_FILES = [  # 항목 단위(id, 항목, 라벨) 손라벨만. 사실 단위 라벨은 쓰지 않는다.
    ("labels/train500_audit.csv", "item", "label"), ("labels/train250_audit.csv", "item", "label"),
    ("labels/train750_region_call.csv", "항목", "라벨"), ("labels/train250_sme_call.csv", "항목", "라벨"),
]


def load_mod(path: Path):
    spec = importlib.util.spec_from_file_location("cand", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read_raw(d: Path, name: str) -> dict:
    p = d / f"{name}.jsonl"
    if not p.exists():
        return {}
    return {json.loads(l)["id"]: json.loads(l)["text"] for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}


def f1(labels, preds, ids, v):
    tp = sum(1 for i in ids if labels[i][v] and preds[i][v])
    fp = sum(1 for i in ids if not labels[i][v] and preds[i][v])
    fn = sum(1 for i in ids if labels[i][v] and not preds[i][v])
    return (2 * tp / (2 * tp + fp + fn) if tp else 0.0), tp, fp, fn


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--script", default=str(ROOT / "cloud" / "script_dump.py"))
    ap.add_argument("--input", default=str(ROOT / "open" / "exp950.jsonl.gz"))
    a = ap.parse_args()
    raw = Path(a.raw)
    m = load_mod(Path(a.script))
    ev = load_mod(ROOT / "scripts" / "mlx_eval_extract.py")
    table = m.load_competitive_table(str(ROOT / "open" / "data"))
    m._TABLE_CACHE.update(table)
    with gzip.open(a.input, "rt", encoding="utf-8") as f:
        recs = [json.loads(l) for l in f]
    labels = ev.load_labels(ROOT / "open" / "dev_labels.csv")
    dev_ids = [r["id"] for r in recs if r["id"] in labels]
    unl_ids = [r["id"] for r in recs if r["id"] not in labels]

    R = {n: read_raw(raw, n) for n in ("main", "item", "model", "sme", "region", "perf", "goods", "judge", "judge_rag")}
    print("원본 출력 건수:", {n: len(x) for n, x in R.items()})

    orig_perf, orig_goods = m.needs_perf_call, m.needs_goods_item_call

    def rule_preds(use_perf=False, use_goods=False):
        # 기각된 호출은 apply_* 안에서도 needs_*로 막혀 있으므로, 실험 판정원에서만 게이트를 연다.
        m.needs_perf_call = (lambda r: True) if use_perf else orig_perf
        m.needs_goods_item_call = ((lambda r: m.is_goods(r) and not any(c in table for c in m.codes_in_record(r)))
                                   if use_goods else orig_goods)
        out = {}
        for r in recs:
            i = r["id"]
            out[i] = m.decide(r, R["main"].get(i, ""), table, item_text=R["item"].get(i, ""),
                              model_text=R["model"].get(i, ""), sme_text=R["sme"].get(i, ""),
                              perf_text=R["perf"].get(i, "") if use_perf else "",
                              region_text=R["region"].get(i, ""),
                              goods_text=R["goods"].get(i, "") if use_goods else "")[0]
        m.needs_perf_call, m.needs_goods_item_call = orig_perf, orig_goods
        return out

    def judge_preds(name):
        out, bad = {}, 0
        for r in recs:
            j = m.parse_facts(R[name].get(r["id"], "")) if R[name] else None
            bad += j is None
            out[r["id"]] = {v: int(bool((j or {}).get(v))) for v in ITEMS}
        return out, bad

    src = {"rule": rule_preds()}
    if R["perf"]:
        src["rule+perf"] = rule_preds(use_perf=True)
    if R["goods"]:
        src["rule+goods"] = rule_preds(use_goods=True)
    for jn in ("judge", "judge_rag"):
        if R[jn]:
            src[jn], bad = judge_preds(jn)
            print(f"{jn}: 파싱 실패 {bad}건")
            src[f"or({jn})"] = {i: {v: int(src["rule"][i][v] or src[jn][i][v]) for v in ITEMS} for i in src["rule"]}
            src[f"and({jn})"] = {i: {v: int(src["rule"][i][v] and src[jn][i][v]) for v in ITEMS} for i in src["rule"]}
    names = list(src)

    # 1) dev 항목별
    print(f"\n== dev {len(dev_ids)}건 항목별 F1 (TP/FP/FN) ==")
    print("item  " + "".join(f"{n:>18}" for n in names))
    macro = defaultdict(float)
    for v in ITEMS:
        cells = []
        for n in names:
            s, tp, fp, fn = f1(labels, src[n], dev_ids, v)
            macro[n] += s / len(ITEMS)
            cells.append(f"{s:.3f}({tp}/{fp}/{fn})")
        print(f"{v:<5} " + "".join(f"{c:>18}" for c in cells))
    print("macro " + "".join(f"{macro[n]:>18.4f}" for n in names))

    # 2) 항목별 선택의 교차검증
    fa, fb = ev.split_half(labels, dev_ids)
    for pool_name, pool in (("rule 계열만", [n for n in names if n.startswith("rule")]), ("전체", names)):
        scores = []
        for tune, test in ((fa, fb), (fb, fa)):
            chosen = {v: max(pool, key=lambda n: (f1(labels, src[n], tune, v)[0], n == "rule")) for v in ITEMS}
            scores.append(sum(f1(labels, src[chosen[v]], test, v)[0] for v in ITEMS) / len(ITEMS))
        full = {v: max(pool, key=lambda n: (f1(labels, src[n], dev_ids, v)[0], n == "rule")) for v in ITEMS}
        print(f"\n교차검증[{pool_name}] {sum(scores) / 2:.4f} (A→B {scores[0]:.4f} · B→A {scores[1]:.4f})")
        print("  dev 전체로 고른 항목별 판정원: " + ", ".join(f"{v}={full[v]}" for v in ITEMS if full[v] != "rule"))

    # 2-1) 판정 변형별 JUDGE_POLICY 제안(제출 후보 submissions/20260924_judge_combo에 붙여 넣는다)
    for jn in ("judge", "judge_rag"):
        if jn not in src:
            continue
        opts = {"rule": "rule", jn: "judge", f"or({jn})": "or", f"and({jn})": "and"}
        pool = list(opts)
        scores = []
        for tune, test in ((fa, fb), (fb, fa)):
            chosen = {v: max(pool, key=lambda n: (f1(labels, src[n], tune, v)[0], n == "rule")) for v in ITEMS}
            scores.append(sum(f1(labels, src[chosen[v]], test, v)[0] for v in ITEMS) / len(ITEMS))
        full = {v: max(pool, key=lambda n: (f1(labels, src[n], dev_ids, v)[0], n == "rule")) for v in ITEMS}
        dev_macro = sum(f1(labels, src[full[v]], dev_ids, v)[0] for v in ITEMS) / len(ITEMS)
        policy = {v: opts[full[v]] for v in ITEMS}
        print(f"\n[{jn}] 교차검증 {sum(scores) / 2:.4f} · dev 전체 선택 {dev_macro:.4f}")
        print(f'JUDGE_VARIANT = "{"rag" if jn == "judge_rag" else "plain"}"')
        print("JUDGE_POLICY = " + json.dumps(policy, ensure_ascii=False))

    # 3) 무라벨 750
    hand = {}
    for path, kc, lc in LABEL_FILES:
        p = ROOT / path
        if p.exists():
            for row in csv.DictReader(open(p, encoding="utf-8")):
                if row.get(lc) in ("0", "1"):
                    hand[(row["id"], row[kc])] = int(row[lc])
    print(f"\n== 무라벨 {len(unl_ids)}건 · 손라벨 쌍 {sum(1 for k in hand if k[0] in set(unl_ids))} ==")
    base = src["rule"]
    print(f"{'판정원':<16}{'양성':>7}{'규칙 대비 +':>12}{'-':>6}{'  손라벨 쌍 정밀도(맞음/라벨있음)':>30}")
    for n in names:
        pos = sum(src[n][i][v] for i in unl_ids for v in ITEMS)
        add = sum(1 for i in unl_ids for v in ITEMS if src[n][i][v] and not base[i][v])
        rem = sum(1 for i in unl_ids for v in ITEMS if base[i][v] and not src[n][i][v])
        lab = [(hand[(i, v)]) for i in unl_ids for v in ITEMS if src[n][i][v] and (i, v) in hand]
        newlab = [(hand[(i, v)]) for i in unl_ids for v in ITEMS
                  if src[n][i][v] and not base[i][v] and (i, v) in hand]
        print(f"{n:<16}{pos:>7}{add:>12}{rem:>6}   전체 {sum(lab)}/{len(lab)} · 새 양성 {sum(newlab)}/{len(newlab)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
