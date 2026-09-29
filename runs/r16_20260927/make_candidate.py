"""09-28 후보 생성: wrap_r15 script.py → R16(make_r16.py, 제외어 복원·'국가' 오독) → 머리말 갱신.
사용: make_candidate.py SRC.py(submissions/20260928_wrap_r15/script.py) DST.py"""
import subprocess, sys, tempfile, os
here = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
tmp = tempfile.mkdtemp()
r = os.path.join(tmp, "r16.py")
subprocess.run([sys.executable, os.path.join(here, "make_r16.py"), src, r], check=True)
with open(r, encoding="utf-8") as f:
    s = f.read()
old = '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — wrap_r15 변형(09-28 후보: plus_r3 + W 줄바꿈 문장 이어 읽기 + R15).
'''
new = '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — wrap_r16 변형(09-28 후보: wrap_r15 + R16 제외어가 지우던 자격 문장 복원).

R16(09-27 밤): 자연 공고 20,000의 자격 줄을 넓게 모아 규칙이 못 읽는 줄을 필터별로 나눴다(09-23 ⑤가 '아직 재지 않았다'고 적은
제외어 위험). 실적: 괄호·※ 주석을 걷은 본문이 입찰자 자격 절('…실적이 있는/보유한 업체·자')이면 EVAL_CONTEXT_RE의 '인정·
대상으로·합산·건수·실적만'이 있어도 받는다('공공기관을 대상으로 … 실적이 있는 업체', '…실적이 있는 업체(준공 건만 인정)').
지역: 입찰자 소재지 자격 절(REGION_QUAL_RE)이 있는 줄은 첫 40자 '위치·납품·주소·설치' 필터·'확인서' 필터·'본사만' 필터에서
되살리고 그 절 구간만 판정에 쓴다. 지명 약칭(서울·경기·충북 …)은 그 절 안에서만 시·도로 읽는다. 시설 등급('종합평가 적정')은
가산점이 아니고 평가표 점수 줄(': 5점')은 가산 조건이다. v4: '국가종합전자조달시스템'·'국가계약법'·'국가에서 인증받은'의
'국가'는 발주처가 아니다. 자연 줄 주입(설계에 안 쓴 절반 공고의 실제 실적 자격 줄 120개): v2 404 → 448/480.
무라벨 20,000 +74(v2 +24 · v4 +21 · v8 +13 · v7 +9 · v3 +5 · v6 +2) · dev 판정 변화 0 · LLM 입력 960건 차이 0.
생성: runs/r16_20260927/make_r16.py.

이하 wrap_r15 설명(09-28 후보: plus_r3 + W 줄바꿈 문장 이어 읽기 + R15).
'''
assert s.count(old) == 1
s = s.replace(old, new)
with open(dst, "w", encoding="utf-8") as f:
    f.write(s)
print("wrote", dst)
