import sys, json, re
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
m = D.load_mod(sys.argv[1])
tbl = m.load_competitive_table('open/data')
def cat(p):
    d = {}
    for l in open(p, encoding='utf-8'):
        r = json.loads(l); d[r['id']] = r.get('text', '')
    return d
E = 'runs/cloud_int8_exp/exp/raw/'
S = {k: cat(E + k + '.jsonl') for k in ['main', 'item', 'model', 'sme', 'region']}
recs = {r['id']: r for r in m.iter_records('open/exp950.jsonl.gz')}
ids = sys.argv[2].split(',')
for i in ids:
    r = recs[i]
    llm = m.parse_facts(S['main'].get(i, '')) or {}
    item = m.parse_facts(S['item'].get(i, '')) or {}
    rx = m.regex_facts(r, tbl)
    code = llm.get('계약목적물_세부품명번호'); it = tbl.get(str(code)) or {}
    icode = item.get('세부품명번호'); iit = tbl.get(str(icode)) or {}
    src = m.full_text(r)
    dl = [ln.strip()[:120] for ln in src.split('\n') if '직접생산' in ln][:2]
    print(f"--- {i} {r['meta']['업무구분']} {float(r['meta']['입찰추정가격']):,.0f} | title={m.title_of(r)[:60]!r}")
    print(f"    meta품목={str(r['meta'].get('세부품명번호목록'))[:60]} | 본호출={code} {it.get('name','')} | 품목호출={icode} {iit.get('name','')} | rx코드={rx.get('계약목적물_세부품명번호')}")
    print(f"    직생 줄: {dl}")
