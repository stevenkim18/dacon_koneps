"""09-29 후보 생성: wrap_r16 script.py → R17(make_r17.py GN,B,A,D) → V1W(var_v1w.py) → V24F(var_v24f.py) → 머리말 갱신.
사용: make_candidate.py SRC.py(submissions/20260928_wrap_r16/script.py) DST.py [FLAGS=GN,B,A,D] [V1W=1] [V24F=1] [V19B=1] [V12P=1] [F3S=1] [V1S=1] [GL2=1]"""
import subprocess, sys, tempfile, os
here = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
opts = dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a)
flags = opts.get("FLAGS", "GN,B,A,D")
tmp = tempfile.mkdtemp()
a = os.path.join(tmp, "r17.py"); b = os.path.join(tmp, "v1w.py"); c = os.path.join(tmp, "v24f.py"); d = os.path.join(tmp, "v19b.py"); e = os.path.join(tmp, "v12p.py"); g = os.path.join(tmp, "gl2.py"); h = os.path.join(tmp, "f3s.py"); k = os.path.join(tmp, "v1s.py")
subprocess.run([sys.executable, os.path.join(here, "make_r17.py"), src, a, flags], check=True)
cur = a
if opts.get("V1W", "1") == "1":
    subprocess.run([sys.executable, os.path.join(here, "var_v1w.py"), cur, b], check=True); cur = b
if opts.get("V24F", "1") == "1":
    subprocess.run([sys.executable, os.path.join(here, "var_v24f.py"), cur, c], check=True); cur = c
if opts.get("V19B", "1") == "1":
    subprocess.run([sys.executable, os.path.join(here, "var_v19b.py"), cur, d], check=True); cur = d
if opts.get("V12P", "1") == "1":
    subprocess.run([sys.executable, os.path.join(here, "var_v12p.py"), cur, e], check=True); cur = e
if opts.get("F3S", "1") == "1":
    subprocess.run([sys.executable, os.path.join(here, "var_f3s.py"), cur, h], check=True); cur = h
if opts.get("V1S", "1") == "1":
    subprocess.run([sys.executable, os.path.join(here, "var_v1s.py"), cur, k], check=True); cur = k
if opts.get("GL2", "1") == "1":
    subprocess.run([sys.executable, os.path.join(here, "var_gl2.py"), cur, g], check=True); cur = g
with open(cur, encoding="utf-8") as f:
    s = f.read()
old = '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — wrap_r16 변형(09-28 후보: wrap_r15 + R16 제외어가 지우던 자격 문장 복원).
'''
new = '''"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — r17 변형(09-29 후보: wrap_r16 + R17 삭제·수준 편집 탐침에서 찾은 구멍).

R17(09-28): 지금까지의 탐침은 위반 문장을 '넣는' 편집만 쟀다. 부재형(v10·v11·v16·v18·v20)은 운영진이 자격 줄을 '지워서' 만들고,
v13·v15·v17은 주 자격 문장의 기업규모 낱말을 '바꿔서' 만든다(dev 정답 공고). 무라벨 공고에 같은 편집을 해서 판정기를 쟀다.
 GN  int8 본 호출은 기업규모 근거로 meta 조항호내용('[판로지원법 시행령] 중기업,소기업,소상공인 제한')을 옮겨 적는다. 본문에서 제한을
     지운 편집 공고에서 이 수준이 남아 v11을 놓쳤다(int8② dev DEV-063). meta를 옮긴 근거는 버리고, v11도 수준만 LLM∨정규식으로 채운다.
 B   입찰방식 요약 줄('제한경쟁(중소기업)', '경쟁형태 : …', 방식 속성 나열)도 '입찰방법:' 머리말과 같이 다른 자격 줄이 없을 때 제한의
     근거에서 뺀다(dev DEV-039). 삭제 탐침 v16 1,740 → 1,855/2,321 · v18 2,548 → 2,614/3,412 · 무라벨 20,000 변화 0.
 A   제한을 부정하는 줄('…으로 제한하지 않습니다', '제한경쟁을 시행하지 않습니다', '…의 제한이 없습니다')은 수준 근거가 아니다(v14 −8).
 D   실적 어미 '…실적이 있을 것', 줄 머리 '※' 자격 줄(v2 +3 · v8 +2).
 V1W 기관 유형으로만 참가를 한정하는 문장('산학협력단에 한정하여 참여', '대학교 부설 연구소만 참여 가능', '…기관이어야 입찰 참가') ·
     v1 보류 문장 규칙 경로 13 → 22/30 · 무라벨 20,000 +1.
 V24F 공고서 예산의 억·천만·백만 단위 표기('800백만원', '3억 5천만원')도 원문 대조에 쓴다(저장 출력 판정 변화 0).
 V19B 확약서 요구 시점 '입찰 전·개찰 시·미제출 시 입찰 제한'(항목표 비고 '입찰 전 발급') · 무라벨 20,000 v19 +7(전부 입찰 단계 요구).
 V12P 직생 요구 어미 뒤 괄호 주석('…발급받은 업체(증명서 제출)', '…발급받은 자(유효기간 내 …)') · 무라벨 20,000 변화 0.
 F3S 용역 공고에서 본 호출 코드가 경쟁제품으로 성립하지 않고 품목 호출 코드는 성립하며 제출 서류가 직생 증명서를 요구하면 품목 호출 코드
     (직생 자격 줄을 지운 편집에서 본 호출이 코드를 잃음 — MLX 4bit 탐침 v10 14 → 17/25 · dev 변화 0 · 750 +1).
 GL2 본 호출 LLM의 기업규모 근거가 서류 목록('…확인서 1부'·'사본')·가점·평가·미발급 안내 줄이거나 자격 줄이 따로 없는 공고의
     입찰방식 요약 줄이면 수준을 인정하지 않는다(정규식 파서·전용 호출과 같은 거름) · MLX 4bit 기업규모 삭제 탐침 v11 12 → 19/25 · 저장 출력 변화 0.
 V1S 인원 규모 요건 '상시 종업원 수 30명 이상인 업체', '상시 종업원 20인 이상을 보유한 업체'(운영 답변: 법령 근거 없는 인력 보유 제한도 v1)
     · H5 66 → 72/108 · 무라벨 20,000 +1('상시 근로자 25명 이상인 업체').
LLM 호출·프롬프트·출력 예산은 wrap_r16과 같다. 생성: runs/r17_20260928/make_candidate.py.

이하 wrap_r16 설명(09-28 후보: wrap_r15 + R16 제외어가 지우던 자격 문장 복원).
'''
assert s.count(old) == 1
s = s.replace(old, new)
with open(dst, "w", encoding="utf-8") as f:
    f.write(s)
print("wrote", dst)
