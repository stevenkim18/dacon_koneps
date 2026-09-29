"""같은 양식(줄 Jaccard>=0.7)·같은 계약법·업무·계약방법·금액 구간인데 판정이 갈리는 무라벨 묶음을 항목별로 보여 준다.
  python runs/int8_port_20260923/template_audit.py SCRIPT.py ITEM [최대 묶음 수]
묶음은 template_clusters.py가 만든 _cache/incons_examples.pkl."""
import sys, json, gzip, re, hashlib, collections, pickle, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import devtool as D
WS = re.compile(r'\s+')
def load_recs(ids):
    out = {}
    with gzip.open(D.ROOT/'open/train_unlabeled.jsonl.gz','rt',encoding='utf-8') as f:
        for l in f:
            r = json.loads(l)
            if r['id'] in ids: out[r['id']] = r
    return out
def main(script, item, maxg=12, examples=None):
    ex = pickle.load(open(examples,'rb'))
    groups = ex.get(item, [])[:maxg]
    ids = {i for _, mem in groups for i, _ in mem}
    recs = load_recs(ids)
    m = D.load_mod(script); tbl = m.load_competitive_table(str(D.ROOT/'open/data'))
    for key, mem in groups:
        print(f'######## {item} group {key}')
        lsets = {}
        for i, p in mem:
            r = recs[i]; rx = m.regex_facts(r, tbl)
            hits, evid, _ = m.decide(r, '', tbl)
            mm = r['meta']
            print(f"  [{p}] {i} 추정={mm.get('입찰추정가격')} 소관={mm.get('소관구분')} 품명={str(mm.get('세부품명번호목록'))[:40]} 조항호={str(mm.get('조항호내용'))[:40]} 지역={mm.get('지역제한여부')}/{str(mm.get('제한지역코드목록'))[:20]}")
            print(f"       level={rx.get('기업규모_제한')} ev={str(rx.get('기업규모_근거'))[:110]!r}")
            print(f"       code={rx.get('계약목적물_세부품명번호')} comp={m.is_competitive(rx, r, tbl)} exc={rx.get('우선조달_예외사유_기재')} 직생={rx.get('직접생산확인_요구')} region={rx.get('지역제한')} 단위={rx.get('지역_단위')} 시도={rx.get('지역_시도목록')} e={str(evid.get(item,''))[:80]!r}")
            lsets[i] = {WS.sub(' ', ln).strip() for d in r['docs'] for ln in d['text'].split('\n') if len(WS.sub('', ln)) >= 8}
        a, b = mem[0][0], next((i for i, p in mem if p != mem[0][1]), None)
        if b:
            da = sorted(lsets[a] - lsets[b], key=len)[:6]; db = sorted(lsets[b] - lsets[a], key=len)[:6]
            print(f'   only in {a}:', [x[:90] for x in da])
            print(f'   only in {b}:', [x[:90] for x in db])
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12, sys.argv[4] if len(sys.argv) > 4 else
         str(Path(__file__).resolve().parent / '_cache' / 'incons_examples.pkl'))
