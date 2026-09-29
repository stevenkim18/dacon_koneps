"""09-24 표현 확장 변형(좁힌 판). 사용: build2.py OUT.py KEYS  (KEYS 예: A2B2C2D2E1 — 두 글자씩)"""
import sys, re
SRC = "submissions/20260925_v8nat_v22fix_v21wide/script.py"
OUT, KEYS = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
def rep(s, old, new):
    assert s.count(old) == 1, (old[:90], s.count(old)); return s.replace(old, new)

def A2(s):  # 기업규모 자격 표지 '…만 참여 가능'(가산·창업·벤처·대기업 문맥 제외)
    return rep(s, '''        if not listed and not re.search(r"한함|한정|제한|소지한|보유(하고|한)|갖춘|등록(한|된)|자이어야|업체이어야"
                                        r"|우선\\s*조달계약\\s*대상|업체일 것|참가\\s*자격|경쟁\\s*\\(|경쟁입찰\\s*\\(", s):
            continue''', '''        if not listed and not re.search(r"한함|한정|제한|소지한|보유(하고|한)|갖춘|등록(한|된)|자이어야|업체이어야"
                                        r"|우선\\s*조달계약\\s*대상|업체일 것|참가\\s*자격|경쟁\\s*\\(|경쟁입찰\\s*\\(", s) \\
                and not (SME_ONLY_RE.search(s) and not SME_ONLY_EXCLUDE_RE.search(s)):
            continue''').replace('''def rx_sme_level(rec: Dict[str, Any]) -> Tuple[str, str]:''', '''# 09-24: '…중소기업자만 참여 가능', '소기업 또는 소상공인만 입찰 참여 가능'도 자격 문장이다. 다만 중소기업 가산 적용 제외
# 상투문, 1억 미만 적법 목록(소기업·소상공인·벤처·창업), SW 대기업 참여제한 설명은 아니다(무라벨 20,000 판독 7건).
SME_ONLY_RE = re.compile(r"만\\s*(입찰\\s*)?(에\\s*)?(참여|참가|응찰)\\s*(가능|할\\s*수|이\\s*가능)")
SME_ONLY_EXCLUDE_RE = re.compile(r"가산|적용하지|창업|벤처|대기업|중견기업|소프트웨어")


def rx_sme_level(rec: Dict[str, Any]) -> Tuple[str, str]:''', 1)

def B2(s):  # v4: 공공 발주처 어휘 확대 + '…이상인 자' + 공공 한정 줄은 '실적이 있는/보유한' 요구가 있으면 구체성 면제
    s = rep(s, 'PUBLIC_ISSUER_RE = re.compile(r"국가|정부|공공기관|지방자치단체|지자체|공기업|대학병원|\\[수요기관|기관(이|에서)?\\s*발주")',
               'PUBLIC_ISSUER_RE = re.compile(r"국가|정부|공공기관|지방자치단체|지자체|공기업|대학병원|\\[수요기관|기관(이|에서)?\\s*발주"\n'
               '                              r"|광역\\s*자치\\s*단체|기초\\s*자치\\s*단체|중앙\\s*행정\\s*기관|관공서|준정부\\s*기관")\n'
               "# 09-24: 공공 발주처로 한정한 실적 요구는 금액·기간이 없어도 구체적이다(집행기준 제5조④3). 단 '실적이 있는·보유한' 요구여야 한다\n"
               "# ('실적 조회 후 결정', '대가지급, 실적', '누계공정 실적', '실적내역 증빙' 같은 줄은 요구가 아니다 — 무라벨 판독).\n"
               'PERF_REQUIRE_RE = re.compile(r"(실적|경험)\\s*(이|을)?\\s*(있는|있어야|보유|갖춘|가진)")')
    s = rep(s, '''PUBLIC_OPEN_RE = re.compile(r"(또는|및|이나|,|·|ㆍ)\\s*(일반\\s*)?(민간|기업체?|회사|법인|단체|상장|사기업|금융기관)"''',
               '''PUBLIC_OPEN_RE = re.compile(r"(또는|및|이나|,|·|ㆍ)\\s*(일반\\s*)?(민간|기업체?|회사|법인|단체|상장|사기업|금융기관|아파트)"''')
    s = rep(s, '''        if not (parse_amounts(s) or PERF_SPECIFIC_RE.search(s)):
            continue
        if re.search(r"업체|자이어야|자\\)|있어야|참가\\s*자격|한함|있는 자|보유한 자|한\\s*자\\b|단체", s):''',
               '''        if not (parse_amounts(s) or PERF_SPECIFIC_RE.search(s) or (public_only_issuer(s) and PERF_REQUIRE_RE.search(s) and not re.search(r"국가관|채용|우선|확인하시|숙지|기술진|인력\\s*풀|구성하여", s))):
            continue
        if re.search(r"업체|자이어야|자\\)|있어야|참가\\s*자격|한함|있는 자|보유한 자|한\\s*자\\b|단체|인\\s*자\\b", s):''')
    return s

