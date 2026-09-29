import json, gzip, random, re, sys, copy, importlib.util
from datetime import timedelta
def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
mods = [load(p, f'm{i}') for i, p in enumerate(sys.argv[1:])]
m0 = mods[0]; tbl = m0.load_competitive_table('open/data')
WD = '월화수목금토일'
FMT = [
 lambda d: f"마. 사업설명회 : {d.year}. {d.month}. {d.day}.({WD[d.weekday()]}) 14:00, 발주기관 회의실",
 lambda d: f"사업설명회 일시: {d.year}년 {d.month}월 {d.day}일 오후 2시",
 lambda d: f"제안요청 설명회는 {d.month}월 {d.day}일({WD[d.weekday()]}) 15:00에 개최합니다.",
 lambda d: f"과업설명회 개최 — {d.year}-{d.month:02d}-{d.day:02d} 10:00, 수요기관 대회의실",
 lambda d: f"현장설명회: {d.month}월 {d.day}일 14시 (장소: 발주기관 소회의실)",
 lambda d: f"사업설명회 개최(일시: '{d.year % 100}. {d.month}. {d.day}. 14:00)",
 lambda d: f"설명회 일정 : {d.month}. {d.day}. 14:00",
 lambda d: f"제안설명회 일시 {d.year}.{d.month:02d}.{d.day:02d}(목) 오전 10시",
]
rng = random.Random(5); base = []
for l in gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8'):
    r = json.loads(l)
    if r['meta'].get('적용계약법') != '지방계약법' or '협상' not in str(r['meta'].get('낙찰방법')): continue
    if r.get('dropped_doc_counts'): continue
    base.append(r)
rng.shuffle(base)
picked = []
for r in base:
    if len(picked) >= 10: break
    b, dl, _ = m0.rx_briefing(r)
    if dl and not b and not m0.decide(r, '', tbl)[0]['v23']: picked.append((r, dl))
print('bases', len(picked))
def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r['docs']:
        if d['type'] != '공고문': continue
        lines = d['text'].split('\n'); k = min(len(lines) - 1, 5)
        lines.insert(k, sent); d['text'] = '\n'.join(lines); break
    return r
tot = [0] * len(mods)
for fi, f in enumerate(FMT):
    hits = [0] * len(mods)
    for r, dl in picked:
        s = f(dl - timedelta(days=5))
        for mi, m in enumerate(mods):
            hits[mi] += m.decide(inject(r, s), '', tbl)[0]['v23']
    for mi in range(len(mods)): tot[mi] += hits[mi]
    print(hits, '/', len(picked), '|', FMT[fi](picked[0][1] - timedelta(days=5)))
print('total', tot, '/', len(picked) * len(FMT))
