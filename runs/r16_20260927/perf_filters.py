import pickle, re, collections, random, importlib.util
S="runs/r16_20260927"
spec = importlib.util.spec_from_file_location('m', 'submissions/20260928_wrap_r15/script.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
res = pickle.load(open(S+'/harvest.pkl','rb'))
miss = [(i, ln) for i, f, ln, cv in res if f == 'perf' and cv is False]
PAREN = re.compile(r"\([^()]*\)|\[[^\[\]]*\]|※.*$|\*.*$")
QUAL = re.compile(r"(실적|경험|이력)[^\n]{0,40}?(이|을|를)?\s*(\d+\s*(건|회)\s*이상\s*)?(있는|보유한|보유하고\s*있는|갖춘|가진)\s*(업체|자\b|자\s*이어야|자이어야|사업자|법인|기관|단체)"
                  r"|실적이\s*(\d+\s*(건|회)\s*이상\s*)?있어야")
def strip(s):
    t = s
    for _ in range(3): t = PAREN.sub(" ", t)
    return t
def why(s):
    t = strip(s)
    if not QUAL.search(t): return 'no-qual'
    steps = [('사실이있는제재', re.search(r"사실이\s*있는", s) and re.search(r"불합격|제재|부정당|위반|감가|해지|해제", s)),
             ('인력', not re.search(r"실적|수행\s*경험|납품\s*경험", s) and re.search(r"책임자|PM\b|인력|재직|경력|강사|전문가|전공|학위", s)),
             ('EVAL', M.EVAL_CONTEXT_RE.search(s)), ('BOILER', M.PERF_BOILERPLATE_RE.search(s)),
             ('서류', re.search(r"\d+\s*부\b|서식|제출\s*서류|구비\s*서류", s)),
             ('제안', re.search(r"제안서에|제안사의|발표자|정성|제시하며|기술하|열거", s)),
             ('우대', re.search(r"우대|선호|권장|권고", s))]
    for name, hit in steps:
        if hit: return name + (':' + hit.group(0) if hasattr(hit, 'group') else '')
    return 'other'
c = collections.Counter(); ex = collections.defaultdict(list)
seen=set()
for i, ln in miss:
    k = re.sub(r"\d+", "", ln)[:80]
    if k in seen: continue
    seen.add(k)
    w = why(ln); c[w.split(':')[0] if not w.startswith('EVAL') else w] += 1; ex[w].append((i, ln))
for k, v in c.most_common(40): print(v, k)
pickle.dump(ex, open(S+'/perf_why.pkl','wb'))
