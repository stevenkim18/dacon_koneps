"""G2: LLM 기업규모 근거가 본문에 전혀 없으면(줄 단위·공백 무시 대조 모두 실패 — meta 조항호내용을 옮겨 적은 경우) 수준을 버린다.
인용 줄이 본문에 있으면 그 줄들을 이어 붙여 수준을 다시 읽고, 못 읽으면 LLM 수준을 그대로 둔다(여러 줄 자격 문장 보호).
  python runs/r17_20260928/var_ground2.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = '''        elif ev:
            # 근거 문장에 기업규모 단어가 없다(직접생산확인증명서 소지 문장 등, dev DEV-060·063 v11).
            llm = dict(llm, 기업규모_제한="없음")
'''
new = old + '''        else:
            # 09-28 G2: 통째로는 원문에 없는 근거. 줄 단위·공백 무시로 대조해 본문 줄이 하나도 없으면 meta 조항호내용
            # ('[판로지원법 시행령] 중기업,소기업,소상공인 제한', '추정가격 1억원이상 고시금액 미만 물품·용역(중소기업자)')을
            # 옮겨 적은 것이라 수준을 버린다(int8② dev DEV-063 v11 누락 — 본문에서 기업규모 제한을 지운 편집 공고).
            vlines = _verified_lines(raw_ev, full_text(rec))
            if not vlines:
                llm = dict(llm, 기업규모_제한="없음")
            else:
                vlevel = classify_level(_join_lines(vlines))
                if vlevel:
                    llm = dict(llm, 기업규모_제한=vlevel)
'''
assert src.count(old) == 1
open(sys.argv[2], "w", encoding="utf-8").write(src.replace(old, new))
