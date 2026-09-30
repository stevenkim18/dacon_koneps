# 로컬 실행 결과 (runs)

로컬 MLX(`models/gemma-4-26b-a4b-it-4bit`)로 생성해 둔 모델 출력과 검토 자료다. 규칙만 바꾼 후보는 이 출력을 다시 채점해 평가한다(재생성하면 수 시간이 걸린다). 2026-09-17에 `/tmp/mlx_runs`에서 옮겼다.

제출 ZIP에는 넣지 않는다.

## 폴더 목록 (2026-09-30 정리)

폴더마다 자기 `README.md`가 있으면 링크했다. 없는 것은 이 문서의 해당 절이나 연결된 기록을 본다. 대부분의 도구는 저장소 루트에서 `.venv/bin/python runs/<폴더>/<파일>`로 실행하고, GPU 없이 저장된 출력과 무라벨 20,000 정규식 재생만 쓴다.

| 폴더 | 날짜 | 내용 | 결과물·기록 |
|---|---|---|---|
| `mlx/` | 09-17~ | 로컬 MLX 4bit 기본 출력(dev 200 · 무라벨 250/500)과 dev 전용 호출 출력. 이 문서 아래 `mlx/` 절 | 거의 모든 후보의 재채점 입력 |
| [`review_sme_recall_20260918/`](review_sme_recall_20260918/README.md) | 09-18 | `sme_recall` 제출 전 리뷰 | [`20260919_sme_recall_reviewed`](../submissions/20260919_sme_recall_reviewed/README.md) |
| [`final_20260919/`](final_20260919/README.md) | 09-19 | 09-19 최종 후보(R1+C3+W1+Y1+P+T2), 재추론 없이 재채점 | 미제출 |
| [`item_fallback_20260919/`](item_fallback_20260919/README.md) | 09-19 | v20 제48조 + 품목 meta 대체(R1+C3) | 미제출 |
| [`v20_sw48_20260919/`](v20_sw48_20260919/README.md) | 09-19 | v20 대기업 참여제한 탐지 보강(R1) | 미제출 |
| [`final_20260920/`](final_20260920/README.md) | 09-20 | 기업규모 수준 오독 2종 수정 | 미제출 |
| `v21_full_context_20260920/` | 09-20~21 | 발췌 그물 확장(S1)과 전용 호출(S2)을 나눠 잰 dev 생성. 이 문서 아래 절. `generate.sh`의 후보 폴더는 남아 있지 않다 | S1 기각 · S2 채택 → [`20260921_recall_first`](../submissions/20260921_recall_first/README.md) |
| [`rejected_20260921/`](rejected_20260921/README.md) | 09-21 | 측정으로 기각한 후보 코드(`metacmp` v24 대조 전용 호출, `candlist` 후보 목록 교체) | 기각 |
| `v22_focused_20260921/` | 09-21 | 실적·지역 전용 호출 dev 생성(`generate.sh` · `dev.log` · `exp_tight_gate.py`) | 지역 채택 · 실적 기각 → [`20260922_focused_calls`](../submissions/20260922_focused_calls/README.md) |
| `v22_goods_20260921/` | 09-21 | 물품 품목 전용 호출 dev 생성 | 기각([`submissions/README.md`](../submissions/README.md) '닫힌 문') |
| `v24_metacmp_20260921/` | 09-21 | v24 대조 전용 호출 dev 생성과 변형(`exp_*.py`). 해석은 `rejected_20260921/README.md` | 판정 변화 0건, 기각 |
| `thinking_20260922/` | 09-22 | Gemma 4 thinking 모드 시험. 이 문서 아래 09-22 절 | 기각 |
| [`cloud_int8_20260923/`](cloud_int8_20260923/README.md) | 09-23 | 클라우드 int8(서버와 같은 vLLM·양자화) dev 200 실행 | int8 dev 0.8468 |
| [`cloud_int8_exp/`](cloud_int8_exp/README.md) | 09-23 | int8 실험 묶음(실적·물품 호출 재시험, LLM 직접 판정) | 전부 기각 |
| [`int8_port_20260923/`](int8_port_20260923/README.md) | 09-23 | int8 출력 형식 보정 도구·변형(`devtool.py`는 이후 도구들이 함께 씀) | [`20260924_int8_quote_port`](../submissions/20260924_int8_quote_port/README.md) |
| [`edit_model_20260923/`](edit_model_20260923/README.md) | 09-23 | 편집 공고 모형 실험(압축을 푼 `open/dev.jsonl`을 읽는다) | [`20260924_edit_model_combo`](../submissions/20260924_edit_model_combo/README.md)(보류) |
| [`review_20260924/`](review_20260924/README.md) | 09-24 | 09-24 검토 도구. `devscore.sh`(dev 재채점 3벌)는 이후 후보 검증에도 썼다 | study log 09-24 ①② |
| [`sme_sentence_20260924/`](sme_sentence_20260924/README.md) | 09-24 | 평가셋 구성 적합 · int8/4bit 차이 · 여러 줄 기업규모 문장 · v17 수의계약 | [`20260927_sme_sentence_v17`](../submissions/20260927_sme_sentence_v17/README.md) |
| [`review_20260925/`](review_20260925/README.md) | 09-25 | 후보 재검토(서버 경로) · 안전망 · 소액수의 대비판 생성기 | [`20260926_private_scope_safetynet`](../submissions/20260926_private_scope_safetynet/README.md) 등 |
| [`scope_audit_20260925/`](scope_audit_20260925/README.md) | 09-25 | 법령 적용 범위 전수 대조 · 편집 문장 재현율 | [`20260927_private_scope_recall`](../submissions/20260927_private_scope_recall/README.md) |
| [`review_20260926/`](review_20260926/README.md) | 09-26 | 09-27 후보 재검토 | [`20260927_scope_cleanup`](../submissions/20260927_scope_cleanup/README.md) |
| [`recall_probe_20260926/`](recall_probe_20260926/README.md) | 09-26 | 새 표현 주입 탐침 R1~R9(+R14 `make_round3.py`) | [`20260927_scope_recall`](../submissions/20260927_scope_recall/README.md) · [`20260928_plus_r3`](../submissions/20260928_plus_r3/README.md) |
| [`wrapjoin_20260927/`](wrapjoin_20260927/README.md) | 09-27 | 줄바꿈 문장 이어 읽기(W)와 R15 | [`20260928_wrap_r15`](../submissions/20260928_wrap_r15/README.md) |
| [`r16_20260927/`](r16_20260927/README.md) | 09-27 | 제외어가 지우던 자격 문장 되살리기(R16) | [`20260928_wrap_r16`](../submissions/20260928_wrap_r16/README.md) |
| [`del_probe_20260928/`](del_probe_20260928/README.md) | 09-28 | 지우기·바꾸기 편집 탐침(정규식 경로) | [`20260929_r17_edit_shapes`](../submissions/20260929_r17_edit_shapes/README.md) |
| [`r17_20260928/`](r17_20260928/README.md) | 09-28 | R17 후보 생성·검증 | [`20260929_r17_edit_shapes`](../submissions/20260929_r17_edit_shapes/README.md) |
| [`r18_20260928/`](r18_20260928/README.md) | 09-28 | R18 새 보류 세트로 다시 재기 | [`20260929_r18_fresh_holdout`](../submissions/20260929_r18_fresh_holdout/README.md)(최종 제출) |
| `replay_cache/` | — | `scripts/replay_unlabeled.py` 판정 캐시. **git 제외**, 지워도 다시 만들어진다 | — |

