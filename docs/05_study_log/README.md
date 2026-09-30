# 연구 일지 목록

대회 기간(2026-09-15~09-28)에 날마다 쓴 실험·판단 기록 48편이다. 제목은 각 문서의 첫 줄이다. ★는 [대회 회고](../06_wrap_up/01_retrospective.md)가 근거로 링크한 문서다.
제출 결과와 후보는 [`submissions/README.md`](../../submissions/README.md), 도구와 출력은 [`runs/README.md`](../../runs/README.md)에 있다.

## 2026-09-15

- [PPS-DEV-01 읽기](20260915/1.%20read_pps-dev-01.md)
- [Python으로 공고 읽기](20260915/2.%20read_dev_python.md)
- [첫 제출 결과와 피드백](20260915/3.%20first_submission.md)
- [모델에 전달할 문서 확인](20260915/4.%20inspect_context.md)

## 2026-09-16

- [두 번째 제출: balanced context 결과](20260916/1.%20balanced_context_submission.md)

## 2026-09-17

- [로컬 MLX 추론 확보 + attachment_excerpt 후보 항목별 F1 비교](20260917/1.%20mlx_local_eval_attachment_excerpt.md)
- [dev 재분석: v22/v23 적용 조건 오표기, v13 대량 오탐 원인, 근거 문구 희소성](20260917/2.%20dev_reanalysis_v13_v22_v23.md)
- [금액 구간 게이트 + 판로지원법 항목(v14·v15·v16·v18) 규칙 판정](20260917/3.%20meta_price_gates_and_sme_rules.md)
- ★ [처음부터 다시 분석: 라벨은 "법 조문의 기계적 적용"이다](20260917/4.%20from_scratch_reanalysis.md)
- [평가셋 분포 추정과 기업규모 판정 정리](20260917/5.%20test_distribution_and_sme_level.md)

## 2026-09-18

- ★ [sme_level Public 점수와 "로컬 개선이 얼마나 전달되는가"](20260918/1.%20sme_level_public_score.md)
- [튜닝에 쓰지 않은 500건에서 오탐 사냥하기](20260918/2.%20false_positive_hunt_on_untuned_500.md)
- [제한경쟁 게이트를 법 조문으로 대체하기](20260918/3.%20sme_level_recall_and_the_law.md)

## 2026-09-19

- [전달률은 상수가 아니다 — 0.32 구간과 0.57 구간](20260919/1.%20transfer_rate_two_regimes.md)
- [2026-09-19 토크 게시판 추가 답변과 구현 영향](20260919/2.%20talkboard_corrections.md)
- [v10 품목 융합 규칙 — 변형 4종을 재채점하고 전부 기각](20260919/2.%20v10_item_fusion_variants.md)
- [2026-09-19 저장 출력만으로 잰 규칙 후보 3건 — 셋 다 기각, 대신 법령 근거 2건 확보](20260919/3.%20cheap_rule_candidates_closed.md)
- [2026-09-19 v20 — 좁혀야 할 것은 `is_software`가 아니라 대기업 참여제한 탐지였다](20260919/4.%20v20_sw48_detection.md)
- [2026-09-19 오답은 항목이 아니라 공고에 뭉쳐 있다 — meta 증언으로 품목 되살리기](20260919/5.%20item_code_meta_fallback.md)
- [2026-09-19 운영 답변·항목표를 코드와 한 줄씩 대조](20260919/6.%20talkboard_recheck.md)
- [2026-09-19 품목 판정 — 로직은 남아 있었고, 프롬프트는 닫혔다](20260919/7.%20item_code_and_prompt.md)
- [2026-09-19 무라벨 500건 라벨링이 찾아낸 것 — 기업규모 탐지 실패](20260919/8.%20sme_level_detection_on_500.md)

## 2026-09-20

- ★ [2026-09-20 교차검증이 Public을 예측하지 못한다 — 그리고 우리 측정 도구는 정밀도만 잰다](20260920/1.%20cv_no_longer_predicts_public.md)
- [2026-09-20 ② 2시간 예산은 70%가 비어 있고, 채택 규칙이 점수를 깎고 있었다](20260920/2.%20two_hour_budget_and_f1_asymmetry.md)

## 2026-09-21

- [2026-09-21 ① 누락 측정 도구를 만들었고, `rx_performance`의 금액 요건이 v2·v4·v8의 재현율을 막고 있었다](20260921/1.%20recall_probe_and_perf_amount_gate.md)
- ★ [2026-09-21 ② F1/2 규칙이 실전에서 확인됐다 — dev가 내려가고 Public이 올랐다](20260921/2.%20f1_half_rule_confirmed.md)
- ★ [2026-09-21 ③ 전용 LLM 호출은 '법이 어휘를 고정한 사실'에서만 작동한다 — 4전 1승](20260921/3.%20focused_calls_closed_vocabulary_law.md)
- [4. 원문 전체 창 분할을 닫고, v20 금액 하한의 법 근거가 없음을 찾다](20260921/4.%20window_sweep_closed_and_v20_lower_bound.md)

