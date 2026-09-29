import sys, re
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
script = sys.argv[1]; which = sys.argv[2] if len(sys.argv) > 2 else 'int8'
m, recs, out = D.run(script, which)
lab = D.labels()
def pool(i):
    n = int(re.sub(r'\D', '', i))
    return 'C' if (n <= 80 or 131 <= n <= 141) else 'M'
res = D.score(out, lab)
print('macro', round(res['macro'], 4))
for v in D.ITEMS:
    f, tp, fp, fn = res[v]
    fps = [i for i in out if not int(lab[i][v]) and out[i][0][v]]
    fns = [i for i in out if int(lab[i][v]) and not out[i][0][v]]
    print(f"{v:4} F1={f:.3f} tp={tp} fp={fp} fn={fn} | FP: {' '.join(i.replace('PPS-DEV-','')+pool(i) for i in fps)} | FN: {' '.join(i.replace('PPS-DEV-','')+pool(i) for i in fns)}")
