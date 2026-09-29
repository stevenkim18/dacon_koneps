"""P2(막연한 실적 요구) 첫 판이 무라벨 20,000(정규식 재생)에서 새로 켠 v2·v4·v8 판정과 판독 분류를 CSV로 남긴다.
분류는 09-25 대화형 판독 결과다(원문 줄을 읽고 입찰참가자격으로 입찰자의 실적을 요구하는지 판단):
  G  = 입찰자 실적 요구(참가자격)            T  = 학교 여행·수련 상투문 '유경험업체로서 실적이 우수하고 건실한 업체'
  FP = 입찰자 자격이 아님(협력방안·대행사·'…업체에게 제작'·제품 사용실적·인력 구성·인건비 적용계수·조문 인용)
최종판(PERF_VAGUE_EXCL_RE)에서 여전히 켜지는지도 적는다.
사용: vague_perf_audit.py BASE.py FIRST_CUT.py FINAL.py OUT.csv"""
import csv, gzip, json, re, sys, importlib.util
def load(p):
    s = importlib.util.spec_from_file_location("m" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
base, first, final = (load(p) for p in sys.argv[1:4])
out = sys.argv[4]
FP = {"PPS-D-015721", "PPS-D-020441", "PPS-D-020233", "PPS-D-019694", "PPS-D-007162", "PPS-D-017969", "PPS-D-016516",
      "PPS-D-013724", "PPS-D-013831", "PPS-D-010336", "PPS-D-000249"}
T_RE = re.compile(r"유\s*경험[^\n]{0,20}실적이\s*우수|실적이\s*우수하고\s*건실")
tbl = base.load_competitive_table("open/data")
rows = []
for l in gzip.open("open/train_unlabeled.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(l)
    if base.rx_performance(r):
        continue
    new = first.rx_performance(r)
    if not new:
        continue
    hb, hf, hn = (m.decide(r, "", tbl)[0] for m in (base, first, final))
    for item in ("v2", "v4", "v8"):
        if hf[item] and not hb[item]:
            line = new[0]
            cls = "FP" if r["id"] in FP else ("T" if any(T_RE.search(s) for s in new) else "G")
            mt = r["meta"]
            rows.append([r["id"], item, mt.get("적용계약법"), mt.get("계약방법"), mt.get("낙찰방법"), mt.get("입찰추정가격"),
                         line[:300], cls, int(bool(hn[item])), "claude-opus-5.5(대화형 판독)"])
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "항목", "적용계약법", "계약방법", "낙찰방법", "추정가격", "새_실적_줄", "분류(G/T/FP)", "최종판_발동", "생성자"])
    w.writerows(rows)
from collections import Counter
print(len(rows), Counter((x[1], x[7], x[8]) for x in rows))
