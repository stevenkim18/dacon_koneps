"""Diff two candidate scripts over the 750 unlabeled int8 outputs (and dev), print changes with hand labels."""
import sys, json, gzip, csv, glob, collections
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import devtool as D
S=str(__import__('pathlib').Path(__file__).resolve().parent)
def main(a, b, which='750', show=True):
    recs = [json.loads(l) for l in gzip.open(D.ROOT/'open/exp950.jsonl.gz','rt',encoding='utf-8')]
    recs = [r for r in recs if (not r['id'].startswith('PPS-DEV')) == (which=='750')]
    RAW = {k: D.ROOT/f'runs/cloud_int8_exp/exp/raw/{k}.jsonl' for k in ['main','item','model','sme','region']}
    _, _, oa = D.run(a, recs=recs, raw=RAW)
    _, _, ob = D.run(b, recs=recs, raw=RAW)
    lab = {}
    for p in glob.glob(str(D.ROOT/'labels/*.csv')):
        for row in csv.DictReader(open(p, encoding='utf-8')):
            if row.get('label') in ('0','1') and 'item' in row:
                lab[(row['id'], row['item'])] = (row['label'], (row.get('reason') or '')[:100])
    if which == 'dev':
        dl = D.labels()
        for i in dl:
            for v in D.ITEMS: lab[(i,v)] = (dl[i][v], 'dev')
    d = collections.Counter(); rows=[]
    R = {r['id']: r for r in recs}
    for i in oa:
        ha, ea = oa[i]; hb, eb = ob[i]
        for v in D.ITEMS:
            if ha[v] != hb[v]:
                d[v] += hb[v]-ha[v]; rows.append((i, v, hb[v]-ha[v], lab.get((i,v)), eb.get(v,'') or ea.get(v,'')))
    print(which, 'Δ by item', dict(d), 'total', sum(d.values()), '| labelled:', collections.Counter((dd, l[0]) for _,_,dd,l,_ in rows if l))
    if show:
        for i,v,dd,l,e in sorted(rows, key=lambda x:(int(x[1][1:]),x[0])):
            mm = R[i]['meta']
            print(f"{'+' if dd>0 else '-'}{v} {i} {mm.get('업무구분')} {mm.get('계약방법')} 추정={mm.get('입찰추정가격')} label={l[0] if l else '-'} {('('+l[1]+')') if l else ''}")
            print(f"     ev: {str(e)[:180]!r}")
    return oa, ob
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv)>3 else '750')
