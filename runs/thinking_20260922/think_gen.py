"""(기각된 실험, 재현용 보존) Gemma 4 thinking 2단계 생성 파일럿. 1단계: 스키마 없이 생각(thought 채널)을 budget까지 생성, 2단계: 생각을 붙이고 JSON 스키마로 답.
  python think_gen.py --kind main|sme|region|perf|item|model --input dev.jsonl --out out.jsonl [--limit N] [--budget 1024]"""
import argparse, json, sys, time, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("--kind", default="main"); ap.add_argument("--input", default=str(ROOT / "open/dev.jsonl"))
ap.add_argument("--out", required=True); ap.add_argument("--limit", type=int); ap.add_argument("--budget", type=int, default=1024)
ap.add_argument("--script", default=str(ROOT / "submissions/20260923_port_v20title/script.py"))
ap.add_argument("--ids", default=None)
a = ap.parse_args()
spec = importlib.util.spec_from_file_location("c", a.script); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
table = mod.load_competitive_table(str(ROOT / "open/data"))
from mlx_vlm import load, stream_generate, generate
from mlx_vlm.structured import build_json_schema_logits_processor
model, processor = load(str(ROOT / "models/gemma-4-26b-a4b-it-4bit"))
tok = processor.tokenizer if hasattr(processor, "tokenizer") else processor
class Shim:
    def count_tokens(self, messages):
        ids = tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=True)
        if hasattr(ids, "keys") and "input_ids" in ids: ids = ids["input_ids"]
        return len(ids)
sme_law = mod.load_sme_law(str(ROOT / "open/data")); perf_law = mod.load_perf_law(str(ROOT / "open/data"))
recs = [json.loads(l) for l in open(a.input, encoding="utf-8")]
if a.ids:
    want = set(open(a.ids).read().split()); recs = [r for r in recs if r["id"] in want]
done = set()
outp = Path(a.out)
if outp.exists():
    done = {json.loads(l)["id"] for l in outp.read_text(encoding="utf-8").splitlines()}
todo = [r for r in recs if r["id"] not in done]
if a.kind == "item": todo = [r for r in todo if mod.needs_item_call(r)]
if a.kind == "model": todo = [r for r in todo if mod.needs_model_call(r)]
if a.limit: todo = todo[: a.limit]
print(f"[think] {a.kind} 대상 {len(todo)}건 (완료 {len(done)})", file=sys.stderr, flush=True)
END = "<channel|>"
THINK_NOTE = ("\n\n[생각 방식] 과제와 규칙을 다시 옮겨 적지 않는다. 판단이 갈리는 원문 줄만 골라, "
              "각 줄이 규칙의 어느 경우에 해당하는지 한두 문장으로 검토한 뒤 답한다.")
t0 = time.time()
with outp.open("a", encoding="utf-8") as f:
    for n, rec in enumerate(todo, 1):
        if a.kind == "main":
            msgs, ntok, scale = mod.fit_to_budget(rec, table, Shim()); schema = mod.extraction_schema(); mt = mod.MAX_TOKENS
        elif a.kind == "sme":
            msgs = mod.build_sme_messages(rec, sme_law); schema = mod.sme_schema(); mt = mod.TOKENS_SME
        elif a.kind == "region":
            msgs = mod.build_region_messages(rec, perf_law); schema = mod.region_schema(); mt = mod.TOKENS_REGION
        elif a.kind == "perf":
            msgs = mod.build_perf_messages(rec, perf_law); schema = mod.perf_schema(); mt = 400
        elif a.kind == "item":
            msgs = mod.build_item_messages(rec, table); schema = mod.item_schema(table); mt = 128
        elif a.kind == "model":
            msgs = mod.build_model_messages(rec); schema = mod.model_schema(); mt = 128
        msgs = [dict(m) for m in msgs]
        msgs[0]["content"] = msgs[0]["content"] + THINK_NOTE
        prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, enable_thinking=True)
        t1 = time.time(); thought = ""; ntk = 0
        try:
            for res in stream_generate(model, processor, prompt, max_tokens=a.budget, temperature=0.0):
                thought += res.text; ntk += 1
                if END in thought:
                    thought = thought[: thought.index(END) + len(END)]; break
            if END not in thought:
                thought += "\n" + END          # 예산 소진: 생각을 강제로 닫는다
            t2 = time.time()
            proc = build_json_schema_logits_processor(tok, schema)
            text = generate(model, processor, prompt + thought, verbose=False, max_tokens=mt, temperature=0.0,
                            logits_processors=[proc]).text
        except Exception as e:
            print(f"  ! {rec['id']} {type(e).__name__}: {str(e)[:200]}", file=sys.stderr); text = ""; t2 = time.time()
        f.write(json.dumps({"id": rec["id"], "text": text, "thought": thought, "think_tokens": ntk,
                            "t_think": round(t2 - t1, 1), "t_answer": round(time.time() - t2, 1)}, ensure_ascii=False) + "\n"); f.flush()
        if n % 5 == 0 or n == len(todo) or n <= 2:
            print(f"  [{a.kind}] {n}/{len(todo)} {time.time()-t0:.0f}s think_tok={ntk}", file=sys.stderr, flush=True)
