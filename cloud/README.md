# 클라우드 GPU로 서버에 가까운 조건에서 돌려 보기

작성 2026-09-23. **목적:** 대회 서버와 같은 모델 리비전·vLLM 0.26·int8·max_model_len 16384로 제출 코드를 dev 200건에 돌린다. 아래 PyTorch 템플릿은 서버의 베이스 이미지·torch·CUDA·CPU/RAM 자원과 동일하지 않다.
그래서 로컬 MLX 4bit 결과가 서버를 얼마나 잘못 보여 왔는지 잰다. 규칙 2-1: "로컬 개발 환경(GPU·런타임·정밀도)은 자유"다.

| 파일 | 어디서 | 하는 일 |
|---|---|---|
| `make_bundle.sh` | Mac | 코드·dev·법령패키지·무라벨 750을 `cloud_bundle.tar.gz`(약 11MB)로 묶는다 |
| `setup.sh` | 클라우드 | GPU·vLLM 버전 확인, 고정 모델을 대회 리비전 그대로 내려받는다(약 50GB) |
| `run_dev.sh` | 클라우드 | dev 200건 실행 → `out/dev/`에 CSV·로그·점수·호출별 원본 출력 |
| `run_750.sh` | 클라우드(선택) | 손라벨 있는 무라벨 750건 실행 → 원본 출력만 저장(채점은 Mac) |
| `script_dump.py` | 클라우드 | `20260924_v20_quote_region35/script.py` + `PPS_DUMP_DIR` 원본 출력 저장. 판정 로직은 같다 |
| `score_csv.py` | 어디서나 | CSV와 dev 정답 비교, 항목별 F1. 로컬 예측의 macro 재현을 확인했다 |

## 0. 준비 (Mac, 10분)

1. `google/gemma-4-26B-A4B-it`은 공개 모델이므로 토큰 없이 다운로드할 수 있다(2026-09-23 RunPod에서 `config.json` 접근 확인). Hugging Face 다운로드 제한이 걸리면 Settings → Access Tokens의 **Read 토큰**을 클라우드 터미널에서만 입력한다. 토큰을 채팅·문서에 붙여 넣지 않는다.
2. 묶음 만들기: `bash cloud/make_bundle.sh` → 저장소 최상위에 `cloud_bundle.tar.gz`.

## 1. GPU 빌리기 (RunPod 예시)

서버와 같은 **NVIDIA L40S 48GB 1장**이 가장 좋다. 없으면 A100 80GB도 되며, 그때는 실행 시 `GPU_MEM=0.52`로 KV 캐시 크기를 서버에 맞춘다.
Vast.ai·Lambda 등 다른 곳도 같은 방식이다. 요금과 화면 이름은 서비스마다 다르고 바뀌므로 대여 직전에 확인한다.

1. RunPod 가입 → 크레딧 충전(처음엔 소액).
2. **Pods → Deploy** → GPU **L40S × 1**.
3. 템플릿: RunPod 공식 **PyTorch 2.8.0**. 파드 터미널에서 `pip install vllm==0.26.0`과 `pip install transformers==5.14.1`을 실행한다. 2026-09-23 실측에서 pip가 받은 transformers 5.17.0은 Gemma 4의 층별 `head_dim` 설정을 vLLM 0.26이 읽지 못해 모델 로드에 실패했다. 5.14.1은 이 오류를 피하는 버전이다.
   `vllm/vllm-openai:v0.26.0` 이미지는 API 서버를 시작하는 ENTRYPOINT가 있어 RunPod의 시작 명령 칸에 `sleep infinity`를 넣는 방식은 확인되지 않았다. PyTorch 템플릿은 vLLM 버전은 맞출 수 있지만 torch·CUDA 버전이 서버 이미지와 다를 수 있다. `setup.sh`가 찍는 버전을 기록해 비교 해석에 반영한다.
4. 디스크: **Volume 120GB 이상**(`/workspace`에 연결). 모델만 약 50GB다.
5. 파드가 뜨면 **Connect → Jupyter Notebook → Launcher → Terminal**로 터미널을 연다. Web terminal을 켜서 써도 된다.

## 2. 묶음 올리기

가장 쉬운 방법은 `runpodctl`이다.
- Mac: `brew install runpod/runpodctl/runpodctl` 후 `runpodctl send cloud_bundle.tar.gz` → 코드가 나온다.
- 파드: `cd /workspace && runpodctl receive <코드>`

SSH 키를 등록했다면 `scp -P <포트> cloud_bundle.tar.gz root@<IP>:/workspace/`도 된다.

## 3. 실행 (파드 터미널)

