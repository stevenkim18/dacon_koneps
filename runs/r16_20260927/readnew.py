import sys, gzip, json, pickle, importlib.util
BASE, VAR, CH = sys.argv[1], sys.argv[2], sys.argv[3]
items = sys.argv[4].split(',') if len(sys.argv) > 4 else None
def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
A = load(BASE, 'a'); B = load(VAR, 'b')
TA = A.load_competitive_table('open/data'); TB = B.load_competitive_table('open/data')
ids = set(pickle.load(open(CH, 'rb')))
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r['id'] not in ids: continue
    ha, ea, _ = A.decide(json.loads(l), '', TA); hb, eb, _ = B.decide(json.loads(l), '', TB)
    diff = [v for v in ha if ha[v] != hb[v] and (not items or v in items)]
    if not diff: continue
    mt = r['meta']
    print(f"== {r['id']} {mt.get('적용계약법')[:2]} {mt.get('계약방법')}/{mt.get('낙찰방법')} p={mt.get('입찰추정가격')} 지역meta={mt.get('지역제한여부')}:{mt.get('제한지역코드목록')} | " + " ".join(f"{'+' if hb[v] else '-'}{v}" for v in diff))
    shown = set()
    for v in diff:
        e = (eb.get(v) or ea.get(v) or '').replace('\n', '⏎')
        if e and e not in shown:
            shown.add(e); print('    ', v, ':', e[:260])
