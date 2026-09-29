"""P2 주입 시험(서버 경로: 주입 전 원문의 int8 출력을 둔 비관적 가정). 막연한 실적 문장 → v2(고시금액 미만), 지역+실적 → v8."""
import json, gzip, re, sys, copy, importlib.util, random
ROOT = '.'
def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
mods = [load(p) for p in sys.argv[1:]]
mod = mods[0]
tbl = mod.load_competitive_table(ROOT + "/open/data")
raw = ROOT + "/runs/cloud_int8_exp/exp/raw/"
def saved(n):
    d = {}
    for l in open(raw + n + ".jsonl", encoding="utf-8"):
        r = json.loads(l); d[r["id"]] = r.get("text", "")
    return d
S = {k: saved(k) for k in ("main", "item", "model", "sme", "region")}
recs = [json.loads(l) for l in gzip.open(ROOT + "/open/exp950.jsonl.gz", "rt", encoding="utf-8")]
recs = [mod.normalize(r) for r in recs if not r["id"].startswith("PPS-DEV") and not r.get("dropped_doc_counts")
        and any(d["type"] == "공고문" for d in r["docs"]) and S["main"].get(r["id"])]
def kw(i, region_text=None):
    return dict(item_text=S["item"].get(i, ""), model_text=S["model"].get(i, ""), sme_text=S["sme"].get(i, ""),
                region_text=S["region"].get(i, "") if region_text is None else region_text)
def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문": continue
        lines = d["text"].split("\n")
        k = next((j for j, l in enumerate(lines) if re.search(r"참가\s*자격", l)), len(lines) // 3)
        lines.insert(k + 1, sent); d["text"] = "\n".join(lines); break
    return r
m = lambda r, k: r["meta"].get(k)
def price(r):
    try: return float(m(r, "입찰추정가격") or m(r, "배정예산금액") or 0)
    except: return 0
priv = lambda r: m(r, "계약방법") == "수의계약"
small_local = lambda r: m(r, "적용계약법") == "지방계약법" and m(r, "낙찰방법") == "소액수의견적"
V2 = ["다. 유사 용역 수행 실적이 있는 업체",
      "라. 행사 대행 실적을 보유한 업체만 참가 가능",
      "- 관련 분야 납품 실적이 있는 업체이어야 합니다.",
      "마. 본 사업과 유사한 사업을 수행한 실적이 있는 업체",
      "○ 동일 분야 교육 운영 실적이 있는 자",
      "바. 실적이 우수하고 건실한 업체로서 부정당업자로 입찰참가자격 제한 중에 있지 아니한 업체",
      "사. 학교급식 납품 실적이 있는 업체",
      "공공기관 납품 실적을 보유한 업체"]
V8 = ["다. 공고일 기준 사업자등록증을 갖춘 경상북도에 소재한 실적이 우수한 업체.",
      "라. 주된 영업소가 경상북도에 소재하고 유사 용역 수행 실적이 있는 업체",
      "마. 경상북도 소재 업체로서 관련 분야 납품 실적을 보유한 업체",
      "- 입찰공고일 현재 본점 소재지가 경상북도인 업체로서 행사 대행 실적이 있는 자"]
rng = random.Random(5)
def run(item, sents, cond):
    pool = [r for r in recs if cond(r)]
    base = [r for r in pool if not mod.decide(r, S["main"][r["id"]], tbl, **kw(r["id"]))[0][item]]
    rng.shuffle(base); base = base[:10]
    res = []
    for mm in mods:
        hit = 0; tot = 0
        for r in base:
            for s in sents:
                rr = inject(r, s); tot += 1
                hit += mm.decide(rr, S["main"][r["id"]], tbl, **kw(r["id"]))[0][item]
        res.append(f"{hit}/{tot}")
    print(item, 'bases', len(base), ' '.join(res))
    # 문장별(마지막 스크립트)
    mm = mods[-1]
    for s in sents:
        h = sum(mm.decide(inject(r, s), S["main"][r["id"]], tbl, **kw(r["id"]))[0][item] for r in base)
        h0 = sum(mods[0].decide(inject(r, s), S["main"][r["id"]], tbl, **kw(r["id"]))[0][item] for r in base)
        print(f"   {h0:2d}→{h:2d}/{len(base)}  {s}")
run("v2", V2, lambda r: not priv(r) and not small_local(r) and 5e6 <= price(r) < 2.3e8)
run("v8", V8, lambda r: not small_local(r) and price(r) >= 5e6 and m(r, "지역제한여부") != "Y")
