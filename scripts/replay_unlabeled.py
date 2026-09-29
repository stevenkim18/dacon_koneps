#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""무라벨 20,000건을 정규식 경로(LLM 출력 없음)로 판정해 후보 스크립트끼리의 양성 차이를 잰다.

`scripts/gate_ablation.py`는 게이트 문자열 치환 변형만 다루지만, 이 도구는 **임의의 후보 script.py 두 개 이상**을 비교한다.
스크립트 내용 해시별로 판정을 캐시하므로 같은 스크립트는 한 번만 돈다(1회 약 50초).

  python scripts/replay_unlabeled.py BASE.py VARIANT.py [VARIANT2.py ...]

출력: 기준 항목별 양성 수, 변형마다 Δ양성·변경 공고 수·항목별 Δ. 변경 공고 id 목록은 `runs/replay_cache/changed_<변형 이름>.pkl`.
주의: LLM 사실이 필요한 항목(v1·v9·v19, 품목 호출에 기대는 v10~v13)은 이 경로에서 실제와 다르다. 그 항목은
`scripts/eval_unlabeled750.py`(저장된 전 파이프라인 출력)로 본다. 판정 중 예외가 난 레코드는 None으로 세어 보고한다.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import pickle
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "runs" / "replay_cache"
ITEMS = [f"v{i}" for i in range(1, 25)]


def run(script: str):
    h = hashlib.md5(Path(script).read_bytes()).hexdigest()[:10]
    CACHE.mkdir(parents=True, exist_ok=True)
    cp = CACHE / f"{Path(script).parent.name}_{Path(script).stem}_{h}.pkl"
    if cp.exists():
        return pickle.load(open(cp, "rb"))
    spec = importlib.util.spec_from_file_location(f"m{h}", script)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    tbl = m.load_competitive_table(str(ROOT / "open" / "data"))
    out = {}
    with gzip.open(ROOT / "open" / "train_unlabeled.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            try:
                hits = m.decide(r, "", tbl)[0]
                out[r["id"]] = tuple(hits[v] for v in ITEMS)
            except Exception:
                out[r["id"]] = None
    pickle.dump(out, open(cp, "wb"))
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    base = run(sys.argv[1])
    bc = Counter()
    for t in base.values():
        if t:
            bc.update({v: x for v, x in zip(ITEMS, t)})
    print(f"기준 {sys.argv[1]} · 양성 {sum(bc.values()):,} · 예외 {sum(t is None for t in base.values())}")
    print("  " + " ".join(f"{v}:{bc[v]}" for v in ITEMS))
    for vs in sys.argv[2:]:
        var = run(vs)
        d, changed = Counter(), []
        for i, t in var.items():
            b = base.get(i)
            if t is None or b is None or t == b:
                continue
            changed.append(i)
            for v, x, y in zip(ITEMS, b, t):
                if x != y:
                    d[v] += y - x
        name = f"{Path(vs).parent.name}_{Path(vs).stem}"
        pickle.dump(changed, open(CACHE / f"changed_{name}.pkl", "wb"))
        print(f"{vs}: Δ{sum(d.values()):+d} · 변경 {len(changed)}공고 · 예외 {sum(t is None for t in var.values())} · "
              + " ".join(f"{v}{d[v]:+d}" for v in ITEMS if d[v]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
