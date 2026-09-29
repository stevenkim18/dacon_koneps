"""같은 양식 묶음에서 판정이 갈린 쌍마다, 판정을 가른 사실이 '원문이 실제로 다름'인지 '같은 원문을 다르게 읽음'인지 분류한다.
  python runs/int8_port_20260923/template_brittle.py SCRIPT.py
항목별로: 판정이 다른 쌍 수, 그중 항목 관련 줄(사실 근거 줄)이 양쪽 원문에 똑같이 있는 쌍 수(= 규칙 흔들림 후보)."""
import sys, json, gzip, re, collections, pickle
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import devtool as D
S = str(Path(__file__).resolve().parent / '_cache')
WS = re.compile(r'\s+')
EVK = {'v2':'실적_근거','v3':'실적_근거','v4':'실적_근거','v5':'지역_근거','v6':'지역_근거','v7':'지역_근거','v8':'지역_근거',
       'v12':'기업규모_근거','v13':'기업규모_근거','v14':'기업규모_근거','v15':'기업규모_근거','v16':'기업규모_근거','v17':'기업규모_근거','v18':'기업규모_근거',
       'v10':None,'v11':'기업규모_근거','v20':None}
def main(script):
    ex = pickle.load(open(S + '/incons_examples.pkl', 'rb'))
    ids = {i for groups in ex.values() for _, mem in groups for i, _ in mem}
    recs = {}
    with gzip.open(D.ROOT/'open/train_unlabeled.jsonl.gz','rt',encoding='utf-8') as f:
        for l in f:
            r = json.loads(l)
            if r['id'] in ids: recs[r['id']] = r
    m = D.load_mod(script); tbl = m.load_competitive_table(str(D.ROOT/'open/data'))
    facts = {i: m.regex_facts(r, tbl) for i, r in recs.items()}
    norm = {i: WS.sub('', m.full_text(r)) for i, r in recs.items()}
    out = collections.defaultdict(collections.Counter); samples = collections.defaultdict(list)
    for item, groups in ex.items():
        for key, mem in groups:
            pos = [i for i, p in mem if p]; neg = [i for i, p in mem if not p]
            for a in pos:
                for b in neg:
                    fa, fb = facts[a], facts[b]
                    k = EVK.get(item)
                    # what differs
                    diff = [f for f in ('기업규모_제한','계약목적물_세부품명번호','직접생산확인_요구','직접생산_언급_넓게','우선조달_예외사유_기재','지역제한','지역_단위','지역_시도목록','실적제한','실적_발주처_공공한정') if fa.get(f) != fb.get(f)]
                    ev = str(fa.get(k) or '') if k else ''
                    same_text = bool(ev) and WS.sub('', ev) in norm[b]
                    kind = 'same-evidence-in-both' if same_text else ('meta/amount' if not diff else 'text differs')
                    out[item][kind] += 1
                    if same_text and len(samples[item]) < 3: samples[item].append((a, b, diff, ev[:100]))
    for item in sorted(out, key=lambda v: int(v[1:])):
        print(item, dict(out[item]))
        for s in samples[item]: print('     ', s)
if __name__ == '__main__':
    main(sys.argv[1])
