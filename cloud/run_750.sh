#!/usr/bin/env bash
# (클라우드, 선택) 손라벨이 있는 무라벨 750건에 같은 코드를 돌려 호출별 원본 출력을 저장한다(채점은 Mac에서).
set -euo pipefail
cd "$(dirname "$0")/.."
# RunPod PyTorch 템플릿에서는 pip 설치 CUDA 라이브러리 경로가 기본 검색 경로에 없다.
site_packages=$(python -c 'import site; print(site.getsitepackages()[0])')
if [[ -d "$site_packages/nvidia" ]]; then
  export LD_LIBRARY_PATH="$(find "$site_packages/nvidia" -type d -name lib | paste -sd:)":$site_packages/torch/lib:${LD_LIBRARY_PATH:-}
fi
export PPS_MODEL_DIR=${MODEL_DIR:-/workspace/models/gemma-4-26B-A4B-it}
export PPS_DATA_DIR=$PWD/open/data
for part in train_sample250 train_sample500_next; do
  OUT=$PWD/out/$part
  mkdir -p "$OUT"
  PPS_OUTPUT_DIR=$OUT PPS_DUMP_DIR=$OUT/raw python cloud/script_dump.py --input runs/mlx/$part.jsonl \
    --gpu-mem "${GPU_MEM:-0.92}" 2>&1 | tee "$OUT/run.log"
done
