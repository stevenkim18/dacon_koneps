import sys, json, re
sys.path.insert(0, 'runs/int8_port_20260923')
import devtool as D
script = 'submissions/20260926_phrase_parser_recall/script.py'
lab = D.labels()
for which in ['int8', 'b4']:
    m, recs, out = D.run(script, which)
    S = {k: D.load_saved(v) for k, v in D.RAW[which].items()}
    print('=================', which)
    for r in recs:
        i = r['id']
        if not out[i][0]['v9'] and not int(lab[i]['v9']): continue
        main = m.parse_facts(S['main'].get(i, '')) or {}
        mt = S['model'].get(i, '')
        print(f"--- {i} label={lab[i]['v9']} pred={out[i][0]['v9']} goods={m.is_goods(r)} 업무={r['meta']['업무구분']} 계약={r['meta']['계약방법']}")
        print('   main 특정모델_지정:', main.get('특정모델_지정'), '| 근거:', str(main.get('특정모델_근거'))[:200])
        print('   model call:', mt[:300].replace('\n',' '))
        print('   e9:', out[i][1].get('e9','')[:200])
