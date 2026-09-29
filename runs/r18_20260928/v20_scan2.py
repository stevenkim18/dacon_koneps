import sys, re, pickle, importlib.util, random
from collections import Counter
sys.path.insert(0, "runs/r18_20260928")
from load20k import load
spec = importlib.util.spec_from_file_location("m", "submissions/20260929_r17_edit_shapes/script.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
recs = load()
SWC = re.compile(r"(정보\s*시스템|시스템|홈페이지|플랫폼|포털|DB|데이터베이스|전산|소프트웨어|S/?W|앱|어플리케이션|애플리케이션|웹|누리집|정보화|ISP|ISMP|클라우드|전자\s*정부)"
                 r"[^\n]{0,15}(구축|고도화|개발|개편|유지\s*보수|유지\s*관리|운영|재구축|개선|전환|리뉴얼|통합)")
out = []
for r in recs:
    m = r["meta"]; p = M.price(r) or 0
    if p < 1e8 or str(m.get("계약방법")) == "수의계약": continue
    if M.is_software(r): continue
    t = M.title_of(r)
    if SWC.search(t):
        src = M.full_text(r)
        out.append((r["id"], t[:90], m.get("업무구분"), str(m.get("면허업종제한목록"))[:70], "소프트웨어" in src, bool(re.search(r"대기업|중견기업|상호출자", src))))
print(len(out))
c = Counter((o[2], o[4], o[5]) for o in out); print(c)
random.seed(2)
for o in random.sample(out, min(45, len(out))): print(o)