루트의 로그·스크립트: `queue_20260921.sh`·`.log`(09-21 GPU 직렬 큐) · `v21_sme_unlabeled.log` · `v22_region_unlabeled.log`(무라벨 전용 호출 생성) · `v22_candlist_20260921.log`·`v22_candlist_score.log`(후보 목록 교체, 기각) · `win_dev_20260921.log`(원문 전체 창 분할, 기각) · `gate_ablation_20260922.log`(아래 09-22 절).

## mlx/

### rule_extract 계열 (현재 후보가 쓰는 출력)

| 파일 | 건수 | 내용 |
|---|---:|---|
| `extract_outputs.jsonl` · `extract_run.log` | 200 | dev 본 호출(사실 추출 JSON) |
| `item_outputs.jsonl` · `item_run.log` | 122 | dev 용역 품목 판별 호출 |
| `model_outputs.jsonl` · `model_dev_run.log` · `model_dev_score0.log` | 59 | dev 물품 모델명(v9) 판별 호출 |
| `extract_test.jsonl` | 3 | 추출 호출 동작 확인용 시험 출력 |
| `train_sample250.jsonl` | 250 | 무라벨 표본(`labels/README.md` 생성 절차 1) |
| `train250_main.jsonl` · `train250_item.jsonl` · `train250_model.jsonl` · `train250_run.log` · `model_train_run.log` | 250 · 153 · 55 | 무라벨 표본의 본·품목·모델명 호출 |
| `audit250.txt` · `audit250_todo.txt` | — | `scripts/audit_unlabeled.py` 검토 자료(라벨 작성에 사용) |
| `audit500.txt` | — | 추가 500건의 `scripts/audit_unlabeled.py` 검토 자료(2026-09-18 생성, sme_level 기준 154쌍). 라벨 미작성 |
| `train_sample500_next.jsonl` | 500 | 무라벨 추가 표본: 250건 표본과 같은 섞기(`random.Random(20260917).shuffle`)의 251~750번째. 기존 표본과 겹침 0건 |
| `train500_main.jsonl` · `train500_item.jsonl` · `train500_model.jsonl` · `train500_run.log` | 500 · 317 · 92 | 추가 표본의 본·품목·모델명 호출(2026-09-17 23:56 ~ 09-18 02:29, sme_level 프롬프트 = audit_v9와 동일). 본 호출 JSON 불량 1건(PPS-D-014168). **라벨 미작성**: sme_level 기준 판정 154쌍(공고 115건) |

