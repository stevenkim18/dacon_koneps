"""09-28 삭제 탐침(기업규모, 운영진 편집 모형): dev 부재형 정답 공고(v16·v18·v11 13건)에 남은 기업규모 낱말은
서류 목록('…확인서 1부'), 입찰방식 머리말('입 찰 방 법: 제한경쟁(소기업·소상공인)'), 상생·하도급·신용평가 상투문,
미발급 안내('발급받지 못한 업체에 한함')뿐이었다. 이 모형대로 무라벨 공고에서 **그 밖의 기업규모 줄을 모두 지우고**
(자격 문장·확인서 유효기간 안내·간주 특별법인 문단) 정규식 파서가 '없음'을 읽는지 본다.
  python runs/del_probe_20260928/sme_delete.py SCRIPT.py OUT.pkl
결과: {id: dict(level, ev, price, method, band, kept=[남긴 줄])}"""
import sys, gzip, json, pickle, importlib.util, re
from pathlib import Path
from multiprocessing import Pool
ROOT = Path(__file__).resolve().parents[2]
M = TBL = None
W = re.compile(r"소기업|소상공인|중소기업|중기업")
# 운영진이 남긴 종류(dev 정답 공고 13건 판독)
KEEP_LIST = re.compile(r"\d+\s*부\b|각\s*1\s*부|사본|서류\s*$|증빙할\s*수\s*있는\s*서류")
KEEP_METHOD = re.compile(r"입\s*찰\s*방\s*법|계\s*약\s*방\s*법|제한\s*경쟁|경쟁\s*입찰|총액\s*입찰|단가\s*입찰|적격\s*심사|최저가|협상에\s*의한")
KEEP_BOILER = re.compile(r"상생|하도급|신용\s*평가|신용평가|제\s*8\s*조의\s*2|부정당|발급\s*받지\s*못한|발급\s*되지\s*않은\s*경우|평가|가점|배점|협동조합")
QUAL_VERB = re.compile(r"소지|보유|자격|업체|자로|자이어야|자\s*$|한함|한정|제한|대상")


def init(script):
    global M, TBL
    spec = importlib.util.spec_from_file_location("m", script); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    TBL = M.load_competitive_table(str(ROOT / "open" / "data"))


def keep_line(ln):
    if KEEP_LIST.search(ln) or KEEP_BOILER.search(ln):
        return True
    # 입찰방식 요약 줄: 방식 낱말이 있고 자격 동사(소지·보유·업체·자로 …)가 없다
    if KEEP_METHOD.search(ln) and not re.search(r"소지|보유|확인서|업체|자로서|자이어야|으로서", ln):
        return True
    return False


def edit(rec):
    kept, removed = [], 0
    for d in rec["docs"]:
        out = []
        lines = d["text"].split("\n")
        st = [x.strip() for x in lines]
        drop = set()
        for k, ln in enumerate(st):
            if not W.search(ln) or keep_line(ln):
                if W.search(ln):
                    kept.append(ln)
                continue
            s, e = M._sentence_span(st, k)
            drop.update(range(s, e + 1))
        for k, ln in enumerate(lines):
            if k in drop:
                removed += 1
                continue
            out.append(ln)
        d["text"] = "\n".join(out)
    return kept, removed


def work(line):
    r = M.normalize(json.loads(line))
    try:
        lv0, _ = M.rx_sme_level(r)
        if lv0 == "없음":
            return None
        p = M.price(r) or 0
        h0 = M.decide(r, "", TBL)[0]
        kept, removed = edit(r)
        lv, ev = M.rx_sme_level(r)
        h1 = M.decide(r, "", TBL)[0]
        band = "lt1" if p < 1e8 else ("mid" if p < 2.3e8 else "ge")
        return r["id"], dict(level=lv, ev=ev, lv0=lv0, price=p, band=band, method=r["meta"].get("계약방법"),
                             kept=kept, removed=removed, h0={k: h0[k] for k in ("v11", "v13", "v14", "v15", "v16", "v17", "v18")},
                             h1={k: h1[k] for k in ("v11", "v13", "v14", "v15", "v16", "v17", "v18")},
                             exc=M.has_procurement_exception(M.full_text(r)) or M.meta_exception(r))
    except Exception as ex:
        return r["id"], dict(err=repr(ex))


if __name__ == "__main__":
    lines = gzip.open(ROOT / "open" / "train_unlabeled.jsonl.gz", "rt", encoding="utf-8").readlines()
    with Pool(8, initializer=init, initargs=(sys.argv[1],)) as pool:
        res = [x for x in pool.map(work, lines, chunksize=50) if x]
    out = dict(res)
    pickle.dump(out, open(sys.argv[2], "wb"))
    from collections import Counter
    c = Counter((v.get("band"), v.get("level")) for v in out.values() if "err" not in v)
    print("restricted", len(out), "errors", sum("err" in v for v in out.values()))
    for k, n in sorted(c.items(), key=str): print(k, n)
