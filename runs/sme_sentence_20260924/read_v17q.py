import sys, json, gzip, pickle, hashlib, importlib.util, random
from pathlib import Path
ITEMS = [f"v{i}" for i in range(1, 25)]
def cache(p):
    h = hashlib.md5(Path(p).read_bytes()).hexdigest()[:10]
    return pickle.load(open(f"runs/replay_cache/{Path(p).parent.name}_{Path(p).stem}_{h}.pkl", 'rb'))
base, var = sys.argv[1], sys.argv[2]
A, B = cache(base), cache(var); k = ITEMS.index('v17')
ids = sorted(i for i in A if A[i] and B[i] and B[i][k] and not A[i][k])
random.Random(int(sys.argv[4]) if len(sys.argv)>4 else 1).shuffle(ids); want = set(ids[:int(sys.argv[3])])
spec = importlib.util.spec_from_file_location('b', var); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from collections import Counter
cz = Counter()
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r['id'] in set(ids): cz[(r['meta']['적용계약법'], r['meta']['업무구분'], str(r['meta']['조항호내용'])[:40])] += 1
    if r['id'] not in want: continue
    lv, ev = m.rx_sme_level(r); mt = r['meta']
    print(f"--- {r['id']} {mt['적용계약법'][:2]} {mt['업무구분']} {float(mt['입찰추정가격']):,.0f} | {mt['조항호내용']}")
    print('    ev:', ev[:230])
print(cz.most_common(12))
