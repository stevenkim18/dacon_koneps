# phrase_parser_recall_nov8 — phrase_parser_recall에서 v8 국가 적용만 되돌린 판

상태: **예비 후보(09-26) · 미제출.** 09-25 결과 S25가 **0.6908 미만**일 때 [`20260926_phrase_parser_recall`](../20260926_phrase_parser_recall/README.md) 대신 낸다.
S25 < 0.6908이면 09-25 해석표에서 "국가 v8 중복 제한은 라벨 0일 가능성"이 가장 유력하다([`20260925_v8nat_v22fix_v21wide`](../20260925_v8nat_v22fix_v21wide/README.md)).

## 차이

`phrase_parser_recall/script.py`와 두 줄만 다르다(머리말 1줄 · 판정 줄 1줄).

```python
v["v8"] = int(local and not small_quote and perf and region)   # 국가 적용 되돌림
```

나머지 변경(v4 공공 발주처 실적 · 기업규모 파서 보강 · 확인서 미발급 안내·머리말 · "…만 참여 가능" · v12 · 지역 표현 · v1 정규식 보조, v22 수정판 · v21 확장)은 모두 같다. 설명은 원본 README와 [study log 09-24 ③](../../docs/05_study_log/20260924/3.%20phrase_parser_hunt.md).

## 검증 ([`dev_validation.log`](dev_validation.log) · [`mock_validation.log`](mock_validation.log))

| 검사 | 결과 |
|---|---|
| dev 판정 전수 차이 (09-25 후보 대비, 저장 출력 3벌) | DEV-039 v18 정탐 +1(세 벌 모두) — v8 국가는 dev 판정 변화가 원래 0 |
| dev macro | 4bit 0.8738 · int8 단독 0.8615 · int8 묶음 0.8557 (원본과 같음) |
| 무라벨 750 저장 출력 | v8 −3(09-25 후보가 더한 국가 v8 3건) · v4 +1 |
| 무라벨 20,000 | 09-25 후보 대비 Δ−58(v8 −64 포함), 현재 최고점(int8_quote_port) 대비 **Δ+39**(v22 +31 · v4 +35 · v2 +15 · v8 +2 · v3 +1 · 기업규모 파서·v12 −54 / +9) · 예외 0 |
| 주입 시험 · 근거 문구 | 원본과 같음(전 항목 100%, v21 104/112 · 근거 요건 위반 0, 750 양성 121) |
| mock | 종료코드 0 · 자가검증 PASS · 10행 49열 · v열 0/1 · BOM 없음 · 헤더 = sample_submission |
| ZIP | `submit.zip` SHA-256 `9427aa0767b0fb9510a03b0501267c73af112768a11a8de2affa9a12915b0ce4` (50,177바이트). 압축 안팎 해시 일치: `script.py` `ce2df1bc…` |

## 결과

| 항목 | 값 |
|---|---|
| 제출 ID · 제출 시각 · Public · 서버 시간 | *미제출* |
