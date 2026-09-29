import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
from poolcounts import counts, pool
lab = D.labels()
VERS = [('focused_calls', 'submissions/20260922_focused_calls/script.py', 0.687531013),
        ('v22_region_fix', 'submissions/20260923_v22_region_fix/script.py', 0.6888170931),
        ('int8_quote_port', 'submissions/20260924_int8_quote_port/script.py', 0.690815618),
        ('09-25 cand', 'submissions/20260925_v8nat_v22fix_v21wide/script.py', None),
        ('09-26 cand', 'submissions/20260926_phrase_parser_recall/script.py', None)]
C = {name: counts(p) for name, p, _ in VERS}
def item_counts(res):
    out = {}
    for v in D.ITEMS:
        c = dict(tpC=0, fnC=0, fpC=0, tpM=0, fnM=0, fpM=0)
        for i, h in res['dev'].items():
            p = pool(i); y = int(lab[i][v]); x = h[v]
            if y and x: c['tp'+p] += 1
            elif y: c['fn'+p] += 1
            elif x: c['fp'+p] += 1
        c['unl'] = sum(h[v] for h in res['unl'].values())
        out[v] = c
    return out
IC = {k: item_counts(v) for k, v in C.items()}
N = 1853; nC = 91; nCtrl = 109 + 750
def macro(ic, fracC, q=0.0, miss=0.0, use_may=True):
    a = fracC * N / nC; b = (1 - fracC) * N / nCtrl
    tot = 0; per = {}
    for v, c in ic.items():
        nat = c['unl'] + (c['fpM'] + c['tpM'] if use_may else 0)
        tp = a * c['tpC'] + b * q * nat
        fp = a * c['fpC'] + b * (1 - q) * nat
        fn = a * c['fnC'] + b * miss * 1.0 + (b * c['fnM'] if use_may else 0)
        f = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
        per[v] = f; tot += f
    return tot / 24, per
import itertools
print('Model B (all natural hits FP):')
for fracC in [0.08, 0.10, 0.11, 0.12, 0.14, 0.16, 0.2, 0.3]:
    vals = [macro(IC[n], fracC)[0] for n, _, _ in VERS]
    print(f'  fracC={fracC:.2f} ' + ' '.join(f'{n}={x:.4f}' for (n, _, _), x in zip(VERS, vals)) + f'  d1={vals[1]-vals[0]:+.4f} d2={vals[2]-vals[1]:+.4f} d3={vals[3]-vals[2]:+.4f} d4={vals[4]-vals[3]:+.4f}')
print('observed d1=+0.0013 d2=+0.0020')
print('Model A (natural hits TP with prob q; natural misses at rate miss per item per notice):')
for fracC, q, miss in [(0.45, 0.75, 0.01), (0.3, 0.75, 0.01), (0.2, 0.75, 0.02), (0.1, 0.75, 0.03), (0.0, 0.75, 0.05), (0.0, 0.6, 0.05), (0.0, 0.5, 0.03), (0.1, 0.5, 0.03)]:
    vals = [macro(IC[n], fracC, q, miss)[0] for n, _, _ in VERS]
    print(f'  fracC={fracC:.2f} q={q} miss={miss} ' + ' '.join(f'{x:.4f}' for x in vals) + f'  d1={vals[1]-vals[0]:+.4f} d2={vals[2]-vals[1]:+.4f} d3={vals[3]-vals[2]:+.4f} d4={vals[4]-vals[3]:+.4f}')
