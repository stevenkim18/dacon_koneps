"""09-28 자연 줄 탐침 N3(v3·v4·v5): 무라벨 20,000 중 설계에 쓰지 않은 공고(id 해시 홀수)의 실제 자격 줄을 무라벨 750 공고에 넣는다.
 - v3: 금액이 있는 실적 자격 줄. 줄의 첫 금액을 **넣을 공고의 사업예산 이상**으로 같은 단위 표기로 고친다(운영진 편집 = 숫자만 바꿈).
 - v4: 공공 발주처(국가·지자체·공공기관·정부·관공서·공기업 …)로 실적을 한정한 자연 줄 그대로.
 - v5: 입찰자 소재지 자격 줄(시·도 하나) 그대로 → meta 지역제한 N·고시금액 이상(지방 5억 이상) 공고.
  python runs/r17_20260928/probe_n3.py BASE.py [VAR.py] [n_lines=80] [nb=4] [show=40]"""
import sys, gzip, json, re, random, copy, hashlib, importlib.util, collections
ROOT = "/Users/seungwookim/Code/edu/SeSac/contest/DACON_KONEPS"
args = sys.argv[1:]; paths = [a for a in args if a.endswith(".py")]; opts = dict(a.split("=", 1) for a in args if "=" in a)
NL = int(opts.get("n_lines", 80)); NB = int(opts.get("nb", 4))


def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


mods = [load(p) for p in paths]; M0 = mods[0]
tbl = M0.load_competitive_table(ROOT + "/open/data")
held = lambda i: int(hashlib.md5(i.encode()).hexdigest(), 16) % 2 == 1
FULL = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "경기도",
        "강원특별자치도", "충청북도", "충청남도", "전북특별자치도", "전라남도", "경상북도", "경상남도", "제주특별자치도", "강원도", "전라북도"]
PERF_LINE = re.compile(r"(실적|경험|이력)[^\n]{0,60}?(이|을|를)?\s*(\d+\s*(건|회)\s*이상\s*)?(있는|있어야|보유한|보유하고\s*있는|보유하여야|갖춘|가진|이\s*있을\s*것)")
AMT = re.compile(r"(?<![\d,.])(\d[\d,]*(?:\.\d+)?)\s*(억|천만|백만|만|천)?\s*원")
PERF_NOT = re.compile(r"배점|\d+\s*점|평가|우대|가점|가산|부정당|제재|결격|배제|사고|경력|기술자|책임자|인력|강사|전문가|연구원|\||보증|삭제|권고")
PUB = re.compile(r"국가|정부|공공기관|지방자치단체|지자체|관공서|공기업|행정기관|국가기관|중앙부처|공사[·,]|[가-힣]{2,}청(?![가-힣])|교육청|\[수요기관|\[기관")
PLACE = "|".join(FULL)
REG_LINE = re.compile(r"(본점|주된\s*영업소|영업소|본사|사업장|소재지|주\s*사무소)[^\n]{0,80}?(" + PLACE + r")[^\n]{0,30}?(소재|있는|둔|두고|위치|인\s|내)[^\n]{0,15}?(업체|자(?![가-힣])|사업자|법인)"
                      r"|(" + PLACE + r")\s*(지역\s*)?(소재한|소재하는|소재의|소재)\s*(업체|사업자|법인)")
