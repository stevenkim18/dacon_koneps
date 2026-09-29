import sys, re, random, pickle
from collections import Counter
sys.path.insert(0, "runs/r18_20260928")
import v1x
from load20k import load
pred = pickle.load(open("runs/replay_cache/20260929_r17_edit_shapes_script_3d4b038cc7.pkl", "rb"))
hits = []
for r in load():
    if r["meta"].get("계약방법") == "수의계약": continue
    for d in r["docs"]:
        for ln in d["text"].split("\n"):
            s = ln.strip()
            if len(s) >= 8 and v1x.v1x_line(s):
                hits.append((r["id"], pred[r["id"]][0], s[:150])); break
ids = {h[0] for h in hits}
print("notices", len(ids), "lines", len(hits))
c = Counter(re.sub(r"[\d○]+", "#", h[2])[:40] for h in hits)
for k, v in c.most_common(15): print(v, k)
random.seed(3)
for h in random.sample(hits, min(80, len(hits))): print(h)
