"""09-26 밤 새 표현 주입 탐침(probe_paraphrases.py)이 찾은 규칙 경로 재현율 구멍을 막는 변형 생성기.
기준은 `submissions/20260927_scope_cleanup/script.py`. LLM 호출·프롬프트는 바꾸지 않는다(판정기·정규식만).

  R1  v2·v4·v8 실적 줄: '납품한 경험·납품 이력이 있는', '실적 증명이 가능한 업체', '동일 품목', 줄 끝이 '…있는 기관'·'갖춘 자'·
      '사업자'·'…로 참가를 제한함'·'참여 가능'인 자격 줄을 읽는다.
  R2  v4 공공 발주처: '중앙부처'.
  R3  v21 지분 하한: '퍼센트', '100분의 N', '구성원 각 N% 이상'(대표사 지분과 함께 적은 줄).
  R4  v12 직생 요구: '직접생산 확인을 받은 제조업체에 한함'.
  R5  지역 줄: '…에 사업자등록을 한 업체', '도내 업체(… 소재)'.
  R6  v1 특정기관: '대학(…)에 한하여 입찰에 참가', 협회·학회 회원사 한정, '비영리법인만 참가'.
  R7  v1 시설·인력(좁게): 'N명 이상의 인력·직원을 보유한 업체', '전국 모든 … 센터·지점이 있는 업체'.

사용: make_recall_probe.py SRC.py DST.py [R1,R2,...,DOC]   (기본: 전부 + DOC 머리말)
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
parts = set((sys.argv[3] if len(sys.argv) > 3 else "R1,R2,R3,R4,R5,R6,R7,R8,R9,DOC").split(","))  # R10은 따로 켠다
s = open(src, encoding="utf-8").read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90])
    s = s.replace(old, new)


if "R1" in parts:
    sub('''PERF_SPECIFIC_RE = re.compile(r"최근\\s*\\d+\\s*(년|개월)|\\d+\\s*(년|개월)\\s*(이내|이상|간)|\\d+\\s*건\\s*이상"
                              r"|\\d+\\s*회\\s*이상|다년간|동일\\s*(건|용역|물품)|동종")''',
        '''PERF_SPECIFIC_RE = re.compile(r"최근\\s*\\d+\\s*(년|개월)|\\d+\\s*(년|개월)\\s*(이내|이상|간)|\\d+\\s*건\\s*이상"
                              r"|\\d+\\s*회\\s*이상|다년간|동일\\s*(건|용역|물품|품목)|동종")''')
    sub('''PERF_VAGUE_RE = re.compile(r"[가-힣A-Za-z0-9)\\]][^\\n]{0,60}?실적\\s*(이|을)?\\s*(있는|있어야|보유|갖춘|가진|우수)")''',
        '''PERF_VAGUE_RE = re.compile(r"[가-힣A-Za-z0-9)\\]][^\\n]{0,60}?실적\\s*(이|을)?\\s*(있는|있어야|보유|갖춘|가진|우수|(증명|증빙)이\\s*가능한\\s*(업체|자))")''')
    sub('''    for s in _lines(rec, r"실적|수행\\s*경험|납품\\s*경험"):''',
        '''    # 09-27 R1: '해당 물품을 납품한 경험이 있는 업체', '납품 이력이 있는 업체'(새 표현 주입 탐침 09-26 밤).
    # 새로 받는 줄('…한 경험·이력')이 인력 요건(책임자·PM·재직자·경력)이면 입찰자 실적 요구가 아니다(무라벨 20,000 판독).
    for s in _lines(rec, r"실적|수행\\s*경험|납품\\s*경험|(납품|수행|공급|대행|운영|시공)한\\s*(경험|이력)|(납품|수행|공급)\\s*이력"):
        if not re.search(r"실적|수행\\s*경험|납품\\s*경험", s) and re.search(r"책임자|PM\\b|인력|재직|경력|강사|전문가", s):
            continue''')
    sub('''        if not re.search(r"이상|보유|있는|갖춘", s) and not vague:''',
        '''        if not re.search(r"이상|보유|있는|갖춘|가진", s) and not vague:''')
    sub('''        if re.search(r"업체|자이어야|자\\)|있어야|참가\\s*자격|한함|있는 자|보유한 자|한\\s*자\\b|단체|인\\s*자\\b", s):''',
        '''        # 09-27 R1: 입찰자 명사가 '실적이 있는 기관'·'실적을 보유한 사업자'이거나 '갖춘 자'로 끝나는 자격 줄도 받는다
        # (실적증명 서류 안내 '…발급 자격이 있는 기관에서 발급하는 서류로 제출'은 제외). 기존 명사 목록의 판정은 그대로다.
        new_noun = bool(re.search(r"(실적|경험)[^\\n]{0,15}(있는|보유한|갖춘|가진)\\s*(전문\\s*)?기관|(갖춘|가진)\\s*자"
                                  r"|(있는|보유한|갖춘|가진)\\s*(법인\\s*)?사업자", s)) \\
            and not re.search(r"증명은|증빙은|양식|서류로|발급하는", s)
        if re.search(r"업체|자이어야|자\\)|있어야|참가\\s*자격|한함|있는 자|보유한 자|한\\s*자\\b|단체|인\\s*자\\b", s) or new_noun:''')

if "R2" in parts:
    sub('''                              r"|광역\\s*자치\\s*단체|기초\\s*자치\\s*단체|중앙\\s*행정\\s*기관|관공서|준정부\\s*기관")''',
        '''                              r"|광역\\s*자치\\s*단체|기초\\s*자치\\s*단체|중앙\\s*행정\\s*기관|관공서|준정부\\s*기관|중앙\\s*부처")''')

if "R3" in parts:
    sub('''        r"(최소\\s*(참여)?\\s*지분(율|비율)?|지분(율|비율)?[^\\n]{0,15}최소)[^\\n%]{0,25}?(\\d+(\\.\\d+)?)\\s*%", src)]''',
        '''        r"(최소\\s*(참여)?\\s*지분(율|비율)?|지분(율|비율)?[^\\n]{0,15}최소)[^\\n%]{0,25}?(\\d+(\\.\\d+)?)\\s*(%|퍼센트)", src)]''')
    sub('''                   for m in re.finditer(r"(지분(율|비율)?|참여\\s*비율|출자\\s*비율)[^\\n%]{0,20}?(\\d+(\\.\\d+)?)\\s*%\\s*(이상|으로|로\\s*한)", ln)]''',
        '''                   for m in re.finditer(r"(지분(율|비율)?|참여\\s*비율|출자\\s*비율)[^\\n%]{0,20}?(?:100\\s*분\\s*의\\s*)?(\\d+(\\.\\d+)?)\\s*(?:%|퍼센트)?\\s*(이상|으로|로\\s*한)", ln)
                   if "%" in m.group(0) or "퍼센트" in m.group(0) or re.search(r"100\\s*분\\s*의", m.group(0))]
    # 09-27 R3: '대표사 51% 이상, 구성원 각 3% 이상'처럼 대표사 지분 뒤에 구성원 하한을 적은 줄(앞의 식은 대표사 값을 읽는다)
    share_extra += [(float(m.group(1)), ln) for ln in _lines(rec, r"공동\\s*(수급|도급|이행|계약)|구성원")
                    for m in re.finditer(r"구성원\\s*(?:별\\s*)?(?:은\\s*|의\\s*)?각\\s*(?:최소\\s*)?(?:지분\\s*)?(\\d+(?:\\.\\d+)?)\\s*(?:%|퍼센트)\\s*이상", ln)]''')

if "R4" in parts:
    sub('''                   or (re.search(r"(발급\\s*받은|확인을?\\s*받은|갖춘|제출한)\\s*(업체|자)\\s*(에\\s*한|만|이어야|여야|일\\s*것|로\\s*제한|$|[.)])", s)''',
        '''                   or (re.search(r"(발급\\s*받은|확인을?\\s*받은|갖춘|제출한)\\s*(제조\\s*)?(업체|자)\\s*(에\\s*한|만|이어야|여야|일\\s*것|로\\s*제한|$|[.)])", s)''')

if "R5" in parts:
    sub('''    for s in _lines(rec, r"주된\\s*영업소|본점|소재지|본사|소재한\\s*(업체|자|사업자)|소재하(는|고)\\s*있는|내에\\s*소재"''',
        '''    # 09-27 R5: '경상남도에 사업자등록을 한 업체만', '도내 업체(경상남도 소재)로 제한'(새 표현 주입 탐침 09-26 밤)
    for s in _lines(rec, r"주된\\s*영업소|본점|소재지|본사|소재한\\s*(업체|자|사업자)|소재하(는|고)\\s*있는|내에\\s*소재"
                           r"|에\\s*사업자\\s*등록을?\\s*(한|하고\\s*있는)\\s*(업체|자)|도내\\s*(업체|사업자)"''')

V1_EXTRA = '''
# 09-27 R6·R7: 새 표현 주입 탐침(09-26 밤)에서 규칙 경로가 놓친 v1 편집형 문장. 무라벨 20,000에서 거의 켜지지 않는 좁은 형태만 받는다.
#  R6 '「고등교육법」에 따른 대학(산학협력단 포함)에 한하여 입찰에 참가', '○○협회 회원사로 등록된 업체에 한함', '○○학회 정회원 기관'(자격 머리말),
#     '비영리법인(사단법인 또는 재단법인)만 입찰 참가 가능'(중소기업·소상공인과 함께 적은 판로지원법 예외 안내는 제외)
#  R7 운영 답변(417321·417633): 법령 근거 없는 시설·인력 보유 제한도 v1 — 'N명 이상의 인력·직원을 보유한 업체'(dev DEV-063 '50명 이상의
#     보안인력을 보유한 업체'), '전국 모든 광역단체에 … 센터가 있는 업체'(DEV-046)
V1_INST_LIMIT_RE = re.compile(r"(대학교?|산학\\s*협력단|연구\\s*기관|연구소|\\[기관\\((대학|대학교|연구기관|산학협력단)\\)\\])[^\\n]{0,25}?"
                              r"(에|으로|로)\\s*한하여\\s*(입찰에?\\s*)?(참가|참여|응찰)")
V1_MEMBER_RE = re.compile(r"(협회|학회|연합회|\\[기관\\(협회\\)\\])\\s*(의\\s*)?(정\\s*)?회원(사|기관|업체)?\\s*"
                          r"(로\\s*(등록|가입)(된|한)\\s*(업체|기관|자)\\s*|인\\s*(업체|기관|자)\\s*)?(에\\s*한|만\\s*(입찰\\s*)?(참가|참여))"
                          r"|참가\\s*자격\\s*[:：][^\\n]{0,30}(협회|학회)\\s*(의\\s*)?(정\\s*)?회원")
V1_NPO_ONLY_RE = re.compile(r"(비영리\\s*법인|사단\\s*법인|재단\\s*법인)[^\\n]{0,30}만\\s*(입찰\\s*)?(에\\s*)?(참여|참가)")
V1_STAFF_RE = re.compile(r"\\d+\\s*(명|인)\\s*이상의?\\s*[^\\n]{0,20}(인력|직원|요원|근로자|인원)[^\\n]{0,6}?(을|를)?\\s*(보유|고용)(한|하고\\s*있는)\\s*(업체|자)"
                         r"|(인력|직원|요원|근로자|인원)\\s*\\d+\\s*(명|인)\\s*이상(을|를)?\\s*(보유|고용)(한|하고\\s*있는)\\s*(업체|자)")
V1_NETWORK_RE = re.compile(r"전국[^\\n]{0,20}(모든|각|17개)[^\\n]{0,30}(센터|지사|지점|영업소|서비스망|사업소)[^\\n]{0,15}(있는|운영|보유|갖춘)[^\\n]{0,10}(업체|자)")
V1_EXTRA_EXCL_RE = re.compile(r"중소기업|소상공인|낙찰자|계약\\s*상대자|하도급|평가|배점|가점|\\d+\\s*점|우대")
# 인력 보유 요건은 일반 인원 수만 본다: 자격증·전문인력 요건(법정 등록기준일 수 있다)과 소액수의 견적(운영 답변 DEV-083 비위반)은 제외
V1_STAFF_EXCL_RE = re.compile(r"자격증|자격을|전문\\s*인력|기술자")
'''

if "R6" in parts or "R7" in parts:
    sub('''

def _lines(rec: Dict[str, Any], pat: str) -> List[str]:''', V1_EXTRA + '''

def _lines(rec: Dict[str, Any], pat: str) -> List[str]:''')
    pats = []
    if "R6" in parts:
        pats += ["V1_INST_LIMIT_RE", "V1_MEMBER_RE", "V1_NPO_ONLY_RE"]
    if "R7" in parts:
        pats += ["V1_STAFF_RE", "V1_NETWORK_RE"]
    cond = " or ".join(f"{p}.search(s)" for p in pats if p != "V1_STAFF_RE")
    if "R7" in parts:
        cond += ' or (V1_STAFF_RE.search(s) and not V1_STAFF_EXCL_RE.search(s) and _meta_method(rec) != "수의계약")'
    sub('''    inst_only = [s for s in _lines(rec, r"만\\s*(입찰\\s*)?(에\\s*)?(참여|참가|응찰)\\s*(가능|할\\s*수)")''',
        f'''    inst_extra = [s for s in _lines(rec, r"한하여|한함|회원|법인|이상|전국")
                  if ({cond}) and not V1_EXTRA_EXCL_RE.search(s)]
    inst_only = [s for s in _lines(rec, r"만\\s*(입찰\\s*)?(에\\s*)?(참여|참가|응찰)\\s*(가능|할\\s*수)")''')
    sub('''        "특정기관_한정": bool(inst_only),
        "특정기관_근거": inst_only[0] if inst_only else None,''',
        '''        "특정기관_한정": bool(inst_only or inst_extra),
        "특정기관_근거": (inst_only + inst_extra)[0] if (inst_only or inst_extra) else None,''')

if "R8" in parts:
    # 금액 표기: '80,000천원'(천 원 단위)과 '￦49,000,000'(원화 기호)은 AMOUNT_RE가 읽지 못했다(무라벨 20,000 실적 줄의 천 원 표기 약 50공고).
    # v3(실적 1배수) 금액 비교에만 쓴다. v2 구체성 표지로도 쓰면 '제안사가 직접 수행한 실적이 건당 20,000천원 이상인 용역에 한함' 같은
    # 평가용 실적 인정 기준 줄이 새로 켜진다(무라벨 20,000 판독 3공고).
    sub('''def parse_amounts(s: str) -> List[float]:
''', '''THOUSAND_WON_RE = re.compile(r"(?<![\\d,.])(\\d[\\d,]*)\\s*천\\s*원")
WON_SIGN_RE = re.compile(r"[₩￦]\\s*(\\d[\\d,]*\\d)")


def parse_amounts_ext(s: str) -> List[float]:
    """parse_amounts + 천 원 단위('80,000천원 이상')·원화 기호('￦49,000,000') 표기(09-27 R8, v3 실적 금액용)."""
    out = parse_amounts(s)
    for m in THOUSAND_WON_RE.finditer(s):
        try:
            out.append(float(m.group(1).replace(",", "")) * 1000)
        except ValueError:
            pass
    for m in WON_SIGN_RE.finditer(s):
        try:
            out.append(float(m.group(1).replace(",", "")))
        except ValueError:
            pass
    return out


def parse_amounts(s: str) -> List[float]:
''')
    sub('''    _perf_amounts = [a for s in perf for a in parse_amounts(s)]''',
        '''    _perf_amounts = [a for s in perf for a in parse_amounts_ext(s)]''')

if "R9" in parts:
    # v24 예산 축: LLM이 옮긴 금액을 원문에서 확인할 때 '37,930,000'만 찾았다. 예산을 천 원·만 원 단위로 적은 공고
    # ('예산: 35,000천원', '3,500만원')는 비교 자체를 하지 않았다(무라벨 20,000 예산 줄 천 원 표기 약 690공고).
    sub('''    if isinstance(amount, (int, float)) and amount > 1_000_000 and f"{int(amount):,}" in full_text(rec):''',
        '''    if isinstance(amount, (int, float)) and amount > 1_000_000 and _amount_in_text(amount, full_text(rec)):''')
    sub('''def meta_mismatch(rec: Dict[str, Any], facts: Dict[str, Any]) -> bool:''',
        '''def _amount_in_text(amount: float, src: str) -> bool:
    """LLM이 옮긴 금액이 원문에 있는지: 원 단위 쉼표 표기 또는 (나누어떨어질 때) 천 원·만 원 단위 표기."""
    a = int(amount)
    if f"{a:,}" in src:
        return True
    if a % 1000 == 0 and re.search(r"(?<![\\d,.])%s\\s*천\\s*원" % re.escape(f"{a // 1000:,}"), src):
        return True
    if a % 10000 == 0 and re.search(r"(?<![\\d,.])%s\\s*만\\s*원" % re.escape(f"{a // 10000:,}"), src):
        return True
    return False


def meta_mismatch(rec: Dict[str, Any], facts: Dict[str, Any]) -> bool:''')

if "R10" in parts:
    # v4 '특정실적': 집행기준 제5조④3(특정기관이 발주한 실적만 요구하고 다른 기관·민간 실적을 배제)·2(특정 명칭 실적)와
    # dev DEV-042('중고등학교 학생 대상 … 여행 실적', v4=1 — 지금 누락)·DEV-051('대학병원에 납품한 실적', v4=1).
    # 학교·대학·병원·복지시설·도서관 등 특정 유형 기관 대상 실적만 인정하는 자격 줄을 공공 발주처 한정과 같이 본다.
    sub('''def public_only_issuer(s: str) -> bool:''',
        '''CLIENT_PERF_RE = re.compile(
    r"(초\\s*[·ㆍ,]?\\s*중\\s*[·ㆍ,]?\\s*고등?\\s*학교|중\\s*[·ㆍ,]?\\s*고등?\\s*학교|고등\\s*학교|중\\s*학교|초등\\s*학교|유치원|어린이집|학교"
    r"|전문\\s*대학|대학교?|(대학|종합|상급\\s*종합|3\\s*차)\\s*(병원|의료\\s*기관)|병원|의료\\s*기관|보건소|(사회\\s*)?복지\\s*시설|요양\\s*(원|시설)|도서관)"
    r"[^\\n]{0,40}?(실적|경험|이력)")
CLIENT_PERF_EXCL_RE = re.compile(r"부교수|교원|책임\\s*연구원|연구원|강사|교수|학위|졸업")


def client_specific_perf(s: str) -> bool:
    """09-27 R10: 실적을 학교·대학·병원·복지시설 등 특정 유형 기관 대상으로 한정한 자격 줄(집행기준 제5조④2·3, dev DEV-042).
    발주기관 자리표시('[수요기관(고등학교)]')는 실적 대상이 아니라서 지운다. 민간·기업에도 열린 목록과 인력 요건은 제외."""
    t = re.sub(r"\\[수요기관\\([^)\\]]*\\)[^\\]]*\\]", " ", s)
    t = re.sub(r"(업체|자)\\s*(또는|및|,)\\s*(단체|법인)", r"\\1", t)
    return bool(CLIENT_PERF_RE.search(t)) and "민간" not in t and not PUBLIC_OPEN_RE.search(t) \\
        and not CLIENT_PERF_EXCL_RE.search(t)


def public_only_issuer(s: str) -> bool:''')
    sub('''        "실적_발주처_공공한정": any(public_only_issuer(s) for s in perf),''',
        '''        "실적_발주처_공공한정": any(public_only_issuer(s) or client_specific_perf(s) for s in perf),''')

if "R11" in parts:
    # 2차(보류 세트 H에서 남은 구멍): '교육 프로그램 운영 경험이 있는 업체'('…한' 없이), '계약을 이행 완료한 사실이 있는 업체',
    # '1천만원 이상 납품 실적 보유자'. 제재 조항('검사불합격 통보를 받은 사실')·인력 요건은 제외(무라벨 20,000 판독).
    sub('''    for s in _lines(rec, r"실적|수행\\s*경험|납품\\s*경험|(납품|수행|공급|대행|운영|시공)한\\s*(경험|이력)|(납품|수행|공급)\\s*이력"):''',
        '''    for s in _lines(rec, r"실적|수행\\s*경험|납품\\s*경험|(납품|수행|공급|대행|운영|시공)한\\s*(경험|이력)|(납품|수행|공급)\\s*이력"
                         r"|(운영|공급|대행|시공)\\s*경험이\\s*있는|(이행|수행|납품|공급)\\s*(을\\s*)?(완료)?\\s*한\\s*사실이\\s*있는"):
        if re.search(r"사실이\\s*있는", s) and re.search(r"불합격|제재|부정당|위반|감가|해지|해제", s):
            continue''')
    sub('''        if not re.search(r"실적|수행\\s*경험|납품\\s*경험", s) and re.search(r"책임자|PM\\b|인력|재직|경력|강사|전문가", s):''',
        '''        if not re.search(r"실적|수행\\s*경험|납품\\s*경험", s) and re.search(r"책임자|PM\\b|인력|재직|경력|강사|전문가|전공|학위", s):''')
    sub('''        if not re.search(r"이상|보유|있는|갖춘|가진", s) and not vague:''',
        '''        if not re.search(r"이상|보유|있는|갖춘|가진|사실이\\s*있는", s) and not vague:''')
    sub('''        new_noun = bool(re.search(r"(실적|경험)[^\\n]{0,15}(있는|보유한|갖춘|가진)\\s*(전문\\s*)?기관|(갖춘|가진)\\s*자"''',
        '''        new_noun = bool(re.search(r"(실적|경험)[^\\n]{0,15}(있는|보유한|갖춘|가진)\\s*(전문\\s*)?기관|(갖춘|가진)\\s*자|실적\\s*보유자"''')
    sub('''        if not (vague or parse_amounts(s) or PERF_SPECIFIC_RE.search(s)''',
        '''        # 09-27 R11: '…한 사실이 있는 업체'는 이행을 끝낸 사실 요구라 기간·금액 없이도 구체적이다
        if re.search(r"(이행|수행|납품|공급)\\s*(을\\s*)?(완료)?\\s*한\\s*사실이\\s*있는\\s*(업체|자)", s):
            vague = True
        if not (vague or parse_amounts(s) or PERF_SPECIFIC_RE.search(s)''')

if "R12" in parts:
    # 2차 지역 표현: '충청북도에 주사무소를 둔 업체', '충청북도 소재 법인', '충청북도에 소재하는 사업자에 한함'
    # (공동도급·분담 구성원의 소재지는 입찰자 제한이 아니라 제외 — 무라벨 PPS-D-011499)
    sub('''                           r"|에\\s*사업자\\s*등록을?\\s*(한|하고\\s*있는)\\s*(업체|자)|도내\\s*(업체|사업자)"''',
        '''                           r"|에\\s*사업자\\s*등록을?\\s*(한|하고\\s*있는)\\s*(업체|자)|도내\\s*(업체|사업자)"
                           r"|주\\s*사무소를?\\s*(둔|두고)|소재\\s*법인|소재하는\\s*(업체|사업자|자|법인)"''')
    sub('''        if re.search(r"각서|서약|확약|확\\s*인\\s*서|동의서|법원|재판\\s*관할|면\\s*소재지|보험\\s*대상|대상물|성과품", s):''',
        '''        if re.search(r"각서|서약|확약|확\\s*인\\s*서|동의서|법원|재판\\s*관할|면\\s*소재지|보험\\s*대상|대상물|성과품", s):
            continue
        if re.search(r"소재하는\\s*(업체|사업자|자|법인)", s) and re.search(r"공동\\s*도급|분담|구성원", s):''')

if "R13" in parts:
    # 2차 v1: '전국 주요 도시(7개 이상)에 직영 지점을 두고 있는 업체' — 지점 망 요건(브랜드 소개 문구 '1,200개 이상 지점 운영 중인
    # 전문 브랜드'는 입찰자 요건이 아니라 '…있는·두고 있는 업체·자'로 끝나야 한다)
    sub('''V1_NETWORK_RE = re.compile(r"전국[^\\n]{0,20}(모든|각|17개)[^\\n]{0,30}(센터|지사|지점|영업소|서비스망|사업소)[^\\n]{0,15}(있는|운영|보유|갖춘)[^\\n]{0,10}(업체|자)")''',
        '''V1_NETWORK_RE = re.compile(r"전국[^\\n]{0,20}(모든|각|17개)[^\\n]{0,30}(센터|지사|지점|영업소|서비스망|사업소)[^\\n]{0,15}(있는|운영|보유|갖춘)[^\\n]{0,10}(업체|자)"
                           r"|전국[^\\n]{0,30}\\d+\\s*개\\s*(이상|시\\s*·?\\s*도|도시)[^\\n]{0,25}(센터|지사|지점|영업소|사업소)[^\\n]{0,10}"
                           r"(있는|두고\\s*있는|운영하는|보유한|갖춘)\\s*(업체|자)")''')

if "DOC2" in parts:
    sub('''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — scope_recall 변형(09-27 후보).
''', '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — scope_recall_plus 변형(09-27 후보).

scope_recall 위에 R10~R13을 얹었다. LLM 호출·입력은 같다.
R10 v4 '특정실적': 학교·대학·병원·복지시설·어린이집·도서관 등 특정 유형 기관 대상 실적만 인정하는 자격 줄(집행기준 제5조④2·3,
dev DEV-042 '중고등학교 학생 대상 … 여행 실적' v4=1) · R11 실적 줄 2차 표현('운영 경험이 있는 업체', '이행 완료한 사실이 있는 업체',
'실적 보유자') · R12 지역 2차 표현('주사무소를 둔', '소재 법인', '소재하는 업체') · R13 v1 지점 망('전국 … N개 이상 … 지점을 두고 있는 업체').

이하 scope_recall 설명.
''')

if "DOC3" in parts:
    sub('''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — safetynet_vague_perf 변형.
''', '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — s26_recall_plus 변형(09-28 대체판).

09-26 제출본(safetynet_vague_perf, Public 0.7066) 위에 규칙 경로 재현율 보강 R1~R13만 얹었다(소액수의 v10·v20 규칙은 그대로 둠).
09-27 scope_recall_plus 결과가 소액수의 제거 쪽 손실을 가리킬 때 낸다. LLM 호출·입력은 09-26 제출본과 같다.
R1~R9 = scope_recall 설명, R10~R13 = scope_recall_plus 설명과 같다.

이하 safetynet_vague_perf 설명.
''')

if "DOC" in parts:
    sub('''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — scope_cleanup 변형(09-27 후보).
''', '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — scope_recall 변형(09-27 후보).

scope_cleanup 위에 규칙 경로 재현율 보강 R1~R9를 얹었다(09-26 밤 새 표현 주입 탐침에서 찾은 구멍). LLM 호출·입력은 같다.
R1 실적 줄 표현(납품한 경험·이력, 실적 증명이 가능한 업체, '…있는 기관'·'갖춘 자'·'보유한 사업자') · R2 v4 '중앙부처' ·
R3 v21 '퍼센트'·'100분의 N'·'구성원 각 N% 이상' · R4 v12 '확인을 받은 제조업체' · R5 지역 '…에 사업자등록을 한 업체'·'도내 업체' ·
R6 v1 '대학(…)에 한하여 참가'·협회·학회 회원사 한정·'비영리법인만' · R7 v1 'N명 이상의 인력·직원을 보유한 업체'(수의계약 제외)·
'전국 모든 … 센터가 있는 업체' · R8 v3 실적 금액의 천 원 단위·원화 기호 · R9 v24 예산 금액의 천 원·만 원 단위 표기 확인.

이하 scope_cleanup 설명.
''')

open(dst, "w", encoding="utf-8").write(s)
print("wrote", dst, sorted(parts))
