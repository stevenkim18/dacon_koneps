# vague_perf_no_private — 09-27 대비판 B: 소액수의 v10·v17 규칙을 둘 다 뺀 판

상태: **대비 후보(09-27) · 미제출.** 09-26에 [`20260926_safetynet_vague_perf`](../20260926_safetynet_vague_perf/README.md)를 내고 **Public − S25 < −0.004**이면 낸다(해석표는 09-26 판 README). 기준 판에서 **소액수의 두 규칙** — v10 수의계약 블록(`make_v10q.py` 1번)과 v17 수의계약 블록(`make_sent2.py` E) — 만 뺐다. 제2조의2 단서 예외(`make_sent2.py` D), 직생 자격 문장 인식(`make_v10q.py` 2번), P2, 안전망, v1fix, v3·v23 재현율, 여러 줄 기업규모 문장은 그대로다.
생성기: [`runs/review_20260925/make_no_private.py`](../../runs/review_20260925/make_no_private.py). LLM 호출은 기준과 같다.

## 결과

| 항목 | 값 |
|---|---|
| 제출 ID · 제출 시각 | *미제출* |
| Public 점수 | *미제출* |
| 서버 소요 시간 | *미제출* (예상 약 51분) |

## 측정 ([`dev_validation.log`](dev_validation.log) · [`mock_validation.log`](mock_validation.log))

| 검사 | 결과 |
|---|---|
| dev 재채점 3벌 | 4bit 0.8721 · int8 단독 0.8601 · int8 묶음 0.8540 (기준 대비 −0.0015: v17 **DEV-21 정탐을 잃고** DEV-090 오탐을 뺀다) |
| 저장 출력 판정 차이 | dev −v17 DEV-21(라벨 1) · −v17 DEV-090(라벨 0) · 무라벨 750 int8 v10 −22 · v17 −1(PPS-D-009336) |
| 무라벨 20,000 | 기준 대비 Δ−359(v10 −254 · v17 −105) · 09-25 제출본 대비 Δ+78 · 예외 0 |
| 근거 문구 · mock | 요건 위반 0 · 종료코드 0 · 자가검증 PASS · 10행 49열 · 헤더 일치 · v열 0/1 · BOM 없음 · ID 중복 없음 |
| 문법 | Python 3.9.6 · 3.11.4 · 3.13.5 |
| ZIP | `submit.zip` SHA-256 `78f4a267c510ccdfc494672a34ad1e4d4129c575e2aeb6c1a064eb02068b1abf` · `script.py` `fe2ac0d2…`(압축 안팎 일치) · `requirements.txt` `5740d52b…` |

## 주의

v17 소액수의 규칙은 dev 대표 예시 DEV-21(지방 물품 소액수의견적, 조항호내용 '소기업 소상공인 계약', 중소기업 수준 자격, v17=1)을 잡는 유일한 경로다. 이 판은 그 정탐을 버린다. 09-26 하락폭이 작으면 대비판 A(`no_v10q`)를 먼저 낸다.
