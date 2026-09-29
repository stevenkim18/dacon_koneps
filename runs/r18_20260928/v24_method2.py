"""v24 계약방법 축(정제): 공고서 머리말 줄('입찰방법:', '계약방법:', '경쟁형태:', '입찰방식:')이 밝힌 경쟁 종류 집합에 meta 계약방법이 없는 공고."""
import json, csv, re, sys, pickle, random
from collections import Counter
sys.path.insert(0, "runs/r18_20260928")
METH_LINE = re.compile(r"(계\s*약\s*방\s*법|입\s*찰\s*방\s*법|경\s*쟁\s*형\s*태|입\s*찰\s*방\s*식|계\s*약\s*방\s*식|입\s*찰\s*및\s*계\s*약\s*방\s*(법|식))\s*[:：|]\s*([^\n]{0,80})")
KIND = re.compile(r"(일반\s*경쟁|제한\s*경쟁|지명\s*경쟁|수의|제한\s*입찰|일반\s*입찰)")
NORM = {"일반경쟁": "일반경쟁", "일반입찰": "일반경쟁", "제한경쟁": "제한경쟁", "제한입찰": "제한경쟁", "지명경쟁": "지명경쟁", "수의": "수의계약"}
def text_kinds(r):
    out = []
    for d in r["docs"]:
        for ln in d["text"].split("\n"):
            for m in METH_LINE.finditer(ln):
                ks = {NORM[re.sub(r"\s", "", k)] for k in KIND.findall(m.group(3))}
                if ks: out.append((ks, ln.strip()[:120]))
    return out
def mismatch(r):
    mm = str(r["meta"].get("계약방법") or "")
    tk = text_kinds(r)
    if not tk or not mm: return None
    allk = set().union(*[k for k, _ in tk])
    if mm in allk: return None
    return tk[0]
if __name__ == "__main__":
    lab = {x['id']: x for x in csv.DictReader(open('open/dev_labels.csv'))}
    for ln in open('open/dev.jsonl'):
        r = json.loads(ln); mt = mismatch(r)
        if mt:
            g = [k for k in lab[r['id']] if k.startswith('v') and lab[r['id']][k] == '1']
            print(r['id'], 'v24', lab[r['id']]['v24'], 'gold', g, 'meta', r['meta'].get('계약방법'), mt[1][:90])
    if len(sys.argv) > 1:
        from load20k import load
        recs = load(); c = Counter(); ex = []
        for r in recs:
            mt = mismatch(r)
            if mt:
                c[(r['meta'].get('계약방법'), tuple(sorted(mt[0])))] += 1; ex.append((r['id'], r['meta'].get('계약방법'), mt[1]))
        print(len(ex), c.most_common(10))
        random.seed(11)
        for e in random.sample(ex, min(40, len(ex))): print(e)
