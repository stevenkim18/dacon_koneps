#!/bin/zsh
# r18 후보 검증: r17 대비. 저장소 루트에서 zsh runs/r18_20260928/validate.sh
A=submissions/20260929_r17_edit_shapes/script.py
B=submissions/20260929_r18_fresh_holdout/script.py
T=runs/r18_20260928
PY=.venv/bin/python
( echo "## 1. dev 200 재채점 3벌 (devscore.sh)"; echo "r17:"; zsh runs/review_20260924/devscore.sh $A; echo "r18:"; zsh runs/review_20260924/devscore.sh $B ) > $T/final_core1.log 2>&1 &
( echo "## 2. 저장 출력 판정·근거 차이 (fulldiff, r17 대비)"; $PY runs/int8_port_20260923/fulldiff.py $A $B ) > $T/final_core2.log 2>&1 &
( echo "## 3. 무라벨 20,000 정규식 재생 (preplay, r17 대비)"; $PY runs/r16_20260927/preplay.py $A $B ) > $T/final_core3.log 2>&1 &
( echo "## 4. LLM 입력 동일성 (llm_input_same)"; $PY runs/review_20260926/llm_input_same.py $A $B ) > $T/final_core4.log 2>&1 &
wait
( echo "## 6-1 구조 변형"; $PY runs/wrapjoin_20260927/probe_struct.py $A $B nb=5 ) > $T/final_struct.log 2>&1 &
( echo "## 6-2 H3"; $PY runs/wrapjoin_20260927/probe_inject_h3.py $A $B nb=6 ) > $T/final_h3.log 2>&1 &
( echo "## 6-3 H4"; $PY runs/wrapjoin_20260927/probe_inject_h4.py $A $B nb=6 ) > $T/final_h4.log 2>&1 &
( for p in runs/review_20260925/serverpath_inject.py runs/recall_probe_20260926/probe_inject.py runs/recall_probe_20260926/probe_inject_h.py runs/recall_probe_20260926/probe_inject_h2.py; do echo "### $p"; $PY $p $A $B; done ) > $T/final_inject.log 2>&1 &
wait
( echo "## 6-5 자연 줄 N"; $PY runs/r16_20260927/probe_natural.py $A $B n_lines=120 nb=4 ) > $T/final_natural.log 2>&1 &
( echo "## 6-6 자연 줄 N2"; $PY runs/r16_20260927/probe_natural2.py $A $B ) > $T/final_natural2.log 2>&1 &
( echo "## 6-8 자연 줄 N3"; $PY runs/r17_20260928/probe_n3.py $A $B ) > $T/final_n3.log 2>&1 &
( echo "## 6-10 v1 보류 세트 H5~H9"; for h in runs/r17_20260928/probe_h5_v1.py $T/probe_h6_v1.py $T/probe_h7_v1.py $T/probe_h8_v1.py $T/probe_h9_v1.py; do echo "### $h"; $PY $h $A $B | grep -v miss; done; echo "## 6-11 H10"; $PY $T/probe_inject_h10.py $A $B transforms=T0,T2 ) > $T/final_holdout.log 2>&1 &
( echo "## 6-9 LLM 경로 탐침 172(b4)"; for s in $A $B; do echo "### $s"; $PY runs/r17_20260928/score_llm_probe.py $s runs/r17_20260928/llm_probe b4; done ) > $T/final_llmprobe.log 2>&1 &
wait
echo VALIDATION_DONE > $T/final.flag
