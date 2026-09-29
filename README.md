# DACON KONEPS

나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 프로젝트입니다.

현재 저장소에는 대회 규정, 데이터 명세, 공식 베이스라인을 빠르게 찾아볼 수 있도록 문서를 정리해 두었습니다.

실제 제출 파일, 점수와 실험 판단은 [제출 이력](submissions/README.md)에 날짜별로 기록합니다.

로컬 모델 출력(재채점용)은 [runs](runs/README.md), 무라벨 자가 라벨은 [labels](labels/README.md)에 보존합니다.

## 문서 허브

전체 요약과 현재 기준의 주요 제약은 [문서 허브](docs/README.md)에서 확인합니다.

AI·데이터·LLM·RAG를 처음 공부한다면 [학습 가이드](docs/04_learning/README.md)에서 시작합니다. 먼저 [빠른 실습 계획](docs/04_learning/01_quick-start.md)을 따라 실행·평가·제출을 경험하고, 필요할 때 [전체 개념과 책·참고 자료](docs/04_learning/02_concepts-and-resources.md)를 봅니다.

상세 문서는 다음 순서로 읽으면 됩니다.

1. [대회 개요](docs/01_competition/01_overview.md)
2. [대회 규칙](docs/01_competition/02_rules.md)
3. [평가 및 제출](docs/01_competition/03_evaluation.md)
4. [일정](docs/01_competition/04_schedule.md)
5. [데이터 개요](docs/02_data/01_overview.md)
6. [데이터 상세 명세](docs/02_data/02_detailed-spec.md)
7. [dev 200건 분석](docs/02_data/03_dev-200-analysis.md)
8. [무라벨 20,000건 분석](docs/02_data/04_train-unlabeled-20000-analysis.md)
9. [코드 공유 목록](docs/03_baselines/01_codeshare.md)
10. [Gemma 베이스라인](docs/03_baselines/02_gemma.md)
11. [Gemma + 법령 RAG 베이스라인](docs/03_baselines/03_rag.md)

`AGENTS.md`는 Codex 작업 지침 파일이므로 문서 모음과 분리해 프로젝트 루트에 유지합니다.
