import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fit import IC, D, lab, C, pool
a, b = sys.argv[1], sys.argv[2]
print(f'{"item":5} {"A tpC/fpC/fnC fpM unl":28} {"B tpC/fpC/fnC fpM unl":28}  changed notices (dev)')
for v in D.ITEMS:
    x, y = IC[a][v], IC[b][v]
    if x == y: continue
    ch = []
    for i in C[a]['dev']:
        if C[a]['dev'][i][v] != C[b]['dev'][i][v]:
            ch.append(f"{'+' if C[b]['dev'][i][v] else '-'}{i.replace('PPS-DEV-','')}{pool(i)}(y={lab[i][v]})")
    print(f"{v:5} {x['tpC']}/{x['fpC']}/{x['fnC']} {x['fpM']} {x['unl']:<14} {y['tpC']}/{y['fpC']}/{y['fnC']} {y['fpM']} {y['unl']:<14} {' '.join(ch)}")
