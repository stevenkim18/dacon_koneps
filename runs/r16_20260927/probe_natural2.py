"""자연 줄 주입 탐침 2: v21(지분) · v12(직생) · v19(확약서) · v22(설명회). 무라벨 20,000(홀수 해시)에서 개념 줄을 넓게 뽑아
위반형으로 최소 편집한 뒤 알맞은 공고(무라벨 750, 저장 출력 있음)에 넣는다.
  python runs/r16_20260927/probe_natural2.py BASE.py [VAR.py] [n_lines=60] [nb=4] [show=N]"""
import sys, gzip, json, re, random, copy, hashlib, importlib.util, collections
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
args = sys.argv[1:]; paths = [a for a in args if a.endswith(".py")]; opts = dict(a.split("=", 1) for a in args if "=" in a)
NL = int(opts.get("n_lines", 60)); NB = int(opts.get("nb", 4))
def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
mods = [load(p) for p in paths]; M0 = mods[0]
tbl = M0.load_competitive_table(ROOT + "/open/data")
held = lambda i: int(hashlib.md5(i.encode()).hexdigest(), 16) % 2 == 1
FAM = {
 # 지분: '지분율 N% 이상' 류 → N을 3으로
 "v21": (re.compile(r"(지분|출자\s*비율|참여\s*비율)[^\n]{0,40}?\d+(\.\d+)?\s*%\s*이상"), re.compile(r"대표사[^\n]{0,8}\d+\s*%\s*이상\s*$|\|"),
         lambda ln: re.sub(r"(\d+(\.\d+)?)(\s*%\s*이상)", lambda m: "3" + m.group(3), ln, count=1) if not re.search(r"대표", ln) else
                    re.sub(r"(구성원[^\n]{0,20}?)(\d+(\.\d+)?)(\s*%)", lambda m: m.group(1) + "3" + m.group(4), ln, count=1)),
 # 직생: 자격으로 쓴 직접생산확인 소지·보유 요구
 "v12": (re.compile(r"직접\s*생산[^\n]{0,40}(증명서|확인서|확인)[^\n]{0,40}(소지|보유|받은|필한|갖춘)[^\n]{0,20}(업체|자(?![가-힣])|사업자)"),
         re.compile(r"\d+\s*부\b|위반|하도급|하청|제재|해당\s*시|경우|환경\s*마크|단체\s*표준|\|"), lambda ln: ln),
 # 확약서: 제조사 공급·기술지원 확약서 입찰(마감) 시 제출
 "v19": (re.compile(r"(제조|공급|기술\s*지원)[^\n]{0,40}확약서[^\n]{0,60}(입찰|마감|투찰|개찰)|(입찰|마감|투찰|개찰)[^\n]{0,60}(제조|공급|기술\s*지원)[^\n]{0,40}확약서"),
         re.compile(r"본인은|서약|계약\s*(체결\s*)?(시|전|후)|낙찰자|해당\s*시|필요\s*시|청렴|\|"), lambda ln: ln),
 # 설명회 미참석 시 참가 불가
 "v22": (re.compile(r"(설명회|현장\s*설명)[^\n]{0,60}(참석|참가)[^\n]{0,40}(불가|없|제한|한하여|한함|제외|무효|불인정|허용하지)"),
         re.compile(r"\|"), lambda ln: ln),
}
random.seed(1)
lines = collections.defaultdict(list)
for l in gzip.open(ROOT + "/open/train_unlabeled.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(l)
    if not held(r["id"]): continue
    for d in r["docs"]:
        for ln in d["text"].split("\n"):
            ln = ln.strip()
            if not (12 <= len(ln) <= 300): continue
            for it, (a, x, _) in FAM.items():
                if a.search(ln) and not x.search(ln): lines[it].append(ln)
for it in lines:
    seen, out = set(), []
    for x in lines[it]:
        k = re.sub(r"\d+|\s+", "", x)[:60]
        if k not in seen: seen.add(k); out.append(x)
    random.shuffle(out); lines[it] = out[:NL]
print("자연 줄 표본:", {k: len(v) for k, v in lines.items()})
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
priv = lambda r: m(r, "계약방법") == "수의계약"
goods = lambda r: "물품" in str(m(r, "업무구분") or "")
nego = lambda r: m(r, "낙찰방법") == "협상에의한계약"
def comp_of(r): return M0.is_competitive({"계약목적물_세부품명번호": (M0.meta_item_codes(r) or [""])[0]}, r, tbl)
COND = {"v21": lambda r: not priv(r), "v12": lambda r: not priv(r) and goods(r) and not comp_of(r), "v19": lambda r: goods(r), "v22": lambda r: nego(r)}
def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문": continue
        L = d["text"].split("\n"); ks = [j for j, x in enumerate(L) if re.search(r"참가\s*자격", x)]
        k0 = ks[0] if ks else len(L) // 3
        L.insert(k0 + 1, sent); d["text"] = "\n".join(L); break
    return r
res = collections.defaultdict(collections.Counter); miss = collections.defaultdict(list)
for it, L in lines.items():
    pool = [r for r in recs if COND[it](r)]; random.shuffle(pool)
    pool = [r for r in pool if not M0.decide(r, S["main"][r["id"]], tbl, **kw(r["id"]))[0][it]][:NB]
    for ln in L:
        sent = FAM[it][2](ln)
        for b in pool:
            r2 = inject(b, sent)
            for mi, mm in enumerate(mods):
                hr = mm.decide(r2, "", tbl)[0][it]; hl = mm.decide(r2, S["main"][b["id"]], tbl, **kw(b["id"]))[0][it]
                res[(it, mi)]["n"] += 1; res[(it, mi)]["r"] += hr; res[(it, mi)]["l"] += hl
                if mi == len(mods) - 1 and not hl and not hr: miss[it].append(sent)
for it in lines:
    print(it, " | ".join(f"{paths[mi].split('/')[-2]} 정규식만 {res[(it, mi)]['r']}/{res[(it, mi)]['n']} · LLM있음 {res[(it, mi)]['l']}/{res[(it, mi)]['n']}" for mi in range(len(mods))))
if opts.get("show"):
    for it, L in miss.items():
        print("## 놓침", it, len(set(L)))
        for x in list(dict.fromkeys(L))[:int(opts["show"])]: print("   ", x[:220])
