"""09-28 R18 H6(v1 보류 세트, H5 코드 복사): V1W 설계 뒤에 새로 쓴 특정기관 한정 문장. 무라벨 750(저장 int8 출력) 공고 참가자격 절에 넣어
정규식 경로·서버 경로(저장 LLM 출력 유지) 재현율을 두 판에서 비교한다. 문장은 dev v1 정답 말투(기관 유형만 참가·회원사·지사망·인원)를 본떴다.
  python runs/r17_20260928/probe_h5_v1.py BASE.py VAR.py [nb=6]"""
import sys, json, gzip, re, copy, random, importlib.util
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
H5 = [  # 09-28 R18 H6(v1 보류 세트): V1X 설계 전에 새로 쓴 문장 — 이름은 H5 코드 재사용을 위해 그대로 둔다
    "가. 입찰참가자격: 「고등교육법」에 따른 전문대학 이상 교육기관",
    "○ 본 과업은 국립대학교 산학협력단에 한정하여 발주합니다.",
    "나. 정부출연 연구기관 또는 국공립 연구기관만 입찰 가능",
    "- 입찰 참가 대상은 ○○도 산하 공공기관으로 한정한다.",
    "다. ○○협회 정회원사만 참가 신청을 할 수 있습니다.",
    "라. 입찰참가는 한국○○조합 조합원에 한하여 허용함",
    "마. 「비영리민간단체 지원법」에 따라 등록된 단체만 신청 가능",
    "3) 입찰 참가 자격 : 사회적협동조합 또는 사회적기업",
    "○ 전국 17개 시·도에 직영 서비스센터를 모두 갖춘 업체",
    "가. 수도권에 자체 교육장(100석 이상)을 보유한 업체에 한함",
    "나. 공고일 현재 정규직 직원 50명 이상 재직 업체만 입찰 가능",
    "- 입찰 참가자는 ○○부 지정 전문기관이어야 한다.",
    "※ 대학(원) 부설 연구소가 아닌 자는 입찰에 참여할 수 없습니다.",
    "다. 본 입찰은 공기업 및 준정부기관만 응찰할 수 있음",
    "라) 입찰자는 ○○학회에 기관회원으로 가입되어 있어야 함",
    "4. 참가자격: ○○재단 인증 교육기관",
    "가. 최근 3년간 ○○시와 협약을 체결한 기관에 한하여 참가 가능",
    "○ 입찰참가자격 : 지방자치단체가 출자·출연한 기관",
    "나. 본 사업 참여는 한국○○진흥원 등록 기관으로 제한합니다.",
    "- 자체 연구소(기업부설연구소)를 보유한 업체만 참가 가능",
    "다. 전국 5개 권역 이상에 물류창고를 운영하는 업체이어야 함",
    "라. 본 용역은 의료법에 따른 종합병원만 수행할 수 있음",
    "○ 입찰 참가는 ○○대학교 기술지주회사 자회사로 제한",
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