## 2026-09-22

- [2026-09-22 ① 규칙 쪽 레버를 전수 측정하다 — 빠졌던 이식 3건과 v20 하한, 그리고 닫힌 문들](20260922/1.%20rule_levers_swept_and_lost_port.md)
- [2026-09-22 ② dev에서는 안 보이는 '개념 혼동' 오탐 — v22·지역·v4](20260922/2.%20concept_confusion_invisible_in_dev.md)
- [2026-09-22 토크 게시판 재확인](20260922/3.%20talkboard_recheck.md)

## 2026-09-23

- ★ [2026-09-23 ① 105위 — 규칙 미세조정으로는 닿지 않는다. 서버와 같은 int8 환경을 빌려 원인을 잰다](20260923/1.%20leaderboard_gap_and_cloud_int8_plan.md)
- ★ [2026-09-23 ② dev는 '위반 공고 91건 + 5월 공고 109건'이다 · 서버(int8)에서만 버려지던 인용을 되살렸다](20260923/2.%20dev_structure_and_int8_quote_port.md)
- [2026-09-23 ③ 상위권 가설 1·2(대량 자가 라벨·비슷한 공고 검색)를 작게 시험했다 — 자연 분포 재현율에는 구멍이 없다](20260923/3.%20h1_h2_trials_closed.md)
- ★ [2026-09-23 ④ 아무도 안 읽은 조문 — 국가계약에도 v8(실적+지역 중복 제한 금지)이 있다](20260923/4.%20unread_law_articles_v8_national.md)
- ★ [2026-09-23 ⑤ dev의 위반 공고는 '실제 공고를 고쳐 만든 것'이다 — 0.78까지의 경로를 이 구조로 다시 잰다](20260923/5.%20edited_notices_dataset_model.md)

## 2026-09-24

- [2026-09-24 ① int8_quote_port 0.6908 — 결과 해석과 09-25 후보](20260924/1.%20int8_quote_port_result_and_next.md)
- [2026-09-24 ② 전략 재검토 — 자연 비용 0인 표현 확장, 그리고 기각한 세 방안](20260924/2.%20rereview_zero_cost_broadening.md)
- [2026-09-24 ③ 표현·파서 구멍 찾기 — 주입 시험으로 찾고, 자연 공고를 읽어 거른다](20260924/3.%20phrase_parser_hunt.md)
- ★ [2026-09-24 ④ 평가셋 구성 적합 · 서버(int8)에서만 늘어나는 v1·v9 · 여러 줄 기업규모 문장과 v17 수의계약](20260924/4.%20sme_sentence_join_and_v17_private.md)

## 2026-09-25

- [2026-09-25 ① v8nat 0.7053 — 결과 해석, 적용 범위 전수 대조, 소액수의·편집 재현율 후보](20260925/1.%20v8nat_result_and_scope_audit.md)
- [2026-09-25 ② 09-26·09-27 후보 재검토 — 서버 경로에서 v1 정규식 보조가 꺼져 있었다](20260925/2.%20candidate_rereview_server_path.md)
- [2026-09-25 ③ 09-26 제출본 재확인 — 막연한 실적 요구(P2)와 09-27 대비판](20260925/3.%20vague_perf_and_contingency.md)

## 2026-09-26

- [2026-09-26 ① safetynet_vague_perf 0.7066 — 결과 해석과 09-27 선택](20260926/1.%20safetynet_vague_perf_result.md)

## 2026-09-27

- [2026-09-27 ① 09-27 결과 0.7139 이후: 줄바꿈 구조 구멍(W)과 4차 표현(R15) → 09-28 wrap_r15](20260927/1.%20wrapjoin_structural_hole_and_r15.md)
- [2026-09-27 ② 실제 공고 자격 줄로 잰 구멍 — 제외어가 지우던 자격 문장(R16) → 09-28 wrap_r16](20260927/2.%20natural_line_probe_and_r16.md)

## 2026-09-28

- [2026-09-28 ① 09-28 결과 0.7202 이후: 지우기·바꾸기 편집 탐침(R17) → 09-29 r17_edit_shapes](20260928/1.%20edit_shape_probes_and_r17.md)
- ★ [2026-09-28 ② 새 보류 세트로 다시 재기 → 09-29 r18_fresh_holdout](20260928/2.%20fresh_holdout_r18.md)
