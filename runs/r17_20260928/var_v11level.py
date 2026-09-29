"""L: v11(경쟁제품 입찰·기업규모 제한 없음)도 v13·v15처럼 기업규모 수준만 'LLM 없음 → 정규식 수준'으로 채운다.
  python runs/r17_20260928/var_v11level.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = 'ITEM_SOURCE.update({"v13": "llm_or_level", "v15": "llm_or_level", "v19": "or"})\n'
new = old + ('# 09-28 L: v11도 수준만 LLM∨정규식. LLM이 수준을 못 읽거나(근거 미대조로 버림) 없음이라 해도 본문 자격 줄에 기업규모 제한이\n'
             '# 있으면 v11(제한 없음)이 아니다(dev DEV-074 v13 공고: 본문 소기업 제한인데 LLM 수준이 비면 v11 오탐).\n'
             'ITEM_SOURCE["v11"] = "llm_or_level"\n')
assert src.count(old) == 1
open(sys.argv[2], "w", encoding="utf-8").write(src.replace(old, new))
