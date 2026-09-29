"""F: 본 호출 코드가 경쟁제품 표에 있으나 적용 조건(고시 특이사항·금액 한도)에 안 맞고, 품목 호출 코드는 경쟁제품으로 성립하면
품목 호출 코드를 쓴다(int8 본 호출이 행사·운영 대행 공고를 SW 계열 '운영위탁서비스 8111181101'로 고르는 유형, dev DEV-075 v10 누락).
  python runs/r17_20260928/var_fusion.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = '''        code = "해당없음" if veto else (base or "해당없음")
'''
new = '''        code = "해당없음" if veto else (base or "해당없음")
        # 09-28 F: 두 호출이 모두 경쟁제품 코드를 냈는데 본 호출 코드만 적용 조건(8111 계열 SW 특이사항·금액 한도)에 막히면
        # 품목 호출 코드를 쓴다 — int8 본 호출이 행사·운영 대행을 SW '운영위탁서비스(8111181101)'로 고르는 유형(dev DEV-075 v10).
        icode = str(item["세부품명번호"])
        if code in table and icode in table and icode != code:
            _dr = {"직접생산확인_요구": rx.get("직접생산확인_요구")}
            if not is_competitive(dict(_dr, 계약목적물_세부품명번호=code), rec, table) \\
                    and is_competitive(dict(_dr, 계약목적물_세부품명번호=icode), rec, table):
                code = icode
'''
assert src.count(old) == 1
open(sys.argv[2], "w", encoding="utf-8").write(src.replace(old, new))