def C2(s):  # v12: '발급받은·확인을 받은·갖춘·제출한 업체(자)' + 입찰자 자격 어미(낙찰자 공급·제작 의무 제외)
    return rep(s, '''    direct = [s for s in _lines(rec, r"직접생산") if re.search(r"소지|보유", s) and not re.search(r"\\d+\\s*부\\b|해당\\s*시", s)]''',
                  '''    # 09-24: '발급받은·확인을 받은·갖춘·제출한 업체(자)'도 입찰자 자격 어미가 붙으면 직생 요구로 본다.
    # 낙찰자의 공급 의무·제작 조건 문장은 자격이 아니다(무라벨 PPS-D-015111·016529).
    direct = [s for s in _lines(rec, r"직접생산")
              if not re.search(r"\\d+\\s*부\\b|해당\\s*시", s)
              and (re.search(r"소지|보유", s)
                   or (re.search(r"(발급\\s*받은|확인을?\\s*받은|갖춘|제출한)\\s*(업체|자)\\s*(에\\s*한|만|이어야|여야|일\\s*것|로\\s*제한|$|[.)])", s)
                       and not re.search(r"낙찰자|생산한\\s*제품|제품을\\s*공급|제작하여야|납품하여야", s)))]''')

def D2(s):  # 지역: 새 표현은 입찰자 자격 줄만(도급자·낙찰자 의무, 과업 설명 '가능한', 활용 권고 제외)
    s = rep(s, '''    for s in _lines(rec, r"주된\\s*영업소|본점|소재지|본사|소재한\\s*(업체|자|사업자)|소재하(는|고)\\s*있는|내에\\s*소재"):''',
               '''    for s in _lines(rec, r"주된\\s*영업소|본점|소재지|본사|소재한\\s*(업체|자|사업자)|소재하(는|고)\\s*있는|내에\\s*소재"
                           r"|소재\\s*(업체|사업자)|관내\\s*(에\\s*)?(업체|사업자|사업장|본점|주된)|주된\\s*사무소|사업장을\\s*(둔|두고)"
                           r"|지역\\s*(업체|업자)\\s*(만|에\\s*한|로\\s*제한)"):
        # 09-24: 새로 받은 표현('소재 업체', '관내 업체', '주된 사무소', '사업장을 둔', '지역 업체만')은 입찰자 자격 줄만 본다.
        if not re.search(r"주된\\s*영업소|본점|소재지|본사|소재한\\s*(업체|자|사업자)|소재하(는|고)\\s*있는|내에\\s*소재", s) \\
                and re.search(r"도급자|계약\\s*상대자|낙찰자|활용|임차|하도급|협력|가능한|주요\\s*내용|과업", s):
            continue''')
    s = rep(s, '''        restrict = re.search(r"제한|한함|한정|자격|참가|있는\\s*(업체|자)|둔\\s*(업체|자)|소재한\\s*(업체|자)", s)''',
               '''        restrict = re.search(r"제한|한함|한정|자격|참가|있는\\s*(업체|자)|둔\\s*(업체|자)|소재한\\s*(업체|자)|만\\s*(입찰\\s*)?(참여|참가)", s)''')
    return s

