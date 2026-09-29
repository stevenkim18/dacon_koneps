"""모델 없이 베이스라인의 4,000자 문서 입력을 원본과 비교합니다."""

import csv
import importlib.util
import os
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    # 배포본 함수를 직접 사용해 제출 코드와 같은 방식으로 입력을 구성합니다.
    spec = importlib.util.spec_from_file_location("baseline", root / "open/baseline/script.py")
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    notice = next(r for r in baseline.iter_records(str(root / "open/dev.jsonl.gz"))
                  if r["id"] == "PPS-DEV-01")
    with (root / "open/dev_labels.csv").open(encoding="utf-8-sig", newline="") as f:
        label = next(r for r in csv.DictReader(f) if r["id"] == notice["id"])

    context = baseline.build_context(notice, max_chars=4000)
    output = root / "docs/04_learning/examples/PPS-DEV-01-context"
    output.mkdir(parents=True, exist_ok=True)
    (output / "full_documents.txt").write_text(
        "\n\n".join(f"[{d['type']}:{d['doc_id']}]\n{d['text']}" for d in notice["docs"]),
        encoding="utf-8",
    )
    (output / "context_4000.txt").write_text(context, encoding="utf-8")
    (output / "user_prompt_4000.txt").write_text(
        baseline.build_user_prompt(notice, max_chars=4000), encoding="utf-8")
    (output / "system_prompt.txt").write_text(
        baseline.build_system_prompt(baseline.item_table(str(root / "open/data"))),
        encoding="utf-8",
    )

    lines = ["# PPS-DEV-01 문서 입력 비교", "",
             "베이스라인의 `build_context(max_chars=4000)` 결과다. 실제 모델·토크나이저는 실행하지 않았다.",
             "실제 실행의 `fit_to_budget` 단계에서는 토큰 예산에 따라 입력이 더 줄어들 수 있다.", "",
             "| 문서 | 원본 본문 글자 수 | 입력에 포함된 본문 글자 수 | 상태 |",
             "|---|---:|---:|---|"]
    for d in notice["docs"]:
        header = f"[{d['type']}:{d['doc_id']}]\n"
        start = context.find(header)
        kept = len(os.path.commonprefix([d["text"], context[start + len(header):]])) if start >= 0 else 0
        status = "전체 포함" if kept == len(d["text"]) else "일부 잘림" if kept else "미수록"
        lines.append(f"| {d['type']} | {len(d['text']):,} | {kept:,} | {status} |")

    lines += ["", "## 제공 정답 근거 확인", ""]
    for i in range(1, 25):
        if label[f"v{i}"] != "1":
            continue
        evidence = label[f"e{i}"]
        if not evidence:
            lines.append(f"- v{i}: 제공 근거가 비어 있어 포함 여부 검사 제외.")
            continue
        in_original = any(evidence in d["text"] for d in notice["docs"])
        lines += [f"- v{i} 근거가 원본 문서에 있는가: {in_original}",
                  f"- v{i} 근거가 4,000자 문서 입력에 있는가: {evidence in context}",
                  "", "```text", evidence, "```"]

    lines += ["", "## 읽을 파일", "",
              "- [전체 문서](full_documents.txt)",
              "- [4,000자 예산 문서 입력](context_4000.txt)",
              "- [메타데이터까지 포함한 user 프롬프트](user_prompt_4000.txt)",
              "- [판단 지시인 system 프롬프트](system_prompt.txt)", "",
              "4,000자는 문서 구성 예산이다. 메타데이터·system 지시와 절단 안내까지 포함한 전체 입력 길이를 뜻하지 않는다."]
    report = "\n".join(lines) + "\n"
    (output / "README.md").write_text(report, encoding="utf-8")
    print(report)
    print("저장 위치:", output)


if __name__ == "__main__":
    main()
