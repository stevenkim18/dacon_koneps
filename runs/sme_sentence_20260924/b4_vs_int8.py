import sys, json, gzip, os, pickle
from pathlib import Path
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
R = Path('.')
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8')]
SP = os.path.dirname(os.path.abspath(__file__))
script = sys.argv[1]
m = D.load_mod(script)
u750 = jl('runs/mlx/train_sample250.jsonl') + jl('runs/mlx/train_sample500_next.jsonl')
u750 = [m.normalize(r) for r in u750]
def cat(*ps):
    d = {}
    for p in ps:
        if Path(p).exists():
            for l in open(p, encoding='utf-8'):
                r = json.loads(l); d[r['id']] = r.get('text', '')
    return d
tbl = m.load_competitive_table('open/data')
b4 = {k: cat(f'runs/mlx/train250_{k}.jsonl', f'runs/mlx/train500_{k}.jsonl') for k in ['main','item','model','sme','region']}
i8 = {k: cat(f'runs/cloud_int8_exp/exp/raw/{k}.jsonl') for k in ['main','item','model','sme','region']}
res = {}
for name, S in [('b4', b4), ('i8', i8)]:
    out = {}
    for r in u750:
        i = r['id']
        hits, evid, _ = m.decide(r, S['main'].get(i, ''), tbl, item_text=S['item'].get(i, ''), model_text=S['model'].get(i, ''),
                                 sme_text=S['sme'].get(i, ''), region_text=S['region'].get(i, ''))
        out[i] = (hits, evid)
    res[name] = out
pickle.dump(res, open(os.path.join(SP, 'b4i8_750.pkl'), 'wb'))
print('ids', len(u750), 'missing main b4', sum(1 for r in u750 if r['id'] not in b4['main']), 'i8', sum(1 for r in u750 if r['id'] not in i8['main']))
for v in D.ITEMS:
    a = {i for i in res['b4'] if res['b4'][i][0][v]}; b = {i for i in res['i8'] if res['i8'][i][0][v]}
    print(f'{v:4} b4={len(a):3} i8={len(b):3} both={len(a&b):3} b4only={len(a-b):3} i8only={len(b-a):3}')
