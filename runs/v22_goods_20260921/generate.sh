#!/bin/zsh
set -u
cd "$(dirname "$0")/../.."
.venv/bin/python scripts/mlx_eval_extract.py --script submissions/20260922_focused_calls/script.py \
  --outputs runs/mlx/extract_outputs.jsonl --item-outputs runs/mlx/item_outputs.jsonl \
  --model-outputs runs/mlx/model_outputs.jsonl --sme-outputs runs/mlx/v21_sme_dev.jsonl \
  --region-outputs runs/mlx/v22_region_dev.jsonl --goods-outputs runs/mlx/v22_goods_dev.jsonl --cv
