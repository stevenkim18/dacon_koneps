import json,gzip,re,collections,pickle,sys,csv
ITEMS=[f"v{i}" for i in range(1,25)]
lab={r["id"]:r for r in csv.DictReader(open("open/dev_labels.csv",encoding="utf-8"))}
res=pickle.load(open(sys.argv[1],"rb"))
thr=float(sys.argv[2]); which=sys.argv[3]
def norm(l): return re.sub(r"\s+","",l)
tr={}
need={v[0] for k,v in res.items() if v and v[1]>=thr}
for l in gzip.open("open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=json.loads(l)
    if r["id"] in need: tr[r["id"]]=r
dev={json.loads(l)["id"]:json.loads(l) for l in open("open/dev.jsonl",encoding="utf-8")}
def pool(i):
    n=int(i.split("-")[-1]); return "V" if (1<=n<=80 or 131<=n<=141) else "M"
for i,(j,jac) in sorted(res.items()):
    if jac<thr or pool(i)!=which: continue
    d=dev[i]; t=tr[j]
    tl={norm(x) for dd in t["docs"] for x in dd["text"].split("\n")}
    uniq=[]
    for dd in d["docs"]:
        for x in dd["text"].split("\n"):
            n=norm(x)
            if len(n)>=8 and n not in tl: uniq.append((dd["type"],x.strip()))
    pos=[v for v in ITEMS if lab[i][v]=="1"]
    print(f"########## {i} labels={pos} twin={j} jac={jac:.2f} uniq_lines={len(uniq)} meta_same={ {k:(d['meta'][k]==t['meta'][k]) for k in ['입찰추정가격','계약방법','지역제한여부','면허업종제한목록']} }")
    for ty,x in uniq[:40]:
        print(f"   [{ty}] {x[:230]}")
