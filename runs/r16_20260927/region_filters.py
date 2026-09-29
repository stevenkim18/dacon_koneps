import pickle, re, collections, random, importlib.util
S="runs/r16_20260927"
spec = importlib.util.spec_from_file_location('m', 'submissions/20260928_wrap_r15/script.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
res = pickle.load(open(S+'/harvest.pkl','rb'))
miss = [(i, ln) for i, f, ln, cv in res if f == 'region' and cv is False]
strong = re.compile(r"(소재|영업소|본점|본사|사업장)[^\n]{0,80}(업체|자|사업자|법인)\s*(이어야|여야|로\s*제한|에\s*한|만|로\s*한정|일\s*것|\.|$|이며|로서|으로서|\))|(둔|두고|있는|소재한|소재하는|소재의)\s*(업체|자|사업자|법인)")
TRIG = re.compile(r"주된\s*영업소|본점|소재지|본사|소재한\s*(업체|자|사업자)|소재하(는|고)\s*있는|내에\s*소재"
                           r"|에\s*사업자\s*등록을?\s*(한|하고\s*있는)\s*(업체|자)|도내\s*(업체|사업자)"
                           r"|주\s*사무소를?\s*(둔|두고)|소재\s*법인|소재하는\s*(업체|사업자|자|법인)"
                           r"|사업장이\s*[^\n]{0,30}(내에|관내에)\s*(있는|소재)"
                           r"|소재\s*(업체|사업자)|관내\s*(에\s*)?(업체|사업자|사업장|본점|주된)|주된\s*사무소|사업장을\s*(둔|두고)"
                           r"|지역\s*(업체|업자)\s*(만|에\s*한|로\s*제한)")
def why(s):
    if not TRIG.search(s): return 'no-trigger'
    if not re.search(r"주된\s*영업소|본점|소재지|본사|소재한\s*(업체|자|사업자)|소재하(는|고)\s*있는|내에\s*소재", s) and re.search(r"도급자|계약\s*상대자|낙찰자|활용|임차|하도급|협력|가능한|주요\s*내용|과업", s): return 'F1-newword-ctx'
    m = re.search(r"주소|위치|장소|납품|설치|전화|☎", s[:40])
    if m: return 'F2-first40:' + m.group(0)
    m = re.search(r"가산|가점|배점|평가|\+\s*\d+(\.\d+)?\s*점|우선\s*선정", s)
    if m: return 'F3-eval:' + m.group(0)
    m = re.search(r"각서|서약|확약|확\s*인\s*서|동의서|법원|재판\s*관할|면\s*소재지|보험\s*대상|대상물|성과품", s)
    if m: return 'F4-doc:' + m.group(0)
    if re.search(r"소재하는\s*(업체|사업자|자|법인)", s) and re.search(r"공동\s*도급|분담|구성원", s): return 'F5-joint'
    if re.search(r"중간\s*처리\s*업체|처리\s*업체(와|과|\s*또는)|업체(와|과)\s*(공동|분담)|협력\s*업체|현지\s*운행|본사\s*\(\s*인\s*\)", s): return 'F6-partner'
    if re.search(r"소재지\s*[:：]", s) and not re.search(r"제한|자격|인\s*자|있는\s*자|한\s*업체|참가|둔\s*자", s): return 'F7-colon'
    if re.search(r"관할\s*법원|소송", s): return 'F8'
    if re.search(r"본사는|참가하고자|신청을\s*합니다|신청합니다", s): return 'F9'
    restrict = re.search(r"제한|한함|한정|자격|참가|있는\s*(업체|자)|둔\s*(업체|자)|소재한\s*(업체|자)|만\s*(입찰\s*)?(참여|참가)|두고\s*(영업\s*중인|있는)\s*(업체|자|법인|개인\s*사업자|사업자)", s)
    if (re.search(r"주\s*소\s*[:：]|장\s*소\s*[:：]", s[:40]) or re.search(r"\[상세주소\]|\[?우편번호\]?|피보험자|본사\s*\(\s*본인", s)) and not restrict: return 'F10-addr'
    if not re.search(r"주된\s*영업소|본점|소재지|소재한|소재하|내에\s*소재", s) and not restrict: return 'F11-bonsa-norestrict'
    if not (M.PROVINCE_RE.search(s) or "단위=기초" in s or "기초자치단체" in s): return 'F12-no-fullprov'
    return 'other'
c = collections.Counter(); ex = collections.defaultdict(list); seen=set()
for i, ln in miss:
    if not strong.search(ln): continue
    k = re.sub(r"\[[^\]]*\]|\d+", "", ln)[:80]
    if k in seen: continue
    seen.add(k); w = why(ln); c[w] += 1; ex[w].append((i, ln))
for k, v in c.most_common(40): print(v, k)
pickle.dump(ex, open(S+'/region_why.pkl','wb'))
