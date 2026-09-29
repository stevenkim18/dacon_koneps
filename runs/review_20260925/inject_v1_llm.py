"""v1 정규식 OR가 LLM 출력이 있을 때도 켜지는지: int8 저장 출력(950건)을 그대로 두고 공고문에 v1 문장만 주입."""
import json, gzip, re, sys, copy, importlib.util
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
mods = [load(p) for p in sys.argv[1:]]
tbl = mods[0].load_competitive_table(ROOT + "/open/data")
raw = ROOT + "/runs/cloud_int8_exp/exp/raw/"
def saved(n):
    d = {}
    for l in open(raw + n + ".jsonl", encoding="utf-8"):
        r = json.loads(l); d[r["id"]] = r.get("text", "")
    return d
S = {k: saved(k) for k in ("main", "item", "model", "sme", "region")}
recs = [json.loads(l) for l in gzip.open(ROOT + "/open/exp950.jsonl.gz", "rt", encoding="utf-8")]
SENT = ["본 입찰은 「고등교육법」 제2조에 따른 대학만 참여 가능합니다.",
        "산학협력단만 입찰에 참가할 수 있습니다.",
        "라. 국공립 연구기관 또는 대학교만 참여 가능함",
        "[기관(대학)]만 입찰 참여 가능",
        "본 용역은 4년제 대학교만 참가 가능합니다.",
        "대학 부설 연구소만 참여 가능"]
def kw(i):
    return dict(item_text=S["item"].get(i, ""), model_text=S["model"].get(i, ""), sme_text=S["sme"].get(i, ""), region_text=S["region"].get(i, ""))
base = []
for r in recs:
    i = r["id"]
    if r.get("dropped_doc_counts") or not any(d["type"] == "공고문" for d in r["docs"]): continue
    if not S["main"].get(i): continue
    if mods[0].decide(r, S["main"][i], tbl, **kw(i))[0]["v1"]: continue
    base.append(r)
    if len(base) >= 12: break
def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문": continue
        lines = d["text"].split("\n"); k = next((j for j, l in enumerate(lines) if re.search(r"참가\s*자격", l)), len(lines) // 3)
        lines.insert(k + 1, sent); d["text"] = "\n".join(lines); break
    return r
print("base", len(base))
for s in SENT:
    with_llm = [sum(m.decide(inject(b, s), S["main"][b["id"]], tbl, **kw(b["id"]))[0]["v1"] for b in base) for m in mods]
    no_llm = [sum(m.decide(inject(b, s), "", tbl)[0]["v1"] for b in base) for m in mods]
    print("LLM있음", with_llm, "| LLM없음", no_llm, "/", len(base), "|", s)
