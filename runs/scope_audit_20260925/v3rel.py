import json, gzip, re, importlib.util, sys
from collections import Counter
spec = importlib.util.spec_from_file_location('m', 'submissions/20260926_phrase_parser_recall/script.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
tbl = m.load_competitive_table('open/data')
REL = re.compile(r"(기초\s*금액|추정\s*가격|사업\s*예산|사업비|사업\s*금액|계약\s*금액|예산\s*액|배정\s*예산|본\s*(사업|용역|건)\s*(규모|금액)|발주\s*금액|용역\s*금액|설계\s*금액)[^\n]{0,20}?(이상|\d+(\.\d+)?\s*배|\d+\s*%)")
MUL = re.compile(r"(\d+(\.\d+)?)\s*배\s*(수)?\s*이상|(\d{2,3})\s*%\s*이상")
hits = Counter(); ex = []
n = 0
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l); n += 1
    for d in r['docs']:
        for ln in d['text'].split('\n'):
            if '실적' not in ln or not re.search(r'이상', ln): continue
            if not (REL.search(ln) or MUL.search(ln)): continue
            if m.EVAL_CONTEXT_RE.search(ln) or re.search(r'\d+\s*부\b|서식|제출\s*서류|우대|선호|평가|배점|점\)', ln): continue
            h = m.decide(r, '', tbl)[0]
            hits['v3' if h['v3'] else 'no_v3'] += 1
            if len(ex) < 60: ex.append((r['id'], h['v3'], h['v2'], r['meta']['입찰추정가격'], ln.strip()[:230]))
            break
print(n, hits)
for e in ex: print(e)
