#!/bin/zsh
# 실적·지역 전용 호출을 dev 200건에 생성한다. 기존 본·품목·모델명·기업규모 출력은 재사용한다
# (본 호출 프롬프트가 09-21 후보와 동일하므로 새 추론은 두 전용 호출뿐이다).
set -u
cd "$(dirname "$0")/../.."
.venv/bin/python scripts/mlx_eval_extract.py --script submissions/20260922_focused_calls/script.py \
  --outputs runs/mlx/extract_outputs.jsonl \
  --item-outputs runs/mlx/item_outputs.jsonl \
  --model-outputs runs/mlx/model_outputs.jsonl \
  --sme-outputs runs/mlx/v21_sme_dev.jsonl \
  --perf-outputs runs/mlx/v22_perf_dev.jsonl \
  --region-outputs runs/mlx/v22_region_dev.jsonl --cv
