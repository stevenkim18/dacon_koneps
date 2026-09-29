"""09-29 r18 후보: r17_edit_shapes script.py → R18 판정 규칙(A~F) → V1X(v1 넓은 틀) → V9X(모델명 보조 호출) → 머리말.
  python runs/r18_20260928/make_candidate.py SRC.py(submissions/20260929_r17_edit_shapes/script.py) DST.py [FLAGS=A,B,C,D,E,F] [V1X=1] [V9X=1]"""
import subprocess, sys, tempfile, os
here = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
opts = dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a)
tmp = tempfile.mkdtemp()
cur = os.path.join(tmp, "rules.py")
subprocess.run([sys.executable, os.path.join(here, "make_r18rules.py"), src, cur, "FLAGS=" + opts.get("FLAGS", "A,B,C,D,E,F")], check=True)
if opts.get("V1X", "1") == "1":
    nxt = os.path.join(tmp, "v1x.py"); subprocess.run([sys.executable, os.path.join(here, "make_v1x.py"), cur, nxt], check=True); cur = nxt
if opts.get("V9X", "1") == "1":
    nxt = os.path.join(tmp, "v9x.py"); subprocess.run([sys.executable, os.path.join(here, "make_v9x.py"), cur, nxt], check=True); cur = nxt
s = open(cur, encoding="utf-8").read()
old = '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — r17 변형(09-29 후보: wrap_r16 + R17 삭제·수준 편집 탐침에서 찾은 구멍).
'''
new = '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — r18 변형(09-29 후보: r17_edit_shapes + R18 새 보류 세트에서 찾은 구멍).

R18(09-28 오후): 설계에 쓰지 않은 새 문장 세트로 규칙·LLM 경로를 다시 쟀다. 가장 큰 구멍은 v1(특정기관 한정)이었다 — 새로 쓴 문장
세트마다 규칙 경로가 10~30%만 잡았다(H6 42/138 · H7 18/120 · H8 0/120 · H9 12/120).
 V1X 입찰자가 주어이거나 '…만 참가'·'…에 한함'·'…으로 한정한다'·'참가 자격: …기관' 틀인 기관·회원·시설·인력 한정 문장(법정 등록·지정,
     실적 발주처, 서류 목록, 수의계약·지명경쟁 제외). 마지막 보류 세트 H9 12 → 54/120 · 무라벨 20,000 +2.
 V9X v9 모델명 전용 호출은 그대로 두고, 기존 후보 줄에 없던 제조사·상표·모델 번호 줄('AMD Ryzen 9 9950X3D', '후지쯔 fi-8170')만 따로
     같은 프롬프트로 한 번 더 묻는다(기존 호출이 '지정 없음'인 물품 공고만, 기존 판정은 꺼지지 않음). 4bit 새 보류 세트 30 → 36/60 · 이전 탐침 10 → 14/20.
 A   '중 소기업'(가운뎃점 빠진 '중·소기업')을 중소기업으로 읽는다(20,000: v13 −5 · v15 −4 · v17 +3, 전부 확인서 이름).
 B   v13·v15는 LLM 수준과 정규식 수준의 OR(수준 바꾸기 편집에서 LLM이 바뀌지 않은 사본을 인용 — 4bit 탐침 v13 13→16/18 · v15 16→18/19).
 C   v4 '(민간실적 제외)'는 공공 한정이다(+1).  D  실적 '…경험을 보유한 법인', '…완수한 이력이 확인되는 사업자'(v4 +2).
 E   기업규모 '…으로 확인받은 업체'.  F  v19 확약서 시점 '투찰 시·전'(+7).
LLM 호출 5종의 입력은 r17과 같고, v9 보조 호출만 새로 더해진다(무라벨 750 기준 약 5%의 물품 공고). 생성: runs/r18_20260928/make_candidate.py.

이하 r17 설명(09-29 첫 후보: wrap_r16 + R17 삭제·수준 편집 탐침에서 찾은 구멍).
'''
assert s.count(old) == 1
s = s.replace(old, new, 1)
open(dst, "w", encoding="utf-8").write(s)
print("wrote", dst)
