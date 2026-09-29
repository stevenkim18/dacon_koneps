import sys
S = sys.argv[1]
old = ('BRIEF_RESTRICT_RE = re.compile(r"설명회[^\\n]{0,80}(참석[^\\n]{0,30}(한하|만|자격|허용되지|제외|접수하지|불가)"\n'
       '                               r"|미참석|불참|참석하지 아니한|참석한 자)")')
new = ('BRIEF_RESTRICT_RE = re.compile(r"설명회[^\\n]{0,80}(참[석가][^\\n]{0,30}(한하|한해|만|자격|허용되지|제외|접수하지|불가|없|무효|필수)"\n'
       '                               r"|미참석|불참|참석하지\\s*(아니한|않은)|참석한\\s*(자|업체))")')
for src_name, dst_name in [("combo.py", "combo2.py"), ("v22narrow.py", "v22narrow2.py")]:
    src = open(f"{S}/var/{src_name}", encoding="utf-8").read()
    assert src.count(old) == 1, (src_name, src.count(old))
    open(f"{S}/var/{dst_name}", "w", encoding="utf-8").write(src.replace(old, new))
print("ok")
