"""Fresh-paraphrase injection probe on the server path (saved int8 outputs) and the regex-only path.
usage: probe_inject.py SCRIPT.py [SCRIPT2.py ...] [item,item]
SME items use base notices whose regex AND saved-LLM level are both '없음' (append = realistic edit)."""
import json, gzip, re, sys, copy, importlib.util, random, collections
from pathlib import Path
ROOT = "/Users/seungwookim/Code/edu/SeSac/contest/DACON_KONEPS"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe_paraphrases import Q

def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
paths = [a for a in sys.argv[1:] if a.endswith(".py")]
mods = [load(p) for p in paths]
mod = mods[0]
rest = [a for a in sys.argv[1:] if not a.endswith(".py")]
filt = rest[0].split(",") if rest else None
tbl = mod.load_competitive_table(ROOT + "/open/data")
raw = ROOT + "/runs/cloud_int8_exp/exp/raw/"
def saved(n):
    d = {}
    for l in open(raw + n + ".jsonl", encoding="utf-8"):
        r = json.loads(l); d[r["id"]] = r.get("text", "")
    return d
S = {k: saved(k) for k in ("main", "item", "model", "sme", "region")}
recs = [json.loads(l) for l in gzip.open(ROOT + "/open/exp950.jsonl.gz", "rt", encoding="utf-8")]
recs = [mod.normalize(r) for r in recs if not r["id"].startswith("PPS-DEV") and not r.get("dropped_doc_counts")
        and any(d["type"] == "공고문" for d in r["docs"]) and S["main"].get(r["id"])]
def kw(i): return dict(item_text=S["item"].get(i, ""), model_text=S["model"].get(i, ""), sme_text=S["sme"].get(i, ""), region_text=S["region"].get(i, ""))
bc = {}
def base_hits(r):
    if r["id"] not in bc: bc[r["id"]] = mod.decide(r, S["main"][r["id"]], tbl, **kw(r["id"]))[0]
    return bc[r["id"]]
def no_level(r):
    rx = mod.regex_facts(r, tbl)
    if rx.get("기업규모_제한") not in (None, "없음"): return False
    try: f = json.loads(S["main"][r["id"]])
    except Exception: f = {}
    if f.get("기업규모_제한") not in (None, "없음"): return False
    try: s = json.loads(S["sme"].get(r["id"]) or "{}")
    except Exception: s = {}
    return s.get("기업규모_제한") in (None, "없음", "")
def inject(r, sent, where, rng):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문": continue
        lines = d["text"].split("\n")
        ks = [j for j, l in enumerate(lines) if re.search(r"참가\s*자격", l)]
        k0 = ks[0] if ks else len(lines) // 3
        k = k0 if where == "after_qual" else min(len(lines) - 1, k0 + rng.randint(3, 25))
        lines.insert(k + 1, sent); d["text"] = "\n".join(lines); break
    return r
m = lambda r, k: r["meta"].get(k)
def price(r):
    try: return float(m(r, "입찰추정가격") or m(r, "배정예산금액") or 0)
    except: return 0
local = lambda r: m(r, "적용계약법") == "지방계약법"
nego = lambda r: "협상" in str(m(r, "낙찰방법"))
priv = lambda r: m(r, "계약방법") == "수의계약"
goods = lambda r: "물품" in str(m(r, "업무구분") or "")
noregion = lambda r: m(r, "지역제한여부") != "Y"
def comp_of(r):
    return mod.is_competitive({"계약목적물_세부품명번호": (mod.meta_item_codes(r) or [""])[0]}, r, tbl)
tests = [
    ("v1", Q["v1"], lambda r: True),
    ("v2", Q["v2"], lambda r: not priv(r) and 5e6 <= price(r) < 2.3e8),
    ("v4", Q["v4"], lambda r: not priv(r) and price(r) >= 2.3e8),
    ("v5", [s.replace("{P1}", "경상남도") for s in Q["v_region_prov"]], lambda r: not priv(r) and noregion(r) and ((not local(r) and price(r) >= 2.3e8) or (local(r) and price(r) >= 5e8))),
    ("v6", [s.replace("{P1}", "전라남도") for s in Q["v_region_sgg"]], lambda r: not priv(r) and noregion(r) and 5e6 <= price(r) < 2.3e8),
    ("v7", [s.replace("{P1}", "부산광역시").replace("{P2}", "울산광역시") for s in Q["v_region_two"]], lambda r: not priv(r) and noregion(r) and 5e6 <= price(r) < 2.3e8),
    ("v12", Q["v12"], lambda r: not priv(r) and goods(r) and not comp_of(r)),
    ("v15", Q["v_sme_small"], lambda r: not priv(r) and 1e8 <= price(r) < 2.3e8 and not comp_of(r) and no_level(r)),
    ("v13", Q["v_sme_small"], lambda r: not priv(r) and comp_of(r) and no_level(r)),
    ("v14", Q["v_sme_mid"], lambda r: not priv(r) and price(r) >= 2.3e8 and not comp_of(r) and no_level(r)),
    ("v17", Q["v_sme_mid"], lambda r: not priv(r) and 1e6 <= price(r) < 1e8 and not comp_of(r) and no_level(r)),
    ("v19", Q["v19"], lambda r: goods(r)),
    ("v21", Q["v21_local"], lambda r: local(r) and not priv(r)),
    ("v21n", Q["v21_nat"], lambda r: not local(r) and not priv(r)),
    ("v22", Q["v22"], lambda r: nego(r)),
]
rng = random.Random(26)
NB = 10
for item, sents, cond in tests:
    if filt and item not in filt: continue
    it = item.rstrip("n") if item.endswith("n") and item != "v2n" else item
    it = "v21" if item == "v21n" else item
    pool = [r for r in recs if cond(r) and not base_hits(r)[it]]
    rng.shuffle(pool); pool = pool[:NB]
    if not pool:
        print(item, "기반 공고 없음"); continue
    tot = collections.Counter()
    for s in sents:
        hl = [0] * len(mods); hr = [0] * len(mods)
        for b in pool:
            r2 = inject(b, s, "after_qual", rng)
            for mi, mm in enumerate(mods):
                hl[mi] += mm.decide(r2, S["main"][b["id"]], tbl, **kw(b["id"]))[0][it]
                hr[mi] += mm.decide(r2, "", tbl)[0][it]
        for mi in range(len(mods)):
            tot[("l", mi)] += hl[mi]; tot[("r", mi)] += hr[mi]
        flag = "" if max(hl + hr) == len(pool) else "  <-- MISS"
        print(f"  {item} LLM있음 {hl} · 정규식만 {hr} /{len(pool)} | {s[:70]}{flag}")
    n = len(pool) * len(sents)
    print(f"{item}: LLM있음 {[tot[('l', i)] for i in range(len(mods))]}/{n} · 정규식만 {[tot[('r', i)] for i in range(len(mods))]}/{n}  (pool {len(pool)})")
