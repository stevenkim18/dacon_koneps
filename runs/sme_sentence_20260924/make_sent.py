"""Build the sentence-aware SME candidate variant on top of a base script.

usage: python make_sent.py BASE.py OUT.py
"""
import sys

base, out = sys.argv[1], sys.argv[2]
src = open(base, encoding="utf-8").read()


def sub(old, new, count=1):
    global src
    assert src.count(old) == count, (src.count(old), old[:80])
    src = src.replace(old, new)


# 1) sentence-aware candidate windows
sub('''    pat = re.compile(r"소기업|소상공인|중소기업|중기업")
    out: List[Tuple[str, str]] = []
    for d in rec["docs"]:
        lines = [ln.strip() for ln in d["text"].split("\\n")]
        for k, ln in enumerate(lines):
            if not pat.search(ln):
                continue
            out.append((ln, ln))
            if k + 1 < len(lines) and lines[k + 1]:
                out.append((f"{ln} {lines[k + 1]}", ln))
    return out
''', r'''    pat = re.compile(r"소기업|소상공인|중소기업|중기업")
    out: List[Tuple[str, str]] = []
    for d in rec["docs"]:
        lines = [ln.strip() for ln in d["text"].split("\n")]
        for k, ln in enumerate(lines):
            if not pat.search(ln):
                continue
            s, e = _sentence_span(lines, k)
            if s == k:
                out.append((ln, ln))
                if k + 1 < len(lines) and lines[k + 1]:
                    out.append((_join_lines(lines[k:max(k + 1, e) + 1]), ln))
            else:
                # 세 줄 이상으로 나뉜 자격 문장의 가운데 줄('따른 소상공인으로서 … 발급된')에 다음 줄만 붙여 읽으면 앞 줄의
                # '중소기업 또는'이 빠져 수준을 거꾸로 읽는다(dev DEV-21 v17 누락). 문장 시작부터 끝까지 붙여 판단하고,
                # 조각+다음 줄 창은 만들지 않는다. 줄 단독 후보는 남긴다(자격 동사가 없으면 어차피 채택되지 않는다).
                out.append((ln, ln))
                out.append((_join_lines(lines[s:max(k + 1, e) + 1]), ln))
    return out


# 줄이 앞 줄 문장의 연속인지: 앞 줄이 종결(다·함·음·것·마침표·'…한 자'·'업체'·'(…함)'·줄 끝 '-')로 끝나지 않고,
# 이 줄이 목록 기호·괄호 주석으로 시작하지 않을 때. PDF 추출로 문장 가운데 빈 줄이 하나 끼는 경우도 잇는다.
_SENT_MARK_RE = re.compile(r"^(?:[가-하]\s*[\.\)]|\d{1,3}\s*[\.\)]|\(\s*[\d가-하]{1,2}\s*\)|[①-⑳⑴-⒇㉠-㉭㈀-㈍]"
                           r"|[\-–—•◦○●◎□■▶▷▸►※❍❏✓✔*◇◆▪◈▣◐◑◉☞➢➤|<\[【]|[ⅰ-ⅹⅠ-Ⅻ]|주\s*\d|[ㅇㆍ·]\s)")
_NOTE_START_RE = re.compile(r"^\(\s*(?:\*|※|주|단|참고|예)")
_SENT_END_RE = re.compile(r"(?:[.。!?:：;\-–—]|다|함|음|것|임|요|[한된는인은을]\s*자|업체|\([^()]*(?:함|음|것|다|임)\s*\.?\))\s*$")


def _continues(lines: List[str], j: int) -> bool:
    if j <= 0 or j >= len(lines) or not lines[j] or _SENT_MARK_RE.match(lines[j]) or _NOTE_START_RE.match(lines[j]):
        return False
    p = j - 1
    if not lines[p] and p >= 1:
        p -= 1
    return bool(lines[p]) and not _SENT_END_RE.search(lines[p])


def _sentence_span(lines: List[str], k: int, back: int = 3, fwd: int = 3) -> Tuple[int, int]:
    s = k
    while s > 0 and k - s < back and _continues(lines, s):
        s -= 1
        if not lines[s] and s > 0:
            s -= 1
    e = k
    while e + 1 < len(lines) and e - k < fwd:
        j = e + 1
        if not lines[j] and j + 1 < len(lines) and _continues(lines, j + 1):
            j += 1
        if not _continues(lines, j):
            break
        e = j
    return s, e


def _join_lines(parts: List[str]) -> str:
    """판정용으로 줄을 잇는다. 낱말 가운데 줄바꿈('소상 ⏎ 공인확인서', '중소 ⏎ 기업')은 공백 없이 붙인다."""
    out = ""
    for x in parts:
        if not x:
            continue
        if out and re.search(r"[가-힣]$", out) and re.match(r"[가-힣]", x):
            out += x
        else:
            out += (" " if out else "") + x
    return out
''')

