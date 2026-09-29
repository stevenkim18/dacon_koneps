import json, gzip, re, collections, importlib.util, csv
ROOT=str(__import__("pathlib").Path(__file__).resolve().parents[2])
spec=importlib.util.spec_from_file_location("m", ROOT+"/submissions/20260924_int8_quote_port/script.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
tbl=m.load_competitive_table(ROOT+"/open/data")
QUAL = re.compile(r"참가\s*자격|자격\s*요건|참가자의\s*자격|응찰\s*자격|입찰\s*참여\s*자격")
TOP = re.compile(r"^\s*(\d{1,2}|[IVX]{1,4}|[一二三四五六七八九十])\s*[\.\)]\s*\S")
def sec_lines(r):
    out=set(); found=False
    for d in r["docs"]:
        lines=d["text"].split("\n"); i=0
        while i<len(lines):
            l=lines[i]
            if TOP.match(l) and QUAL.search(l) and len(l.strip())<60:
                j=i+1
                while j<len(lines) and not (TOP.match(lines[j]) and len(lines[j].strip())<60 and not QUAL.search(lines[j])): j+=1
                found=True
                for x in lines[i:j]:
                    n=re.sub(r"\s+","",x)
                    if n: out.add(n)
                i=j
            else: i+=1
    return found,out
labs=collections.defaultdict(dict)
for f in ["labels/train250_audit.csv","labels/train500_audit.csv"]:
    for row in csv.DictReader(open(ROOT+"/"+f,encoding="utf-8")):
        if row["label"] in ("0","1"): labs[row["id"]][row["item"]]=int(row["label"])
Q={"v2","v3","v4","v5","v6","v7","v8","v12","v13","v14","v15","v17","v21","v22"}
res=collections.defaultdict(lambda: collections.Counter()); rows=[]
for line in gzip.open(ROOT+"/open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=json.loads(line)
    if r["id"] not in labs: continue
    hits,evid,_=m.decide(r,"",tbl)
    found,S=sec_lines(r)
    for k,lab in labs[r["id"]].items():
        if k not in Q or not hits.get(k): continue
        ev=re.sub(r"\s+","",evid.get(k,"") or "")
        where = "nosec" if not found else ("in" if ev and any(ev[:30] in s or (len(s)>15 and s in ev) for s in S) else "out")
        res[where][lab]+=1; rows.append((where,k,lab,r["id"],(evid.get(k) or "")[:120]))
for w in ("in","out","nosec"):
    c=res[w]; n=c[0]+c[1]; print(w, "labeled pairs", n, "precision", round(c[1]/n,3) if n else None, dict(c))
for x in rows:
    if x[0]!="in": print(x)
