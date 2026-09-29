"""G: LLM 기업규모 수준은 근거가 본문에 있을 때만 쓴다(int8 본 호출이 meta 조항호내용 '[판로지원법 시행령] 중기업,소기업,소상공인 제한',
'추정가격 1억원이상 고시금액 미만 물품·용역(중소기업자)'을 근거로 옮겨 적으면 지금은 수준이 그대로 남는다 — int8② dev DEV-063 v11 누락).
  python runs/r17_20260928/var_ground.py SRC.py DST.py [narrow]"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
narrow = len(sys.argv) > 3 and sys.argv[3] == "narrow"
old = '''        elif ev:
            # 근거 문장에 기업규모 단어가 없다(직접생산확인증명서 소지 문장 등, dev DEV-060·063 v11).
            llm = dict(llm, 기업규모_제한="없음")
'''
if narrow:
    new = old + '''        elif _meta_quote(rec, raw_ev):
            # 09-28 G: 본문에 없는 근거가 meta 조항호내용을 옮겨 적은 것이면 본문 기준 라벨과 어긋난다(int8② dev DEV-063 v11).
            llm = dict(llm, 기업규모_제한="없음")
'''
else:
    new = old + '''        else:
            # 09-28 G: 근거가 본문에 없으면(줄 단위·공백 무시 대조로도) 수준을 인정하지 않는다. int8 본 호출은 meta 조항호내용
            # ('[판로지원법 시행령] 중기업,소기업,소상공인 제한', '추정가격 1억원이상 고시금액 미만 물품·용역(중소기업자)')을 근거로
            # 옮겨 적는다(int8② dev DEV-063 v11 누락). 인용 줄이 원문에 있으면 그 줄의 수준을 쓴다.
            vlines = _verified_lines(raw_ev, full_text(rec))
            vlevel = next((lv for lv in (classify_level(x) for x in vlines) if lv), None)
            llm = dict(llm, 기업규모_제한=vlevel or "없음")
'''
assert src.count(old) == 1
src = src.replace(old, new)
if narrow:
    anchor = "def decide(rec: Dict[str, Any], llm_text: str, table: Dict[str, Dict[str, Any]],"
    helper = '''def _meta_quote(rec: Dict[str, Any], raw_ev: str) -> bool:
    """LLM 근거가 meta 조항호내용(공백 무시)을 옮긴 것인지."""
    q = re.sub(r"\\s+", "", raw_ev or "")
    mv = re.sub(r"\\s+", "", str(meta(rec, "조항호내용") or ""))
    return bool(q) and bool(mv) and (q in mv or mv in q)


'''
    src = src.replace(anchor, helper + anchor, 1)
open(sys.argv[2], "w", encoding="utf-8").write(src)
