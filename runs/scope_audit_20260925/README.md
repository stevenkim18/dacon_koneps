# 09-25 ① 도구 — 적용 범위 전수 대조 · 편집 문장 재현율

해석은 [study log 09-25 ①](../../docs/05_study_log/20260925/1.%20v8nat_result_and_scope_audit.md), 결과물은 [`submissions/20260927_private_scope_recall`](../../submissions/20260927_private_scope_recall/README.md). 저장소 루트에서 `.venv/bin/python runs/scope_audit_20260925/<파일>`로 실행한다(`runs/int8_port_20260923/devtool.py`·`runs/sme_sentence_20260924/`의 도구를 함께 쓴다).

| 파일 | 내용 |
|---|---|
| `pred0925.py` | 09-24 ④ 적합 모형으로 09-25 후보 예측(v8 국가 정밀도 0/0.5/0.87 민감도). 실제 +0.0145는 모형 범위 밖 — 편집 재현율 몫을 모형이 못 본다 |
| `v3rel.py` · `read_perf.py` | 무라벨에서 상대 금액 실적 표현 줄 찾기 · 두 스크립트 사이 실적 관련 판정 변화 읽기 |
| `inject_v3.py BASE [VAR…]` | v3 상대 금액 문장 10종 × 공고 8 주입(기준 0/80 → 후보 80/80) |
| `inject_v23.py BASE [VAR…]` | 지방·협상 공고에 마감 5일 전 설명회 문장 8형식 × 10 주입(50/80 → 80/80) |
| `v9svc.py` | int8 본 호출이 용역 공고에서 특정모델 지정이라 한 것(지방 용역 확대 기각 근거) |
| `v4name.py` | '유사 실적 불인정·실적만 인정' 표현 스캔(794공고, 거의 평가 문맥 → 레버 아님) |
| `v10look.py SCRIPT ID,…` | v10 적중 공고의 품목(meta·본 호출·품목 호출)과 직생 줄 |
| `make_v3rel.py` · `make_v23d.py` · `make_v10q.py` | 후보 생성기(후보 폴더에도 복사) |
