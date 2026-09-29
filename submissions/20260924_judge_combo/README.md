# judge_combo — v20_quote_region35 + LLM 직접 판정 호출(항목별 조합)

상태: **보류 · 미제출.** 09-23 int8 실험에서 LLM 직접 판정이 규칙보다 낮아(교차검증 0.8116·0.8183 < 0.8313) 조합표를 채우지 않았다. 틀은 다음 판정 프롬프트 실험에 재사용한다.

이전 상태: 틀(미완성). 항목별 조합표 `JUDGE_POLICY`가 전부 `"rule"`이라 지금은 [`20260924_v20_quote_region35`](../20260924_v20_quote_region35/README.md)와 **같은 CSV**를 낸다(mock 바이트 비교 확인).
클라우드 int8 실험(`cloud/run_exp.sh`) 결과로 `JUDGE_VARIANT`·`JUDGE_POLICY`를 채운 뒤 제출한다.

## 무엇이 다른가

- 단계 8 **LLM 직접 판정**: 24개 항목 기준·금액 문턱을 담은 시스템 프롬프트 + 본 호출과 같은 원문 발췌 → `판단_메모` + v1~v24 불리언.
  프롬프트 문자열은 실험 스크립트 `cloud/script_dump.py`와 **동일**하다(diff 확인). 그래야 실험 결과가 옮겨진다.
- `JUDGE_VARIANT="rag"`면 `model/cases.json`(dev 200건 정답 사례집, `cloud/build_cases.py`로 생성)에서 비슷한 사례 2건을 예시로 붙인다.
  규칙 2-1(`model/`에는 RAG 인덱스 등 정적 자산)·2-2(제공 자료로 만든 자가 라벨)·2-5(평가 공고 간 정보 공유 없음)에 맞춘 설계다.
- 조합: `"rule"` 판정기만 · `"judge"` LLM만 · `"or"` · `"and"`. 판정 출력이 없거나 파싱 실패면 그 공고는 판정기 결과를 쓴다.
- 시간: 전부 `"rule"`이면 판정 호출을 하지 않는다. 예산(6,000초)이 부족하면 판정 호출을 생략하거나 남은 공고를 판정기 결과로 둔다.

## 실험 후 마무리 절차

1. Mac: `runs/cloud_int8_exp/`에 결과를 풀고
   `.venv/bin/python scripts/judge_combine.py --raw runs/cloud_int8_exp/out/exp/raw`
2. 출력의 `[judge]`·`[judge_rag]` 블록 중 하나를 고른다. 기준은 **교차검증**과 **무라벨 750 새 양성의 손라벨 정밀도**다.
   dev 전체 선택 점수는 낙관적이다. `judge_rag`는 이웃 dev 공고가 예시로 들어가 더 낙관적이다.
   무라벨에서 새 양성의 정밀도가 그 항목의 F1/2(대략 0.35~0.5)보다 낮은 항목은 `"rule"`로 되돌린다.
3~5. `.venv/bin/python scripts/finalize_judge.py --variant plain|rag --policy '<JSON>'` — 상수 반영, mock(종료코드 0·PASS), ZIP(rag면 `model/` 포함), 압축 안팎 해시·SHA-256을 한 번에 한다.
6. 시간 확인: 실험 `run.log`의 `실험 직접 판정` 단계 시간으로 1,853건 시간을 추정한다.
   09-23 추정(미측정): 서버 기존 50분 55초 + 판정 호출 약 25~30분 = 약 80분. 예산 관리자가 6,000초에서 멈춘다.

## 검증 (09-23, 틀 상태)

| 검증 | 결과 |
|---|---|
| 문법 | 통과 |
| `JUDGE_POLICY` 전부 rule → mock CSV | `v20_quote_region35`와 바이트 동일 |
| 정책 적용 함수 | or·and·judge 동작, 판정 출력이 비면 판정기 결과 유지 |
| `rag` 변형 + 정책 활성 mock | 단계 8 실행, 사례집 200건을 `model/`에서 로드, 자가검증 PASS |
| 근거 후보를 모든 항목에 생성(LLM 판정이 새로 켠 항목도 근거를 갖게) | int8 dev 200행이 기존 후보와 **완전히 같음** · mock CSV 바이트 동일 |
| `scripts/finalize_judge.py`(정책 반영 → mock → ZIP → 해시) | rag 시험 실행 성공 후 틀로 되돌림 |

실행하지 않은 것: GPU 실행(판정 출력은 실험 후 생긴다), 서버 시간 측정.
