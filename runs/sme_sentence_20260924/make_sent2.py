"""Stage 2 on top of make_sent.py output: parser fixes found while reading v17 hits + v17 small-business private contracts.

usage: python make_sent2.py SENT_SCRIPT.py OUT.py [--no-v17q] [--no-parser]
"""
import sys

inp, out = sys.argv[1], sys.argv[2]
flags = set(sys.argv[3:])
src = open(inp, encoding="utf-8").read()


def sub(old, new, count=1):
    global src
    assert src.count(old) == count, (src.count(old), old[:90])
    src = src.replace(old, new)


if "--no-parser" not in flags:
    # A) 가운뎃점 변형('소기업⋅소상공인 확인서', U+22C5·U+2219·U+30FB)도 같은 구분자다(무라벨 PPS-D-015659)
    sub('DOT = "·ㆍ‧․･•"', 'DOT = "·ㆍ‧․･•⋅∙・"')
    # B) '중소기업 또는 소상공인확인서'는 확인서 이름이다 — 본문 수준 낱말로 읽지 않는다(무라벨 PPS-D-007970)
    sub('''                         rf"|중기업\\s*(또는|및|,|[{DOT}])\\s*소기업\\s*[{DOT}]?\\s*소상공인\\s*확인서")''',
        '''                         rf"|중기업\\s*(또는|및|,|[{DOT}])\\s*소기업\\s*[{DOT}]?\\s*소상공인\\s*확인서"
                         r"|중소기업\\s*(또는|및)\\s*소상공인\\s*확인서")''')
    # B2) 확인서 이름 변형: '<중·소기업 확인서>'(일반 확인서), '소기업이나 소상공인확인서', '중소기업확인서(소기업 또는 소상공인)'
    sub('''                         r"|중소기업\\s*(또는|및)\\s*소상공인\\s*확인서")''',
        '''                         r"|중소기업\\s*(또는|및)\\s*소상공인\\s*확인서"
                         rf"|중\\s*[{DOT}/]\\s*소기업\\s*확인서")''')
    sub('''CERT_SMALL_RE = re.compile(rf"(?<![중{DOT}])소기업\\s*[{DOT}및또는,\\s]*소상공인\\s*확인서|(?<![중{DOT}])소기업\\s*확인서"
                           rf"|중소기업\\s*확인서\\s*\\(\\s*소기업\\s*[{DOT}/,]?\\s*소상공인")''',
        '''CERT_SMALL_RE = re.compile(rf"(?<![중{DOT}])소기업\\s*(?:[{DOT}및또는,\\s]|이나|혹은)*소상공인\\s*확인서|(?<![중{DOT}])소기업\\s*확인서"
                           rf"|중소기업\\s*확인서\\s*\\(\\s*소기업\\s*(?:[{DOT}/,]|또는|및|이나)?\\s*소상공인")''')
    # B3) 조문 인용 '법 제33조제1항에 따라 중소기업자로 보는 법인'은 소기업·소상공인 정의의 일부다
    sub('''    body = re.sub(r"중소기업(으로)?\\s*간주(되는|된)?", " ", body)''',
        '''    body = re.sub(r"중소기업(으로)?\\s*간주(되는|된)?|중소기업자로\\s*보는", " ", body)''')
    # C) '… 소기업·소상공인 확인서를 소지한 자. 다만, 여성기업·장애인기업은 중기업도 참여 가능'처럼 '다만' 뒤 예외절의
    #    수준 낱말이 주 자격을 덮지 않게, '다만' 앞부분이 수준을 말하면 그것을 쓴다(무라벨 PPS-D-006400·000846)
    sub('''    if not sentence:
        return None
    small_cert = bool(CERT_SMALL_RE.search(sentence))''',
        '''    if not sentence:
        return None
    m_but = re.search(r"다만\\s*[,，]?|\\(\\s*단\\s*[,，]", sentence)
    if m_but and m_but.start() > 10:
        head = classify_level(sentence[:m_but.start()])
        if head:
            return head
    small_cert = bool(CERT_SMALL_RE.search(sentence))''')

if "--no-v17q" not in flags:
    # D) 시행령 제2조의2 ①1호 단서(가목: 소기업 3인 이하, 나목: 유찰)는 1억 미만에서도 중소기업자 간 제한경쟁을 허용한다.
    #    본문이 그 단서를 근거로 명시하면 중소기업 수준 제한은 위반이 아니다(무라벨 PPS-D-002419·013080).
    sub('''\nEXCEPTION_RE = re.compile(''', '''\nSMALL_PROVISO_RE = re.compile(r"제\\s*2\\s*조의\\s*2[^\\n]{0,25}?(단서|제?\\s*1\\s*호\\s*(가|나)\\s*목)")\nEXCEPTION_RE = re.compile(''')
    sub('''        v["v17"] = int(p < ONE_HUNDRED_MILLION and level == "중소기업")
        v["v18"]''', '''        v["v17"] = int(p < ONE_HUNDRED_MILLION and level == "중소기업" and not SMALL_PROVISO_RE.search(full_text(rec)))
        v["v18"]''')
    # E) 2천만~1억 수의계약의 근거가 '소기업 또는 소상공인과 체결하는 계약'(국가 시행령 제26조①5호가목3)·지방 시행령
    #    제25조①5호라목, meta 조항호내용 '(소기업 소상공인 계약)')인데 자격을 중소기업 수준으로 두면 근거 조항과 어긋난다.
    #    항목표는 v2·v6·v7·v8에만 '지방 + 소액수의 가능'을 두었고, v17 대표 예시 DEV-21이 바로 이 소액수의견적이다.
    sub('''        v["v18"] = int(p < ONE_HUNDRED_MILLION and level == "없음" and not absence_exception)
''', '''        v["v18"] = int(p < ONE_HUNDRED_MILLION and level == "없음" and not absence_exception)
    if private_contract and not comp and not exception and priced and "소기업" in str(meta(rec, "조항호내용") or ""):
        v["v17"] = int(p < ONE_HUNDRED_MILLION and level == "중소기업" and not SMALL_PROVISO_RE.search(full_text(rec)))
''')

open(out, "w", encoding="utf-8").write(src)
print("written", out)
