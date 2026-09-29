"""두 후보 스크립트의 판정·근거 차이를 저장 출력 전부(dev 4bit·int8 2회, 무라벨 750 4bit·int8)에서 공고 단위로 뽑는다.
  python runs/int8_port_20260923/fulldiff.py BASE.py PORT.py
"""
import sys, json, gzip, csv, glob, collections, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import devtool as D
R = D.ROOT
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8')]
dev = jl(R/'open/dev.jsonl')
u750 = jl(R/'runs/mlx/train_sample250.jsonl') + jl(R/'runs/mlx/train_sample500_next.jsonl')
exp = [json.loads(l) for l in gzip.open(R/'open/exp950.jsonl.gz','rt',encoding='utf-8')]
def cat(*ps):
    import tempfile
    out = Path(tempfile.gettempdir())/('konepps_cat_' + '_'.join(Path(p).stem for p in ps) + '.jsonl')
    if not out.exists():
        with open(out, 'w', encoding='utf-8') as f:
            for p in ps:
                f.write(open(R/p, encoding='utf-8').read())
    return out
SETS = {
 'dev·4bit': (dev, dict(main=R/'runs/mlx/extract_outputs.jsonl', item=R/'runs/mlx/item_outputs.jsonl', model=R/'runs/mlx/model_outputs.jsonl',
                        sme=R/'runs/mlx/v21_sme_dev.jsonl', region=R/'runs/mlx/v22_region_dev.jsonl')),
 'dev·int8①': (dev, {k: R/f'runs/cloud_int8_20260923/dev/raw/{k}.jsonl' for k in ['main','item','model','sme','region']}),
 'dev·int8②': (dev, {k: R/f'runs/cloud_int8_exp/exp/raw/{k}.jsonl' for k in ['main','item','model','sme','region']}),
 '750·4bit': (u750, {k: cat(f'runs/mlx/train250_{k}.jsonl', f'runs/mlx/train500_{k}.jsonl') for k in ['main','item','model','sme','region']}),
 '750·int8': ([r for r in exp if not r['id'].startswith('PPS-DEV')], {k: R/f'runs/cloud_int8_exp/exp/raw/{k}.jsonl' for k in ['main','item','model','sme','region']}),
}
def labels():
    lab = {}
    for p in glob.glob(str(R/'labels/*.csv')):
        for row in csv.DictReader(open(p, encoding='utf-8')):
            if row.get('label') in ('0','1') and 'item' in row:
                lab[(row['id'], row['item'])] = row['label']
    for i, r in D.labels().items():
        for v in D.ITEMS: lab[(i, v)] = r[v]
    return lab
def main(a, b):
    lab = labels()
    ABS = {'v10','v11','v16','v18','v20'}
    for name, (recs, raw) in SETS.items():
        t0 = time.time(); ma, _, oa = D.run(a, recs=recs, raw=raw); ta = time.time() - t0
        t0 = time.time(); mb, _, ob = D.run(b, recs=recs, raw=raw); tb = time.time() - t0
        src = {r['id']: mb.full_text(r) for r in recs}
        ch, evch, bad = [], 0, []
        for i in oa:
            (ha, ea), (hb, eb) = oa[i], ob[i]
            for v in D.ITEMS:
                if ha[v] != hb[v]:
                    ch.append((i, v, hb[v] - ha[v], lab.get((i, v), '-'), (eb.get(v) or ea.get(v) or '')[:90]))
                if hb[v] and (ea.get(v) or '') != (eb.get(v) or ''):
                    evch += 1
                if hb[v] and v not in ABS:
                    e = eb.get(v) or ''
                    if e and (e not in src[i] or len(e) > 500): bad.append((i, v))
        cnt = collections.Counter((d, l) for _, _, d, l, _ in ch)
        print(f"== {name}: 판정 변경 {len(ch)}건 {dict(cnt)} · 근거 문구 변경 {evch}건 · 근거 요건 위반 {len(bad)}건 · 시간 {ta:.1f}s→{tb:.1f}s")
        for i, v, d, l, e in sorted(ch, key=lambda x: (x[1], x[0])):
            print(f"    {'+' if d > 0 else '-'}{v:<4} {i:<14} label={l}  {e!r}")
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
