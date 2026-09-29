"""09-26 후보 위에 '구체성 표지 없는 실적 요구' 인정(P2)을 얹는다.
사용: make_vague.py SRC.py DST.py
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()

anchor = 'PERF_BOILERPLATE_RE = re.compile(r"신용과\\s*실적|신용\\s*및\\s*실적|사고")\n'
assert anchor in s, "anchor1"
add = anchor + r'''# 09-25 P2: 구체성 표지(금액·기간·건수·동종) 없이 '무엇의 실적'만 적은 자격 줄도 실적 요구다
# (dev DEV-048 "…경북에 소재한 실적이 우수한 업체" v8=1을 규칙이 못 읽어 놓쳤다). 실적 앞에 대상 설명이 있어야 한다 —
# 줄 첫머리의 '실적이 있는 자'는 법정 상투문 '신용과 / 실적이 있는 자'의 줄바꿈 조각일 수 있어 받지 않는다.
# 제외: 인력 경력·자격, 협력방안, 대행사(대행여행사) 요건, '…업체에게 제작' 지시, 제품 사용실적, 인력 구성,
# 인건비 적용계수, 조문 인용(무라벨 20,000 새 적중 판독에서 나온 비자격 문맥).
PERF_VAGUE_RE = re.compile(r"[가-힣A-Za-z0-9)\]][^\n]{0,60}?실적\s*(이|을)?\s*(있는|있어야|보유|갖춘|가진|우수)")
PERF_VAGUE_EXCL_RE = re.compile(r"경력|학위|자격증|기술자|책임자|기술인력|참여\s*인력|투입\s*인력|강사|전문가|에게|하도급|협력"
                                r"|대행\s*(여행)?사\s*(는|가|를|의|에)|대행여행사|현지\s*여행사|사용\s*실적|구성하여야|로\s*구성"
                                r"|적용\s*계수|인건비|제\s*\d+\s*조\s*\(")
'''
s = s.replace(anchor, add, 1)

old1 = ('        if not re.search(r"이상|보유|있는|갖춘", s):\n            continue\n'
        '        if EVAL_CONTEXT_RE.search(s) or PERF_BOILERPLATE_RE.search(s):')
assert old1 in s, "anchor2"
new1 = ('        vague = bool(PERF_VAGUE_RE.search(s)) and not PERF_VAGUE_EXCL_RE.search(s)\n'
        '        if not re.search(r"이상|보유|있는|갖춘", s) and not vague:\n            continue\n'
        '        if EVAL_CONTEXT_RE.search(s) or PERF_BOILERPLATE_RE.search(s):')
s = s.replace(old1, new1, 1)

old2 = '        if not (parse_amounts(s) or PERF_SPECIFIC_RE.search(s) or relative_perf_multipliers(s) or (public_only_issuer(s)'
assert old2 in s, "anchor3"
new2 = '        if not (vague or parse_amounts(s) or PERF_SPECIFIC_RE.search(s) or relative_perf_multipliers(s) or (public_only_issuer(s)'
s = s.replace(old2, new2, 1)

head = '"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — private_scope_safetynet 변형.\n'
assert s.count(head) == 1, "anchor4"
new_head = ('"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — safetynet_vague_perf 변형.\n\n'
            "09-25 P2(막연한 실적 요구): 금액·기간·건수·동종 같은 구체성 표지 없이 '무엇의 실적이 있는·보유한 업체',\n"
            "'실적이 우수한 업체'로 쓴 자격 줄도 실적 요구로 읽는다. 집행기준 제5조① 단서(고시금액 미만 제조·용역은 실적으로\n"
            "자격 제한 금지)에 구체성 요건은 없다. dev DEV-048 v8 정탐 +1 · DEV-057 v8 오탐 +1(위반 묶음, 편집 대상이 아닌 줄).\n"
            "무라벨 20,000 v2 +94 · v8 +37 · v4 +1(새 적중 판독: 입찰자 실적 요구 다수, 학교 여행·수련 상투문 '유경험업체로서\n"
            "실적이 우수하고 건실한 업체' 일부). 서버 경로 주입 v2 10/80 → 80/80. LLM 호출·입력은 바뀌지 않는다.\n\n"
            "이하 private_scope_safetynet 설명.\n\n")
s = s.replace(head, new_head, 1)

open(dst, "w", encoding="utf-8").write(s)
print("ok", dst)
