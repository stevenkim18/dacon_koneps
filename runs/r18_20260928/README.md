# 09-28 R18 — 09-29 후보 생성·검증 도구

저장소 루트에서 `.venv/bin/python runs/r18_20260928/<파일>`로 실행한다. 결과 패키지: [`submissions/20260929_r18_fresh_holdout`](../../submissions/20260929_r18_fresh_holdout/README.md) · 기록: [study log 09-28 ②](../../docs/05_study_log/20260928/2.%20fresh_holdout_r18.md).

| 파일 | 내용 |
|---|---|
| `make_candidate.py` | `submissions/20260929_r17_edit_shapes/script.py` → R18 규칙(A~F) → V1X → V9X → 머리말. `FLAGS=`·`V1X=`·`V9X=` 스위치 |
| `make_r18rules.py` | A '중 소기업' · B v13·v15 수준 OR · C v4 민간 제외 · D 실적 경험·이력 · E '확인받은 업체' · F v19 '투찰 시·전' · G(기각) 조각 줄 버리기 |
| `v1x.py` · `make_v1x.py` | V1X 틀(정규식 모음)과 후보 스크립트에 끼우는 변형기 |
| `v9cand.py` · `make_v9x.py` | V9X 보조 모델명 호출(제조사·상표·모델 번호 줄 표지, `MODEL2_SEP`로 기존 출력과 이어 decide에 넘김) · `make_v9c.py`(기각한 덧붙이기판) |
| `probe_h6_v1.py` ~ `probe_h9_v1.py` | v1 새 보류 세트(각 세트는 앞 설계 뒤에 작성, H9만 설계에 안 씀) |
| `probe_h10.py` · `probe_inject_h10.py` | 규칙 항목 새 보류 세트 H10(v6 문장은 익명화 형식을 안 따라 무효) |
| `build_v9_probe.py` · `v9probe/` | v9 새 보류 세트 H9(30줄 × 2공고) · MLX 4bit 출력(`base_model_h9`·`v9c_model_*`·`m2_*`) |
| `mlx_calls.py` | 후보 스크립트의 전용 호출 하나(model·model2·item)만 로컬 MLX 4bit로 돌린다 |
| `score_v9.py` · `score_v9x.py` | V9C·V9X 채점(탐침·자연) |
| `fake_runner_test.py` | MockRunner.chat을 JSON 가짜로 바꿔 run() 전 단계(보조 호출 포함)를 돌린다 |
| `v20_scan*.py` · `v24_method*.py` · `v24_amount.py` · `v19_list_scan.py` · `v1x_scan.py` | 기각·판독용 스캔 |
| `validate.sh` · `final_*.log` · `timing.py` | 검증(패키지 `validation.log`로 모음) |
| `load20k.py` | 무라벨 20,000 pickle 캐시(`runs/replay_cache/u20k.pkl`, 없으면 만든다) |