```bash
cd /workspace && tar --no-same-owner --no-same-permissions --warning=no-unknown-keyword -xzf cloud_bundle.tar.gz
pip install vllm==0.26.0 transformers==5.14.1  # RunPod PyTorch 템플릿에서 1회
# 다운로드 제한이 걸린 경우에만: read -rsp 'HF token: ' HF_TOKEN; echo; export HF_TOKEN
bash cloud/setup.sh             # 모델 내려받기(네트워크에 따라 수십 분)
bash cloud/run_dev.sh           # dev 200건 + 채점
# 선택: bash cloud/run_750.sh   # 무라벨 750건 원본 출력
```

A100 80GB라면 `GPU_MEM=0.52 bash cloud/run_dev.sh`.
`run_dev.sh`와 `run_750.sh`는 RunPod PyTorch 템플릿에서 필요한 CUDA 공유 라이브러리 경로를 자동으로 설정한다.

## 4. 결과 가져오기 → 파드 끄기

브라우저 대신 Mac에서 상태를 보려면 RunPod **Pods → 해당 Pod → Connect**의 `SSH over exposed TCP` 주소·포트를 사용한다. 공개키를 파드 생성 뒤에 등록했다면 기존 파드의 `/root/.ssh/authorized_keys`에도 공개키를 넣어야 직접 SSH가 된다. 개인키는 Mac에만 둔다.

```bash
ssh -i ~/.ssh/id_ed25519_runpod_dacon -p <포트> root@<IP>
# 접속 후: tail -f /workspace/out/dev/run.log
# 접속 후: nvidia-smi
# Mac에서 파일 복사: scp -i ~/.ssh/id_ed25519_runpod_dacon -P <포트> -r root@<IP>:/workspace/out/dev runs/cloud_int8_20260923/
```

`ssh.runpod.io` 경유 접속은 대화형 터미널용이고 SCP/SFTP를 지원하지 않는다. 파일 전송에는 위의 직접 TCP 연결을 쓴다.

```bash
cd /workspace && tar -czf results.tar.gz out/ && runpodctl send results.tar.gz
```

Mac에서 `runpodctl receive <코드>` 후 `runs/cloud_int8_20260923/`에 푼다.
**끝나면 파드를 Stop/Terminate 한다.** 켜 둔 시간만큼 과금된다. 모델을 다시 받지 않으려면 Volume만 남기고 파드를 끈다(Volume도 소액 과금).

## 5. 무엇을 보나

| 볼 것 | 위치 | 비교 대상 |
|---|---|---|
| dev macro F1·항목별 F1 | `out/dev/score.txt` | 로컬 4bit 같은 코드 **0.8706**(`submissions/20260924_v20_quote_region35/dev_validation.log`) |
| 유효 JSON 수·전용 호출 유효 수 | `out/dev/run.log` 마지막 JSON 줄 | 로컬 199/200 |
| 단계별 시간·생략된 단계 | `out/dev/run.log`의 `[예산]`·`!` 줄 | 서버 전체 1,853건 50분 55초 |
| 호출별 원본 출력 | `out/dev/raw/*.jsonl` | Mac에서 `scripts/mlx_eval_extract.py --outputs …/main.jsonl --item-outputs …/item.jsonl …`로 규칙만 바꿔 재채점 |

해석:
- **클라우드 int8 dev ≪ 0.87**이면 로컬 4bit와 결과가 다르다. 유효 JSON·출력 잘림·단계 생략을 먼저 보고, 런타임 차이도 확인한다. 서버에서도 같다고 단정하지 않는다.
- **클라우드 int8 dev ≈ 0.87**이면 dev·Public 격차의 원인을 계속 조사한다. 4bit에서 기각한 LLM 판정 확대를 int8로 다시 잰다.
- 두 경우 모두 `raw/`가 있으면 이후 규칙 실험은 GPU 없이 Mac에서 int8 출력으로 할 수 있다.

## 6. 실험 묶음 — `run_exp.sh` (2026-09-23 실행 · 결과: 전부 기각, 아래 7절)

한 번의 모델 로드로 **dev 200 + 손라벨 무라벨 750 = 950건**(`open/exp950.jsonl.gz`)에 아래를 모두 돌려 원본 출력을 저장한다.
판정기(제출 후보와 동일)는 그대로이고, 새 호출의 원본은 `out/exp/raw/`에 따로 남는다. 스위치를 끄면 판정이 제출 후보와 같다(int8 dev 0.8468 재현 확인).

