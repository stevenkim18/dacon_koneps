"""무라벨 20,000을 한 번 읽어 pickle로 캐시(분석용)."""
import gzip, json, pickle
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
CP = ROOT / "runs" / "replay_cache" / "u20k.pkl"
def load():
    if CP.exists():
        return pickle.load(open(CP, "rb"))
    recs = [json.loads(l) for l in gzip.open(ROOT / "open" / "train_unlabeled.jsonl.gz", "rt", encoding="utf-8")]
    CP.parent.mkdir(parents=True, exist_ok=True)
    pickle.dump(recs, open(CP, "wb"))
    return recs
if __name__ == "__main__":
    r = load(); print(len(r)); print(list(r[0].keys())); print(list(r[0]["meta"].keys()))
