import sys, re
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
script = sys.argv[1]; which = sys.argv[2]
m, recs, out = D.run(script, which)
lab = D.labels()
def pool(i):
    n = int(re.sub(r'\D', '', i)); return 'C' if (n <= 80 or 131 <= n <= 141) else 'M'
cnt = {}
for v in D.ITEMS:
    c = {'tpC':0,'fnC':0,'fpC':0,'tpM':0,'fnM':0,'fpM':0}
    for i in out:
        p = pool(i); y = int(lab[i][v]); h = out[i][0][v]
        if y and h: c['tp'+p] += 1
        elif y: c['fn'+p] += 1
        elif h: c['fp'+p] += 1
    cnt[v] = c
nC = sum(1 for i in out if pool(i)=='C'); nM = len(out) - nC
print('pools', nC, nM)
def macro(fracC, N=1853, extra_fp_per_ctrl=0.0):
    a = fracC*N/nC; b = (1-fracC)*N/nM
    fs = {}
    for v, c in cnt.items():
        tp = a*c['tpC'] + b*c['tpM']; fn = a*c['fnC'] + b*c['fnM']; fp = a*c['fpC'] + b*c['fpM'] + extra_fp_per_ctrl*(1-fracC)*N/24
        fs[v] = 2*tp/(2*tp+fp+fn) if tp else 0
    return sum(fs.values())/24, fs
for f in [0.455, 0.35, 0.25, 0.2, 0.15, 0.1, 0.07, 0.05]:
    mac, fs = macro(f)
    print(f'fracC={f:.3f}  macro={mac:.4f}  ' + ' '.join(f'{v}:{fs[v]:.2f}' for v in D.ITEMS))
