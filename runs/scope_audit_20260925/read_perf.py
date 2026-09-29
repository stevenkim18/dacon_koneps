import sys, json, gzip, pickle, hashlib, importlib.util
from pathlib import Path
ITEMS = [f"v{i}" for i in range(1, 25)]
def cache(p):
    h = hashlib.md5(Path(p).read_bytes()).hexdigest()[:10]
    return pickle.load(open(f"runs/replay_cache/{Path(p).parent.name}_{Path(p).stem}_{h}.pkl", 'rb'))
base, var = sys.argv[1], sys.argv[2]
A, B = cache(base), cache(var)
spec = importlib.util.spec_from_file_location('b', var); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ch = {i: [ITEMS[k] for k in range(24) if A[i][k] != B[i][k]] for i in A if A[i] and B[i] and A[i] != B[i]}
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r['id'] not in ch: continue
    mt = r['meta']; perf = m.rx_performance(r)
    print(f"--- {r['id']} {ch[r['id']]} {mt['계약방법']} {mt['적용계약법'][:2]} 추정 {float(mt['입찰추정가격'] or 0):,.0f} 예산 {float(mt['배정예산금액'] or 0):,.0f}")
    for s in perf[:3]: print('    perf:', s[:220])
