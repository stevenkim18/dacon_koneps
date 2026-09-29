"""v10 for small private contracts (소액수의) + qualification-phrased 직생 submission, on top of a base script.

usage: python make_v10q.py BASE.py OUT.py
"""
import sys

inp, out = sys.argv[1], sys.argv[2]
src = open(inp, encoding="utf-8").read()


def sub(old, new, count=1):
    global src
    assert src.count(old) == count, (src.count(old), old[:90])
    src = src.replace(old, new)


# 판로지원법 제9조①1호·시행령 제10조①②: 경쟁제품을 추정가격 1천만원 이상 소액수의계약(국가 시행령 제26조①5호가목·
# 지방 시행령 제25조①5호)으로 조달해도 직접생산 여부를 확인해야 한다. 항목표가 v10 근거로 든 조문이 바로 제9조다.
sub('''    v["v12"] = int(bool(facts.get("직접생산확인_요구")) and not comp)''',
    '''    # 판로지원법 제9조①1호·시행령 제10조①②: 경쟁제품을 추정가격 1천만원 이상 소액수의계약(국가 시행령 제26조①5호가목·
    # 지방 시행령 제25조①5호)으로 조달해도 직접생산 여부를 확인해야 한다(항목표 v10 근거 = 판로지원법 제9조).
    # 무라벨 20,000의 수의계약은 전부 소액수의견적이다.
    if private_contract and priced and p >= 10_000_000:
        comp_q = (comp and not competitive_exempt(rec)
                  and note_condition_met(rec, table.get(str(facts.get("계약목적물_세부품명번호") or "")) or {}))
        v["v10"] = int(comp_q and not facts.get("직접생산확인_요구") and not facts.get("직접생산_언급_넓게"))
    v["v12"] = int(bool(facts.get("직접생산확인_요구")) and not comp)''')

# '…직접생산증명서를 제출할 수 있는 업체'·'…직접생산증명원 제출 가능 업체'처럼 자격 문장으로 쓴 제출 요구는 직생 요구다
# (무라벨 PPS-D-000497 손라벨 0). '제출서류: 직접생산확인증명서' 같은 서류 목록은 아니다(운영 답변: 서류 목록은
# 참가자격으로서의 소지 요구가 아님).
sub('''            if re.search(r"증명서|확인서", window) and re.search(r"소지|보유|발급|확인되지|자격", window):''',
    '''            if re.search(r"증명서|확인서|증명원", window) and re.search(r"소지|보유|발급|확인되지|자격|제출\\s*(이\\s*)?가능(한)?\\s*(업체|자|사업자)|제출할\\s*수\\s*있는", window):''')

open(out, "w", encoding="utf-8").write(src)
print("written", out)
