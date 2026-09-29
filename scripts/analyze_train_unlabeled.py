"""무라벨 20,000건의 구조, 문서 손실, 메타데이터와 후보 신호를 분석한다.

모델을 실행하거나 라벨을 생성하지 않으며 Python 표준 라이브러리만 사용한다.
키워드 집계는 위반 판정이 아니라 사람이 검토할 후보군의 크기를 보는 용도다.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
TRAIN_PATH = ROOT / "open" / "train_unlabeled.jsonl.gz"
DEV_PATH = ROOT / "open" / "dev.jsonl.gz"
BASELINE_PATH = ROOT / "open" / "baseline" / "script.py"

KEYWORD_GROUPS = {
    "실적 제한": ("실적제한", "실적 제한", "수행실적", "납품실적"),
    "지역 제한": ("지역제한", "지역 제한", "소재한 업체", "소재 업체"),
    "직접생산확인": ("직접생산확인증명서", "직접생산 확인증명서", "직접생산확인"),
    "중소기업": ("중소기업",),
    "소기업·소상공인": ("소기업", "소상공인"),
    "물품공급 확약": ("물품공급확약서", "물품공급 확약서"),
    "소프트웨어 사업": ("소프트웨어사업", "소프트웨어 사업", "SW사업", "정보화사업"),
    "공동수급·공동도급": ("공동수급", "공동도급", "공동이행", "분담이행"),
    "현장설명회": ("현장설명회", "현장 설명회", "현장설명"),
    "모델·상표 명시": ("모델명", "모델 명", "상표명", "상표 명", "특정모델"),
}

KEY_META_FIELDS = (
    "적용계약법",
    "업무구분",
    "계약방법",
    "낙찰방법",
    "소관구분",
    "공동도급구성방식",
    "정보화사업여부",
    "지역제한여부",
    "업종제한여부",
    "긴급공고여부",
    "입찰방법",
    "조달방식",
)


def load_baseline():
    spec = importlib.util.spec_from_file_location("official_baseline", BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"베이스라인을 불러올 수 없습니다: {BASELINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_jsonl_gz(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number} JSON 오류") from error


def percentile(values: list[int], ratio: float) -> int:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * ratio)]


def summarize_numbers(values: list[int]) -> dict[str, float | int]:
    return {
        "min": min(values),
        "p50": percentile(values, 0.5),
        "p90": percentile(values, 0.9),
        "p95": percentile(values, 0.95),
        "p99": percentile(values, 0.99),
        "max": max(values),
        "mean": statistics.mean(values),
    }


def value_key(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def parse_yyyymmdd(value: Any) -> datetime | None:
    if not isinstance(value, str) or len(value) != 8 or not value.isdigit():
        return None
    try:
        return datetime.strptime(value, "%Y%m%d")
    except ValueError:
        return None


def analyze(path: Path, *, include_baseline: bool, include_keywords: bool) -> dict[str, Any]:
    baseline = load_baseline() if include_baseline else None
    ids: list[str] = []
    record_lengths: list[int] = []
    doc_counts: Counter[int] = Counter()
    type_counts: Counter[str] = Counter()
    type_lengths: dict[str, list[int]] = defaultdict(list)
    meta_counts: dict[str, Counter[str]] = defaultdict(Counter)
    completeness_counts: dict[str, Counter[str]] = defaultdict(Counter)
    dropped_records = 0
    dropped_types: Counter[str] = Counter()
    empty_docs = 0
    attachment_records = 0
    repeated_type_records = 0
    anon_counts: Counter[str] = Counter()
    assembly_versions: Counter[str] = Counter()
    keyword_counts: Counter[str] = Counter()
    keyword_by_type: dict[str, Counter[str]] = defaultdict(Counter)
    exact_record_hashes: dict[str, list[str]] = defaultdict(list)
    exact_doc_hashes: Counter[str] = Counter()
    dates_invalid = Counter()
    opening_lags: list[int] = []
    opening_before_posting: list[tuple[str, int]] = []
    amount_stats: dict[str, list[int]] = {"배정예산금액": [], "입찰추정가격": []}
    amount_special: dict[str, Counter[str]] = defaultdict(Counter)

    raw_chars = 0
    retained_chars = 0
    baseline_type_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    baseline_omitted_records = 0
    baseline_attachment_records = 0
    baseline_keyword_visible: Counter[str] = Counter()

    for record in read_jsonl_gz(path):
        record_id = record.get("id", "")
        ids.append(record_id)
        docs = record.get("docs", [])
        meta = record.get("meta", {})

        doc_counts[len(docs)] += 1
        types_in_record = Counter(doc.get("type", "<없음>") for doc in docs)
        if any(doc_type != "공고문" for doc_type in types_in_record):
            attachment_records += 1
        if any(count > 1 for count in types_in_record.values()):
            repeated_type_records += 1

        full_text_parts: list[str] = []
        per_record_chars = 0
        for doc in docs:
            doc_type = doc.get("type", "<없음>")
            text = doc.get("text", "")
            length = len(text)
            type_counts[doc_type] += 1
            type_lengths[doc_type].append(length)
            per_record_chars += length
            raw_chars += length
            empty_docs += not text.strip()
            full_text_parts.append(text)
            exact_doc_hashes[hashlib.sha256(text.encode("utf-8")).hexdigest()] += 1

            if include_keywords:
                for group, terms in KEYWORD_GROUPS.items():
                    if any(term in text for term in terms):
                        keyword_by_type[group][doc_type] += 1

        full_text = "\n".join(full_text_parts)
        record_lengths.append(per_record_chars)
        exact_record_hashes[
            hashlib.sha256(
                json.dumps(
                    {"docs": full_text_parts, "meta": meta},
                    ensure_ascii=False,
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
        ].append(record_id)

        if include_keywords:
            for group, terms in KEYWORD_GROUPS.items():
                if any(term in full_text for term in terms):
                    keyword_counts[group] += 1

        dropped = record.get("dropped_doc_counts", {})
        if dropped:
            dropped_records += 1
            for doc_type, count in dropped.items():
                dropped_types[doc_type] += int(count)
        for key, value in record.get("input_completeness", {}).items():
            completeness_counts[key][value_key(value)] += 1
        anon_counts[value_key(record.get("anon_applied"))] += 1
        assembly_versions[value_key(record.get("assembly_policy_version"))] += 1

        for key, value in meta.items():
            meta_counts[key][value_key(value)] += 1
        for field in amount_stats:
            value = meta.get(field)
            if isinstance(value, int):
                amount_stats[field].append(value)
                if value in (0, 1):
                    amount_special[field][str(value)] += 1
            else:
                amount_special[field][value_key(value)] += 1

        posted = parse_yyyymmdd(meta.get("공고게시일자"))
        opening = parse_yyyymmdd(meta.get("개찰예정일자"))
        if posted is None:
            dates_invalid["공고게시일자"] += 1
        if opening is None:
            dates_invalid["개찰예정일자"] += 1
        if posted is not None and opening is not None:
            lag = (opening - posted).days
            opening_lags.append(lag)
            if lag < 0:
                opening_before_posting.append((record_id, lag))

        if baseline is not None:
            context = baseline.build_context(record, max_chars=4000)
            if include_keywords:
                for group, terms in KEYWORD_GROUPS.items():
                    if any(term in full_text for term in terms) and any(term in context for term in terms):
                        baseline_keyword_visible[group] += 1
            included_docs = 0
            attachment_included = False
            for doc in docs:
                doc_type = doc["type"]
                text = doc["text"]
                header = f"[{doc_type}:{doc['doc_id']}]\n"
                start = context.find(header)
                kept = (
                    len(os.path.commonprefix([text, context[start + len(header) :]]))
                    if start >= 0
                    else 0
                )
                retained_chars += kept
                included_docs += kept > 0
                attachment_included |= kept > 0 and doc_type != "공고문"
                stats = baseline_type_stats[doc_type]
                stats[0] += 1
                stats[1] += kept > 0
                stats[2] += kept == len(text)
            baseline_omitted_records += included_docs < len(docs)
            baseline_attachment_records += attachment_included

    duplicate_ids = sum(count - 1 for count in Counter(ids).values() if count > 1)
    duplicate_record_groups = [ids for ids in exact_record_hashes.values() if len(ids) > 1]
    exact_duplicate_records = sum(len(ids) - 1 for ids in duplicate_record_groups)
    exact_duplicate_docs = sum(count - 1 for count in exact_doc_hashes.values() if count > 1)

    result: dict[str, Any] = {
        "path": str(path),
        "records": len(ids),
        "unique_ids": len(set(ids)),
        "duplicate_ids": duplicate_ids,
        "empty_docs": empty_docs,
        "doc_counts": dict(sorted(doc_counts.items())),
        "type_counts": dict(type_counts),
        "record_lengths": summarize_numbers(record_lengths),
        "type_lengths": {key: summarize_numbers(values) for key, values in type_lengths.items()},
        "attachment_records": attachment_records,
        "repeated_type_records": repeated_type_records,
        "dropped_records": dropped_records,
        "dropped_types": dict(dropped_types),
        "completeness": {key: dict(value) for key, value in completeness_counts.items()},
        "anon_applied": dict(anon_counts),
        "assembly_versions": dict(assembly_versions),
        "exact_duplicate_records": exact_duplicate_records,
        "duplicate_record_groups": duplicate_record_groups,
        "exact_duplicate_docs": exact_duplicate_docs,
        "meta_counts": {key: dict(value) for key, value in meta_counts.items()},
        "amount_stats": {
            key: summarize_numbers(values) if values else {} for key, values in amount_stats.items()
        },
        "amount_special": {key: dict(value) for key, value in amount_special.items()},
        "date_invalid": dict(dates_invalid),
        "opening_lags": summarize_numbers(opening_lags),
        "opening_before_posting_count": len(opening_before_posting),
        "opening_before_posting_examples": opening_before_posting[:20],
    }
    if include_keywords:
        result["keyword_counts"] = dict(keyword_counts)
        result["keyword_by_type"] = {
            key: dict(value) for key, value in keyword_by_type.items()
        }
    if baseline is not None:
        result["baseline"] = {
            "raw_chars": raw_chars,
            "retained_chars": retained_chars,
            "retention_rate": retained_chars / raw_chars,
            "records_with_omitted_docs": baseline_omitted_records,
            "records_with_attachment_included": baseline_attachment_records,
            "type_stats": dict(baseline_type_stats),
            "keyword_visible": dict(baseline_keyword_visible),
        }
    return result


def compact_meta(result: dict[str, Any]) -> dict[str, Any]:
    return {
        field: result["meta_counts"].get(field, {})
        for field in KEY_META_FIELDS
    }


def print_summary(train: dict[str, Any], dev: dict[str, Any] | None) -> None:
    print("[기본 무결성]")
    for key in (
        "records",
        "unique_ids",
        "duplicate_ids",
        "empty_docs",
        "exact_duplicate_records",
        "exact_duplicate_docs",
    ):
        print(f"{key}={train[key]}")
    print(f"assembly_versions={train['assembly_versions']}")
    print(f"anon_applied={train['anon_applied']}")
    print(f"duplicate_record_groups={train['duplicate_record_groups']}")

    print("\n[문서 구조]")
    print(f"doc_counts={train['doc_counts']}")
    print(f"type_counts={train['type_counts']}")
    print(f"attachment_records={train['attachment_records']}")
    print(f"repeated_type_records={train['repeated_type_records']}")
    print(f"record_lengths={train['record_lengths']}")
    for doc_type, stats in train["type_lengths"].items():
        print(f"{doc_type} lengths={stats}")

    print("\n[입력 완전성]")
    print(f"dropped_records={train['dropped_records']}")
    print(f"dropped_types={train['dropped_types']}")
    print(f"completeness={train['completeness']}")

    print("\n[메타데이터 주요 분포]")
    for field, counts in compact_meta(train).items():
        print(f"{field}={counts}")
    print(f"amount_stats={train['amount_stats']}")
    print(f"amount_special={train['amount_special']}")
    print(f"date_invalid={train['date_invalid']}")
    print(f"opening_lags={train['opening_lags']}")
    print(f"opening_before_posting_count={train['opening_before_posting_count']}")
    print(f"opening_before_posting_examples={train['opening_before_posting_examples']}")

    print("\n[자가 라벨링 후보 문구: 위반 판정 아님]")
    for group, count in train.get("keyword_counts", {}).items():
        print(f"{group}={count}, 문서유형={train['keyword_by_type'][group]}")

    if "baseline" in train:
        print("\n[공식 베이스라인 build_context(max_chars=4000)]")
        print(json.dumps(train["baseline"], ensure_ascii=False, indent=2))

    if dev is not None:
        print("\n[dev 200건과 구조 비교]")
        print(f"train doc_counts={train['doc_counts']}, dev doc_counts={dev['doc_counts']}")
        print(f"train type_counts={train['type_counts']}, dev type_counts={dev['type_counts']}")
        print(f"train record_lengths={train['record_lengths']}")
        print(f"dev record_lengths={dev['record_lengths']}")
        print(f"train dropped_records={train['dropped_records']}, dev dropped_records={dev['dropped_records']}")
        for field in ("적용계약법", "업무구분", "계약방법", "낙찰방법", "소관구분"):
            print(f"{field} train={train['meta_counts'].get(field, {})}")
            print(f"{field} dev={dev['meta_counts'].get(field, {})}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="전체 집계를 JSON으로 출력")
    parser.add_argument("--skip-dev", action="store_true", help="dev 비교를 생략")
    args = parser.parse_args()

    train = analyze(TRAIN_PATH, include_baseline=True, include_keywords=True)
    dev = None if args.skip_dev else analyze(DEV_PATH, include_baseline=False, include_keywords=False)
    if args.json:
        print(json.dumps({"train": train, "dev": dev}, ensure_ascii=False, indent=2))
    else:
        print_summary(train, dev)


if __name__ == "__main__":
    main()
