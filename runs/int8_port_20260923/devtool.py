"""Scratch helper: run a candidate script's decide() over dev with saved raw outputs; return hits/evidence."""
import json, csv, importlib.util, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ITEMS = [f"v{i}" for i in range(1, 25)]

def load_mod(path):
    spec = importlib.util.spec_from_file_location("cand_" + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def load_saved(p):
    d = {}
    if p and Path(p).exists():
        for l in open(p, encoding='utf-8'):
            r = json.loads(l); d[r['id']] = r.get('text', '')
    return d

RAW = {
 'int8': dict(main=ROOT/'runs/cloud_int8_20260923/dev/raw/main.jsonl', item=ROOT/'runs/cloud_int8_20260923/dev/raw/item.jsonl',
              model=ROOT/'runs/cloud_int8_20260923/dev/raw/model.jsonl', sme=ROOT/'runs/cloud_int8_20260923/dev/raw/sme.jsonl',
              region=ROOT/'runs/cloud_int8_20260923/dev/raw/region.jsonl'),
 'b4': dict(main=ROOT/'runs/mlx/extract_outputs.jsonl', item=ROOT/'runs/mlx/item_outputs.jsonl', model=ROOT/'runs/mlx/model_outputs.jsonl',
            sme=ROOT/'runs/mlx/v21_sme_dev.jsonl', region=ROOT/'runs/mlx/v22_region_dev.jsonl'),
}

def dev_records(m):
    return list(m.iter_records(str(ROOT/'open/dev.jsonl')))

def labels():
    return {r['id']: r for r in csv.DictReader(open(ROOT/'open/dev_labels.csv', encoding='utf-8'))}

def run(script, which='int8', recs=None, raw=None):
    m = load_mod(str(script))
    tbl = m.load_competitive_table(str(ROOT/'open/data'))
    recs = recs or dev_records(m)
    raw = raw or RAW[which]
    S = {k: load_saved(v) for k, v in raw.items()}
    out = {}
    for r in recs:
        i = r['id']
        kw = dict(item_text=S.get('item', {}).get(i, ''), model_text=S.get('model', {}).get(i, ''),
                  sme_text=S.get('sme', {}).get(i, ''), region_text=S.get('region', {}).get(i, ''))
        hits, evid, _ = m.decide(r, S['main'].get(i, ''), tbl, **kw)
        out[i] = (hits, evid)
    return m, recs, out

def score(out, lab, ids=None):
    ids = ids or list(out)
    res = {}
    for v in ITEMS:
        tp = sum(1 for i in ids if int(lab[i][v]) and out[i][0][v]); fp = sum(1 for i in ids if not int(lab[i][v]) and out[i][0][v])
        fn = sum(1 for i in ids if int(lab[i][v]) and not out[i][0][v])
        res[v] = (2*tp/(2*tp+fp+fn) if tp else 0.0, tp, fp, fn)
    res['macro'] = sum(res[v][0] for v in ITEMS)/24
    return res