# 2) '중소기업자의 우선조달계약'(조문 제목)도 수준 낱말에서 지운다
sub('''    body = re.sub(r"중소기업자?\\s*(와의\\s*|간\\s*)?우선\\s*조달(계약)?", " ", body)''',
    '''    body = re.sub(r"중소기업자?\\s*(와의\\s*|간\\s*|의\\s*)?우선\\s*조달(계약)?", " ", body)''')

# 3) '중소기업확인서(소기업·소상공인)'은 소기업·소상공인 확인서다
sub('''CERT_SME_RE = re.compile(rf"중\\s*[{DOT}/]\\s*소기업\\s*[{DOT}]?\\s*소상공인\\s*확인서|중소기업\\s*[{DOT}]?\\s*소상공인\\s*확인서|중소기업\\s*확인서"''',
    '''CERT_SME_RE = re.compile(rf"중\\s*[{DOT}/]\\s*소기업\\s*[{DOT}]?\\s*소상공인\\s*확인서|중소기업\\s*[{DOT}]?\\s*소상공인\\s*확인서|중소기업\\s*확인서(?!\\s*\\(\\s*소기업)"''')
sub('''CERT_SMALL_RE = re.compile(rf"(?<![중{DOT}])소기업\\s*[{DOT}및또는,\\s]*소상공인\\s*확인서|(?<![중{DOT}])소기업\\s*확인서")''',
    '''CERT_SMALL_RE = re.compile(rf"(?<![중{DOT}])소기업\\s*[{DOT}및또는,\\s]*소상공인\\s*확인서|(?<![중{DOT}])소기업\\s*확인서"
                           rf"|중소기업\\s*확인서\\s*\\(\\s*소기업\\s*[{DOT}/,]?\\s*소상공인")''')

# 4) '중소기업으로 간주되는 특별법인' 안내는 수준 낱말이 아니다(무라벨 PPS-D-006839·010929)
sub('''    body = re.sub(r"중소기업자?\\s*(와의\\s*|간\\s*|의\\s*)?우선\\s*조달(계약)?", " ", body)''',
    '''    body = re.sub(r"중소기업자?\\s*(와의\\s*|간\\s*|의\\s*)?우선\\s*조달(계약)?", " ", body)
    body = re.sub(r"중소기업(으로)?\\s*간주(되는|된)?", " ", body)''')

# 5) '중, 소기업 또는 소상공인'(쉼표 표기)도 중·소기업이다(무라벨 PPS-D-019656·019675)
sub('''    if re.search(rf"중\\s*[{DOT}/]\\s*소기업|중소기업(자)?", body):''',
    '''    if re.search(rf"중\\s*[{DOT}/,]\\s*소기업|중소기업(자)?", body):''')

# 6) 원문자 변형 글머리(➀·❶)
sub('''r"^(?:[가-하]\\s*[\\.\\)]|\\d{1,3}\\s*[\\.\\)]|\\(\\s*[\\d가-하]{1,2}\\s*\\)|[①-⑳⑴-⒇㉠-㉭㈀-㈍]"''',
    '''r"^(?:[가-하]\\s*[\\.\\)]|\\d{1,3}\\s*[\\.\\)]|\\(\\s*[\\d가-하]{1,2}\\s*\\)|[①-⑳⑴-⒇㉠-㉭㈀-㈍➀-➓❶-❿]"''')

# 7) (선택) 본 호출 LLM의 기업규모 근거 줄도 문장 전체로 넓혀 수준을 판단한다 — v11·v13·v15는 LLM 출처라 서버에서 이 경로를 쓴다
if len(sys.argv) > 3 and sys.argv[3] == "llm":
    sub('''        ev = clean_evidence(raw_ev, full_text(rec))
        level = classify_level(ev)''',
        '''        ev = clean_evidence(raw_ev, full_text(rec))
        level = classify_level(_expand_sentence(rec, ev))''')
    sub('''def _join_lines(parts: List[str]) -> str:''',
        '''def _expand_sentence(rec: Dict[str, Any], ev: str) -> str:
    """근거 문구가 여러 줄 자격 문장의 조각이면 그 문장 전체(판정용)를 돌려준다. 원문에서 못 찾으면 그대로."""
    if not ev:
        return ev
    parts = [x.strip() for x in ev.split("\\n") if x.strip()]
    if not parts:
        return ev
    first, last = parts[0], parts[-1]
    for d in rec["docs"]:
        lines = [ln.strip() for ln in d["text"].split("\\n")]
        for k, ln in enumerate(lines):
            if first in ln:
                kk = k
                for j in range(k, min(k + 10, len(lines))):
                    if last in lines[j]:
                        kk = j
                        break
                s, _ = _sentence_span(lines, k)
                _, e = _sentence_span(lines, kk)
                return _join_lines(lines[s:e + 1])
    return ev


def _join_lines(parts: List[str]) -> str:''')

open(out, "w", encoding="utf-8").write(src)
print("written", out)
