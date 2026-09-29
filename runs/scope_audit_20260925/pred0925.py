import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fit import IC, D
N = 1853; nC = 91; nCtrl = 859
base = IC['focused_calls']
def counts(ic, fracC, tau, q, miss):
    a = fracC * N / nC; b = (1 - fracC) * N / nCtrl
    out = {}
    for v in D.ITEMS:
        c, c0 = ic[v], base[v]
        tpC = c0['tpC'] + tau * (c['tpC'] - c0['tpC']); fnC = c0['fnC'] + tau * (c['fnC'] - c0['fnC']); fpC = c0['fpC'] + tau * (c['fpC'] - c0['fpC'])
        nat = c['unl'] + c['fpM'] + c['tpM']
        out[v] = [a * tpC + b * q * nat, a * fpC + b * (1 - q) * nat, a * fnC + b * (miss + c['fnM'] / nCtrl) * nCtrl]
    return out
f1 = lambda tp, fp, fn: 2 * tp / (2 * tp + fp + fn) if tp > 0 else 0.0
macro = lambda cnt: sum(f1(*cnt[v]) for v in D.ITEMS) / 24
OBS = 0.690815618
print('params                          | 모형 int8_quote_port → 09-25 후보(750 계수) | 20,000 계수로 v8·v22 직접 가산: v8 국가 정밀도 0 / 0.5 / 0.87')
for fracC, tau, q, miss in [(0.08, 0.3, 0.6, 0.005), (0.08, 0.5, 0.6, 0.005), (0.12, 0.1, 0.5, 0.005), (0.10, 0.2, 0.6, 0.005), (0.25, 0.3, 0.9, 0.02)]:
    c8 = counts(IC['int8_quote_port'], fracC, tau, q, miss); c25 = counts(IC['09-25 cand'], fracC, tau, q, miss)
    m8, m25 = macro(c8), macro(c25)
    nnat = (1 - fracC) * N
    add_v8 = 66 / 20000 * nnat; add_v22 = 31 / 20000 * nnat
    res = []
    for p8 in (0.0, 0.5, 0.87):
        c = {v: list(x) for v, x in c8.items()}
        # new national v8 hits: TP portion was a miss before (FN -> TP), FP portion is new FP
        c['v8'][0] += p8 * add_v8; c['v8'][2] = max(0.0, c['v8'][2] - p8 * add_v8); c['v8'][1] += (1 - p8) * add_v8
        p22 = 0.7
        c['v22'][0] += p22 * add_v22; c['v22'][2] = max(0.0, c['v22'][2] - p22 * add_v22); c['v22'][1] += (1 - p22) * add_v22
        res.append(macro(c) - m8)
    v8 = c8['v8']
    print(f'fracC={fracC:.2f} tau={tau} q={q} miss={miss} | {m25 - m8:+.4f} → 예상 {OBS + m25 - m8:.4f} | {res[0]:+.4f} / {res[1]:+.4f} / {res[2]:+.4f} → {OBS+res[0]:.4f} / {OBS+res[1]:.4f} / {OBS+res[2]:.4f}  (모형 v8 TP {v8[0]:.1f} FP {v8[1]:.1f} FN {v8[2]:.1f}, 추가 v8 {add_v8:.1f}건 · v22 {add_v22:.1f}건)')
