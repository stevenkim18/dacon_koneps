# 09-25 후보 재검토 도구

해석은 [study log 09-25 ②](../../docs/05_study_log/20260925/2.%20candidate_rereview_server_path.md). 모두 저장소 루트에서 `.venv/bin/python runs/review_20260925/<파일>`로 실행한다. GPU 불필요(저장된 int8·4bit 출력 사용).

| 파일 | 내용 |
|---|---|
| `inject_v1_llm.py` | v1 '기관만 참여 가능' 문장을 무라벨 12건에 주입하고, **int8 본 호출 출력이 있는 상태(서버 경로)**와 없는 상태(정규식 경로)를 함께 잰다. `inject_v1_llm.py A.py B.py …` |
| `serverpath_inject.py` | 같은 방식의 전 항목 주입 시험. 스크립트를 여러 개 주면 첫 스크립트로 기반 공고를 고르고 모두 같은 공고·위치로 잰다(v1·v9·v19·v13·v15·v17·v14·v22·v12·v2·v4·v21·v5·v6·v7) + 주입 문장이 본 호출 발췌에 들어가는지(LLM이 볼 기회). `serverpath_inject.py SCRIPT.py [항목,…]` |
| `make_v1fix.py` | 후보 `script.py`에 `FACT_KEYS += "특정기관_근거"` 수정만 얹는다. `make_v1fix.py SRC.py DST.py 이름` |
| `make_safetynet.py` | v1fix 후보에 LLM 판정 항목 안전망(S1 v13·v15 `llm_or_level`, S2 v19 확약서 정규식 OR + 인용 둘 중 하나 조건 충족)을 얹는다. `submissions/20260926_private_scope_safetynet/script.py` 생성기 |
| `count750.py` | 무라벨 750 int8 전 파이프라인의 항목별 양성 수 |
| `variant_orlvl_13_15.py` | 시험 변형(초기판): v13·v15의 기업규모 수준만 LLM이 '없음'일 때 정규식 수준으로 채움. 최종은 `make_safetynet.py` |
| `v19_750.py` | v19 확약서 정규식 안전망을 LLM 판정과 OR하면 dev+750에서 새로 켜지는 것 |
| `v20_scope.py` | 공고명 SW 목적물인데 `is_software`가 거짓인 공고의 분포 — 기각 근거('프로그램 운영' 방과후 용역이 대부분) |
| `make_vague_perf.py` | (09-25 ③) 안전망 판에 **P2 막연한 실적 요구**(`PERF_VAGUE_RE`·`PERF_VAGUE_EXCL_RE`)를 얹는다. `submissions/20260926_safetynet_vague_perf/script.py` 생성기. `make_vague_perf.py SRC.py DST.py` |
| `make_vague_perf_firstcut.py` | P2 첫 판(제외어 좁음) 생성기. 판독 대상 148쌍을 재현하는 용도 |
| `vague_perf_audit.py` | P2 첫 판이 무라벨 20,000에서 새로 켠 v2·v4·v8과 판독 분류(G 입찰자 실적 요구 · T 학교 여행·수련 상투문 · FP 비자격)를 `labels/train20k_vague_perf_audit.csv`로 쓴다 |
| `inject_vague_perf.py` | 막연한 실적 문장(v2 8종, 지역+실적 v8 4종)을 서버 경로(int8 출력 유지)로 주입. `inject_vague_perf.py BASE.py NEW.py` |
| `make_no_private.py` | 09-27 대비판 생성기: 소액수의 v10·v17 규칙을 뺀다(`--v10-only`면 v10만). `submissions/20260927_vague_perf_no_private`·`_no_v10q` |

## 요점

- **서버 경로 주입 시험이 없었다.** 지금까지 주입 시험은 `decide(rec, "", tbl)`(LLM 출력 없음)만 썼다. 이 경로에서는 `merge_facts`가 정규식 사실을 통째로 돌려줘 출처 정책(`ITEM_SOURCE`)이 적용되지 않는다. 앞으로 정규식 보조를 `or`·`and`로 붙이면 `inject_v1_llm.py`·`serverpath_inject.py`처럼 저장된 LLM 출력을 둔 채로 잰다.
- 그 방식으로 찾은 것: v1 정규식 보조가 서버에서 0/60 → 수정 후 60/60(`submissions/20260926_phrase_parser_recall_v1fix`).
- 나머지 정규식 출처 항목(v2·v4·v5·v6·v7·v12·v14·v17·v21·v22)은 LLM 출력 유무와 관계없이 같은 재현율이었다. v14·v17의 '놓침'은 기반 공고가 이미 소기업 수준이거나 경쟁제품(통학운송·행사대행)이라 대상이 아닌 경우였다.
- (09-25 ③) 막연한 실적 요구: 기존 v2 주입 문장은 전부 기간·금액·'동종' 표지가 있어 구멍이 안 보였다. 표지 없는 8종은 기준 10/80 → P2 80/80. 지역+실적(v8) 문장 중 짧은 지역 표현("경상북도에 소재한 실적이 우수한 업체")은 정규식이 못 읽고 지역 전용 호출 몫이다(비관적 주입 20/40).