```bash
python scripts/mlx_eval_extract.py --outputs runs/mlx/extract_outputs.jsonl \
    --item-outputs runs/mlx/item_outputs.jsonl --model-outputs runs/mlx/model_outputs.jsonl --score-only --cv
python scripts/audit_unlabeled.py --sample runs/mlx/train_sample250.jsonl \
    --outputs runs/mlx/train250_main.jsonl --item-outputs runs/mlx/train250_item.jsonl \
    --model-outputs runs/mlx/train250_model.jsonl --labels labels/train250_audit.csv --report

# 추가 500건 생성(중단 시 같은 명령으로 이어서 실행)
caffeinate -is python scripts/mlx_eval_extract.py --dev runs/mlx/train_sample500_next.jsonl \
    --outputs runs/mlx/train500_main.jsonl --item-outputs runs/mlx/train500_item.jsonl \
    --model-outputs runs/mlx/train500_model.jsonl --generate-only
```

### 베이스라인 계열 (폐기 후보 기록)

| 파일 | 건수 | 내용 |
|---|---:|---|
| `baseline_outputs.jsonl` · `baseline.log` · `baseline_report.json` | 128 | 공식 베이스라인 방식 dev 층화 표본(`scripts/mlx_eval_dev.py`) |
| `attach_outputs.jsonl` · `attach.log` · `attach_report.json` · `attach_v2.log` · `attach_v2_report_sim.json` | 128 | attachment_excerpt 후보(study log 1~3) |

### 기타

- `hwpx/`: `open/data/법령패키지/중기부고시/중기부고시_경쟁제품_제2025-96호.hwpx` 압축 해제본(고시 본문 확인용)

