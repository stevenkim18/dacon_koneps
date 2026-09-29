"""무라벨 20,000건을 양식이 거의 같은 공고끼리 묶고(줄 단위 Jaccard >= 0.7), 같은 묶음·같은 계약법·업무·계약방법·금액 구간인데
후보 판정이 갈리는 곳을 항목별로 모은다. 결과는 _cache/에 저장해 template_audit.py·template_brittle.py가 읽는다.
  python template_clusters.py SCRIPT.py          (SCRIPT의 무라벨 재생 캐시가 없으면 먼저 scripts/replay_unlabeled.py를 돌린다)"""
import sys, json, gzip, re, hashlib, collections, pickle
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = HERE / '_cache'
WS = re.compile(r'\s+')
ITEMS = [f'v{i}' for i in range(1, 25)]
def band(p):
    try: p = float(p)
    except (TypeError, ValueError): return 'NA'
    return '<1억' if p < 1e8 else '<2.3억' if p < 2.3e8 else '<3.5억' if p < 3.5e8 else '<5억' if p < 5e8 else '>=5억'
def main(script):
    h = hashlib.md5(Path(script).read_bytes()).hexdigest()[:10]
    cands = sorted((ROOT / 'runs' / 'replay_cache').glob(f'*_{h}.pkl'))
    if not cands:
        sys.exit(f'재생 캐시 없음: python scripts/replay_unlabeled.py {script} 를 먼저 돌린다')
    pred = pickle.load(open(cands[0], 'rb'))
    lines_of, meta = {}, {}
    with gzip.open(ROOT / 'open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8') as f:
        for l in f:
            r = json.loads(l)
            lines_of[r['id']] = {hashlib.md5(WS.sub('', ln).encode()).digest()[:8]
                                 for d in r['docs'] for ln in d['text'].split('\n') if len(WS.sub('', ln)) >= 25}
            m = r['meta']; meta[r['id']] = (m.get('적용계약법'), m.get('업무구분'), m.get('계약방법'), m.get('입찰추정가격'))
    df = collections.Counter()
    for ls in lines_of.values(): df.update(ls)
    groups = collections.defaultdict(list)
    for i, ls in lines_of.items():
        for _, hh in sorted((df[x], x) for x in ls if 2 <= df[x] <= 300)[:3]:
            groups[hh].append(i)
    parent = {}
    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x]); x = parent[x]
        return x
    for ids in groups.values():
        if not 2 <= len(ids) <= 300: continue
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                A, B = lines_of[ids[a]], lines_of[ids[b]]
                k = len(A & B)
                if k and k / (len(A) + len(B) - k) >= 0.7:
                    ra, rb = find(ids[a]), find(ids[b])
                    if ra != rb: parent[ra] = rb
    clusters = collections.defaultdict(list)
    for i in lines_of: clusters[find(i)].append(i)
    multi = [v for v in clusters.values() if len(v) >= 2]
    ex, incons, ng = collections.defaultdict(list), collections.Counter(), 0
    for c in multi:
        sub = collections.defaultdict(list)
        for i in c:
            a, u, k, p = meta[i]; sub[(a, u, k, band(p))].append(i)
        for key, ids in sub.items():
            if len(ids) < 2: continue
            ng += 1
            for j, v in enumerate(ITEMS):
                vals = [pred[i][j] for i in ids if pred.get(i)]
                if len(set(vals)) > 1:
                    incons[v] += 1; ex[v].append((key, [(i, pred[i][j]) for i in ids]))
    CACHE.mkdir(exist_ok=True)
    pickle.dump({'clusters': multi, 'meta': meta}, open(CACHE / 'clusters20k.pkl', 'wb'))
    pickle.dump(dict(ex), open(CACHE / 'incons_examples.pkl', 'wb'))
    print(f'묶음 {len(multi)}개 · 묶인 공고 {sum(map(len, multi))}건 · 같은 양식·같은 구간 그룹 {ng}개')
    print('판정이 갈린 그룹(항목별):', dict(sorted(incons.items(), key=lambda x: -x[1])))
if __name__ == '__main__':
    main(sys.argv[1])
