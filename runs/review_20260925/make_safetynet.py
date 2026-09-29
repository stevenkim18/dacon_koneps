"""v1fix 후보 script.py에 LLM 출처 항목의 정규식 안전망 두 가지를 얹는다. 사용: make_safetynet.py SRC.py DST.py 이름

 S1) v13·v15 기업규모 수준: 본 호출·기업규모 전용 호출이 모두 '없음'일 때만 정규식 수준으로 채운다(`llm_or_level` 모드).
     다른 사실(품목·예외·금액)은 그대로 LLM 값을 쓴다.
 S2) v19 확약서: '확약서' + 입찰·마감·투찰·참가 신청 + 제조·공급·기술지원·A/S 줄을 정규식으로도 읽어 LLM과 OR.
     서약·계약 시·낙찰자 의무·해당 시 제출 등은 뺀다. `확약서_근거`도 사실 병합 키에 넣는다(v1과 같은 근거 병합 문제를 피함).
"""
import sys

src, dst, name = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding="utf-8").read()


def sub(old: str, new: str, tag: str) -> None:
    global s
    assert s.count(old) == 1, f"anchor not unique: {tag} ({s.count(old)})"
    s = s.replace(old, new)


# 머리말: 이름을 바꾸고 이번 변경을 맨 앞에 적는다.
head_end = s.index(" 변형.\n") + len(" 변형.\n")
head_start = s.index("경진대회 — ") + len("경진대회 — ")
s = s[:head_start] + name + s[head_end - len(" 변형.\n"):]
sub(" 변형.\n\n", " 변형.\n\n"
    "09-25 안전망(safetynet): LLM이 판정하는 항목에 정규식 보조를 붙인다. 저장 출력 950건(dev+무라벨 750, int8) 기준\n"
    "  S1) v13·v15 기업규모 수준: 본 호출·전용 호출이 모두 '없음'일 때만 정규식 수준 사용 — 판정 변화 0건.\n"
    "  S2) v19 확약서 정규식 OR(서약·계약 시·낙찰자 의무 제외) — dev 정규식 적중 3건 모두 라벨 1, 무라벨 750 새 적중 2건.\n"
    "  or 모드의 근거 키(특정기관_근거·확약서_근거)는 불리언을 정규식만 참으로 만들었으면 정규식 줄을 쓴다.\n\n", "doc")

# S2 정규식: 사실 추출
sub('''    share_line = next((s for s in _lines(rec, r"지분") if re.search(r"\\d\\s*%", s)), "")''',
    '''    share_line = next((s for s in _lines(rec, r"지분") if re.search(r"\\d\\s*%", s)), "")
    # 09-25 S2: 제조사 물품공급·기술지원 확약서를 입찰·마감 전에 보유·제출하게 하는 줄(v19). 입찰서 서약문('본인은 …')·
    # 계약 시 제출·낙찰자 의무·해당 시 제출은 아니다(dev DEV-196 서약문 = 0, DEV-035·036·037 = 1).
    commit = [s for s in _lines(rec, r"확약서") if V19_BID_RE.search(s) and V19_MAKER_RE.search(s) and not V19_EXCL_RE.search(s)]''',
    "share_line")
sub('''        "확약서_입찰시제출": False,
        "확약서_근거": None,''',
    '''        "확약서_입찰시제출": bool(commit),
        "확약서_근거": commit[0] if commit else None,
        # 정규식 전용 키(LLM 스키마에 없어 병합 후에도 남는다): LLM이 '예'라면서 조건에 안 맞는 줄을 인용해도
        # 정규식이 찾은 줄로 v19 조건을 확인할 수 있게 한다(무라벨 750: LLM 확약 '예'인데 인용이 계약 시·서약서인 공고 18건).
        "확약서_근거_정규식": commit[0] if commit else None,''', "commit facts")
# 판정 줄: LLM 인용 또는 정규식 줄 중 하나가 조건(확약·입찰|마감·제조|공급|기술지원|A/S)을 만족하면 인정
sub('''    commit_ev = str(facts.get("확약서_근거") or "")
    v["v19"] = int(is_goods(rec) and bool(facts.get("확약서_입찰시제출")) and "확약" in commit_ev
                   and bool(re.search(r"입찰|마감", commit_ev)) and bool(re.search(r"제조|공급|기술지원|A/S", commit_ev)))''',
    '''    commit_evs = [str(facts.get("확약서_근거") or ""), str(facts.get("확약서_근거_정규식") or "")]
    v["v19"] = int(is_goods(rec) and bool(facts.get("확약서_입찰시제출")) and any(commit_ev_ok(ev) for ev in commit_evs))''',
    "judge v19")
sub('''def judge(rec: Dict[str, Any], facts: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> Dict[str, int]:''',
    '''def commit_ev_ok(ev: str) -> bool:
    """v19 근거 조건: 확약서를 입찰·마감 시점에 제조·공급·기술지원·A/S 주체로부터 받게 하는 줄."""
    return "확약" in ev and bool(re.search(r"입찰|마감", ev)) and bool(re.search(r"제조|공급|기술지원|A/S", ev))


def judge(rec: Dict[str, Any], facts: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> Dict[str, int]:''',
    "commit_ev_ok def")
