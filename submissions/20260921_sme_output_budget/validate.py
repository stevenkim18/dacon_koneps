"""CPU-only regression checks; does not simulate actual server inference."""
import importlib.util
import json
import sys
import types
from pathlib import Path
from tokenizers import Tokenizer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def saved(name):
    return {r['id']: r['text'] for r in map(json.loads, (ROOT / 'runs/mlx' / name).read_text().splitlines())}

old = load(HERE.parent / '20260921_recall_first/script.py', 'baseline')
new = load(HERE / 'script.py', 'candidate')
table = new.load_competitive_table(str(ROOT / 'open/data'))
main, item, model, sme = map(saved, ['extract_outputs.jsonl', 'item_outputs.jsonl', 'model_outputs.jsonl', 'v21_sme_dev.jsonl'])
records = list(new.iter_records(str(ROOT / 'open/dev.jsonl.gz')))
changed = 0
for rec in records:
    rid = rec['id']
    args = dict(item_text=item.get(rid, ''), model_text=model.get(rid, ''), sme_text=sme.get(rid, ''))
    assert old.build_messages(rec, table) == new.build_messages(rec, table)
    changed += old.decide(rec, main.get(rid, ''), table, **args) != new.decide(rec, main.get(rid, ''), table, **args)
assert changed == 0
print('saved-output regression:', len(records), 'records, changed:', changed)

# Exercise actual VLLMRunner.chat with a stub backend: validates parameter routing only.
class Params:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
vllm = types.ModuleType('vllm')
vllm.SamplingParams = Params
sampling = types.ModuleType('vllm.sampling_params')
sampling.StructuredOutputsParams = Params
sys.modules['vllm'] = vllm
sys.modules['vllm.sampling_params'] = sampling
class Backend:
    def chat(self, batch, sampling_params, **kwargs):
        self.last = sampling_params.max_tokens
        return [types.SimpleNamespace(outputs=[types.SimpleNamespace(text='{}', finish_reason='stop', token_ids=[1, 2])]) for _ in batch]
runner = object.__new__(new.VLLMRunner)
runner.sp = Params(max_tokens=1200)
runner.llm = Backend()
for schema, expected in [(None,1200),(new.sme_schema(),400),(new.item_schema(table),128),(new.model_schema(),128)]:
    assert runner.chat([[{'role':'user','content':'test'}]], schema) == ['{}']
    assert runner.llm.last == expected
print('output budget routing: main=1200, sme=400, item/model=128 PASS')

tok = Tokenizer.from_file(str(ROOT / 'models/gemma-4-26b-a4b-it-4bit/tokenizer.json'))
lengths = [len(tok.encode(text, add_special_tokens=False).ids) for text in sme.values()]
valid = sum(new.parse_facts(text) is not None for text in sme.values())
print('saved SME outputs:', json.dumps({'count':len(lengths),'valid_json':valid,'over_128':sum(n>128 for n in lengths),'over_400':sum(n>400 for n in lengths),'median':sorted(lengths)[len(lengths)//2],'max':max(lengths)}))
print('Retokenized local outputs indicate length risk; these are not server truncation counts.')
