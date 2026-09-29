import json, gzip, random, re, sys, copy, importlib.util, collections
sys.path.insert(0, sys.argv[2])
from paraphrases import P
spec=importlib.util.spec_from_file_location("cand", sys.argv[1]); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
tbl=mod.load_competitive_table("open/data")
ITEMS=[f"v{i}" for i in range(1,25)]
rng=random.Random(11)
base=[]
for l in gzip.open("open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=json.loads(l)
    if r.get("dropped_doc_counts") or r["meta"].get("계약방법")=="수의계약": continue
    if not any(d["type"]=="공고문" for d in r["docs"]): continue
    base.append(r)
rng.shuffle(base); base=base[:8000]
def inject(r, sent):
    r=copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"]!="공고문": continue
        lines=d["text"].split("\n")
        k=next((i for i,l in enumerate(lines) if re.search(r"참가\s*자격", l)), None)
        if k is None: k=min(len(lines)-1, len(lines)//3)
        lines.insert(k+1, sent); d["text"]="\n".join(lines); break
    return r
def price(r):
    try: return float(r["meta"].get("입찰추정가격") or 0)
    except: return 0
def clean_base(r):
    rx=mod.regex_facts(r,tbl)
    if rx["기업규모_제한"]!="없음": return False
    if rx["우선조달_예외사유_기재"] or mod.meta_exception(r): return False
    facts=mod.merge_facts(None, rx, {})
    if mod.is_competitive(facts, r, tbl): return False
    if re.search(r"소기업|중소기업|소상공인", str(r["meta"].get("조항호내용") or "")): return False  # meta also says no SME restriction
    return True
tests=[("v14",P["v_sme_mid"],lambda r: price(r)>=2.3e8),("v17",P["v_sme_mid"],lambda r: 5e6<=price(r)<1e8),("v15",P["v_sme_small"],lambda r: 1e8<=price(r)<2.3e8)]
for item,sents,cond in tests:
    bases=[r for r in base if cond(r) and clean_base(r)][:10]
    tot=0;n=0
    for s in sents:
        hit=sum(mod.decide(inject(b,s),"",tbl)[0][item] for b in bases)
        lv=[mod.rx_sme_level(inject(b,s))[0] for b in bases]
        tot+=hit; n+=len(bases)
        print(f"{item} {hit}/{len(bases)} levels={collections.Counter(lv)} | {s[:80]}")
    print(f"== {item}: {tot}/{n}")
