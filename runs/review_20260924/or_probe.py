import json, gzip, csv, collections, sys
sys.path.insert(0, "runs/int8_port_20260923")
import devtool
ROOT = devtool.ROOT
RAW = {k: ROOT/f"runs/cloud_int8_exp/exp/raw/{k}.jsonl" for k in ("main","item","model","sme","region")}
m = devtool.load_mod(str(ROOT/"submissions/20260924_int8_quote_port/script.py"))
recs = [json.loads(l) for l in gzip.open(ROOT/"open/exp950.jsonl.gz","rt",encoding="utf-8")]
recs = [m.normalize(r) if hasattr(m,"normalize") else r for r in recs]
S = {k: devtool.load_saved(v) for k,v in RAW.items()}
tbl = m.load_competitive_table(str(ROOT/"open/data"))
lab = devtool.labels()
hl = collections.defaultdict(dict)
for f in ["labels/train250_audit.csv","labels/train500_audit.csv"]:
    for row in csv.DictReader(open(ROOT/f,encoding="utf-8")):
        if row["label"] in ("0","1"): hl[row["id"]][row["item"]] = int(row["label"])
def run_all():
    out = {}
    for r in recs:
        i = r["id"]
        out[i] = m.decide(r, S["main"].get(i,""), tbl, item_text=S["item"].get(i,""), model_text=S["model"].get(i,""),
                          sme_text=S["sme"].get(i,""), region_text=S["region"].get(i,""))[0]
    return out
base = run_all()
orig = dict(m.ITEM_SOURCE)
for k in ["v2","v3","v4","v5","v6","v7","v8","v12","v14","v16","v17","v18","v20","v21","v22","v24"]:
    m.ITEM_SOURCE.clear(); m.ITEM_SOURCE.update(orig); m.ITEM_SOURCE[k] = "or"
    new = run_all()
    add_dev = [(i, int(lab[i][k])) for i in new if i in lab and new[i][k] and not base[i][k]]
    rem_dev = [(i, int(lab[i][k])) for i in new if i in lab and base[i][k] and not new[i][k]]
    add_u = [(i, hl[i].get(k, "?")) for i in new if i not in lab and new[i][k] and not base[i][k]]
    rem_u = [(i, hl[i].get(k, "?")) for i in new if i not in lab and base[i][k] and not new[i][k]]
    print(f"{k}: dev +{len(add_dev)} (TP {sum(x for _,x in add_dev)}) -{len(rem_dev)} (TP lost {sum(x for _,x in rem_dev)}) | 750 +{len(add_u)} -{len(rem_u)}  added-labels {collections.Counter(str(x) for _,x in add_u)}")
m.ITEM_SOURCE.clear(); m.ITEM_SOURCE.update(orig)
