"""v24 금액 축(정규식): 공고서가 '추정가격'·'배정예산/예산액'이라고 이름 붙인 금액이 meta 값과 다른지."""
import json, csv, re, sys, importlib.util
from collections import Counter
sys.path.insert(0, "runs/r18_20260928")
spec = importlib.util.spec_from_file_location("m", "submissions/20260929_r17_edit_shapes/script.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
AMT = r"금?\s*([\d,]{5,})\s*원"
EST_RE = re.compile(r"추\s*정\s*가\s*격\s*(?:\(?[^\d\n]{0,12}\)?)?\s*[:：|]?\s*" + AMT)
BUD_RE = re.compile(r"(?:배\s*정\s*예\s*산|예\s*산\s*액|사\s*업\s*예\s*산|소\s*요\s*예\s*산|총\s*사\s*업\s*비|사\s*업\s*비|용\s*역\s*금\s*액|예\s*산\s*금\s*액)\s*(?:\(?[^\d\n]{0,12}\)?)?\s*[:：|]?\s*" + AMT)
def vals(r):
    m = r["meta"]; out = []
    for k in ("배정예산금액", "입찰추정가격"):
        try: out.append(float(m.get(k)))
        except (TypeError, ValueError): pass
    return out
def near(a, xs):
    for x in xs:
        for f in (1.0, 1.1, 1 / 1.1):
            if abs(a - x * f) <= max(1000, x * 0.002): return True
    return False
def check(r):
    xs = vals(r)
    if not xs or max(xs) < 1e6: return None
    for d in r["docs"]:
        for ln in d["text"].split("\n"):
            for rx, kind in ((EST_RE, "est"), (BUD_RE, "bud")):
                for mm in rx.finditer(ln):
                    try: a = float(mm.group(1).replace(",", ""))
                    except ValueError: continue
                    if a < 1e6: continue
                    if not near(a, xs):
                        return (kind, int(a), [int(x) for x in xs], ln.strip()[:140])
    return None
if __name__ == "__main__":
    lab = {x['id']: x for x in csv.DictReader(open('open/dev_labels.csv'))}
    for ln in open('open/dev.jsonl'):
        r = json.loads(ln); c = check(r)
        if c or lab[r['id']]['v24'] == '1': print(r['id'], 'v24', lab[r['id']]['v24'], c)
    if len(sys.argv) > 1:
        from load20k import load
        recs = load(); hits = [(r['id'], check(r)) for r in recs]; hits = [h for h in hits if h[1]]
        print(len(hits), Counter(h[1][0] for h in hits))
        import random; random.seed(4)
        for h in random.sample(hits, min(25, len(hits))): print(h)
