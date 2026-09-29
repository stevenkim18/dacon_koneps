# 09-28 R17 — 09-29 후보 생성·검증 도구

저장소 루트에서 `.venv/bin/python runs/r17_20260928/<파일>`로 실행한다. 결과 패키지: [`submissions/20260929_r17_edit_shapes`](../../submissions/20260929_r17_edit_shapes/README.md) · 기록: [study log 09-28 ①](../../docs/05_study_log/20260928/1.%20edit_shape_probes_and_r17.md).

| 파일 | 내용 |
|---|---|
| `make_candidate.py` | `submissions/20260928_wrap_r16/script.py` → R17 전체 → 머리말. 스위치로 변경을 켜고 끈다(기본 전부 켬) |
| `make_r17.py` | GN(meta 인용 근거 버림 + v11 수준 LLM∨정규식) · B(입찰방식 요약 줄 머리말) · A(부정문) · D(실적 '있을 것'·'※' 줄) |
| `var_v1w.py` · `var_v1s.py` | v1 기관 유형 한정 · 인원 규모 요건 |
| `var_v24f.py` · `var_v19b.py` · `var_v12p.py` | v24 예산 억·백만 표기 · v19 '입찰 전' · v12 괄호 주석 어미 |
| `var_f3s.py` · `var_gl2.py` | 품목 호출 코드(서류 목록이 직생 증명서를 요구할 때) · 본 호출 기업규모 근거 줄 거름 |
| `var_fusion.py` · `var_f2.py` · `var_ground.py` · `var_ground2.py` · `var_v11level.py` | 기각한 변형(F·F2·F3·G·G2) — README '검토하고 넣지 않은 것' |
| `probe_n3.py` | 자연 줄 탐침 N3(v3 금액 바꾸기 · v4 공공 발주처 줄 · v5) |
| `probe_h5_v1.py` | V1W 설계 뒤 새로 쓴 v1 보류 세트 H5(18문장) |
| `build_llm_probe.py` · `score_llm_probe.py` | LLM 경로 편집 탐침 172건 생성·채점(`llm_probe/`: `probe.jsonl`, `b4_*.jsonl` MLX 4bit 출력, `score_final.log`) |
| `header_only_count.py` · `sme_negation_count.py` | 요약 줄뿐인 자연 공고 · 부정문 근거 공고 세기 |
| `final_*.log` | 최종 후보 검증 로그(패키지 `validation.log`로 모음) |

MLX 재생성: `scripts/mlx_eval_extract.py --script <후보> --dev runs/r17_20260928/llm_probe/probe.jsonl --outputs …/b4_main.jsonl --item-outputs … --model-outputs … --sme-outputs … --generate-only`(본 호출 약 20초/건).
