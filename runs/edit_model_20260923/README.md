# 편집 공고 모형 실험 (2026-09-23 밤)

해석은 [study log 09-23 ⑤](../../docs/05_study_log/20260923/5.%20edited_notices_dataset_model.md). GPU 실행 없음 — 저장 출력(4bit dev, 클라우드 int8 dev·무라벨 750)과 무라벨 20,000 정규식 재생만 썼다.

| 파일 | 내용 |
|---|---|
| `pools.py` | dev 예측을 위반 묶음(ID 1~80·131~141)과 5월 묶음으로 나눠 항목별 TP/FP/FN |
| `dump_errs.py` · `errs_int8.txt` · `errs_4bit.txt` | dev 오답 전부(meta·우리 근거·정답 근거) |
| `hist_pools.py` · `hist_pools.json` | 제출했던 7개 버전의 dev 묶음별 성적과 무라벨 750 양성 수 |
| `rate750.py` | 무라벨 750 int8 전 파이프라인 항목별 양성(자연 오탐률) |
| `twopool.py` | 두 묶음 모형(초기 버전) |
| `twins.py` · `twindiff.py` | dev 공고와 가장 비슷한 무라벨 공고 찾기·줄 차이 |
| `paraphrases.py` | dev 편집 문장을 본뜬 항목별 문장 |
| `inject_test.py` · `inject_sme.py` · `inject_v22.py` | 자연 공고에 문장을 넣고 정규식 경로로 켜지는지 |
| `removal_test.py` | 자연 공고에서 기업규모·직생·대기업 자격 줄을 지우고 부재 항목이 켜지는지 |
| `evalvar.py` | 변형 스크립트를 dev(int8·4bit)·무라벨 750 int8로 한 번에 채점 |
| `mk_v22b.py` · `mk_v22c.py` | v22 제한 표현 확대 패치(첫 판) · 제외어를 발표·평가 벌점·운영 안내·명시적 부정으로 다시 정리한 판(`v22narrow3`·`combo3`) |
| `variants/` | `v9and` · `smegate`(v16·v18 meta 게이트) · `smegate_partial`(일반경쟁은 남김) · `v22narrow2`·`v22narrow3` · `combo2`·`combo3`(v9and+smegate+v22). 기준은 `submissions/20260924_int8_quote_port/script.py`. `combo3`에 주석을 단 것이 제출 후보 `submissions/20260924_edit_model_combo/script.py` |

실행은 저장소 루트에서 `.venv/bin/python runs/edit_model_20260923/evalvar.py <script.py> ...` 형태. `inject_*`는 두 번째 인자로 `paraphrases.py`가 있는 폴더를 받는다.
