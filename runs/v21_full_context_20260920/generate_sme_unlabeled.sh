#!/bin/zsh
# 전용 호출(S2)을 튜닝에 쓰지 않은 무라벨 750건에 돌린다.
# 목적: v16·v18(부재탐지·정밀도 0.88·양성 최다) 정탐을 깎지 않는지 기존 감사 라벨로 확인.
set -u
cd "$(dirname "$0")/../.."
P=.venv/bin/python
S=submissions/20260921_recall_first/script.py
for n in 250 500; do
  src=runs/mlx/train_sample${n}.jsonl
  [ $n = 500 ] && src=runs/mlx/train_sample500_next.jsonl
  echo "=== 무라벨 ${n}건 전용 호출 생성 ==="
  $P scripts/mlx_eval_extract.py --script $S --dev $src \
    --outputs runs/mlx/train${n}_main.jsonl \
    --item-outputs runs/mlx/train${n}_item.jsonl \
    --model-outputs runs/mlx/train${n}_model.jsonl \
    --sme-outputs runs/mlx/train${n}_sme.jsonl --generate-only
  echo "[$n] 종료코드 $?"
done
