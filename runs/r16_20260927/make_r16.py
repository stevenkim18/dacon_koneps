"""09-27 밤 R16 — 제외어가 지우던 '진짜 자격 문장' 되살리기(실적·지역). wrap_r15 위에 얹는다. 판정기·정규식만 바뀐다.

자연 공고 20,000에서 자격 줄 후보를 넓게 모아(runs/r16_20260927/harvest.py) 규칙이 못 읽는 줄을 필터별로 나눴다.
09-23 ⑤에 '아직 재지 않았다'고 적어 둔 제외어 위험(실적 EVAL_CONTEXT_RE의 '인정·대상으로', 지역 '확인서·평가')이 실제로 컸다.
 P) 실적: 괄호·※ 주석을 걷어 낸 본문이 입찰자 자격 절('…실적이 있는/보유한 업체·자')이면 '인정·대상으로·합산·건수·실적만'이
    있어도 자격 줄로 본다('공공기관을 대상으로 … 실적이 있는 업체', '…실적이 있는 업체(준공 건만 인정)', '합산 3천만원 이상의
    수행실적이 있는 업체'). 본문에 배점·점·평가·기재·'실적 인정/인정 범위/…인정함'·우대·보증금·각서·삭제·'업체 중 … 건수'가
    있으면 그대로 거른다. 이렇게 되살린 줄만 서류·제안서 낱말 필터를 주석 걷은 본문에 건다.
 I) v4 공공 발주처: '국가종합전자조달시스템', '국가를 당사자로 하는 계약에 관한 법률', '국가계약법', '국가에서 인증받은'의
    '국가'는 발주처가 아니다(자연 공고 판독: 등록 요건·법령 이름이 든 실적 줄이 v4로 켜졌다).
 R) 지역: 입찰자 지역 자격 절(주체 → 지명 → 서술 → 업체·자, 지명 → 본점·사업장 → 둔·두고, 지명 → 소재 업체, 지명에 둔 업체)
    REGION_QUAL_RE가 있는 줄은 첫 40자 '주소·위치·장소·납품·설치·전화' 필터, '확인서' 필터, '본사만 걸린 줄' 필터에서 되살린다
    ('소재지가 강원특별자치도에 위치한 업체', '납품이 가능한 업체로서 주된 영업소의 소재지가 부산광역시에 …', 기업규모 자격과 지역
    자격이 한 줄에 있는 경우, '경기도 소재 업체'). 앵커 낱말로만 들어온 줄('…전라남도에 둔 업체이어야 합니다', '제주특별자치도에
    영업소를 두고 있는 업체')도 이 자격 절이 있어야 받는다. 되살린 줄은 **자격 절 구간만** 판정에 쓴다(줄의 다른 곳에 있는 기초
    토큰·시도가 단위·목록을 바꾸지 않게). 구입·우대·점수·거리·삭제·공동수급 구성원 문맥은 되살리지 않는다.
    지명 약칭(서울·부산·경기·충북·전남 등, 광주 제외)은 이 자격 절 안에서만 시·도로 읽는다('서울, 경기에 있는 업체').
    '청소년수련시설 종합평가 등급'은 평가(가산점) 필터에서 빼고, 평가표 점수 줄(': 5점')은 거른다.
    v24(목록 대조)는 전체 이름 시·도만 쓰는 기존 방식을 그대로 둔다.
사용: make_r16.py SRC.py DST.py [--no-issuer]
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
ISSUER = "--no-issuer" not in sys.argv
with open(src, encoding="utf-8") as f:
    s = f.read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90])
    s = s.replace(old, new)


# ---------- P) 실적 제외어 ----------
sub(r'''EVAL_CONTEXT_RE = re.compile(r"기재|배점|\d+\s*점|건수|합산|평가|인정|실적만|대상으로|제출\s*-|\|\s*\d")''',
    r'''EVAL_CONTEXT_RE = re.compile(r"기재|배점|\d+\s*점|건수|합산|평가|인정|실적만|대상으로|제출\s*-|\|\s*\d")
# 09-27 R16: 위 낱말 중 '인정·대상으로·합산·건수·실적만'은 참가자격 문장에도 흔하다(자연 공고 판독: '공공기관을 대상으로 … 실적이
# 있는 업체', '…실적이 있는 업체(준공 건만 인정)'). 괄호·※ 주석을 걷은 본문이 입찰자 자격 절이고 평가 낱말이 없으면 자격 줄이다.
_PERF_NOTE_RE = re.compile(r"\([^()\n]*\)|\[[^\[\]\n]*\]|［[^］\n]*］|【[^】\n]*】|<[^<>\n]*>|※.*$|\*.*$")
PERF_QUAL_CLAUSE_RE = re.compile(
    r"(실적|경험|이력)[^\n]{0,40}?(이|을|를)?\s*(\d+\s*(건|회)\s*이상\s*)?(있는|보유한|보유하고\s*있는|갖춘|가진)\s*"
    r"(업체|자(?![가-힣])|자이어야|자로|사업자|법인|기관|단체)|실적이\s*(\d+\s*(건|회)\s*이상\s*)?있어야")
PERF_QUAL_BAD_RE = re.compile(r"기재|배점|\d+\s*점|평가|제출\s*-|\|\s*\d|실적\s*인정|인정\s*(기준|범위|방법|대상|한도)"
                              r"|인정\s*(한다|합니다|함|됨)?\s*\.?\s*$|우대|선호|권장|권고|보증금|각서|삭제|업체\s*중|건수의\s*실적")


def perf_main_text(s: str) -> str:
    t = s
    for _ in range(3):
        t = _PERF_NOTE_RE.sub(" ", t)
    return t


def perf_qual_line(s: str) -> bool:
    if "삭제" in s:
        return False
    t = perf_main_text(s)
    return bool(PERF_QUAL_CLAUSE_RE.search(t)) and not PERF_QUAL_BAD_RE.search(t)''')

sub(r'''        if EVAL_CONTEXT_RE.search(s) or PERF_BOILERPLATE_RE.search(s):
            continue
        # 서류 목록·서식 안내는 자격 제한이 아니다(무라벨 라벨 검토: '실적증명서 1부[서식 3]' 류)
        if re.search(r"\d+\s*부\b|서식|제출\s*서류|구비\s*서류", s):
            continue
        # 제안서 작성·발표·정성평가 안내는 자격이 아니다
        if re.search(r"제안서에|제안사의|발표자|정성|제시하며|기술하|열거", s):
            continue''',
    r'''        rescued = bool(EVAL_CONTEXT_RE.search(s)) and perf_qual_line(s)       # 09-27 R16
        if (EVAL_CONTEXT_RE.search(s) and not rescued) or PERF_BOILERPLATE_RE.search(s):
            continue
        s_main = perf_main_text(s) if rescued else s
        # 서류 목록·서식 안내는 자격 제한이 아니다(무라벨 라벨 검토: '실적증명서 1부[서식 3]' 류)
        if re.search(r"\d+\s*부\b|서식|제출\s*서류|구비\s*서류", s_main):
            continue
        # 제안서 작성·발표·정성평가 안내는 자격이 아니다
        if re.search(r"제안서에|제안사의|발표자|정성|제시하며|기술하|열거", s_main):
            continue''')

# ---------- I) v4 공공 발주처의 '국가' 오독 ----------
if ISSUER:
    sub(r'''def public_only_issuer(s: str) -> bool:
    # '실적이 있는 업체 또는 단체'의 단체·법인은 입찰자 형태이지 발주처가 아니다.
    t = re.sub(r"(업체|자)\s*(또는|및|,)\s*(단체|법인)", r"\1", s)''',
        r'''# 09-27 R16: 등록 요건·법령·인증 이름 속 '국가'는 발주처가 아니다(자연 공고 판독: '국가종합전자조달시스템에 … 등록한 업체로
# 최근 3년간 … 실적이 있는 업체', '국가계약법 시행령 제21조에 따라 … 금융기관을 대상으로 … 실적', '국가에서 인증받은 … 시설').
NATIONAL_NAME_RE = re.compile(r"국가\s*종합\s*전자\s*조달(\s*시스템)?|국가를\s*당사자로\s*하는\s*계약에\s*관한\s*법률(\s*시행령|\s*시행규칙)?"
                              r"|국가\s*계약\s*법(\s*시행령|\s*시행규칙)?|국가\s*에서\s*인(증|정)\s*(을\s*)?받은|국가\s*(공인|인증|자격|기술\s*자격)")


def public_only_issuer(s: str) -> bool:
    # '실적이 있는 업체 또는 단체'의 단체·법인은 입찰자 형태이지 발주처가 아니다.
    t = re.sub(r"(업체|자)\s*(또는|및|,)\s*(단체|법인)", r"\1", s)
    t = NATIONAL_NAME_RE.sub(" ", t)''')

# ---------- R) 지역 ----------
sub(r'''def _wrap_ground(ev: Optional[str], src: str) -> Optional[str]:''',
    r'''# 09-27 R16: 입찰자 지역 자격 절. 지명 약칭은 이 절 안에서만 시·도로 읽는다(광주는 경기도 광주시와 겹쳐 뺀다).
SHORT_PROV_MAP = {"서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시", "인천": "인천광역시", "대전": "대전광역시",
                  "울산": "울산광역시", "세종": "세종특별자치시", "경기": "경기도", "강원": "강원특별자치도", "충북": "충청북도",
                  "충남": "충청남도", "전북": "전북특별자치도", "전남": "전라남도", "경북": "경상북도", "경남": "경상남도",
                  "제주": "제주특별자치도"}
SHORT_PROV_RE = re.compile(r"(?<![가-힣])(서울|부산|대구|인천|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)"
                           r"(?:특별시|광역시|특별자치시|특별자치도|시|도)?"
                           r"(?=\s|,|·|ㆍ|‧|、|/|\(|및|또는|와\s|과\s|에|의\s|내|지역|권|소재|인\s|이며|이고|이어야|\)|」|’|'|”|\"|\.|$)")
_RQ_PLACE1 = r"(?:[“\"'‘「『〚]?\s*(?:(?:\[지역:[^\]\n]*\]\s*)+|%s|%s)\s*[”\"'’」』〛]?)" % (PROVINCE_RE.pattern, SHORT_PROV_RE.pattern)
_RQ_PLACE = r"(?:%s(?:\s*(?:,|·|ㆍ|‧|、|/|및|또는|와|과|혹은)\s*%s)*)" % (_RQ_PLACE1, _RQ_PLACE1)
_RQ_NOUN = r"(?:업체|자(?![가-힣])|자이|자로|사업자|사업체|법인|업자)(?!\s*(?:에서|에게|로부터|와\s*공동|과\s*공동))"
REGION_QUAL_RE = re.compile(
    r"(?:주된\s*영업소|영업소|영업장|본점|본사|소재지|사업장|주\s*사무소|주된\s*사무소)[^\n]{0,60}?" + _RQ_PLACE +
    r"[^\n]{0,25}?(?:소재|있|둔|두고|두어|위치|인\s|이며|이고|내|관내|등록되어)[^\n]{0,15}?" + _RQ_NOUN +
    r"|" + _RQ_PLACE + r"\s*(?:에|의|내에|내|관내에|관내|지역에|지역\s*내에)?\s*(?:본사|본점|주\s*사무소|주된\s*영업소|영업소|사업장|주\s*사업장|소재지)"
    r"\s*(?:을|를|이|가)?\s*(?:둔|두고|두어야|있는|소재|보유)[^\n]{0,15}?" + _RQ_NOUN +
    r"|" + _RQ_PLACE + r"\s*(?:에\s*|내\s*|지역\s*|관내\s*)?(?:소재(?:한|하는|하고\s*있는|의|인|를\s*두고\s*있는)?|관내|내)\s*(?:업체|사업자|사업체|법인|업자|자(?![가-힣]))"
    r"|" + _RQ_PLACE + r"\s*(?:내\s*)?에\s*(?:둔|두고\s*있는|두어야\s*하는)\s*(?:업체|자(?![가-힣])|사업자|법인)")
# 자격 절이 있어도 입찰자 참가 제한이 아닌 문맥: 우대·가산·점수, 자재 구입·고용, 거리 기준, 삭제 조항, 공동수급 구성원·분담.
REGION_QUAL_BAD_RE = re.compile(r"우대|가산|가점|배점|:\s*\d+(\.\d+)?\s*점|\d+(\.\d+)?\s*점\s*$|구입|구매하|구매할|사용할|고용|채용"
                                r"|하도급|협력|이내에?\s*(소재|위치)|㎞|km|킬로|거리|삭제|공동\s*(도급|수급|이행)|분담|구성원")
# 자격 절 정규식은 무거워서(긴 공고 6배 느림) 싼 앵커 낱말이 있는 줄에만 돌린다. 네 갈래 모두 이 낱말 중 하나를 품는다.
REGION_QUAL_ANCHOR = r"영업소|영업장|본점|본사|소재|사업장|사무소|둔\s|둔$|두고|두어|위치|관내|[가-힣]내\s*(업체|사업자|자)"
REGION_QUAL_ANCHOR_RE = re.compile(REGION_QUAL_ANCHOR)


def region_qual(s: str) -> Optional["re.Match"]:
    if not REGION_QUAL_ANCHOR_RE.search(s) or REGION_QUAL_BAD_RE.search(s):
        return None
    return REGION_QUAL_RE.search(s)


def region_short_provinces(lines: List[str]) -> set:
    return {SHORT_PROV_MAP[m.group(1)] for x in lines for q in REGION_QUAL_RE.finditer(x) for m in SHORT_PROV_RE.finditer(q.group(0))}


def _wrap_ground(ev: Optional[str], src: str) -> Optional[str]:''')

sub(r'''def rx_region(rec: Dict[str, Any], joined: bool = False) -> List[str]:''',
    r'''REGION_TRIGGER = (r"주된\s*영업소|본점|소재지|본사|소재한\s*(업체|자|사업자)|소재하(는|고)\s*있는|내에\s*소재"
                  r"|에\s*사업자\s*등록을?\s*(한|하고\s*있는)\s*(업체|자)|도내\s*(업체|사업자)"
                  r"|주\s*사무소를?\s*(둔|두고)|소재\s*법인|소재하는\s*(업체|사업자|자|법인)"
                  r"|사업장이\s*[^\n]{0,30}(내에|관내에)\s*(있는|소재)"
                  r"|소재\s*(업체|사업자)|관내\s*(에\s*)?(업체|사업자|사업장|본점|주된)|주된\s*사무소|사업장을\s*(둔|두고)"
                  r"|지역\s*(업체|업자)\s*(만|에\s*한|로\s*제한)")
REGION_TRIGGER_RE = re.compile(REGION_TRIGGER)


def rx_region(rec: Dict[str, Any], joined: bool = False) -> List[str]:''')

sub(r'''    for s in _lines(rec, r"주된\s*영업소|본점|소재지|본사|소재한\s*(업체|자|사업자)|소재하(는|고)\s*있는|내에\s*소재"
                           r"|에\s*사업자\s*등록을?\s*(한|하고\s*있는)\s*(업체|자)|도내\s*(업체|사업자)"
                           r"|주\s*사무소를?\s*(둔|두고)|소재\s*법인|소재하는\s*(업체|사업자|자|법인)"
                           r"|사업장이\s*[^\n]{0,30}(내에|관내에)\s*(있는|소재)"
                           r"|소재\s*(업체|사업자)|관내\s*(에\s*)?(업체|사업자|사업장|본점|주된)|주된\s*사무소|사업장을\s*(둔|두고)"
                           r"|지역\s*(업체|업자)\s*(만|에\s*한|로\s*제한)", joined):''',
    r'''    for s in _lines(rec, REGION_TRIGGER + "|" + REGION_QUAL_ANCHOR, joined):
        # 09-27 R16: 입찰자 지역 자격 절(qual)이 있으면 아래 일부 필터에서 되살리고, 되살린 줄은 자격 절 구간만 쓴다.
        # 기존 트리거에 안 걸리는 줄(앵커 낱말로만 들어온 줄)은 자격 절이 있어야 받는다.
        qual = region_qual(s)
        old = bool(REGION_TRIGGER_RE.search(s))
        if not qual and not old:
            continue
        rescued = not old''')

sub(r'''        if re.search(r"주소|위치|장소|납품|설치|전화|☎", s[:40]):
            continue
        if re.search(r"가산|가점|배점|평가|\+\s*\d+(\.\d+)?\s*점|우선\s*선정", s):      # 지역업체 가산점 조건은 참가 제한이 아니다
            continue''',
    r'''        if re.search(r"주소|위치|장소|납품|설치|전화|☎", s[:40]):
            if not qual:
                continue
            rescued = True                   # 09-27 R16: '소재지가 … 위치한 업체', '납품이 가능한 업체로서 주된 영업소의 소재지가 …'
        # 지역업체 가산점 조건은 참가 제한이 아니다. 시설 등급('청소년수련시설 종합평가 결과 적정')은 가산점이 아니고,
        # 평가표 점수 줄(': 5점')은 가산 조건이다(09-27 R16).
        if re.search(r"가산|가점|배점|평가|\+\s*\d+(\.\d+)?\s*점|우선\s*선정|:\s*\d+(\.\d+)?\s*점|\d+(\.\d+)?\s*점\s*$",
                     re.sub(r"종합\s*평가|평가\s*(등급|결과)", " ", s)):
            continue''')

sub(r'''        if re.search(r"각서|서약|확약|확\s*인\s*서|동의서|법원|재판\s*관할|면\s*소재지|보험\s*대상|대상물|성과품", s):
            continue''',
    r'''        if re.search(r"각서|서약|확약|동의서|법원|재판\s*관할|면\s*소재지|보험\s*대상|대상물|성과품", s):
            continue
        if re.search(r"확\s*인\s*서", s):
            if not qual:
                continue
            rescued = True                   # 09-27 R16: 기업규모 확인서 자격과 지역 자격이 한 줄에 있는 경우''')

sub(r'''        if not re.search(r"주된\s*영업소|본점|소재지|소재한|소재하|내에\s*소재", s) and not restrict:
            continue
        if PROVINCE_RE.search(s) or "단위=기초" in s or "기초자치단체" in s:
            out.append(s)
    return out''',
    r'''        if not re.search(r"주된\s*영업소|본점|소재지|소재한|소재하|내에\s*소재", s) and not restrict:
            if not qual:
                continue
            rescued = True                   # 09-27 R16: '경기도 소재 업체', '대구·경북 지역에 사업장을 보유한 사업자'
        seg = qual.group(0) if rescued else s
        if PROVINCE_RE.search(seg) or "단위=기초" in seg or "기초자치단체" in seg or (qual and SHORT_PROV_RE.search(qual.group(0))):
            out.append(seg)
    return out''')

sub(r'''    provinces = sorted({PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(" ".join(region))}''',
    r'''    provinces = sorted({PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(" ".join(region))} | region_short_provinces(region)''')

with open(dst, "w", encoding="utf-8") as f:
    f.write(s)
print("ok", dst, "issuer" if ISSUER else "no-issuer")
