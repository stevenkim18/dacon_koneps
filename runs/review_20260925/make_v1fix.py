"""후보 script.py에 v1 정규식 OR 수정(특정기관_근거를 사실 병합 키에 추가)만 얹는다. 사용: make_v1fix.py SRC.py DST.py 이름"""
import sys
src, dst, name = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding="utf-8").read()
old_doc = '"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — phrase_parser_recall 변형.\n'
new_doc = ('"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — ' + name + ' 변형.\n\n'
           "09-25 검토 수정(v1fix): v1 정규식 보조(ITEM_SOURCE v1='or')가 LLM 출력이 있으면 작동하지 않았다. 'or' 모드는\n"
           "특정기관_한정만 LLM∨정규식으로 합치고 근거는 LLM 값(대개 null)을 써서, 근거 공란 규칙에 걸려 v1=0이 됐다.\n"
           "특정기관_근거를 사실 병합 키(FACT_KEYS)에 넣어 LLM 근거가 비면 정규식 근거를 쓰게 한다. 다른 출처 모드의 항목은\n"
           "이 키를 쓰지 않아 영향이 없다. 저장 출력(int8 dev 200·무라벨 750, 4bit dev) 판정 변화 0, int8 출력이 있는 상태의\n"
           "주입 시험 v1 0/60 → 60/60(대학·산학협력단 문장 5종 × 12건).\n\n"
           "이하 원래 설명.\n\n")
assert s.count(old_doc) == 1, "docstring head"
s = s.replace(old_doc, new_doc)
old = ('FACT_KEYS = BOOL_KEYS + ["계약목적물_세부품명번호", "기업규모_제한", "실적_요구금액_원", "지역_단위", "지역_시도목록",\n'
       '                         "설명회_개최일", "제안서_마감일", "공동수급_최소지분율"]')
new = ('# 09-25: 특정기관_근거도 병합 키다. v1은 \'or\' 모드인데 근거가 LLM 값으로만 들어가면 LLM이 놓친 줄을 정규식이 잡아도\n'
       '# 근거 공란으로 v1=0이 된다(주입 시험: LLM 출력 있음 0/60, 없음 60/60). 이 키를 쓰는 판정 줄은 v1뿐이다.\n'
       'FACT_KEYS = BOOL_KEYS + ["계약목적물_세부품명번호", "기업규모_제한", "실적_요구금액_원", "지역_단위", "지역_시도목록",\n'
       '                         "설명회_개최일", "제안서_마감일", "공동수급_최소지분율", "특정기관_근거"]')
assert s.count(old) == 1, "FACT_KEYS"
s = s.replace(old, new)
open(dst, "w", encoding="utf-8").write(s)
print("wrote", dst)
