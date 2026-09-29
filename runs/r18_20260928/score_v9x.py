"""V9X 채점: 기존 모델명 호출 출력 + 보조 호출(model2) 출력을 MODEL2_SEP로 이어 decide()에 넘긴다."""
import sys, json, csv, importlib.util
from pathlib import Path
T = Path("runs/r18_20260928"); P = T / "v9probe"
def L(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
B = L("submissions/20260929_r17_edit_shapes/script.py", "b"); V = L(sys.argv[1] if len(sys.argv) > 1 else str(T / "v9x.py"), "v")
TB = B.load_competitive_table("open/data")
def out(*ps):
    d = {}
    for p in ps:
        if Path(p).exists():
            for l in open(p, encoding="utf-8"):
                x = json.loads(l); d[x["id"]] = x.get("text", "")
    return d
def v9(M, r, main, mtext, m2=None):
    txt = mtext + (V.MODEL2_SEP + m2 if m2 is not None and M is V else "")
    h, e, _ = M.decide(r, main, TB, model_text=txt)
    return h["v9"], e.get("v9", "")
def run(name, recs, main, base_model, m2, lab=None):
    hb = hv = 0; diff = []
    for r in recs:
        i = r["id"]; bm = base_model.get(i, "")
        a, _ = v9(B, r, main.get(i, ""), bm); b, eb = v9(V, r, main.get(i, ""), bm, m2.get(i, "") if V.needs_model2_call(r) else None)
        hb += a; hv += b
        if a != b: diff.append((i, a, b, (lab or {}).get(i, ""), eb[:100]))
    print(f"{name}: base {hb} → V9X {hv} / {len(recs)}")
    for x in diff: print("    ", x)
# H9: 본 호출 출력은 원 공고의 int8 출력(탐침 편집 전) — v9는 모델명 호출이 덮어쓰므로 영향 작음
i8main = out("runs/cloud_int8_exp/exp/raw/main.jsonl")
labH = json.load(open(P / "probe_labels.json"))
recs = [B.normalize(json.loads(l)) for l in open(P / "probe.jsonl")]
mainH = {r["id"]: i8main.get(labH[r["id"]]["base"], "") for r in recs}
run("H9 보류 탐침(4bit 모델 호출)", recs, mainH, out(P / "base_model_h9.jsonl"), out(P / "m2_h9.jsonl"), {k: v["note"][:30] for k, v in labH.items()})
labR = json.load(open("runs/r17_20260928/llm_probe/probe_labels.json"))
recs = [B.normalize(json.loads(l)) for l in open(P / "r17v9.jsonl")]
run("r17 탐침(4bit 본 호출·모델 호출)", recs, out("runs/r17_20260928/llm_probe/b4_main.jsonl"), out("runs/r17_20260928/llm_probe/b4_model.jsonl"), out(P / "m2_r17.jsonl"), {k: v["note"][:30] for k, v in labR.items()})
# 자연: dev·750 (4bit 기존 출력 / int8 기존 출력) + 4bit 보조 호출
dl = {r["id"]: "dev_v9=" + r["v9"] for r in csv.DictReader(open("open/dev_labels.csv"))}
recs = [B.normalize(json.loads(l)) for l in open(P / "nat_m2.jsonl")]
m2 = out(P / "m2_nat.jsonl")
run("자연 dev+750 (4bit 기존)", recs, out("runs/mlx/extract_outputs.jsonl", "runs/mlx/train250_main.jsonl", "runs/mlx/train500_main.jsonl"),
    out("runs/mlx/model_outputs.jsonl", "runs/mlx/train250_model.jsonl", "runs/mlx/train500_model.jsonl"), m2, dl)
run("자연 dev+750 (int8 기존 + 4bit 보조)", recs, i8main, out("runs/cloud_int8_exp/exp/raw/model.jsonl"), m2, dl)
