import sys, os, json, gzip, pickle, importlib.util, hashlib, re
from pathlib import Path
ITEMS = [f"v{i}" for i in range(1, 25)]
base, var, item = sys.argv[1], sys.argv[2], sys.argv[3]
sign = sys.argv[4] if len(sys.argv) > 4 else '+'
lim = int(sys.argv[5]) if len(sys.argv) > 5 else 40
def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def cache(p):
    h = hashlib.md5(Path(p).read_bytes()).hexdigest()[:10]
    return pickle.load(open(f"runs/replay_cache/{Path(p).parent.name}_{Path(p).stem}_{h}.pkl", 'rb'))
A, B = cache(base), cache(var)
k = ITEMS.index(item)
ids = [i for i in A if A[i] and B[i] and A[i][k] != B[i][k] and ((B[i][k] == 1) == (sign == '+'))]
print(item, sign, len(ids))
ma, mb = load(base, 'a'), load(var, 'b')
want = set(ids[:lim])
n = 0
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r['id'] not in want: continue
    n += 1
    la, ea = ma.rx_sme_level(r); lb, eb = mb.rx_sme_level(r)
    # find the sentence used by new
    lines = []
    for d in r['docs']:
        L = [x.strip() for x in d['text'].split('\n')]
        for j, x in enumerate(L):
            if eb and x == eb:
                s, e = mb._sentence_span(L, j); lines = L[s:e+1]; break
        if lines: break
    mt = r['meta']
    print(f"--- {r['id']} {mt['계약방법']} {mt['업무구분']} {mt['입찰추정가격']} | 조항호={str(mt['조항호내용'])[:40]} | old={la} new={lb}")
    print('    old ev:', ea[:150]); print('    new sent:', ' ⏎ '.join(lines)[:400])
