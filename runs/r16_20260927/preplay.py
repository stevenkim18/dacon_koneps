"""무라벨 20,000 정규식 경로 판정을 8프로세스로 병렬 재생한다(scripts/replay_unlabeled.py와 같은 캐시 형식·경로).
  python runs/r16_20260927/preplay.py BASE.py VAR.py [VAR2.py ...]   → 항목별 Δ, 변경 공고 목록(pkl)"""
import sys, gzip, json, pickle, hashlib, importlib.util, time
from pathlib import Path
from multiprocessing import Pool
from collections import Counter
ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "runs" / "replay_cache"
ITEMS = [f"v{i}" for i in range(1, 25)]
M = TBL = None
def init(script):
    global M, TBL
    spec = importlib.util.spec_from_file_location("m", script); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    TBL = M.load_competitive_table(str(ROOT / "open" / "data"))
def work(line):
    r = json.loads(line)
    try:
        t0 = time.time(); h = M.decide(r, "", TBL)[0]; dt = time.time() - t0
        return r["id"], tuple(h[v] for v in ITEMS), dt
    except Exception:
        return r["id"], None, 0.0
def run(script):
    h = hashlib.md5(Path(script).read_bytes()).hexdigest()[:10]
    cp = CACHE / f"{Path(script).parent.name}_{Path(script).stem}_{h}.pkl"
    if cp.exists():
        return pickle.load(open(cp, "rb")), None
    lines = gzip.open(ROOT / "open" / "train_unlabeled.jsonl.gz", "rt", encoding="utf-8").readlines()
    with Pool(8, initializer=init, initargs=(script,)) as pool:
        res = pool.map(work, lines, chunksize=50)
    out = {i: t for i, t, _ in res}
    pickle.dump(out, open(cp, "wb"))
    return out, max(res, key=lambda x: x[2])
if __name__ == "__main__":
    base, _ = run(sys.argv[1])
    for vs in sys.argv[2:]:
        var, slow = run(vs)
        d, changed = Counter(), []
        for i, t in var.items():
            b = base.get(i)
            if t is None or b is None or t == b: continue
            changed.append(i)
            for v, x, y in zip(ITEMS, b, t):
                if x != y: d[v] += y - x
        name = f"{Path(vs).parent.name}_{Path(vs).stem}"
        pickle.dump(changed, open(CACHE / f"changed_{name}.pkl", "wb"))
        print(f"{vs}: Δ{sum(d.values()):+d} · 변경 {len(changed)}공고 · 예외 {sum(t is None for t in var.values())} · "
              + " ".join(f"{v}{d[v]:+d}" for v in ITEMS if d[v]) + (f" · 최장 {slow[2]:.2f}s {slow[0]}" if slow else ""))
