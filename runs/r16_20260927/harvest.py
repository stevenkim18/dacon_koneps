"""자연 공고 20,000에서 계열별 '자격 줄 후보'를 넓게 모으고, 후보 스크립트의 줄 추출기가 잡는지 본다."""
import sys, gzip, json, pickle, importlib.util, re
from multiprocessing import Pool
SCRIPT = sys.argv[1]; OUT = sys.argv[2]
PROV = r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충청|충북|충남|전라|전북|전남|경상|경북|경남|제주)"
FAM = {
 'region': (re.compile(PROV + r"[^\n]{0,60}(소재|영업소|본점|본사|사업장|관내|[^가-힣]둔\s|두고|두어야)|(소재|영업소|본점|본사|사업장)[^\n]{0,60}" + PROV + r"|\[지역:[^\]]*단위=기초[^\]]*\][^\n]{0,40}(소재|영업소|본점|본사|사업장|관내|둔\s|두고)"),
            re.compile(r"업체|자\b|자이어야|자로|사업자|법인|이어야|있어야|한함|한정|제한|가능"),
            re.compile(r"공채|지역개발|관할\s*법원|소송|우편번호|가산|가점|배점|\d+\s*점")),
 'perf': (re.compile(r"실적|수행\s*경험|납품\s*경험|이력|수행한\s*(업체|자)|납품한\s*(업체|자)"),
          re.compile(r"(업체|자|사업자|법인|기관)\s*(이어야|여야|에\s*한|만|로\s*제한|로\s*한정|일\s*것)|있는\s*(업체|자)|보유한\s*(업체|자)|갖춘\s*(업체|자)|있어야"),
          re.compile(r"평가|배점|점\s*\||\d+\s*점|가점|감점|서식|\d+\s*부\b|제출\s*서류|구비\s*서류|기술자|책임자|인력|경력")),
 'share': (re.compile(r"지분|출자\s*비율|참여\s*비율"), re.compile(r"\d\s*(%|퍼센트)|100\s*분\s*의"), re.compile(r"대표사\s*[^\n]{0,10}\d+\s*%\s*이상[^\n]*$^")),
 'direct': (re.compile(r"직접\s*생산"), re.compile(r"소지|보유|받은|필한|받아야|갖춘|업체|자\b"), re.compile(r"\d+\s*부\b|위반|하도급|하청|제재")),
 'commit': (re.compile(r"확약서|공급\s*확인서|기술지원\s*확인서|공급\s*증명"), re.compile(r"입찰|마감|개찰|제출"), re.compile(r"서약|본인은")),
 'brief': (re.compile(r"설명회|현장\s*설명"), re.compile(r"참석|불참|미참"), re.compile(r"$^")),
}
def load():
    spec = importlib.util.spec_from_file_location('m', SCRIPT); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
M = None; TBL = None
def init():
    global M, TBL; M = load(); TBL = M.load_competitive_table('open/data')
def covered(ln, outs):
    return any(ln in o or o in ln for o in outs)
def work(line):
    r = M.normalize(json.loads(line)); mt = r['meta']
    txt = M.full_text(r)
    lines = []
    for d in r['docs']:
        for ln in d['text'].split('\n'):
            ln = ln.strip()
            if 8 <= len(ln) <= 400: lines.append(ln)
    res = []
    outs = None
    for fam, (a, b, x) in FAM.items():
        cands = [ln for ln in lines if a.search(ln) and b.search(ln) and not x.search(ln)]
        if not cands: continue
        if outs is None:
            rg = M.rx_region(r) + M.rx_region(r, joined=True)
            pf = M.rx_performance(r) + M.rx_performance(r, joined=True)
            outs = {'region': rg, 'perf': pf,
                    'direct': M._lines(r, r"직접생산", joined=True), 'commit': M._lines(r, r"확약서", joined=True),
                    'share': [], 'brief': []}
            fx = M.regex_facts(r, TBL); outs['_fx'] = fx
        for ln in dict.fromkeys(cands):
            res.append((r['id'], fam, ln, covered(ln, outs[fam]) if fam in ('region', 'perf') else None))
    return res
if __name__ == '__main__':
    lines = gzip.open('open/train_unlabeled.jsonl.gz', 'rt', encoding='utf-8').readlines()
    with Pool(8, initializer=init) as pool:
        res = [y for x in pool.map(work, lines, chunksize=100) for y in x]
    pickle.dump(res, open(OUT, 'wb'))
    import collections
    c = collections.Counter((f, cv) for _, f, _, cv in res)
    print(c)
