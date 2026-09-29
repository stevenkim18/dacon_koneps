"""GL2: 본 호출 LLM의 기업규모 근거가 서류 목록('…확인서 1부', '사본')·가점·평가·신용·하도급·제8조의2·부정당·미발급 안내 줄이거나,
기업규모 자격 줄이 따로 없는 공고의 입찰방식 요약 줄이면 수준을 인정하지 않는다(정규식 파서·전용 호출 S2와 같은 거름).
MLX 4bit 삭제 탐침(v11: 본문 기업규모 자격 줄을 지운 경쟁제품 공고 25건)에서 본 호출이 19건에 수준을 답했고, 근거는 meta·서류 목록·요약 줄이었다.
  python runs/r17_20260928/var_gl2.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = '''        elif level and SME_NEG_RE.search(ev):
            llm = dict(llm, 기업규모_제한="없음")      # 09-28 R17 A: 제한을 부정하는 줄은 수준 근거가 아니다
'''
new = '''        elif SME_LLM_EV_EXCL_RE.search(raw_ev) or SME_UNISSUED_RE.search(raw_ev) or (sme_method_line(raw_ev) and sme_header_only(rec)):
            # 09-28 R17 GL2: 서류 목록·가점·평가·미발급 안내 줄, 자격 줄이 따로 없는 공고의 입찰방식 요약 줄은 제한의 근거가 아니다
            # (정규식 파서·전용 호출과 같은 거름). 본문 자격 줄을 지운 편집 공고에서 본 호출이 이런 줄을 근거로 수준을 답했다.
            llm = dict(llm, 기업규모_제한="없음")
        elif level and SME_NEG_RE.search(ev):
            llm = dict(llm, 기업규모_제한="없음")      # 09-28 R17 A: 제한을 부정하는 줄은 수준 근거가 아니다
'''
assert src.count(old) == 1
src = src.replace(old, new)
anchor = "def _meta_quote(rec: Dict[str, Any], raw_ev: str) -> bool:"
helper = '''SME_LLM_EV_EXCL_RE = re.compile(r"\\d+\\s*부\\b|사본|가점|평가|신용|하도급|제8조의2|부정당")


'''
assert src.count(anchor) == 1
src = src.replace(anchor, helper + anchor)
open(sys.argv[2], "w", encoding="utf-8").write(src)
