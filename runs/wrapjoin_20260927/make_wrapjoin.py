"""09-27 W(줄바꿈 문장 이어 읽기) — 한 문장이 원문 줄 넘김으로 두세 줄에 나뉘면 한 줄씩 보는 정규식이 자격 어미를 놓친다.
구조 변형 주입(문장 가운데 줄바꿈, 빈 줄 없음)에서 규칙 경로 재현율: v1 80→15/120 · v4 100→15/110 · v5 100→25/110 ·
v21 95→35/100 · v2 150→95/160 · v12 95→50/95 · v19 25→10/25 · v22 105→80/110(기업규모 계열은 09-24 여러 줄 파서로 영향 작음).
dev 정답 근거 54건 중 2건(DEV-01 v1, DEV-21 v17)이 실제로 여러 줄에 걸친 문장이다.

변경(모두 추가형, 기존 한 줄 후보를 먼저 두어 기존 판정·근거는 그대로):
 1) `_lines(rec, pat, joined=True)`면 한 줄 후보 뒤에 '빈 줄 없이 바로 이어지는 줄'을 이은 문장 후보를 덧붙인다
    (빈 줄을 건너 잇지 않는다 — 표 칸끼리 붙는 것을 막는다). 문장 시작 줄부터 최대 4줄·500자.
 2) 실적(v2·v3·v4·v8)·지역(v5~v8)·특정기관(v1)·직생(v12)·확약서(v19)·지분(v21)에 적용. v22는 원문에서 못 찾았을 때만 이은 문장에서 찾는다.
 3) 이은 문장 후보는 이미 잡힌 한 줄을 품지 않은 '새 문장'만 쓴다(이미 잡힌 문장의 금액·시도 목록·판정은 그대로). v24 지역 목록 대조는 한 줄 후보 그대로.
 4) 이은 문장이 근거가 되면 원문 구간(줄바꿈 포함 정확한 부분문자열)으로 되돌려 넣는다.

사용: make_wrapjoin.py SRC.py DST.py
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)


# 1) _lines + 이은 문장 후보
sub('''def _lines(rec: Dict[str, Any], pat: str) -> List[str]:
    rx = re.compile(pat)
    return [ln.strip() for d in rec["docs"] for ln in d["text"].split("\\n") if rx.search(ln)]
''', '''def _lines(rec: Dict[str, Any], pat: str, joined: bool = False) -> List[str]:
    rx = re.compile(pat)
    out = [ln.strip() for d in rec["docs"] for ln in d["text"].split("\\n") if rx.search(ln)]
    if joined:
        out += [x for x in _wrapped_sentences(rec, rx) if x not in out]
    return out


# 09-27 W: 한 문장이 원문 줄 넘김으로 두세 줄에 나뉜 경우('…발주한 동종 용역 실적이 ⏎ 있는 업체')를 위해, 빈 줄 없이
# 바로 이어지는 줄을 이은 문장 후보. 앞 줄이 종결(다·함·음·것·마침표·'…한 자'·'업체')로 끝나지 않고 이 줄이 목록 기호·
# 괄호 주석으로 시작하지 않을 때만 잇는다(기업규모 파서의 _continues와 같은 기준, 단 빈 줄은 건너지 않는다 — 표 칸끼리
# 붙는 것을 막는다). 판정에만 쓰고, 근거는 _wrap_ground로 원문 구간(줄바꿈 포함)으로 되돌린다.
# 익명화 자리표시('[지역:r1|단위=기초|…]', '[수요기관(…)]', '[상세주소]')로 시작하는 줄은 목록 기호가 아니라 문장의 이어짐이다.
_WRAP_TOKEN_START_RE = re.compile(r"^\\[(?:지역:|수요기관|기관|상세주소|시설명|부서|직위|담당자|전화번호|공고번호|우편번호|기관홈페이지)")


def _wrap_continues(lines: List[str], j: int) -> bool:
    if j <= 0 or j >= len(lines) or not lines[j] or not lines[j - 1]:
        return False
    if (_SENT_MARK_RE.match(lines[j]) and not _WRAP_TOKEN_START_RE.match(lines[j])) or _NOTE_START_RE.match(lines[j]):
        return False
    return not _SENT_END_RE.search(lines[j - 1])


# 표 칸(|)·서식 문구(대표자 선임서·참가 확인서·서명란)가 든 이은 문장은 버린다 — 줄을 이으면 표의 주소 칸이나 서식 문장이
# 자격 문장처럼 읽힌다(무라벨 20,000 첫 판 새 적중 판독: '소재지 | 상기인을 … 대표자로 선임합니다', '업체명 | 소재지 | …').
_WRAP_FORM_RE = re.compile(r"\\||선임합니다|위임합니다|확인합니다|\\(\\s*인\\s*\\)|접\\s*수\\s*인|서명\\s*(란|:|：)|\\(\\s*서명\\s*\\)|날인")
_WRAP_TOKEN_RE = re.compile(r"\\[[^\\[\\]\\n]*\\]")  # 익명화 자리표시 안의 | 는 표 칸이 아니다
_WRAP_CACHE: Dict[int, Any] = {}


def _wrapped_all(rec: Dict[str, Any]) -> List[str]:
    key = id(rec)
    hit = _WRAP_CACHE.get(key)
    if hit is not None and hit[0] is rec:
        return hit[1]
    out: List[str] = []
    for d in rec["docs"]:
        lines = [ln.strip() for ln in d["text"].split("\\n")]
        k, n = 0, len(lines)
        while k < n:
            if not lines[k]:
                k += 1
                continue
            e = k
            while e + 1 < n and e - k < 3 and _wrap_continues(lines, e + 1):
                e += 1
            if e > k:
                joined = _join_lines(lines[k:e + 1])
                if len(joined) <= 500 and not _WRAP_FORM_RE.search(_WRAP_TOKEN_RE.sub(" ", joined)):
                    out.append(joined)
            k = e + 1
    if len(_WRAP_CACHE) > 8:
        _WRAP_CACHE.clear()
    _WRAP_CACHE[key] = (rec, out)
    return out


def _wrapped_sentences(rec: Dict[str, Any], rx: "re.Pattern") -> List[str]:
    return [x for x in _wrapped_all(rec) if rx.search(x)]


_WRAP_PLACE1 = r"(?:(?:\\[지역:[^\\]\\n]*\\]\\s*)+|%s)" % PROVINCE_RE.pattern
_WRAP_PLACE = r"(?:%s(?:\\s*(?:,|·|ㆍ|및|또는|와|과|혹은)\\s*%s)*)" % (_WRAP_PLACE1, _WRAP_PLACE1)
_WRAP_REGION_RE = re.compile(
    # 주체 → 지명 → 서술: '본점 소재지가 [지역:…]인 업체', '주된 영업소가 ○○도 관내에 있어야'
    r"(주된\\s*영업소|영업소|본점|본사|소재지|사업장|주\\s*사무소)[^\\n]{0,40}?" + _WRAP_PLACE +
    r"[^\\n]{0,25}?(소재|있는|있어야|둔\\s*(업체|자|사업자)|두고|위치|인\\s*(업체|자|사업자)|내에|관내|한정|한함|로\\s*제한)"
    # 지명 → 주체·서술: '○○도에 본사를 둔', '[지역:…] 관내에 사업장을 두고 있는', '○○도 소재 업체', '○○도에 사업자등록을 한'
    r"|" + _WRAP_PLACE + r"\\s*(에|의|내에|내|관내에|관내)?\\s*(본사|본점|주\\s*사무소|주된\\s*영업소|영업소|사업장)\\s*(을|를|이|가)?\\s*(둔|두고|두어야|있는|소재)"
    r"|" + _WRAP_PLACE + r"\\s*(에\\s*)?(소재\\s*(업체|사업자|법인|하는|한)|관내\\s*(업체|사업자)|지역\\s*(업체|소재)|내\\s*(업체|사업자)|사업자\\s*등록을?\\s*(한|하고))")


def _wrap_ground(ev: Optional[str], src: str) -> Optional[str]:
    """이은 문장 후보가 근거가 되면 원문의 정확한 구간(줄바꿈 포함)으로 되돌린다. 원문에 그대로 있으면 그대로 둔다."""
    if not ev or ev in src:
        return ev
    return _ground_quote(ev, src) or ev
''')

# 2) 실적·지역 정규식 함수에 joined 인자
sub('''def rx_performance(rec: Dict[str, Any]) -> List[str]:
    out = []''', '''def rx_performance(rec: Dict[str, Any], joined: bool = False) -> List[str]:
    out = []''')
sub('''                         r"|\\d+\\s*(회|건)\\s*이상\\s*(수행|납품|공급|운영)한\\s*(업체|자)"):
        if re.search(r"사실이\\s*있는", s)''', '''                         r"|\\d+\\s*(회|건)\\s*이상\\s*(수행|납품|공급|운영)한\\s*(업체|자)", joined):
        if re.search(r"사실이\\s*있는", s)''')
sub('''def rx_region(rec: Dict[str, Any]) -> List[str]:
    out = []''', '''def rx_region(rec: Dict[str, Any], joined: bool = False) -> List[str]:
    out = []''')
sub('''                           r"|지역\\s*(업체|업자)\\s*(만|에\\s*한|로\\s*제한)"):''',
    '''                           r"|지역\\s*(업체|업자)\\s*(만|에\\s*한|로\\s*제한)", joined):''')

# 3) regex_facts: 한 줄 후보 우선, 이은 문장은 덧붙임
sub('''    src = full_text(rec)
    perf = rx_performance(rec)
    region = rx_region(rec)
    level, level_ev = rx_sme_level(rec)
    region_text = " ".join(region) + " " + str(meta(rec, "제한지역코드목록") or "")
    provinces = sorted({PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(" ".join(region))}''',
    '''    src = full_text(rec)
    # 09-27 W: 한 줄 후보를 먼저 두고, 여러 줄로 나뉜 문장 후보를 뒤에 덧붙인다(근거·첫 후보는 그대로).
    perf1 = rx_performance(rec)
    perf = perf1 + [x for x in rx_performance(rec, joined=True) if x not in perf1]
    region1 = rx_region(rec)
    # 지역은 이은 문장 안에서 '영업소·소재지·본점 → 지명 → 소재·둔·있는' 순서로 이어지는 구간만 덧붙인다
    # (지역 단위·시도 목록도 그 구간에서만 읽는다). 이은 줄에 섞인 공고 머리글·현장 주소·협정서 서식의
    # 기초 토큰이 시·도 제한을 시군구(v6)로 뒤집었다(무라벨 20,000 첫 판 v6 +18, 판독상 거의 전부 오탐).
    region = region1 + [m.group(0) for x in rx_region(rec, joined=True) if x not in region1
                        for m in [_WRAP_REGION_RE.search(x)] if m and m.group(0) not in " ".join(region1)]
    level, level_ev = rx_sme_level(rec)
    region_text = " ".join(region) + " " + str(meta(rec, "제한지역코드목록") or "")
    provinces = sorted({PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(" ".join(region))}''')
sub('''    share_extra = [(float(m.group(3)), ln) for ln in _lines(rec, r"공동\\s*(수급|도급|이행|계약)|구성원")''',
    '''    share_extra = [(float(m.group(3)), ln) for ln in _lines(rec, r"공동\\s*(수급|도급|이행|계약)|구성원", joined=True)''')
sub('''    share_extra += [(float(m.group(1)), ln) for ln in _lines(rec, r"공동\\s*(수급|도급|이행|계약)|구성원")''',
    '''    share_extra += [(float(m.group(1)), ln) for ln in _lines(rec, r"공동\\s*(수급|도급|이행|계약)|구성원", joined=True)''')
sub('''    brief_restrict = briefing_restriction(src)''',
    '''    brief_restrict = briefing_restriction(src) or briefing_restriction(
        "\\n".join(_wrapped_sentences(rec, re.compile(r"설명회|현장\\s*설명|설명\\s*회"))))''')
sub('''    direct = [s for s in _lines(rec, r"직접생산")
              if not''', '''    direct = [s for s in _lines(rec, r"직접생산", joined=True)
              if not''')
sub('''    _perf_amounts = [a for s in perf for a in parse_amounts_ext(s)]
    _budget_ref = float(meta(rec, "배정예산금액") or price(rec) or 0)
    if _budget_ref > 0:
        _perf_amounts += [_budget_ref * k for s in perf for k in relative_perf_multipliers(s)]''',
    '''    _perf_amt_src = perf
    _perf_amounts = [a for s in _perf_amt_src for a in parse_amounts_ext(s)]
    _budget_ref = float(meta(rec, "배정예산금액") or price(rec) or 0)
    if _budget_ref > 0:
        _perf_amounts += [_budget_ref * k for s in _perf_amt_src for k in relative_perf_multipliers(s)]''')
sub('''    commit = [s for s in _lines(rec, r"확약서") if''', '''    commit = [s for s in _lines(rec, r"확약서", joined=True) if''')
sub('''    inst_extra = [s for s in _lines(rec, r"한하여|한함|회원|법인|이상|전국")''',
    '''    inst_extra = [s for s in _lines(rec, r"한하여|한함|회원|법인|이상|전국", joined=True)''')
sub('''    inst_only = [s for s in _lines(rec, r"만\\s*(입찰\\s*)?(에\\s*)?(참여|참가|응찰)\\s*(가능|할\\s*수)")''',
    '''    inst_only = [s for s in _lines(rec, r"만\\s*(입찰\\s*)?(에\\s*)?(참여|참가|응찰)\\s*(가능|할\\s*수)", joined=True)''')
# 근거: 이은 문장이면 원문 구간으로
sub('''        "실적_근거": perf[0] if perf else None,''', '''        "실적_근거": _wrap_ground(perf[0], src) if perf else None,''')
sub('''        "지역_근거": region[0] if region else None,''', '''        "지역_근거": _wrap_ground(region[0], src) if region else None,''')
sub('''        "특정기관_근거": (inst_only + inst_extra)[0] if (inst_only or inst_extra) else None,''',
    '''        "특정기관_근거": _wrap_ground((inst_only + inst_extra)[0], src) if (inst_only or inst_extra) else None,''')
sub('''        "확약서_근거": commit[0] if commit else None,''', '''        "확약서_근거": _wrap_ground(commit[0], src) if commit else None,''')
sub('''        "확약서_근거_정규식": commit[0] if commit else None,''', '''        "확약서_근거_정규식": _wrap_ground(commit[0], src) if commit else None,''')
sub('''        "설명회_근거": (brief_restrict.group(0) if brief_restrict else brief_ev) or None,''',
    '''        "설명회_근거": _wrap_ground((brief_restrict.group(0) if brief_restrict else brief_ev) or None, src),''')
sub('''        "공동수급_근거": share_line or None,''', '''        "공동수급_근거": _wrap_ground(share_line or None, src),''')

# 근거(e12): 판정과 같게 이은 문장 후보까지 보고, 원문 구간으로 되돌린다(한 줄 후보가 먼저라 기존 근거는 그대로).
sub('''        cand = [s for s in _lines(rec, r"직접생산") if re.search(r"소지|보유", s)]
        return clean_evidence(cand[0], src) if cand else ""''',
    '''        cand = [s for s in _lines(rec, r"직접생산", joined=True) if re.search(r"소지|보유", s)]
        return (clean_evidence(cand[0], src) or _evidence_span(cand[0], src)) if cand else ""''')

# W-b) v12: 직생 증명서가 환경마크·GR·단체표준과 나란히 '생산 능력 확인 서류'의 하나로 나열된 줄(건설폐기물 처리용역의
#      순환아스콘 생산시설 확인)은 직생 요구가 아니다 — 09-27 정리 C('입증자료(직접생산확인증, 환경마크, GR)를 갖춘 자',
#      무라벨 PPS-D-019104·014423 손라벨 0)와 같은 개념. 무라벨 20,000 기준판 v12 183건 중 21건이 이 줄만으로 켜졌다.
sub("""              if not re.search(r"\\d+\\s*부\\b|해당\\s*시|공고(한|된|하는)\\s*경우|계약\\s*예정자|낙찰\\s*예정자|입증\\s*(서류|자료)", s)
              and (re.search(r"소지|보유", s)""",
    """              if not re.search(r"\\d+\\s*부\\b|해당\\s*시|공고(한|된|하는)\\s*경우|계약\\s*예정자|낙찰\\s*예정자|입증\\s*(서류|자료)", s)
              and not re.search(r"환경\\s*마크|(?<![A-Za-z])G\\s?R(?![A-Za-z])|단체\\s*표준", s)
              and (re.search(r"소지|보유", s)""")

open(dst, "w", encoding="utf-8").write(s)
print("wrote", dst)
