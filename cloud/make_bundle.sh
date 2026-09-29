#!/usr/bin/env bash
# (Mac에서 실행) 클라우드로 올릴 묶음 cloud_bundle.tar.gz를 만든다. 모델은 넣지 않는다(클라우드에서 직접 받는다).
set -euo pipefail
cd "$(dirname "$0")/.."
tar -czf cloud_bundle.tar.gz \
  cloud/script_dump.py cloud/score_csv.py cloud/setup.sh cloud/run_dev.sh cloud/run_750.sh cloud/run_exp.sh cloud/cases.json \
  submissions/20260924_v20_quote_region35/script.py \
  open/data open/dev.jsonl.gz open/dev_labels.csv open/exp950.jsonl.gz \
  runs/mlx/train_sample250.jsonl runs/mlx/train_sample500_next.jsonl
ls -lh cloud_bundle.tar.gz
