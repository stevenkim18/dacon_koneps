"""서버 경로(저장된 int8 LLM 출력이 있는 상태) 주입 시험.
LLM 출력은 주입 전 원문으로 만든 것이므로 'LLM이 주입 문장을 놓쳤다'는 비관적 가정이다.
함께 잰다: 주입 문장이 본 호출 발췌(build_snippets)에 들어가는지(LLM이 볼 기회가 있는지).
사용: serverpath_inject.py SCRIPT.py [SCRIPT2.py …] [항목필터]
여러 스크립트를 주면 첫 스크립트로 기반 공고를 고르고 모두 같은 공고·같은 위치로 잰다(열 순서 = 인자 순서)."""
import json, gzip, re, sys, copy, importlib.util, random, collections
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, ROOT + "/runs/edit_model_20260923")
from paraphrases import P
def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
paths = [a for a in sys.argv[1:] if a.endswith(".py")]
mods_all = [load(p) for p in paths]
mod = mods_all[0]
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
base_cache = {}
def base_hits(r):
    if r["id"] not in base_cache: base_cache[r["id"]] = mod.decide(r, S["main"][r["id"]], tbl, **kw(r["id"]))[0]
    return base_cache[r["id"]]
def inject(r, sent, where="after_qual", rng=None):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문": continue
        lines = d["text"].split("\n")
        if where == "after_qual":
            k = next((j for j, l in enumerate(lines) if re.search(r"참가\s*자격", l)), len(lines) // 3)
        else:  # 참가자격 절 안의 마지막 쪽(다음 큰 제목 직전)
            ks = [j for j, l in enumerate(lines) if re.search(r"참가\s*자격", l)]
            k0 = ks[0] if ks else len(lines) // 3
            k = min(len(lines) - 1, k0 + rng.randint(3, 25))
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
V1 = ["라. 본 용역은 「고등교육법」 제2조에 따른 대학 또는 산학협력단만 참여 가능함",
      "체육교육학 전공이 있는 [기관(대학)]만 입찰 참여 가능합니다.",
      "본 입찰은 4년제 대학교만 참여 가능",
      "전국 모든 광역단체에 골재기계 수리 센터가 있는 업체",
      "마. ○○협회 정회원사에 한하여 입찰에 참가할 수 있습니다.",
      "한국○○연구원 인증을 받은 기관만 참가 가능",
      "[지역:r1|단위=기초|광역=경기도] 지역에 소재한 교육(연수) 시설을 보유하고 있는 자",
      "- 공공기관 지정 전문기관으로 등록된 업체에 한함"]
V19 = ["입찰참가 신청 시 제조사의 물품공급 확약서를 제출하여야 합니다.",
       "라. 입찰서 제출 마감일까지 제조사 기술지원 확약서를 제출한 업체에 한함",
       "※ 입찰 시 제조사(공급사)의 물품공급 및 A/S 확약서 원본 제출 필수",
       "- 제조사로부터 발급받은 물품공급확약서를 입찰마감일 전까지 제출할 것",
       "입찰참가자는 제조사의 기술지원확약서를 입찰서류와 함께 제출하여야 함"]
V9 = ["- 규격: 삼성전자 SM-T970 (또는 LG전자 동급 모델)",
      "구매 물품: HP LaserJet Pro M404dn 3대",
      "모델명: Dell OptiPlex 7010 SFF",
      "제조사: 캐논코리아, 모델: imageRUNNER ADVANCE DX C5840i",
      "품명 및 규격: 에어컨(LG전자 FQ18PDNBA1) 5대"]
V13 = P["v_sme_small"]
tests = [
    ("v1", V1, lambda r: True),
    ("v19", V19, lambda r: goods(r)),
    ("v9", V9, lambda r: goods(r)),
    ("v15", P["v_sme_small"], lambda r: not priv(r) and 1e8 <= price(r) < 2.3e8 and not comp_of(r)),
    ("v13", V13, lambda r: not priv(r) and comp_of(r)),
    ("v17", P["v_sme_mid"], lambda r: not priv(r) and 1e6 <= price(r) < 1e8 and not comp_of(r)),
    ("v14", P["v_sme_mid"], lambda r: not priv(r) and price(r) >= 2.3e8 and not comp_of(r)),
    ("v22", P["v22"] + P["v22_more"], lambda r: nego(r)),
    ("v12", P["v12"], lambda r: not priv(r) and goods(r) and not comp_of(r)),
    ("v2", P["v2"], lambda r: not priv(r) and 5e6 <= price(r) < 2.3e8),
    ("v4", P["v4"], lambda r: not priv(r) and price(r) >= 2.3e8),
    ("v21", P["v21_local"], lambda r: local(r) and not priv(r)),
    ("v5", [s.replace("{P1}", "경기도") for s in P["v_region_prov"]], lambda r: not priv(r) and noregion(r) and ((not local(r) and price(r) >= 2.3e8) or (local(r) and price(r) >= 5e8))),
    ("v6", [s.replace("{P1}", "충청남도") for s in P["v_region_sgg"]], lambda r: not priv(r) and noregion(r) and 5e6 <= price(r) < 2.3e8),
    ("v7", [s.replace("{P1}", "대구광역시").replace("{P2}", "경상북도") for s in P["v_region_two"]], lambda r: not priv(r) and noregion(r) and 5e6 <= price(r) < 2.3e8),
]
rng = random.Random(11)
NB = 10
for item, sents, cond in tests:
    if filt and item not in filt: continue
    pool = [r for r in recs if cond(r) and not base_hits(r)[item]]
    rng.shuffle(pool); pool = pool[:NB]
    if not pool:
        print(item, "기반 공고 없음"); continue
    tot = collections.Counter()
    for where in ("after_qual", "deep"):
        for s in sents:
            hit_llm = [0] * len(mods_all); hit_rx = [0] * len(mods_all); vis = 0
            for b in pool:
                r2 = inject(b, s, where, rng)
                for mi, mm in enumerate(mods_all):
                    hit_llm[mi] += mm.decide(r2, S["main"][b["id"]], tbl, **kw(b["id"]))[0][item]
                    hit_rx[mi] += mm.decide(r2, "", tbl)[0][item]
                msgs, n, sc = mod.fit_to_budget(r2, tbl, type("T", (), {"count_tokens": staticmethod(lambda ms: sum(len(x["content"]) for x in ms) // 2)})())
                vis += int(s.strip()[:40] in msgs[1]["content"])
            for mi in range(len(mods_all)):
                tot[(where, "llm", mi)] += hit_llm[mi]; tot[(where, "rx", mi)] += hit_rx[mi]
            tot[(where, "vis")] += vis
            if where == "after_qual":
                print(f"  {item} LLM있음 {hit_llm} · 정규식만 {hit_rx} · 발췌노출 {vis:2d} /{len(pool)} | {s[:60]}")
    n = len(pool) * len(sents)
    L = lambda w, k: [tot[(w, k, mi)] for mi in range(len(mods_all))]
    print(f"{item}: 참가자격 직후 → LLM있음 {L('after_qual','llm')}/{n} · 정규식만 {L('after_qual','rx')}/{n} · 발췌노출 {tot[('after_qual','vis')]}/{n}"
          f" | 깊은 위치 → LLM있음 {L('deep','llm')}/{n} · 정규식만 {L('deep','rx')}/{n} · 발췌노출 {tot[('deep','vis')]}/{n}")
