#!/usr/bin/env bash
# (클라우드) 제출 후보 코드를 서버와 같은 설정(int8, max_model_len 16384)으로 dev 200건에 돌리고 채점한다.
# 결과: out/dev/submission.csv · run.log(단계별 시간·유효 JSON 수) · score.txt · raw/*.jsonl(호출별 원본 출력)
set -euo pipefail
cd "$(dirname "$0")/.."
# RunPod PyTorch 템플릿에서는 pip 설치 CUDA 라이브러리 경로가 기본 검색 경로에 없다.
site_packages=$(python -c 'import site; print(site.getsitepackages()[0])')
if [[ -d "$site_packages/nvidia" ]]; then
  export LD_LIBRARY_PATH="$(find "$site_packages/nvidia" -type d -name lib | paste -sd:)":$site_packages/torch/lib:${LD_LIBRARY_PATH:-}
fi
export PPS_MODEL_DIR=${MODEL_DIR:-/workspace/models/gemma-4-26B-A4B-it}
export PPS_DATA_DIR=$PWD/open/data
OUT=${OUT:-$PWD/out/dev}
export PPS_OUTPUT_DIR=$OUT PPS_DUMP_DIR=$OUT/raw
mkdir -p "$OUT"
# L40S(48GB)는 서버와 같게 0.92. A100 80GB라면 GPU_MEM=0.52로 서버의 KV 캐시 크기에 맞춘다.
start=$(date +%s)
python cloud/script_dump.py --input open/dev.jsonl.gz --gpu-mem "${GPU_MEM:-0.92}" 2>&1 | tee "$OUT/run.log"
echo "전체 소요 $(( $(date +%s) - start ))초" | tee -a "$OUT/run.log"
python cloud/score_csv.py "$OUT/submission.csv" open/dev_labels.csv | tee "$OUT/score.txt"
