"""09-28 LLM 경로 편집 탐침 묶음: 무라벨 750(저장 int8 출력 있음)에서 항목별로 '기준 판정 0' 공고를 골라 운영진식 편집을 한다.
편집한 공고에 LLM(로컬 MLX 4bit 또는 서버 int8)을 다시 돌려 전 파이프라인 재현율을 잰다(규칙 경로 탐침으로는 안 보이는 항목).
  v11: 경쟁제품 입찰 · 기업규모 자격 줄 삭제(서류 목록·입찰방식 요약·상투문은 남김 — dev 부재형 정답 공고 모형)
  v13: 경쟁제품 · 주 자격 문장 수준을 소기업·소상공인으로(본문+확인서)
  v15: 비경쟁 1억~고시금액 · 중소기업 → 소기업·소상공인        v17: 비경쟁 1억 미만 · 소기업 → 중소기업
  v10: 경쟁제품 용역 · 직생 요구 줄 삭제(서류 목록·위반 제재 상투문은 남김)
  v1 : 특정기관 한정 문장 삽입(H·H2·H3·H4·Q 세트)       v19: 확약서 입찰 시 제출 문장 삽입       v9: 규격서 특정 모델명 줄 삽입
  python runs/r17_20260928/build_llm_probe.py SCRIPT.py OUT_DIR"""
import sys, json, gzip, copy, random, re, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "runs/del_probe_20260928"), str(ROOT / "runs/recall_probe_20260926"), str(ROOT / "runs/wrapjoin_20260927")]
SCRIPT, OUT = sys.argv[1], Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("m", SCRIPT); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
import sme_delete as SD, level_swap as LS, absence_delete as AD
SD.M = LS.M = AD.M = M
from probe_paraphrases import Q, H, H2
from probe_h3 import H3
from probe_h4 import H4
TBL = M.load_competitive_table(str(ROOT / "open/data"))
raw = ROOT / "runs/cloud_int8_exp/exp/raw"


def saved(n):
    d = {}
    for l in open(raw / f"{n}.jsonl", encoding="utf-8"):
        r = json.loads(l); d[r["id"]] = r.get("text", "")
    return d


S = {k: saved(k) for k in ("main", "item", "model", "sme", "region")}
recs = [M.normalize(json.loads(l)) for l in gzip.open(ROOT / "open/exp950.jsonl.gz", "rt", encoding="utf-8")]
recs = [r for r in recs if not r["id"].startswith("PPS-DEV") and not r.get("dropped_doc_counts") and S["main"].get(r["id"])]
cap = {}
_orig_merge = M.merge_facts


def spy(llm, rx, policy):
    out = _orig_merge(llm, rx, policy)
    cap[policy.get("계약목적물_세부품명번호", "llm")] = out
    return out


M.merge_facts = spy
info = {}
for r in recs:
    i = r["id"]; cap.clear()
    h = M.decide(r, S["main"][i], TBL, item_text=S["item"].get(i, ""), model_text=S["model"].get(i, ""),
                 sme_text=S["sme"].get(i, ""), region_text=S["region"].get(i, ""))[0]
    f = cap.get("llm") or cap.get("or") or {}
    lv, ev = M.rx_sme_level(r)
    info[i] = dict(h=h, comp=M.is_competitive(f, r, TBL), lv=lv, ev=ev, p=M.price(r) or 0,
                   priv=M._meta_method(r) == "수의계약", exc=M.has_procurement_exception(M.full_text(r)) or M.meta_exception(r),
                   goods=M.is_goods(r), svc=M.needs_item_call(r), rxf=M.regex_facts(r, TBL),
                   proviso=bool(M.SMALL_PROVISO_RE.search(M.full_text(r))))
M.merge_facts = _orig_merge
rng = random.Random(928)
byid = {r["id"]: r for r in recs}
out, lab = [], {}


def add(kind, item, r2, base_id, note=""):
    nid = f"PRB-{kind}-{base_id[-6:]}-{len(out):03d}"
    r2 = copy.deepcopy(r2); r2["id"] = nid
    out.append(r2); lab[nid] = dict(item=item, base=base_id, kind=kind, note=note[:200])


def pick(cond, n):
    ids = [i for i in info if cond(info[i])]
    rng.shuffle(ids)
    return ids[:n]


def insert(r, sent, doc_pred=lambda d: d["type"] == "공고문"):
    r = copy.deepcopy(r)
    for d in r["docs"]:
        if not doc_pred(d):
            continue
        lines = d["text"].split("\n")
        ks = [j for j, x in enumerate(lines) if re.search(r"참가\s*자격|규\s*격|사\s*양|요구\s*사항", x)]
        k0 = ks[0] if ks else len(lines) // 3
        lines.insert(k0 + 1, sent); d["text"] = "\n".join(lines)
        return r, True
    return r, False


