import json, gzip, random, re, sys, copy, importlib.util, collections
sys.path.insert(0, "runs/edit_model_20260923")
from paraphrases import P
def load(p):
    spec=importlib.util.spec_from_file_location("c"+str(abs(hash(p))), p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
mods=[load(p) for p in sys.argv[1:]]
tbl=mods[0].load_competitive_table("open/data")
rng=random.Random(7); base=[]
for l in gzip.open("open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=json.loads(l)
    if r.get("dropped_doc_counts") or not any(d["type"]=="공고문" for d in r["docs"]): continue
    base.append(r)
rng.shuffle(base); base=base[:6000]
def inject(r, sent):
    r=copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"]!="공고문": continue
        lines=d["text"].split("\n")
        k=next((i for i,l in enumerate(lines) if re.search(r"참가\s*자격", l)), None)
        if k is None: k=min(len(lines)-1, len(lines)//3)
        lines.insert(k+1, sent); d["text"]="\n".join(lines); break
    return r
m=lambda r,k: r["meta"].get(k)
local=lambda r: m(r,"적용계약법")=="지방계약법"; priv=lambda r: m(r,"계약방법")=="수의계약"
for name, sents, cond in [("local",P["v21_local"],lambda r: local(r) and not priv(r)),("nat",P["v21_nat"],lambda r: not local(r) and not priv(r))]:
    bases=[r for r in base if cond(r) and not mods[0].decide(r,"",tbl)[0]["v21"]][:8]
    for s in sents:
        res=[sum(mm.decide(inject(b,s),"",tbl)[0]["v21"] for b in bases) for mm in mods]
        print(name, res, "/", len(bases), "|", s)
