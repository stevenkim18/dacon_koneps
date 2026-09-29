"""V19L 후보: 제출서류 목록(머리글이 입찰 관련 서류)의 제조사 확약서 항목."""
import sys, re, json, csv, pickle, importlib.util, random
sys.path.insert(0, "runs/r18_20260928")
spec = importlib.util.spec_from_file_location("m", "submissions/20260929_r17_edit_shapes/script.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
ITEM_RE = re.compile(r"확약서")
MAKER_RE = re.compile(r"제조|공급|기술\s*지원|A/?S|기술\s*서비스")
HEAD_BID_RE = re.compile(r"입찰\s*(관련|참가|참여)?\s*(신청\s*)?(시\s*)?(제출\s*)?서류|입찰\s*(서\s*)?제출\s*시|입찰\s*시\s*제출|제출\s*서류|구비\s*서류|참가\s*(신청|등록)\s*(시\s*)?(제출\s*)?서류|전자\s*입찰\s*시|입찰\s*참가\s*신청")
HEAD_CONTRACT_RE = re.compile(r"계약\s*(체결\s*)?(시|전|후|서류|관련)|낙찰\s*(자|후)|적격\s*심사|계약\s*이행|납품\s*시|준공|검수|대금\s*청구|기술\s*평가|제안서")
EXCL_RE = M.V19_EXCL_RE
HEADISH = re.compile(r"^\s*(?:[가-하]\s*[\.\)]|\d{1,2}\s*[\.\)]|\(\s*[\d가-하]{1,2}\s*\)|[①-⑳]|[■□◆◇○●▶▷※]|\d\)\s)")
def v19_list(r):
    if not M.is_goods(r): return None
    for d in r["docs"]:
        L = [x.strip() for x in d["text"].split("\n")]
        for j, ln in enumerate(L):
            if not (ITEM_RE.search(ln) and MAKER_RE.search(ln)) or EXCL_RE.search(ln): continue
            if M.V19_BID_RE.search(ln): continue      # 이미 정규식이 보는 줄
            # 위로 올라가며 가장 가까운 머리글(입찰/계약)을 찾는다
            for k in range(j - 1, max(-1, j - 16), -1):
                h = L[k]
                if not h: continue
                if HEAD_CONTRACT_RE.search(h) and len(h) < 60: break
                if HEAD_BID_RE.search(h) and len(h) < 60:
                    return (h[:60], ln[:140])
    return None
if __name__ == "__main__":
    lab = {x['id']: x for x in csv.DictReader(open('open/dev_labels.csv'))}
    for l in open('open/dev.jsonl'):
        r = M.normalize(json.loads(l)); c = v19_list(r)
        if c or lab[r['id']]['v19'] == '1': print(r['id'], 'v19', lab[r['id']]['v19'], c)
    if len(sys.argv) > 1:
        from load20k import load
        pred = pickle.load(open("runs/replay_cache/20260929_r17_edit_shapes_script_3d4b038cc7.pkl", "rb"))
        hits = []
        for r in load():
            r = M.normalize(r); c = v19_list(r)
            if c and not pred[r['id']][18]: hits.append((r['id'], r['meta'].get('계약방법'), c))
        print(len(hits)); random.seed(7)
        for h in random.sample(hits, min(40, len(hits))): print(h)
