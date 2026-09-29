# v20 대기업 참여제한 탐지 보강 (R1) — 채택 후보, 미제출

기준: `submissions/20260919_sme_recall_reviewed/script.py` (제출본, Public 0.6716800657).
변경은 `regex_facts()`의 `대기업_참여제한_문구` 한 곳뿐이다. LLM 호출·프롬프트·스키마는 손대지 않았으므로 **재추론이 필요 없다.**

| 지표 | 기준 | 이 후보 |
|---|---:|---:|
| dev 200 macro F1 | 0.8366 | **0.8403** |
| 교차 검증 | 0.8075 | **0.8117** |
| v20 dev F1 | 0.909 (5/1/0) | **1.000 (5/0/0)** |
| 무라벨 250 정밀도 | 0.765 | 0.765 |
| 무라벨 20,000 v20 발동 | 185건 | **177건** (오탐 8건 제거) |

다른 23개 항목의 dev 판정은 전부 동일하다. v20은 `ABSENCE` 항목이라 근거 문구(2차 정성평가)에 영향이 없다.

근거와 기각한 변형(R2 부가세)은 [study log 4](../../docs/05_study_log/20260919/4.%20v20_sw48_detection.md)에 있다.
`change.diff`가 기준 대비 전체 변경이다. 다음 제출 후보에 접어 넣을 것.

재현:

```sh
python3 scripts/mlx_eval_extract.py --script runs/v20_sw48_20260919/experimental_script.py \
  --outputs runs/mlx/extract_outputs.jsonl --item-outputs runs/mlx/item_outputs.jsonl \
  --model-outputs runs/mlx/model_outputs.jsonl --score-only --cv
```
