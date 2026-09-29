# 09-24 ④ 분석 도구 — 평가셋 구성 적합 · int8/4bit 차이 · 여러 줄 기업규모 문장 · v17 수의계약

GPU 없이 저장 출력(dev 4bit·int8 2벌, 무라벨 750 4bit·int8)과 무라벨 20,000 정규식 재생으로 쟀다. 해석은 [study log 09-24 ④](../../docs/05_study_log/20260924/4.%20sme_sentence_join_and_v17_private.md), 결과물은 [`submissions/20260927_sme_sentence_v17`](../../submissions/20260927_sme_sentence_v17/README.md).
모두 저장소 루트에서 `.venv/bin/python runs/sme_sentence_20260924/<파일>`로 실행한다(`runs/int8_port_20260923/devtool.py`를 쓴다).

| 파일 | 내용 |
|---|---|
| `errs.py SCRIPT [int8\|b4]` | dev 항목별 F1과 오탐·누락 공고(위반 묶음 C / 5월 묶음 M 표시) |
| `poolcounts.py` · `fit.py` · `fit3.py` | 같은 LLM 호출을 쓴 제출 3개(focused_calls·v22_region_fix·int8_quote_port)를 dev 묶음별 계수 + 무라벨 750 int8 적중률로 재현해 평가셋 구성(위반 공고 비율 fracC, dev 수정 전이율 τ, 자연 적중 정탐률 q, 누락률 miss)을 격자 적합. 출력 `fit3_output.txt` |
| `mix.py` · `decomp.py` | 묶음 비율별 macro 추정 · 두 버전 사이 항목별 계수 변화와 바뀐 dev 공고 |
| `b4_vs_int8.py` · `i8only.py ITEM [i8only\|both\|b4only]` | 무라벨 750에서 4bit·int8 판정 비교(int8이 v1 5→15, v9 11→26) · 한쪽에서만 켜진 공고의 근거 |
| `v9look.py` · `v9lines.py` | dev v9의 본 호출·모델명 전용 호출 근거 줄(int8 오탐 10건의 출처) |
| `lvl_disagree.py` | 정규식 기업규모 수준 ≠ 기업규모 전용 호출 수준인 공고(950건 중 44건) |
| `make_sent.py BASE OUT` · `make_sent2.py SENT OUT [--no-v17q] [--no-parser]` | 후보 생성기(1단계: 문장 인식 창, 2단계: 확인서 이름·표기 변형 + v17 단서 예외 + v17 소기업·소상공인 수의계약) |
| `vdiff.py BASE VAR` | dev(int8·4bit)·무라벨 750(int8·4bit) 판정 차이 |
| `read_changes.py BASE VAR ITEM +\|- N` · `read_v17q.py` · `show_cands.py` · `list_final.py` | 20,000 재생 캐시(`runs/replay_cache`)에서 바뀐 공고를 읽는 도구 · 최종 변경 목록 CSV |
| `inj_v17diff.py VAR` | `inject_test.py`의 v17 주입 결과가 기준과 달라진 공고 |
