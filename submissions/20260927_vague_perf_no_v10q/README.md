# vague_perf_no_v10q — 09-27 대비판 A: v10 소액수의 규칙만 뺀 판

상태: **대비 후보(09-27) · 미제출.** 09-26에 [`20260926_safetynet_vague_perf`](../20260926_safetynet_vague_perf/README.md)를 내고 **Public − S25가 −0.004 ~ +0.008**이면 낸다(해석표는 09-26 판 README). 기준 판에서 **v10 소액수의 블록(판로지원법 제9조①1호, `make_v10q.py` 1번) 하나만** 뺐다. v17 소액수의(dev DEV-21 v17=1)와 P2·안전망 등 나머지는 그대로다.
생성기: [`runs/review_20260925/make_no_private.py`](../../runs/review_20260925/make_no_private.py) `--v10-only`. LLM 호출은 기준과 같다(판정 줄 한 블록만 다름).

## 결과

| 항목 | 값 |
|---|---|
| 제출 ID · 제출 시각 | *미제출* |
| Public 점수 | *미제출* |
| 서버 소요 시간 | *미제출* (예상 약 51분) |

## 측정 ([`dev_validation.log`](dev_validation.log) · [`mock_validation.log`](mock_validation.log))

| 검사 | 결과 |
|---|---|
| dev 재채점 3벌 | 4bit 0.8736 · int8 단독 0.8617 · int8 묶음 0.8555 — 기준과 같음(dev에 수의계약 경쟁제품 공고가 없다) |
| 저장 출력 판정 차이 | dev 0건 · 무라벨 750 int8 v10 −22 · 4bit v10 −23 |
| 무라벨 20,000 | 기준 대비 Δ−254(v10만) · 09-25 제출본 대비 Δ+183 · 예외 0 |
| 근거 문구 · mock | 요건 위반 0 · 종료코드 0 · 자가검증 PASS · 10행 49열 · 헤더 일치 · v열 0/1 · BOM 없음 · ID 중복 없음 |
| 문법 | Python 3.9.6 · 3.11.4 · 3.13.5 |
| ZIP | `submit.zip` SHA-256 `22ebef1cb4be95361b2ee4ad79115bd0b264a164cec1b302beb1ce35228671e9` · `script.py` `367f9959…`(압축 안팎 일치) · `requirements.txt` `5740d52b…` |

## 읽는 법

09-26 판과의 차이는 v10 소액수의뿐이다. 09-27 − 09-26 > 0이면 v10 소액수의는 평가셋에서 오탐이었다. < 0이면 정탐이었다(09-28에 09-26 판을 다시 내거나 최고점 판 유지).
