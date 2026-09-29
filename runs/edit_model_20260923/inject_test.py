import json, gzip, random, re, sys, copy, importlib.util, collections, pickle
sys.path.insert(0, sys.argv[2])
from paraphrases import P
spec=importlib.util.spec_from_file_location("cand", sys.argv[1]); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
tbl=mod.load_competitive_table("open/data")
ITEMS=[f"v{i}" for i in range(1,25)]
rng=random.Random(7)
# base pool: natural notices, 완전관측, not 수의계약
base=[]
for l in gzip.open("open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=json.loads(l)
    if r.get("dropped_doc_counts"): continue
    if not any(d["type"]=="공고문" for d in r["docs"]): continue
    base.append(r)
rng.shuffle(base)
base=base[:6000]
PROV=["서울특별시","부산광역시","대구광역시","인천광역시","광주광역시","대전광역시","경기도","충청북도","충청남도","전라남도","경상북도","경상남도"]
def inject(r, sent):
    r=copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"]!="공고문": continue
        lines=d["text"].split("\n")
        k=next((i for i,l in enumerate(lines) if re.search(r"참가\s*자격", l)), None)
        if k is None: k=min(len(lines)-1, len(lines)//3)
        lines.insert(k+1, sent)
        d["text"]="\n".join(lines)
        break
    return r
def price(r):
    try: return float(r["meta"].get("입찰추정가격") or 0)
    except: return 0
cache={}
def base_hits(r):
    if r["id"] not in cache: cache[r["id"]]=mod.decide(r,"",tbl)[0]
    return cache[r["id"]]
def pick(cond, item, n):
    out=[]
    for r in base:
        if len(out)>=n: break
        if cond(r) and not base_hits(r)[item]: out.append(r)
    return out
m=lambda r,k: r["meta"].get(k)
local=lambda r: m(r,"적용계약법")=="지방계약법"
nego=lambda r: "협상" in str(m(r,"낙찰방법"))
priv=lambda r: m(r,"계약방법")=="수의계약"
noregion=lambda r: m(r,"지역제한여부")!="Y"
tests=[
 ("v22", P["v22"], lambda r: nego(r)),
 ("v21", P["v21_local"], lambda r: local(r) and not priv(r)),
 ("v21", P["v21_nat"], lambda r: not local(r) and not priv(r)),
 ("v12", P["v12"], lambda r: not priv(r) and not mod.meta_item_codes(r) and m(r,"업무구분")=="물품(내자)"),
 ("v2", P["v2"], lambda r: not priv(r) and 5e6<=price(r)<2.3e8),
 ("v4", P["v4"], lambda r: not priv(r) and price(r)>=2.3e8),
 ("v5", [s.replace("{P1}",p) for s in P["v_region_prov"] for p in ["경기도"]], lambda r: not priv(r) and noregion(r) and ((not local(r) and price(r)>=2.3e8) or (local(r) and price(r)>=5e8))),
 ("v7", [s.replace("{P1}",a).replace("{P2}",b) for s in P["v_region_two"] for a,b in [("대구광역시","경상북도")]], lambda r: not priv(r) and noregion(r) and 5e6<=price(r)<2.3e8),
 ("v6", [s.replace("{P1}",p) for s in P["v_region_sgg"] for p in ["충청남도"]], lambda r: not priv(r) and noregion(r) and 5e6<=price(r)<2.3e8),
 ("v14", P["v_sme_mid"], lambda r: not priv(r) and price(r)>=2.3e8),
 ("v17", P["v_sme_mid"], lambda r: not priv(r) and 5e6<=price(r)<1e8),
 ("v15", P["v_sme_small"], lambda r: not priv(r) and 1e8<=price(r)<2.3e8),
]
summary=collections.OrderedDict()
for item, sents, cond in tests:
    bases=pick(cond, item, 8)
    for s in sents:
        hit=0; n=0; side=collections.Counter()
        for b in bases:
            r=inject(b, s)
            h=mod.decide(r,"",tbl)[0]
            n+=1; hit+=h[item]
            bh=base_hits(b)
            for v in ITEMS:
                if h[v] and not bh[v] and v!=item: side[v]+=1
        summary.setdefault(item,[]).append((hit,n))
        print(f"{item:4} {hit}/{n}  side={dict(side)}  | {s[:90]}")
print("==== recall on paraphrases (regex path)")
for item,v in summary.items():
    h=sum(a for a,b in v); n=sum(b for a,b in v)
    print(f"{item}: {h}/{n} = {h/n:.2f}   per-sentence full-hit {sum(1 for a,b in v if a==b)}/{len(v)}")
