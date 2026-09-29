"""V12P: 직생 요구 어미 '…발급받은 업체(증명서 제출)', '…발급받은 자(유효기간 내 …)'처럼 괄호 주석이 바로 붙은 자격 줄도 받는다.
  python runs/r17_20260928/var_v12p.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = '''or (re.search(r"(발급\\s*받은|확인을?\\s*받은|갖춘|제출한)\\s*(제조\\s*)?(업체|자)\\s*(에\\s*한|만|이어야|여야|일\\s*것|로\\s*제한|$|[.)])", s)'''
new = '''or (re.search(r"(발급\\s*받은|확인을?\\s*받은|갖춘|제출한)\\s*(제조\\s*)?(업체|자)\\s*(에\\s*한|만|이어야|여야|일\\s*것|로\\s*제한|$|[.)]|\\((증명서|유효|입찰|전자|제출|[^()\\n]{0,30}(까지|있어야)))", s)'''
assert src.count(old) == 1, src.count(old)
open(sys.argv[2], "w", encoding="utf-8").write(src.replace(old, new))
