"""무라벨 20,000에서 기업규모 낱말이 '입찰방식 요약 줄 + 서류 목록·상투문'에만 있는 공고(일반화한 머리말 전용)를 센다."""
import sys, gzip, json, re, importlib.util
from multiprocessing import Pool
sys.path.insert(0, 'runs/del_probe_20260928')
M = None
W = re.compile(r"소기업|소상공인|중소기업|중기업")
def init(p):
    global M
    s = importlib.util.spec_from_file_location('m', p); M = importlib.util.module_from_spec(s); s.loader.exec_module(M)
    import sme_delete as SD; SD.M = M
    globals()['SD'] = SD
def work(line):
    r = M.normalize(json.loads(line))
    lv, ev = M.rx_sme_level(r)
    if lv == "없음": return None
    lines = [ln.strip() for d in r['docs'] for ln in d['text'].split('\n') if W.search(ln)]
    body = [ln for ln in lines if not SD.keep_line(ln)]
    if body: return None
    p = M.price(r) or 0
    return r['id'], lv, ev[:160], p, r['meta'].get('계약방법'), M.has_procurement_exception(M.full_text(r)) or M.meta_exception(r)
if __name__ == '__main__':
    L = gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8').readlines()
    with Pool(8, initializer=init, initargs=(sys.argv[1],)) as pool:
        res = [x for x in pool.map(work, L, chunksize=100) if x]
    import collections
    c = collections.Counter(('lt1' if p < 1e8 else 'mid' if p < 2.3e8 else 'ge', m, e) for _, _, _, p, m, e in res)
    for k, v in sorted(c.items(), key=str): print(k, v)
    for x in res[:40]: print(x)
