"""v20: 사업 내용상 SW 사업인데 is_software가 거짓인 1억 이상 입찰 공고를 센다."""
import sys, re, pickle, importlib.util
from collections import Counter
sys.path.insert(0, "runs/r18_20260928")
from load20k import load
spec = importlib.util.spec_from_file_location("m", "submissions/20260929_r17_edit_shapes/script.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
recs = load()
pred = pickle.load(open("runs/replay_cache/20260929_r17_edit_shapes_script_3d4b038cc7.pkl", "rb"))
ITEMS = [f"v{i}" for i in range(1, 25)]
c = Counter(); samples = []
info = Counter()
for r in recs:
    m = r["meta"]
    info[str(m.get("정보화사업여부"))] += 1
    p = M.price(r) or 0
    method = str(m.get("계약방법") or "")
    title = M.title_of(r)
    if p < 1e8 or method == "수의계약":
        continue
    sw = M.is_software(r)
    t_sw = bool(M.SW_OBJECT_RE.search(title))
    c[(sw, t_sw, str(m.get("정보화사업여부")))] += 1
    if not sw and t_sw:
        samples.append((r["id"], title[:80], m.get("업무구분"), m.get("면허업종제한목록"), m.get("정보화사업여부"), pred[r["id"]][19] if pred.get(r["id"]) else None))
print(info)
for k, v in sorted(c.items(), key=lambda x: -x[1]): print(k, v)
print(len(samples))
import random; random.seed(1)
for s in random.sample(samples, min(40, len(samples))): print(s)
