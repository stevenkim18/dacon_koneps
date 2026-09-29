"""09-28 R17 생성기: wrap_r16 판정기 위에 아래 변경을 스위치로 얹는다(LLM 호출·프롬프트는 그대로).
  GN  LLM 기업규모 근거가 meta 조항호내용을 옮겨 적은 것이면 수준을 버림 + v11도 수준만 'LLM 없음 → 정규식'(llm_or_level)
  B   입찰방식 요약 줄('제한경쟁(중소기업)', '소기업·소상공인 간 제한경쟁입찰입니다', '경쟁형태 : …')을 '입찰방법:' 머리말과 같이 본다
      — 다른 기업규모 자격 줄이 하나도 없을 때만 제한의 근거에서 뺀다(dev DEV-039: 머리말만 남은 편집 공고 v18=1)
  A   기업규모 제한을 부정하는 줄('…으로 제한하지 않습니다', '제한경쟁을 시행하지 않습니다', '…의 제한이 없습니다', '제한경쟁입찰 비대상')은
      수준의 근거로 쓰지 않고, 그런 줄이 있으면 부재형(v11·v16·v18)은 예외 선언으로 본다
  D   실적 자격 어미 '…실적이 있을 것'·'보유할 것', '※'로 시작하는 자격 줄(주석 걷기가 줄 전체를 지우던 것)
  python runs/r17_20260928/make_r17.py SRC.py DST.py GN,B,A,D"""
import sys

src = open(sys.argv[1], encoding="utf-8").read()
flags = set(sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] else set()


def rep(old, new, count=1):
    global src
    assert src.count(old) == count, (old[:80], src.count(old))
    src = src.replace(old, new)


if "GN" in flags:
    rep('''        elif ev:
            # 근거 문장에 기업규모 단어가 없다(직접생산확인증명서 소지 문장 등, dev DEV-060·063 v11).
            llm = dict(llm, 기업규모_제한="없음")
''', '''        elif ev:
            # 근거 문장에 기업규모 단어가 없다(직접생산확인증명서 소지 문장 등, dev DEV-060·063 v11).
            llm = dict(llm, 기업규모_제한="없음")
        elif _meta_quote(rec, raw_ev):
            # 09-28 R17 GN: 본문에 없는 근거가 meta 조항호내용('[판로지원법 시행령] 중기업,소기업,소상공인 제한',
            # '추정가격 1억원이상 고시금액 미만 물품·용역(중소기업자)')을 옮겨 적은 것이면 본문 기준 라벨과 어긋난다.
            # 편집 공고는 본문 자격 줄만 지우고 meta는 그대로라 int8 본 호출이 meta를 수준 근거로 댄다(int8② dev DEV-063 v11 누락).
            llm = dict(llm, 기업규모_제한="없음")
''')
    rep('''def decide(rec: Dict[str, Any], llm_text: str, table: Dict[str, Dict[str, Any]],''',
        '''def _meta_quote(rec: Dict[str, Any], raw_ev: str) -> bool:
    """LLM 근거가 meta 조항호내용을 (공백 무시) 그대로 옮긴 것인지."""
    q = re.sub(r"\\s+", "", raw_ev or "")
    mv = re.sub(r"\\s+", "", str(meta(rec, "조항호내용") or ""))
    return len(q) >= 6 and bool(mv) and (q in mv or mv in q)


def decide(rec: Dict[str, Any], llm_text: str, table: Dict[str, Dict[str, Any]],''')
    rep('ITEM_SOURCE.update({"v13": "llm_or_level", "v15": "llm_or_level", "v19": "or"})\n',
        'ITEM_SOURCE.update({"v13": "llm_or_level", "v15": "llm_or_level", "v19": "or"})\n'
        '# 09-28 R17 GN: v11도 수준만 LLM∨정규식 — LLM 수준이 비어도(meta 근거를 버린 경우 등) 본문 자격 줄에 기업규모 제한이 있으면\n'
        '# v11(제한 없음)이 아니다. 저장 출력 5벌 판정 변화 0(단독 적용 시).\n'
        'ITEM_SOURCE["v11"] = "llm_or_level"\n')

