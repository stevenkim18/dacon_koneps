"""개발 데이터에서 공고 한 건을 찾아 내용을 출력하는 첫 실습."""

import csv
import gzip
import json
from pathlib import Path


def main():
    # 실행 위치와 관계없이 이 파일을 기준으로 프로젝트 폴더를 찾습니다.
    project_dir = Path(__file__).resolve().parent.parent
    data_path = project_dir / "open" / "dev.jsonl.gz"
    labels_path = project_dir / "open" / "dev_labels.csv"
    items_path = project_dir / "open" / "data" / "항목표.json"
    target_id = "PPS-DEV-01"

    # JSON 파일 전체를 읽고, v1~v24를 키로 갖는 항목 목록을 가져옵니다.
    with items_path.open(encoding="utf-8") as items_file:
        items = json.load(items_file)["항목"]

    # gzip.open의 rt는 압축 파일을 텍스트로 읽는다는 뜻입니다.
    with gzip.open(data_path, "rt", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            # JSONL 한 줄을 Python 딕셔너리(키와 값의 모음)로 바꿉니다.
            notice = json.loads(line)
            if notice["id"] != target_id:
                continue

            documents = notice["docs"]
            print(f"공고 ID: {notice['id']}")
            print(f"문서 수: {len(documents)}")
            print("문서 종류:", ", ".join(doc["type"] for doc in documents))

            # 첨부문서와 구분하여 공고문 본문을 출력합니다.
            for document in documents:
                if document["type"] == "공고문":
                    print("\n[공고문 본문]\n")
                    print(document["text"])

            # DictReader는 CSV 헤더를 키로 사용합니다. 값은 문자열로 읽힙니다.
            with labels_path.open(encoding="utf-8-sig", newline="") as labels_file:
                for label in csv.DictReader(labels_file):
                    # 행 순서가 아닌 ID로 공고와 정답을 연결합니다.
                    if label["id"] != notice["id"]:
                        continue

                    print("\n[24개 항목의 제공 정답]")
                    violation_count = 0

                    # range(1, 25)는 1부터 24까지 반복합니다.
                    for number in range(1, 25):
                        violation_key = f"v{number}"
                        evidence_key = f"e{number}"
                        item_name = items[violation_key]["항목명"]
                        value = int(label[violation_key])
                        evidence = label[evidence_key]
                        violation_count += value
                        status = "위반" if value == 1 else "비위반"

                        print(f"\n{violation_key} | {item_name} | {status}")
                        print("근거:", evidence or "없음")

                        # 근거는 첨부문서에도 있을 수 있어 모든 문서를 확인합니다.
                        # 빈 문자열은 항상 포함된 것으로 처리되므로 검사하지 않습니다.
                        if evidence:
                            found = any(evidence in doc["text"] for doc in documents)
                            print("근거 문장이 공고문·첨부문서에 있는가:", found)

                    print(
                        f"\n요약: 제공 정답 기준 위반 {violation_count}개 / "
                        f"비위반 {24 - violation_count}개"
                    )
                    return

            raise SystemExit(f"정답을 찾지 못했습니다: {target_id}")

    raise SystemExit(f"공고를 찾지 못했습니다: {target_id}")


if __name__ == "__main__":
    main()
