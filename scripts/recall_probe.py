#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""누락(FN) 후보를 뽑는다 — 우리가 '아니다'라고 판정한 공고에서 넓은 그물이 근거 문장을 찾은 건.

지금까지의 검토 도구(`scripts/audit_unlabeled.py`)는 **우리가 양성이라 한 쌍만** 사람에게 보여 준다.
즉 정밀도만 잰다. 정탐을 꺼 버리면 그 공고는 목록에서 사라져 재현율 손실이 측정에 잡히지 않는다
(docs/05_study_log/20260920/1). 이 스크립트는 반대쪽을 본다.

  사실별로 ① 판정기가 쓴 값이 음성/없음이고 ② 넓은 정규식 그물이 후보 문장을 찾은 공고
  → 사람(또는 외부 LLM)이 원문과 법 조문으로 라벨할 대상

사용법
  python scripts/recall_probe.py --report            # 집계만
  python scripts/recall_probe.py --out runs/mlx/recall_candidates.txt --per-family 12
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
# 원래 기본값 20260921_full_context는 이름이 바뀌어 없다 → 그 후보를 이어 제출한 recall_first를 쓴다
DEFAULT_SCRIPT = ROOT / "submissions" / "20260921_recall_first" / "script.py"


def log(msg: str) -> None:
    print(f"[recall_probe] {msg}", file=sys.stderr, flush=True)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("cand", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_jsonl_text(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        out[row["id"]] = row["text"]
    return out


# 넓은 그물. 판정 규칙이 쓰는 좁은 정규식과 달리 "이 사실을 말하는 문장일 수 있다"만 본다.
# 여기 걸렸는데 판정기가 음성이면, 판정기가 틀렸거나 그물이 과하게 넓은 것이다 — 라벨로 가른다.
NETS: List[Tuple[str, str, str, List[str]]] = [
    # (사실 키, 기대 음성값, 넓은 그물, 좌우하는 항목)
    ("실적제한", "False",
     r"(실적|납품\s*경험|수행\s*경험)[^\n]{0,60}?(있는|보유|이상|충족|요구|제출|한함|한정|갖춘|증명)",
     ["v2", "v3", "v4", "v8"]),
    ("지역제한", "False",
     r"(본점|주된\s*영업소|본사|소재지|관내|역내)[^\n]{0,40}?(소재|위치|등록|둔|있는|한함|한정|제한)",
     ["v5", "v6", "v7", "v8"]),
    ("특정기관_한정", "False",
     r"(대학|산학협력단|연구원|협회|조합|재단|학교|기관|단체|법인)[^\n]{0,30}?"
     r"(만\s*참여|만\s*참가|에\s*한하|에\s*한함|으로\s*한정|이어야)",
     ["v1"]),
    ("특정모델_지정", "False",
     r"(모델명?|제조사|제작사|상표|브랜드|품번|규격)\s*[:：]\s*\S|[A-Z]{2,}[-\s]?\d{2,}",
     ["v9"]),
    ("확약서_입찰시제출", "False",
     r"(확약서|공급\s*확인서|공급\s*증명|기술지원\s*확약)[^\n]{0,40}?(제출|보유|소지|첨부|구비)",
     ["v19"]),
    ("설명회_미참석_참가불가", "False",
     r"설명회[^\n]{0,60}?(참석|참가)[^\n]{0,30}?(한하|만|자격|필수|의무)",
     ["v22"]),
    ("기업규모_제한", "없음",
     r"(중소기업|소기업|소상공인|중기업)[^\n]{0,40}?(한함|한정|제한|이어야|만\s*참|참가\s*자격|대상)",
     ["v13", "v14", "v15", "v17"]),
    ("직접생산확인_요구", "False",
     r"직접\s*생산[^\n]{0,40}?(증명서|확인서)[^\n]{0,30}?(소지|보유|제출|요구|필요)",
     ["v12"]),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=str(DEFAULT_SCRIPT))
    ap.add_argument("--data-dir", default=str(ROOT / "open" / "data"))
    ap.add_argument("--samples", nargs="+", default=[
        str(ROOT / "runs" / "mlx" / "train_sample250.jsonl"),
        str(ROOT / "runs" / "mlx" / "train_sample500_next.jsonl")])
    ap.add_argument("--mains", nargs="+", default=[
        str(ROOT / "runs" / "mlx" / "train250_main.jsonl"),
        str(ROOT / "runs" / "mlx" / "train500_main.jsonl")])
    ap.add_argument("--models", nargs="+", default=[
        str(ROOT / "runs" / "mlx" / "train250_model.jsonl"),
        str(ROOT / "runs" / "mlx" / "train500_model.jsonl")])
    ap.add_argument("--out", default=None, help="검토 자료 저장 경로")
    ap.add_argument("--per-family", type=int, default=10, help="사실별로 검토 자료에 넣을 공고 수")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    mod = load_module(Path(a.script))
    table = mod.load_competitive_table(a.data_dir)
    recs: List[dict] = []
    for p in a.samples:
        recs += [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines()]
    mains: Dict[str, str] = {}
    for p in a.mains:
        mains.update(load_jsonl_text(Path(p)))
    models: Dict[str, str] = {}
    for p in a.models:
        models.update(load_jsonl_text(Path(p)))
    recs = [r for r in recs if r["id"] in mains]
    log(f"대상 {len(recs)}건 (저장된 본 호출 출력 기준)")

    # 판정기가 실제로 쓴 사실값을 항목별 출처(ITEM_SOURCE)에 맞춰 재구성한다.
    def used_facts(rec: dict) -> Dict[str, Dict[str, object]]:
        llm = mod.parse_facts(mains.get(rec["id"], ""))
        md = models.get(rec["id"], "")
        if md:
            llm = mod.apply_model_call(rec, llm, md)
        rx = mod.regex_facts(rec, table)
        if llm is not None:
            llm = dict(llm, 우선조달_예외사유_기재=rx["우선조달_예외사유_기재"])
        return {mode: mod.merge_facts(llm, rx, {k: mode for k in mod.FACT_KEYS})
                for mode in set(mod.ITEM_SOURCE.values())}

    hits: Dict[str, List[Tuple[str, str]]] = {k: [] for k, _, _, _ in NETS}
    totals = {k: 0 for k, _, _, _ in NETS}
    for rec in recs:
        by_mode = used_facts(rec)
        src = mod.full_text(rec)
        for key, neg, pat, items in NETS:
            # 그 사실을 쓰는 항목들의 출처 중 하나라도 양성이면 '우리가 잡은 것'으로 본다
            caught = False
            for v in items:
                val = by_mode[mod.ITEM_SOURCE[v]].get(key)
                if (neg == "없음" and val not in (None, "없음")) or (neg == "False" and bool(val)):
                    caught = True
                    break
            if caught:
                continue
            totals[key] += 1
            m = re.search(pat, src)
            if m:
                line = next((ln.strip() for ln in src.split("\n") if m.group(0)[:30] in ln), m.group(0))
                hits[key].append((rec["id"], line[:220]))

    print(f"\n{'사실':22}{'음성 판정':>10}{'그물 적발':>10}{'적발률':>8}  좌우 항목")
    for key, neg, _, items in NETS:
        n = len(hits[key])
        t = max(totals[key], 1)
        print(f"{key:22}{totals[key]:>10}{n:>10}{n / t:>8.1%}  {','.join(items)}")
    print("\n적발률이 높을수록 '우리가 아니라고 한 공고에 근거 문장이 있다'는 뜻이다 —")
    print("그물이 과한지 판정기가 놓친 것인지는 라벨로만 가른다. F1/2 정리상 라벨 정밀도가 0.34를 넘으면 켜는 쪽이 이득이다.")

    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for key, neg, _, items in NETS:
                f.write(f"\n{'=' * 90}\n{key} — 음성 판정 {totals[key]}건 중 그물 적발 {len(hits[key])}건 · 좌우 항목 {items}\n{'=' * 90}\n")
                for rid, line in hits[key][: a.per_family]:
                    f.write(f"[{rid}] {line}\n   라벨(1/0/?) = \n")
        log(f"검토 자료 저장: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
