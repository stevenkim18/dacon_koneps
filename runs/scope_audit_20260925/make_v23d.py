"""v23 briefing-date formats (briefing line only) on top of a base script.

usage: python make_v23d.py BASE.py OUT.py
"""
import sys

inp, out = sys.argv[1], sys.argv[2]
src = open(inp, encoding="utf-8").read()


def sub(old, new, count=1):
    global src
    assert src.count(old) == count, (src.count(old), old[:90])
    src = src.replace(old, new)


sub('''def rx_briefing(rec: Dict[str, Any]) -> Tuple[Optional[date], Optional[date], str]:''',
    '''# 설명회 줄 전용 날짜 형식: 요일 괄호 없는 '2월 7일 14시', 두 자리 연도 ''26. 2. 7.', 시각이 붙은 '2. 7. 14:00'.
# 마감일 탐색에는 쓰지 않는다(목록 번호 등을 날짜로 읽을 수 있어서).
BRIEF_MD_RE = re.compile(r"(?<![\\d\\.])(\\d{1,2})\\s*월\\s*(\\d{1,2})\\s*일")
BRIEF_YY_RE = re.compile(r"['’‘`]\\s*(\\d{2})\\s*[\\.\\-/]\\s*(\\d{1,2})\\s*[\\.\\-/]\\s*(\\d{1,2})")
BRIEF_TIME_RE = re.compile(r"(?<![\\d\\.])(\\d{1,2})\\s*\\.\\s*(\\d{1,2})\\s*\\.?\\s*(?=\\d{1,2}\\s*[:시]|오전|오후)")


def brief_dates(s: str, year: int) -> List[date]:
    ds = dates_in(s, year)
    if ds:
        return ds
    out = []
    for m in BRIEF_YY_RE.finditer(s):
        dt = _to_date(2000 + int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if dt:
            out.append(dt)
    for rx in (BRIEF_MD_RE, BRIEF_TIME_RE):
        if out:
            break
        for m in rx.finditer(s):
            dt = _to_date(year, int(m.group(1)), int(m.group(2)))
            if dt:
                out.append(dt)
    return out


def rx_briefing(rec: Dict[str, Any]) -> Tuple[Optional[date], Optional[date], str]:''')
sub('''        ds = dates_in(s, year)
        if ds:
            brief, ev = ds[0], s
            break''', '''        ds = brief_dates(s, year)
        if ds:
            brief, ev = ds[0], s
            break''')

open(out, "w", encoding="utf-8").write(src)
print("written", out)
