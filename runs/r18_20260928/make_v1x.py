"""V1X를 후보 스크립트의 regex_facts(inst_extra)에 OR로 넣는다.
  python runs/r18_20260928/make_v1x.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
mod = open(__file__.replace("make_v1x.py", "v1x.py"), encoding="utf-8").read()
body = mod.split("import re\n", 1)[1]
anchor = "def _lines(rec: Dict[str, Any], pat: str, joined: bool = False) -> List[str]:"
add = ('# 09-28 R18 V1X: 특정기관·회원·시설·인력 한정 문장의 넓은 틀. 새 보류 세트 H6(설계 전 작성) 규칙 경로 42/138에서 드러난 구멍 —\n'
       "# '…으로 한정한다', '참가 자격 : 사회적협동조합 또는 사회적기업', '…학회에 기관회원으로 가입되어 있어야', '자체 교육장을 보유한 업체에 한함',\n"
       "# '직원 50명 이상 재직 업체만'. 입찰자가 주어이거나 '…만 참가'·'…에 한함' 틀일 때만 받고, 법정 등록·지정(조달청 등록, 측정대행업,\n"
       "# 수질검사기관)·실적 발주처·서류 목록·해당자 한정 줄은 뺀다(무라벨 20,000 새 적중 판독).\n" + body + "\n\n")
assert src.count(anchor) == 1
src = src.replace(anchor, add + anchor, 1)
old = """    if share_extra:
        extra_min, extra_line = min(share_extra, key=lambda t: t[0])"""
new = """    if _meta_method(rec) not in ("수의계약", "지명경쟁"):     # 사회적기업 수의계약·지명경쟁(법정 근거)은 제외
        inst_extra += [s for s in _lines(rec, r"만|한하여|한함|한한다|한정|제한|이어야|여야|에\\s*한|아닌|가입|자격|대상", joined=True)
                       if v1x_line(s) and s not in inst_extra]
    if share_extra:
        extra_min, extra_line = min(share_extra, key=lambda t: t[0])"""
assert src.count(old) == 1
src = src.replace(old, new, 1)
open(sys.argv[2], "w", encoding="utf-8").write(src)
