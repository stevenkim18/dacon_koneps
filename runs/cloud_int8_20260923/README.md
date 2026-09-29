# RunPod L40S · vLLM int8 dev 실행 (2026-09-23)

`cloud/script_dump.py`(`submissions/20260924_v20_quote_region35/script.py`와 같은 판정에 원본 출력 저장 추가)를 dev 200건에 실행했다. 결과는 `dev/`에 보관한다. RunPod Pod `gn31veeu05m7pm`, NVIDIA L40S 48GB 1장, PyTorch 2.8 템플릿에 `vllm==0.26.0`, `transformers==5.14.1`, 설치 결과 `torch==2.11.0+cu130`/CUDA 13.0. 고정 모델 리비전 `4d7ae4984b7db7de8f8457170b3f1a419ee76d52`, `int8_per_channel_weight_only`, `max_model_len=16384`, GPU 메모리 비율 0.92.

| 측정 | 결과 |
|---|---:|
| dev macro F1 | **0.8468** |
| 유효 본 호출 JSON | 199/200 |
| 전체 시간 | 1322초 (모델 로드 748초, 추론 566초) |
| 항목별 주요 약점 | v9 F1 0.476 (FP 10), v1 0.500, v24 0.571 |

항목별 TP/FP/FN은 [`dev/score.txt`](dev/score.txt), 단계·모델 로그는 [`dev/run.log`](dev/run.log), 추론 원본은 `dev/raw/`를 본다. `submission.csv`는 49열·200행 검사를 통과했다. 클라우드 dev 점수는 Public 점수가 아니며, RunPod의 CPU/RAM·베이스 이미지는 대회 서버와 다르다. 로컬 MLX 4bit의 같은 후보 dev 0.8706보다 0.0238 낮다(처음 적은 0.8715는 thinking 품목 출력으로 잰 값이라 09-23 저녁 고쳤다). Mac 재채점(`dev/mac_rescore.log`)으로 0.8468을 그대로 재현했고 교차검증은 0.8016이다.

처음 모델 로드 두 번은 실패했다. 첫 실패는 PyTorch 템플릿에서 pip CUDA 공유 라이브러리 경로가 누락된 `torchcodec` 로드 오류(`dev/run_load_error.log`), 두 번째는 pip 최신 `transformers==5.17.0`과 vLLM 0.26의 Gemma 4 `head_dim` 설정 충돌(`dev/run_config_error.log`). `cloud/run_dev.sh`에 CUDA 경로 설정을 넣고 `transformers==5.14.1`로 고정했다.

RunPod의 `/workspace/out/dev`를 직접 SSH/SCP로 로컬에 복사했다. 이 폴더는 제출 ZIP에 넣지 않는다.
