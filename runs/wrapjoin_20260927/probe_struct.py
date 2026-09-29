"""09-27 구조 변형 주입 시험: 같은 위반 문장을 T0 한 줄 · T1 표 칸 · T2 문장 가운데 줄바꿈 · T3 자격 머리글 줄에 이어 붙임 · T4 깊은 위치 · T5 다른 첨부 문서로 넣는다.
usage: struct_probe.py SCRIPT.py [SCRIPT2.py] [transforms=T0,T1,...] [items=v2,v4]"""
import json, gzip, re, sys, copy, importlib.util, random, collections
from pathlib import Path
ROOT = "/Users/seungwookim/Code/edu/SeSac/contest/DACON_KONEPS"
sys.path.insert(0, ROOT + "/runs/recall_probe_20260926")
sys.path.insert(0, ROOT + "/runs/edit_model_20260923")
from probe_paraphrases import Q, H, H2
from paraphrases import P
def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
args = sys.argv[1:]
paths = [a for a in args if a.endswith(".py")]
opts = dict(a.split("=", 1) for a in args if "=" in a)
TR = opts.get("transforms", "T0,T1,T2,T3,T4,T5").split(",")
ITF = opts.get("items", "").split(",") if opts.get("items") else None
mods = [load(p) for p in paths]; mod = mods[0]
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
def split_mid(s, rng):
    sp = [m.start() for m in re.finditer(" ", s)]
    if not sp: return s
    mid = len(s) // 2
    k = min(sp, key=lambda x: abs(x - mid))
    return s[:k] + "\n" + s[k + 1:]
def inject(r, sent, tr, rng):
    r = copy.deepcopy(r)
    if tr == "T5":   # into another doc if present, else at end of 공고문
        others = [d for d in r["docs"] if d["type"] != "공고문"]
        d = others[0] if others else r["docs"][-1]
        lines = d["text"].split("\n"); k = min(len(lines), max(1, len(lines) // 3))
        lines.insert(k, sent); d["text"] = "\n".join(lines); return r
    for d in r["docs"]:
        if d["type"] != "공고문": continue
        lines = d["text"].split("\n")
        ks = [j for j, l in enumerate(lines) if re.search(r"참가\s*자격", l)]
        k0 = ks[0] if ks else len(lines) // 3
        if tr == "T0": lines.insert(k0 + 1, sent)
        elif tr == "T1": lines.insert(k0 + 1, "| 입찰참가자격 | " + sent + " |")
        elif tr == "T2": lines.insert(k0 + 1, split_mid(sent, rng))
        elif tr == "T3": lines[k0] = lines[k0].rstrip() + " " + sent
        elif tr == "T4": lines.insert(min(len(lines), k0 + rng.randint(15, 40)), sent)
        elif tr == "T6":  # blank lines around + bullet-less, preceded by empty line (HWP style)
            lines[k0 + 1:k0 + 1] = ["", sent, ""]
        d["text"] = "\n".join(lines); break
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
def no_level(r):
    rx = mod.regex_facts(r, tbl)
    if rx.get("기업규모_제한") not in (None, "없음"): return False
    try: f = json.loads(S["main"][r["id"]])
    except Exception: f = {}
    if f.get("기업규모_제한") not in (None, "없음"): return False
    try: s = json.loads(S["sme"].get(r["id"]) or "{}")
    except Exception: s = {}
    return s.get("기업규모_제한") in (None, "없음", "")
def cat(*ls):
    out = []
    for l in ls: out += l
    return out
sgg = lambda L, p: [s.replace("{P1}", p) for s in L]
tests = [
    ("v1", cat(Q["v1"], H["v1"], H2["v1"]), lambda r: True),
    ("v2", cat(P["v2"], Q["v2"], H["v2"], H2["v2"]), lambda r: not priv(r) and 5e6 <= price(r) < 2.3e8),
    ("v4", cat(P["v4"], Q["v4"], H["v4"], H2["v4"]), lambda r: not priv(r) and price(r) >= 2.3e8),
    ("v5", sgg(cat(P["v_region_prov"], Q["v_region_prov"], H["v_region_prov"], H2["v_region_prov"]), "경상남도"),
          lambda r: not priv(r) and noregion(r) and ((not local(r) and price(r) >= 2.3e8) or (local(r) and price(r) >= 5e8))),
    ("v6", sgg(cat(P["v_region_sgg"], Q["v_region_sgg"]), "전라남도"), lambda r: not priv(r) and noregion(r) and 5e6 <= price(r) < 2.3e8),
    ("v7", [s.replace("{P1}", "부산광역시").replace("{P2}", "울산광역시") for s in cat(P["v_region_two"], Q["v_region_two"])],
          lambda r: not priv(r) and noregion(r) and 5e6 <= price(r) < 2.3e8),
    ("v12", cat(P["v12"], Q["v12"], H["v12"], H2["v12"]), lambda r: not priv(r) and goods(r) and not comp_of(r)),
    ("v15", cat(P["v_sme_small"], Q["v_sme_small"], H2["v_sme_small"]), lambda r: not priv(r) and 1e8 <= price(r) < 2.3e8 and not comp_of(r) and no_level(r)),
    ("v14", cat(P["v_sme_mid"], Q["v_sme_mid"]), lambda r: not priv(r) and price(r) >= 2.3e8 and not comp_of(r) and no_level(r)),
    ("v17", cat(P["v_sme_mid"], Q["v_sme_mid"], H2["v_sme_mid"]), lambda r: not priv(r) and 1e6 <= price(r) < 1e8 and not comp_of(r) and no_level(r)),
    ("v19", Q["v19"], lambda r: goods(r)),
    ("v21", cat(P["v21_local"], Q["v21_local"], H["v21_local"], H2["v21_local"]), lambda r: local(r) and not priv(r)),
    ("v22", cat(P["v22"], P["v22_more"], Q["v22"]), lambda r: nego(r)),
]
rng = random.Random(28)
NB = int(opts.get("nb", 6))
res = collections.defaultdict(lambda: collections.Counter())
miss = collections.defaultdict(list)
for item, sents, cond in tests:
    if ITF and item not in ITF: continue
    pool = [r for r in recs if cond(r) and not base_hits(r)[item]]
    rng.shuffle(pool); pool = pool[:NB]
    if not pool: print(item, "no pool"); continue
    for s in sents:
        for tr in TR:
            for b in pool:
                r2 = inject(b, s, tr, rng)
                for mi, mm in enumerate(mods):
                    hl = mm.decide(r2, S["main"][b["id"]], tbl, **kw(b["id"]))[0][item]
                    hr = mm.decide(r2, "", tbl)[0][item]
                    res[(item, tr, mi)]["n"] += 1; res[(item, tr, mi)]["l"] += hl; res[(item, tr, mi)]["r"] += hr
                    if mi == len(mods) - 1 and not hl and not hr:
                        miss[(item, tr)].append(s)
print("item  " + "  ".join(f"{t:>14s}" for t in TR))
for item, _, _ in tests:
    if ITF and item not in ITF: continue
    for mi in range(len(mods)):
        row = []
        for tr in TR:
            c = res[(item, tr, mi)]
            row.append(f"{c['r']:4d}/{c['l']:4d}/{c['n']:4d}")
        print(f"{item:5s}[{mi}] " + "  ".join(f"{x:>14s}" for x in row))
if opts.get("show"):
    for (item, tr), L in sorted(miss.items()):
        cnt = collections.Counter(L)
        print(f"--- MISS {item} {tr}: {len(L)}")
        for s, c in cnt.most_common(): print(f"   {c}x {s[:110]}")
