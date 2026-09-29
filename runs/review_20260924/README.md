# 09-24 검토 도구

해석은 [study log 09-24 ①](../../docs/05_study_log/20260924/1.%20int8_quote_port_result_and_next.md) · [②](../../docs/05_study_log/20260924/2.%20rereview_zero_cost_broadening.md). 모두 저장소 루트에서 `.venv/bin/python runs/review_20260924/<파일>`로 실행한다. GPU 불필요.

| 파일 | 내용 |
|---|---|
| `next_v8nat_v22fix.py` | int8_quote_port + v8 국가 + v22 수정판(09-24 ① 측정본). `submissions/20260925_v8nat_v22fix_v21wide/script.py`는 여기에 v21 확장을 더한 것 |
| `devscore.sh` | dev 200 재채점 3벌(4bit·int8 단독·int8 묶음). `zsh runs/review_20260924/devscore.sh <script.py>` |
| `v22_unit.py` | v22 정규식 단위 점검(켜져야 할 문장·꺼져야 할 문장). `v22_unit.py OLD.py NEW.py` |
| `inject_v21.py` · `inject_v12.py` | 바꿔 쓴 v21 지분 문장·v12 직생 문장을 자연 공고에 넣어 켜지는지(정규식 경로). `inject_v21.py BASE.py NEW.py` |
| `or_probe.py` | 본 호출 LLM 사실을 규칙 항목에 OR했을 때 dev·750 새 양성(int8 950건 저장 출력) — 기각 근거 |
| `sec_evid.py` · `sec_labels.py` | "입찰참가자격" 절 안/밖 근거의 분포(20,000)와 손라벨 정밀도 — 기각 근거 |
| `pool_items.py` · `fulldiff_A_to_*.txt` · `v20_swtitle_cands.pkl` · `mock/` | 09-24 ① 측정 산출물 |

## 09-24 ③ 표현·파서 구멍 찾기 ([study log](../../docs/05_study_log/20260924/3.%20phrase_parser_hunt.md))

| 파일 | 내용 |
|---|---|
| `build_phrase_parser.py` | 09-25 후보에 변경을 두 글자 키로 얹어 변형을 만든다. `build_phrase_parser.py OUT.py A2E4M1B2C2D2G1` = `submissions/20260926_phrase_parser_recall/script.py`의 본문(머리말 제외). A2 기업규모 "…만 참여 가능" · B2 v4 공공 발주처 · C2 v12 · D2 지역 · M1 기업규모 자격 표지 · E1/E4 미발급 안내·머리말 · G1 v1 정규식 보조 |
| `newhits.py` | 두 스크립트가 20,000에서 다르게 판정한 (공고, 항목)과 근거 줄을 항목별로 뽑는다(`replay_unlabeled.py`를 먼저 돌려 변경 id 캐시를 만든다). `newhits.py BASE.py VAR.py [항목,…|-] [최대]` |
| `cmpcache.py` | `runs/replay_cache/`의 판정 캐시끼리 항목별 Δ를 센다 |
| `inject_v1.py` | v1 바꿔 쓴 문장 주입 |
