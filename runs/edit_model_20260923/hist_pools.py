import json, csv, sys, importlib.util, inspect, collections
ITEMS=[f"v{i}" for i in range(1,25)]
def load(p):
    out={}
    try:
        for line in open(p,encoding="utf-8"):
            r=json.loads(line); out[r["id"]]=r["text"]
    except FileNotFoundError: pass
    return out
DEV=dict(main=load("runs/mlx/extract_outputs.jsonl"), item=load("runs/mlx/item_outputs.jsonl"), model=load("runs/mlx/model_outputs.jsonl"), sme=load("runs/mlx/v21_sme_dev.jsonl"), region=load("runs/mlx/v22_region_dev.jsonl"))
NAT={k:{**load(f"runs/mlx/train250_{k}.jsonl"),**load(f"runs/mlx/train500_{k}.jsonl")} for k in ["main","item","model","sme","region"]}
lab={r["id"]:{v:int(r[v]) for v in ITEMS} for r in csv.DictReader(open("open/dev_labels.csv",encoding="utf-8"))}
dev=[json.loads(l) for l in open("open/dev.jsonl",encoding="utf-8")]
nat=[json.loads(l) for f in ["runs/mlx/train_sample250.jsonl","runs/mlx/train_sample500_next.jsonl"] for l in open(f,encoding="utf-8")]
def pool(i):
    n=int(i.split("-")[-1]); return "V" if (1<=n<=80 or 131<=n<=141) else "M"
res={}
for path in sys.argv[1:]:
    spec=importlib.util.spec_from_file_location("m"+str(abs(hash(path))), path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    tbl=mod.load_competitive_table("open/data")
    params=inspect.signature(mod.decide).parameters
    def run(r, O):
        i=r["id"]; kw={}
        for k,pn in [("item","item_text"),("model","model_text"),("sme","sme_text"),("region","region_text")]:
            if pn in params: kw[pn]=O[k].get(i,"")
        return mod.decide(r, O["main"].get(i,""), tbl, **kw)[0]
    st={v:collections.Counter() for v in ITEMS}
    for r in dev:
        h=run(r,DEV); i=r["id"]; pl=pool(i)
        for v in ITEMS:
            p=h[v]; l=lab[i][v]
            if p and l: st[v][pl+"tp"]+=1
            elif p: st[v][pl+"fp"]+=1
            elif l: st[v][pl+"fn"]+=1
    natc=collections.Counter()
    for r in nat:
        h=run(r,NAT); natc.update({v:h[v] for v in ITEMS})
    res[path]={"st":{v:dict(st[v]) for v in ITEMS},"nat":dict(natc)}
    T=collections.Counter()
    for v in ITEMS: T.update(st[v])
    print(path.split("/")[1], dict(T), "nat750 total", sum(natc.values()))
json.dump(res, open(sys.argv[0].replace("hist_pools.py","hist_pools.json"),"w"))