## v21_full_context_20260920/ — 09-21 후보의 구성별 측정 (2026-09-20~21)

전용 호출(S2)과 발췌 그물 확장(S1)의 효과를 **분리해서** 재기 위해 dev 200건을 두 벌 생성했다.
생성 스크립트는 `generate.sh`(두 단계 순차 실행).

| 파일 | 건수 | 내용 |
|---|---:|---|
| `runs/mlx/v21_sme_dev.jsonl` | 200 | 기업규모·직생 전용 호출 출력. **8.6초/건** |
| `runs/mlx/v21_main_dev.jsonl` | 200 | 그물 확장(S1) 프롬프트로 재생성한 본 호출 출력. 3,635초(61분) = **21.4초/건**, 프롬프트 평균 4,957토큰 |

구성별 dev 점수(모두 `submissions/20260921_recall_first/script.py`로 채점):

| 구성 | 본 호출 | 전용 호출 | dev macro | 교차검증 |
|---|---|---|---:|---:|
| A 기준 | `extract_outputs.jsonl` | — | 0.8366 | 0.8075 |
| B 전용호출·게이트 없음 | 같음 | `v21_sme_dev` | 0.8197 | 0.8064 |
| **B2 전용호출·게이트** | 같음 | 같음 | **0.8393** | **0.8114** |
| C1 S1만 | `v21_main_dev` | — | 0.8299 | 0.7927 |
| C2 S1+S2 | 같음 | `v21_sme_dev` | 0.8330 | 0.7966 |

→ **S1 기각**(-0.006 dev·-0.015 cv, v14·v18 정탐 손실), **S2 채택**.
`configC_S1S2.log`는 프로세스 시작 시점의 게이트 없는 스크립트로 채점된 값이므로 `configC2_gated.log`를 본다.

규칙 변형 실험 파일(채점 전용, 제출에 넣지 않는다):

| 파일 | 내용 | 판정 |
|---|---|---|
| `exp_perf_noamount.py` | 실적 금액 요건 완전 제거 | 기각(dev -0.0186) |
| `exp_perf_v2.py` | 금액 → 구체성 표지 + 제외 규칙 | **채택**(후보에 반영) |
| `exp_meta_item.py` | 위 + 메타 세부품명번호 우선 | **채택**(후보에 반영) |
| `exp_omnibus_gate.py` | 위 + 본 호출 근거에도 같은 게이트 | 기각(dev -0.0060) |

## 2026-09-22 — 규칙 재생 도구·게이트 절제·thinking 모드

| 경로 | 내용 |
|---|---|
| `gate_ablation_20260922.log` | `scripts/gate_ablation.py` 무라벨 20,000건 전수(13분, 기준 `20260922_focused_calls`). 게이트 15개를 하나씩 끈 Δ양성. 해석은 [study log 09-22 ①](../docs/05_study_log/20260922/1.%20rule_levers_swept_and_lost_port.md) §4 |
| `replay_cache/` | `scripts/replay_unlabeled.py`의 판정 캐시(스크립트 내용 해시별 pickle)와 변경 공고 목록 `changed_*.pkl`. 지워도 다시 만들어진다 |
| `thinking_20260922/` | **기각된** Gemma 4 thinking 모드 시험. `think_gen.py`(2단계 생성: 스키마 없이 생각 1,024토큰 → 같은 JSON 스키마로 답), dev 출력 `think_item_dev.jsonl`(용역 품목 122건) · `think_model_dev.jsonl`(모델명 59건). 각 줄에 `thought`·`think_tokens`·`t_think`·`t_answer` 포함 |

thinking 결과(후보 `20260923_v22_region_fix` 기준 dev 0.8706): 품목 호출 **0.8715**(+0.0009, v10·v11 정탐 +1씩 / v12 오탐 +1 / v13 정탐 −1),
모델명 호출 **0.8631**(−0.0075, v9 오탐 2 → 6). 로컬 건당 약 32초·17초(기존 약 9초). 재채점 명령:

