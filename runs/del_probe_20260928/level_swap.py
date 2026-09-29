"""09-28 수준 치환 탐침(v15·v17·v13): 실제 공고의 주 자격 문장(정규식 파서 근거 줄의 문장 범위)에서 기업규모 낱말을
운영진 편집처럼 바꾼다. dev 정답: DEV-076(본문 '중소기업 또는 소상공인' + 확인서만 '소기업·소상공인' → v13=1),
DEV-080(본문 소기업 + 뒤 안내문 '중소기업‧소상공인 확인서는…' 그대로 → v15=1), DEV-21(본문 중소기업 → v17=1).
  FULL: 본문+확인서 · BODY: 본문만 · CERT: 확인서 이름만
  python runs/del_probe_20260928/level_swap.py SCRIPT.py OUT.pkl"""
import sys, gzip, json, pickle, importlib.util, re, copy
from pathlib import Path
from multiprocessing import Pool
ROOT = Path(__file__).resolve().parents[2]
M = TBL = None
DOT = "·ㆍ‧․･•⋅∙・"
PROTECT = re.compile(r"[「『｢〔][^」』｣〕]{0,40}[」』｣〕]|중소기업\s*기본법|중소기업\s*범위|중소기업\s*제품|중소기업\s*공공구매|중소기업공공구매"
                     r"|중소\s*벤처|중소기업청|중소기업\s*간주|중소기업중앙회|중소기업협동조합|종합정보망|중소\s*소프트웨어")


def _sub_unprotected(s, pat, rep):
    out, last = [], 0
    for m in PROTECT.finditer(s):
        out.append(re.sub(pat, rep, s[last:m.start()])); out.append(m.group(0)); last = m.end()
    out.append(re.sub(pat, rep, s[last:]))
    return "".join(out)


CERT_SME = rf"(중\s*[{DOT}/]?\s*소기업\s*[{DOT}]?\s*(?:,|또는|및)?\s*소상공인\s*확인서|중\s*[{DOT}/]?\s*소기업\s*(?:또는|및)\s*소상공인\s*확인서|중\s*[{DOT}/]?\s*소기업\s*확인서|중기업\s*[,{DOT}]\s*소기업\s*[,{DOT}]?\s*(?:또는)?\s*소상공인\s*확인서)"
CERT_SMALL = rf"((?<![중{DOT}])소기업\s*(?:[{DOT},]|또는|및)?\s*소상공인\s*확인서|(?<![중{DOT}])소기업\s*확인서)"


def to_small(s, mode):
    if mode in ("FULL", "CERT"):
        s = re.sub(CERT_SME, "소기업·소상공인 확인서", s)
    if mode in ("FULL", "BODY"):
        # 확인서 이름은 건드리지 않도록 잠시 가린다
        certs = []
        def hide(m):
            certs.append(m.group(0)); return f"\x00{len(certs) - 1}\x00"
        s = re.sub(CERT_SME + "|" + CERT_SMALL, hide, s)
        s = _sub_unprotected(s, rf"중기업\s*[,{DOT}]\s*소기업", "소기업")
        s = _sub_unprotected(s, rf"중\s*[{DOT}/]\s*소기업", "소기업")
        s = _sub_unprotected(s, r"중소기업", "소기업")
        s = re.sub(r"\x00(\d+)\x00", lambda m: certs[int(m.group(1))], s)
    return s


def to_mid(s, mode):
    if mode in ("FULL", "CERT"):
        s = re.sub(CERT_SMALL, "중소기업·소상공인 확인서", s)
    if mode in ("FULL", "BODY"):
        certs = []
        def hide(m):
            certs.append(m.group(0)); return f"\x00{len(certs) - 1}\x00"
        s = re.sub(CERT_SME + "|" + CERT_SMALL, hide, s)
        s = _sub_unprotected(s, rf"(?<![중{DOT}/])소기업", "중소기업")
        s = re.sub(r"\x00(\d+)\x00", lambda m: certs[int(m.group(1))], s)
    return s


def init(script):
    global M, TBL
    spec = importlib.util.spec_from_file_location("m", script); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    TBL = M.load_competitive_table(str(ROOT / "open" / "data"))


def swap(rec, ev, fn, mode):
    r2 = copy.deepcopy(rec)
    for d in r2["docs"]:
        lines = d["text"].split("\n")
        st = [x.strip() for x in lines]
        for k, ln in enumerate(st):
            if ln and ln == ev.strip():
                s, e = M._sentence_span(st, k)
                new = [fn(x, mode) for x in lines[s:e + 1]]
                changed = new != lines[s:e + 1]
                lines[s:e + 1] = new
                d["text"] = "\n".join(lines)
                return r2, changed, " / ".join(x.strip() for x in new)[:400]
    return r2, False, ""


def work(line):
    r = M.normalize(json.loads(line))
    try:
        lv, ev = M.rx_sme_level(r)
        if lv == "없음" or not ev:
            return None
        p = M.price(r) or 0
        if p < 1e6 or M._meta_method(r) == "수의계약":
            return None
        rx = M.regex_facts(r, TBL)
        comp = M.is_competitive(rx, r, TBL)
        exc = M.has_procurement_exception(M.full_text(r))
        tasks = []
        if comp and lv == "중소기업":
            tasks.append(("v13", to_small))
        if not comp and not exc and 1e8 <= p < 2.3e8 and lv == "중소기업":
            tasks.append(("v15", to_small))
        if not comp and not exc and p < 1e8 and lv == "소기업·소상공인" and not M.SMALL_PROVISO_RE.search(M.full_text(r)):
            tasks.append(("v17", to_mid))
        if not tasks:
            return None
        h0 = M.decide(r, "", TBL)[0]
        out = {}
        for item, fn in tasks:
            if h0[item]:
                continue
            for mode in ("FULL", "BODY", "CERT"):
                r2, changed, new = swap(r, ev, fn, mode)
                if not changed:
                    continue
                h1 = M.decide(r2, "", TBL)[0]
                lv2, ev2 = M.rx_sme_level(r2)
                out[(item, mode)] = dict(hit=h1[item], lv2=lv2, ev2=ev2[:200], new=new)
        return (r["id"], out) if out else None
    except Exception as ex:
        return r["id"], {("err", "err"): repr(ex)}


if __name__ == "__main__":
    lines = gzip.open(ROOT / "open" / "train_unlabeled.jsonl.gz", "rt", encoding="utf-8").readlines()
    with Pool(8, initializer=init, initargs=(sys.argv[1],)) as pool:
        res = [x for x in pool.map(work, lines, chunksize=50) if x]
    out = dict(res)
    pickle.dump(out, open(sys.argv[2], "wb"))
    from collections import Counter
    n, h = Counter(), Counter()
    for v in out.values():
        for k, x in v.items():
            if k[0] == "err":
                n[k] += 1; continue
            n[k] += 1; h[k] += x["hit"]
    for k in sorted(n): print(k, f"{h[k]}/{n[k]}")
