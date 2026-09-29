"""Diff a variant vs base on dev (int8, b4) by pool + on 750 (int8, b4)."""
import sys, os, re, json, pickle
sys.path.insert(0, 'runs/int8_port_20260923'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import devtool as D
from poolcounts import pool
base, var = sys.argv[1], sys.argv[2]
lab = D.labels()
def u750():
    def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8')]
    return jl('runs/mlx/train_sample250.jsonl') + jl('runs/mlx/train_sample500_next.jsonl')
def cat(*ps):
    d = {}
    for p in ps:
        if os.path.exists(p):
            for l in open(p, encoding='utf-8'):
                r = json.loads(l); d[r['id']] = r.get('text', '')
    return d
RAW750 = {'b4': {k: cat(f'runs/mlx/train250_{k}.jsonl', f'runs/mlx/train500_{k}.jsonl') for k in ['main','item','model','sme','region']},
          'int8': {k: cat(f'runs/cloud_int8_exp/exp/raw/{k}.jsonl') for k in ['main','item','model','sme','region']}}
def run750(script, which):
    m = D.load_mod(script); tbl = m.load_competitive_table('open/data'); S = RAW750[which]; out = {}
    for r in u750():
        r = m.normalize(r); i = r['id']
        h, e, _ = m.decide(r, S['main'].get(i, ''), tbl, item_text=S['item'].get(i, ''), model_text=S['model'].get(i, ''),
                           sme_text=S['sme'].get(i, ''), region_text=S['region'].get(i, ''))
        out[i] = (h, e)
    return out
for which in ['int8', 'b4']:
    _, _, ob = D.run(base, which); _, _, ov = D.run(var, which)
    sb, sv = D.score(ob, lab), D.score(ov, lab)
    print(f'== dev {which}: macro {sb["macro"]:.4f} -> {sv["macro"]:.4f}')
    for i in ob:
        for v in D.ITEMS:
            if ob[i][0][v] != ov[i][0][v]:
                print(f'   {"+" if ov[i][0][v] else "-"}{v} {i}{pool(i)} label={lab[i][v]}')
    a, b = run750(base, which), run750(var, which)
    ch = [(i, v, b[i][0][v]) for i in a for v in D.ITEMS if a[i][0][v] != b[i][0][v]]
    print(f'== 750 {which}: changes {len(ch)}:', ' '.join(f'{"+" if x else "-"}{v}:{i}' for i, v, x in ch))
