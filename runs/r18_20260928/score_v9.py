"""V9 탐침·자연 공고 채점: 모델 호출 출력만 바꿔 v9 판정(is_goods ∧ 특정모델_지정 ∧ '동등' 없음)을 비교한다."""
import sys, json, importlib.util, csv
from pathlib import Path
T = Path("runs/r18_20260928"); P = T / "v9probe"
def L(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
B = L("submissions/20260929_r17_edit_shapes/script.py", "b"); V = L(str(T / "v9c.py"), "v")
def out(p):
    d = {}
    if Path(p).exists():
        for l in open(p, encoding="utf-8"):
            x = json.loads(l); d[x["id"]] = x.get("text", "")
    return d
def v9(M, r, mtext, main=None):
    llm = M.apply_model_call(r, dict(main or {}), mtext) if mtext else dict(main or {})
    ev = str((llm or {}).get("특정모델_근거") or "")
    return int(M.is_goods(r) and bool((llm or {}).get("특정모델_지정")) and "동등" not in ev), ev
# 1) H9 보류 탐침
lab = json.load(open(P / "probe_labels.json"))
recs = [B.normalize(json.loads(l)) for l in open(P / "probe.jsonl")]
bo, vo = out(P / "base_model_h9.jsonl"), out(P / "v9c_model_h9.jsonl")
hb = hv = 0; rows = []
for r in recs:
    a, ea = v9(B, r, bo.get(r["id"], "")); b, eb = v9(V, r, vo.get(r["id"], ""))
    hb += a; hv += b
    if a != b or not b: rows.append((r["id"], a, b, lab[r["id"]]["note"][:40], eb[:60]))
print(f"H9 보류 탐침(60): base {hb} → V9C {hv}")
for x in rows: print("   ", x)
# 2) r17 v9 탐침
recs = [B.normalize(json.loads(l)) for l in open(P / "r17v9.jsonl")]
bo = out("runs/r17_20260928/llm_probe/b4_model.jsonl"); vo = out(P / "v9c_model_r17.jsonl")
hb = hv = 0
for r in recs:
    hb += v9(B, r, bo.get(r["id"], ""))[0]; hv += v9(V, r, vo.get(r["id"], ""))[0]
print(f"r17 탐침(20): base {hb} → V9C {hv}  (본 호출 값 없이 모델 호출만)")
# 3) 자연 공고(dev·750 중 후보 줄이 바뀐 35건): 4bit 기준 출력 대비
lab = {r["id"]: r for r in csv.DictReader(open("open/dev_labels.csv"))}
b4 = {}
for p in ["runs/mlx/model_outputs.jsonl", "runs/mlx/train250_model.jsonl", "runs/mlx/train500_model.jsonl"]:
    b4.update(out(p))
i8 = out("runs/cloud_int8_exp/exp/raw/model.jsonl")
vo = out(P / "v9c_model_nat.jsonl")
recs = [B.normalize(json.loads(l)) for l in open(P / "nat_changed.jsonl")]
for r in recs:
    a4 = v9(B, r, b4.get(r["id"], ""))[0] if r["id"] in b4 else None
    a8 = v9(B, r, i8.get(r["id"], ""))[0] if r["id"] in i8 else None
    b, eb = v9(V, r, vo.get(r["id"], ""))
    if b != a4:
        print("  nat", r["id"], "dev_v9=" + lab[r["id"]]["v9"] if r["id"] in lab else "", "b4", a4, "i8", a8, "→ V9C4bit", b, "|", eb[:110])
