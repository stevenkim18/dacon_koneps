"""dev 200건에서 '메타 + 원문 정규식 + 법령 금액 기준'만으로 항목별 F1을 측정한다.

모델 없이 라벨이 법 조문을 기계적으로 적용한 결과인지 확인하기 위한 탐침(probe)이다.
정규식은 LLM 추출기를 대신하는 거친 대리물이므로, 여기 점수는 '규칙 구조가 맞는지'의 하한 신호로만 본다.

실행: python3 scripts/rule_probe.py
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "open"
recs = {}
for line in open(ROOT / "dev.jsonl", encoding="utf-8"):
    r = json.loads(line)
    recs[r["id"]] = r
labs = {row["id"]: row for row in csv.DictReader(open(ROOT / "dev_labels.csv", encoding="utf-8"))}
ids = list(recs)

GW = ("서울특별시|부산광역시|대구광역시|인천광역시|광주광역시|대전광역시|울산광역시|세종특별자치시|경기도|"
      "강원특별자치도|강원도|충청북도|충청남도|전북특별자치도|전라북도|전라남도|경상북도|경상남도|제주특별자치도|제주도")
UNIT = {"억": 1e8, "천만": 1e7, "백만": 1e6, "만": 1e4}


def text(r):
    return "\n".join(d["text"] for d in r["docs"])


def price(r):
    return r["meta"]["입찰추정가격"]


def notice_threshold(r):
    # 국가: 고시금액 2.3억. 지방: 지방계약법 시행규칙 제24조 제2호 나목(법 제5조 미적용 지자체 5억) — dev 양성과 일치
    return 5e8 if r["meta"]["적용계약법"] == "지방계약법" else 2.3e8


def region_clauses(r):
    out = []
    for m in re.finditer(r"[^\n]{0,200}(주된\s*영업소|본점\s*소재지|본사|소재지)[^\n]{0,200}", text(r)):
        c = m.group(0)
        if re.search(GW, c) and not re.search(r"관계없|무관|제한\s*없", c):
            out.append(c)
    return out


def has_region(r):
    return bool(region_clauses(r)) or r["meta"]["지역제한여부"] == "Y"


def parse_amounts(s):
    out = []
    for m in re.finditer(r"(\d[\d,\.]*)\s*(억|천만|백만|만)?\s*(\d[\d,]*)?\s*(천만|백만|만)?\s*원", s):
        try:
            v = float(m.group(1).replace(",", "")) * UNIT.get(m.group(2), 1)
            if m.group(3) and m.group(4):
                v += float(m.group(3).replace(",", "")) * UNIT[m.group(4)]
            out.append(v)
        except ValueError:
            pass
    return out


def performance_amounts(r):
    amounts = []
    for m in re.finditer(r"[^\n]*실적[^\n]*", text(r)):
        s = m.group(0)
        if re.search(r"이상|보유|있는", s) and re.search(r"최근|이내|단일", s):
            amounts += parse_amounts(s)
    return amounts


def is_local(r):
    return r["meta"]["적용계약법"] == "지방계약법"


def local_small_quote(r):
    # 항목표 비고 "지방 + 소액수의 가능": 지방계약 소액수의견적은 실적·지역 제한 위반 대상에서 제외
    return is_local(r) and r["meta"]["낙찰방법"] == "소액수의견적"


def eligibility_performance(r):
    """참가자격으로 요구하는 실적 문장만 남긴다(평가표·제출서류의 실적 기재는 제외)."""
    out = []
    for m in re.finditer(r"[^\n]*실적[^\n]*", text(r)):
        s = m.group(0)
        if not (re.search(r"이상|보유|있는", s) and re.search(r"최근|이내|단일|간", s) and parse_amounts(s)):
            continue
        if re.search(r"기재|배점|\d+\s*점|건수|합산|평가|인정|실적만|대상으로|제출\s*-|\|\s*\d", s):
            continue
        if re.search(r"업체|자이어야|자\)|있어야|참가\s*자격|한함|있는 자|보유한 자", s):
            out.append(s)
    return out


def restriction_clauses(r):
    out = []
    for m in re.finditer(r"[^\n]{0,200}(주된\s*영업소|본점\s*소재지|본사|소재)[^\n]{0,200}", text(r)):
        c = m.group(0)
        if re.search(GW, c) or "단위=기초" in c or "기초자치단체" in c:
            out.append(c)
    return out


def min_shares(r):
    pat = r"(최소\s*(참여)?\s*지분(율|비율)?|지분(율|비율)?[^\n]{0,15}최소)[^\n%]{0,25}?(\d+(\.\d+)?)\s*%"
    return [float(m.group(5)) for m in re.finditer(pat, text(r))]


def is_software(r):
    return "소프트웨어" in (r["meta"]["면허업종제한목록"] or "") or bool(re.search(r"소프트웨어사업자", text(r)))


PUBLIC_ISSUER = r"국가|정부|공공기관|지방자치단체|지자체|공기업|대학병원|\[수요기관|기관(이|에서)?\s*발주"

RULES = {
    # 실적: 고시금액 2.3억은 국가·지방 공통, 지방 소액수의 제외
    2: lambda r: bool(eligibility_performance(r)) and price(r) < 2.3e8 and not local_small_quote(r),
    # 실적금액이 사업예산(배정예산금액) 1배 이상
    3: lambda r: any(a >= r["meta"]["배정예산금액"] for s in eligibility_performance(r) for a in parse_amounts(s)),
    # 발주처를 공공기관 등으로 한정(민간 포함 시 제외)
    4: lambda r: any(re.search(PUBLIC_ISSUER, s) and "민간" not in s for s in eligibility_performance(r)),
    5: lambda r: has_region(r) and price(r) >= notice_threshold(r),
    # 시·군·구 단위 제한: 익명화 토큰 단위=기초 또는 [수요기관(기초자치단체)] 내 소재
    6: lambda r: not local_small_quote(r) and price(r) < notice_threshold(r)
    and (any("단위=기초" in c or "기초자치단체" in c for c in restriction_clauses(r))
         or "단위=기초" in (r["meta"]["제한지역코드목록"] or "")),
    7: lambda r: not local_small_quote(r) and price(r) < notice_threshold(r)
    and (any(len(set(re.findall(GW, c))) >= 2 for c in restriction_clauses(r))
         or len(set(re.findall(GW, r["meta"]["제한지역코드목록"] or ""))) >= 2),
    # 지방계약법 시행규칙 제25조 제7항: 실적(1호)과 지역(6호) 중복 제한 금지
    8: lambda r: is_local(r) and not local_small_quote(r) and bool(eligibility_performance(r)) and has_region(r),
    16: lambda r: 1e8 <= price(r) < 2.3e8
    and not re.search(r"중소기업(자)?\s*(확인|인 자|로서|에\s*한|만|제한|\))|중기업|소기업|소상공인", text(r)),
    18: lambda r: price(r) < 1e8 and not re.search(r"소기업|소상공인", text(r)),
    # SW사업인데 대기업·상호출자제한기업 참여제한 문구 없음(1억 미만은 소기업 제한으로 사실상 배제)
    20: lambda r: is_software(r) and price(r) >= 1e8 and not re.search(r"대기업|상호출자제한|중견기업", text(r)),
    # 공동수급 최소지분율: 지방 5%, 국가 10% 미만이면 위반
    21: lambda r: any(x < (5 if is_local(r) else 10) for x in min_shares(r)),
    22: lambda r: r["meta"]["낙찰방법"] == "협상에의한계약"
    and re.search(r"설명회[^\n]{0,80}(참석[^\n]{0,30}(한하|만|자격|허용되지|제외|접수하지|불가)|미참석|불참|참석하지 아니한|참석한 자)", text(r)),
}


def score(k, fn):
    tp = fp = fn_ = 0
    fps, fns = [], []
    for i in ids:
        p, t = bool(fn(recs[i])), labs[i][f"v{k}"] == "1"
        if p and t:
            tp += 1
        elif p:
            fp += 1
            fps.append(i)
        elif t:
            fn_ += 1
            fns.append(i)
    f1 = 2 * tp / (2 * tp + fp + fn_) if tp else 0.0
    print(f"v{k:<2} F1={f1:.3f} tp={tp} fp={fp} fn={fn_}  FP={fps[:8]} FN={fns}")


def v23_gap_report():
    """v23: 지방 협상계약에서 설명회일~제안서 마감일 간격이 추정가격별 기준(10/20/40일) 미만인지 수작업 확인용."""
    need = lambda p: 40 if p >= 1e9 else (20 if p >= 1e8 else 10)
    print("\nv23 기준(지방자치단체 입찰시 낙찰자 결정기준 제7장 제3절 2-다): 설명은 제안서 마감 전일부터 기산해 N일 전")
    for i in ids:
        if labs[i]["v23"] == "1":
            print(f"  {i} 추정가격={price(recs[i]):,} 필요간격={need(price(recs[i]))}일  근거={labs[i]['e23'][:60]!r}")


if __name__ == "__main__":
    for k, fn in RULES.items():
        score(k, fn)
    v23_gap_report()
