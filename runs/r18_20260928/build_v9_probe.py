"""V9 보류 탐침 H9: V9C 설계 뒤 새로 쓴 모델명·제조사 지정 줄 30개를 물품 공고(무라벨 750, 기준 v9=0)의 규격서류에 넣는다.
  python runs/r18_20260928/build_v9_probe.py OUT_DIR"""
import sys, json, gzip, copy, random, re, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("m", str(ROOT / "submissions/20260929_r17_edit_shapes/script.py")); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
H9 = ["CPU: 인텔 코어 울트라 7 155H 프로세서", "모니터: LG전자 27UP850N 27인치", "노트북: 삼성 갤럭시북4 프로 NT960XGK", "복합기: 신도리코 D451 흑백 레이저",
      "태블릿: Apple iPad Air 11 (M2) Wi-Fi 128GB", "소프트웨어: Microsoft Office LTSC Standard 2024", "측정 장비는 Keysight 사의 N9020B MXA 신호분석기로 한다",
      "현미경: Olympus CX43 생물현미경", "원심분리기(한일과학 Combi-514R)", "트랙터: 대동 HX1400 (140마력)", "영상장치: 소니 FX6 시네마 카메라 바디",
      "빔프로젝터 엡손 EB-L630U", "네트워크 스위치: Cisco Catalyst 9300-48P", "방화벽: Fortinet FortiGate 200F", "냉난방기: 캐리어 CPV-Q1308DX 스탠드형",
      "청소기: 다이슨 V15 디텍트", "스캐너: 후지쯔 fi-8170", "3D프린터: Stratasys J55 Prime", "드론: DJI Mavic 3 Enterprise(M3E)",
      "펌프: 그런포스(Grundfos) CR 32-2", "분광광도계 Shimadzu UV-1900i", "보안카메라: 하이크비전 DS-2CD2387G2", "서버: Dell PowerEdge R760",
      "UPS: APC Smart-UPS SRT 3000VA", "전동공구: 마키타 DHP486Z 충전드릴", "제세동기: 필립스 하트스타트 HS1", "로봇청소기 삼성 비스포크 AI 스팀",
      "음향 콘솔: Yamaha CL5 디지털 믹서", "제조사: 한국○○정밀, 모델: KP-500", "승합차: 현대 스타리아 11인승 투어러"]
raw = ROOT / "runs/cloud_int8_exp/exp/raw"
mo = {json.loads(l)["id"]: json.loads(l).get("text", "") for l in open(raw / "model.jsonl", encoding="utf-8")}
recs = [M.normalize(json.loads(l)) for l in gzip.open(ROOT / "open/exp950.jsonl.gz", "rt", encoding="utf-8")]
pool = []
for r in recs:
    if r["id"].startswith("PPS-DEV") or r.get("dropped_doc_counts") or not M.is_goods(r):
        continue
    res = M.parse_facts(mo.get(r["id"], "")) or {}
    if not res.get("특정모델_지정"):
        pool.append(r)
rng = random.Random(9280)
rng.shuffle(pool)
out, lab = [], {}
def insert(r, sent):
    r = copy.deepcopy(r)
    docs = [d for d in r["docs"] if d["type"] in ("규격서", "과업지시서", "제안요청서")] or [d for d in r["docs"] if d["type"] == "공고문"] or r["docs"]
    d = docs[0]; L = d["text"].split("\n")
    ks = [j for j, x in enumerate(L) if re.search(r"규\s*격|사\s*양|요구\s*사항|구성|품\s*명", x)]
    k0 = ks[0] if ks else len(L) // 3
    L.insert(k0 + 1, sent); d["text"] = "\n".join(L)
    return r
k = 0
for n, sent in enumerate(H9):
    for rep in range(2):
        b = pool[k]; k += 1
        r2 = insert(b, sent); nid = f"H9-{n:02d}{rep}-{b['id'][-6:]}"; r2["id"] = nid
        out.append(r2); lab[nid] = {"item": "v9", "base": b["id"], "kind": "v9h9", "note": sent}
with open(OUT / "probe.jsonl", "w", encoding="utf-8") as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump(lab, open(OUT / "probe_labels.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "pool", len(pool))
