# s26_recall_plus — 09-28 대비판: 09-26 제출본 + 재현율 보강 R1~R13 (소액수의 규칙 유지)

상태: **보류 · 미제출(조건 미충족, `s26_plus_r3`가 대신하던 판).** 09-27 [`scope_recall_plus`](../20260927_scope_recall_plus/README.md)가 **0.7100 미만**일 때 09-28에 내기로 했으나, 09-27이 0.7139258423이라 쓰지 않는다(해석표는 그 README).
구성: 09-26 제출본 [`safetynet_vague_perf`](../20260926_safetynet_vague_perf/README.md)(Public **0.7066**)에 R1~R13만 얹었다. v10·v20 소액수의 규칙, v12·v1 정리 전 판정은 09-26 그대로다.
- 09-27 판에서 범위 정리 몫(scope_cleanup)만 뺀 판이다. 09-27이 범위 정리로 손해를 봤다면 이 판이 그 손해 없이 보강 몫만 받는다.
- LLM 호출·입력은 09-26 제출본과 같다(960건 차이 0) → 예상 서버 시간 약 51분.

생성: `make_recall_probe.py submissions/20260926_safetynet_vague_perf/script.py <out> R1,…,R13,DOC3` ([생성기](../../runs/recall_probe_20260926/make_recall_probe.py)).

| 검사 ([`validation.log`](validation.log)) | 결과 |
|---|---|
| dev int8 단독 · 교차 | 0.8617 · 0.8275 → **0.8732 · 0.8455** (정탐 +3: v1 DEV-046·063, v4 DEV-042 · 오탐 0) |
| 무라벨 750 | +4 (v2 1 · v4 3, 모두 라벨 없음) |
| 무라벨 20,000 (09-26 대비) | **+159** (v1 +1 · v2 +24 · v3 +1 · v4 +119 · v8 +14), 136공고, 예외 0 — scope_recall_plus의 보강 몫과 같다 |
| LLM 입력 · 근거 문구 | 960건 차이 0 · 요건 위반 0 |
| mock | 10·960건 PASS (960건 25.7초) · 49열 · 헤더·0/1·ID·BOM 이상 없음 |
| ZIP | `submit.zip` SHA-256 `f856d6b69d9ef30e16dabf6db3bc842cc542b309e9d37f67a8a410eb07a0b26a` · `script.py` `5f66b0f0…`(압축 안팎 일치) · `requirements.txt` 09-26과 동일 |

예상: 0.7066 + 보강 몫(+0.002~0.008) = **약 0.709~0.715**. 소액수의 해석과 무관하다.
