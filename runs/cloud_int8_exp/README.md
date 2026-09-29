# RunPod L40S · vLLM int8 실험 묶음 950건 (2026-09-23)

`cloud/run_exp.sh`로 dev 200 + 손라벨 무라벨 750(`open/exp950.jsonl.gz`)을 모델 1회 로드로 실행했다(파드 시각 05:35~07:06, 5,536초).
코드 `cloud/script_dump.py`(제출 후보 `20260924_v20_quote_region35` 판정 + 실험 스위치), 환경은 [`../cloud_int8_20260923`](../cloud_int8_20260923/README.md)과 같다(vLLM 0.26.0 · torch 2.11.0+cu130 · transformers 5.14.1 · 모델 리비전 `4d7ae498…` · int8 · max_model_len 16384).

| 파일 | 내용 |
|---|---|
| `exp/run.log` | 단계별 시간·유효 건수 |
| `exp/raw/*.jsonl` | 호출별 원본: main·item(592)·model(206)·sme·region·perf·goods(258)·judge·judge_rag(각 950, judge_rag 파싱 실패 1) |
| `exp/submission.csv` | 실적·물품 호출을 켠 상태의 판정 CSV(참고용, 채택 판정원 아님) |
| `combine.log` | `scripts/judge_combine.py --raw runs/cloud_int8_exp/exp/raw` 출력 |

켠 실험: 실적 전용 호출(`PPS_ENABLE_PERF`) · 물품 품목 호출(`PPS_ENABLE_GOODS`) · LLM 직접 판정(`PPS_JUDGE`) · 직접 판정 + dev 사례 2건(`PPS_JUDGE_RAG`, `cloud/cases.json`, 자기 자신 제외).

| 판정원 | dev macro | 비고 |
|---|---:|---|
| 규칙(제출 후보) | 0.8410 | 교차검증(규칙 계열만) 0.8313. 같은 코드 단독 dev 실행은 0.8468 → 배치 구성 변동 약 0.006 |
| + 실적 호출 | 0.8287 | v2 오탐 1→4 · v4·v8 +1 |
| + 물품 품목 호출 | 0.8333 | v10 오탐 2→5 · v11 +1 |
| LLM 직접 판정 단독 · OR · AND | 0.3255 · 0.6879 · 0.4352 | v10·v11·v13·v16·v18 F1 0, v15 오탐 17 · v17 11 · v23 15 · v2 13 |
| 판정+사례 단독 · OR · AND | 0.2994 · 0.6870 · 0.4056 | |
| 항목별 최적 조합 | dev 0.8421 / 0.8447 | **교차검증 0.8116 / 0.8183 < 규칙 0.8313** |

무라벨 750: 판정이 규칙 대비 +302(판정+사례 +275)건을 새로 켰고, 손라벨이 있는 새 양성은 **1/6**만 맞았다.
**결론: 네 실험 모두 기각.** 해석은 [study log 09-23 ① 9절](../../docs/05_study_log/20260923/1.%20leaderboard_gap_and_cloud_int8_plan.md).

분석 시 주의: `apply_perf_call`·`apply_goods_item_call` 안에도 `needs_*` 게이트가 있어, `judge_combine.py`는 실험 판정원에서만 게이트를 연다(처음 분석에서 두 호출이 무시됐던 버그를 고친 뒤의 수치다).
이 폴더는 제출 ZIP에 넣지 않는다.
