import json, gzip, re, collections, importlib.util, pickle, sys
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
ITEMS=[f"v{i}" for i in range(1,25)]
Q=["v1","v2","v3","v4","v5","v6","v7","v8","v12","v13","v14","v15","v17","v21","v22"]
stat=collections.defaultdict(collections.Counter); samples=collections.defaultdict(list)
for line in gzip.open(ROOT+"/open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=json.loads(line)
    try: hits,evid,_=m.decide(r,"",tbl)
    except Exception: continue
    found,S=None,None
    for k in Q:
        if not hits[k]: continue
        if S is None: found,S=sec_lines(r)
        ev=re.sub(r"\s+","",evid.get(k,"") or "")
        if not found: stat[k]["nosec"]+=1; continue
        inside = any(ev[:30] in s or (len(s)>15 and s in ev) for s in S) if ev else False
        stat[k]["in" if inside else "out"]+=1
        if not inside and len(samples[k])<400: samples[k].append((r["id"], (evid.get(k) or "")[:160]))
for k in Q: print(k, dict(stat[k]))
pickle.dump(dict(samples), open(sys.argv[1],"wb"))
