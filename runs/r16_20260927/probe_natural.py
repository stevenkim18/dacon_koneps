"""자연 공고의 실제 자격 줄로 만든 주입 탐침(N 세트). Claude가 쓴 문장이 아니라 무라벨 20,000에서 뽑은 줄의 서식·말투를 그대로 쓴다.
 - 실적(v2): 자격 절('…실적이 있는/보유한 업체·자')과 기간·금액·건수가 있는 자연 줄을 무작위 추출 → 고시금액 미만·실적 없는 공고에 넣는다.
 - 지역(v7·v6): 입찰자 소재지 자격 절이 있고 시·도가 하나인 자연 줄 → 그 시·도를 'X 또는 Y'(v7) / 'X [지역:r9|단위=기초|광역=X]'(v6)로 고쳐
   meta 지역제한 N·고시금액 미만(지방 5억 미만) 공고에 넣는다.
줄 추출은 기준·후보 스크립트의 추출기와 무관한 넓은 정규식으로 하고, 설계에 쓰지 않은 공고(id 해시 홀수)만 쓴다.
  python runs/r16_20260927/probe_natural.py BASE.py VAR.py [n_lines=80] [nb=4]"""
import sys, gzip, json, re, random, copy, hashlib, importlib.util, collections
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
args = sys.argv[1:]; paths = [a for a in args if a.endswith(".py")]; opts = dict(a.split("=", 1) for a in args if "=" in a)
NL = int(opts.get("n_lines", 80)); NB = int(opts.get("nb", 4))
def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
mods = [load(p) for p in paths]; M0 = mods[0]
tbl = M0.load_competitive_table(ROOT + "/open/data")
held = lambda i: int(hashlib.md5(i.encode()).hexdigest(), 16) % 2 == 1
FULL = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "경기도",
        "강원특별자치도", "충청북도", "충청남도", "전북특별자치도", "전라남도", "경상북도", "경상남도", "제주특별자치도"]
ADJ = {"서울특별시": "경기도", "경기도": "인천광역시", "인천광역시": "경기도", "부산광역시": "경상남도", "경상남도": "부산광역시", "대구광역시": "경상북도",
       "경상북도": "대구광역시", "광주광역시": "전라남도", "전라남도": "광주광역시", "대전광역시": "충청남도", "충청남도": "대전광역시",
       "울산광역시": "경상남도", "세종특별자치시": "충청북도", "충청북도": "세종특별자치시", "강원특별자치도": "경기도",
       "전북특별자치도": "충청남도", "제주특별자치도": "전라남도"}
PERF_LINE = re.compile(r"(실적|경험|이력)[^\n]{0,40}?(이|을|를)?\s*(\d+\s*(건|회)\s*이상\s*)?(있는|보유한|보유하고\s*있는|갖춘|가진)\s*(업체|자(?![가-힣])|사업자|법인)")
PERF_SPEC = re.compile(r"최근\s*\d+\s*(년|개월)|\d+\s*(년|개월)\s*(이내|간)|\d[\d,\.]*\s*(억|천만|백만|만)?\s*원|\d+\s*(건|회)\s*이상")
PERF_NOT = re.compile(r"배점|\d+\s*점|평가|우대|가점|가산|부정당|제재|결격|배제|사고|경력|기술자|책임자|인력|강사|전문가|연구원|\|")
SHORT = {"서울": "경기", "부산": "경남", "대구": "경북", "인천": "경기", "대전": "충남", "울산": "경남", "세종": "충북", "경기": "인천", "강원": "경기",
         "충북": "세종", "충남": "대전", "전북": "충남", "전남": "광주", "경북": "대구", "경남": "부산", "제주": "전남"}
PLACE = "|".join(FULL) + r"|(?<![가-힣])(?:" + "|".join(SHORT) + r")(?:시|도)?(?=[\s,·에인이내지의])"
REG_LINE = re.compile(r"(본점|주된\s*영업소|영업소|본사|사업장|소재지|주\s*사무소)[^\n]{0,80}?(" + PLACE + r")[^\n]{0,30}?(소재|있는|둔|두고|위치|인\s|내)[^\n]{0,15}?(업체|자(?![가-힣])|사업자|법인)"
                      r"|(" + PLACE + r")\s*(에|내에|지역에)?\s*(본사|본점|주된\s*영업소|영업소|사업장)[^\n]{0,6}(둔|두고|있는|보유)[^\n]{0,10}(업체|자(?![가-힣])|사업자|법인)"
                      r"|(" + PLACE + r")\s*(지역\s*)?(소재한|소재하는|소재의|소재)\s*(업체|사업자|법인)")
