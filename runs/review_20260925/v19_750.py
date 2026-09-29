import json, gzip, re, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "int8_port_20260923"))
import devtool as D
S=str(D.ROOT)+"/submissions/20260926_phrase_parser_recall_v1fix/script.py"
m=D.load_mod(S)
V19_EXCL = re.compile(r"본인은|서약|이의를?\s*제기|계약\s*(체결\s*)?(시|전|후|이후)|계약\s*체결|낙찰자\s*(는|로|가)|낙찰\s*후|납품\s*(시|전|후)|해당\s*시|필요\s*시|요청\s*시|제출할\s*수\s*있|청렴|보증금|이행\s*각서|지급\s*확약|근로|노동|고용|불인정|허위")
BID_RE = re.compile(r"입찰\s*(서|참가|시|마감|등록)|마감|참가\s*신청|투찰|참가\s*전")
MAKER_RE = re.compile(r"제조|공급|기술\s*지원|A/?S|기술\s*서비스")
def rx19(rec):
    return [ln for ln in m._lines(rec, r"확약서") if BID_RE.search(ln) and MAKER_RE.search(ln) and not V19_EXCL.search(ln)]
recs=[json.loads(l) for l in gzip.open(D.ROOT/'open/exp950.jsonl.gz','rt',encoding='utf-8')]
RAW={k: D.ROOT/f'runs/cloud_int8_exp/exp/raw/{k}.jsonl' for k in ['main','item','model','sme','region']}
_,_,o=D.run(S, recs=recs, raw=RAW)
lab=D.labels()
c=collections.Counter()
for r in recs:
    r=m.normalize(r)
    if not m.is_goods(r): continue
    i=r["id"]; h=o[i][0]["v19"]; x=rx19(r)
    if x and not h:
        y = lab[i]["v19"] if i in lab else "-"
        c["regex_only", y]+=1
        print("regex-only", i, "label", y, "|", x[0][:160])
    elif x and h: c["both"]+=1
    elif h and not x: c["llm_only"]+=1
print(c)
