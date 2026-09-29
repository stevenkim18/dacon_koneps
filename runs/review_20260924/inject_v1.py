"""v1(특정기관 한정) 바꿔 쓴 문장을 자연 공고 참가자격 줄 뒤에 넣고 정규식 경로로 켜지는지. 사용: inject_v1.py BASE.py NEW.py"""
import json, gzip, random, re, sys, copy, importlib.util
def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
mods = [load(p) for p in sys.argv[1:]]
tbl = mods[0].load_competitive_table("open/data")
S = ["본 입찰은 「고등교육법」 제2조에 따른 대학만 참여 가능합니다.",
     "산학협력단만 입찰에 참가할 수 있습니다.",
     "라. 국공립 연구기관 또는 대학교만 참여 가능함",
     "[기관(대학)]만 입찰 참여 가능",
     "본 용역은 4년제 대학교만 참가 가능합니다.",
     "대학 부설 연구소만 참여 가능"]
rng = random.Random(7); base = []
for l in gzip.open("open/train_unlabeled.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(l)
    if r.get("dropped_doc_counts") or not any(d["type"] == "공고문" for d in r["docs"]): continue
    base.append(r)
rng.shuffle(base); base = [b for b in base[:3000] if not mods[0].decide(b, "", tbl)[0]["v1"]][:8]
def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문": continue
        lines = d["text"].split("\n"); k = next((i for i, l in enumerate(lines) if re.search(r"참가\s*자격", l)), len(lines) // 3)
        lines.insert(k + 1, sent); d["text"] = "\n".join(lines); break
    return r
for s in S:
    print([sum(m.decide(inject(b, s), "", tbl)[0]["v1"] for b in base) for m in mods], "/", len(base), "|", s)
