#!/usr/bin/env python3
"""dev 200건 + 정답으로 사례집(cases.json)을 만든다. 제공 자료(dev·항목표)만 쓴다 — 규칙 2-2의 자가 라벨·RAG 사례집.
각 사례: id · 공고명 · 메타 요약 · 검색용 질의문 · 정답 위반 항목(항목명·정답 근거 160자).

  python cloud/build_cases.py   → cloud/cases.json
"""
import csv
import gzip
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("m", ROOT / "cloud" / "script_dump.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

items = json.loads((ROOT / "open/data/항목표.json").read_text(encoding="utf-8"))["항목"]
labels = {r["id"]: r for r in csv.DictReader(open(ROOT / "open/dev_labels.csv", encoding="utf-8"))}
cases = []
with gzip.open(ROOT / "open/dev.jsonl.gz", "rt", encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line)
        lab = labels[rec["id"]]
        meta = rec.get("meta", {})
        pos = [{"item": v, "name": items[v]["항목명"], "evidence": (lab.get("e" + v[1:]) or "").strip()[:160]}
               for v in m.ITEMS if lab[v] == "1"]
        cases.append({"id": rec["id"], "title": m.title_of(rec)[:120],
                      "meta": f"{meta.get('적용계약법')}·{meta.get('업무구분')}·{meta.get('계약방법')}·{meta.get('낙찰방법')}·추정가격 {meta.get('입찰추정가격')}",
                      "query": m.case_query(rec), "positives": pos})
out = ROOT / "cloud" / "cases.json"
out.write_text(json.dumps(cases, ensure_ascii=False), encoding="utf-8")
print(f"{len(cases)}건 · 위반 있는 사례 {sum(1 for c in cases if c['positives'])} · {out.stat().st_size // 1024}KB")