def E1(s):  # 부재 항목: 입찰방법 머리말·확인서 미발급 안내는 기업규모 자격 문장이 아니다(dev DEV-039)
    frag = r'(입\s*찰|계\s*약)\s*(및\s*계\s*약\s*)?방\s*법\s*[:：]|발급\s*받지\s*못한|발급\s*되지\s*않은\s*경우'
    s = rep(s, 'SME_LINE_EXCLUDE_RE = re.compile(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰")',
            'SME_LINE_EXCLUDE_RE = re.compile(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰")\n'
            '# 09-24: 참가자격 문장이 아닌 기업규모 조각 — 입찰방법 머리말, 확인서 미발급 안내(dev DEV-039: 자격 문장 없이 머리말만 남은 공고가 v18=1)\n'
            f'SME_FRAGMENT_RE = re.compile(r"{frag}")')
    s = rep(s, '''    if not line or SME_LINE_EXCLUDE_RE.search(line):
        return None''', '''    if not line or SME_LINE_EXCLUDE_RE.search(line) or SME_FRAGMENT_RE.search(line):
        return None''')
    s = rep(s, '''        if re.search(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰", s):
            continue''', '''        if re.search(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰", s):
            continue
        if SME_FRAGMENT_RE.search(s):
            continue''')
    return s


def M1(s):  # 기업규모 자격 표지 보강: '소지하여야·구비해야·소지 업체', 협동조합 낱말만으로 줄 전체를 버리지 않음
    s = rep(s, '''        if re.search(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰", s):
            continue''', '''        # 09-24: '…중소기업 협동조합으로서 …확인서를 소지한 자'처럼 자격 목록에 협동조합이 함께 적힌 줄은 버리지 않는다.
        if re.search(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|경쟁제품|유찰", s) \\
                or (re.search(r"협동조합", s) and not re.search(r"소지한|보유한|소지하여야|자격을\\s*구비", s)):
            continue''')
    s = rep(s, '''        if not listed and not re.search(r"한함|한정|제한|소지한|보유(하고|한)|갖춘|등록(한|된)|자이어야|업체이어야"''',
               '''        if not listed and not re.search(r"한함|한정|제한|소지한|보유(하고|한)|갖춘|등록(한|된)|자이어야|업체이어야"
                                        r"|소지\\s*(하여야|해야|업체|자)|소지업체|구비\\s*(해야|하여야|한)|자격을\\s*구비"''')
    return s

def G1(s):  # v1: 대학·산학협력단·연구기관'만' 입찰 참여 가능 — 정규식 보조 탐지(LLM과 OR)
    s = rep(s, '''        "특정기관_한정": False,
        "특정기관_근거": None,''', '''        "특정기관_한정": bool(inst_only),
        "특정기관_근거": inst_only[0] if inst_only else None,''')
    s = rep(s, '''    share_line = next((s for s in _lines(rec, r"지분") if re.search(r"\\d\\s*%", s)), "")''',
               '''    share_line = next((s for s in _lines(rec, r"지분") if re.search(r"\\d\\s*%", s)), "")
    # 09-24: '대학 또는 산학협력단만 참여 가능', '4년제 대학교만 참여 가능', '[기관(대학)]만 입찰 참여 가능'(dev DEV-01·035·049).
    # 입찰 참여의 주어가 대학·산학협력단·연구기관일 때만 본다(무라벨 20,000: 인원·연구원·낙찰자·제출 문장은 제외).
    inst_only = [s for s in _lines(rec, r"만\\s*(입찰\\s*)?(에\\s*)?(참여|참가|응찰)\\s*(가능|할\\s*수)")
                 if INSTITUTION_ONLY_RE.search(s) and not re.search(r"인원|연구원\\s*만|학생|근무\\s*시간|낙찰자|실적|제출", s)]''')
    s = rep(s, '''def _lines(rec: Dict[str, Any], pat: str) -> List[str]:''',
               '''INSTITUTION_ONLY_RE = re.compile(r"(대학교?|산학\\s*협력단|연구\\s*기관|\\[기관\\((대학|대학교|연구기관|산학협력단)\\)\\])"
                                 r"(\\s*(또는|및|,)\\s*[^\\n]{0,40})?\\s*만\\s*(입찰\\s*)?(에\\s*)?(참여|참가|응찰)\\s*(가능|할\\s*수)")


def _lines(rec: Dict[str, Any], pat: str) -> List[str]:''')
    s = rep(s, '''ITEM_SOURCE.update({"v1": "llm", "v9": "llm",''', '''ITEM_SOURCE.update({"v1": "or", "v9": "llm",''')
    return s

