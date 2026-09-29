"""LLM 경로 항목을 여러 사실 출처의 OR로 판정하는 변형.
  python runs/r18_20260928/var_or.py SRC.py DST.py 'v13=llm_or_level,rx;v15=llm_or_level,rx' [V9MAIN=1]"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
spec = sys.argv[3] if len(sys.argv) > 3 else ""
opts = dict(a.split("=", 1) for a in sys.argv[4:] if "=" in a)
item_or = {}
for part in [p for p in spec.split(";") if p]:
    k, modes = part.split("=")
    item_or[k] = modes.split(",")
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
assert src.count(old) == 1
src = src.replace(old, new)
anchor = "def _mode_policy(mode: str) -> Dict[str, str]:"
src = src.replace(anchor, "ITEM_OR: Dict[str, List[str]] = %r\n\n\n" % item_or + anchor, 1)
if opts.get("V9MAIN") == "1":
    old9 = """    if model_text:
        llm = apply_model_call(rec, llm, model_text)
"""
    new9 = """    main_model = (llm or {}).get("특정모델_지정"), str((llm or {}).get("특정모델_근거") or "")
    if model_text:
        llm = apply_model_call(rec, llm, model_text)
        if llm is not None and not llm.get("특정모델_지정") and main_model[0]:
            _mev = clean_evidence(main_model[1], full_text(rec))
            if _mev and "동등" not in _mev:
                llm = dict(llm, 특정모델_지정=True, 특정모델_근거=_mev)
"""
    assert src.count(old9) == 1
    src = src.replace(old9, new9)
open(sys.argv[2], "w", encoding="utf-8").write(src)
