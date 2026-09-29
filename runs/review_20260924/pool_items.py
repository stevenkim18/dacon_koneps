"""dev 두 묶음(위반 V / 5월 M)별 항목 TP·FN·FP를 후보 스크립트마다 센다(클라우드 int8 저장 출력).
사용: .venv/bin/python runs/review_20260924/pool_items.py A/script.py B/script.py ..."""
import json, csv, sys, importlib.util, collections
ITEMS=[f"v{i}" for i in range(1,25)]
lab={r["id"]:{v:int(r[v]) for v in ITEMS} for r in csv.DictReader(open("open/dev_labels.csv",encoding="utf-8"))}
dev=[json.loads(l) for l in open("open/dev.jsonl",encoding="utf-8")]
def pool(i):
    n=int(i.split("-")[-1]); return "V" if (1<=n<=80 or 131<=n<=141) else "M"
def load(p): return {json.loads(l)["id"]:json.loads(l)["text"] for l in open(p,encoding="utf-8")}
S={k:load(f"runs/cloud_int8_20260923/dev/raw/{k}.jsonl") for k in ["main","item","model","sme","region"]}
for path in sys.argv[1:]:
    spec=importlib.util.spec_from_file_location("m"+str(abs(hash(path))),path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    tbl=m.load_competitive_table("open/data"); c=collections.Counter()
    for r in dev:
        i=r["id"]
        h=m.decide(r,S["main"].get(i,""),tbl,item_text=S["item"].get(i,""),model_text=S["model"].get(i,""),sme_text=S["sme"].get(i,""),region_text=S["region"].get(i,""))[0]
        for v in ITEMS:
            p,l=h[v],lab[i][v]
            if p and l: c[(v,"tp")]+=1
            elif p: c[(v,"fp"+pool(i))]+=1
            elif l: c[(v,"fn")]+=1
    print(path)
    print("  item  TP FN FPv FPm")
    for v in ITEMS:
        row=[c[(v,k)] for k in ("tp","fn","fpV","fpM")]
        if any(row): print(f"  {v:>4} {row[0]:3d} {row[1]:2d} {row[2]:3d} {row[3]:3d}")
    print("  total", [sum(c[(v,k)] for v in ITEMS) for k in ("tp","fn","fpV","fpM")])
