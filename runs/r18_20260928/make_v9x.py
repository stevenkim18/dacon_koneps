"""V9X 변형: 기존 모델명 호출(v9)은 그대로 두고, 기존 후보 줄에 들지 않은 제조사·상표·모델 번호 줄만 모아 같은 프롬프트로 한 번 더 묻는다.
기존 호출이 '지정 없음'일 때만 두 번째 호출이 '지정'이면 v9 사실을 참으로 바꾼다(기존 판정은 꺼지지 않는다).
서버에서는 두 호출 출력을 한 문자열(MODEL2_SEP로 구분)로 decide()에 넘긴다 — 저장 출력(기존 호출만)으로 재채점하면 기존과 같다.
  python runs/r18_20260928/make_v9x.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
v9 = open(__file__.replace("make_v9x.py", "v9cand.py"), encoding="utf-8").read()
body = v9.split("import re\n", 1)[1].split("\ndef extra_lines")[0].replace("def is_extra(s: str) -> bool:", "def _model_extra_line(s: str) -> bool:")
# 1) 두 번째 호출 후보 줄·메시지
anchor = "def model_schema() -> Dict[str, Any]:"
add = '''# ----- 4-2b. 모델명 보조 호출 (09-28 R18 V9X) -----
# 모델 번호가 두 자리 숫자·대문자 조합이 아닌 표기('AMD Ryzen 9 9950X3D', 'Thermo Fisher iCAP PRO', '아크론브라스 터보젯 1720',
# '후지쯔 fi-8170')는 기존 후보 줄에 들지 않아 전용 호출이 보지 못했다(편집 탐침 20건 중 8건). 기존 후보 줄은 그대로 두고
# (덧붙이면 기존 호출의 답이 바뀐다 — 4bit dev DEV-052 정답이 꺼졌다) 새 표지로 잡힌 줄만 따로 같은 프롬프트로 묻는다.
''' + body + '''
MODEL2_SEP = "\\n\\u241e\\n"


def model2_candidate_lines(rec: Dict[str, Any]) -> List[str]:
    order = {"규격서": 0, "과업지시서": 1, "제안요청서": 2, "공고문": 3}
    base = model_candidate_lines(rec)
    seen = set(base) | {s[:200] for s in base}
    out = []
    for d in sorted(rec["docs"], key=lambda d: order.get(d["type"], 4)):
        for line in d["text"].split("\\n"):
            s = line.strip()
            if len(s) < 4 or s in seen or s[:200] in seen:
                continue
            if _model_extra_line(s):
                seen.add(s[:200])
                out.append(s[:200])
                if len(out) >= MODEL_MAX_LINES:
                    return out
    return out


def needs_model2_call(rec: Dict[str, Any]) -> bool:
    return is_goods(rec) and bool(model2_candidate_lines(rec))


def build_model2_messages(rec: Dict[str, Any]) -> List[Dict[str, str]]:
    lines = model2_candidate_lines(rec)
    body = "\\n".join(f"{n}. {s}" for n, s in enumerate(lines, 1))
    user = f"[물품] {title_of(rec)[:100]}\\n[세부품명] {meta(rec, '세부품명번호목록')}\\n\\n[후보 줄]\\n{body}\\n"
    return [{"role": "system", "content": MODEL_SYSTEM_PROMPT}, {"role": "user", "content": user}]


def apply_model2_call(rec: Dict[str, Any], llm: Optional[Dict[str, Any]], model2_text: str) -> Optional[Dict[str, Any]]:
    """기존 호출(또는 본 호출)이 특정모델 지정을 못 찾았을 때만 보조 호출의 '지정' 답을 쓴다. 줄 번호가 유효해야 한다."""
    if llm is not None and llm.get("특정모델_지정"):
        return llm
    res = parse_facts(model2_text)
    if not res or not res.get("특정모델_지정"):
        return llm
    lines = model2_candidate_lines(rec)
    idx = res.get("줄번호")
    line = lines[idx - 1] if isinstance(idx, int) and 1 <= idx <= len(lines) else ""
    if not line:
        return llm
    return dict(llm or {}, 특정모델_지정=True, 특정모델_근거=line)


'''
assert src.count(anchor) == 1
src = src.replace(anchor, add + anchor, 1)
# 2) decide(): model_text를 기존/보조로 나눈다
old = """    if model_text:
        llm = apply_model_call(rec, llm, model_text)
"""
new = """    model2_text = ""
    if MODEL2_SEP in (model_text or ""):
        model_text, model2_text = model_text.split(MODEL2_SEP, 1)
    if model_text:
        llm = apply_model_call(rec, llm, model_text)
    if model2_text and needs_model2_call(rec):
        llm = apply_model2_call(rec, llm, model2_text)
"""
assert src.count(old) == 1
src = src.replace(old, new, 1)
# 3) run(): 단계 3b 보조 호출 — 기존 호출 뒤, 판정 전에
old3 = """        log(f"모델명 판별 호출 {len(model_idx)}건 · 유효 {sum(1 for t in model_texts.values() if parse_facts(t))}건")
        budget.stage("단계3 모델명 호출", t0)
    else:
        log(f"  ! 모델명 호출 생략(예산 {budget.left():.0f}s)")
"""
new3 = old3 + """
    # 단계 3b(09-28 R18 V9X): 기존 후보 줄에 없던 제조사·상표·모델 번호 줄만 따로 묻는다(기존 호출이 '지정 없음'인 물품 공고만)
    def _model_found(i: int) -> bool:
        res = parse_facts(model_texts.get(i, ""))
        if res is not None and needs_model_call(recs[i]):
            return bool(res.get("특정모델_지정"))
        base = parse_facts(texts.get(i, "")) or {}
        return bool(base.get("특정모델_지정"))
    model2_idx = [i for i, rec in enumerate(recs) if needs_model2_call(rec) and not _model_found(i)]
    if model2_idx and budget.afford(30.0):
        t0 = time.time()
        model2_msgs = [build_model2_messages(recs[i]) for i in model2_idx]
        outs = run_stage(runner, model2_msgs, chunk, budget, model_schema(), "모델명 보조 호출", TOKENS_MODEL)
        for j, o in zip(model2_idx, outs):
            model_texts[j] = model_texts.get(j, "") + MODEL2_SEP + (o or "")
        log(f"모델명 보조 호출 {len(model2_idx)}건 · 유효 {sum(1 for o in outs if parse_facts(o))}건")
        budget.stage("단계3b 모델명 보조 호출", t0)
    else:
        log(f"  ! 모델명 보조 호출 생략({len(model2_idx)}건 · 예산 {budget.left():.0f}s)")
"""
assert src.count(old3) == 1
src = src.replace(old3, new3, 1)
open(sys.argv[2], "w", encoding="utf-8").write(src)
