# DACON KONEPS

DACON [나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회](https://dacon.io/competitions/official/236754/overview/description)(2026-08-26 ~ 09-30) 참가 기록입니다.

입찰공고 1건(공고문·첨부 문서·나라장터 meta)을 읽고 24개 법령 항목의 위반 여부(0/1)와 원문 근거 문구를 내는 문제입니다. 모든 참가자가 같은 고정 LLM(`google/gemma-4-26B-A4B-it`)을 서버에서 돌리는 코드 제출형 대회였습니다.

## 결과

- 최종 제출 [`20260929_r18_fresh_holdout`](submissions/20260929_r18_fresh_holdout/README.md): Public(= Private) **0.7267850222**, 서버 실행 55분 42초 / 120분
- **최종 78위 / 607팀**(팀명 `나쵸a`). 15회 제출했고 공식 베이스라인 0.2150에서 시작했다. 2차 평가 진출선(15위)은 0.76217이었다([제출 이력](submissions/README.md#최종-결과))

## 접근

LLM은 판단하지 않고 **판정에 필요한 사실만 JSON으로 뽑습니다.** 정규식이 같은 사실을 원문에서 한 번 더 뽑아 LLM 결손을 메우고, **Python 법령 판정기**가 meta 금액·계약유형과 사실을 배포된 법령패키지의 조건식에 넣어 v1~v24를 판정합니다. 이 구조 전환 하나로 0.21 → 0.62가 됐고, 이후 법령 적용 범위와 재현율 규칙으로 0.73 가까이 올렸습니다. 과정과 교훈은 [대회 회고](docs/06_wrap_up/01_retrospective.md)에 있습니다.

## 저장소 구조

| 경로 | 내용 |
|---|---|
| [`docs/`](docs/README.md) | 대회 규칙·데이터 명세 요약, 학습 가이드, [연구 일지](docs/05_study_log/README.md), 대회 후 정리 |
| [`submissions/`](submissions/README.md) | 제출·후보 스냅샷(`script.py` · `submit.zip` · 검증 로그)과 제출 이력 |
| [`runs/`](runs/README.md) | 로컬 MLX·클라우드 int8 모델 출력과 실험 도구(재추론 없이 재채점할 때 쓴다) |
| [`labels/`](labels/README.md) | 무라벨 표본 손라벨(자가 라벨) |
| `scripts/` | 공통 도구: dev 재채점(`mlx_eval_extract.py`), 무라벨 20,000 재생(`replay_unlabeled.py`), 근거 문구 점검(`evidence_audit.py`) 등 |
| [`cloud/`](cloud/README.md) | 서버와 같은 조건(vLLM int8)의 클라우드 GPU 실행 절차 |
| `requirements-local.txt` | 로컬 분석·MLX 추론 환경(Python 3.13.5, Apple Silicon) |
| `AGENTS.md` | AI 코딩 에이전트(Codex·Claude Code) 작업 지침 |

저장소에 넣지 않은 것(`.gitignore`): `open/`(대회 배포 데이터, 재배포 금지), `models/`(MLX 가중치), `.venv/`, `runs/replay_cache/`(다시 만들어지는 캐시). 데이터를 받아 놓는 방법은 [재현 문서](docs/06_wrap_up/02_reproduce.md) 0단계에 있습니다.

## 읽는 순서

1. [대회 회고](docs/06_wrap_up/01_retrospective.md): 무엇이 점수를 올렸고 무엇이 안 됐는지
2. [최종 제출물 재현하기](docs/06_wrap_up/02_reproduce.md): 제출 파일 확인, mock 실행, 저장 출력으로 dev 재채점
3. [제출 이력](submissions/README.md): 제출 15회와 미제출 후보 29개, 대회 중 결정 기록
4. [문서 허브](docs/README.md): 대회 규칙, 평가, 데이터 명세, 베이스라인

AI·데이터·LLM을 처음 공부한다면 [학습 가이드](docs/04_learning/README.md)에서 시작합니다.
