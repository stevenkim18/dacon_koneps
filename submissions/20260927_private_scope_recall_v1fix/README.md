# private_scope_recall_v1fix — 09-27 후보 + v1 정규식 보조 수정

상태: **제출 후보(09-27, 또는 09-26 대안) · 미제출.** 기준은 [`20260927_private_scope_recall`](../20260927_private_scope_recall/README.md)(미제출). 변경 내용과 점수 추정은 그 README를 그대로 따른다.
여기에 [`20260926_phrase_parser_recall_v1fix`](../20260926_phrase_parser_recall_v1fix/README.md)와 같은 한 줄 수정(`FACT_KEYS`에 `"특정기관_근거"`)만 더했다.

## 결과

| 항목 | 값 |
|---|---|
| 제출 ID · 제출 시각 | *미제출* |
| Public 점수 | *미제출* |
| 서버 소요 시간 | *미제출* (예상 약 51분) |

## 왜 고쳤나

기준 후보도 09-26 후보의 v1 정규식 보조를 물려받았고, 같은 이유로 **LLM 출력이 있으면 v1 정규식이 작동하지 않는다**(자세한 원인은 `20260926_phrase_parser_recall_v1fix` README).

| 주입 시험(int8 저장 출력이 있는 무라벨 12건, 문장 5종) | 기준 | 이 판 |
|---|---:|---:|
| LLM 출력 있음(서버 경로) | **0/60** | **60/60** |
| LLM 출력 없음(정규식 경로) | 60/60 | 60/60 |

## 검증 ([`dev_validation.log`](dev_validation.log) · [`mock_validation.log`](mock_validation.log))

| 검사 | 결과 |
|---|---|
| dev 재채점 3벌 | 4bit 0.8730 · int8 단독 0.8612 · int8 묶음 0.8549 — **기준과 동일** |
| 저장 출력 전 판정 차이(dev 4bit·int8 2벌, 무라벨 750 4bit·int8) | **판정 0 · 근거 0 · 근거 요건 위반 0** |
| 무라벨 20,000 정규식 재생 | Δ+0 · 변경 0공고 · 예외 0 (기준 양성 5,159) |
| 근거 문구 | dev 양성 133 · 750 양성 129, 공란 3건은 기준과 같음 |
| mock | 종료코드 0 · 자가검증 PASS · 10행 49열 · 헤더 = sample_submission · v열 0/1 · BOM 없음 · ID 중복 없음 |
| ZIP | `submit.zip` SHA-256 `a7bcab7c1949a00f1d8e143eba81a4debc2fee71119477dc4374f3f8f9ffdecd` (최상위 `script.py`·`requirements.txt`). `script.py` `814015ae…` · `requirements.txt` `5740d52b…`(기준과 동일) |

## 점수 추정

기준 README 그대로다: 평가셋이 소액수의 공고에 v10·v17을 라벨했으면 +0.010~0.020, 안 했으면 −0.008~−0.015. v1 수정 몫은 0~+0.002.
09-28 되돌림 판이 필요하면 이 폴더의 `script.py`에서 기준 README의 되돌림 대상(`make_v10q.py` 1번, `make_sent2.py` E 블록)을 빼고 v1 수정은 남긴다.

## 실행하지 않은 것

- 서버 vLLM 실제 실행(LLM 호출 코드는 기준과 같다).
- 도구: [`runs/review_20260925/`](../../runs/review_20260925/README.md).