| 스위치 | 내용 | 4bit에서의 이력 |
|---|---|---|
| `PPS_ENABLE_PERF=1` | 실적 전용 호출 | 09-21 dev 정탐 0·오탐 29로 기각 |
| `PPS_ENABLE_GOODS=1` | 물품 품목 전용 호출 | 09-21 dev 정탐 0·오탐 10으로 기각 |
| `PPS_JUDGE=1` | **LLM 직접 판정**: 24개 항목 기준·금액 문턱을 준 시스템 프롬프트 + 본 호출과 같은 원문 발췌 → `판단_메모` + v1~v24 불리언 | 새 실험 |
| `PPS_JUDGE_RAG=1` | 직접 판정 + 글자 2-gram 유사도로 고른 **dev 사례 2건**(정답 항목·근거, 자기 자신 제외). `PPS_CASES=cloud/cases.json` | 새 실험 |

프롬프트 길이(실제 Gemma 토크나이저, 40건 표본): 직접 판정 중앙값 4,405 · 최대 6,761 / 사례 포함 4,629 · 7,055. 본 호출(중앙값 4,037)과 비슷하다.
예상 시간은 **측정하지 않았다**. dev 본 호출이 200건 352초였으므로 950건 × (본 호출 + 판정 2종)만 약 1.5시간, 모델 로드 12분을 더해 2시간 안팎으로 추정한다.

```bash
cd /workspace && tar --no-same-owner --no-same-permissions --warning=no-unknown-keyword -xzf cloud_bundle.tar.gz
bash cloud/run_exp.sh                           # 950건 전부
# 먼저 dev만: INPUT=open/dev.jsonl.gz OUT=$PWD/out/exp_dev bash cloud/run_exp.sh
tar -czf results_exp.tar.gz out/exp/            # Mac으로 가져간 뒤 파드 종료
```

Mac 분석: `runs/cloud_int8_exp/`에 풀고
`.venv/bin/python scripts/judge_combine.py --raw runs/cloud_int8_exp/out/exp/raw`
→ dev 항목별 F1(판정원별) · 항목별 선택 교차검증 · 무라벨 750 양성 수와 손라벨 쌍 정밀도.

주의: `judge_rag`의 dev 점수는 자기 자신을 빼도 **같은 양식의 이웃 dev 공고**(예: DEV-135~138)가 예시로 들어가 낙관적이다. 채택 판단은 무라벨 750 정밀도와 함께 본다.
이 도구의 교차검증은 판정원 선택 방식이 `mlx_eval_extract.py --cv`와 달라(규칙 계열만 0.8392) 같은 도구 안에서만 비교한다.

## 7. 실행 기록 (2026-09-23)

| 실행 | 결과 | 사본 |
|---|---|---|
| `run_dev.sh` dev 200 | int8 dev **0.8468** · 교차 0.8016 (로컬 4bit 0.8706 · 0.8397) · 유효 JSON 199/200 · 모델 로드 748초 + 추론 566초 | `runs/cloud_int8_20260923/` |
| `run_exp.sh` 950건(파드 05:35~07:06, 5,536초) | 모든 호출 유효. 모델 로드 247초 · 본 호출 1,652초 · 직접 판정 1,095초 · 판정+사례 약 1,090초 | `runs/cloud_int8_exp/`(분석 `combine.log`) |

실험 결과(dev macro · 교차검증): 규칙 0.8410 · 0.8313 / +실적 0.8287 / +물품 0.8333 / 직접 판정 단독 0.3255 / 판정+사례 단독 0.2994 / 항목별 최적 조합 교차 0.8116·0.8183. **규칙보다 나은 판정원이 없다.**
해석은 [study log 09-23 ① 9절](../docs/05_study_log/20260923/1.%20leaderboard_gap_and_cloud_int8_plan.md).

### 파드를 다시 켤 때 (실측 주의사항)

- `/workspace`(모델 49GB·코드·결과)는 남지만 **pip로 설치한 vLLM은 사라진다.** 다시 설치한다:
  `/usr/local/bin/pip install --break-system-packages vllm==0.26.0 transformers==5.14.1`
  (`--break-system-packages` 없이 비대화형으로 실행하면 PEP 668 오류로 바로 실패한다.)
- 두 번째 실행부터 모델 로드가 748초 → **247초**로 줄었다(컴파일 캐시).
- 백그라운드 실행은 `nohup … & echo $! > pid`로 띄우고 `kill -0 $(cat pid)`로 살아 있는지 본다.
  `pgrep -f`·`pkill -f`에 SSH 명령줄에도 들어가는 패턴을 쓰면 자기 자신을 잡는다(09-23 대기 루프 오작동·연결 끊김).
- 리비전 확인: `head -qn1 /workspace/models/gemma-4-26B-A4B-it/.cache/huggingface/download/*.metadata | sort | uniq -c` → `12 4d7ae4984b…` 한 줄.
