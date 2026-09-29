"""LLM 경로 탐침 채점: 탐침 공고별 목표 항목이 켜졌는지(재현율)와 목표 밖 항목의 새 양성(원 공고 대비)을 센다.
  python runs/r17_20260928/score_llm_probe.py SCRIPT.py PROBE_DIR [mode]
  mode: rx(정규식만) · int8orig(원 공고의 저장 int8 출력) · b4(탐침에 새로 돌린 MLX 4bit 출력: PROBE_DIR/b4_*.jsonl) · <prefix>(PROBE_DIR/<prefix>_*.jsonl)"""
import sys, json, gzip, importlib.util, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SCRIPT, P = sys.argv[1], Path(sys.argv[2]); MODE = sys.argv[3] if len(sys.argv) > 3 else "rx"
spec = importlib.util.spec_from_file_location("m", SCRIPT); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
TBL = M.load_competitive_table(str(ROOT / "open/data"))
lab = json.load(open(P / "probe_labels.json", encoding="utf-8"))
recs = [M.normalize(json.loads(l)) for l in open(P / "probe.jsonl", encoding="utf-8")]
base = {json.loads(l)["id"]: M.normalize(json.loads(l)) for l in gzip.open(ROOT / "open/exp950.jsonl.gz", "rt", encoding="utf-8")}


def saved(path):
    d = {}
    if Path(path).exists():
        for l in open(path, encoding="utf-8"):
            r = json.loads(l); d[r["id"]] = r.get("text", "")
    return d


I8 = {k: saved(ROOT / f"runs/cloud_int8_exp/exp/raw/{k}.jsonl") for k in ("main", "item", "model", "sme", "region")}
NEW = {k: saved(P / f"{MODE}_{k}.jsonl") for k in ("main", "item", "model", "sme", "region")} if MODE not in ("rx", "int8orig") else None


def run(r, src_id, outs):
    if outs is None:
        return M.decide(r, "", TBL)
    return M.decide(r, outs["main"].get(src_id, ""), TBL, item_text=outs["item"].get(src_id, ""), model_text=outs["model"].get(src_id, ""),
                    sme_text=outs["sme"].get(src_id, ""), region_text=outs["region"].get(src_id, ""))


res = collections.defaultdict(collections.Counter); side = collections.Counter(); miss = collections.defaultdict(list)
for r in recs:
    L = lab[r["id"]]; b = base[L["base"]]
    if MODE == "rx":
        hb = run(b, b["id"], None)[0]; hp, ep, _ = run(r, r["id"], None)
    elif MODE == "int8orig":
        hb = run(b, b["id"], I8)[0]; hp, ep, _ = run(r, L["base"], I8)
    else:
        if not NEW["main"].get(r["id"]):
            continue
        hb = run(b, b["id"], I8)[0]; hp, ep, _ = run(r, r["id"], NEW)
    it = L["item"]
    res[L["kind"]]["n"] += 1; res[L["kind"]]["hit"] += hp[it]
    if not hp[it]:
        miss[L["kind"]].append((r["id"], L["note"][:90]))
    for v in hp:
        if v != it and hp[v] and not hb[v]:
            side[(L["kind"], v)] += 1
print(f"mode={MODE}")
for k, c in sorted(res.items()):
    print(f"  {k:8s} {c['hit']:3d}/{c['n']:3d}")
print("  목표 밖 새 양성:", dict(side))
if len(sys.argv) > 4:
    for k, L in miss.items():
        print("## miss", k)
        for x in L: print("   ", x)
