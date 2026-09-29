"""V24F: LLM이 옮긴 공고서 예산이 원문에 있는지 볼 때 '800백만원', '3억 5천만원', '2억원'처럼 억·천만·백만 단위 표기도 인정한다
(지금은 쉼표 원 단위·천 원·만 원만 봐서 이런 공고는 예산 대조를 건너뛴다 — 편집으로 바꾼 예산을 놓침).
  python runs/r17_20260928/var_v24f.py SRC.py DST.py"""
import sys
src = open(sys.argv[1], encoding="utf-8").read()
old = '''    if a % 10000 == 0 and re.search(r"(?<![\\d,.])%s\\s*만\\s*원" % re.escape(f"{a // 10000:,}"), src):
        return True
    return False
'''
new = '''    if a % 10000 == 0 and re.search(r"(?<![\\d,.])%s\\s*만\\s*원" % re.escape(f"{a // 10000:,}"), src):
        return True
    # 09-28 R17 V24F: 억·천만·백만 단위 표기('800백만원', '3억 5천만원', '금2억원')를 원 단위로 풀어 같은 금액이 있는지 본다
    if a % 1_000_000 == 0 and re.search(r"[억만]\\s*원|백\\s*만\\s*원", src):
        for m in AMOUNT_RE.finditer(src):
            if m.group(2) in ("억", "천만", "백만"):
                try:
                    v = float(m.group(1).replace(",", "")) * UNIT[m.group(2)]
                    if m.group(3) and m.group(4):
                        v += float(m.group(3).replace(",", "")) * UNIT[m.group(4)]
                except ValueError:
                    continue
                if abs(v - a) < 1:
                    return True
    return False
'''
assert src.count(old) == 1
open(sys.argv[2], "w", encoding="utf-8").write(src.replace(old, new))
# 근거 문구: 쉼표 표기로 못 찾으면 억·천만·백만 표기로 같은 금액을 적은 줄을 쓴다
src2 = open(sys.argv[2], encoding="utf-8").read()
old2 = '''    amount = facts.get("공고서_예산금액_원")
    if isinstance(amount, (int, float)) and amount > 1_000_000 and f"{int(amount):,}" in src:
        known = [float(meta(rec, k)) for k in ("배정예산금액", "입찰추정가격") if meta(rec, k) not in (None, "")]
        if known and all(abs(amount - x) > max(1000.0, x * 0.001) for x in known):
            ev = line_with(f"{int(amount):,}")
            if ev:
                return ev
'''
new2 = '''    amount = facts.get("공고서_예산금액_원")
    if isinstance(amount, (int, float)) and amount > 1_000_000 and _amount_in_text(amount, src):
        known = [float(meta(rec, k)) for k in ("배정예산금액", "입찰추정가격") if meta(rec, k) not in (None, "")]
        if known and all(abs(amount - x) > max(1000.0, x * 0.001) for x in known):
            ev = line_with(f"{int(amount):,}")
            if not ev:
                # 09-28 R17 V24F: '800백만원'·'3억 5천만원' 표기 줄
                for d in rec["docs"]:
                    for ln in d["text"].split("\\n"):
                        if _amount_in_text(amount, ln):
                            ev = clean_evidence(ln.strip(), src)
                            if ev:
                                break
                    if ev:
                        break
            if ev:
                return ev
'''
assert src2.count(old2) == 1
open(sys.argv[2], "w", encoding="utf-8").write(src2.replace(old2, new2))
