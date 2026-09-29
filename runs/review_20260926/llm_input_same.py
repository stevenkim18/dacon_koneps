"""두 후보 스크립트가 LLM에 보내는 메시지와 호출 대상 집합이 같은지 960건(dev 200 + 무라벨 750 + test 표본 10)에서 확인한다.
사용: llm_input_same.py BASE.py NEW.py"""
import sys, json, gzip, importlib.util
from pathlib import Path
R = Path(__file__).resolve().parents[2]
def load(p):
    s = importlib.util.spec_from_file_location("m" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
A, B = load(sys.argv[1]), load(sys.argv[2])
tbl = A.load_competitive_table(str(R / "open/data"))
recs = [json.loads(l) for l in open(R / "open/dev.jsonl", encoding="utf-8")]
recs += [json.loads(l) for f in ["runs/mlx/train_sample250.jsonl", "runs/mlx/train_sample500_next.jsonl"] for l in open(R / f, encoding="utf-8")]
recs += [json.loads(l) for l in gzip.open(R / "open/data/test.jsonl.gz", "rt", encoding="utf-8")]
class Tok:
    @staticmethod
    def count_tokens(ms): return sum(len(x["content"]) for x in ms) // 2
LAW = "법령 발췌(검사용 고정 문자열)"
diff = {}
def cmp(name, fa, fb):
    try: a = fa()
    except Exception as e: a = ("EXC", type(e).__name__)
    try: b = fb()
    except Exception as e: b = ("EXC", type(e).__name__)
    if a != b: diff.setdefault(name, []).append(rid)
for r in recs:
    ra, rb = A.normalize(json.loads(json.dumps(r))), B.normalize(json.loads(json.dumps(r)))
    rid = r["id"]
    cmp("main(fit_to_budget)", lambda: A.fit_to_budget(ra, tbl, Tok())[0], lambda: B.fit_to_budget(rb, tbl, Tok())[0])
    for n in ["needs_item_call", "needs_model_call", "needs_sme_call", "needs_perf_call", "needs_region_call", "needs_goods_item_call"]:
        cmp(n, lambda: getattr(A, n)(ra), lambda: getattr(B, n)(rb))
    cmp("item", lambda: A.build_item_messages(ra, tbl), lambda: B.build_item_messages(rb, tbl))
    cmp("model", lambda: A.build_model_messages(ra), lambda: B.build_model_messages(rb))
    cmp("sme", lambda: A.build_sme_messages(ra, LAW), lambda: B.build_sme_messages(rb, LAW))
    cmp("region", lambda: A.build_region_messages(ra, LAW), lambda: B.build_region_messages(rb, LAW))
    cmp("perf", lambda: A.build_perf_messages(ra, LAW), lambda: B.build_perf_messages(rb, LAW))
    cmp("goods_item", lambda: A.build_goods_item_messages(ra, tbl), lambda: B.build_goods_item_messages(rb, tbl))
print("records", len(recs), "· 차이:", {k: len(v) for k, v in diff.items()} or "없음")
