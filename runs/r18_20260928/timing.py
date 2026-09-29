"""무라벨 20,000 중 본문이 가장 긴 공고 365건에서 decide(정규식 경로) 시간을 두 스크립트로 잰다."""
import sys, time, importlib.util
sys.path.insert(0, "runs/r18_20260928")
from load20k import load
recs = sorted(load(), key=lambda r: -sum(len(d["text"]) for d in r["docs"]))[:365]
for p in sys.argv[1:]:
    s = importlib.util.spec_from_file_location("m" + str(abs(hash(p))), p); M = importlib.util.module_from_spec(s); s.loader.exec_module(M)
    T = M.load_competitive_table("open/data"); t0 = time.time(); mx = 0
    for r in recs:
        r = M.normalize(r); a = time.time(); M.decide(r, "", T); mx = max(mx, time.time() - a)
    print(f"{p}: {time.time() - t0:.1f}초 (최대 {mx:.2f}초/건)")
