import json, csv, re, importlib.util
spec = importlib.util.spec_from_file_location("m", "submissions/20260929_r17_edit_shapes/script.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
lab = {r['id']: r for r in csv.DictReader(open('open/dev_labels.csv'))}
SWC = re.compile(r"(정보\s*시스템|시스템|홈페이지|플랫폼|포털|DB|데이터베이스|전산|소프트웨어|S/?W|앱|어플리케이션|애플리케이션|웹|누리집|정보화|ISP|ISMP|클라우드|전자\s*정부|키오스크\s*소프트)"
                 r"[^\n]{0,15}(구축|고도화|개발|개편|유지\s*보수|유지\s*관리|운영|재구축|개선|전환|기능\s*개선|리뉴얼|통합)")
for ln in open('open/dev.jsonl'):
    r = json.loads(ln); i = r['id']
    p = M.price(r) or 0
    t = M.title_of(r)
    sw = M.is_software(r)
    swc = bool(SWC.search(t))
    if sw or swc or lab[i]['v20'] == '1':
        print(i, 'lab', lab[i]['v20'], 'is_sw', sw, 'title_swc', swc, int(p), r['meta'].get('계약방법'), t[:70], '|', str(r['meta'].get('면허업종제한목록'))[:60])