if "B" in flags:
    rep('''SME_HEADER_RE = re.compile(r"(입\\s*찰|계\\s*약)\\s*(및\\s*계\\s*약\\s*)?방\\s*법\\s*[:：]")
''', '''SME_HEADER_RE = re.compile(r"(입\\s*찰|계\\s*약)\\s*(및\\s*계\\s*약\\s*)?방\\s*법\\s*[:：]")
# 09-28 R17 B: 입찰방식 요약 줄도 머리말이다 — '라. 방 법: 제한경쟁(중소기업․소상공인), 총액입찰', '3. 경쟁형태 : 제한경쟁입찰(중소기업)',
# '나. 총액입찰, 지역제한, 소기업·소상공인간 경쟁입찰입니다', '<제한경쟁입찰 – 소기업·소상공인, 비영리법인 참여가능>'.
# 자격 동사·확인서가 있는 줄은 자격 문장이라 머리말이 아니다. 머리말은 다른 기업규모 자격 줄이 하나도 없을 때만 제한의 근거에서 뺀다
# (삭제 탐침: 자격 문장·확인서 안내를 지우고 요약 줄을 남기면 1억~고시금액 7.6%·1억 미만 2.1%에서 파서가 수준을 다시 읽었다.
#  무라벨 20,000에서 요약 줄뿐인 자연 공고는 제한경쟁·예외 없음 기준 4곳).
SME_METHOD_PAREN_RE = re.compile(r"(제한|경쟁)\\s*(경쟁)?\\s*(입찰)?\\s*[\\(（\\[]\\s*[^()（）\\[\\]\\n]{0,30}?(중\\s*[·ㆍ‧․]?\\s*소기업|소기업|소상공인|중기업)[^()（）\\[\\]\\n]{0,30}[\\)）\\]]")
SME_METHOD_ATTR_RE = re.compile(r"총액|단가|적격\\s*심사|협상|단독|공동\\s*(수급|이행|도급)|전자\\s*입찰|최저가|낙찰\\s*하한|계약\\s*이행\\s*능력|청렴|규격|2\\s*단계|지역\\s*제한|분리")
SME_METHOD_HEAD_RE = re.compile(r"경쟁\\s*형태|^\\W*[가-하0-9]{0,2}\\s*[.)]?\\s*방\\s*법\\s*[:：]|입\\s*찰\\s*방\\s*식|계\\s*약\\s*방\\s*식")
SME_METHOD_NOT_RE = re.compile(r"소지|보유|확인서|자로서|으로서|자이어야|업체이어야|업체여야|참가\\s*자격|자격을|자격이|갖춘|등록한|발급|해당하는\\s*자"
                               r"|따른|(?<!협상에\\s)(?<!협상에)의한|의거|근거|규정에|에\\s*따라")


def sme_method_line(ln: str) -> bool:
    """입찰방식 요약 줄: '입찰방법:' 머리말, 또는 조문 인용·자격 동사 없이 '제한경쟁(…중소기업…)' 괄호나 입찰방식 속성 2개 이상을 나열한 줄."""
    if SME_HEADER_RE.search(ln):
        return True
    if SME_METHOD_NOT_RE.search(ln):
        return False
    return bool(SME_METHOD_PAREN_RE.search(ln) or SME_METHOD_HEAD_RE.search(ln) or len(SME_METHOD_ATTR_RE.findall(ln)) >= 2)
''')
    rep('''            if _SME_WORD_RE.search(ln) and not SME_HEADER_RE.search(ln) and not SME_NONQUAL_RE.search(ln) \\''',
        '''            if _SME_WORD_RE.search(ln) and not sme_method_line(ln) and not SME_NONQUAL_RE.search(ln) \\''')
    rep('''                 and not (header_only and SME_HEADER_RE.search(ln))]''',
        '''                 and not (header_only and sme_method_line(ln))]''')
    rep('''        if SME_UNISSUED_RE.search(s) or (header_only and SME_HEADER_RE.search(s)):''',
        '''        if SME_UNISSUED_RE.search(s) or (header_only and (sme_method_line(s) or sme_method_line(ev_line))):''')

