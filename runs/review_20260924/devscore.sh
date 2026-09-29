#!/bin/zsh
# dev 200 재채점 3벌(4bit·int8 단독·int8 950묶음). 사용: zsh runs/review_20260924/devscore.sh submissions/<후보>/script.py
S=$1
PY=.venv/bin/python
score() {  # $1=label $2=main $3=item $4=model $5=sme $6=region
  out=$($PY scripts/mlx_eval_extract.py --script $S --score-only --cv --outputs $2 --item-outputs $3 --model-outputs $4 --sme-outputs $5 --region-outputs $6 2>&1)
  final=$(echo "$out" | grep -E "^macro" | awk '{print $NF}')
  cv=$(echo "$out" | grep "교차 검증 평균" | awk '{print $NF}')
  echo "$1: macro $final · 교차 $cv"
}
score "4bit    " runs/mlx/extract_outputs.jsonl runs/mlx/item_outputs.jsonl runs/mlx/model_outputs.jsonl runs/mlx/v21_sme_dev.jsonl runs/mlx/v22_region_dev.jsonl
D=runs/cloud_int8_20260923/dev/raw
score "int8단독" $D/main.jsonl $D/item.jsonl $D/model.jsonl $D/sme.jsonl $D/region.jsonl
E=runs/cloud_int8_exp/exp/raw
score "int8묶음" $E/main.jsonl $E/item.jsonl $E/model.jsonl $E/sme.jsonl $E/region.jsonl
