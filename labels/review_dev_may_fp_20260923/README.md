# 5월 dev 경계 사례 독립 검토 (24쌍, 공고 20건)

2026-09-23 클라우드 int8 저장 출력과 `submissions/20260924_int8_quote_port/script.py`로 만든 검토 목록이다. 이 후보는 아직 제출하지 않았다. 코드나 저장 출력은 변경하지 않았다.

## 검토 방법

1. `cases.csv`의 각 행에 연결된 `cases/ID.txt`를 연다. 공고문과 첨부 `docs`, `meta`, `dropped_doc_counts`를 함께 읽는다.
2. `open/data/항목표.json`의 해당 항목 정의와 `open/data/법령패키지/`의 **배포본**을 기준으로 사람 판단 `1`(위반), `0`(아님), `?`(자료 부족·해석 보류)를 적는다.
3. 근거가 되는 문서를 `source_doc_id`에, 원문 그대로의 문장을 `exact_original_quote`에 적는다. 부재탐지 항목은 근거 문장 대신 확인한 문서 범위와 누락 여부를 `reason_from_supplied_rules`에 적는다.
4. 먼저 독립적으로 적고, 그 뒤에 `open/dev_labels.csv` 및 코드 출력을 대조한다. 라벨과 다르면 임의로 한쪽을 정답으로 간주하지 않는다.

이 목록은 **모델이 양성으로 잡았지만 dev 라벨은 0인 사례**를 5월 공고에서 고른 것이다. dev가 평가 분포를 대표하지 않으며 일부 dev 라벨은 제공 자료로 재현되지 않을 수 있다. 따라서 이 파일을 채웠다는 사실만으로 Public 개선을 주장하지 않는다.

출처: `open/dev.jsonl`, `open/dev_labels.csv`, `runs/cloud_int8_20260923/dev/raw/`와 위 후보 코드. 원본을 복사한 `cases/*.txt`는 검토 편의를 위한 자료다.
