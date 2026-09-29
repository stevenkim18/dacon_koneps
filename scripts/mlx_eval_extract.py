"""rule_extract 계열 후보(사실 추출 + 법령 판정기)를 dev에서 평가한다. --script로 대상 지정(기본 item_veto).

1) --regex-only : LLM 없이 정규식 사실만으로 판정(즉시)
2) 기본        : 로컬 MLX Gemma 4(4bit)로 추출 JSON을 생성해 --outputs에 누적 저장(중단 후 이어서 실행 가능)
3) --score-only: 저장된 출력으로 정책(llm / rx / or / and)별 항목 F1을 비교
4) --item-outputs: 용역 품목 판별 호출 출력도 같은 방식으로 생성·저장하고 판정에 반영
5) --cv        : dev를 양성 분포가 비슷한 두 절반으로 나눠, 한쪽에서 항목별 출처를 고르고 다른 쪽에서 채점(양방향 평균)

사용법
  python scripts/mlx_eval_extract.py --regex-only
  python scripts/mlx_eval_extract.py --outputs runs/mlx/extract_outputs.jsonl
  python scripts/mlx_eval_extract.py --outputs runs/mlx/extract_outputs.jsonl --score-only
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
ITEMS = [f"v{i}" for i in range(1, 25)]
DEFAULT_SCRIPT = ROOT / "submissions" / "20260918_sme_level" / "script.py"


def log(msg: str) -> None:
    print(f"[eval_extract] {msg}", file=sys.stderr, flush=True)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("rule_extract_candidate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_labels(path: Path) -> Dict[str, Dict[str, int]]:
    with open(path, encoding="utf-8", newline="") as f:
        return {row["id"]: {v: int(row[v]) for v in ITEMS} for row in csv.DictReader(f)}


def f1_table(labels, preds, ids) -> Dict[str, Dict[str, float]]:
    out = {}
    for v in ITEMS:
        tp = sum(1 for i in ids if labels[i][v] and preds[i][v])
        fp = sum(1 for i in ids if not labels[i][v] and preds[i][v])
        fn = sum(1 for i in ids if labels[i][v] and not preds[i][v])
        f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
        out[v] = {"f1": f1, "tp": tp, "fp": fp, "fn": fn}
    out["_macro"] = sum(out[v]["f1"] for v in ITEMS) / len(ITEMS)
    return out


def split_half(labels, ids: List[str]):
    """양성이 드문 항목부터 양성 공고를 A/B에 번갈아 배정하고, 남은 공고도 번갈아 배정한다(결정론적)."""
    order = sorted(ITEMS, key=lambda v: sum(labels[i][v] for i in ids))
    a, b, assigned = [], [], set()
    for v in order:
        for i in ids:
            if labels[i][v] and i not in assigned:
                (a if len(a) <= len(b) else b).append(i)
                assigned.add(i)
    for i in ids:
        if i not in assigned:
            (a if len(a) <= len(b) else b).append(i)
            assigned.add(i)
    return a, b


def print_table(title: str, tables: Dict[str, Dict], ids_n: int) -> None:
    names = list(tables)
    log(f"== {title} ({ids_n}건) ==")
    print("item  " + "  ".join(f"{n:>18}" for n in names))
    for v in ITEMS:
        cells = []
        for n in names:
            r = tables[n][v]
            cells.append(f"{r['f1']:.3f}({r['tp']}/{r['fp']}/{r['fn']})".rjust(18))
        print(f"{v:<5} " + "  ".join(cells))
    print("macro " + "  ".join(f"{tables[n]['_macro']:>18.4f}" for n in names))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=str(DEFAULT_SCRIPT))
    ap.add_argument("--model", default=str(ROOT / "models" / "gemma-4-26b-a4b-it-4bit"))
    ap.add_argument("--dev", default=str(ROOT / "open" / "dev.jsonl"))
    ap.add_argument("--labels", default=str(ROOT / "open" / "dev_labels.csv"))
    ap.add_argument("--data-dir", default=str(ROOT / "open" / "data"))
    ap.add_argument("--outputs", default=str(ROOT / "runs" / "mlx" / "extract_outputs.jsonl"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--regex-only", action="store_true")
    ap.add_argument("--score-only", action="store_true")
    ap.add_argument("--item-outputs", default=None, help="용역 품목 판별 호출 출력 JSONL")
    ap.add_argument("--model-outputs", default=None, help="물품 특정 모델 판별 호출(v9) 출력 JSONL")
    ap.add_argument("--sme-outputs", default=None, help="기업규모·직접생산 전용 호출(S2) 출력 JSONL")
    ap.add_argument("--perf-outputs", default=None, help="실적 전용 호출 출력 JSONL")
    ap.add_argument("--region-outputs", default=None, help="지역 전용 호출 출력 JSONL")
    ap.add_argument("--goods-outputs", default=None, help="물품 품목 전용 호출 출력 JSONL")
    ap.add_argument("--metacmp-outputs", default=None, help="공고서-나라장터 대조 전용 호출(v24) 출력 JSONL")
    ap.add_argument("--cv", action="store_true")
    ap.add_argument("--dump-preds", default=None, help="최종 판정(항목별)을 JSON {id: {v: 0/1}}로 저장")
    ap.add_argument("--generate-only", action="store_true", help="라벨 없는 입력(무라벨 표본)용: 생성·저장만 하고 채점하지 않음")
    a = ap.parse_args()

    mod = load_module(Path(a.script))
    table = mod.load_competitive_table(a.data_dir)
    recs = list(mod.iter_records(a.dev))
    if a.limit:
        recs = recs[: a.limit]
    labels = {} if a.generate_only else load_labels(Path(a.labels))
    ids = [r["id"] for r in recs]

    if a.regex_only:
        preds = {r["id"]: mod.decide(r, "", table)[0] for r in recs}
        print_table("정규식 사실만", {"regex": f1_table(labels, preds, ids)}, len(ids))
        return 0

    def load_saved(path: Path) -> Dict[str, str]:
        saved: Dict[str, str] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                saved[row["id"]] = row["text"]
        return saved

    done = load_saved(Path(a.outputs))
    item_done = load_saved(Path(a.item_outputs)) if a.item_outputs else {}
    model_done = load_saved(Path(a.model_outputs)) if a.model_outputs else {}
    sme_done = load_saved(Path(a.sme_outputs)) if a.sme_outputs else {}
    perf_done = load_saved(Path(a.perf_outputs)) if a.perf_outputs else {}
    region_done = load_saved(Path(a.region_outputs)) if a.region_outputs else {}
    goods_done = load_saved(Path(a.goods_outputs)) if a.goods_outputs else {}
    has_goods = hasattr(mod, "build_goods_item_messages")
    metacmp_done = load_saved(Path(a.metacmp_outputs)) if a.metacmp_outputs else {}
    has_metacmp = hasattr(mod, "build_metacmp_messages")
    has_sme = hasattr(mod, "build_sme_messages")
    has_focus = hasattr(mod, "build_perf_messages")
    sme_law = mod.load_sme_law(a.data_dir) if has_sme else ""
    perf_law = mod.load_perf_law(a.data_dir) if has_focus else ""

    def extra(rec_id: str) -> Dict[str, str]:
        """후보 스크립트가 전용 호출을 지원할 때만 sme_text를 넘긴다(구 후보와 호환)."""
        kw = {"item_text": item_done.get(rec_id, ""), "model_text": model_done.get(rec_id, "")}
        if has_sme:
            kw["sme_text"] = sme_done.get(rec_id, "")
        if has_focus:
            kw["perf_text"] = perf_done.get(rec_id, "")
            kw["region_text"] = region_done.get(rec_id, "")
        if has_goods:
            kw["goods_text"] = goods_done.get(rec_id, "")
        if has_metacmp:
            kw["metacmp_text"] = metacmp_done.get(rec_id, "")
        return kw

    jobs = []
    if not a.score_only:
        jobs.append((Path(a.outputs), done, [r for r in recs if r["id"] not in done], "main"))
        if a.item_outputs:
            jobs.append((Path(a.item_outputs), item_done,
                         [r for r in recs if mod.needs_item_call(r) and r["id"] not in item_done], "item"))
        if a.model_outputs:
            jobs.append((Path(a.model_outputs), model_done,
                         [r for r in recs if mod.needs_model_call(r) and r["id"] not in model_done], "model"))
        if a.sme_outputs and has_sme:
            jobs.append((Path(a.sme_outputs), sme_done,
                         [r for r in recs if mod.needs_sme_call(r) and r["id"] not in sme_done], "sme"))
        if a.perf_outputs and has_focus:
            jobs.append((Path(a.perf_outputs), perf_done,
                         [r for r in recs if mod.needs_perf_call(r) and r["id"] not in perf_done], "perf"))
        if a.metacmp_outputs and has_metacmp:
            jobs.append((Path(a.metacmp_outputs), metacmp_done,
                         [r for r in recs if mod.needs_metacmp_call(r) and r["id"] not in metacmp_done], "metacmp"))
        if a.goods_outputs and has_goods:
            jobs.append((Path(a.goods_outputs), goods_done,
                         [r for r in recs if mod.needs_goods_item_call(r) and r["id"] not in goods_done], "goods"))
        if a.region_outputs and has_focus:
            jobs.append((Path(a.region_outputs), region_done,
                         [r for r in recs if mod.needs_region_call(r) and r["id"] not in region_done], "region"))
    if any(todo for _, _, todo, _ in jobs):
        from mlx_vlm import generate, load
        from mlx_vlm.structured import build_json_schema_logits_processor

        model, processor = load(a.model)
        tok = processor.tokenizer if hasattr(processor, "tokenizer") else processor

        class Shim:
            def count_tokens(self, messages):
                ids_ = tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=True)
                if hasattr(ids_, "keys") and "input_ids" in ids_:
                    ids_ = ids_["input_ids"]
                return len(ids_)

        for path, store, todo, kind in jobs:
            log(f"[{kind}] 생성 대상 {len(todo)}건 (저장됨 {len(store)}건)")
            if not todo:
                continue
            schema = {"main": lambda: mod.extraction_schema(), "item": lambda: mod.item_schema(table),
                      "model": lambda: mod.model_schema(), "sme": lambda: mod.sme_schema(),
                      "perf": lambda: mod.perf_schema(), "region": lambda: mod.region_schema(),
                      "goods": lambda: None, "metacmp": lambda: mod.metacmp_schema()}[kind]()
            max_tokens = mod.MAX_TOKENS if kind == "main" else (
                500 if kind == "metacmp" else (400 if kind in ("sme", "perf", "region") else 128))
            if kind == "goods":
                max_tokens = 160
            path.parent.mkdir(parents=True, exist_ok=True)
            t0 = time.time()
            with path.open("a", encoding="utf-8") as f:
                for n, rec in enumerate(todo, 1):
                    if kind == "main":
                        msgs, ntok, scale = mod.fit_to_budget(rec, table, Shim())
                    elif kind == "goods":
                        msgs = mod.build_goods_item_messages(rec, table)
                        scale = 1.0
                        ntok = Shim().count_tokens(msgs)
                        schema = mod.goods_item_schema(mod.goods_candidates(rec, table))
                    elif kind == "metacmp":
                        msgs = mod.build_metacmp_messages(rec)
                        scale = 1.0
                        ntok = Shim().count_tokens(msgs)
                    elif kind in ("sme", "perf", "region"):
                        msgs = {"sme": lambda: mod.build_sme_messages(rec, sme_law),
                                "perf": lambda: mod.build_perf_messages(rec, perf_law),
                                "region": lambda: mod.build_region_messages(rec, perf_law)}[kind]()
                        scale = 1.0
                        ntok = Shim().count_tokens(msgs)
                    else:
                        msgs = mod.build_item_messages(rec, table) if kind == "item" else mod.build_model_messages(rec)
                        scale = 1.0
                        ntok = Shim().count_tokens(msgs)
                    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
                    proc = build_json_schema_logits_processor(tok, schema)
                    try:
                        text = generate(model, processor, prompt, verbose=False, max_tokens=max_tokens,
                                        temperature=0.0, enable_thinking=False, logits_processors=[proc]).text
                    except Exception as e:
                        log(f"  ! {rec['id']} 생성 실패: {type(e).__name__}: {str(e)[:200]}")
                        text = ""
                    store[rec["id"]] = text
                    f.write(json.dumps({"id": rec["id"], "tokens": ntok, "scale": scale, "text": text},
                                       ensure_ascii=False) + "\n")
                    f.flush()
                    if n % 10 == 0 or n == len(todo):
                        log(f"  [{kind}] {n}/{len(todo)} … {time.time() - t0:.0f}s (tok={ntok})")

    if a.generate_only:
        log(f"생성 완료: main {len(done)}건 · item {len(item_done)}건 · model {len(model_done)}건 · sme {len(sme_done)}건")
        return 0

    scored = [r for r in recs if r["id"] in done]
    sids = [r["id"] for r in scored]
    parsed = sum(1 for r in scored if mod.parse_facts(done[r["id"]]))
    log(f"채점 {len(sids)}건 · 유효 JSON {parsed}건")
    tables = {}
    keys = mod.FACT_KEYS
    per_mode_preds = {}
    for name in ("rx", "llm", "or", "and"):
        policy = {k: name for k in keys}
        per_mode_preds[name] = {r["id"]: mod.decide(r, done[r["id"]], table, policy=policy,
                                                    **extra(r["id"]))[0] for r in scored}
        tables[name] = f1_table(labels, per_mode_preds[name], sids)
    preds = {r["id"]: mod.decide(r, done[r["id"]], table, **extra(r["id"]))[0] for r in scored}
    tables["final(항목별)"] = f1_table(labels, preds, sids)
    if a.dump_preds:
        Path(a.dump_preds).write_text(json.dumps({i: {v: int(preds[i][v]) for v in ITEMS} for i in preds}), encoding="utf-8")
    print_table("정책별", tables, len(sids))

    if a.cv:
        fold_a, fold_b = split_half(labels, sids)
        log(f"== 교차 검증: A {len(fold_a)}건 / B {len(fold_b)}건 ==")
        scores = []
        for tune, test, tag in ((fold_a, fold_b, "A로 선택→B 채점"), (fold_b, fold_a, "B로 선택→A 채점")):
            chosen = {}
            for v in ITEMS:
                best = max(("rx", "llm", "or", "and"),
                           key=lambda n: (f1_table(labels, per_mode_preds[n], tune)[v]["f1"], n == "rx"))
                chosen[v] = best
            mixed = {i: {v: per_mode_preds[chosen[v]][i][v] for v in ITEMS} for i in test}
            cv_macro = f1_table(labels, mixed, test)["_macro"]
            fixed_macro = f1_table(labels, preds, test)["_macro"]
            scores.append(cv_macro)
            log(f"  {tag}: 교차선택 macro {cv_macro:.4f} · 현재 ITEM_SOURCE macro {fixed_macro:.4f}")
        log(f"  교차 검증 평균 macro {sum(scores) / 2:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
