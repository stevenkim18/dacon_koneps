# 모바일 개발자를 위한 AI·데이터·LLM·RAG 학습 지도

[학습 가이드로 돌아가기](README.md) · [먼저 해볼 빠른 실습 계획](01_quick-start.md)

현재는 빠른 실습 계획을 먼저 진행하고, 이 문서는 막히는 개념을 찾아보거나 이후 체계적으로 공부할 때 사용한다.

> 대상: 모바일 개발 경험은 있지만 AI·데이터·LLM·RAG는 처음인 개발자.
> 목표: 입찰공고와 법령을 읽어 위반 여부와 원문 근거를 제시하는 시스템을 이해하고 구현하기.
> 기간 제한 없이, 개념 이해와 실습 결과를 기준으로 진행한다. 자료 링크 확인: 2026-09-15.

## 1. 큰 그림

AI는 넓은 분야이고, 머신러닝은 데이터에서 패턴을 학습하는 접근이다. 딥러닝은 여러 층의 신경망을 사용하는 머신러닝이다. LLM은 대규모 언어 모델이다. RAG는 모델의 종류가 아니라, 필요한 자료를 검색해 생성 모델에 제공하는 시스템 구성 방식이다.

다음 순서로 공부한다.

1. Python과 데이터 탐색
2. 머신러닝과 평가
3. 필요한 수학과 신경망
4. 자연어 처리와 LLM
5. 프롬프트와 구조화 출력
6. 정보 검색과 임베딩
7. RAG와 근거 추적
8. 입찰·법령 도메인 적용
9. 평가·운영·재현성

법령 도메인 학습은 1단계부터 실제 공고를 조금씩 읽으며 병행한다. 각 단계의 모든 자료를 완독할 필요는 없다. 주교재 하나와 실습을 중심으로 하고 나머지는 참고서로 사용한다.

### 기존 개발 경험과 연결하기

| 모바일 개발에서 익숙한 것 | AI 프로젝트에서 확장할 것 |
|---|---|
| 모델 객체, DTO, JSON 파싱 | 데이터 스키마, 결측값, 라벨, 문서 출처 |
| 단위 테스트와 회귀 테스트 | 평가 데이터셋, 항목별 지표, 오답 분석 |
| API 응답 검증 | 출력 형식 검증 + 답의 사실성·근거 검증 |
| 의존성 및 빌드 버전 관리 | 데이터·모델·프롬프트·검색 인덱스 버전 관리 |
| 메모리·지연 시간 최적화 | 토큰 예산, GPU 메모리, 배치 추론, 생성 속도 |

AI 시스템도 소프트웨어 테스트가 필요하다. 여기에 데이터 분포에 따른 오류율 측정이 추가된다. 타입이 올바른 응답과 내용이 올바른 응답은 다르다.

## 2. Python과 데이터 탐색

### 배울 개념

- Python: 리스트·딕셔너리·컴프리헨션, 함수, 타입 힌트, 제너레이터, 예외 처리, 가상환경.
- NumPy: 배열, shape, 축(axis), 벡터 연산, 브로드캐스팅.
- pandas: DataFrame, 필터링, 집계, 병합, 결측값 처리.
- JSON/JSONL/CSV/gzip, Unicode 정규화, 문서 ID와 출처 관리.
- EDA(탐색적 데이터 분석): 데이터의 분포·이상·누락을 이해하는 과정.
- 데이터셋, 샘플, 특성(feature), 라벨(label), 메타데이터.
- 중복 데이터, 라벨 오류, 표본 편향, 문서 누락.

### 자료

