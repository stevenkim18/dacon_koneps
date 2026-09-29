#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""원문 전체 창 분할 실험 — 정규식 그물로 발췌하는 대신 원문 전체를 창으로 잘라 전부 읽힌다.

현재 본 호출은 13개 정규식 그물이 고른 줄만 본다(dev 중앙값 커버리지 49.2%).
이 스크립트는 같은 스키마·같은 지시문으로 원문을 ~10k 토큰 창으로 잘라 창마다 추출하고 사실을 병합한다.

  생성:  python scripts/window_sweep.py --generate --out runs/mlx/win_dev.jsonl
  채점:  python scripts/window_sweep.py --score   --out runs/mlx/win_dev.jsonl
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
ITEMS = [f"v{i}" for i in range(1, 25)]
CAND = ROOT / "submissions" / "20260922_focused_calls" / "script.py"


def log(m): print(f"[window_sweep] {m}", file=sys.stderr, flush=True)


def load_mod(p: Path):
    s = importlib.util.spec_from_file_location("cand", p); mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod); return mod


def windows(mod, rec, tok, win_tokens: int) -> List[str]:
    """원문을 줄 단위로 창에 담는다. 문서 경계는 유지하고, 창마다 앞 창의 마지막 2줄을 겹친다."""
    pieces: List[str] = []
    for d in rec["docs"]:
        pieces.append(f"=== [{d['type']}] ===")
        pieces.extend(d["text"].splitlines())
    out, cur, n = [], [], 0
    for line in pieces:
        t = len(tok.encode(line, add_special_tokens=False)) + 1
        if n + t > win_tokens and cur:
            out.append("\n".join(cur)); cur = cur[-2:]; n = sum(len(tok.encode(x, add_special_tokens=False)) + 1 for x in cur)
        cur.append(line); n += t
    if cur: out.append("\n".join(cur))
    return out or [""]


def build_window_messages(mod, rec, table, wtext: str, k: int, total: int):
    m = rec.get("meta", {})
    meta_lines = "\n".join(f"- {kk}: {'미기재' if m.get(kk) is None else m.get(kk)}" for kk in mod.META_FIELDS if kk in m)
    cands = mod.candidate_items(rec, table)
    cand_lines = "\n".join(f"- {c} {n}" + (f" ({note})" if note else "") for c, n, note in cands) or "- (후보 없음)"
    user = (f"[공고명] {mod.title_of(rec)[:120]}\n\n"
            f"[나라장터 입력 메타]\n{meta_lines}\n\n"
            f"[세부품명 후보]\n{cand_lines}\n\n"
            f"[공고 원문 {k}/{total} 부분]\n" + wtext + "\n\n"
            f"이 부분에 없는 사실은 추측하지 말고 기본값(false/null/없음/해당없음)으로 둔다.\n")
    return [{"role": "system", "content": mod.SYSTEM_PROMPT}, {"role": "user", "content": user}]


LEVEL_RANK = {"없음": 0, "중소기업": 1, "중기업": 2, "소기업·소상공인": 3, "소상공인": 4}


