"""v24 계약방법 축: 공고서가 스스로 밝힌 계약방법(머리말 줄)과 meta 계약방법 비교."""
import json, csv, re, sys, pickle
from collections import Counter
sys.path.insert(0, "runs/r18_20260928")
METH_LINE = re.compile(r"(계\s*약\s*방\s*법|입\s*찰\s*방\s*법|경\s*쟁\s*형\s*태|입\s*찰\s*방\s*식|계\s*약\s*방\s*식)\s*[:：|]\s*([^\n]{0,60})")
KIND = re.compile(r"(일반\s*경쟁|제한\s*경쟁|지명\s*경쟁|수의\s*계약)")
def text_methods(r):
    out = []
    for d in r["docs"]:
        for ln in d["text"].split("\n"):
            m = METH_LINE.search(ln)
            if m:
                k = KIND.findall(m.group(2))
                if k:
                    out.append((re.sub(r"\s", "", k[0]), ln.strip()[:120]))
    return out
def mismatch(r):
    mm = str(r["meta"].get("계약방법") or "")
    tm = text_methods(r)
    if not tm or not mm: return None
    kinds = {k for k, _ in tm}
    if mm not in kinds:
        return tm
    return None
if __name__ == "__main__":
    lab = {x['id']: x for x in csv.DictReader(open('open/dev_labels.csv'))}
    for ln in open('open/dev.jsonl'):
        r = json.loads(ln)
        mt = mismatch(r)
        if mt:
            print(r['id'], 'v24', lab[r['id']]['v24'], 'meta', r['meta'].get('계약방법'), mt[:2])
    if len(sys.argv) > 1:
        from load20k import load
        recs = load(); c = Counter(); ex = []
        for r in recs:
            mt = mismatch(r)
            if mt:
                c[(r['meta'].get('계약방법'), mt[0][0])] += 1; ex.append((r['id'], r['meta'].get('계약방법'), mt[0][1]))
        print(sum(c.values()), c.most_common(12))
        import random; random.seed(3)
        for e in random.sample(ex, min(30, len(ex))): print(e)
