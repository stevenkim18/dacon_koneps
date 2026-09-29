import sys, json, gzip, importlib.util
def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
mb = load(sys.argv[1], 'b')
want = set(sys.argv[2].split(','))
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r['id'] not in want: continue
    lv, ev = mb.rx_sme_level(r)
    print('=====', r['id'], lv, '| ev:', ev[:120])
    # show accepted candidates with levels
    for s, evl in mb._sme_candidates(r):
        if evl == ev:
            print('   cand:', s[:330])
