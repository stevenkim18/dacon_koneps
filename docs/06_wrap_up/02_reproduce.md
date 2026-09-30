# 최종 제출물 재현하기

> 작성 2026-09-30. 대상은 최종 제출 [`submissions/20260929_r18_fresh_holdout`](../../submissions/20260929_r18_fresh_holdout/README.md)(Public 0.7267850222).
> 1~4단계는 이 문서를 쓰며 실제로 실행해 기록과 같은 결과를 확인했다. 5~6단계는 이번에 실행하지 않았다.

## 0. 준비

**대회 데이터는 저장소에 없다.** `open/`은 재배포 금지 대상이라 `.gitignore`로 뺐다. DACON [데이터 페이지](https://dacon.io/competitions/official/236754/data)에서 받아 저장소 루트의 `open/`에 푼다.

```text
open/
├── README.md · sample_submission.csv · baseline/
├── dev.jsonl.gz · dev_labels.csv · train_unlabeled.jsonl.gz
├── data/
│   ├── test.jsonl.gz · 항목표.json · 정답스키마_디코딩.json
│   └── 법령패키지/ (법령 txt, 중기부고시 세부품명 csv·hwpx)
├── dev.jsonl          ← 파생: runs/edit_model_20260923 도구가 읽는다
└── exp950.jsonl.gz    ← 파생: dev 200 + 손라벨 무라벨 750, int8 도구·cloud 실험이 읽는다
```

파생 파일 두 개는 배포 파일과 저장소의 표본으로 다시 만든다. `exp950.jsonl.gz`는 아래 명령의 출력과 압축을 푼 내용이 바이트 단위로 같다(2026-09-30 SHA-256 대조).

```bash
gzip -dk open/dev.jsonl.gz
{ gzip -dc open/dev.jsonl.gz; cat runs/mlx/train_sample250.jsonl runs/mlx/train_sample500_next.jsonl; } | gzip > open/exp950.jsonl.gz
```

**Python 환경.** mock 실행은 표준 라이브러리만 쓰므로 설치할 것이 없다(기록상 Python 3.9.6·3.13.5 통과). 실제 추론에 쓰는 vLLM은 대회 서버의 고정 패키지다. 분석 도구와 로컬 MLX 추론은 [`requirements-local.txt`](../../requirements-local.txt)로 만든다(Python 3.13.5, Apple Silicon).

```bash
python3.13 -m venv .venv && .venv/bin/pip install -r requirements-local.txt
```

## 1. 제출 파일 확인

```bash
shasum -a 256 submissions/20260929_r18_fresh_holdout/submit.zip
# e5067e8bc628ff398b4d3c8d91689c53fab77ef13219cf69c365363dffe8da0a  (README 기록과 같음)
```

ZIP 안에는 `script.py`와 `requirements.txt`뿐이다. 압축 안의 `script.py`는 폴더의 `script.py`와 같다(`cmp`로 확인).

## 2. mock 실행 — 모델 없이 입력·출력 흐름 확인 (약 2초)

LLM을 부르지 않고 정규식 사실만으로 판정해 `submission.csv`를 쓴다. 제출 형식 점검용이며 점수와는 무관하다.

```bash
R=$PWD   # 저장소 루트에서 실행
mkdir -p /tmp/r18/pkg && unzip -o submissions/20260929_r18_fresh_holdout/submit.zip -d /tmp/r18/pkg
(cd /tmp/r18/pkg && PPS_DATA_DIR="$R/open/data" PPS_OUTPUT_DIR=/tmp/r18/out python3 script.py --mock)
```

확인 결과(2026-09-30): 종료코드 0 · 1.5초 · 자가검증 PASS · 10행 × 49열 · 헤더 `id, v1~v24, e1~e24` · ID가 입력 순서와 같음 · v열 전부 0/1.

## 3. dev 재채점 — 저장된 모델 출력으로 (GPU 없음, 약 75초)

새 추론 없이 `runs/`에 저장한 LLM 출력을 최종 판정기에 다시 넣어 dev 200 점수를 낸다.

```bash
zsh runs/review_20260924/devscore.sh submissions/20260929_r18_fresh_holdout/script.py
```

| 출력 | macro F1 | 교차검증 |
|---|---:|---:|
| 로컬 MLX 4bit (`runs/mlx/`) | 0.8820 | 0.8639 |
| 클라우드 int8 단독 (`runs/cloud_int8_20260923/`) | 0.8672 | 0.8500 |
| 클라우드 int8 950 묶음 (`runs/cloud_int8_exp/`) | 0.8654 | 0.8446 |

2026-09-30 실행값이 [`validation.log`](../../submissions/20260929_r18_fresh_holdout/validation.log) 1절과 같다. dev 점수는 규칙을 만든 데이터에서 잰 것이라 Public(0.7268)보다 높다. 왜 dev로 후보를 고르지 않았는지는 [회고](01_retrospective.md) 5절에 있다.

## 4. 무라벨 20,000 정규식 재생 (GPU 없음, 캐시가 없으면 약 16분)

두 후보의 판정 차이를 무라벨 20,000건 전체에서 잰다(LLM 출력 없이 정규식 사실 경로만). 판정 캐시는 `runs/replay_cache/`에 쌓이고 git에서 뺀다.

```bash
.venv/bin/python scripts/replay_unlabeled.py \
  submissions/20260929_r17_edit_shapes/script.py submissions/20260929_r18_fresh_holdout/script.py
```

확인 결과(2026-09-30, 캐시 없이 15분 58초): 기준 양성 5,369 · 예외 0 · r18 **Δ+6 · 변경 24공고 · 예외 0**(v1 +2 · v4 +3 · v13 −5 · v15 −4 · v17 +3 · v19 +7). [`validation.log`](../../submissions/20260929_r18_fresh_holdout/validation.log) 3절과 같다.

## 5. 로컬 MLX로 새 추론 (이번에는 실행하지 않음)

2026-09-30 기준 `models/`에는 가중치(약 14GB)가 없고 설정·토크나이저만 남아 있다. 새로 추론하려면 다시 받는다.

```bash
.venv/bin/hf download mlx-community/gemma-4-26b-a4b-it-4bit --local-dir models/gemma-4-26b-a4b-it-4bit
```

생성 명령은 [`runs/README.md`](../../runs/README.md)의 `mlx/` 절에 있다. dev 200건 본 호출에 약 1시간이 걸렸다(09-20 확장 프롬프트 실측 21.4초/건, M1 Max). 로컬 4bit는 서버 int8과 출력이 다르다. 서버 int8이 v1을 약 3배, v9를 약 2.4배 더 켠다([09-24 ④](../05_study_log/20260924/4.%20sme_sentence_join_and_v17_private.md)).

## 6. 서버와 같은 조건 — 클라우드 GPU (이번에는 실행하지 않음)

대회 서버는 고정 Gemma 4 26B-A4B를 vLLM int8로 돌린다. 같은 조건은 RunPod L40S에서 [`cloud/README.md`](../../cloud/README.md) 절차로 재현했다(09-23). 모델 리비전은 `cloud/setup.sh`에 고정돼 있고, 올릴 묶음은 `cloud/make_bundle.sh`로 만든다. 이 스크립트는 0단계에서 준비한 `open/` 파일과 `exp950.jsonl.gz`를 묶는다.
