import json, gzip, random, re, sys, copy, importlib.util
sys.path.insert(0, 'runs/edit_model_20260923')
from paraphrases import P
def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
A = load('submissions/20260926_phrase_parser_recall/script.py', 'a'); B = load(sys.argv[1], 'b')
tbl = A.load_competitive_table('open/data')
rng = random.Random(7); base = []
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r.get('dropped_doc_counts'): continue
    if not any(d['type'] == '공고문' for d in r['docs']): continue
    base.append(r)
rng.shuffle(base); base = base[:6000]
def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r['docs']:
        if d['type'] != '공고문': continue
        lines = d['text'].split('\n')
        k = next((i for i, l in enumerate(lines) if re.search(r'참가\s*자격', l)), None)
        if k is None: k = min(len(lines) - 1, len(lines) // 3)
        lines.insert(k + 1, sent); d['text'] = '\n'.join(lines); break
    return r
price = lambda r: float(r['meta'].get('입찰추정가격') or 0)
priv = lambda r: r['meta'].get('계약방법') == '수의계약'
picked = []
for r in base:
    if len(picked) >= 8: break
    if not priv(r) and 5e6 <= price(r) < 1e8 and not A.decide(r, '', tbl)[0]['v17']: picked.append(r)
for s in P['v_sme_mid']:
    for b in picked:
        r = inject(b, s)
        ha = A.decide(r, '', tbl)[0]['v17']; hb = B.decide(r, '', tbl)[0]['v17']
        if ha != hb:
            print('==', b['id'], 'old', ha, 'new', hb, '|', s)
            print('   old level', A.rx_sme_level(r)); print('   new level', B.rx_sme_level(r))
