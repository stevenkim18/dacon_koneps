# SME 출력 예산 일치 후보

상태: **미제출 · 대체됨(2026-09-21).** 같은 버그를 **모든 전용 호출로 확장해 고친** `20260922_focused_calls`가 이 후보를 대신한다 — 이 후보는 기업규모만 400으로 올렸는데, 실측하면 지역 호출도 23%가 128을 넘고 기업규모는 400에서도 잘린다(512로 잡음).

원래 설명: 기준은 `20260921_recall_first`(Public 0.6839532054, 43분 26초). 작성일 2026-09-21.

## 변경

기업규모·직생 전용 호출만 최대 출력 128 → 400토큰으로 변경했다. 로컬 MLX 평가 설정(400)과 일치시킨다. 본 호출 1200, 품목·모델명 128, 프롬프트·판정·시간 예산은 유지한다. 호출마다 종료 사유와 출력 토큰 수를 집계해 기록한다. 이 집계는 진단 로그이며 예측 보정에 사용하지 않는다.

## 확인한 결과

- `validation.log`: 저장된 dev 200건을 같은 출력으로 재생했을 때 판정·근거·본 호출 프롬프트 변경 0건. 가짜 vLLM 백엔드로 실제 chat 메서드의 예산 선택(1200/400/128/128)을 확인했다. 실제 GPU 추론 시험은 아니다.
- 저장된 `v21_sme_dev.jsonl`을 로컬 모델 tokenizer.json으로 재토큰화: 200건 중 159건이 128토큰 초과, 중앙값 175, 최대 400. 유효 JSON 198/200. 이는 서버 잘림 건수가 아니며 400토큰도 완성을 보장하지 않는다.
- `dev_validation.log`: 저장된 MLX 출력 재채점 macro F1 0.8307, 교차검증 0.8034. 24항목별 F1·TP/FP/FN은 로그에 수록. 기준과 동일하며 새 서버 점수 예측이 아니다.
- `mock_validation.log`: 배포 샘플 10건, 환경변수 입력·출력 경로, 49열 CSV 자가검증 PASS. 모델 없는 실행 약 0.2초. 실제 추론 시간과 무관하다.
- ZIP은 script.py·requirements.txt만 포함. 기존 최고 후보 ZIP은 수정하지 않았다.
- ZIP SHA-256: `3a01257ff38bf6eb6b24d243f4833fd801e6ccafa65b43c16a185d66c7b151ad`. 압축 무결성 검사 통과.

## 재현

저장소 루트에서:

```sh
.venv/bin/python submissions/20260921_sme_output_budget/validate.py
.venv/bin/python scripts/mlx_eval_extract.py --script submissions/20260921_sme_output_budget/script.py --dev open/dev.jsonl.gz --outputs runs/mlx/extract_outputs.jsonl --item-outputs runs/mlx/item_outputs.jsonl --model-outputs runs/mlx/model_outputs.jsonl --sme-outputs runs/mlx/v21_sme_dev.jsonl --score-only --cv
PPS_DATA_DIR="$PWD/open/data" PPS_OUTPUT_DIR="$PWD/submissions/20260921_sme_output_budget/mock_output" .venv/bin/python submissions/20260921_sme_output_budget/script.py --mock
```

## 미확인과 다음 확인

Public 점수·실제 서버 소요 시간·서버 전용 호출 JSON 완성률은 미측정. 새 로컬 추론은 수행하지 않았다(기존 로컬 출력이 이미 400토큰 설정으로 생성됨). 서버에서 단계4의 유효 JSON 수, 출력진단의 length 종료 수, 단계별 시간과 Public을 기준 후보와 비교해야 한다. 점수 상승은 보장하지 않는다.

기존 시간 관리의 필수 본 호출 중단 가능성 및 2시간 초과 위험은 이번 단일 변경으로 해결하지 않았다. 100분 내부 예산 유지. 추후 추가 추론을 크게 늘리기 전에 필수 호출 완료 보장을 별도로 보완해야 한다. CSV 선기록만으로 정상 호출 요건이나 시간 초과를 해결할 수 없다.

제출 ID·시각: 없음. 채택 여부: 서버 결과 후 결정.
