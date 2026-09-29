"""기업규모 파서가 고른 근거 줄이 제한을 부정하는 문장('제한하지 않습니다', '시행하지 않습니다', '비대상', '관련 없습니다')인 공고."""
import sys, gzip, json, re, importlib.util
from multiprocessing import Pool
M = TBL = None
NEG = re.compile(r"(제한|실시|시행|적용|운영|진행)\s*하지\s*(않|아니)|제한\s*(을|를)?\s*(두지|하지)\s*않|비\s*대상|관련\s*(이\s*)?없|해당\s*(하지|되지)\s*않|제한\s*없|제한이\s*없|하지\s*아니한다")
def init(p):
    global M, TBL
    s = importlib.util.spec_from_file_location('m', p); M = importlib.util.module_from_spec(s); s.loader.exec_module(M)
    TBL = M.load_competitive_table('open/data')
def work(line):
    r = M.normalize(json.loads(line))
    lv, ev = M.rx_sme_level(r)
    if lv == "없음" or not NEG.search(ev): return None
    h = M.decide(r, "", TBL)[0]
    p = M.price(r) or 0
    return r['id'], lv, ev[:220], p, r['meta'].get('계약방법'), M.has_procurement_exception(M.full_text(r)), M.meta_exception(r), {k: h[k] for k in ('v11','v14','v15','v16','v17','v18') if h[k]}
if __name__ == '__main__':
    L = gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8').readlines()
    with Pool(8, initializer=init, initargs=(sys.argv[1],)) as pool:
        res = [x for x in pool.map(work, L, chunksize=100) if x]
    import collections
    print('negated evidence notices', len(res))
    c = collections.Counter(('lt1' if p < 1e8 else 'mid' if p < 2.3e8 else 'ge', m, e or me) for _, _, _, p, m, e, me, _ in res)
    for k, v in sorted(c.items(), key=str): print(k, v)
    for x in res[:60]: print(x[0], x[1], x[3], x[4], 'exc', x[5], x[6], x[7], '|', x[2][:170])
