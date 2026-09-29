#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""근거 문구(e1~e24) 전수 검사 — 2차 정성평가 요건 확인용.

양성(부재탐지 v10·v11·v16·v18·v20 제외)마다 근거가 ① 비어 있지 않고 ② 공고 원문(`docs` 본문)의 부분문자열이며
③ 500자 이하인지 본다. 부재탐지 항목과 음성 항목의 근거가 비어 있는지도 센다.
dev 200(저장 출력)과 무라벨 750(저장 출력) 두 벌을 본다.

  python scripts/evidence_audit.py submissions/<후보>/script.py

09-19 이래 무라벨 750의 공란 4건(PPS-D-017887 v19 · 017996 v7 · 019612 v7 · 000850 v6)은 알려진 것이다. 새 문제가 0건인지 확인한다.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV = {"files": ["open/dev.jsonl"],
       "outs": {"main": ["runs/mlx/extract_outputs.jsonl"], "item": ["runs/mlx/item_outputs.jsonl"],
                "model": ["runs/mlx/model_outputs.jsonl"], "sme": ["runs/mlx/v21_sme_dev.jsonl"],
                "region": ["runs/mlx/v22_region_dev.jsonl"]}}
U750 = {"files": ["runs/mlx/train_sample250.jsonl", "runs/mlx/train_sample500_next.jsonl"],
        "outs": {k: [f"runs/mlx/train250_{k}.jsonl", f"runs/mlx/train500_{k}.jsonl"]
                 for k in ["main", "item", "model", "sme", "region"]}}


def load(paths):
    d = {}
    for p in paths:
        p = ROOT / p
        if p.exists():
            d.update({json.loads(l)["id"]: json.loads(l)["text"] for l in p.read_text(encoding="utf-8").splitlines()})
    return d


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    spec = importlib.util.spec_from_file_location("cand", sys.argv[1])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    tbl = m.load_competitive_table(str(ROOT / "open" / "data"))
    for name, cfg in (("dev", DEV), ("무라벨750", U750)):
        outs = {k: load(v) for k, v in cfg["outs"].items()}
        recs = [json.loads(l) for f in cfg["files"] for l in (ROOT / f).read_text(encoding="utf-8").splitlines()]
        c, bad = Counter(), []
        for r in recs:
            i = r["id"]
            hits, evid, _ = m.decide(r, outs["main"].get(i, ""), tbl, item_text=outs["item"].get(i, ""),
                                     model_text=outs["model"].get(i, ""), sme_text=outs["sme"].get(i, ""),
                                     region_text=outs["region"].get(i, ""))
            src = m.full_text(r)
            for v in m.ITEMS:
                e = evid[v]
                if v in m.ABSENCE:
                    c["부재탐지_근거있음"] += bool(e)
                    continue
                if not hits[v]:
                    c["음성_근거있음"] += bool(e)
                    continue
                c["양성"] += 1
                if not e:
                    c["공란"] += 1; bad.append((i, v, "공란"))
                elif e not in src:
                    c["원문아님"] += 1; bad.append((i, v, "원문아님"))
                elif len(e) > 500:
                    c["500자초과"] += 1; bad.append((i, v, "500자초과"))
        print(name, dict(c), bad[:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
