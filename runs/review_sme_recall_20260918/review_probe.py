"""후보는 수정하지 않고 저장 출력 재채점 및 단일 변경 영향 확인. 저장소 루트에서 실행."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import time
import types
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'submissions/20260919_sme_recall/script.py'
spec = importlib.util.spec_from_file_location('ev', ROOT / 'scripts/mlx_eval_extract.py')
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)
src = SOURCE.read_text()

def module(source):
    m = types.ModuleType('candidate')
    m.__file__ = str(SOURCE)
    exec(compile(source, str(SOURCE), 'exec'), m.__dict__)
    return m

def saved(name):
    return {r['id']: r['text'] for r in map(json.loads, (ROOT / 'runs/mlx' / name).read_text().splitlines())}

base = module(src)
table = base.load_competitive_table(str(ROOT / 'open/data'))
labels = ev.load_labels(ROOT / 'open/dev_labels.csv')
datasets = [
    ('dev', ROOT / 'open/dev.jsonl', 'extract_outputs.jsonl', 'item_outputs.jsonl', 'model_outputs.jsonl'),
    ('train500', ROOT / 'runs/mlx/train_sample500_next.jsonl', 'train500_main.jsonl', 'train500_item.jsonl', 'train500_model.jsonl'),
    ('train250', ROOT / 'runs/mlx/train_sample250.jsonl', 'train250_main.jsonl', 'train250_item.jsonl', 'train250_model.jsonl'),
]
law_guard = '''    for m in EXCEPTION_RE.finditer(src):
        if m.group(0).lstrip().startswith("제"):
            context = src[max(0, m.start() - 120):m.end() + 120]
            if not re.search(r"판로지원|구매촉진|우선\\s*조달", context):
                continue
'''
variants = {'original': src,
    'explicit_priority_target': src.replace('r"|업체일 것|참가', 'r"|우선\\s*조달계약\\s*대상|업체일 것|참가'),
    'body_exception_absence_only': src.replace('if not comp and not exception and priced and not private_contract:', 'if not comp and priced and not private_contract:'),
    'without_meta_negotiation': src.replace(r'|협상에\s*의한\s*계약', ''),
    'no_unqualified_article_exception': src.replace(r'제\s*2\s*조의\s*3|우선조달계약', r'우선조달계약'),
    'article_law_guard': src.replace('    for m in EXCEPTION_RE.finditer(src):\n', law_guard),
}
variants['combined'] = variants['explicit_priority_target'].replace('    for m in EXCEPTION_RE.finditer(src):\n', law_guard)
(Path(__file__).parent / 'experimental_script.py').write_text(variants['combined'])
report = {}
for name, path, mainfile, itemfile, modelfile in datasets:
    recs = list(base.iter_records(str(path)))
    main, items, models = saved(mainfile), saved(itemfile), saved(modelfile)
    preds = {}
    detail = {}
    for variant, source in variants.items():
        m = module(source)
        start = time.monotonic()
        results = {r['id']: m.decide(r, main.get(r['id'], ''), table, item_text=items.get(r['id'], ''), model_text=models.get(r['id'], '')) for r in recs}
        preds[variant] = {i: x[0] for i, x in results.items()}
        info = {'seconds': round(time.monotonic() - start, 3)}
        if name == 'dev':
            info['score'] = ev.f1_table(labels, preds[variant], list(preds[variant]))
        info['changes'] = [{ 'id': i, 'item': v, 'old': preds['original'][i][v], 'new': p[v], 'label': labels[i][v] if name == 'dev' else None} for i,p in preds[variant].items() for v in base.ITEMS if p[v] != preds['original'][i][v]]
        info['positive_pairs'] = sum(sum(p.values()) for p in preds[variant].values())
        if variant == 'original':
            info['evidence_errors'] = []
            info['dropped_absence'] = []
            for r in recs:
                h, e, _ = results[r['id']]
                for v in base.ITEMS:
                    if h[v] and v not in base.ABSENCE and (not e[v] or e[v] not in base.full_text(r) or len(e[v]) > 500):
                        info['evidence_errors'].append([r['id'], v, e[v]])
                    if h[v] and v in base.ABSENCE and r.get('dropped_doc_counts'):
                        info['dropped_absence'].append([r['id'], v, r['dropped_doc_counts']])
                if name == 'dev':
                    wrong = [v for v in base.ITEMS if h[v] != labels[r['id']][v]]
                    if wrong:
                        detail[r['id']] = {'wrong': {v: {'pred':h[v], 'label':labels[r['id']][v], 'evidence':e[v]} for v in wrong}, 'meta':r['meta'], 'rx_level':base.rx_sme_level(r), 'exception':base.has_procurement_exception(base.full_text(r))}
        report[f'{name}/{variant}'] = info
    (Path(__file__).parent / f'{name}_errors.json').write_text(json.dumps(detail, ensure_ascii=False, indent=2))

with zipfile.ZipFile(SOURCE.parent / 'submit.zip') as z:
    report['zip'] = {'files':z.namelist(), 'script_matches':z.read('script.py') == SOURCE.read_bytes(), 'requirements_match':z.read('requirements.txt') == (SOURCE.parent/'requirements.txt').read_bytes(), 'sha256':hashlib.sha256((SOURCE.parent/'submit.zip').read_bytes()).hexdigest()}

report['synthetic_unrelated_law'] = base.has_procurement_exception('「정부 입찰·계약 집행기준」 제2조의3에 따라 하도급 관련사항을 공고합니다.')
class FailedRunner:
    def chat(self, *args):
        raise RuntimeError('synthetic failure')
report['synthetic_call_failure'] = base.run_chunk(FailedRunner(), [[{'role':'user','content':'공고 내용'}]])
(Path(__file__).parent / 'probe_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
for k,v in report.items():
    if isinstance(v, dict) and 'seconds' in v:
        print(k, 'macro=', v.get('score',{}).get('_macro'), 'pairs=',v['positive_pairs'], 'changes=',len(v['changes']), 'seconds=',v['seconds'])
        if v['changes']:
            print(json.dumps(v['changes'], ensure_ascii=False))
    else:
        print(k, v)