# v11: 경쟁제품 · 기업규모 자격 줄 삭제
for i in pick(lambda x: x["comp"] and not x["priv"] and not x["exc"] and x["lv"] != "없음" and not x["h"]["v11"], 25):
    r2 = copy.deepcopy(byid[i]); SD.edit(r2)
    add("v11del", "v11", r2, i)
# v13: 경쟁제품 · 중소기업 → 소기업
for i in pick(lambda x: x["comp"] and not x["priv"] and x["lv"] == "중소기업" and not x["h"]["v13"], 20):
    r2, ch, new = LS.swap(byid[i], info[i]["ev"], LS.to_small, "FULL")
    if ch: add("v13swap", "v13", r2, i, new)
# v15: 비경쟁 1억~고시 · 중소기업 → 소기업
for i in pick(lambda x: not x["comp"] and not x["priv"] and not x["exc"] and 1e8 <= x["p"] < 2.3e8 and x["lv"] == "중소기업" and not x["h"]["v15"], 20):
    r2, ch, new = LS.swap(byid[i], info[i]["ev"], LS.to_small, "FULL")
    if ch: add("v15swap", "v15", r2, i, new)
# v17: 비경쟁 1억 미만 · 소기업 → 중소기업
for i in pick(lambda x: not x["comp"] and not x["priv"] and not x["exc"] and 1e6 <= x["p"] < 1e8 and x["lv"] == "소기업·소상공인" and not x["h"]["v17"]
              and not x["proviso"], 15):
    r2, ch, new = LS.swap(byid[i], info[i]["ev"], LS.to_mid, "FULL")
    if ch: add("v17swap", "v17", r2, i, new)
# v10: 경쟁제품 용역 · 직생 삭제
for i in pick(lambda x: x["comp"] and x["svc"] and not x["priv"] and not x["h"]["v10"] and (x["rxf"]["직접생산확인_요구"] or x["rxf"]["직접생산_언급_넓게"]), 25):
    r2 = copy.deepcopy(byid[i]); AD.delete(r2, AD.DW, AD.D_KEEP)
    add("v10del", "v10", r2, i)
# v1: 특정기관 한정 문장 삽입
V1 = H4["v1"] + H3["v1"] + H2["v1"] + H["v1"] + Q["v1"]
for n, i in enumerate(pick(lambda x: not x["priv"] and not x["h"]["v1"], 30)):
    sent = V1[n % len(V1)]
    r2, ok = insert(byid[i], sent)
    if ok: add("v1ins", "v1", r2, i, sent)
# v19: 확약서 입찰 시 제출 삽입
V19 = H4["v19"] + Q["v19"]
for n, i in enumerate(pick(lambda x: x["goods"] and not x["h"]["v19"], 20)):
    sent = V19[n % len(V19)]
    r2, ok = insert(byid[i], sent)
    if ok: add("v19ins", "v19", r2, i, sent)
# v9: 규격서·과업지시서 특정 모델명 줄 삽입(dev 정답 모양: 부품 칩셋·제조사·모델명·형식명)
V9 = ["- 제조사·모델명 : 한화비전(Hanwha Vision) XNO-C9083R", "Chipset: Intel Core Ultra 7 265H 이상 아닌 동일 모델", "형식명 : KBT-2450HX(대동공업)",
      "• 본체: 삼성전자 NT960XGQ-A51A 1식", "CPU: AMD Ryzen 9 9950X3D", "분석장비: Thermo Fisher iCAP PRO XP ICP-OES", "살수 노즐: 아크론브라스 터보젯 1720",
      "드론 배터리: DJI Matrice 30 시리즈 TB30 인텔리전트 플라이트 배터리일 것", "측정기(모델 HD-3200P, 한국계측)", "GPU: NVIDIA RTX A6000 48GB"]
for n, i in enumerate(pick(lambda x: x["goods"] and not x["h"]["v9"], 20)):
    sent = V9[n % len(V9)]
    r2, ok = insert(byid[i], sent, lambda d: d["type"] in ("규격서", "과업지시서", "제안요청서"))
    if not ok:
        r2, ok = insert(byid[i], sent)
    if ok: add("v9ins", "v9", r2, i, sent)
with open(OUT / "probe.jsonl", "w", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump(lab, open(OUT / "probe_labels.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(len(out), Counter(v["kind"] for v in lab.values()))
