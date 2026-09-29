"""V9C 변형: model_candidate_lines 뒤에 제조사·상표 낱말/모델 번호 모양 줄을 덧붙인다(기존 줄 순서 유지, 최대 40줄).
  python runs/r18_20260928/make_v9c.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
v9 = open(__file__.replace("make_v9c.py", "v9cand.py"), encoding="utf-8").read()
body = v9.split("import re\n", 1)[1].split("\ndef extra_lines")[0]
old = """def needs_model_call(rec: Dict[str, Any]) -> bool:"""
new_fn = '''# 09-28 R18 V9C: 모델 번호가 두 자리 숫자·대문자 조합이 아닌 표기('AMD Ryzen 9 9950X3D', 'Thermo Fisher iCAP PRO', '아크론브라스 터보젯 1720')는
# 후보 줄에 들지 않아 전용 호출이 보지 못했다(편집 탐침 20건 중 8건). 기존 후보 줄 뒤에 제조사·상표 낱말, 한글 제조사 괄호,
# 형식명·제작사 표지, 숫자-문자 혼합 모델 번호 줄을 덧붙인다(기존 줄의 순서·번호는 그대로).\n''' + body + '''

def _model_candidate_lines_base(rec: Dict[str, Any]) -> List[str]:
'''
anchor = "def model_candidate_lines(rec: Dict[str, Any]) -> List[str]:\n"
assert src.count(anchor) == 1 and src.count(old) == 1
src = src.replace(anchor, new_fn, 1)
wrapper = '''def model_candidate_lines(rec: Dict[str, Any]) -> List[str]:
    out = _model_candidate_lines_base(rec)
    if len(out) >= MODEL_MAX_LINES:
        return out
    order = {"규격서": 0, "과업지시서": 1, "제안요청서": 2, "공고문": 3}
    seen = set(out)
    for d in sorted(rec["docs"], key=lambda d: order.get(d["type"], 4)):
        for line in d["text"].split("\\n"):
            s = line.strip()
            if len(s) < 4 or s[:200] in seen or s in seen:
                continue
            if _model_extra_line(s):
                seen.add(s[:200])
                out.append(s[:200])
                if len(out) >= MODEL_MAX_LINES:
                    return out
    return out


'''
src = src.replace(old, wrapper + old, 1)
src = src.replace("def is_extra(s: str) -> bool:", "def _model_extra_line(s: str) -> bool:", 1)
open(sys.argv[2], "w", encoding="utf-8").write(src)
