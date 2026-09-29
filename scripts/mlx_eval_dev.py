"""로컬 MLX(Gemma 4 26B-A4B, 4bit)로 dev 200건을 실제 추론해 항목별 F1을 확인한다.

평가 서버는 vLLM + int8 양자화를 쓰고 이 스크립트는 mlx-vlm + 4bit 양자화를 쓰므로
점수가 서버와 그대로 일치하지는 않는다(대회 토크보드도 "로컬과 서버의 점수·출력이
다를 수 있음"이라고 안내한다). 그래도 지금까지 유일했던 "모델 없는 대리 지표"보다
훨씬 직접적인 신호를 준다 — 같은 계열의 실제 Gemma 4 모델로 항목별 F1을 처음 확인한다.

사용법
  python scripts/mlx_eval_dev.py --script open/baseline/script.py --limit 20
  python scripts/mlx_eval_dev.py --script submissions/20260916_attachment_excerpt/script.py --limit 20
  python scripts/mlx_eval_dev.py --script ... --out docs/... (전체 200건은 --limit 생략)
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
ITEMS = [f"v{i}" for i in range(1, 25)]


def log(msg: str) -> None:
    print(f"[mlx_eval] {msg}", file=sys.stderr, flush=True)


def load_script_module(path: str):
    p = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(f"cand_{p.stem}_{abs(hash(str(p)))}", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_labels(path: Path) -> Dict[str, Dict[str, int]]:
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out[row["id"]] = {v: int(row[v]) for v in ITEMS}
    return out


class MLXCountingShim:
    """fit_to_budget이 요구하는 count_tokens(messages) 인터페이스만 제공합니다."""

    def __init__(self, tokenizer):
        self.tok = tokenizer

    def count_tokens(self, messages: List[Dict[str, str]]) -> int:
        try:
            ids = self.tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=True)
            if hasattr(ids, "keys") and "input_ids" in ids:
                ids = ids["input_ids"]
            return len(ids)
        except Exception:
            return len(self.tok.encode("\n".join(m["content"] for m in messages)))


def confusion(labels: Dict[str, Dict[str, int]], preds: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, Any]]:
    report = {}
    f1s = []
    for v in ITEMS:
        tp = fp = fn = tn = 0
        for rec_id, gold in labels.items():
            g = gold[v]
            p = preds.get(rec_id, {}).get(v, 0)
            if g == 1 and p == 1:
                tp += 1
            elif g == 0 and p == 1:
                fp += 1
            elif g == 1 and p == 0:
                fn += 1
            else:
                tn += 1
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        report[v] = {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": round(prec, 4),
                      "recall": round(rec, 4), "f1": round(f1, 4), "positives": tp + fn}
        f1s.append(f1)
    report["_macro_f1"] = round(sum(f1s) / len(f1s), 4)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="로컬 MLX Gemma 4로 dev F1 확인")
    ap.add_argument("--script", required=True, help="평가할 script.py 경로 (베이스라인 또는 후보)")
    ap.add_argument("--model", default=str(ROOT / "models" / "gemma-4-26b-a4b-it-4bit"))
    ap.add_argument("--dev", default=str(ROOT / "open" / "dev.jsonl"))
    ap.add_argument("--labels", default=str(ROOT / "open" / "dev_labels.csv"))
    ap.add_argument("--data-dir", default=str(ROOT / "open" / "data"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--ids-file", default=None, help="한 줄에 id 하나. 지정하면 이 id 집합만 평가(순서는 dev 파일 순서 유지)")
    ap.add_argument("--max-chars", type=int, default=4000)
    ap.add_argument("--max-tokens", type=int, default=1536)
    ap.add_argument("--no-structured", action="store_true", help="llguidance JSON 스키마 강제 끄기")
    ap.add_argument("--out", default=None, help="결과 JSON 저장 경로")
    ap.add_argument("--save-outputs", default=None, help="레코드별 원문 출력까지 저장할 JSONL 경로")
    a = ap.parse_args()

    mod = load_script_module(a.script)
    recs = list(mod.iter_records(a.dev, limit=None))
    if a.ids_file:
        want = {ln.strip() for ln in Path(a.ids_file).read_text(encoding="utf-8").splitlines() if ln.strip()}
        recs = [r for r in recs if r["id"] in want]
    if a.limit:
        recs = recs[: a.limit]
    labels_all = load_labels(Path(a.labels))
    labels = {r["id"]: labels_all[r["id"]] for r in recs if r["id"] in labels_all}
    log(f"평가 대상 {len(recs)}건 (라벨 매칭 {len(labels)}건) · script={a.script}")

    tbl = mod.item_table(data_dir=a.data_dir)
    schema = mod.decode_schema(data_dir=a.data_dir)
    system_prompt = mod.build_system_prompt(tbl)

    log(f"모델 로드 중: {a.model}")
    t0 = time.time()
    from mlx_vlm import load, generate
    from mlx_vlm.structured import build_json_schema_logits_processor

    model, processor = load(a.model)
    tokenizer = processor.tokenizer if hasattr(processor, "tokenizer") else processor
    log(f"모델 로드 완료 {time.time() - t0:.1f}s")

    shim = MLXCountingShim(tokenizer)

    preds: Dict[str, Dict[str, int]] = {}
    raw_outputs = []
    t_inf = time.time()
    for i, rec in enumerate(recs, 1):
        if rec["id"] not in labels:
            continue
        msgs, ntok, mc = mod.fit_to_budget(rec, system_prompt, shim, a.max_chars)
        prompt = tokenizer.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)

        kwargs = dict(max_tokens=a.max_tokens, temperature=0.0, enable_thinking=False)
        if not a.no_structured:
            proc = build_json_schema_logits_processor(tokenizer, schema)
            kwargs["logits_processors"] = [proc]

        try:
            result = generate(model, processor, prompt, verbose=False, **kwargs)
            text = result.text
        except Exception as e:
            log(f"  ! {rec['id']} 생성 실패: {type(e).__name__}: {str(e)[:200]}")
            text = ""

        parsed, missing = mod.parse_judgment(text)
        final = mod.postprocess(parsed, rec)
        preds[rec["id"]] = {v: final[v]["위반여부"] for v in ITEMS}
        if a.save_outputs:
            raw_outputs.append({"id": rec["id"], "tokens": ntok, "max_chars": mc,
                                 "missing": missing, "text": text})
        if i % 5 == 0 or i == len(recs):
            log(f"  {i}/{len(recs)}건 … {time.time() - t_inf:.0f}s (마지막 {rec['id']} tok={ntok})")

    inf_seconds = time.time() - t_inf
    report = confusion(labels, preds)
    log(f"macro F1 = {report['_macro_f1']}  (추론 {inf_seconds:.0f}s · 건당 {inf_seconds/max(1,len(preds)):.1f}s)")
    for v in ITEMS:
        r = report[v]
        if r["positives"] or r["fp"]:
            log(f"  {v}: P={r['precision']} R={r['recall']} F1={r['f1']} (pos={r['positives']}, tp={r['tp']}, fp={r['fp']}, fn={r['fn']})")

    if a.out:
        out_path = Path(a.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "script": a.script, "model": a.model, "n": len(preds),
            "max_chars": a.max_chars, "structured": not a.no_structured,
            "inf_seconds": round(inf_seconds, 1), "report": report,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"저장: {out_path}")
    if a.save_outputs:
        with open(a.save_outputs, "w", encoding="utf-8") as f:
            for row in raw_outputs:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        log(f"원문 출력 저장: {a.save_outputs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
