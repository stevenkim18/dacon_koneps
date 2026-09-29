"""v3 relative-amount performance requirement on top of a base script.

usage: python make_v3rel.py BASE.py OUT.py [--hold]
  --hold : also accept perf lines that end with '…실적 보유' (qualification written as a noun phrase)
"""
import sys

inp, out = sys.argv[1], sys.argv[2]
flags = set(sys.argv[3:])
src = open(inp, encoding="utf-8").read()


def sub(old, new, count=1):
    global src
    assert src.count(old) == count, (src.count(old), old[:90])
    src = src.replace(old, new)


# 실적 금액을 계약 금액 자체로 적은 경우('사업예산 이상', '본 용역 기초금액 이상', '입찰공고금액의 1배 이상',
# '기초금액의 130% 이상'). 항목명 '실적제한 1배수 이상'(비고: 사업예산 기준)과 같은 개념이라 배수(없으면 1배)를 예산에 곱해 비교한다.
sub('''def parse_amounts(s: str) -> List[float]:''', '''PERF_REL_RE = re.compile(
    r"(?:기초\\s*금액|추정\\s*가격|사업\\s*예산(?:\\s*금?\\s*액)?|총?\\s*사업비|사업\\s*금액|예산\\s*액|배정\\s*예산(?:\\s*금?\\s*액)?"
    r"|(?:입찰\\s*)?공고\\s*금액|발주\\s*금액|용역\\s*금액|설계\\s*금액"
    r"|(?:본|당해|해당|이번)\\s*(?:사업|용역|과업|건|물품|입찰)의?\\s*(?:금액|규모|예산|사업비|기초\\s*금액|추정\\s*가격))"
    r"\\s*(?:의|대비|기준)?\\s*(?:(\\d+(?:\\.\\d+)?)\\s*배\\s*수?|(\\d{2,3})\\s*%)?\\s*(?:이상|을\\s*초과|초과)")


def relative_perf_multipliers(s: str) -> List[float]:
    out = []
    for mm in PERF_REL_RE.finditer(s):
        if re.search(r"(아래|다음|하기|별표|별첨|표\\s*\\d*)\\s*(의\\s*)?$", s[max(0, mm.start() - 8):mm.start()]):
            continue                         # '아래 사업금액 이상'은 표에 적은 별도 금액이다
        out.append(float(mm.group(1)) if mm.group(1) else (float(mm.group(2)) / 100 if mm.group(2) else 1.0))
    return out


def parse_amounts(s: str) -> List[float]:''')
sub('''    _perf_amounts = [a for s in perf for a in parse_amounts(s)]''',
    '''    _perf_amounts = [a for s in perf for a in parse_amounts(s)]
    _budget_ref = float(meta(rec, "배정예산금액") or price(rec) or 0)
    if _budget_ref > 0:
        _perf_amounts += [_budget_ref * k for s in perf for k in relative_perf_multipliers(s)]''')

# 상대 금액 표현('이번 사업 금액 이상', '입찰공고금액의 2배 이상')도 실적 줄의 구체성 신호다
sub('''        if not (parse_amounts(s) or PERF_SPECIFIC_RE.search(s) or (public_only_issuer(s)''',
    '''        if not (parse_amounts(s) or PERF_SPECIFIC_RE.search(s) or relative_perf_multipliers(s) or (public_only_issuer(s)''')

if "--hold" in flags:
    # '…이행실적 보유'처럼 명사형으로 끝나는 자격 목록 줄
    sub('''        if re.search(r"업체|자이어야|자\\)|있어야|참가\\s*자격|한함|있는 자|보유한 자|한\\s*자\\b|단체|인\\s*자\\b", s):''',
        '''        if re.search(r"업체|자이어야|자\\)|있어야|참가\\s*자격|한함|있는 자|보유한 자|한\\s*자\\b|단체|인\\s*자\\b|실적\\s*보유\\s*$", s):''')

open(out, "w", encoding="utf-8").write(src)
print("written", out)