# 근거 문구(e19): 판정 조건을 만족하는 줄을 우선 쓴다
sub('''    if item == "v12":''',
    '''    if item == "v19":
        for ev in ((llm or {}).get("확약서_근거"), rx.get("확약서_근거_정규식"), rx.get("확약서_근거")):
            ev = clean_evidence(ev, src) or _evidence_span(ev, src)
            if ev and commit_ev_ok(ev):
                return ev
    if item == "v12":''', "evidence v19")
sub('''def regex_facts(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:''',
    '''V19_BID_RE = re.compile(r"입찰\\s*(서|참가|시|마감|등록)|마감|참가\\s*신청|투찰|참가\\s*전")
V19_MAKER_RE = re.compile(r"제조|공급|기술\\s*지원|A/?S|기술\\s*서비스")
V19_EXCL_RE = re.compile(r"본인은|서약|이의를?\\s*제기|계약\\s*(체결\\s*)?(시|전|후|이후)|계약\\s*체결|낙찰자\\s*(는|로|가)|낙찰\\s*후"
                         r"|납품\\s*(시|전|후)|해당\\s*시|필요\\s*시|요청\\s*시|제출할\\s*수\\s*있|청렴|보증금|이행\\s*각서|지급\\s*확약"
                         r"|근로|노동|고용|불인정|허위")


def regex_facts(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:''', "regex_facts def")

# or 모드의 근거 키: 불리언을 정규식만 참으로 만들었으면 근거도 정규식 줄을 쓴다. LLM이 '아니오'라고 하면서 다른 줄을
# 인용하면 그 인용이 판정 줄의 낱말 검사(v19: 확약·입찰|마감·제조|공급)에 걸려 정규식 적중이 버려졌다(주입 시험 10/50).
sub('''        elif mode in ("or", "llm_then_rx"):
            empty = v in (None, "", [], "없음", "해당없음", "불명")
            out[k] = rx[k] if empty else v''',
    '''        elif mode in ("or", "llm_then_rx"):
            pair = OR_EVIDENCE_OF.get(k)
            if pair and not bool(llm.get(pair)) and bool(rx.get(pair)):
                out[k] = rx[k]              # 불리언을 정규식만 참으로 만들었다 → 근거도 정규식 줄
                continue
            empty = v in (None, "", [], "없음", "해당없음", "불명")
            out[k] = rx[k] if empty else v''', "merge or evidence")
sub('''def merge_facts(llm: Optional[Dict[str, Any]], rx: Dict[str, Any], policy: Dict[str, str]) -> Dict[str, Any]:''',
    '''# or 모드에서 근거 키 → 그 근거가 뒷받침하는 불리언 키
OR_EVIDENCE_OF = {"특정기관_근거": "특정기관_한정", "확약서_근거": "확약서_입찰시제출"}


def merge_facts(llm: Optional[Dict[str, Any]], rx: Dict[str, Any], policy: Dict[str, str]) -> Dict[str, Any]:''',
    "merge def")

# 출처 정책
sub('''ITEM_SOURCE.update({"v1": "or", "v9": "llm", "v11": "llm", "v13": "llm", "v15": "llm", "v19": "llm",
                    "v10": "and", "v23": "or"})''',
    '''ITEM_SOURCE.update({"v1": "or", "v9": "llm", "v11": "llm", "v13": "llm", "v15": "llm", "v19": "llm",
                    "v10": "and", "v23": "or"})
# 09-25 안전망: v13·v15는 수준만 'LLM 없음 → 정규식', v19는 확약서 사실을 LLM∨정규식.
ITEM_SOURCE.update({"v13": "llm_or_level", "v15": "llm_or_level", "v19": "or"})''', "ITEM_SOURCE")
sub('''"설명회_개최일", "제안서_마감일", "공동수급_최소지분율", "특정기관_근거"]''',
    '''"설명회_개최일", "제안서_마감일", "공동수급_최소지분율", "특정기관_근거",
                         "확약서_근거"]''', "FACT_KEYS")
sub('''# ===== 8. 법령 판정기 =====''',
    '''def _mode_policy(mode: str) -> Dict[str, str]:
    """출처 모드별 사실 병합 정책. 'llm_or_level'은 기업규모 수준만 LLM이 '없음'일 때 정규식 수준을 쓰고 나머지는 LLM."""
    if mode == "llm_or_level":
        pol = {k: "llm" for k in FACT_KEYS}
        pol["기업규모_제한"] = "or"
        return pol
    return {k: mode for k in FACT_KEYS}


# ===== 8. 법령 판정기 =====''', "mode policy")
sub('''        by_mode = {mode: judge(rec, merge_facts(llm, rx, {k: mode for k in FACT_KEYS}), table)
                   for mode in set(ITEM_SOURCE.values())}''',
    '''        by_mode = {mode: judge(rec, merge_facts(llm, rx, _mode_policy(mode)), table)
                   for mode in set(ITEM_SOURCE.values())}''', "by_mode")
open(dst, "w", encoding="utf-8").write(s)
print("wrote", dst)
