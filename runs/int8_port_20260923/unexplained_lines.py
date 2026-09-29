"""무라벨 20,000건에서 '참가자격 제한처럼 보이는데 우리 사실 추출기(지역·실적·기업규모·직생·확약서·업종등록)가 설명하지 못하는 줄'을 모아
유형별로 센다. 누락(재현율) 후보 유형을 찾기 위한 탐색 도구다.
  python runs/int8_port_20260923/unexplained_lines.py SCRIPT.py OUT.pkl"""
import sys, json, gzip, re, collections, pickle
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import devtool as D
WS = re.compile(r'\s+')
# 참가자격 제한 표지(문장 끝이 자격 요구로 끝나는 줄)
QUAL = re.compile(r'(한하여|한함|한정|에\s*한해|만\s*(?:참여|참가|입찰|응찰|가능|해당)|(?:보유|소지|등록|갖춘|구비|인증|지정|가입|소속|설립|승인|허가)[^\n]{0,15}(?:한\s*자|한\s*업체|하고\s*있는|된\s*자|된\s*업체|받은\s*자|받은\s*업체|한\s*기관|된\s*기관|해야|하여야|하여야\s*함|할\s*것)|(?:자|업체|기관)\s*(?:이어야|여야)\s*(?:합니다|함|한다))')
# 이미 우리가 다루거나 위반이 아닌 상투 자격
KNOWN = re.compile(r'시행령\s*제1[2-3]조|시행규칙\s*제1[4-5]조|부정당|입찰참가자격\s*(?:을\s*)?등록|입찰참가\s*등록|업종코드|\(\d{4}\)|중소기업|소기업|소상공인|중·소|직접\s*생산|직생|확약|소재|본점|주된\s*영업소|지역|실적|공동수급|공동도급|분담|서류|1부|사본|평가|가점|감점|배점|제안서|청렴|서약|보증|계약보증|하도급|노무|근로|인지세|채권|안전보건|개인정보|보안서약|신용|휴업|폐업|파산|결격|제재|국세|지방세|전자입찰|공인인증|대리인|대표자|법인등기|사업자등록|나라장터|G2B|조달청|재입찰|유찰|낙찰|적격|예정가격|협상|설명회')
TYPES = [
    ('대학·연구기관', r'대학|산학협력단|연구기관|연구원(?!\s*\d)|국공립|출연'),
    ('협회·조합·회원', r'협회|조합|회원|연합회|단체'),
    ('인증·지정', r'인증|ISO|KS|GS|NEP|NET|우수제품|혁신제품|성능인증|지정업체|지정된'),
    ('면허·허가·신고업', r'면허|허가|신고|등록증|등록업체|업\s*등록'),
    ('인력·자격증', r'기술자|기사|자격증|자격을\s*갖춘|인력|전문가|박사|석사|명\s*이상|인\s*이상'),
    ('시설·장비', r'장비|시설|공장|차량|창고|설비|실험실|보유\s*장비'),
    ('특정 제품·제조사', r'제조사|정품|대리점|총판|원제조|순정'),
    ('기타', r'.'),
]
def main(script, out):
    m = D.load_mod(script); tbl = m.load_competitive_table(str(D.ROOT/'open/data'))
    cnt = collections.Counter(); notices = collections.defaultdict(set); samples = collections.defaultdict(list)
    n = 0
    with gzip.open(D.ROOT/'open/train_unlabeled.jsonl.gz','rt',encoding='utf-8') as f:
        for l in f:
            r = json.loads(l)
            meth = str(r['meta'].get('계약방법'))
            if meth == '수의계약':
                continue
            n += 1
            seen = set()
            for d in r['docs']:
                for ln in d['text'].split('\n'):
                    s = ln.strip()
                    if not (12 <= len(s) <= 300) or not QUAL.search(s) or KNOWN.search(s):
                        continue
                    key = WS.sub('', s)
                    if key in seen: continue
                    seen.add(key)
                    t = next(name for name, pat in TYPES if re.search(pat, s))
                    cnt[t] += 1; notices[t].add(r['id'])
                    if len(samples[t]) < 400: samples[t].append((r['id'], d['type'], meth, r['meta'].get('입찰추정가격'), s[:220]))
    print('입찰 공고(수의계약 제외):', n)
    for t, _ in TYPES:
        print(f'  {t:12s} 줄 {cnt[t]:5d} · 공고 {len(notices[t]):5d}')
    pickle.dump({'samples': dict(samples), 'notices': {k: sorted(v) for k, v in notices.items()}}, open(out, 'wb'))
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
