import json, csv, sys, importlib.util, collections
ITEMS=[f"v{i}" for i in range(1,25)]
lab={r["id"]:{v:int(r[v]) for v in ITEMS} for r in csv.DictReader(open("open/dev_labels.csv",encoding="utf-8"))}
dev=[json.loads(l) for l in open("open/dev.jsonl",encoding="utf-8")]
nat=[json.loads(l) for f in ["runs/mlx/train_sample250.jsonl","runs/mlx/train_sample500_next.jsonl"] for l in open(f,encoding="utf-8")]
def pool(i):
    n=int(i.split("-")[-1]); return "V" if (1<=n<=80 or 131<=n<=141) else "M"
def load(p):
    out={}
    for line in open(p,encoding="utf-8"):
        r=json.loads(line); out[r["id"]]=r["text"]
    return out
SETS={"dev_int8":({k:load(f"runs/cloud_int8_20260923/dev/raw/{k}.jsonl") for k in ["main","item","model","sme","region"]},dev),
      "dev_4bit":(dict(main=load("runs/mlx/extract_outputs.jsonl"),item=load("runs/mlx/item_outputs.jsonl"),model=load("runs/mlx/model_outputs.jsonl"),sme=load("runs/mlx/v21_sme_dev.jsonl"),region=load("runs/mlx/v22_region_dev.jsonl")),dev),
      "nat_int8":({k:load(f"runs/cloud_int8_exp/exp/raw/{k}.jsonl") for k in ["main","item","model","sme","region"]},nat)}
for path in sys.argv[1:]:
    spec=importlib.util.spec_from_file_location("m"+str(abs(hash(path))), path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    tbl=mod.load_competitive_table("open/data")
    line=[path.split("/")[-1]]
    for name,(S,recs) in SETS.items():
        c=collections.Counter(); per=collections.Counter()
        for r in recs:
            i=r["id"]
            h=mod.decide(r,S["main"].get(i,""),tbl,item_text=S["item"].get(i,""),model_text=S["model"].get(i,""),sme_text=S["sme"].get(i,""),region_text=S["region"].get(i,""))[0]
            for v in ITEMS:
                if name.startswith("dev"):
                    p=h[v]; l=lab[i][v]; pl=pool(i)
                    if p and l: c["Vtp"]+=1; per[(v,"tp")]+=1
                    elif p: c[pl+"fp"]+=1; per[(v,"fp")]+=1
                    elif l: c["Vfn"]+=1; per[(v,"fn")]+=1
                else:
                    c["pos"]+=h[v]; per[v]+=h[v]
        if name.startswith("dev"):
            f=[2*per[(v,"tp")]/(2*per[(v,"tp")]+per[(v,"fp")]+per[(v,"fn")]) if per[(v,"tp")] else 0 for v in ITEMS]
            line.append(f"{name}: macro {sum(f)/24:.4f} {dict(c)}")
        else:
            line.append(f"{name}: pos {c['pos']} v9 {per['v9']} v16 {per['v16']} v18 {per['v18']} v22 {per['v22']}")
    print(" | ".join(line))