```bash
.venv/bin/python scripts/mlx_eval_extract.py --script submissions/20260923_v22_region_fix/script.py \
  --outputs runs/mlx/extract_outputs.jsonl --item-outputs runs/thinking_20260922/think_item_dev.jsonl \
  --model-outputs runs/mlx/model_outputs.jsonl --sme-outputs runs/mlx/v21_sme_dev.jsonl \
  --region-outputs runs/mlx/v22_region_dev.jsonl --score-only --cv
```

(`think_*_dev.jsonl`은 `text` 외 필드도 있지만 `mlx_eval_extract.py`는 `id`·`text`만 읽는다.)

### 새 검증 도구 (scripts/)

- `scripts/replay_unlabeled.py BASE.py VAR.py …` — 무라벨 20,000 정규식 경로 재생, 후보 간 항목별 Δ양성·변경 공고·예외 수.
- `scripts/eval_unlabeled750.py BASE.py VAR.py` — 무라벨 750 전 파이프라인(저장 출력) 판정 차이를 손라벨과 함께 출력.
- `scripts/evidence_audit.py SCRIPT.py` — 근거 문구 전수 검사(dev 200 · 무라벨 750).

## 2026-09-23 — 클라우드 int8(RunPod L40S) 실행

로컬 MLX 4bit 대신 **대회 서버와 같은 vLLM 0.26 · int8 · 모델 리비전**으로 돌린 출력이다. 절차는 [`cloud/README.md`](../cloud/README.md).

| 경로 | 내용 |
|---|---|
| [`cloud_int8_20260923/`](cloud_int8_20260923/README.md) | 제출 후보 `20260924_v20_quote_region35`의 dev 200 실행. int8 dev **0.8468**(로컬 4bit 0.8706) · 교차 0.8016 · v9 오탐 2→10 |
| [`cloud_int8_exp/`](cloud_int8_exp/README.md) | dev 200 + 무라벨 750 실험 묶음(실적·물품 호출 재시험, LLM 직접 판정, 판정+dev 사례). **전부 규칙보다 낮아 기각** |

재채점(GPU 불필요):

```bash
R=runs/cloud_int8_20260923/dev/raw
.venv/bin/python scripts/mlx_eval_extract.py --script submissions/20260924_v20_quote_region35/script.py \
  --outputs $R/main.jsonl --item-outputs $R/item.jsonl --model-outputs $R/model.jsonl \
  --sme-outputs $R/sme.jsonl --region-outputs $R/region.jsonl --score-only --cv [--dump-preds preds.json]
.venv/bin/python scripts/judge_combine.py --raw runs/cloud_int8_exp/exp/raw
```

`--dump-preds`(09-23 추가)는 최종 판정을 `{id: {v: 0/1}}` JSON으로 저장한다.
**주의:** 로컬 4bit 기준을 잴 때 품목 출력은 `runs/mlx/item_outputs.jsonl`을 쓴다. `thinking_20260922/think_item_dev.jsonl`을 넣으면 기각된 thinking 출력이 섞여 0.8715가 나온다(09-23에 한 번 잘못 인용했다).

### int8 출력 형식 보정 (09-23 저녁, GPU 불필요)

[`int8_port_20260923/`](int8_port_20260923/README.md) — 위 int8 원본 출력으로 판정기 변형을 잰 도구와 변형 스크립트.
int8은 여러 줄 인용을 한 줄로 이어 붙이고(정확 일치 검사에서 탈락) 공고서 업종코드 칸에 meta 값을 베끼기도 한다.
보정본 int8 dev 0.8468 → **0.8583** · 교차 0.8016 → 0.8327(두 번째 실행 0.8410 → 0.8525), 4bit 0.8706 그대로 → [`submissions/20260924_int8_quote_port`](../submissions/20260924_int8_quote_port/README.md).
