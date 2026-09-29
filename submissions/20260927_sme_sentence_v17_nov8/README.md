# sme_sentence_v17_nov8 — `20260927_sme_sentence_v17`의 v8 국가 되돌림 짝

상태: **불필요(09-25) · 미제출.** 09-25가 0.7053으로 '국가 v8 유지' 칸이라 `_nov8` 계열은 쓰지 않는다. 09-27 후보는 [`20260927_private_scope_recall`](../20260927_private_scope_recall/README.md).
변경·판독·점수 추정은 [`20260927_sme_sentence_v17`](../20260927_sme_sentence_v17/README.md)과 같다. 기준만 `_nov8`이다(v8 판정 줄이 `local and …`).

| 검사 | 결과 |
|---|---|
| 생성 | `make_sent.py` → `make_sent2.py`를 `20260926_phrase_parser_recall_nov8/script.py`에 적용. 본판과의 차이는 머리말 한 줄과 v8 판정 줄뿐(`diff`로 확인) |
| 무라벨 20,000 정규식 재생 (`_nov8` 대비) | Δ−61 · 변경 401공고 · 예외 0 · v11 −4 · v13 −88 · v14 +3 · v15 −76 · v16 −5 · **v17 +114** · v18 −5 (본판과 같음) |
| mock | 종료코드 0 · 자가검증 PASS |
| ZIP | `submit.zip` SHA-256 `03b5c8edb3dce9c4ab69a3dbab765a0c64dc54c699bde7f842f1da86c8174c5f` · `script.py` `c267d580…` · `requirements.txt`는 기준과 동일 |
