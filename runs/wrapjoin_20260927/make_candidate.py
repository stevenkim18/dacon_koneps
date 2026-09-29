"""09-28 후보 생성: plus_r3 script.py → W(make_wrapjoin.py, W-b 포함) → R15(make_r15.py) → 머리말 갱신.
사용: make_candidate.py SRC.py(submissions/20260928_plus_r3/script.py) DST.py"""
import subprocess, sys, tempfile, os
here = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
tmp = tempfile.mkdtemp()
w = os.path.join(tmp, "w.py")
subprocess.run([sys.executable, os.path.join(here, "make_wrapjoin.py"), src, w], check=True)
subprocess.run([sys.executable, os.path.join(here, "make_r15.py"), w, dst], check=True)
with open(dst, encoding="utf-8") as f:
    s = f.read()
old = '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — plus_r3 변형(09-28 후보: 09-27 scope_recall_plus + R14).
'''
new = '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — wrap_r15 변형(09-28 후보: plus_r3 + W 줄바꿈 문장 이어 읽기 + R15).

W(09-27): 한 문장이 원문 줄 넘김으로 두세 줄에 나뉘면 한 줄씩 보는 정규식이 자격 어미를 놓친다. 실적(v2·v3·v4·v8)·특정기관(v1)·
직생(v12)·확약서(v19)·지분(v21) 후보에 '빈 줄 없이 바로 이어지는 줄'을 이은 문장을 덧붙이고(표 칸·서식 문구 제외), 지역은
'영업소·소재지 → 지명 → 소재·둔' 구간만, v22는 원문에서 못 찾을 때만 이은 문장에서 찾는다. 근거는 원문 구간으로 되돌린다.
구조 변형 주입(문장 가운데 줄바꿈): v4 15→100/110 · v5 25→95/110 · v21 35→90/100 · v2 95→155/160 · v1 15→70/120 ·
v6 10→35/40 · v7 10→45/50 · v19 10→21/25 · v22 80→105/110. W-b: 직생 증명서가 환경마크·GR·단체표준과 나란히 '생산 능력
확인 서류'로 나열된 줄은 v12 직생 요구가 아니다(09-27 정리 C와 같은 개념). 생성: runs/wrapjoin_20260927/make_wrapjoin.py.
R15(09-27, 4차 표현): 새 보류 세트 H3에서 놓친 실적 끝맺음('…이상인 자로 제한', '실적…을 보유하여야 합니다', '…이어야 함')·
'실적' 낱말 없는 실적 요구('운영 이력 보유', '납품하여 완료한 업체', 'N회 이상 … 완수한 자')·v12 직생 말투('직접생산확인을
받아야/필한', '확인을 받지 못한 업체는 참가할 수 없음')·지역('두고 있는 법인')·v19 '개찰 전까지'·v1 좁은 형태.
생성: runs/wrapjoin_20260927/make_r15.py. 무라벨 20,000 +86(plus_r3 대비) · LLM 입력 960건 차이 0.

이하 plus_r3 설명(09-28 후보: 09-27 scope_recall_plus + R14).
'''
assert s.count(old) == 1
s = s.replace(old, new)
with open(dst, "w", encoding="utf-8") as f:
    f.write(s)
print("wrote", dst)
