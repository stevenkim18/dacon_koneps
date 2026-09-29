#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""무라벨 750건(`runs/mlx/train_sample250.jsonl` + `train_sample500_next.jsonl`)을 저장된 전 파이프라인 출력
(본·품목·모델명·기업규모·지역 호출)으로 판정하고, 두 후보가 다르게 판정한 (공고, 항목) 쌍을 손라벨과 함께 보여 준다.

  python scripts/eval_unlabeled750.py BASE.py VARIANT.py

손라벨은 `labels/train250_audit.csv`·`labels/train500_audit.csv`(우리가 양성이라 한 쌍의 정탐/오탐 라벨)다.
양성을 지우는 변경이면 지워진 쌍의 라벨이 0이어야 하고, 더하는 변경이면 새 쌍을 라벨해 정밀도를 잰다.
LLM 출력을 쓰므로 정규식 경로 재생(`scripts/replay_unlabeled.py`)과 달리 v1·v9·v10~v13·v19도 실제 판정에 가깝다.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = [f"v{i}" for i in range(1, 25)]
SAMPLES = ["runs/mlx/train_sample250.jsonl", "runs/mlx/train_sample500_next.jsonl"]
KINDS = ["main", "item", "model", "sme", "region"]


def load_texts(path: Path):
    if not path.exists():
        return {}
    return {json.loads(l)["id"]: json.loads(l)["text"] for l in path.read_text(encoding="utf-8").splitlines()}


def judge_all(script: str):
    spec = importlib.util.spec_from_file_location(Path(script).stem, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tbl = mod.load_competitive_table(str(ROOT / "open" / "data"))
    outs = {k: {**load_texts(ROOT / f"runs/mlx/train250_{k}.jsonl"), **load_texts(ROOT / f"runs/mlx/train500_{k}.jsonl")}
            for k in KINDS}
    recs = [json.loads(l) for f in SAMPLES for l in (ROOT / f).read_text(encoding="utf-8").splitlines()]
    hits = {}
    for r in recs:
        i = r["id"]
        hits[i] = mod.decide(r, outs["main"].get(i, ""), tbl, item_text=outs["item"].get(i, ""),
                             model_text=outs["model"].get(i, ""), sme_text=outs["sme"].get(i, ""),
                             region_text=outs["region"].get(i, ""))[0]
    return hits


def labels():
    lab = {}
    for f in ["labels/train250_audit.csv", "labels/train500_audit.csv"]:
        for r in csv.DictReader(open(ROOT / f, encoding="utf-8")):
            lab[(r["id"], r["item"])] = (r["label"], r["reason"])
    return lab


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    a, b, lab = judge_all(sys.argv[1]), judge_all(sys.argv[2]), labels()
    print(f"양성: 기준 {sum(sum(h.values()) for h in a.values())} → 변형 {sum(sum(h.values()) for h in b.values())} (750건)")
    tally = Counter()
    for i in a:
        for v in ITEMS:
            if a[i][v] != b[i][v]:
                l, why = lab.get((i, v), ("-", ""))
                kind = "추가" if b[i][v] else "제거"
                tally[(kind, l)] += 1
                print(f"  {kind} {i} {v} 라벨={l} {why[:90]}")
    print("요약:", dict(tally), "(라벨 1=정탐, 0=오탐, -=미라벨)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
