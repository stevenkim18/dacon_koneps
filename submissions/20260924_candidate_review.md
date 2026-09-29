# 2026-09-24 제출 후보 비교 (2026-09-23 검토)

**권장 제출본: [`20260924_int8_quote_port/submit.zip`](20260924_int8_quote_port/submit.zip).** `20260924_edit_model_combo`의 저장 출력상 dev 이득은 확인되지만, 평가셋에도 이어질 근거가 약하고 제공 자료로 직접 검토한 위반을 대량으로 지운다. 두 후보 모두 **아직 DACON 미제출**이므로 Public 점수는 없다. 기존 최고 Public은 `20260923_v22_region_fix`의 **0.6888170931**, 서버 실측 **50분 55초**다.

| 비교 | int8_quote_port | edit_model_combo |
|---|---:|---:|
| 기준 | v20_quote_region35 + int8 인용 복원·v24 원문 업종코드 | 왼쪽 + v9 AND·v16/v18 meta 게이트·v22 표현 변경 |
| RunPod L40S, vLLM 0.26, int8 저장 출력 dev 200 macro F1 | **0.8583**, 교차 0.8327 | **0.8633**, 교차 0.8398 |
| 같은 환경의 950건 묶음 출력 중 dev 200 재채점 | 0.8525, 교차 0.8277 | 0.8575, 교차 0.8349 |
| MLX 4bit 저장 출력 dev 200 | **0.8706**, 교차 0.8397 | 0.8562, 교차 0.8086 |
| int8 dev 200 판정 변화(왼쪽 기준) | 기준 | 정탐 **2건 제거**, 오탐 **8건 제거**. v22 변화 0 |
| int8 무라벨 750 판정 변화(왼쪽 기준) | 기준 | 양성 **43건 제거**. 기존 자가 라벨: 위반 31, 비위반 2, 보류·미라벨 10 |
| 무라벨 20,000 정규식 재생 양성 수 | 4,857 | 4,215 (−642: v16 −229, v18 −447, v22 +34). 이 재생은 v9 LLM 판정 변화를 포함하지 않음 |
| ZIP·mock | ZIP SHA-256 `cbb7a65afa622b5adcb2971fdf8a15a9ffabede628aabdf0a25517c6cd7d4184`, mock PASS | ZIP SHA-256 `cf5cbc530ea38251ab88f5e4a53ca14c028c4b8b0c8b4de02077b05bb9588be9`, mock PASS |
| 실제 1,853건 서버 실행 시간·Public | 미측정 | 미측정 |

숫자의 출처: 각 후보의 [`dev_validation.log`](20260924_int8_quote_port/dev_validation.log)·[`README.md`](20260924_int8_quote_port/README.md), [`edit_model_combo/dev_validation.log`](20260924_edit_model_combo/dev_validation.log)·[`README.md`](20260924_edit_model_combo/README.md). `mock`은 형식과 실행 경로 검사이며 고정 LLM 성능 검증이 아니다. 두 스크립트의 문법 검사와 ZIP 안팎 `script.py` 바이트 일치는 이번 검토에서 다시 확인했다. 실제 시간 약 51분은 이전 제출의 실측에서 **추정**한 값이다.

## 항목별 판단

- **v9 (특정 모델명):** `edit_model_combo`는 전용 호출과 본 호출이 둘 다 참일 때만 양성으로 한다. int8 dev에서 F1 **0.476 → 0.571**이지만 정탐 `PPS-DEV-09`를 지웠다. 무라벨 750에서 지운 v9 양성에는 자가 라벨 위반 9건이 있다. 운영진은 규격서 등의 모델명도 v9 판단 대상이라고 설명했다. 본 호출이 긴 첨부의 모델명을 놓쳤다는 이유만으로 전용 호출의 양성을 지우는 것은 위험하다. [운영진 답변](https://dacon.io/competitions/official/236754/talkboard/417272)
- **v16·v18 (기업규모 제한 부재):** `edit_model_combo`는 `meta.조항호내용`에 기업규모 낱말이 없으면 위반을 0으로 바꾼다. dev에서는 `PPS-DEV-20` v16 정탐 1건을 잃고 5월 묶음의 오탐 2건을 지웠다. 무라벨 750에서 지운 양성 다수는 제공 자료·배포 법령을 근거로 만든 자가 라벨에서 위반이었다. `조항호내용`의 다른 등록 사유가 공고문 내 기업규모 제한 부재의 예외를 뜻하지는 않는다. 운영진 답변도 등록된 계약방법만으로 v16·v18 적용을 배제하지 말고 실제 `docs`와 예외 사유를 보도록 했다. [계약방법 관련 운영진 답변](https://dacon.io/competitions/official/236754/talkboard/417700)
- **v22 (설명회 참석 제한):** `edit_model_combo`의 새 정규식은 직접 만든 편집 문장 시험에서 **80/144 → 136/144**로 좋아졌다. 그러나 저장된 dev·무라벨 750 출력에는 판정 변화가 **0**이고, 20,000 재생에서 +34건의 진위는 확인되지 않았다. v22만 이식한 후보가 현재 제출본보다 낫다고 판단할 실측 자료가 없다.

## 가설의 한계와 결정

`edit_model_combo`의 예상 Public **0.705~0.71**은 “평가 공고가 위반 문장 편집본이며 자연 공고의 위반은 대부분 라벨 0”이라는 모형을 전제로 한 **추정**이다. 운영진은 dev 라벨이 실제 검토 업무 이력에 기반하고 노이즈가 있으며, 평가셋은 dev와 별도의 검증 절차로 관리한다고 설명했다. 따라서 dev의 5월 묶음 0 라벨을 평가셋의 일반 규칙으로 옮길 근거가 없다. [dev 성격·평가셋 관련 운영진 답변](https://dacon.io/competitions/official/236754/talkboard/417272)

`int8_quote_port`는 int8 dev 두 실행에서 각각 **정탐 +3, 오탐 0**이고, 무라벨 750에서 기존 손라벨 1을 지우지 않았다. 인용을 실제 원문의 부분문자열로 복원하는 변경은 2차 평가의 근거 문자열 요건에도 맞다. 다만 후보 README의 Public **0.690~0.697**도 예측이며, 서버 제출 결과로 확인되지 않았다. v20의 1억 미만 수의계약 SW 공고 +69와 v24 업종코드 +18의 실제 효과도 미확인이다.

**새 후보는 만들지 않는다.** 두 후보의 변경 중 검증된 개선만 고르면 기존 `int8_quote_port`가 남는다. 9월 24일 제출 전 공식 마감·하루 1회 제한을 다시 확인하고, 업로드 파일은 위 ZIP 해시와 대조한다. 제출 후에는 실제 점수·실행 시간·제출 ID를 각 후보 README와 [`submissions/README.md`](README.md)에 기록한다. [공식 규칙](https://dacon.io/competitions/official/236754/overview/rules) · [평가 방식](https://dacon.io/competitions/official/236754/overview/evaluation)

**결과(2026-09-24):** `int8_quote_port` 제출 → Public **0.690815618**(+0.0019985249), 서버 51분 9초. 기록은 [`20260924_int8_quote_port/README.md`](20260924_int8_quote_port/README.md) 결과 절, 해석과 다음 후보는 [study log 09-24 ①](../docs/05_study_log/20260924/1.%20int8_quote_port_result_and_next.md).
