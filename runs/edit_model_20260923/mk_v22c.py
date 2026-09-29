"""v22 제외어를 '발표·평가 벌점·설명회 운영 안내·명시적 부정'으로 다시 정리한 변형(v22narrow3, combo3)을 만든다.
편집형 제한 문장(참가 불가·제외·무효·접수 안 함)은 살리고, 자연 공고의 감점·서면 대체·참석 시간·자료 제공·관련 없음은 막는다."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
old = HERE.joinpath("variants", "v22narrow2.py").read_text(encoding="utf-8")
start = old.index("BRIEF_NOT_RESTRICT_RE = re.compile(")
end = old.index("\n\n", start)
new_block = '''BRIEF_NOT_RESTRICT_RE = re.compile(
    # 제안서 발표·평가 절차(국가 시행령 제43조⑧)와 그 벌점: 참가자격 제한이 아니다
    r"제안서?\\s*(평가\\s*)?설명|제안\\s*설명|제안\\s*내용을\\s*설명|발표|프레젠테이션|ppt|PPT|질의\\s*응답|순서"
    r"|감점|0\\s*점|점\\s*처리|최저점|서면\\s*(심사|평가|대체)"
    # 설명회 운영 안내: 참석 신청 마감·시간·인원·지참물·자료 배부·설명회 미개최
    r"|참석\\s*(인원|시간)|지참|자료[^\\n]{0,10}(별도\\s*)?(제공|배부)|생략|갈음|미실시|실시하지\\s*않|개최하지\\s*않"
    r"|설명회에\\s*참석할\\s*수\\s*없"
    # 명시적 부정
    r"|필수\\s*(조건|사항)이?\\s*아니|의무\\s*(사항)?\\s*(은|이)?\\s*아니|불이익|무관|상관\\s*없|관계\\s*없|관련\\s*(이\\s*)?없"
    r"|제한\\s*(은|이)?\\s*없|불참하더라도|불참해도|미참석\\s*업체도|미참석자도|업체도\\s*(협상|입찰|참가)|독려|참석이\\s*불가능할")'''
v22 = old[:start] + new_block + old[end:]
HERE.joinpath("variants", "v22narrow3.py").write_text(v22, encoding="utf-8")

combo = HERE.joinpath("variants", "combo2.py").read_text(encoding="utf-8")
s2 = combo.index("BRIEF_NOT_RESTRICT_RE = re.compile(")
e2 = combo.index("\n\n", s2)
HERE.joinpath("variants", "combo3.py").write_text(combo[:s2] + new_block + combo[e2:], encoding="utf-8")
print("ok")
