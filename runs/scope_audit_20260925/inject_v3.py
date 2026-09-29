import json, gzip, random, re, sys, copy, importlib.util
def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
mods = [load(p, f'm{i}') for i, p in enumerate(sys.argv[1:])]
tbl = mods[0].load_competitive_table('open/data')
S = [
 "최근 3년 이내 단일 계약금액 기준 본 사업 예산 이상의 유사 용역 수행실적이 있는 업체",
 "입찰공고일 기준 최근 5년간 추정가격의 1.5배 이상의 동종 실적을 보유한 자",
 "공고일 전일 기준 최근 3년 이내 기초금액 이상 규모의 유사사업 실적이 있는 업체이어야 합니다.",
 "나. 최근 5년 이내 사업예산의 100% 이상 단일 용역 이행실적이 있는 업체",
 "- 단일건 실적금액이 이번 사업 금액 이상인 업체에 한함",
 "최근 3년간 배정예산액 이상의 납품실적이 있는 자",
 "라. 입찰공고금액의 2배 이상 수행실적이 있는 업체",
 "본 용역 추정가격 이상의 동일 용역 실적을 보유한 업체만 참가 가능",
 "마. 최근 5년 이내 단일 건으로 사업비 이상의 행사 대행 실적이 있는 업체이어야 함",
 "공고일 기준 최근 3년 이내 해당 사업 기초금액의 120% 이상 실적을 보유한 자",
]
rng = random.Random(3); base = []
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r.get('dropped_doc_counts') or not any(d['type'] == '공고문' for d in r['docs']): continue
    base.append(r)
rng.shuffle(base); base = base[:4000]
def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r['docs']:
        if d['type'] != '공고문': continue
        lines = d['text'].split('\n')
        k = next((i for i, l in enumerate(lines) if re.search(r'참가\s*자격', l)), None)
        if k is None: k = min(len(lines) - 1, len(lines) // 3)
        lines.insert(k + 1, sent); d['text'] = '\n'.join(lines); break
    return r
picked = []
for r in base:
    if len(picked) >= 8: break
    try: p = float(r['meta'].get('입찰추정가격') or 0)
    except: p = 0
    if p < 1e7: continue
    if not mods[0].decide(r, '', tbl)[0]['v3']: picked.append(r)
tot = [0] * len(mods)
for s in S:
    hits = []
    for mi, m in enumerate(mods):
        h = sum(m.decide(inject(b, s), '', tbl)[0]['v3'] for b in picked); hits.append(h); tot[mi] += h
    print(hits, '/', len(picked), '|', s)
print('total', tot, '/', len(picked) * len(S))
