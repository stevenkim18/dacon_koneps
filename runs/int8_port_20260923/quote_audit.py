import gzip, json, re, unicodedata, sys, collections
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import devtool as D
m = D.load_mod(str(D.ROOT/'submissions/20260924_v20_quote_region35/script.py'))
recs = {}
for l in gzip.open(D.ROOT/'open/exp950.jsonl.gz','rt',encoding='utf-8'):
    r = json.loads(l); recs[r['id']] = r
WS = re.compile(r'\s+')
PFX = re.compile(r'^\s*[\(\[【<]?\s*(공고문|규격서|과업지시서|제안요청서|예외공표서|첨부|문서\s*\d*)\s*[\)\]】>]?\s*[-:·]?\s*')
def status(q, src, srcn):
    q = unicodedata.normalize('NFC', str(q)).replace('\r','').strip()
    if not q: return None
    if q in src: return 'exact'
    lines = [x.strip() for x in q.split('\n') if x.strip()]
    if lines and all(x in src for x in lines): return 'lines'
    q2 = PFX.sub('', q)
    if q2 and q2 in src: return 'prefix'
    qn = WS.sub('', q2)
    if len(qn) >= 6 and qn in srcn: return 'ws'
    # quote marks / ellipsis
    q3 = q2.strip('"\'“”‘’「」 ').replace('…','').replace('...','')
    if len(WS.sub('',q3))>=6 and WS.sub('',q3) in srcn: return 'ws'
    return 'miss'
def audit(path, keyfilter):
    c = collections.Counter(); ex = collections.defaultdict(list)
    for l in open(path, encoding='utf-8'):
        o = json.loads(l); r = recs.get(o['id'])
        if not r: continue
        f = m.parse_facts(o.get('text','')) or {}
        src = m.full_text(r); srcn = WS.sub('', src)
        for k,v in f.items():
            if not keyfilter(k) or not v: continue
            vals = v if isinstance(v, list) else [v]
            for q in vals:
                if not isinstance(q, str): continue
                s = status(q, src, srcn)
                if s: 
                    c[(k,s)] += 1
                    if s in ('prefix','ws','miss') and len(ex[(k,s)])<3: ex[(k,s)].append((o['id'], q[:120]))
    return c, ex
if __name__ == '__main__':
    kf = lambda k: k.endswith('근거') or k.endswith('인용')
    for name, path in [('int8 main', D.ROOT/'runs/cloud_int8_exp/exp/raw/main.jsonl'), ('int8 sme', D.ROOT/'runs/cloud_int8_exp/exp/raw/sme.jsonl'),
                       ('int8 region', D.ROOT/'runs/cloud_int8_exp/exp/raw/region.jsonl')]:
        c, ex = audit(path, kf)
        keys = sorted({k for k,_ in c})
        print('=====', name)
        for k in keys:
            row = {s: c[(k,s)] for s in ['exact','lines','prefix','ws','miss'] if c[(k,s)]}
            print(f'  {k:16s}', row)
        for (k,s),v in ex.items():
            if s!='miss': print('   ex', k, s, v[:2])
