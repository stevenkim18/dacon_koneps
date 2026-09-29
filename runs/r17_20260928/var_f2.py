"""F2: 용역 공고에서 본 호출 코드가 경쟁제품으로 성립하지 않을 때(해당없음·표에 없음·특이사항/금액 조건 불충족) 품목 전용 호출이 고른
경쟁제품 코드가 성립하면 그 코드를 쓴다. mode=all(무조건) | lic(면허업종·공고명·본문에 그 세부품명이 보일 때만)
  python runs/r17_20260928/var_f2.py SRC.py DST.py [all|lic]"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
mode = sys.argv[3] if len(sys.argv) > 3 else "all"
old = '''        code = "해당없음" if veto else (base or "해당없음")
'''
new = '''        code = "해당없음" if veto else (base or "해당없음")
        # 09-28 R17 F2: 본 호출은 경쟁제품 코드를 직생 요구 줄(세부품명·번호)에서 읽는 경우가 많아, 그 줄을 지운 편집 공고에서 코드를 잃는다
        # (MLX 4bit 삭제 탐침 25건 중 11건 · dev DEV-064·075 v10 누락). 품목 전용 호출은 과업 설명만 보므로 그 코드를 쓴다.
        icode = str(item["세부품명번호"])
        if icode in table and not veto:
            _dr = {"직접생산확인_요구": rx.get("직접생산확인_요구")}
            if not is_competitive(dict(_dr, 계약목적물_세부품명번호=code), rec, table) \\
                    and is_competitive(dict(_dr, 계약목적물_세부품명번호=icode), rec, table) and _F2_OK(rec, table, icode):
                code = icode
'''
assert src.count(old) == 1
src = src.replace(old, new)
anchor = "def decide(rec: Dict[str, Any], llm_text: str, table: Dict[str, Dict[str, Any]],"
if mode == "all":
    helper = '''def _F2_OK(rec, table, icode):
    return True


'''
else:
    helper = '''def _F2_OK(rec, table, icode):
    """품목 호출 코드의 세부품명(또는 그 앞 4글자)이 공고명·면허업종·본문 과업 줄에 보일 때만."""
    name = str((table.get(icode) or {}).get("name") or "")
    if not name:
        return False
    keys = {name, name[:4], name.replace("서비스", "")}
    hay = title_of(rec) + " " + str(meta(rec, "면허업종제한목록") or "") + " " + full_text(rec)[:3000]
    return any(k and len(k) >= 3 and k in hay for k in keys)


'''
src = src.replace(anchor, helper + anchor, 1)
open(sys.argv[2], "w", encoding="utf-8").write(src)
