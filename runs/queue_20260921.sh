#!/bin/zsh
# GPU 직렬 큐: 앞 작업이 끝나면 이어서 돌린다. 각 단계는 append 모드라 중단 후 재실행하면 이어진다.
set -u
cd "$(dirname "$0")/.."
P=.venv/bin/python
log() { print -r -- "[queue $(date +%H:%M)] $*" }

# 0) 진행 중인 생성이 있으면 기다린다
while pgrep -f mlx_eval_extract.py >/dev/null; do sleep 20; done
log "선행 작업 종료 확인"

# 1) C: 본 호출 후보 목록 교체 — dev 200건 재추론(약 70분)
log "C 시작: 후보 목록 교체 본 호출 재생성"
$P scripts/mlx_eval_extract.py --script submissions/20260922_candlist/script.py \
  --outputs runs/mlx/v22_candlist_main_dev.jsonl \
  --item-outputs runs/mlx/item_outputs.jsonl --model-outputs runs/mlx/model_outputs.jsonl \
  --sme-outputs runs/mlx/v21_sme_dev.jsonl --region-outputs runs/mlx/v22_region_dev.jsonl --cv \
  > runs/v22_candlist_20260921.log 2>&1
log "C 종료코드 $?"

# 2) B1: 지역 전용 호출을 무라벨 750건에 생성(약 113분)
log "B1 시작: 지역 전용 호출 무라벨 750"
for n in 250 500; do
  src=runs/mlx/train_sample${n}.jsonl; [ $n = 500 ] && src=runs/mlx/train_sample500_next.jsonl
  $P scripts/mlx_eval_extract.py --script submissions/20260922_focused_calls/script.py --dev $src \
    --outputs runs/mlx/train${n}_main.jsonl --item-outputs runs/mlx/train${n}_item.jsonl \
    --model-outputs runs/mlx/train${n}_model.jsonl \
    --region-outputs runs/mlx/train${n}_region.jsonl --generate-only \
    >> runs/v22_region_unlabeled.log 2>&1
done
log "B1 종료코드 $?"

# 3) B2: 기업규모 전용 호출을 무라벨 750건에 생성(16/250건까지 되어 있음, 약 110분)
log "B2 시작: 기업규모 전용 호출 무라벨 750"
for n in 250 500; do
  src=runs/mlx/train_sample${n}.jsonl; [ $n = 500 ] && src=runs/mlx/train_sample500_next.jsonl
  $P scripts/mlx_eval_extract.py --script submissions/20260922_focused_calls/script.py --dev $src \
    --outputs runs/mlx/train${n}_main.jsonl --item-outputs runs/mlx/train${n}_item.jsonl \
    --model-outputs runs/mlx/train${n}_model.jsonl \
    --sme-outputs runs/mlx/train${n}_sme.jsonl --generate-only \
    >> runs/v21_sme_unlabeled.log 2>&1
done
log "B2 종료코드 $?"
log "큐 전체 종료"
