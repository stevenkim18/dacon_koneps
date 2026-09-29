"""R18 판정 규칙 변경(LLM 입력 불변).
  A  classify_level: '중 소기업'(가운뎃점이 빠진 '중·소기업')을 중소기업으로 읽는다('“중 소기업 소상공인 확인서”'를 소기업 확인서로 읽던 것).
  B  v13·v15: 기업규모 수준을 LLM 우선(llm_or_level)과 정규식 수준의 OR로 판정한다 — 수준 바꾸기 편집에서 LLM이 바뀌지 않은 사본을
     인용해 놓치던 것(4bit 탐침 v13 13→16/18, v15 16→18/19).
  C  v4: '(민간실적 제외)'·'민간 실적은 인정하지 않음'처럼 민간을 명시적으로 빼는 줄은 공공 한정이다(민간 낱말이 거부권을 갖지 않는다).
  python runs/r18_20260928/make_r18rules.py SRC.py DST.py [FLAGS=A,B,C]"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
flags = set((dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a).get("FLAGS", "A,B,C")).split(","))
if "A" in flags:
    old = '''    if not sentence:
        return None
    m_but = re.search(r"다만\\s*[,，]?|\\(\\s*단\\s*[,，]", sentence)'''
    new = '''    if not sentence:
        return None
    # 09-28 R18 A: 가운뎃점이 빠진 '중 소기업'은 '중·소기업'이다('“중 소기업 소상공인 확인서 ”를 소지한 업체' — 무라벨 PPS-D-005209).
    sentence = re.sub(r"(?<![가-힣])중\\s+소기업", "중·소기업", sentence)
    m_but = re.search(r"다만\\s*[,，]?|\\(\\s*단\\s*[,，]", sentence)'''
    assert src.count(old) == 1; src = src.replace(old, new)
if "B" in flags:
    old = """        by_mode = {mode: judge(rec, merge_facts(llm, rx, _mode_policy(mode)), table)
                   for mode in set(ITEM_SOURCE.values())}
        hits = {k: by_mode[ITEM_SOURCE[k]][k] for k in ITEMS}
"""
    new = """        by_mode = {mode: judge(rec, merge_facts(llm, rx, _mode_policy(mode)), table)
                   for mode in set(ITEM_SOURCE.values()) | {m for ms in ITEM_OR.values() for m in ms}}
        hits = {k: by_mode[ITEM_SOURCE[k]][k] for k in ITEMS}
        for k, ms in ITEM_OR.items():
            hits[k] = max([hits[k]] + [by_mode[m][k] for m in ms])
