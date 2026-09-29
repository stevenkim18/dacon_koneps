#!/usr/bin/env bash
# (클라우드) 실험 묶음을 모델 1회 로드로 돌린다: dev 200 + 손라벨 무라벨 750 = 950건.
#   켜는 것: 실적 전용 호출 · 물품 품목 호출 · LLM 직접 판정 · 직접 판정+dev 사례(자기 자신 제외)
#   결과: out/exp/raw/*.jsonl (Mac에서 scripts/judge_combine.py로 분석), run.log
# 예상(추정, 미측정): 모델 로드 약 12분 + 추론 약 1.5~2시간. dev만 먼저 보려면 INPUT=open/dev.jsonl.gz
set -euo pipefail
cd "$(dirname "$0")/.."
# RunPod PyTorch 템플릿에서는 pip 설치 CUDA 라이브러리 경로가 기본 검색 경로에 없다(run_dev.sh와 같은 처리).
site_packages=$(python -c 'import site; print(site.getsitepackages()[0])')
if [[ -d "$site_packages/nvidia" ]]; then
  export LD_LIBRARY_PATH="$(find "$site_packages/nvidia" -type d -name lib | paste -sd:)":$site_packages/torch/lib:${LD_LIBRARY_PATH:-}
fi
export PPS_MODEL_DIR=${MODEL_DIR:-/workspace/models/gemma-4-26B-A4B-it}
export PPS_DATA_DIR=$PWD/open/data
OUT=${OUT:-$PWD/out/exp}
export PPS_OUTPUT_DIR=$OUT PPS_DUMP_DIR=$OUT/raw
export PPS_ENABLE_PERF=1 PPS_ENABLE_GOODS=1 PPS_JUDGE=1 PPS_JUDGE_RAG=1 PPS_CASES=$PWD/cloud/cases.json
mkdir -p "$OUT"
start=$(date +%s)
python cloud/script_dump.py --input "${INPUT:-open/exp950.jsonl.gz}" --gpu-mem "${GPU_MEM:-0.92}" \
  --budget-s "${BUDGET_S:-30000}" 2>&1 | tee "$OUT/run.log"
echo "전체 소요 $(( $(date +%s) - start ))초" | tee -a "$OUT/run.log"
