import json, gzip, re, importlib.util
spec = importlib.util.spec_from_file_location('m', 'submissions/20260927_sme_sentence_v17/script.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
tbl = m.load_competitive_table('open/data')
PAT = re.compile(r"(유사\s*(한\s*)?(실적|용역|사업|공사|물품)[^\n]{0,15}(인정\s*하지|인정\s*안|불인정|제외|배제|해당\s*없|인정\s*불가))"
                 r"|((동일|같은)\s*(명칭|이름|사업명|용역명)[^\n]{0,20}실적\s*만)"
                 r"|(실적\s*만\s*(을\s*)?인정)")
n = 0; ex = []
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    for d in r['docs']:
        for ln in d['text'].split('\n'):
            if '실적' in ln and PAT.search(ln):
                n += 1
                if len(ex) < 40:
                    h = m.decide(r, '', tbl)[0]
                    ex.append((r['id'], r['meta']['입찰추정가격'], h['v4'], h['v2'], ln.strip()[:200]))
                break
        else: continue
        break
print('notices', n)
for e in ex: print(e)
