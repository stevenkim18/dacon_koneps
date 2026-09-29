"""09-28 삭제 탐침(v10 직생 · v20 SW 대기업 참여제한): 운영진 편집 모형 — 자격 문장·안내문은 지우고 서류 목록·
위반 제재 상투문은 남긴다(dev v10 정답 7건: '각 1부' 목록, '직접생산 확인기준을 위반한 …' 상투문만 남음 ·
v20 정답 5건: 대기업 낱말 0).
  python runs/del_probe_20260928/absence_delete.py SCRIPT.py OUT.pkl"""
import sys, gzip, json, pickle, importlib.util, re
from pathlib import Path
from multiprocessing import Pool
ROOT = Path(__file__).resolve().parents[2]
M = TBL = None
DW = re.compile(r"직접\s*생산|직생")
D_KEEP = re.compile(r"\d+\s*부\b|각\s*1\s*부|사본|위반|하도급|하청|타사\s*제품|확인\s*기준을")
SW = re.compile(r"대기업|상호\s*출자|중견\s*기업|제\s*48\s*조(?!\s*의)|사업\s*금액\s*(하한|기준)|하한\s*(제|금액)")


def init(script):
    global M, TBL
    spec = importlib.util.spec_from_file_location("m", script); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    TBL = M.load_competitive_table(str(ROOT / "open" / "data"))


def delete(rec, word, keep):
    kept = []
    for d in rec["docs"]:
        lines = d["text"].split("\n")
        st = [x.strip() for x in lines]
        drop = set()
        for k, ln in enumerate(st):
            if not word.search(ln):
                continue
            if keep is not None and keep.search(ln):
                kept.append(ln); continue
            s, e = M._sentence_span(st, k)
            drop.update(range(s, e + 1))
        d["text"] = "\n".join(ln for k, ln in enumerate(lines) if k not in drop)
    return kept


def work(line):
    r = M.normalize(json.loads(line))
    try:
        h0 = M.decide(r, "", TBL)[0]
        rx = M.regex_facts(r, TBL)
        out = {}
        src = M.full_text(r)
        # v10: 정규식 경로에서 경쟁제품 입찰로 판정되는 공고 중 직생 요구가 있어 v10=0인 것
        comp = M.is_competitive(rx, r, TBL)
        if comp and M._meta_method(r) != "수의계약" and not h0["v10"] and (rx["직접생산확인_요구"] or rx["직접생산_언급_넓게"]):
            import copy
            r2 = copy.deepcopy(r)
            kept = delete(r2, DW, D_KEEP)
            h1 = M.decide(r2, "", TBL)[0]
            rx2 = M.regex_facts(r2, TBL)
            left = [ln for d in r2["docs"] for ln in d["text"].split("\n") if DW.search(ln)]
            out["v10"] = dict(hit=h1["v10"], kept=kept, left=left[:6], req=rx2["직접생산확인_요구"], broad=rx2["직접생산_언급_넓게"],
                              gate=dict(exempt=M.competitive_exempt(r2), note=M.note_condition_met(r2, TBL.get(str(rx2["계약목적물_세부품명번호"])) or {})))
        # v20: SW 공고에서 대기업 참여제한 문구 때문에 v20=0인 것
        p = M.price(r) or 0
        if M.is_software(r) and p >= 1e6 and not h0["v20"] and rx["대기업_참여제한_문구"] and \
                (p >= 1e8 or (bool(M.SW_OBJECT_RE.search(M.title_of(r))) and M._meta_method(r) != "수의계약")):
            import copy
            r2 = copy.deepcopy(r)
            delete(r2, SW, None)
            h1 = M.decide(r2, "", TBL)[0]
            src2 = M.full_text(r2)
            left = [m.group(0) + " @ " + src2[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
                    for m in re.finditer(r"대기업|상호출자제한|중견기업", src2)][:4]
            out["v20"] = dict(hit=h1["v20"], left=left, noted=M.sw_big_limit_noted(src2))
        return (r["id"], out) if out else None
    except Exception as ex:
        return r["id"], dict(err=repr(ex))


if __name__ == "__main__":
    lines = gzip.open(ROOT / "open" / "train_unlabeled.jsonl.gz", "rt", encoding="utf-8").readlines()
    with Pool(8, initializer=init, initargs=(sys.argv[1],)) as pool:
        res = [x for x in pool.map(work, lines, chunksize=50) if x]
    out = dict(res)
    pickle.dump(out, open(sys.argv[2], "wb"))
    for v in ("v10", "v20"):
        rows = [x[v] for x in out.values() if v in x]
        print(v, "pool", len(rows), "fires after delete", sum(x["hit"] for x in rows))
    print("errors", sum("err" in x for x in out.values()))
