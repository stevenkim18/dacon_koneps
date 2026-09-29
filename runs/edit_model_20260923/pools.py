import json, csv, sys, collections
ITEMS=[f"v{i}" for i in range(1,25)]
lab={r["id"]:{v:int(r[v]) for v in ITEMS} for r in csv.DictReader(open("open/dev_labels.csv",encoding="utf-8"))}
recs={}
for line in open("open/dev.jsonl",encoding="utf-8"):
    r=json.loads(line); recs[r["id"]]=r
def pool(i):
    n=int(i.split("-")[-1])
    return "V" if (1<=n<=80 or 131<=n<=141) else "M"
# check months
mon=collections.Counter()
for i,r in recs.items():
    mon[(pool(i), str(r["meta"].get("공고게시일자"))[:7])]+=1
print(sorted(mon.items()))
for fn in sys.argv[1:]:
    P=json.load(open(fn))
    print("==",fn)
    tot=collections.Counter()
    print("item  V:tp/fp/fn   M:tp/fp/fn")
    for v in ITEMS:
        c=collections.Counter()
        for i in lab:
            p=P[i][v]; l=lab[i][v]; pl=pool(i)
            if p and l: c[pl+"tp"]+=1
            elif p and not l: c[pl+"fp"]+=1
            elif l and not p: c[pl+"fn"]+=1
        tot.update(c)
        print(f"{v:4} V:{c['Vtp']}/{c['Vfp']}/{c['Vfn']}   M:{c['Mtp']}/{c['Mfp']}/{c['Mfn']}")
    print("TOTAL", dict(tot))
