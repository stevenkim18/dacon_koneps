"""무라벨 표본의 위반 판정(공고, 항목) 쌍을 사람·LLM이 검토할 수 있게 근거를 모아 출력한다.

dev는 위반 공고가 44%라 평가셋(무라벨과 비슷한 분포 추정)보다 양성이 훨씬 많다. 실제 분포에서의
정밀도를 재려면 무라벨 표본에서 판정된 양성이 정말 위반인지 확인해야 한다.

사용법
  python scripts/audit_unlabeled.py --sample runs/mlx/train_sample250.jsonl \
      --outputs runs/mlx/train250_main.jsonl --item-outputs runs/mlx/train250_item.jsonl \
      [--model-outputs ...] --items v10,v13 > audit.txt
  python scripts/audit_unlabeled.py ... --labels data/self_labels/train250_audit.csv --report
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = [f"v{i}" for i in range(1, 25)]

# 항목별로 검토자에게 보여 줄 원문 줄 패턴
ITEM_LINES = {
    "v1": r"대학|산학협력단|기관만|협회|조합원|학교|참가\s*자격",
    "v2": r"실적", "v3": r"실적", "v4": r"실적", "v8": r"실적|소재|영업소",
    "v5": r"소재|영업소|지역", "v6": r"소재|영업소|지역", "v7": r"소재|영업소|지역",
    "v9": r"제조사|모델|상표|브랜드|동등",
    "v10": r"직접생산|세부품명|경쟁제품", "v11": r"중소기업|소기업|소상공인|세부품명|경쟁제품",
    "v12": r"직접생산|세부품명", "v13": r"소기업|소상공인|중소기업|세부품명|직접생산",
    "v14": r"중소기업|소기업|소상공인|중기업", "v15": r"중소기업|소기업|소상공인|중기업",
    "v16": r"중소기업|소기업|소상공인|중기업|비영리", "v17": r"중소기업|소기업|소상공인|중기업",
    "v18": r"중소기업|소기업|소상공인|중기업|비영리",
    "v19": r"확약", "v20": r"소프트웨어|대기업|상호출자|중견",
    "v21": r"지분|공동수급", "v22": r"설명회", "v23": r"설명회|마감|제출",
    "v24": r"예산|기초금액|추정가격|업종|경쟁|긴급",
}


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("audit_candidate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_saved(path):
    if not path or not Path(path).exists():
        return {}
    return {json.loads(l)["id"]: json.loads(l)["text"] for l in Path(path).read_text(encoding="utf-8").splitlines()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=str(ROOT / "submissions" / "20260918_sme_level" / "script.py"))
    ap.add_argument("--sample", required=True)
    ap.add_argument("--data-dir", default=str(ROOT / "open" / "data"))
    ap.add_argument("--outputs", required=True)
    ap.add_argument("--item-outputs", default=None)
    ap.add_argument("--model-outputs", default=None)
    ap.add_argument("--items", default=",".join(ITEMS))
    ap.add_argument("--max-lines", type=int, default=8)
    ap.add_argument("--labels", default=None, help="검토 결과 CSV(id,item,label,reason)")
    ap.add_argument("--report", action="store_true", help="라벨 CSV로 항목별 정밀도 집계")
    a = ap.parse_args()

    mod = load_module(Path(a.script))
    table = mod.load_competitive_table(a.data_dir)
    main_out, item_out, model_out = load_saved(a.outputs), load_saved(a.item_outputs), load_saved(a.model_outputs)
    recs = [r for r in mod.iter_records(a.sample) if r["id"] in main_out]
    want = set(a.items.split(","))

    preds = {}
    for r in recs:
        kw = {"item_text": item_out.get(r["id"], "")}
        if "model_text" in mod.decide.__code__.co_varnames:
            kw["model_text"] = model_out.get(r["id"], "")
        hits, evid, _ = mod.decide(r, main_out[r["id"]], table, **kw)
        preds[r["id"]] = (hits, evid)

    if a.report:
        labels = defaultdict(dict)
        with open(a.labels, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                labels[row["id"]][row["item"]] = int(row["label"])
        print(f"표본 {len(recs)}건")
        tot_tp = tot_fp = 0
        for v in ITEMS:
            flagged = [i for i in preds if preds[i][0][v]]
            judged = [i for i in flagged if v in labels[i]]
            tp = sum(labels[i][v] for i in judged)
            fp = len(judged) - tp
            tot_tp += tp
            tot_fp += fp
            if flagged:
                prec = tp / len(judged) if judged else float("nan")
                print(f"{v:<4} 판정 {len(flagged):>3} ({len(flagged) / len(recs) * 100:4.1f}%) · 검토 {len(judged):>3} · "
                      f"정탐 {tp:>3} · 오탐 {fp:>3} · 정밀도 {prec:.2f}")
        print(f"전체 정밀도 {tot_tp / max(1, tot_tp + tot_fp):.3f} (정탐 {tot_tp}, 오탐 {tot_fp})")
        return 0

    for r in recs:
        hits, evid = preds[r["id"]]
        flagged = [v for v in ITEMS if hits[v] and v in want]
        if not flagged:
            continue
        m = r["meta"]
        facts = mod.parse_facts(main_out[r["id"]]) or {}
        item = mod.parse_facts(item_out.get(r["id"], "")) or {}
        print("=" * 100)
        print(f"{r['id']} | {mod.title_of(r)[:80]}")
        print(f"  메타: {m['적용계약법']} · {m['업무구분']} · {m['계약방법']} · {m['낙찰방법']} · 예산 {m['배정예산금액']:,} · "
              f"추정 {m['입찰추정가격']:,} · 지역 {m['제한지역코드목록']} · 업종 {m['면허업종제한목록']} · "
              f"세부품명 {str(m['세부품명번호목록'])[:60]} · 조항 {m['조항호내용']}")
        code = facts.get("계약목적물_세부품명번호")
        print(f"  품목: 본호출 {code} {table.get(code, {}).get('name', '')} · 전용 {item.get('세부품명번호')} "
              f"({item.get('계약목적물_요약')})")
        for v in flagged:
            print(f"  ▶ {v} 판정 · 근거: {evid.get(v, '')[:160]!r}")
            rx = re.compile(ITEM_LINES.get(v, "."))
            shown = 0
            for d in r["docs"]:
                for line in d["text"].split("\n"):
                    s = line.strip()
                    if len(s) > 5 and rx.search(s):
                        print(f"      ({d['type']}) {s[:180]}")
                        shown += 1
                        if shown >= a.max_lines:
                            break
                if shown >= a.max_lines:
                    break
    return 0


if __name__ == "__main__":
    sys.exit(main())
