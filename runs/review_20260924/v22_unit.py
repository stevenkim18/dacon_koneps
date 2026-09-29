"""v22 설명회 참석 제한 정규식 단위 점검: dev 정답 문장·편집형 합성 문장은 켜지고, 자연 공고 오탐 예시는 꺼져야 한다.
사용: .venv/bin/python runs/review_20260924/v22_unit.py OLD/script.py NEW/script.py"""
import sys, csv, importlib.util
sys.path.insert(0, "runs/edit_model_20260923")
from paraphrases import P
def mod(p):
    s = importlib.util.spec_from_file_location("m" + str(abs(hash(p))), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old, new = mod(sys.argv[1]), mod(sys.argv[2])
gold = [r["e22"].replace("\n", " ") for r in csv.DictReader(open("open/dev_labels.csv", encoding="utf-8")) if r["v22"] == "1"]
should_fire = gold + P["v22"] + P["v22_more"]
should_not = [
    "현장설명회 참석은 필수사항은 아니나, 현장설명회를 참여하지 않아 발생되는 모든 문제의 귀책은 입찰참가자에게 있으며, 연구원은 일체의 책임을 부담하지 않음",
    "※ ’26.6.30(화) 17시까지 사업설명회 참석여부 및 인원 확인 필수([이메일])",
    "5. 기타사항(직원 설명회, 의견수렴 등 지원) Ⅲ. 제안 안내 6 1. 입찰참가자격 2. 제안참가 안내 3. 제안서의 효력 4. 기타사항",
    "가. 과업설명회 가. 대표사를 포함하여 입찰참가자격을 충족한 3개사 이내로 구성하여야 하며, 중복",
    "사업설명회 참석은 필수가 아닙니다.",
    "설명회 참석은 의무사항은 아니며 미참석에 따른 불이익은 없음",
]
bad = 0
for label, sents, want in (("fire", should_fire, True), ("quiet", should_not, False)):
    for s in sents:
        o, n = bool(old.briefing_restriction(s)), bool(new.briefing_restriction(s))
        flag = "" if n == want else "  <-- WRONG"
        bad += n != want
        print(f"[{label}] old={int(o)} new={int(n)}{flag} | {s[:90]}")
print(f"\nshould-fire {sum(bool(new.briefing_restriction(s)) for s in should_fire)}/{len(should_fire)} (old {sum(bool(old.briefing_restriction(s)) for s in should_fire)}) · "
      f"should-not fired {sum(bool(new.briefing_restriction(s)) for s in should_not)}/{len(should_not)} (old {sum(bool(old.briefing_restriction(s)) for s in should_not)}) · wrong {bad}")