def merge_windows(mod, facts_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """창별 사실을 합친다. 불리언은 OR, 근거는 참이라고 답한 창에서 가져온다."""
    facts_list = [f for f in facts_list if f]
    if not facts_list: return {}
    out: Dict[str, Any] = dict(facts_list[0])
    for f in facts_list[1:]:
        for k, v in f.items():
            if k in mod.BOOL_KEYS:
                out[k] = bool(out.get(k)) or bool(v)
            elif k.endswith("_근거"):
                if not out.get(k) and v: out[k] = v
            elif k == "기업규모_제한":
                if LEVEL_RANK.get(str(v), 0) > LEVEL_RANK.get(str(out.get(k)), 0): out[k] = v
            elif k == "지역_시도목록":
                out[k] = sorted(set(out.get(k) or []) | set(v or []))
            elif k == "공고서_업종코드":
                out[k] = sorted(set(out.get(k) or []) | set(v or []))
            elif k == "지역_단위":
                if out.get(k) in (None, "없음") and v not in (None, "없음"): out[k] = v
            elif k == "실적_요구금액_원":
                if isinstance(v, (int, float)) and (not isinstance(out.get(k), (int, float)) or v > out[k]): out[k] = v
            elif k == "공동수급_최소지분율":
                if isinstance(v, (int, float)) and (not isinstance(out.get(k), (int, float)) or v < out[k]): out[k] = v
            else:
                if out.get(k) in (None, "", [], "없음", "해당없음", "불명") and v not in (None, "", [], "없음", "해당없음", "불명"):
                    out[k] = v
    # 근거는 그 사실이 참일 때만 남긴다
    for b, e in (("실적제한", "실적_근거"), ("지역제한", "지역_근거"), ("특정기관_한정", "특정기관_근거"),
                 ("특정모델_지정", "특정모델_근거"), ("확약서_입찰시제출", "확약서_근거")):
        if not out.get(b): out[e] = None
    return out


def f1_table(labels, preds, ids):
    o = {}
    for v in ITEMS:
        tp = sum(1 for i in ids if labels[i][v] and preds[i][v])
        fp = sum(1 for i in ids if not labels[i][v] and preds[i][v])
        fn = sum(1 for i in ids if labels[i][v] and not preds[i][v])
        o[v] = {"f1": 2 * tp / (2 * tp + fp + fn) if tp else 0.0, "tp": tp, "fp": fp, "fn": fn}
    o["_macro"] = sum(o[v]["f1"] for v in ITEMS) / len(ITEMS)
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=str(CAND))
    ap.add_argument("--model", default=str(ROOT / "models" / "gemma-4-26b-a4b-it-4bit"))
    ap.add_argument("--input", default=str(ROOT / "open" / "dev.jsonl.gz"))
    ap.add_argument("--out", default=str(ROOT / "runs" / "mlx" / "win_dev.jsonl"))
    ap.add_argument("--win-tokens", type=int, default=10000)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()

    mod = load_mod(Path(a.script))
    table = mod.load_competitive_table(str(ROOT / "open" / "data")); mod._TABLE_CACHE.update(table)
    recs = list(mod.iter_records(a.input, limit=a.limit))
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    done: Dict[str, str] = {}
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line); done[r["key"]] = r["text"]

    if a.generate:
        from mlx_vlm import generate, load
        from mlx_vlm.structured import build_json_schema_logits_processor
        model, processor = load(a.model)
        tk = processor.tokenizer if hasattr(processor, "tokenizer") else processor
        schema = mod.extraction_schema()
        jobs = []
        for rec in recs:
            ws = windows(mod, rec, tk, a.win_tokens)
            for k, w in enumerate(ws, 1):
                key = f"{rec['id']}#{k}/{len(ws)}"
                if key not in done: jobs.append((rec, k, len(ws), w, key))
        log(f"생성 대상 {len(jobs)}창 (저장됨 {len(done)}창 · 레코드 {len(recs)})")
        t0 = time.time()
        with out.open("a", encoding="utf-8") as f:
            for n, (rec, k, tot, w, key) in enumerate(jobs, 1):
                msgs = build_window_messages(mod, rec, table, w, k, tot)
                prompt = tk.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
                proc = build_json_schema_logits_processor(tk, schema)   # 호출마다 새로 만든다(상태 객체)
                try:
                    text = generate(model, processor, prompt, verbose=False, max_tokens=mod.MAX_TOKENS,
                                    temperature=0.0, enable_thinking=False, logits_processors=[proc]).text
                except Exception as e:
                    log(f"  ! {key} 실패 {type(e).__name__}: {str(e)[:150]}"); text = ""
                done[key] = text
                f.write(json.dumps({"key": key, "id": rec["id"], "win": k, "of": tot, "text": text}, ensure_ascii=False) + "\n")
                f.flush()
                if n % 10 == 0 or n == len(jobs):
                    el = time.time() - t0
                    log(f"  {n}/{len(jobs)} … {el:.0f}s (남은 예상 {el/n*(len(jobs)-n):.0f}s)")

    if a.score:
        import csv
        labels = {r["id"]: {v: int(r[v]) for v in ITEMS} for r in csv.DictReader(open(ROOT / "open" / "dev_labels.csv", encoding="utf-8"))}
        by_id: Dict[str, List[str]] = {}
        for key, text in done.items():
            by_id.setdefault(key.split("#")[0], []).append(text)
        merged: Dict[int, str] = {}
        nwin = []
        for i, rec in enumerate(recs):
            texts = by_id.get(rec["id"], [])
            nwin.append(len(texts))
            fl = [mod.parse_facts(t) for t in texts]
            mf = merge_windows(mod, fl)
            if mf: merged[i] = json.dumps(mf, ensure_ascii=False)
        log(f"채점 {len(merged)}/{len(recs)}건 · 창 평균 {sum(nwin)/max(len(nwin),1):.2f}")
        ids = [r["id"] for r in recs]

        def saved(name):
            fp = ROOT / "runs" / "mlx" / f"{name}.jsonl"
            d = {}
            if fp.exists():
                for line in fp.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        r = json.loads(line); d[r["id"]] = r["text"]
            return {i: d[r["id"]] for i, r in enumerate(recs) if r["id"] in d}

        # 전용 호출은 두 조건에 똑같이 넣는다 — 달라지는 것은 본 호출뿐이다.
        aux = dict(item_texts=saved("item_outputs_v3"), model_texts=saved("model_outputs"),
                   sme_texts=saved("v21_sme_dev"), region_texts=saved("v22_region_dev"))
        log("전용 호출 dev 출력: " + " ".join(f"{k}={len(v)}" for k, v in aux.items()))

        def score(main_texts):
            rows, _ = mod.judge_all(recs, table, main_texts, aux["item_texts"], aux["model_texts"],
                                    aux["sme_texts"], {}, aux["region_texts"], {})
            preds = {r["id"]: {v: int(r[v]) for v in ITEMS} for r in rows}
            return f1_table(labels, preds, ids)

        base_main = saved("v21_main_dev")
        # 합집합: 텍스트를 덮어쓰는 게 아니라 **사실을 병합**한다(불리언 OR).
        union = {}
        for i in set(base_main) | set(merged):
            fl = [f for f in (mod.parse_facts(base_main.get(i, "")), mod.parse_facts(merged.get(i, ""))) if f]
            if fl:
                union[i] = json.dumps(merge_windows(mod, fl), ensure_ascii=False)
        res = {"기준(발췌)": score(base_main), "창 분할": score(merged), "발췌+창 사실합집합": score(union)}
        names = list(res)
        print(f'{"item":>5} ' + " ".join(f"{n:>18}" for n in names))
        for v in ITEMS:
            print(f"{v:>5} " + " ".join(f'{res[n][v]["f1"]:>7.3f}({res[n][v]["tp"]}/{res[n][v]["fp"]}/{res[n][v]["fn"]})'.rjust(18) for n in names))
        print(f'{"macro":>5} ' + " ".join(f'{res[n]["_macro"]:>18.4f}' for n in names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
