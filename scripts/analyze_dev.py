"""dev 200건의 구조, 라벨, 근거, 베이스라인 입력 손실을 점검한다.

모델을 실행하지 않으며 Python 표준 라이브러리만 사용한다.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEV_PATH = ROOT / "open" / "dev.jsonl"
LABEL_PATH = ROOT / "open" / "dev_labels.csv"
ITEM_PATH = ROOT / "open" / "data" / "항목표.json"
BASELINE_PATH = ROOT / "open" / "baseline" / "script.py"


def load_baseline():
    spec = importlib.util.spec_from_file_location("official_baseline", BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"베이스라인을 불러올 수 없습니다: {BASELINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def percentile(values: list[int], ratio: float) -> int:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * ratio)]


def positive_count(label: dict[str, str]) -> int:
    return sum(int(label[f"v{i}"]) for i in range(1, 25))


def main() -> None:
    records = [
        json.loads(line)
        for line in DEV_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    with LABEL_PATH.open(encoding="utf-8-sig", newline="") as file:
        labels = list(csv.DictReader(file))
    items = json.loads(ITEM_PATH.read_text(encoding="utf-8"))["항목"]
    labels_by_id = {row["id"]: row for row in labels}

    record_ids = [record["id"] for record in records]
    label_ids = [label["id"] for label in labels]
    if len(records) != 200 or len(labels) != 200:
        raise AssertionError("dev 입력과 라벨은 각각 200건이어야 합니다.")
    if len(record_ids) != len(set(record_ids)) or len(label_ids) != len(set(label_ids)):
        raise AssertionError("중복 ID가 있습니다.")
    if set(record_ids) != set(label_ids):
        raise AssertionError("dev 입력과 라벨의 ID 집합이 다릅니다.")

    positive_rows = sum(positive_count(label) > 0 for label in labels)
    total_positives = sum(positive_count(label) for label in labels)
    violation_distribution = Counter(positive_count(label) for label in labels)
    print("[기본]")
    print(f"입력={len(records)}, 라벨={len(labels)}, 위반 공고={positive_rows}, 정상 공고={len(labels) - positive_rows}")
    print(f"양성 라벨 셀={total_positives}, 공고당 위반 수 분포={dict(sorted(violation_distribution.items()))}")

    print("\n[항목별 라벨]")
    print("항목\t항목명\t양성\t근거 제공\t양성 ID")
    for i in range(1, 25):
        key = f"v{i}"
        positives = [label for label in labels if label[key] == "1"]
        evidence_count = sum(bool(label[f"e{i}"]) for label in positives)
        ids = ",".join(label["id"].removeprefix("PPS-DEV-") for label in positives)
        print(f"{key}\t{items[key]['항목명']}\t{len(positives)}\t{evidence_count}\t{ids}")

    document_counts = Counter(len(record["docs"]) for record in records)
    type_counts = Counter(doc["type"] for record in records for doc in record["docs"])
    lengths = [sum(len(doc["text"]) for doc in record["docs"]) for record in records]
    incomplete = [record for record in records if record["dropped_doc_counts"]]
    print("\n[문서 구조]")
    print(f"문서 수 분포={dict(sorted(document_counts.items()))}, 문서 유형={dict(type_counts)}")
    print(
        "총 글자 수="
        f"{sum(lengths):,}, 평균={statistics.mean(lengths):,.1f}, "
        f"중앙값={statistics.median(lengths):,.0f}, p90={percentile(lengths, 0.9):,}, 최대={max(lengths):,}"
    )
    print(f"첨부 탈락 공고={len(incomplete)}, 빈 문서={sum(not doc['text'].strip() for record in records for doc in record['docs'])}")

    evidence_cells: list[tuple[str, str, str]] = []
    missing_from_original: list[tuple[str, str]] = []
    for record in records:
        label = labels_by_id[record["id"]]
        for i in range(1, 25):
            evidence = label[f"e{i}"]
            if not evidence:
                continue
            evidence_cells.append((record["id"], f"v{i}", evidence))
            if not any(evidence in doc["text"] for doc in record["docs"]):
                missing_from_original.append((record["id"], f"v{i}"))
    print("\n[근거 무결성]")
    print(f"제공 근거 셀={len(evidence_cells)}, 원문 부분문자열 일치={len(evidence_cells) - len(missing_from_original)}")
    print(f"원문 불일치={missing_from_original or '없음'}")

    baseline = load_baseline()
    retained_chars = 0
    raw_chars = 0
    included_by_type: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    context_by_id: dict[str, str] = {}
    records_with_omitted_docs = 0
    for record in records:
        context = baseline.build_context(record, max_chars=4000)
        context_by_id[record["id"]] = context
        included_docs = 0
        for doc in record["docs"]:
            raw_chars += len(doc["text"])
            header = f"[{doc['type']}:{doc['doc_id']}]\n"
            start = context.find(header)
            kept = (
                len(os.path.commonprefix([doc["text"], context[start + len(header) :]]))
                if start >= 0
                else 0
            )
            retained_chars += kept
            included_docs += kept > 0
            stats = included_by_type[doc["type"]]
            stats[0] += 1
            stats[1] += kept > 0
            stats[2] += kept == len(doc["text"])
        records_with_omitted_docs += included_docs < len(record["docs"])

    missed_evidence = [
        (record_id, item)
        for record_id, item, evidence in evidence_cells
        if evidence not in context_by_id[record_id]
    ]
    print("\n[공식 베이스라인 build_context(max_chars=4000)]")
    print(
        f"원문 글자 보존={retained_chars:,}/{raw_chars:,} ({retained_chars / raw_chars:.1%}), "
        f"일부 문서 미수록 공고={records_with_omitted_docs}"
    )
    for doc_type, stats in included_by_type.items():
        print(f"{doc_type}: 전체={stats[0]}, 일부 이상 입력={stats[1]}, 전문 입력={stats[2]}")
    print(
        f"제공 근거 보존={len(evidence_cells) - len(missed_evidence)}/{len(evidence_cells)} "
        f"({(len(evidence_cells) - len(missed_evidence)) / len(evidence_cells):.1%})"
    )
    print(f"누락 근거={missed_evidence}")


if __name__ == "__main__":
    main()
