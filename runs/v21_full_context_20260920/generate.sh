#!/bin/zsh
# dev 200건 로컬 MLX 생성 — 두 단계를 분리해 S1(그물 확장)과 S2(전용 호출)의 효과를 따로 읽는다.
set -u
cd "$(dirname "$0")/../.."
P=.venv/bin/python
S=submissions/20260921_full_context/script.py
OUT=runs/v21_full_context_20260920

echo "=== [1/2] S2만: 09-19 본 호출 출력 + 새 전용 호출 ==="
$P scripts/mlx_eval_extract.py --script $S \
  --outputs runs/mlx/extract_outputs.jsonl \
  --item-outputs runs/mlx/item_outputs.jsonl \
  --model-outputs runs/mlx/model_outputs.jsonl \
  --sme-outputs runs/mlx/v21_sme_dev.jsonl --cv > $OUT/configB_S2only.log 2>&1
echo "[1/2] 종료코드 $?"

echo "=== [2/2] S1+S2: 새 본 호출 출력 + 새 전용 호출 ==="
$P scripts/mlx_eval_extract.py --script $S \
  --outputs runs/mlx/v21_main_dev.jsonl \
  --item-outputs runs/mlx/item_outputs.jsonl \
  --model-outputs runs/mlx/model_outputs.jsonl \
  --sme-outputs runs/mlx/v21_sme_dev.jsonl --cv > $OUT/configC_S1S2.log 2>&1
echo "[2/2] 종료코드 $?"
