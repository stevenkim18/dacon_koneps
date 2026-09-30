"""09-28 R18 H9(v1 최종 보류 세트, H5 코드 복사): V1W 설계 뒤에 새로 쓴 특정기관 한정 문장. 무라벨 750(저장 int8 출력) 공고 참가자격 절에 넣어
정규식 경로·서버 경로(저장 LLM 출력 유지) 재현율을 두 판에서 비교한다. 문장은 dev v1 정답 말투(기관 유형만 참가·회원사·지사망·인원)를 본떴다.
  python runs/r17_20260928/probe_h5_v1.py BASE.py VAR.py [nb=6]"""
import sys, json, gzip, re, copy, random, importlib.util
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[2])
H5 = [  # 09-28 R18 H9(v1 최종 보류 세트): V1X 3차 설계(H5~H8) 뒤에 새로 쓴 문장 — 이름은 H5 코드 재사용을 위해 그대로 둔다
    "가. 본 용역 입찰은 「고등교육법」 제2조제1호의 대학에 한정하여 실시한다.",
    "○ 입찰참가자격: 공공기관 또는 공공기관이 50% 이상 출자한 법인",
    "나. ○○연구조합 가입 기업만 제안 가능함",
    "- 입찰에 참가하려는 자는 ○○시 산하 출연기관이어야 한다",
    "다. 참가대상 : 문화예술진흥법에 따른 전문예술법인·단체",
    "라. 본 과업은 국내 의료기관 중 상급종합병원에서만 수행할 수 있다.",
    "3) 입찰참가는 ○○학회 평생회원 기관으로 제한됨",
    "마. 전국 광역시에 모두 교육센터를 운영 중인 업체만 입찰 가능",
    "○ 자체 콜센터(상담석 30석 이상)를 운영하고 있는 업체에 한함",
    "- 본 입찰은 한국○○연합회에 등록된 회원사에 한하여 참가 가능",
    "가. 입찰자는 창립 20년 이상 된 사단법인이어야 합니다.",
    "나. 사업 수행 주체: 정부 출연 연구원 또는 대학 연구소",
    "※ 본 입찰에는 기술지주회사의 자회사만 참가할 수 있다",
    "4. 입찰 참가 가능 기관 : 광역지방자치단체 산하 공기업",
    "다. 참여 자격 - ○○협회에서 인증한 우수 교육기관",
    "라. 입찰 참가자는 상시 근로자 수가 200명 이상이어야 합니다.",
    "- 국내에 제조 공장을 2곳 이상 운영하는 업체로 한정",
    "○ 참가 가능한 자는 ○○청 지정 협력기관으로 한다.",
    "가. 본 사업의 입찰은 사회적협동조합에 한하여 허용",
    "나. 입찰 참가자: 전국 단위 비영리 민간단체",
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
