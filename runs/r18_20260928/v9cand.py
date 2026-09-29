"""V9C 후보 줄 넓히기: 기존 model_candidate_lines 뒤에 제조사·상표 낱말/모델 번호 모양 줄을 덧붙인다(기존 줄 순서·집합 유지, 최대 40줄)."""
import re
BRANDS_LATIN = (r"Intel|AMD|NVIDIA|Nvidia|Samsung|SAMSUNG|Apple|Dell|DELL|Lenovo|ASUS|Asus|Acer|Microsoft|Cisco|CISCO|Juniper|Huawei|HUAWEI|"
                r"Hikvision|HIKVISION|Dahua|Hanwha|Axis|AXIS|Bosch|BOSCH|Siemens|SIEMENS|Philips|PHILIPS|Panasonic|Sony|SONY|Canon|Epson|EPSON|"
                r"Brother|Fujifilm|Fuji\s?Xerox|Xerox|Ricoh|RICOH|Kyocera|Agilent|Thermo\s?Fisher|Thermo|Shimadzu|SHIMADZU|Waters|Bruker|PerkinElmer|"
                r"Zeiss|ZEISS|Olympus|OLYMPUS|Nikon|Leica|Hitachi|HITACHI|Toshiba|Mitsubishi|Daikin|Carrier|Honeywell|Schneider|ABB|Omron|OMRON|"
                r"Fluke|FLUKE|Keysight|Tektronix|Rohde|Yokogawa|DJI|Garmin|Trimble|Topcon|Stryker|Medtronic|Mindray|Oracle|ORACLE|Red\s?Hat|RedHat|"
                r"VMware|Adobe|Autodesk|IBM|NetApp|Fortinet|FortiGate|Palo\s?Alto|Aruba|Netgear|TP-?Link|Logitech|Makita|DeWalt|Milwaukee|Hilti|"
                r"Kubota|Yanmar|John\s?Deere|Caterpillar|Komatsu|Volvo|Hyundai|HYUNDAI|Kia|Ryzen|Xeon|Core\s?i\d|GeForce|Quadro|Radeon|iPad|iPhone|"
                r"MacBook|Galaxy|ThinkPad|OptiPlex|ProBook|EliteBook|LaserJet|Jabra|Polycom|Crestron|Extron|Barco|BenQ|ViewSonic|Optoma|Vivitek")
BRAND_RE = re.compile(r"(?<![A-Za-z])(?:%s)(?![a-z])" % BRANDS_LATIN)
BRAND_KO_RE = re.compile(r"(?<![가-힣])(?:삼성전자|엘지전자|LG전자|한화비전|한화테크윈|대동공업|현대자동차|기아자동차|쿠쿠전자|위니아|코웨이|린나이|경동나비엔|귀뚜라미|"
                         r"신도리코|캐논|엡손|레노버|시스코|화웨이|하이크비전|다후아|보쉬|지멘스|필립스|파나소닉|도시바|후지쯔|교세라|제록스|"
                         r"인텔|엔비디아|마이크로소프트|오라클|레드햇|안랩|한글과컴퓨터|퍼시스|한샘|일룸|시디즈|휴롬|"
                         r"아크론브라스|애질런트|써모피셔|시마즈|니콘|올림푸스|히타치|미쓰비시|다이킨|허니웰|구보타|얀마|마키타|디월트|힐티|로지텍)(?![가-힣]{0,1}(?:션|리케이션))")
KO_MAKER_PAREN_RE = re.compile(r"[\(（]\s*(?:주\)|㈜)?\s*[가-힣]{2,}(?:전자|공업|산업|정밀|계측|테크|기계|화학|제약|중공업|모터스|통신|케미칼|메디칼|바이오)\s*[\)）]")
KO_HINT_RE = re.compile(r"형식\s*명|형\s*명\s*[:：]|제작사\s*[:：]|제조원\s*[:：]|메이커\s*[:：]|[Mm]odel\s*(?:[:：]|[Nn]o)|[Bb]rand\s*[:：]|[A-Za-z0-9]\s*시리즈")
MIXED_MODEL_RE = re.compile(r"(?<![A-Za-z0-9])(?:\d{2,}(?!E\d)[A-Z]+\d+[A-Za-z0-9\-]*|[A-Z][a-z]+\s\d\s\d{3,}[A-Z]*)(?![A-Za-z0-9])")


def is_extra(s: str) -> bool:
    return bool(BRAND_RE.search(s) or BRAND_KO_RE.search(s) or KO_MAKER_PAREN_RE.search(s) or KO_HINT_RE.search(s) or MIXED_MODEL_RE.search(s))


def extra_lines(M, rec, base_lines, cap=40):
    order = {"규격서": 0, "과업지시서": 1, "제안요청서": 2, "공고문": 3}
    out = list(base_lines)
    seen = set(base_lines)
    if len(out) >= cap:
        return out
    for d in sorted(rec["docs"], key=lambda d: order.get(d["type"], 4)):
        for line in d["text"].split("\n"):
            s = line.strip()
            if len(s) < 4 or s[:200] in seen:
                continue
            if is_extra(s):
                seen.add(s[:200]); out.append(s[:200])
                if len(out) >= cap:
                    return out
    return out
