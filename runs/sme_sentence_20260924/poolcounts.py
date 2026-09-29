"""For a script: per-item counts on dev pools (int8 dev raw) and on the 750 unlabeled (int8 exp raw). Cached to pickle."""
import sys, re, json, gzip, pickle, os
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
SP = os.path.dirname(os.path.abspath(__file__))
def pool(i):
    n = int(re.sub(r'\D', '', i)); return 'C' if (n <= 80 or 131 <= n <= 141) else 'M'
def counts(script, dev_which='int8'):
    key = os.path.join(SP, 'pc_' + re.sub(r'\W', '_', script) + '_' + dev_which + '.pkl')
    if os.path.exists(key): return pickle.load(open(key, 'rb'))
    lab = D.labels()
    m, recs, out = D.run(script, dev_which)
    dev = {i: out[i][0] for i in out}
    # 750 unlabeled with int8 exp raw
    E = 'runs/cloud_int8_exp/exp/raw/'
    raw = dict(main=E+'main.jsonl', item=E+'item.jsonl', model=E+'model.jsonl', sme=E+'sme.jsonl', region=E+'region.jsonl')
    allrecs = list(m.iter_records('open/exp950.jsonl.gz'))
    urecs = [r for r in allrecs if 'DEV' not in r['id']]
    _, _, uout = D.run(script, recs=urecs, raw=raw)
    unl = {i: uout[i][0] for i in uout}
    res = dict(dev=dev, unl=unl)
    pickle.dump(res, open(key, 'wb'))
    return res
if __name__ == '__main__':
    for s in sys.argv[1:]:
        r = counts(s)
        tot = {v: sum(h[v] for h in r['unl'].values()) for v in D.ITEMS}
        print(s, 'unl750 positives', sum(tot.values()), tot)
