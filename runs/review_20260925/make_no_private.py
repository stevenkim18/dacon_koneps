"""09-27 대비판 생성기: 소액수의(수의계약) v10·v17 규칙 두 개만 뺀다.
09-26 제출이 S25(0.7053)보다 낮으면 '평가셋이 소액수의 공고에 v10·v17을 라벨하지 않았다'로 읽고 이 판을 낸다.
빼는 것: make_v10q.py 1번(수의계약 v10 블록) · make_sent2.py E 블록(수의계약 v17 블록).
남기는 것: 제2조의2 단서 예외(make_sent2.py D) · 직생 자격 문장 인식(make_v10q.py 2번) · 나머지 전부.
사용: make_no_private.py SRC.py DST.py [--v10-only]
  --v10-only: v10 소액수의 규칙만 뺀다(v17 소액수의는 dev DEV-21 — 지방 물품 소액수의견적, 조항호내용 '소기업 소상공인 계약',
              중소기업 수준 자격 — 이 v17=1이라 근거가 있다). 09-26 결과가 S25 이상 +0.008 미만이면 이 판으로 v10을 가른다.
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
v10_only = "--v10-only" in sys.argv[3:]
s = open(src, encoding="utf-8").read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


sub('''    # 판로지원법 제9조①1호·시행령 제10조①②: 경쟁제품을 추정가격 1천만원 이상 소액수의계약(국가 시행령 제26조①5호가목·
    # 지방 시행령 제25조①5호)으로 조달해도 직접생산 여부를 확인해야 한다(항목표 v10 근거 = 판로지원법 제9조).
    # 무라벨 20,000의 수의계약은 전부 소액수의견적이다.
    if private_contract and priced and p >= 10_000_000:
        comp_q = (comp and not competitive_exempt(rec)
                  and note_condition_met(rec, table.get(str(facts.get("계약목적물_세부품명번호") or "")) or {}))
        v["v10"] = int(comp_q and not facts.get("직접생산확인_요구") and not facts.get("직접생산_언급_넓게"))
''', '''    # (09-27 대비판) 소액수의 v10 규칙(판로지원법 제9조①1호)은 09-26 결과에 따라 뺐다.
''')
if not v10_only:
  sub('''    if private_contract and not comp and not exception and priced and "소기업" in str(meta(rec, "조항호내용") or ""):
        v["v17"] = int(p < ONE_HUNDRED_MILLION and level == "중소기업" and not SMALL_PROVISO_RE.search(full_text(rec)))
''', '''    # (09-27 대비판) 소액수의 v17 규칙(소기업·소상공인 수의계약 근거와 중소기업 수준 자격)은 뺐다.
''')

head = '"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — safetynet_vague_perf 변형.\n'
if v10_only:
    sub(head, '"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — vague_perf_no_v10q 변형(09-27 대비판).\n\n'
              "09-26 제출(safetynet_vague_perf) 결과로 v10 소액수의 규칙(판로지원법 제9조①1호)만 가를 때 낸다. v17 소액수의\n"
              "(dev DEV-21 v17=1)와 나머지는 그대로다.\n\n"
              "이하 safetynet_vague_perf 설명.\n\n")
else:
    sub(head, '"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — vague_perf_no_private 변형(09-27 대비판).\n\n'
              "09-26 제출(safetynet_vague_perf)이 S25보다 낮을 때 낸다. 소액수의 v10(판로지원법 제9조①1호)·v17(소기업·소상공인\n"
              "수의계약) 규칙 두 개만 뺐고 나머지(P2 막연한 실적, 안전망, v1fix, v3·v23 재현율, 여러 줄 기업규모 문장,\n"
              "제2조의2 단서 예외, 직생 자격 문장)는 그대로다.\n\n"
              "이하 safetynet_vague_perf 설명.\n\n")

open(dst, "w", encoding="utf-8").write(s)
print("ok", dst)
