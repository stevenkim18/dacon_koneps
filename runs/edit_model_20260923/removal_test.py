import json, gzip, random, re, sys, copy, importlib.util, collections
spec=importlib.util.spec_from_file_location("cand", sys.argv[1]); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
tbl=mod.load_competitive_table("open/data")
ITEMS=[f"v{i}" for i in range(1,25)]
rng=random.Random(5)
base=[]
for l in gzip.open("open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=json.loads(l)
    if r.get("dropped_doc_counts") or r["meta"].get("계약방법")=="수의계약": continue
    base.append(r)
rng.shuffle(base); base=base[:9000]
def price(r):
    try: return float(r["meta"].get("입찰추정가격") or 0)
    except: return 0
def remove_lines(r, pred):
    r=copy.deepcopy(r); removed=[]
    for d in r["docs"]:
        keep=[]
        for ln in d["text"].split("\n"):
            if pred(ln): removed.append(ln.strip()); continue
            keep.append(ln)
        d["text"]="\n".join(keep)
    return r, removed
SME_WORD=re.compile(r"소기업|소상공인|중소기업|중기업")
RESTR=re.compile(r"한함|한정|제한|소지한|보유(하고|한)|갖춘|자이어야|업체이어야|업체일 것|자\s*$|업체\s*$|참가\s*자격")
def sme_main_line(ln):
    # the qualification line itself: SME word + restriction verb, not a list item/notes
    s=ln.strip()
    if not SME_WORD.search(s): return False
    if re.search(r"\d+\s*부\b|확인서는|확인서가|확인(이|되지|이 안)|※|간주|특별법인|입\s*찰\s*방\s*법", s): return False
    return bool(RESTR.search(s)) and bool(re.search(r"따른|의한|규정된|해당하는|중소기업|소기업", s))
out=collections.Counter(); ex=collections.defaultdict(list)
def test(item, cond, pred, n=40):
    got=0; tot=0; left=collections.Counter()
    for r in base:
        if tot>=n: break
        if not cond(r): continue
        h0=mod.decide(r,"",tbl)[0]
        if h0[item]: continue
        r2,removed=remove_lines(r,pred)
        if not removed: continue
        h=mod.decide(r2,"",tbl)[0]
        tot+=1; got+=h[item]
        if not h[item] and len(ex[item])<5:
            rx=mod.regex_facts(r2,tbl)
            ex[item].append((r["id"], price(r), rx.get("기업규모_근거") or rx.get("대기업_참여제한_문구"), [x[:90] for x in removed[:2]]))
    print(f"{item}: fired after removal {got}/{tot}")
comp=lambda r: mod.is_competitive(mod.merge_facts(None, mod.regex_facts(r,tbl), {}), r, tbl)
test("v18", lambda r: 5e6<=price(r)<1e8 and not comp(r) and mod.rx_sme_level(r)[0]!="없음", sme_main_line)
test("v16", lambda r: 1e8<=price(r)<2.3e8 and not comp(r) and mod.rx_sme_level(r)[0]!="없음", sme_main_line)
test("v11", lambda r: comp(r) and mod.rx_sme_level(r)[0]!="없음", sme_main_line)
test("v10", lambda r: comp(r) and mod.regex_facts(r,tbl)["직접생산확인_요구"], lambda ln: "직접생산" in ln and re.search(r"소지|보유|갖춘",ln) and not re.search(r"\d+\s*부\b|※|위반",ln))
test("v20", lambda r: mod.is_software(r) and price(r)>=1e8 and mod.regex_facts(r,tbl)["대기업_참여제한_문구"], lambda ln: bool(re.search(r"대기업|중견기업|상호출자|제\s*48\s*조",ln)) and bool(re.search(r"참여|참가|제한|하한",ln)))
for k,v in ex.items():
    print("== misses",k)
    for x in v: print("   ",x)
