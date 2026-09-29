"""후보 스크립트의 전용 호출 하나만 로컬 MLX 4bit로 돌린다(기존 출력 파일에 이어 쓰기).
  python runs/r18_20260928/mlx_calls.py SCRIPT.py RECS.jsonl OUT.jsonl [kind=model]"""
import sys, json, time, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SCRIPT, RECS, OUT = sys.argv[1], sys.argv[2], Path(sys.argv[3])
KIND = sys.argv[4] if len(sys.argv) > 4 else "model"
spec = importlib.util.spec_from_file_location("m", SCRIPT); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
table = M.load_competitive_table(str(ROOT / "open/data"))
recs = [M.normalize(json.loads(l)) for l in open(RECS, encoding="utf-8")]
done = set()
if OUT.exists():
    done = {json.loads(l)["id"] for l in open(OUT, encoding="utf-8")}
need = {"model": M.needs_model_call, "item": M.needs_item_call, "model2": getattr(M, "needs_model2_call", None)}[KIND]
todo = [r for r in recs if need(r) and r["id"] not in done]
print(f"[{KIND}] todo {len(todo)} (done {len(done)})", flush=True)
if todo:
    from mlx_vlm import generate, load
    from mlx_vlm.structured import build_json_schema_logits_processor
    model, processor = load(str(ROOT / "models" / "gemma-4-26b-a4b-it-4bit"))
    tok = processor.tokenizer if hasattr(processor, "tokenizer") else processor
    schema = M.item_schema(table) if KIND == "item" else M.model_schema()
    t0 = time.time()
    with OUT.open("a", encoding="utf-8") as f:
        for n, r in enumerate(todo, 1):
            msgs = {"model": lambda: M.build_model_messages(r), "model2": lambda: M.build_model2_messages(r), "item": lambda: M.build_item_messages(r, table)}[KIND]()
            prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
            proc = build_json_schema_logits_processor(tok, schema)
            try:
                text = generate(model, processor, prompt, verbose=False, max_tokens=128, temperature=0.0,
                                enable_thinking=False, logits_processors=[proc]).text
            except Exception as e:
                print("!", r["id"], type(e).__name__, str(e)[:200], flush=True); text = ""
            f.write(json.dumps({"id": r["id"], "text": text}, ensure_ascii=False) + "\n"); f.flush()
            if n % 20 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)} {time.time() - t0:.0f}s", flush=True)