PLACE_RE = re.compile(PLACE)
REG_NOT = re.compile(r"우대|가산|가점|배점|평가|구입|구매|고용|채용|하도급|협력|공동|분담|구성원|㎞|km|거리|납품\s*장소|설치\s*장소|주\s*소\s*[:：]|\|")
random.seed(0)
v3_lines, v4_lines, reg_lines = [], [], []
for l in gzip.open(ROOT + "/open/train_unlabeled.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(l)
    if not held(r["id"]):
        continue
    for d in r["docs"]:
        for ln in d["text"].split("\n"):
            ln = ln.strip()
            if not (15 <= len(ln) <= 300):
                continue
            if PERF_LINE.search(ln) and not PERF_NOT.search(ln):
                if AMT.search(ln):
                    v3_lines.append(ln)
                if PUB.search(ln[:PERF_LINE.search(ln).start() + 5]) or PUB.search(ln):
                    v4_lines.append(ln)
            m = REG_LINE.search(ln)
            if m and not REG_NOT.search(ln) and len(set(PLACE_RE.findall(ln))) == 1 and "[지역:" not in ln:
                reg_lines.append(ln)


def dedup(L):
    seen, out = set(), []
    for x in L:
        k = re.sub(r"\d+|\s+", "", x)[:60]
        if k not in seen:
            seen.add(k); out.append(x)
    return out


v3_lines, v4_lines, reg_lines = dedup(v3_lines), dedup(v4_lines), dedup(reg_lines)
for L in (v3_lines, v4_lines, reg_lines):
    random.shuffle(L)
v3_lines, v4_lines, reg_lines = v3_lines[:NL], v4_lines[:NL], reg_lines[:NL]
print(f"자연 줄 표본: v3 {len(v3_lines)} · v4 {len(v4_lines)} · v5 {len(reg_lines)}")
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
budget = lambda r: float(m(r, "배정예산금액") or m(r, "입찰추정가격") or 0)
priv = lambda r: m(r, "계약방법") == "수의계약"
local = lambda r: m(r, "적용계약법") == "지방계약법"
BC = {}


def base_hits(r):
    if r["id"] not in BC:
        BC[r["id"]] = M0.decide(r, S["main"][r["id"]], tbl, **kw(r["id"]))[0]
    return BC[r["id"]]


def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문":
            continue
        lines = d["text"].split("\n")
        ks = [j for j, x in enumerate(lines) if re.search(r"참가\s*자격", x)]
        k0 = ks[0] if ks else len(lines) // 3
        lines.insert(k0 + 1, sent); d["text"] = "\n".join(lines); break
    return r


UNITV = {"억": 1e8, "천만": 1e7, "백만": 1e6, "만": 1e4, "천": 1e3, None: 1}


def edit_v3(ln, b):
    """첫 금액을 사업예산 × 1.0~1.5(단위 반올림, 올림)로 같은 표기 단위로 고친다."""
    mm = AMT.search(ln)
    unit = mm.group(2)
    target = b * random.choice([1.0, 1.2, 1.5])
    u = UNITV[unit]
    n = -(-target // u)                       # 올림 → 사업예산 이상
    if unit is None:
        txt = f"{int(n):,}" if "," in mm.group(1) else str(int(n))
    else:
        txt = f"{int(n):,}" if "," in mm.group(1) else str(int(n))
    return ln[:mm.start(1)] + txt + ln[mm.end(1):]


pool_all = [r for r in recs if not priv(r) and price(r) >= 5e6]
random.shuffle(pool_all)
pool3 = [r for r in pool_all if not base_hits(r)["v3"] and budget(r) > 0][:NB]
pool4 = [r for r in pool_all if not base_hits(r)["v4"]][:NB]
pool5 = [r for r in pool_all if m(r, "지역제한여부") != "Y" and not base_hits(r)["v5"] and price(r) >= (5e8 if local(r) else 2.3e8)][:NB]
res = collections.defaultdict(collections.Counter); miss = collections.defaultdict(list)
for item, lines, pool, edit in (("v3", v3_lines, pool3, edit_v3), ("v4", v4_lines, pool4, lambda x, b: x), ("v5", reg_lines, pool5, lambda x, b: x)):
    for ln in lines:
        for b in pool:
            sent = edit(ln, budget(b))
            r2 = inject(b, sent)
            for mi, mm in enumerate(mods):
                hr = mm.decide(r2, "", tbl)[0][item]; hl = mm.decide(r2, S["main"][b["id"]], tbl, **kw(b["id"]))[0][item]
                res[(item, mi)]["n"] += 1; res[(item, mi)]["r"] += hr; res[(item, mi)]["l"] += hl
                if mi == len(mods) - 1 and not hl:
                    miss[item].append(sent)
print("항목 | " + " | ".join(f"{p.split('/')[-2]}/{p.split('/')[-1]}: 정규식만 · LLM있음" for p in paths))
for item in ("v3", "v4", "v5"):
    print(item, " | ".join(f"{res[(item, mi)]['r']}/{res[(item, mi)]['n']} · {res[(item, mi)]['l']}/{res[(item, mi)]['n']}" for mi in range(len(mods))))
if opts.get("show"):
    for item, L in miss.items():
        print("## 놓침", item, len(L))
        for x in list(dict.fromkeys(L))[:int(opts.get("show"))]:
            print("   ", x[:220])
