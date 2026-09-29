"""F3S: 용역 공고에서 본 호출 코드가 경쟁제품으로 성립하지 않을 때, 품목 전용 호출이 고른 경쟁제품 코드가 성립하고
제출 서류 목록이 직생 증명서를 요구하면('직접생산확인증명서 1부', '… 사본') 품목 호출 코드를 쓴다.
MLX 4bit 직생 삭제 탐침: 본 호출이 25건 중 11건 코드를 잃고 품목 호출은 23건 유지 → v10 14 → 17/25. dev 3벌 변화 0 · 750 +1.
  python runs/r17_20260928/var_f3s.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = '''        code = "해당없음" if veto else (base or "해당없음")
'''
new = '''        code = "해당없음" if veto else (base or "해당없음")
        # 09-28 R17 F3S: 본 호출은 경쟁제품 코드를 직생 자격 줄(세부품명·번호)에서 읽는 경우가 많아, 그 줄을 지운 편집 공고에서 코드를
        # 잃는다(MLX 4bit 직생 삭제 탐침 25건 중 11건). 품목 호출은 과업 설명만 봐서 코드를 지킨다(23건). 제출 서류 목록이 직생 증명서를
        # 요구하는 공고(발주기관이 경쟁제품으로 다룬 흔적, dev DEV-13)에서만 품목 호출 코드를 쓴다 — 무조건 쓰면 dev int8 새 오탐 21건.
        icode = str(item["세부품명번호"])
        if icode in table and not veto and DIRECT_LIST_RE.search(full_text(rec)):
            _dr = {"직접생산확인_요구": rx.get("직접생산확인_요구")}
            if not is_competitive(dict(_dr, 계약목적물_세부품명번호=code), rec, table) \\
                    and is_competitive(dict(_dr, 계약목적물_세부품명번호=icode), rec, table):
                code = icode
'''
assert src.count(old) == 1
src = src.replace(old, new)
anchor = "def decide(rec: Dict[str, Any], llm_text: str, table: Dict[str, Dict[str, Any]],"
helper = '''DIRECT_LIST_RE = re.compile(r"직접\\s*생산[^\\n]{0,40}(증명서|확인서|증명원)[^\\n]{0,40}(\\d+\\s*부\\b|사본)")


'''
assert src.count(anchor) == 1
src = src.replace(anchor, helper + anchor, 1)
open(sys.argv[2], "w", encoding="utf-8").write(src)