PLACE_RE = re.compile(PLACE)
REG_NOT = re.compile(r"우대|가산|가점|배점|평가|구입|구매|고용|채용|하도급|협력|공동|분담|구성원|㎞|km|거리|납품\s*장소|설치\s*장소|주\s*소\s*[:：]|\|")
random.seed(0)
perf_lines, reg_lines = [], []
for l in gzip.open(ROOT + "/open/train_unlabeled.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(l)
    if not held(r["id"]): continue
    for d in r["docs"]:
        for ln in d["text"].split("\n"):
            ln = ln.strip()
            if not (15 <= len(ln) <= 300): continue
            if PERF_LINE.search(ln) and PERF_SPEC.search(ln) and not PERF_NOT.search(ln):
                perf_lines.append(ln)
            m = REG_LINE.search(ln)
            if m and not REG_NOT.search(ln) and len(set(PLACE_RE.findall(ln))) == 1 and "[지역:" not in ln:
                reg_lines.append(ln)
def dedup(L):
    seen, out = set(), []
    for x in L:
        k = re.sub(r"\d+|\s+", "", x)[:60]
        if k not in seen: seen.add(k); out.append(x)
    return out
perf_lines, reg_lines = dedup(perf_lines), dedup(reg_lines)
random.shuffle(perf_lines); random.shuffle(reg_lines)
perf_lines, reg_lines = perf_lines[:NL], reg_lines[:NL]
FULL_RE = re.compile("|".join(FULL))
n_short = sum(1 for x in reg_lines if not FULL_RE.search(x))
print(f"자연 줄 표본: 실적 {len(perf_lines)} · 지역 {len(reg_lines)} (약칭만 {n_short}) (홀수 해시 공고만)")
# 주입 대상 공고: 무라벨 750(서버 저장 출력 있음)
raw = ROOT + "/runs/cloud_int8_exp/exp/raw/"
def saved(n):
    d = {}
    for l in open(raw + n + ".jsonl", encoding="utf-8"):
        r = json.loads(l); d[r["id"]] = r.get("text", "")
    return d
S = {k: saved(k) for k in ("main", "item", "model", "sme", "region")}
recs = [M0.normalize(json.loads(l)) for l in gzip.open(ROOT + "/open/exp950.jsonl.gz", "rt", encoding="utf-8")]
recs = [r for r in recs if not r["id"].startswith("PPS-DEV") and not r.get("dropped_doc_counts") and any(d["type"] == "공고문" for d in r["docs"]) and S["main"].get(r["id"])]
kw = lambda i: dict(item_text=S["item"].get(i, ""), model_text=S["model"].get(i, ""), sme_text=S["sme"].get(i, ""), region_text=S["region"].get(i, ""))
m = lambda r, k: r["meta"].get(k)
price = lambda r: float(m(r, "입찰추정가격") or m(r, "배정예산금액") or 0)
priv = lambda r: m(r, "계약방법") == "수의계약"
local = lambda r: m(r, "적용계약법") == "지방계약법"
def base_hits(r): return M0.decide(r, S["main"][r["id"]], tbl, **kw(r["id"]))[0]
def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문": continue
        lines = d["text"].split("\n")
        ks = [j for j, x in enumerate(lines) if re.search(r"참가\s*자격", x)]
        k0 = ks[0] if ks else len(lines) // 3
        lines.insert(k0 + 1, sent); d["text"] = "\n".join(lines); break
    return r
pool_p = [r for r in recs if not priv(r) and 5e6 <= price(r) < 2.3e8]
pool_r = [r for r in recs if not priv(r) and m(r, "지역제한여부") != "Y" and 5e6 <= price(r) < (5e8 if local(r) else 2.3e8)]
random.shuffle(pool_p); random.shuffle(pool_r)
pool_p = [r for r in pool_p if not base_hits(r)["v2"]][:NB]
pool_r = [r for r in pool_r if not base_hits(r)["v7"] and not base_hits(r)["v6"]][:NB]
def _full(p):
    return p if p in FULL else next(f for f in FULL if f.startswith(p[:2]) or (p[:2] == "충북" and f == "충청북도") or (p[:2] == "충남" and f == "충청남도")
                                     or (p[:2] == "전남" and f == "전라남도") or (p[:2] == "경북" and f == "경상북도") or (p[:2] == "경남" and f == "경상남도")
                                     or (p[:2] == "전북" and f == "전북특별자치도"))
def edit_v7(ln):
    p = PLACE_RE.findall(ln)[0]
    return ln.replace(p, f"{p} 또는 {ADJ[p]}" if p in FULL else f"{p}, {SHORT[p[:2]]}", 1)
def edit_v6(ln):
    p = PLACE_RE.findall(ln)[0]; return ln.replace(p, f"{p} [지역:r9|단위=기초|광역={_full(p)}]", 1)
res = collections.defaultdict(collections.Counter); miss = collections.defaultdict(list)
for item, lines, pool, edit in (("v2", perf_lines, pool_p, lambda x: x), ("v7", reg_lines, pool_r, edit_v7), ("v6", reg_lines, pool_r, edit_v6)):
    for ln in lines:
        sent = edit(ln)
        for b in pool:
            r2 = inject(b, sent)
            for mi, mm in enumerate(mods):
                hr = mm.decide(r2, "", tbl)[0][item]; hl = mm.decide(r2, S["main"][b["id"]], tbl, **kw(b["id"]))[0][item]
                res[(item, mi)]["n"] += 1; res[(item, mi)]["r"] += hr; res[(item, mi)]["l"] += hl
                if mi == len(mods) - 1 and not hl: miss[item].append(sent)
print("항목 | " + " | ".join(f"{p.split('/')[-2]}: 정규식만 / LLM있음" for p in paths))
for item in ("v2", "v7", "v6"):
    print(item, " | ".join(f"{res[(item, mi)]['r']}/{res[(item, mi)]['n']} · {res[(item, mi)]['l']}/{res[(item, mi)]['n']}" for mi in range(len(mods))))
if opts.get("show"):
    for item, L in miss.items():
        print("## 놓침", item, len(L))
        for x in list(dict.fromkeys(L))[:int(opts.get("show"))]: print("   ", x[:200])
