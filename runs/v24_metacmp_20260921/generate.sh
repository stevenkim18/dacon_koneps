#!/bin/zsh
set -u
cd "$(dirname "$0")/../.."
.venv/bin/python scripts/mlx_eval_extract.py --script submissions/20260922_metacmp/script.py \
  --outputs runs/mlx/extract_outputs.jsonl --item-outputs runs/mlx/item_outputs.jsonl \
  --model-outputs runs/mlx/model_outputs.jsonl --sme-outputs runs/mlx/v21_sme_dev.jsonl \
  --region-outputs runs/mlx/v22_region_dev.jsonl \
  --metacmp-outputs runs/mlx/v24_metacmp_dev.jsonl --cv
