#!/usr/bin/env bash
# (클라우드에서 1회) GPU·vLLM 확인 후 대회 고정 모델을 정확한 리비전으로 받는다.
# 공개 모델은 토큰 없이 받을 수 있다. 선택 사항: HF_TOKEN(읽기 토큰)으로 다운로드 제한 완화.
set -euo pipefail
MODEL_DIR=${MODEL_DIR:-/workspace/models/gemma-4-26B-A4B-it}
export HF_HOME=${HF_HOME:-/workspace/.hf_cache}
nvidia-smi --query-gpu=name,memory.total --format=csv
python -c "import vllm, torch; print('vllm', vllm.__version__, '| torch', torch.__version__, '| cuda', torch.version.cuda)"
python -c "import huggingface_hub" 2>/dev/null || pip install -q huggingface_hub
python - <<PY
import os
from huggingface_hub import snapshot_download
p = snapshot_download("google/gemma-4-26B-A4B-it", revision="4d7ae4984b7db7de8f8457170b3f1a419ee76d52",
                      local_dir="${MODEL_DIR}", token=os.environ.get("HF_TOKEN") or None)
print("모델 저장 위치:", p)
PY
du -sh "${MODEL_DIR}"
