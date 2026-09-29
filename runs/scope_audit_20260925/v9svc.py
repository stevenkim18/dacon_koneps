import sys, json, gzip, csv, re
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
m = D.load_mod('submissions/20260927_sme_sentence_v17/script.py')
lab = D.labels()
def cat(p):
    d = {}
    for l in open(p, encoding='utf-8'):
        r = json.loads(l); d[r['id']] = r.get('text', '')
    return d
sets = [('dev', list(m.iter_records('open/dev.jsonl')), cat('runs/cloud_int8_20260923/dev/raw/main.jsonl')),
        ('750', [r for r in m.iter_records('open/exp950.jsonl.gz') if 'DEV' not in r['id']], cat('runs/cloud_int8_exp/exp/raw/main.jsonl'))]
for name, recs, main in sets:
    n_svc = n_loc = 0; rows = []
    for r in recs:
        if m.is_goods(r): continue
        n_svc += 1
        f = m.parse_facts(main.get(r['id'], '')) or {}
        if not f.get('특정모델_지정'): continue
        ev = m.clean_evidence(str(f.get('특정모델_근거') or ''), m.full_text(r))
        rows.append((r['id'], r['meta']['적용계약법'][:2], r['meta']['업무구분'], r['meta']['계약방법'], '동등' in str(f.get('특정모델_근거') or ''), lab[r['id']]['v9'] if r['id'] in lab else '-', ev[:170].replace('\n', ' / ')))
    print(f'== {name}: 용역 등 {n_svc}건 중 본 호출 특정모델=True {len(rows)}건 (지방 {sum(1 for x in rows if x[1]=="지방")})')
    for x in rows: print('  ', x)
