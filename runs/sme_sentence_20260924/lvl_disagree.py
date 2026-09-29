import sys, os, json, re
sys.path.insert(0, 'runs/int8_port_20260923'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import devtool as D
m = D.load_mod('submissions/20260926_phrase_parser_recall/script.py')
tbl = m.load_competitive_table('open/data')
lab = D.labels()
def cat(p):
    d = {}
    for l in open(p, encoding='utf-8'):
        r = json.loads(l); d[r['id']] = r.get('text', '')
    return d
sme8 = cat('runs/cloud_int8_exp/exp/raw/sme.jsonl')
recs = list(m.iter_records('open/exp950.jsonl.gz'))
rows = []
for r in recs:
    i = r['id']; src = m.full_text(r)
    rxl, rxev = m.rx_sme_level(r)
    s = m.parse_facts(sme8.get(i, '')) or {}
    said = s.get('기업규모_제한')
    lines = [ln for ln in m._verified_lines(s.get('자격_원문_인용'), src) if '조항호내용' not in ln]
    # level of the joined quote (whole quote as one sentence)
    q = ' '.join(lines)
    ql = m.classify_level(q) if q else None
    if said in ('중소기업', '소기업·소상공인') and rxl in ('중소기업', '소기업·소상공인') and said != rxl:
        rows.append((i, r['meta']['계약방법'], r['meta']['입찰추정가격'], rxl, said, ql, rxev[:120], q[:220]))
print('disagreements (rx level != sme-call level, both non-empty):', len(rows))
for x in rows:
    i = x[0]
    y = {v: lab[i][v] for v in ['v13','v14','v15','v16','v17','v18'] if i in lab and lab[i][v] == '1'} if i in lab else '-'
    print(f'--- {i} {x[1]} {x[2]} rx={x[3]} call={x[4]} joined={x[5]} labels={y}')
    print('    rx ev :', x[6]); print('    quote :', x[7])