"""
    assert src.count(old) == 1; src = src.replace(old, new)
    anchor = "def _mode_policy(mode: str) -> Dict[str, str]:"
    add = '''# 09-28 R18 B: v13·v15는 LLM 수준(llm_or_level)과 정규식 수준(rx) 중 하나라도 위반 수준이면 켠다. 수준 바꾸기 편집(주 자격 문장의
# '중소기업'을 '소기업·소상공인'으로)에서 LLM이 바뀌지 않은 첨부 사본을 인용해 놓쳤다(4bit 탐침 v13 13→16/18 · v15 16→18/19).
# v17은 넣지 않는다(무라벨 750 새 적중 3건이 모두 제한 문장이 아닌 인용 — '운영요령 제44조에 따라 중소기업자와의 우선…').
ITEM_OR: Dict[str, List[str]] = {"v13": ["rx"], "v15": ["rx"]}


'''
    src = src.replace(anchor, add + anchor, 1)
if "C" in flags:
    old = '''def public_only_issuer(s: str) -> bool:
    # '실적이 있는 업체 또는 단체'의 단체·법인은 입찰자 형태이지 발주처가 아니다.
    t = re.sub(r"(업체|자)\\s*(또는|및|,)\\s*(단체|법인)", r"\\1", s)'''
    new = '''PRIVATE_EXCLUDED_RE = re.compile(r"민간\\s*(부문|분야|기업|업체|회사)?\\s*(의\\s*)?(발주\\s*)?(실적|수행\\s*실적)?\\s*(은|는|을)?\\s*"
                                 r"(제외|불인정|인정\\s*(하지|되지|불가)|포함\\s*(하지|되지)\\s*않)")


def public_only_issuer(s: str) -> bool:
    # '실적이 있는 업체 또는 단체'의 단체·법인은 입찰자 형태이지 발주처가 아니다.
    t = re.sub(r"(업체|자)\\s*(또는|및|,)\\s*(단체|법인)", r"\\1", s)
    # 09-28 R18 C: '(민간실적 제외)'·'민간 실적은 인정하지 않음'은 공공 한정을 밝힌 것이다 — 그 구절의 '민간'은 거부권이 없다.
    t = PRIVATE_EXCLUDED_RE.sub(" ", t)'''
    assert src.count(old) == 1; src = src.replace(old, new)
if "D" in flags:
    old = '''                         r"|\\d+\\s*(회|건)\\s*이상[^\\n]{0,15}(수행|납품|공급|운영|완수|이행)한\\s*(업체|자)", joined):'''
    new = '''                         r"|\\d+\\s*(회|건)\\s*이상[^\\n]{0,15}(수행|납품|공급|운영|완수|이행)한\\s*(업체|자)"
                         # 09-28 R18 D: '…위탁운영 경험을 보유한 법인', '…2회 이상 완수한 이력이 확인되는 사업자'(새 보류 세트 H10 누락)
                         r"|(운영|수행|납품|공급|대행|시공)\\s*경험\\s*(을|이)\\s*(보유|갖춘|가진)|(완수|수행|납품|공급|이행)한\\s*이력이\\s*(확인되는|있는)", joined):'''
    assert src.count(old) == 1, "D1"; src = src.replace(old, new)
    old = '''            r"|(있는|보유한|갖춘|가진)\\s*(법인\\s*)?사업자", s)) \\'''
    new = '''            r"|(있는|보유한|갖춘|가진)\\s*(법인\\s*)?사업자|(경험|이력)\\s*(을|이)\\s*(보유한|갖춘|가진|있는)\\s*법인|이력이\\s*확인되는\\s*(사업자|업체|자)", s)) \\'''
    assert src.count(old) == 1, "D2"; src = src.replace(old, new)
if "E" in flags:
    old = '''                                        r"|우선\\s*조달계약\\s*대상|업체일 것|참가\\s*자격|경쟁\\s*\\(|경쟁입찰\\s*\\(", s) \\'''
    new = '''                                        r"|우선\\s*조달계약\\s*대상|업체일 것|참가\\s*자격|경쟁\\s*\\(|경쟁입찰\\s*\\("
                                        r"|(으)?로\\s*확인\\s*(을\\s*)?받은\\s*(업체|자|사업자)", s) \\'''
    assert src.count(old) == 1, "E"; src = src.replace(old, new)
if "F" in flags:
    old = '''    return "확약" in ev and bool(re.search(r"입찰|마감|개찰", ev)) and bool(re.search(r"제조|공급|기술지원|A/S", ev))'''
    new = '''    # 09-28 R18 F: '투찰 전 공급확약서(제조사 직인)를 … 등록해야 함'(정규식 사실은 '투찰'을 시점으로 읽는데 여기서 버렸다)
    return "확약" in ev and bool(re.search(r"입찰|마감|개찰|투찰\\s*(시|전|이전)", ev)) and bool(re.search(r"제조|공급|기술지원|A/S", ev))'''
    assert src.count(old) == 1, "F"; src = src.replace(old, new)
if "G" in flags:
    old = '''                out.append((ln, ln))
                out.append((_join_lines(lines[s:max(k + 1, e) + 1]), ln))
    return out'''
    new = '''                joined = _join_lines(lines[s:max(k + 1, e) + 1])
                # 09-28 R18 G: 문장 가운데·끝 조각 줄('소기업확인서 중 하나를 소지한 업체')이 문장 전체와 다른 수준으로 읽히면 조각은 버린다
                # (dev DEV-065: '…발급된 중기업 / 중소기업확인서, / 소기업확인서 중 하나를 소지한 업체' — 문장 전체는 중소기업 수준).
                if not (classify_level(joined) and classify_level(ln) and classify_level(joined) != classify_level(ln)):
                    out.append((ln, ln))
                out.append((joined, ln))
    return out'''
    assert src.count(old) == 1, "G"; src = src.replace(old, new)
open(sys.argv[2], "w", encoding="utf-8").write(src)
