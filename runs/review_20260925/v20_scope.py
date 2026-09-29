import json, gzip, re, importlib.util, random, collections
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
s=importlib.util.spec_from_file_location("m", ROOT+"/submissions/20260926_phrase_parser_recall/script.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
cnt=collections.Counter(); ex=collections.defaultdict(list)
for l in gzip.open(ROOT+"/open/train_unlabeled.jsonl.gz","rt",encoding="utf-8"):
    r=m.normalize(json.loads(l))
    p=m.price(r) or 0
    if p < 1_000_000: continue
    title=m.title_of(r)
    sw_title=bool(m.SW_OBJECT_RE.search(title))
    is_sw=m.is_software(r)
    src=m.full_text(r)
    phrase=bool(re.search(r"대기업|상호출자제한|중견기업", src)) or m.sw_big_limit_noted(src)
    goods = m.is_goods(r)
    key=("sw" if is_sw else "nosw", "swtitle" if sw_title else "-", "phrase" if phrase else "nophrase", "ge1억" if p>=1e8 else "lt1억", "goods" if goods else "svc", m.meta(r,"계약방법"))
    cnt[key]+=1
    if not is_sw and sw_title and not phrase and p>=1e8 and len(ex[key])<400:
        ex[key].append((r["id"], int(p), title[:90], m.meta(r,"면허업종제한목록")))
for k,v in sorted(cnt.items(), key=lambda x:-x[1]):
    if k[0]=="nosw" and k[1]=="swtitle":
        print(k, v)
import pickle
pickle.dump(ex, open(ROOT+"/../v20_nosw_ex.pkl","wb")) if False else None
allex=[x for k,v in ex.items() for x in v]
random.Random(3).shuffle(allex)
print(len(allex))
for x in allex[:40]: print(x)
