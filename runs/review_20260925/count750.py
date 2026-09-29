import sys, json, gzip, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "int8_port_20260923"))
import devtool as D
recs = [json.loads(l) for l in gzip.open(D.ROOT/'open/exp950.jsonl.gz','rt',encoding='utf-8')]
r750 = [r for r in recs if not r['id'].startswith('PPS-DEV')]
RAW = {k: D.ROOT/f'runs/cloud_int8_exp/exp/raw/{k}.jsonl' for k in ['main','item','model','sme','region']}
for s in sys.argv[1:]:
    _, _, o = D.run(s, recs=r750, raw=RAW)
    c = collections.Counter()
    for i,(h,e) in o.items():
        for v in D.ITEMS: c[v]+=h[v]
    print(s.split('/')[-2][:30], sum(c.values()), " ".join(f"{v}:{c[v]}" for v in D.ITEMS))
