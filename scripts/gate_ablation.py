#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""판정기의 억제 조건(AND 게이트)을 하나씩 꺼서 양성이 얼마나 늘어나는지 잰다.

F1/2 정리: 새 탐지의 정밀도가 `현재 F1/2`(0.684 기준 **0.342**)를 넘으면 F1은 오른다.
게이트는 대부분 dev 오탐 1~2건을 없애려고 붙인 것이고, 그 대가로 평가셋에서 얼마나 많은 정탐을
죽이는지는 잰 적이 없다. 이 스크립트는 **대가의 크기**를 먼저 재고, 큰 것부터 손라벨로 정밀도를 확인한다.

  python scripts/gate_ablation.py --limit 3000          # 표본으로 빠르게
  python scripts/gate_ablation.py                       # 무라벨 20,000건 전수
"""
from __future__ import annotations
import argparse, gzip, importlib.util, io, json, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "submissions" / "20260922_focused_calls" / "script.py"
ITEMS = [f"v{i}" for i in range(1, 25)]

# (이름, 원문, 치환문, 영향 항목) — judge()와 게이트 함수의 문자열 치환으로 만든다.
ABLATIONS = [
    ("G1 소액수의 게이트",        'and not small_quote', 'and True', "v2·v6·v7·v8"),
    ("G2 수의계약 게이트",        'private_contract = _meta_method(rec) == "수의계약"',
                                  'private_contract = False', "v10~v18"),
    ("G3 우선조달 예외 면책",     'absence_exception = exception or meta_exception(rec)',
                                  'absence_exception = False', "v16·v18"),
    ("G4 제7조 경쟁입찰 예외",    'comp_bid = (comp and not competitive_exempt(rec)',
                                  'comp_bid = (comp and True', "v10·v11·v13"),
    ("G5 고시 '…에 한함' 조건",   'and note_condition_met(rec, table.get(str(facts.get("계약목적물_세부품명번호") or "")) or {}))',
                                  'and True)', "v10·v11·v13"),
    ("G6 금액 유효성(100만원)",   'priced = p >= 1_000_000', 'priced = p > 0', "금액 구간 전체"),
    ("G7 v1 근거 필수",           'v["v1"] = int(bool(facts.get("특정기관_한정")) and bool(v1_ev))',
                                  'v["v1"] = int(bool(facts.get("특정기관_한정")))', "v1"),
    ("G8 v9 '동등' 필터",         'and "동등" not in str(facts.get("특정모델_근거") or ""))', 'and True)', "v9"),
    ("G9 v9·v19 물품 한정",       'v["v9"] = int(is_goods(rec) and', 'v["v9"] = int(True and', "v9"),
    ("G10 v19 근거 3중 조건",     'and "확약" in commit_ev', 'and True', "v19"),
    ("G11 v20 SW 한정",           'v["v20"] = int(is_software(rec) and', 'v["v20"] = int(True and', "v20"),
    ("G12 v20 1억 하한",          'v["v20"] = int(is_software(rec) and priced and p >= ONE_HUNDRED_MILLION',
                                  'v["v20"] = int(is_software(rec) and priced and p >= 0', "v20"),
    ("G13 v22 협상 한정",         'v["v22"] = int(is_negotiation(rec) and', 'v["v22"] = int(True and', "v22"),
    ("G14 v12 비경쟁제품 한정",   'v["v12"] = int(bool(facts.get("직접생산확인_요구")) and not comp)',
                                  'v["v12"] = int(bool(facts.get("직접생산확인_요구")))', "v12"),
    ("G15 v10 직생 넓은 탐지",    'and not facts.get("직접생산_언급_넓게"))', 'and True)', "v10"),
]


def load(path: Path, name: str, subs=()):
    src = io.open(path, encoding="utf-8").read()
    for old, new in subs:
        if old not in src:
            raise SystemExit(f"[gate_ablation] 치환 실패: {name} — {old[:60]!r}")
        src = src.replace(old, new, 1)
    tmp = ROOT / ".gate_tmp.py"
    io.open(tmp, "w", encoding="utf-8").write(src)
    spec = importlib.util.spec_from_file_location(f"abl_{name}", tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tmp.unlink(missing_ok=True)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--data", default=str(ROOT / "open" / "train_unlabeled.jsonl.gz"))
    a = ap.parse_args()

    base = load(BASE, "base")
    tbl = base.load_competitive_table(str(ROOT / "open" / "data"))
    variants = [("기준", base, "")]
    for name, old, new, items in ABLATIONS:
        variants.append((name, load(BASE, name, [(old, new)]), items))

    recs = []
    with gzip.open(a.data, "rt", encoding="utf-8") as f:
        for n, line in enumerate(f):
            if a.limit and n >= a.limit:
                break
            recs.append(json.loads(line))
    print(f"[gate_ablation] 대상 {len(recs):,}건", file=sys.stderr)

    t0 = time.time()
    counts = {name: {v: 0 for v in ITEMS} for name, _, _ in variants}
    for rec in recs:
        for name, mod, _ in variants:
            try:
                h = mod.decide(rec, "", tbl)[0]
            except Exception:
                continue
            for v in ITEMS:
                counts[name][v] += h[v]
    base_tot = sum(counts["기준"].values())
    print(f"\n기준 양성 {base_tot:,}건 ({len(recs):,}건 기준) · {time.time()-t0:.0f}s\n")
    print(f"{'게이트':24}{'Δ양성':>8}{'1,853환산':>10}{'ΔPublic 추정':>13}  바뀌는 항목")
    rows = []
    for name, mod, items in variants[1:]:
        d = sum(counts[name].values()) - base_tot
        rows.append((d, name, items, counts[name]))
    for d, name, items, c in sorted(rows, key=lambda x: -x[0]):
        scaled = d / len(recs) * 1853
        est = d / len(recs) * 20000 * 2.9e-5      # 20,000건 환산 × 실측 기울기
        per = ", ".join(f"{v}{c[v]-counts['기준'][v]:+d}" for v in ITEMS if c[v] != counts["기준"][v])
        print(f"{name:24}{d:>+8}{scaled:>+10.0f}{est:>+13.4f}  {per}")
    print("\nΔPublic 추정 = 20,000건 환산 Δ양성 × 2.9e-5 (실측 기울기). **정밀도 0.8~0.9 가정이므로")
    print("실제로는 새 탐지를 손라벨해 정밀도가 0.34를 넘는지 확인해야 한다.**")
    return 0


if __name__ == "__main__":
    sys.exit(main())
