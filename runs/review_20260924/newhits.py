"""변형이 기준 대비 20,000에서 바꾼 (공고, 항목)과 근거 줄을 뽑는다. 사용: newhits.py BASE.py VAR.py [항목필터] [최대]"""
import sys, json, gzip, importlib.util, collections, pickle, glob, os, random
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[2])
def load(p):
    s = importlib.util.spec_from_file_location("m" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
b, n = load(sys.argv[1]), load(sys.argv[2])
only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] != "-" else None
cap = int(sys.argv[4]) if len(sys.argv) > 4 else 12
name = os.path.basename(os.path.dirname(sys.argv[2])) + "_" + os.path.splitext(os.path.basename(sys.argv[2]))[0]
cf = os.path.join(ROOT, "runs/replay_cache", f"changed_{name}.pkl")
ids = set(pickle.load(open(cf, "rb")))
tbl = n.load_competitive_table(ROOT + "/open/data")
rows = collections.defaultdict(list)
for l in gzip.open(ROOT + "/open/train_unlabeled.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(l)
    if r["id"] not in ids: continue
    hb, eb, _ = b.decide(r, "", tbl); hn, en, _ = n.decide(r, "", tbl)
    m = r["meta"]
    for k in hb:
        if hb[k] != hn[k] and (only is None or k in only):
            rows[(k, "+" if hn[k] else "-")].append((r["id"], m.get("적용계약법", "")[:2], m.get("계약방법"), m.get("업무구분"), m.get("입찰추정가격"), m.get("지역제한여부"), (en.get(k) if hn[k] else eb.get(k)) or ""))
rng = random.Random(5)
for key in sorted(rows, key=lambda x: (int(x[0][1:]), x[1])):
    lst = rows[key]
    print(f"\n##### {key[0]} {key[1]}{len(lst)}")
    for row in (lst if len(lst) <= cap else rng.sample(lst, cap)):
        print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]} 지역제한여부={row[5]}\n      {row[6][:230]}")
