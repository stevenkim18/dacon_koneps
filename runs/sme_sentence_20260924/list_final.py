import sys, json, gzip, pickle, hashlib, importlib.util, csv
from pathlib import Path
ITEMS = [f"v{i}" for i in range(1, 25)]
def cache(p):
    h = hashlib.md5(Path(p).read_bytes()).hexdigest()[:10]
    return pickle.load(open(f"runs/replay_cache/{Path(p).parent.name}_{Path(p).stem}_{h}.pkl", 'rb'))
base, var = sys.argv[1], sys.argv[2]
A, B = cache(base), cache(var)
spec = importlib.util.spec_from_file_location('b', var); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rows = []
for it in ['v17', 'v14', 'v16', 'v18']:
    k = ITEMS.index(it)
    for i in A:
        if A[i] and B[i] and A[i][k] != B[i][k]:
            rows.append((i, it, '+' if B[i][k] else '-'))
want = {i for i, _, _ in rows}
recs = {}
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r['id'] in want: recs[r['id']] = r
out = []
for i, it, sgn in sorted(rows, key=lambda x: (x[1], x[2], x[0])):
    r = recs[i]; mt = r['meta']; lv, ev = m.rx_sme_level(r)
    out.append([i, it, sgn, mt['계약방법'], mt['적용계약법'], int(float(mt['입찰추정가격'] or 0)), mt['조항호내용'], lv, ev.replace('\n', ' ')[:300]])
w = csv.writer(open(sys.argv[3], 'w', encoding='utf-8', newline=''))
w.writerow(['id', '항목', '변화', '계약방법', '적용계약법', '추정가격', '조항호내용', '새_수준', '수준_근거줄'])
w.writerows(out)
from collections import Counter
print(Counter((x[1], x[2]) for x in out)); print(Counter(x[3] for x in out if x[1] == 'v17' and x[2] == '+'))
