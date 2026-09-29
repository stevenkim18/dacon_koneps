"""09-28 삭제 탐침(기업규모): 무라벨 20,000에서 정규식 파서가 기업규모 제한을 읽은 공고의 근거 문장(문장 범위)을
지우고 다시 읽기를 반복한다. 운영진이 v16·v18·v11 위반을 만들 때 자격 문장을 지운다면(dev 부재형 정답 공고는 서류 목록·
상투문만 남음), 지운 뒤에도 파서가 수준을 읽는 '잔재 줄'이 누락 원인이 된다.
  python runs/del_probe_20260928/sme_chain.py SCRIPT.py OUT.pkl   (8프로세스)
결과: {id: [(수준, 근거 줄, 문서 종류), ...]} — 첫 원소가 원래 근거, 다음 원소부터가 지운 뒤에도 남은 근거."""
import sys, gzip, json, pickle, importlib.util, copy
from pathlib import Path
from multiprocessing import Pool
ROOT = Path(__file__).resolve().parents[2]
M = TBL = None


def init(script):
    global M, TBL
    spec = importlib.util.spec_from_file_location("m", script); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    TBL = M.load_competitive_table(str(ROOT / "open" / "data"))


def delete_span(rec, ev):
    """근거 줄이 든 문장 범위(_sentence_span)를 지운다. 지운 줄 수를 돌려준다."""
    for d in rec["docs"]:
        lines = d["text"].split("\n")
        st = [ln.strip() for ln in lines]
        for k, ln in enumerate(st):
            if ln and ln == ev.strip():
                s, e = M._sentence_span(st, k)
                del lines[s:e + 1]
                d["text"] = "\n".join(lines)
                return e - s + 1
    return 0


def work(line):
    r = M.normalize(json.loads(line))
    try:
        lv, ev = M.rx_sme_level(r)
        if lv == "없음":
            return None
        chain = []
        r2 = copy.deepcopy(r)
        for _ in range(6):
            lv, ev = M.rx_sme_level(r2)
            if lv == "없음":
                break
            dtype = next((d["type"] for d in r2["docs"] if ev and ev in d["text"]), "?")
            chain.append((lv, ev, dtype))
            if not delete_span(r2, ev):
                chain.append(("삭제실패", ev, dtype)); break
        m = r["meta"]
        return r["id"], dict(chain=chain, price=M.price(r), method=m.get("계약방법"), comp_meta=[c for c in M.meta_item_codes(r) if c in TBL],
                             goods=M.is_goods(r), exc=M.has_procurement_exception(M.full_text(r)))
    except Exception as ex:
        return r["id"], dict(err=repr(ex))


if __name__ == "__main__":
    lines = gzip.open(ROOT / "open" / "train_unlabeled.jsonl.gz", "rt", encoding="utf-8").readlines()
    with Pool(8, initializer=init, initargs=(sys.argv[1],)) as pool:
        res = [x for x in pool.map(work, lines, chunksize=50) if x]
    out = dict(res)
    pickle.dump(out, open(sys.argv[2], "wb"))
    from collections import Counter
    c = Counter(len(v.get("chain", [])) for v in out.values())
    print("restricted notices", len(out), "chain length", sorted(c.items()))
