import sys, json
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
m = D.load_mod('submissions/20260926_phrase_parser_recall/script.py')
recs = {r['id']: r for r in D.dev_records(m)}
lab = D.labels()
for which in ['int8', 'b4']:
    S = D.load_saved(D.RAW[which]['model'])
    print('=========', which)
    for i in ['PPS-DEV-09','PPS-DEV-12','PPS-DEV-23','PPS-DEV-050','PPS-DEV-052','PPS-DEV-088','PPS-DEV-104','PPS-DEV-110','PPS-DEV-128','PPS-DEV-133','PPS-DEV-148','PPS-DEV-152','PPS-DEV-160','PPS-DEV-176','PPS-DEV-180']:
        r = recs[i]; t = S.get(i, '')
        res = m.parse_facts(t) or {}
        lines = m.model_candidate_lines(r)
        idx = res.get('줄번호')
        line = lines[idx-1] if isinstance(idx, int) and 1 <= idx <= len(lines) else ''
        print(f"{i} lab={lab[i]['v9']} call={res.get('특정모델_지정')} n={len(lines)} title={m.title_of(r)[:50]!r}")
        print('     ->', line[:200])
