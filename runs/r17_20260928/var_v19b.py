"""V19B: 확약서 요구 시점 표현에 '입찰 전·이전', '투찰 전', '개찰 시', '미제출 시 입찰 …'을 더한다(항목표 v19 비고 '입찰 전 발급 … 표현 다양').
  python runs/r17_20260928/var_v19b.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = 'V19_BID_RE = re.compile(r"입찰\\s*(서|참가|시|마감|등록)|마감|참가\\s*신청|투찰|참가\\s*전|개찰\\s*(일\\s*)?(전|이전)")\n'
new = ('V19_BID_RE = re.compile(r"입찰\\s*(서|참가|시|마감|등록)|마감|참가\\s*신청|투찰|참가\\s*전|개찰\\s*(일\\s*)?(전|이전)"\n'
       '                        # 09-28 R17 V19B: \'입찰 전, 제조사 … 기술지원확약서 1부 제출 필수\', \'… 미제출자는 개찰시 제외\'(항목표 비고 \'입찰 전 발급\')\n'
       '                        r"|입찰\\s*(전|이전)|개찰\\s*시|미제출\\s*시\\s*(입찰|개찰)")\n')
assert src.count(old) == 1, src.count(old)
open(sys.argv[2], "w", encoding="utf-8").write(src.replace(old, new))
