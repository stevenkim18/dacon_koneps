import sys, json, gzip, random, importlib.util
from collections import Counter
sys.path.insert(0, "runs/r18_20260928")
from load20k import load
import v9cand as V
spec = importlib.util.spec_from_file_location("m", "submissions/20260929_r17_edit_shapes/script.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
recs = load()
added = []; n_goods = 0; n_changed = 0; newcall = 0
for r in recs:
    r = M.normalize(r)
    if not M.is_goods(r): continue
    n_goods += 1
    b = M.model_candidate_lines(r); e = V.extra_lines(M, r, b)
    if len(e) > len(b):
        n_changed += 1; newcall += (len(b) == 0)
        for x in e[len(b):]: added.append((r["id"], x))
print("goods", n_goods, "changed", n_changed, "newcall", newcall, "added lines", len(added))
random.seed(5)
for x in random.sample(added, 60): print(x[0], "|", x[1][:150])
