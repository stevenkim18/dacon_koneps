import json, csv, sys, importlib.util, collections
ITEMS=[f"v{i}" for i in range(1,25)]
spec=importlib.util.spec_from_file_location("cand", sys.argv[1]); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
D=sys.argv[2]  # dir or 'mlx'
if D=="mlx":
    files=dict(main="runs/mlx/extract_outputs.jsonl", item="runs/mlx/item_outputs.jsonl", model="runs/mlx/model_outputs.jsonl", sme="runs/mlx/v21_sme_dev.jsonl", region="runs/mlx/v22_region_dev.jsonl")
else:
    files={k:f"{D}/{k}.jsonl" for k in ["main","item","model","sme","region"]}
def load(p):
    out={}
    try:
        for line in open(p,encoding="utf-8"):
            r=json.loads(line); out[r["id"]]=r["text"]
    except FileNotFoundError: pass
    return out
S={k:load(v) for k,v in files.items()}
table=mod.load_competitive_table("open/data")
lab={r["id"]:r for r in csv.DictReader(open("open/dev_labels.csv",encoding="utf-8"))}
recs={}
for line in open("open/dev.jsonl",encoding="utf-8"):
    r=mod.normalize(json.loads(line)) if hasattr(mod,"normalize") else json.loads(line); recs[r["id"]]=r
def pool(i):
    n=int(i.split("-")[-1]); return "V" if (1<=n<=80 or 131<=n<=141) else "M"
MK=["적용계약법","업무구분","계약방법","낙찰방법","입찰추정가격","배정예산금액","소관구분","지역제한여부","제한지역코드목록","업종제한여부","면허업종제한목록","조항호내용","세부품명번호목록","공동도급구성방식"]
out=[]
for i,r in recs.items():
    hits,evid,_=mod.decide(r,S["main"].get(i,""),table,item_text=S["item"].get(i,""),model_text=S["model"].get(i,""),sme_text=S["sme"].get(i,""),region_text=S["region"].get(i,""))
    for v in ITEMS:
        l=int(lab[i][v]); p=hits[v]
        if p!=l:
            kind="FP" if p else "FN"
            out.append((pool(i),v,kind,i,evid.get(v,""),lab[i]["e"+v[1:]],{k:r["meta"].get(k) for k in MK}, r.get("dropped_doc_counts")))
out.sort(key=lambda x:(x[0],int(x[1][1:]),x[2]))
for o in out:
    print(f"### {o[0]} {o[1]} {o[2]} {o[3]}")
    print("  meta:", json.dumps(o[6],ensure_ascii=False))
    if o[7]: print("  dropped:", o[7])
    if o[4]: print("  our_ev:", o[4][:300].replace("\n"," / "))
    if o[5]: print("  gold_ev:", o[5][:300].replace("\n"," / "))