if "A" in flags:
    rep('''SME_UNISSUED_RE = re.compile(r"발급\\s*받지\\s*못한|발급\\s*되지\\s*않은\\s*경우")
''', '''SME_UNISSUED_RE = re.compile(r"발급\\s*받지\\s*못한|발급\\s*되지\\s*않은\\s*경우")
# 09-28 R17 A: 기업규모 제한을 부정하는 줄 — '중소기업자간 제한경쟁으로 제한하지 않습니다', '소기업·소상공인 제한경쟁을 시행하지 않습니다',
# '고시금액 이상 입찰로 소기업, 소상공인, 중소기업자간 제한 입찰 등의 제한이 없습니다', '중소기업자간 제한경쟁입찰 비대상',
# '[소기업 우선 제한경쟁입찰]과 관련 없습니다'. 파서가 이런 줄에서 수준을 읽어 고시금액 이상 공고에 v14를 켰다(무라벨 20,000 약 7곳).
# '지역제한 없음'·'제8조의2에 해당하지 않는 자'는 기업규모 부정이 아니다.
SME_NEG_RE = re.compile(r"(?<!지역)(?<!지역\\s)(?<!공동수급\\s)제한\\s*(을|를)?\\s*(하지|두지|적용하지)\\s*(않|아니)|(?<!지역)(?<!지역\\s)제한하지\\s*(않|아니)"
                        r"|제한\\s*(경쟁|입찰)(입찰)?\\s*(을|를)?\\s*(실시|시행|적용|진행)하지\\s*(않|아니)|제한\\s*(경쟁|입찰)(입찰)?\\s*비\\s*대상"
                        r"|(?<!지역)(?<!지역\\s)제한이\\s*없|입찰\\s*\\]?\\s*과\\s*관련\\s*없")


def sme_negated(rec: Dict[str, Any]) -> bool:
    for d in rec["docs"]:
        for ln in d["text"].split("\\n"):
            if _SME_WORD_RE.search(ln) and SME_NEG_RE.search(ln) and not re.search(r"(않|아니)[^\\n]{0,4}경우", ln):
                return True
    return False
''')
    # 정규식 파서: 부정 줄은 수준 근거가 아니다
    rep('''        if SME_UNISSUED_RE.search(s) or''', '''        if SME_NEG_RE.search(s) or SME_UNISSUED_RE.search(s) or''')
    # 전용 호출 인용 줄
    rep('''    if not line or SME_LINE_EXCLUDE_RE.search(line) or SME_UNISSUED_RE.search(line):''',
        '''    if not line or SME_LINE_EXCLUDE_RE.search(line) or SME_UNISSUED_RE.search(line) or SME_NEG_RE.search(line):''')
    # 본 호출 근거
    rep('''        elif level:
            llm = dict(llm, 기업규모_제한=level)
''', '''        elif level and SME_NEG_RE.search(ev):
            llm = dict(llm, 기업규모_제한="없음")      # 09-28 R17 A: 제한을 부정하는 줄은 수준 근거가 아니다
        elif level:
            llm = dict(llm, 기업규모_제한=level)
''')
    # 판정기: 부정 줄이 있으면 부재형 예외 선언
    rep('''    absence_exception = exception or meta_exception(rec)
''', '''    absence_exception = exception or meta_exception(rec)
    if sme_negated(rec):
        # 09-28 R17 A: '…으로 제한하지 않습니다'는 제한을 두지 않겠다는 선언이다. 근거 조문이 제2조의3이 아니어도(업무처리기준 제5조 등)
        # 부재형(v11·v16·v18)의 위반으로 보지 않는다 — 수준 판단에서 그 줄을 빼면서 생길 수 있는 부재형 새 적중을 막는다.
        exception = absence_exception = True
''')

if "D" in flags:
    rep('''def perf_main_text(s: str) -> str:
    t = s
''', '''def perf_main_text(s: str) -> str:
    # 09-28 R17 D: 줄 머리의 '※'·'*' 표지는 주석 기호일 뿐이다 — 걷기 전에 떼지 않으면 '※.*$'가 자격 문장 전체를 지웠다
    # ('※ 공고일 전일기준 최근5년 이내 단일 건으로 9천만원이상(VAT포함)의 … 행사대행실적(… 인정)이 있는 업체').
    t = re.sub(r"^\\s*[※\\*]+\\s*", "", s)
''')
    rep('''        if re.search(r"업체|자이어야|자\\)|있어야|참가\\s*자격|한함|있는 자|보유한 자|한\\s*자\\b|단체|인\\s*자\\b", s) or new_noun or r15_end:''',
        '''        # 09-28 R17 D: '…수행실적이 있을 것', '…실적을 보유할 것'도 자격 어미다(자연 줄 탐침 N3 v3 누락)
        r17_end = bool(re.search(r"(실적|경험|이력)[^\\n]{0,30}?(있을|보유할|갖출)\\s*것", s)) and not re.search(r"책임자|PM\\b|인력|경력|기술자|강사|연구원|\\|", s)
        if re.search(r"업체|자이어야|자\\)|있어야|참가\\s*자격|한함|있는 자|보유한 자|한\\s*자\\b|단체|인\\s*자\\b", s) or new_noun or r15_end or r17_end:''')
    rep('''    r"(업체|자(?![가-힣])|자이어야|자로|사업자|법인|기관|단체)|실적이\\s*(\\d+\\s*(건|회)\\s*이상\\s*)?있어야")''',
        '''    r"(업체|자(?![가-힣])|자이어야|자로|사업자|법인|기관|단체)|실적이\\s*(\\d+\\s*(건|회)\\s*이상\\s*)?있어야"
    r"|(실적|경험|이력)[^\\n]{0,30}?(있을|보유할|갖출)\\s*것")''')

open(sys.argv[2], "w", encoding="utf-8").write(src)
print("wrote", sys.argv[2], sorted(flags))
