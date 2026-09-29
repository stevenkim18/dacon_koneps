import json, gzip, random, re, sys, copy, importlib.util
sys.path.insert(0, sys.argv[2])
from paraphrases import P
spec=importlib.util.spec_from_file_location("cand", sys.argv[1]); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
tbl=mod.load_competitive_table("open/data")
rng=random.Random(3); base=[]
for l in gzip.open("open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=json.loads(l)
    if "협상" in str(r["meta"].get("낙찰방법")) and not r.get("dropped_doc_counts"): base.append(r)
rng.shuffle(base); base=[b for b in base if not mod.decide(b,"",tbl)[0]["v22"]][:8]
def inject(r, sent):
    r=copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"]!="공고문": continue
        lines=d["text"].split("\n"); k=next((i for i,l in enumerate(lines) if re.search(r"참가\s*자격", l)), len(lines)//3)
        lines.insert(k+1, sent); d["text"]="\n".join(lines); break
    return r
for s in P["v22"]+P["v22_more"]:
    print(sum(mod.decide(inject(b,s),"",tbl)[0]["v22"] for b in base),"/",len(base)," | ",s)