def E4(s):  # 부재 항목: 확인서 미발급 안내는 자격 문장이 아니다 + 입찰방법 머리말은 다른 기업규모 자격 줄이 전혀 없을 때만 뺀다
    s = rep(s, """SME_LINE_EXCLUDE_RE = re.compile(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰")""",
            """SME_LINE_EXCLUDE_RE = re.compile(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰")
# 09-24: 기업규모 조각. ① 확인서 미발급 안내('…확인서를 발급받지 못한 업체에 한함', '…발급되지 않은 경우')는 자격 문장이 아니다.
# ② 입찰방법 머리말('입 찰 방 법: 제한경쟁(소기업·소상공인)')은 참가자격에 기업규모 문장이 따로 없을 때 제한의 근거가 아니다
#    (dev DEV-039: 머리말·서류 목록·미발급 안내만 남은 공고가 v18=1). 다른 자격 줄이 있으면 머리말도 그대로 쓴다
#    (여러 줄로 나뉜 자격 문장을 파서가 못 읽는 공고에서 머리말이 안전망이다 — 무라벨 20,000 판독).
SME_UNISSUED_RE = re.compile(r"발급\\s*받지\\s*못한|발급\\s*되지\\s*않은\\s*경우")
SME_HEADER_RE = re.compile(r"(입\\s*찰|계\\s*약)\\s*(및\\s*계\\s*약\\s*)?방\\s*법\\s*[:：]")
SME_NONQUAL_RE = re.compile(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|유찰|신청을?\\s*증빙|상생|발급\\s*받지\\s*못한|발급\\s*되지\\s*않은\\s*경우")
_SME_WORD_RE = re.compile(r"소기업|소상공인|중소기업|중기업")


def sme_header_only(rec: Dict[str, Any]) -> bool:
    \"\"\"기업규모 낱말이 입찰방법 머리말·서류 목록·미발급 안내에만 있으면 True.\"\"\"
    for d in rec["docs"]:
        for ln in d["text"].split("\\n"):
            if _SME_WORD_RE.search(ln) and not SME_HEADER_RE.search(ln) and not SME_NONQUAL_RE.search(ln) \\
                    and SME_BODY_WORD_RE.search(CERT_SMALL_RE.sub(" ", CERT_SME_RE.sub(" ", LAW_NAME_RE.sub(" ", ln)))):
                return False
    return True""")
    s = rep(s, """    if not line or SME_LINE_EXCLUDE_RE.search(line):
        return None""", """    if not line or SME_LINE_EXCLUDE_RE.search(line) or SME_UNISSUED_RE.search(line):
        return None""")
    s = rep(s, """        lines = [ln for ln in _verified_lines(sme.get("자격_원문_인용"), src) if "조항호내용" not in ln]""",
               """        header_only = sme_header_only(rec)
        lines = [ln for ln in _verified_lines(sme.get("자격_원문_인용"), src) if "조항호내용" not in ln
                 and not (header_only and SME_HEADER_RE.search(ln))]""")
    s = rep(s, """        if re.search(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰", s):
            continue""", """        if re.search(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰", s):
            continue
        if SME_UNISSUED_RE.search(s) or (header_only and SME_HEADER_RE.search(s)):
            continue""")
    s = rep(s, """    primary: Dict[str, str] = {}
    secondary: Dict[str, str] = {}""", """    header_only = sme_header_only(rec)
    primary: Dict[str, str] = {}
    secondary: Dict[str, str] = {}""")
    return s

F = {"E4": E4, "G1": G1, "M1": M1, "A2": A2, "B2": B2, "C2": C2, "D2": D2, "E1": E1}
for i in range(0, len(KEYS), 2):
    s = F[KEYS[i:i+2]](s)
open(OUT, "w", encoding="utf-8").write(s); print("wrote", OUT, KEYS)
