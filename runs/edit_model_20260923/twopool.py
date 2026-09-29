import json, csv, sys, collections
ITEMS=[f"v{i}" for i in range(1,25)]
lab={r["id"]:{v:int(r[v]) for v in ITEMS} for r in csv.DictReader(open("open/dev_labels.csv",encoding="utf-8"))}
def pool(i):
    n=int(i.split("-")[-1]); return "V" if (1<=n<=80 or 131<=n<=141) else "M"
P=json.load(open(sys.argv[1]))      # dev preds
N=json.load(open(sys.argv[2]))      # natural 750 preds
nat=collections.Counter()
for i,h in N.items(): nat.update({v:h[v] for v in ITEMS})
nN=len(N)
st={v:collections.Counter() for v in ITEMS}
for i in lab:
    if pool(i)!="V": continue
    for v in ITEMS:
        p=P[i][v]; l=lab[i][v]
        st[v]["tp"]+= p and l; st[v]["fp"]+= p and not l; st[v]["fn"]+= l and not p
nV=91
def macro(V,C,rec_scale=1.0, fp_scale=1.0, natscale=1.0, verbose=False):
    fs=[]
    for v in ITEMS:
        pos=(st[v]["tp"]+st[v]["fn"])/nV*V
        tp=st[v]["tp"]/nV*V*rec_scale
        fn=pos-tp
        fp=st[v]["fp"]/nV*V*fp_scale + nat[v]/nN*C*natscale
        f=2*tp/(2*tp+fp+fn) if tp>0 else 0
        fs.append(f)
        if verbose: print(f"  {v}: pos={pos:.0f} tp={tp:.0f} fp={fp:.0f} fn={fn:.0f} F1={f:.3f}")
    return sum(fs)/len(fs)
T=1853
for frac in [1.0,0.8,0.6,0.5,0.4,0.3,0.2,0.1]:
    V=T*frac; C=T-V
    print(f"V={V:.0f} C={C:.0f}: in-sample {macro(V,C):.4f} | recall*0.85 {macro(V,C,0.85):.4f} | recall*0.85 fpV*2 {macro(V,C,0.85,2):.4f} | recall*0.75,fpV*3 {macro(V,C,0.75,3):.4f}")
