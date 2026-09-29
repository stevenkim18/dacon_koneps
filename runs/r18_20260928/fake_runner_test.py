"""V9X 서버 경로 점검: MockRunner.chat을 스키마에 맞는 JSON을 내는 가짜로 바꿔 run() 전 단계를 돌린다.
본 호출 = 빈 출력(정규식 사실만), 모델명 호출·보조 호출 = 줄번호 1 '지정'. 기존 모델명 호출이 없는(후보 줄 0) 물품 공고에서만
보조 호출이 돌고, 그 판정이 CSV에 v9=1·근거(원문 부분문자열)로 들어가는지 본다.
  python runs/r18_20260928/fake_runner_test.py SCRIPT.py INPUT.jsonl(.gz) OUTDIR"""
import sys, json, importlib.util, csv, os, gzip
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
calls = {"model": 0}
def chat(self, batch, schema=None, max_tokens=None):
    out = []
    for msgs in batch:
        if schema and set(schema.get("properties", {})) == {"특정모델_지정", "줄번호"}:
            calls["model"] += 1
            out.append(json.dumps({"특정모델_지정": True, "줄번호": 1}, ensure_ascii=False))
        else:
            out.append("")
    return out
M.MockRunner.chat = chat
os.makedirs(sys.argv[3], exist_ok=True)
rep = M.run(sys.argv[2], os.path.join(sys.argv[3], "submission.csv"), M.MockRunner, limit=None, chunk=64, data_dir="open/data")
print("report", {k: rep[k] for k in rep if k in ("건수", "자가검증", "전체_s")}, "model-schema calls", calls["model"])
op = gzip.open if sys.argv[2].endswith(".gz") else open
recs = {json.loads(l)["id"]: M.normalize(json.loads(l)) for l in op(sys.argv[2], "rt", encoding="utf-8")}
n2 = [i for i, r in recs.items() if M.needs_model2_call(r) and not M.needs_model_call(r)]
rows = {r["id"]: r for r in csv.DictReader(open(os.path.join(sys.argv[3], "submission.csv"), encoding="utf-8"))}
ok = sum(rows[i]["v9"] == "1" for i in n2)
bad = [i for i in n2 if rows[i]["v9"] == "1" and rows[i]["e9"] not in M.full_text(recs[i])]
print("model2-only goods notices", len(n2), "v9=1", ok, "evidence not substring", bad[:3])
