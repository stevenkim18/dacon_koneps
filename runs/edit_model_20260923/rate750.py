import json, sys, importlib.util, collections
ITEMS=[f"v{i}" for i in range(1,25)]
spec=importlib.util.spec_from_file_location("cand", sys.argv[1]); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
tbl=mod.load_competitive_table("open/data")
D="runs/cloud_int8_exp/exp/raw"
def load(p):
    out={}
    for line in open(p,encoding="utf-8"):
        r=json.loads(line); out[r["id"]]=r["text"]
    return out
S={k:load(f"{D}/{k}.jsonl") for k in ["main","item","model","sme","region"]}
recs=[json.loads(l) for f in ["runs/mlx/train_sample250.jsonl","runs/mlx/train_sample500_next.jsonl"] for l in open(f,encoding="utf-8")]
cnt=collections.Counter(); npos=0; nrec=0
preds={}
for r in recs:
    i=r["id"]
    h=mod.decide(r,S["main"].get(i,""),tbl,item_text=S["item"].get(i,""),model_text=S["model"].get(i,""),sme_text=S["sme"].get(i,""),region_text=S["region"].get(i,""))[0]
    preds[i]=h
    cnt.update({v:h[v] for v in ITEMS}); nrec+=1; npos+= any(h.values())
print("records",nrec,"notices with >=1 positive",npos, "total positives", sum(cnt.values()))
print(" ".join(f"{v}:{cnt[v]}" for v in ITEMS))
json.dump(preds, open(sys.argv[2],"w"))
