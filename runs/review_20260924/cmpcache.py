import pickle, glob, sys, collections
ITEMS=[f"v{i}" for i in range(1,25)]
base=pickle.load(open(sorted(glob.glob("runs/replay_cache/20260925_v8nat_v22fix_v21wide_script_*.pkl"))[-1],"rb"))
for name in sys.argv[1:]:
    f=sorted(glob.glob(f"runs/replay_cache/v26_{name}_*.pkl"))
    if not f: print(name, "no cache yet"); continue
    v=pickle.load(open(f[-1],"rb")); d=collections.Counter(); ch=0
    for i,t in v.items():
        b=base.get(i)
        if not t or not b: continue
        if t!=b: ch+=1
        for k,(x,y) in enumerate(zip(b,t)):
            if x!=y: d[ITEMS[k]]+= (y-x)
    print(f"{name}: Δ{sum(d.values()):+d} · 변경 {ch}공고 · " + " ".join(f"{k}{c:+d}" for k,c in sorted(d.items(), key=lambda z:int(z[0][1:])) if c))
