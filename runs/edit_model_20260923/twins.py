import json,gzip,re,collections,pickle,sys
def norm(l): return re.sub(r"\s+","",l)
def lines(r):
    out=set()
    for d in r["docs"]:
        for l in d["text"].split("\n"):
            n=norm(l)
            if len(n)>=12: out.add(n)
    return out
tr=[json.loads(l) for l in gzip.open("open/train_unlabeled.jsonl.gz","rt",encoding="utf-8")]
idx=collections.defaultdict(list); L={}
for r in tr:
    s=lines(r); L[r["id"]]=s
    for x in s: idx[x].append(r["id"])
# drop very common lines
common={x for x,v in idx.items() if len(v)>200}
dev=[json.loads(l) for l in open("open/dev.jsonl",encoding="utf-8")]
res={}
for r in dev:
    s=lines(r); cnt=collections.Counter()
    for x in s:
        if x in common: continue
        for j in idx.get(x,[]): cnt[j]+=1
    best=None
    for j,c in cnt.most_common(5):
        jac=len(s & L[j])/len(s | L[j])
        if best is None or jac>best[1]: best=(j,jac)
    res[r["id"]]=best
pickle.dump(res,open(sys.argv[1],"wb"))
def pool(i):
    n=int(i.split("-")[-1]); return "V" if (1<=n<=80 or 131<=n<=141) else "M"
for p in "VM":
    js=[res[i][1] for i in res if pool(i)==p and res[i]]
    print(p, "n",len(js), "jac>=0.5:",sum(j>=0.5 for j in js), "jac>=0.3:",sum(j>=0.3 for j in js), "median", sorted(js)[len(js)//2])
