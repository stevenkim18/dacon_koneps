import sys, json, os, pickle, csv, glob
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
SP = os.path.dirname(os.path.abspath(__file__))
res = pickle.load(open(os.path.join(SP, 'b4i8_750.pkl'), 'rb'))
m = D.load_mod('submissions/20260926_phrase_parser_recall/script.py')
v = sys.argv[1]; which = sys.argv[2] if len(sys.argv) > 2 else 'i8only'
# existing hand labels
hl = {}
for f in ['labels/train250_audit.csv', 'labels/train500_audit.csv']:
    for r in csv.DictReader(open(f, encoding='utf-8')):
        hl[(r['id'], r['item'])] = (r['label'], r['reason'][:120])
def cat(p):
    d = {}
    for l in open(p, encoding='utf-8'):
        r = json.loads(l); d[r['id']] = r.get('text', '')
    return d
main8 = cat('runs/cloud_int8_exp/exp/raw/main.jsonl'); model8 = cat('runs/cloud_int8_exp/exp/raw/model.jsonl')
recs = {}
for p in ['runs/mlx/train_sample250.jsonl', 'runs/mlx/train_sample500_next.jsonl']:
    for l in open(p, encoding='utf-8'):
        r = json.loads(l); recs[r['id']] = r
a = {i for i in res['b4'] if res['b4'][i][0][v]}; b = {i for i in res['i8'] if res['i8'][i][0][v]}
sel = sorted(b - a) if which == 'i8only' else sorted(a & b) if which == 'both' else sorted(a - b)
for i in sel:
    r = recs[i]; f = m.parse_facts(main8.get(i, '')) or {}
    print(f"--- {i} | {r['meta']['업무구분']} | {r['meta']['계약방법']} | {r['meta']['입찰추정가격']} | title={m.title_of(r)[:60]!r} | hand={hl.get((i, v))}")
    if v == 'v1':
        print('    특정기관_근거:', str(f.get('특정기관_근거'))[:300].replace('\n', ' / '))
    elif v == 'v9':
        lines = m.model_candidate_lines(r); mf = m.parse_facts(model8.get(i, '')) or {}
        idx = mf.get('줄번호'); line = lines[idx-1] if isinstance(idx, int) and 1 <= idx <= len(lines) else ''
        print('    model-call line:', line[:200], '| main:', f.get('특정모델_지정'), str(f.get('특정모델_근거'))[:150].replace('\n', ' / '))
    else:
        print('    e:', res['i8'][i][1].get('e' + v[1:], '')[:250])