- [Python 공식 한국어 자습서](https://docs.python.org/ko/3/tutorial/): 제어문·자료구조·입출력·예외 처리·가상환경 위주로 읽는다. 프로그래밍 입문 전체를 다시 할 필요는 없다.
- [Python for Data Analysis, 3E — Wes McKinney](https://wesmckinney.com/book/): 저자가 공개한 무료 영어 웹북. NumPy, pandas, 데이터 로딩, 정제, 집계 부분을 참고한다.
- [pandas Getting Started](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html): 표 읽기·쓰기, 행 선택, 요약 통계 실습용.

### 실습과 완료 기준

공고 데이터 탐색 노트북을 만든다. 문서 종류별 건수, 문서 길이 분포, 등록정보 결측률, 항목별 위반 비율을 확인한다. 가장 긴 공고와 누락이 있는 공고를 직접 읽는다.

완료 기준: 데이터 한 건의 구조를 설명하고, 품질 문제를 근거와 함께 세 가지 이상 찾아낼 수 있다.

## 3. 머신러닝과 평가

### 배울 개념

- 지도학습·비지도학습, 분류·회귀·군집화.
- 학습(training)과 추론(inference), 파라미터와 하이퍼파라미터.
- 손실함수, 최적화, 일반화, 과적합·과소적합.
- train/validation/test 분리, 교차 검증, 데이터 누수.
- 이진 분류·다중 클래스 분류·다중 라벨 분류의 차이.
- 혼동행렬, precision, recall, F1, macro/micro 평균, 클래스 불균형.
- 표본 수가 작을 때 점수의 불확실성, 임곗값과 확률 보정의 기초.

이 프로젝트는 공고 한 건에 여러 위반이 동시에 존재할 수 있는 다중 라벨 문제로 볼 수 있다. 각 항목은 이진 판단이다. 한 클래스만 선택하는 문제와 구분한다.

### 자료

- [Google 머신러닝 단기집중과정](https://developers.google.com/machine-learning/crash-course?hl=ko): 무료, 한국어 제공. 회귀·분류·데이터·일반화 순으로 학습한다.
- [혼자 공부하는 머신러닝+딥러닝 — 공식 코드와 강의 안내](https://github.com/rickiepark/hg-mldl): 박해선 저. 한국어 입문 주교재 후보. 훈련/테스트 분리, 전처리, 회귀, 분류, 검증, 신경망 부분을 우선한다. 책과 무료 코드·강의의 접근 범위는 다르다.
- [Hands-On Machine Learning, 3rd Edition — Aurélien Géron](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/): 더 깊은 참고서. 머신러닝 개요, 전체 프로젝트 흐름, 분류, 모델 훈련 부분부터 읽는다. 첫 책으로 부담되면 앞의 자료를 먼저 본다.
- [scikit-learn Common Pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): 전처리와 데이터 누수 사례를 읽는다.
- [scikit-learn F1](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html): 평가 구현 때 참고한다.

### 실습과 완료 기준

일반 학습용 작은 데이터로 분류 모델 하나를 학습하고, 훈련 점수와 검증 점수를 비교한다. 혼동행렬에서 잘못 분류된 사례를 읽는다. 이것은 학습 실습이며, 별도 학습한 분류기를 대회 제출물에 넣는 계획은 아니다.

완료 기준: 정확도가 높아도 쓸모없는 모델이 될 수 있는 이유, 데이터 누수, F1과 precision/recall의 관계를 설명할 수 있다.

## 4. 수학과 신경망

### 배울 개념

| 분야 | 우선 배울 내용 | 프로젝트에서 쓰이는 곳 |
|---|---|---|
| 선형대수 | 벡터, 행렬, 내적, 노름, 코사인 유사도 | 임베딩 비교와 신경망 연산 |
| 확률·통계 | 조건부확률, 평균·분산, 표본·분포 | 모델 출력과 평가 결과 이해 |
| 미분 | 도함수, 편미분, 연쇄법칙, 기울기 | 모델 학습 원리 이해 |
| 정보이론 기초 | 로그, 엔트로피, 교차 엔트로피 | 언어 모델의 학습 목표 이해 |
| 신경망 | 가중치, 활성화, 순전파, 역전파, 옵티마이저 | 딥러닝 모델의 작동 방식 |

처음에는 수식을 증명하는 것보다 작은 숫자로 계산하고 그림으로 이해하는 것을 목표로 한다. 필요한 개념이 등장할 때 수학 자료로 돌아와도 된다.

### 자료

- [3Blue1Brown 선형대수 시리즈 소개](https://www.3blue1brown.com/lessons/eola-preview/): 벡터, 행렬 변환, 내적을 시각적으로 이해한다.
- [3Blue1Brown 신경망 자료](https://www.3blue1brown.com/topics/neural-networks): 신경망·경사 하강·역전파의 직관을 얻는다.
- [밑바닥부터 시작하는 딥러닝 1 — 원서 공식 코드](https://github.com/oreilly-japan/deep-learning-from-scratch): 사이토 고키 저. 원리 구현을 원하는 경우 선택한다. 링크는 책 전문이 아니라 코드다.
- [PyTorch Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html): Tensor, Autograd, 모델 구성, 최적화 흐름을 직접 실행한다.

### 실습과 완료 기준

NumPy로 코사인 유사도를 계산하고 PyTorch로 작은 신경망을 한 번 학습한다. 배치 크기를 바꾸며 텐서 shape를 출력한다.

완료 기준: 학습 중 무엇이 바뀌는지, 추론에서 무엇을 계산하는지, 텐서 shape가 왜 중요한지 설명한다.

## 5. 자연어 처리와 LLM

### 배울 개념

- NLP(자연어 처리): 사람의 언어를 컴퓨터로 다루는 분야.
- 토큰화, subword, 어휘집, 토큰 ID, 토큰 임베딩.
- 문맥에 따라 달라지는 표현, 위치 정보, attention, Transformer.
- encoder 계열과 decoder 계열의 역할 차이.
- 다음 토큰 예측과 자기회귀 생성.
- 사전학습, 지도 미세조정, 지시학습, 선호도 정렬의 개념적 차이.
- context window, 입력/출력 토큰, temperature, top-p.
- 환각, 지식의 최신성, 긴 입력에서의 정보 누락.

토큰 임베딩과 문장 검색용 임베딩을 구분한다. 생성 모델의 내부 표현을 아무렇게나 평균낸 값이 좋은 검색 벡터가 되는 것은 아니다.

### 자료

- [Hugging Face 한국어 LLM Course](https://huggingface.co/learn/llm-course/ko/chapter1/1): 모델 개요, 토크나이저, 모델 사용, 데이터 처리부터 읽는다. 번역 범위는 영어판과 다를 수 있다.
- [Hands-On Large Language Models — 저자 공식 사이트](https://www.llm-book.com/): Jay Alammar·Maarten Grootendorst 저. 이 학습 경로의 LLM 주교재 추천. 언어 모델 이해, 토큰·임베딩, Transformer, 생성, 의미 검색·RAG 순으로 읽는다. 책은 유료이며 사이트에서 관련 자료로 이동할 수 있다.
- [The Illustrated Transformer — Jay Alammar](https://jalammar.github.io/illustrated-transformer/): attention과 Transformer를 그림으로 이해하는 무료 아티클. 원래 Transformer 구조를 설명하며, 현대 LLM과 구조가 모두 동일한 것은 아니다. 원문에 한국어 번역 링크가 있다.

### 실습과 완료 기준

한국어 공고 문장을 토큰화하고 글자 수와 토큰 수를 비교한다. 작은 생성 모델을 사용하는 일반 학습 실습에서는 temperature와 입력 길이를 바꾸며 출력을 기록한다.

완료 기준: 모델 가중치에 담긴 지식과 프롬프트로 주어진 자료를 구분하고, 긴 문서를 통째로 넣는 방식의 한계를 설명한다.

## 6. 프롬프트와 구조화 출력

### 배울 개념

- system/user 역할, chat template, 명확한 작업 정의.
- zero-shot, few-shot, 예외와 경계 사례, 작업 분해.
- JSON Schema, 구조화 출력, 파싱·검증·재시도.
- 모델이 말하는 확신과 실제 정답 확률의 차이.
- 문서의 내용과 실행 지시를 분리하는 방법, prompt injection.
- 출처를 가진 답변과 원문 인용 검증.

### 자료

- [AI Engineering — Chip Huyen](https://www.oreilly.com/library/view/ai-engineering/9781098166298/): 모델을 사용해 제품을 만드는 관점의 책. 모델 기초를 익힌 뒤 평가, 프롬프트, RAG, 데이터, 추론 최적화 부분을 읽는다.
- [vLLM Structured Outputs](https://docs.vllm.ai/en/latest/features/structured_outputs/): JSON 스키마를 이용한 출력 제약 개념과 예제. 실행 API는 설치 버전과 대회 서버 버전을 확인한다.
- [대회 기본 베이스라인](https://dacon.io/competitions/official/236754/codeshare/14154): 위 개념을 프로젝트 입출력 흐름에 연결한다.

### 실습과 완료 기준

공고에서 금액·날짜·참가자격 문구를 JSON으로 추출한다. 원문에 없는 값, 파싱 실패, 잘못된 타입, 잘린 출력을 각각 검사한다.

완료 기준: JSON 형식 준수율과 내용 정답률을 따로 측정한다. 구조화 출력은 사실성을 보장하지 않는다는 점을 설명한다.

## 7. 정보 검색과 임베딩

### 배울 개념

- corpus(검색할 문서 집합), query(질의), index(검색용 자료구조).
- 역색인, TF-IDF, BM25, sparse retrieval(주로 단어 일치 기반 검색).
- dense retrieval(학습된 벡터 표현을 이용한 검색), 문장 임베딩, 코사인 유사도.
- top-k, metadata filtering, exact/approximate nearest neighbor.
- hybrid search(키워드와 벡터 검색 결합), reranking(후보 재정렬).
- 검색 평가: Recall@k, MRR, nDCG의 의미.

벡터 DB는 임베딩 모델도, RAG 전체도 아니다. 벡터와 메타데이터를 저장·검색하는 구성요소다. 작은 문서 집합은 배열로 검색부터 구현할 수 있다.

### 자료

- [Introduction to Information Retrieval — Stanford](https://nlp.stanford.edu/IR-book/): 무료 영어 교재. 역색인, 점수 기반 검색, 검색 평가, 확률적 검색 부분을 필요할 때 읽는다.
- [Sentence Transformers Semantic Search](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html): 질의와 문서의 임베딩을 비교하는 실습.
- [Sentence Transformers Retrieve & Re-Rank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html): 1차 검색과 재정렬의 역할 차이.
- [BGE-M3 모델 카드](https://huggingface.co/BAAI/bge-m3): 프로젝트 제공 임베딩 모델을 이해하는 자료. 모델 카드와 실제 사용 버전의 입력 규약을 확인한다.

### 실습과 완료 기준

조문 100개 안팎으로 검색기를 만든다. 질문 20개와 관련 조문을 사람이 정리하고 BM25와 벡터 검색을 비교한다. 법 조항 번호·금액·부정 표현이 있는 질문도 포함한다.

완료 기준: 검색 유사도가 법적 적용 가능성이나 정답 확률과 같지 않음을 이해하고, 왜 검색이 실패했는지 설명한다.

## 8. RAG와 근거 추적

### 배울 개념

- 수집·파싱 → 문서 분할 → 색인 → 검색 → 문맥 구성 → 생성 → 검증.
- chunk(문서 조각), overlap, 조문·절·표 구조를 보존하는 분할.
- 문서 ID, 조문 번호, 버전, 원문 위치를 보존하는 provenance(출처 추적).
- 문맥 길이 예산, 질의 재작성, 검색 필터, 부모 문단 복원.
- 검색 실패와 생성 실패를 구분하는 평가.
- 정답성, 근거 충실성, 인용 정확성, 답변 가능 여부.
- RAG와 fine-tuning의 차이. RAG에 자료를 추가하는 것은 일반적으로 모델 가중치 업데이트가 아니다.

### 이 프로젝트에서는 두 가지 검색을 구분한다

1. **법령 검색:** 어떤 판단 기준을 적용할지 찾는다.
2. **공고 내 근거 검색:** 현재 공고의 어느 문장이 판단을 뒷받침하는지 찾는다.

법령 문구와 공고의 증거 문구는 역할이 다르다. 필요한 기재가 없다는 판단은 관련 문서를 충분히 보았는지까지 확인해야 한다. 상위 검색 결과에 문구가 없다고 전체 공고에 없다고 결론낼 수 없다.

### 자료

- [대회 법령 RAG 베이스라인](https://dacon.io/competitions/official/236754/codeshare/14155): 가장 먼저 프로젝트 흐름과 비교한다.
- [Contextual Retrieval — Anthropic](https://www.anthropic.com/engineering/contextual-retrieval): 청크를 떼어낼 때 맥락이 사라지는 문제와 개선 아이디어. 기본 RAG 구현 후 읽는 심화 자료이며 결과 수치를 자기 데이터에 일반화하지 않는다.
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401): RAG 원 논문. 초록·도식·문제 정의부터 읽는다. 현대 RAG의 모든 구현이 논문 구조와 같지는 않다.
- [Lost in the Middle](https://arxiv.org/abs/2307.03172): 긴 문맥에서 정보 위치가 성능에 영향을 주는 실험. 자기 모델과 자료에서 위치·길이에 따른 차이를 직접 확인한다.

### 실습과 완료 기준

LLM 단독, 항목별 관련 조문 직접 제공, BM25 RAG, 벡터 RAG를 같은 평가셋에서 비교한다. 먼저 단순 함수로 각 단계를 구현하고, 구조를 이해한 뒤 프레임워크 도입을 판단한다.

완료 기준: 틀린 답 하나를 검색·문맥 구성·생성·검증 중 어느 단계에서 발생했는지 추적한다. 정답 조문을 직접 넣었을 때 고쳐지는지도 비교한다.

## 9. 입찰·법령 도메인

### 배울 개념

- 국가계약과 지방계약, 법률·시행령·시행규칙·예규·고시의 관계.
- 계약방법, 참가자격, 낙찰방법, 추정가격, 고시금액.
- 지역·실적 제한, 중소기업자 간 경쟁, 직접생산확인, 공동수급, SW 사업.
- 적용 조건 → 본문 규정 → 단서·예외 → 사실관계 대조 순서.
- 기준일과 법령 버전, 금액·날짜·품목의 정확한 비교.
- 위반 문구 존재, 필수 문구 부재, 문서·메타데이터 불일치의 차이.
- 관측 불완전성: 문서 누락과 실제 기재 부재를 구분한다.

### 자료와 실습

- [대회 데이터 명세](https://dacon.io/competitions/official/236754/talkboard/417195?dtype=recent&page=1), 배포 항목표·법령패키지·dev 사례를 주교재로 삼는다.
- [국가법령정보센터](https://www.law.go.kr/)는 배경지식 학습과 법령 구조 이해에 참고한다.
- [대회 규칙](https://dacon.io/competitions/official/236754/overview/rules): 실제 대회 파이프라인에는 허용된 자료와 고정 법령 스냅샷을 사용한다. 일반 학습 실습과 제출 구현을 구분한다.

각 항목에 적용 조건, 위반 조건, 예외, 필요한 필드, 근거 위치, 정상 사례, 위반 사례를 적은 판단 카드를 만든다. 전체 법령을 암기하기보다 사례를 읽으며 연결한다.

## 10. 평가·운영·재현성

### 배울 개념

- 전체 F1과 항목별 precision/recall/F1, 근거 추출 정확성, 검색 Recall@k.
- 사람이 만든 정답셋과 라벨 지침, 불확실·불일치 사례의 검토.
- 개선용 사례와 최종 확인용 사례 분리. 유사·중복 공고의 분할 주의.
- 합성 라벨은 정답이 아닐 수 있음. 생성 모델의 오류를 검증에 재사용하지 않기.
- LLM-as-a-judge: 모델을 평가자로 쓰는 방법과 그 편향·오류. 사람 평가를 무조건 대체하지 않기.
- ablation: 구성요소 하나를 빼거나 바꾸며 효과를 확인하는 실험.
- 지연 시간, 처리량, 입력/출력 토큰, batch, GPU 메모리, 양자화, KV cache.
- 로그·버전·seed, 결과 캐시와 재현성의 한계, 오류 처리.
- 원문을 명령으로 취급하지 않기, 민감정보·권한 관리, 사람이 검토할 수 있는 출력.

### 자료

- [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/): 평가, 추론 최적화, 운영 아키텍처 부분.
- [Building a Generative AI Platform — Chip Huyen](https://huyenchip.com/2024/07/25/genai-platform.html): 작은 RAG 이후 전체 서비스 구성요소를 이해할 때 읽는다.
- [대회 평가 안내](https://dacon.io/competitions/official/236754/overview/evaluation): 프로젝트 지표, 근거, 실행 환경 계약.

### 실험 기록 형식

| 실험 | 바꾼 것 | 데이터/프롬프트 버전 | 항목별·평균 F1 | 검색 지표 | 근거 검증 | 실행 시간 | 대표 오답 |
|---|---|---|---|---|---|---|---|
| baseline | 변경 없음 | 기록 | 기록 | 해당 시 기록 | 기록 | 기록 | 원인 기록 |

완료 기준: 개선 주장을 같은 평가셋의 비교 결과로 설명하고, 다른 사람이 설정과 버전을 따라 결과를 확인할 수 있다.

## 11. 추천 책을 고르는 방법

1. **첫 머신러닝 책:** 《혼자 공부하는 머신러닝+딥러닝》. 무료 대안은 Google ML 과정.
2. **LLM 주교재:** 《Hands-On Large Language Models》. 무료 보완은 Hugging Face 강의와 Illustrated Transformer.
3. **프로젝트 설계 참고서:** 《AI Engineering》. 작은 LLM/RAG를 만든 후 읽으면 설계 판단과 연결하기 쉽다.
4. **데이터 처리 참고서:** 《Python for Data Analysis》. 무료 웹판에서 필요한 부분을 읽는다.
5. **원리 심화 선택:** 《밑바닥부터 시작하는 딥러닝 1》 또는 《Hands-On Machine Learning》. 모두 구매할 필요는 없다.

책의 설명은 개념을 익히는 데 사용하고, 오래된 예제의 실행 API는 설치한 라이브러리 공식 문서와 대조한다. 대회 제출에서는 대회 고정 환경과 공식 베이스라인을 우선한다.

## 12. 누적 실습 순서

1. **데이터 탐색기:** 공고·첨부·메타데이터와 품질 통계 확인.
2. **작은 분류 실험:** 일반 학습 데이터로 train/validation과 오류 분석 경험.
3. **정보 추출기:** 공고에서 금액·날짜·참가자격을 JSON으로 추출.
4. **법령 검색기:** BM25와 임베딩 검색 비교.
5. **한 항목 판정기:** 적용 조건과 근거를 포함한 판단.
6. **24개 항목 확장:** 항목별 평가와 부재·불일치 처리.
7. **재현 가능한 파이프라인:** 실행 설정, 로그, 결과, 오답 리포트 보존.

각 실습은 “읽기 → 결과 예상하기 → 직접 실행하기 → 실패 사례 찾기 → 자기 말로 설명하기”로 마무리한다. 진도 기준은 강의 완강이 아니라, 새 사례에서 작동 방식과 실패 원인을 설명할 수 있는지다.

처음부터 분산 학습, 거대 모델 사전학습, 강화학습 구현, 다중 에이전트, GraphRAG, 복잡한 벡터 DB 운영까지 확장할 필요는 없다. 기본 검색과 평가를 이해한 뒤 프로젝트에서 실제로 필요한 심화 주제를 선택한다.
