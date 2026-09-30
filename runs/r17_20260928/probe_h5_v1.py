"""09-28 H5(v1 보류 세트): V1W 설계 뒤에 새로 쓴 특정기관 한정 문장. 무라벨 750(저장 int8 출력) 공고 참가자격 절에 넣어
정규식 경로·서버 경로(저장 LLM 출력 유지) 재현율을 두 판에서 비교한다. 문장은 dev v1 정답 말투(기관 유형만 참가·회원사·지사망·인원)를 본떴다.
  python runs/r17_20260928/probe_h5_v1.py BASE.py VAR.py [nb=6]"""
import sys, json, gzip, re, copy, random, importlib.util
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
H5 = [
    "다. 본 입찰은 「고등교육법」 제2조에 따른 대학교(대학원 포함)만 참가할 수 있습니다.",
    "○ 입찰참가자격: 한국○○학회 등록 회원기관에 한함",
    "라. 정부출연연구기관에 한하여 제안서를 제출할 수 있음",
    "- 참가 가능 기관: 국공립 대학교 산학협력단",
    "나. 입찰참가자는 「민법」 제32조에 따라 설립된 비영리법인이어야 합니다.",
    "본 사업은 ○○시 소재 대학의 산학협력단만 응찰 가능함",
    "3) 입찰참가자는 「사회적기업 육성법」에 따른 인증 사회적기업이어야 함",
    "마. 「협동조합 기본법」에 따른 사회적협동조합만 입찰에 참여할 수 있습니다.",
    "○ 전국 광역시·도에 지사를 1개 이상씩 운영하는 업체",
    "가. 한국○○연합회 소속 회원사로 한정합니다.",
    "※ 본 입찰은 공공기관(공기업·준정부기관)만 참여가능",
    "다. 대학 부설 평생교육원에 한하여 입찰 참가 가능",
    "라. ○○진흥원에 등록된 전문연구기관만 제안 가능합니다.",
    "- 상시 종업원 20인 이상을 보유한 업체에 한함",
    "마. 입찰 참가는 지방자치단체 출연기관으로 제한함",
    "나. 입찰 참가 대상: 4년제 대학 산학협력단",
    "본 용역은 ○○협회 회원사 중 정회원만 입찰에 참가할 수 있음",
    "4) 본 입찰은 전문대학을 제외한 대학교 부설 연구소에 한하여 참가를 허용합니다.",
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
