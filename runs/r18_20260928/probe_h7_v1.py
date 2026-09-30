"""09-28 R18 H7(v1 보류 세트, H5 코드 복사): V1W 설계 뒤에 새로 쓴 특정기관 한정 문장. 무라벨 750(저장 int8 출력) 공고 참가자격 절에 넣어
정규식 경로·서버 경로(저장 LLM 출력 유지) 재현율을 두 판에서 비교한다. 문장은 dev v1 정답 말투(기관 유형만 참가·회원사·지사망·인원)를 본떴다.
  python runs/r17_20260928/probe_h5_v1.py BASE.py VAR.py [nb=6]"""
import sys, json, gzip, re, copy, random, importlib.util
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
H5 = [  # 09-28 R18 H7(v1 보류 세트): V1X 설계(H5·H6) 뒤에 새로 쓴 문장 — 이름은 H5 코드 재사용을 위해 그대로 둔다
    "가. 입찰에 참가할 수 있는 자는 「과학기술분야 정부출연연구기관 등의 설립·운영 및 육성에 관한 법률」에 따른 연구기관으로 한다.",
    "○ 참가대상: 전국 4년제 대학교 부설 산학협력단",
    "- 본 공모는 ○○광역시 소재 공공기관만을 대상으로 합니다.",
    "나. ○○협동조합연합회 회원조합에 한하여 입찰할 수 있음",
    "다. 입찰참가자격 – 한국○○협회 정회원 업체",
    "라. 사단법인 한국○○학회 또는 그 회원기관만 제안서 제출 가능",
    "3. 본 사업의 수행기관은 비영리 공익법인으로 한정함",
    "(2) 입찰 참가자는 ○○인증원으로부터 우수기관 인증을 받은 기관이어야 합니다.",
    "○ 전국 8개 도에 A/S 센터를 직접 운영하고 있는 업체로 제한",
    "- 상시근로자 100인 이상 사업장만 입찰 참여 가능",
    "가. 자사 소유의 연수시설(수용인원 200명 이상)을 보유한 업체에 한하여 참가 가능",
    "나. 국내 소재 의과대학 부속병원에 한함",
    "※ 본 입찰은 공공기관 운영에 관한 법률에 따른 기타공공기관만 참여할 수 있습니다",
    "마. 입찰 참가 자격은 ○○시 출연 재단법인으로 한정된다.",
    "라) 평생교육법에 따른 평생교육시설로 등록된 기관만 응찰 가능",
    "○ 참가자격 : 한국○○연구원 등 국책연구기관",
    "다. 본 용역은 ○○대학교 산학협력단 또는 동 대학 부설연구소만 수행 가능함",
    "4) 입찰자는 한국○○조합의 조합원이어야 하며 조합 추천서를 제출하여야 함",
    "가. 본사 직원 30명 이상을 보유한 법인에 한함",
    "- 전국 시·군·구 중 50곳 이상에 지점망을 갖춘 업체",
]
args = sys.argv[1:]; paths = [a for a in args if a.endswith(".py")]; opts = dict(a.split("=", 1) for a in args if "=" in a)
NB = int(opts.get("nb", 6))


def load(p):
    s = importlib.util.spec_from_file_location("c" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


mods = [load(p) for p in paths]; M0 = mods[0]
tbl = M0.load_competitive_table(ROOT + "/open/data")
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
rng = random.Random(5)
rng.shuffle(recs)
pool = [r for r in recs if r["meta"].get("계약방법") != "수의계약" and not M0.decide(r, S["main"][r["id"]], tbl, **kw(r["id"]))[0]["v1"]][:NB]


def inject(r, sent):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if d["type"] != "공고문":
            continue
        lines = d["text"].split("\n")
        ks = [j for j, x in enumerate(lines) if re.search(r"참가\s*자격", x)]
        k0 = ks[-1] if ks else len(lines) // 3
        lines.insert(k0 + 1, sent); d["text"] = "\n".join(lines); break
    return r


res = [[0, 0] for _ in mods]; miss = []
for s in H5:
    for b in pool:
        r2 = inject(b, s)
        for mi, mm in enumerate(mods):
            res[mi][0] += mm.decide(r2, "", tbl)[0]["v1"]
            hl = mm.decide(r2, S["main"][b["id"]], tbl, **kw(b["id"]))[0]["v1"]
            res[mi][1] += hl
            if mi == len(mods) - 1 and not hl:
                miss.append(s)
n = len(H5) * len(pool)
for p, (a, b) in zip(paths, res):
    print(f"{p}: 정규식만 {a}/{n} · LLM있음 {b}/{n}")
import collections
for s, c in collections.Counter(miss).most_common():
    print(f"   miss {c}x {s}")
