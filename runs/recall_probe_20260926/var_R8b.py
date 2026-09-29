#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — scope_cleanup 변형(09-27 후보).

vague_perf_no_v10q(v10 소액수의 규칙 제거) 위에 채점 범위·비자격 문장 정리를 얹었다: A, C, D
(A v20 수의계약 견적 제외 · C v12 조건부 안내문·입증서류 제외 · D v1 비제한 서술을 근거로 쓰지 않음). LLM 호출은 같다.

이하 vague_perf_no_v10q 설명.


09-26 제출(safetynet_vague_perf) 결과로 v10 소액수의 규칙(판로지원법 제9조①1호)만 가를 때 낸다. v17 소액수의
(dev DEV-21 v17=1)와 나머지는 그대로다.

이하 safetynet_vague_perf 설명.


09-25 P2(막연한 실적 요구): 금액·기간·건수·동종 같은 구체성 표지 없이 '무엇의 실적이 있는·보유한 업체',
'실적이 우수한 업체'로 쓴 자격 줄도 실적 요구로 읽는다. 집행기준 제5조① 단서(고시금액 미만 제조·용역은 실적으로
자격 제한 금지)에 구체성 요건은 없다. dev DEV-048 v8 정탐 +1 · DEV-057 v8 오탐 +1(위반 묶음, 편집 대상이 아닌 줄).
무라벨 20,000 v2 +94 · v8 +37 · v4 +1(새 적중 판독: 입찰자 실적 요구 다수, 학교 여행·수련 상투문 '유경험업체로서
실적이 우수하고 건실한 업체' 일부). 서버 경로 주입 v2 10/80 → 80/80. LLM 호출·입력은 바뀌지 않는다.

이하 private_scope_safetynet 설명.


09-25 안전망(safetynet): LLM이 판정하는 항목에 정규식 보조를 붙인다. 저장 출력 950건(dev+무라벨 750, int8) 기준
  S1) v13·v15 기업규모 수준: 본 호출·전용 호출이 모두 '없음'일 때만 정규식 수준 사용 — 판정 변화 0건.
  S2) v19 확약서 정규식 OR(서약·계약 시·낙찰자 의무 제외) — dev 정규식 적중 3건 모두 라벨 1, 무라벨 750 새 적중 2건.
  or 모드의 근거 키(특정기관_근거·확약서_근거)는 불리언을 정규식만 참으로 만들었으면 정규식 줄을 쓴다.

09-25 검토 수정(v1fix): v1 정규식 보조(ITEM_SOURCE v1='or')가 LLM 출력이 있으면 작동하지 않았다. 'or' 모드는
특정기관_한정만 LLM∨정규식으로 합치고 근거는 LLM 값(대개 null)을 써서, 근거 공란 규칙에 걸려 v1=0이 됐다.
특정기관_근거를 사실 병합 키(FACT_KEYS)에 넣어 LLM 근거가 비면 정규식 근거를 쓰게 한다. 다른 출처 모드의 항목은
이 키를 쓰지 않아 영향이 없다. 저장 출력(int8 dev 200·무라벨 750, 4bit dev) 판정 변화 0, int8 출력이 있는 상태의
주입 시험 v1 0/60 → 60/60(대학·산학협력단 문장 5종 × 12건).

이하 원래 설명.


기준: submissions/20260925_v8nat_v22fix_v21wide. LLM 호출·프롬프트·출력 예산은 그대로 두고 판정기의 정규식만 바꾼다.
바꿔 쓴 위반 문장(주입 시험)을 잡되 무라벨 20,000에서 새로 켜지는 것은 원문을 읽어 확인한 것만 넣었다(09-24 ③).
  1) v4 공공 발주처 실적: '광역자치단체·중앙행정기관·관공서·준정부기관' 어휘, '…이상인 자' 어미, 공공 발주처로 한정한
     실적 요구('실적이 있는·보유한')는 금액·기간 없이도 구체적이다(집행기준 제5조④3). 20,000 v4 +35 · v2 +15 · v8 +6.
  2) 기업규모 파서: '…확인서를 소지하여야', '…자격을 구비해야', '확인서 소지업체', '…만 참여 가능'도 자격 문장으로
     읽는다. 확인서 미발급 안내('…발급받지 못한 업체에 한함')는 자격 문장이 아니다. 입찰방법 머리말은 참가자격에
     기업규모 문장이 따로 없을 때 제한의 근거로 쓰지 않는다(dev DEV-039 v18=1). 20,000 v16 −26 · v11 −18 · v18 −7 등.
  3) v12 직생 요구: '발급받은·확인을 받은·갖춘·제출한 업체(자)'도 입찰자 자격 어미가 붙으면 요구로 본다.
  4) 지역: '소재 업체', '관내 업체', '주된 사무소', '사업장을 둔', '지역 업체만'(도급자 의무·과업 설명 제외). 20,000 변화 0.
  5) v1 보조 탐지: '대학·산학협력단·연구기관만 (입찰) 참여 가능'을 정규식으로도 읽어 LLM과 OR. 20,000 변화 0.
  dev: DEV-039 v18 정탐 +1(로컬 4bit, 클라우드 int8 두 실행). 무라벨 750 저장 출력 v4 +1.

이하 v8nat_v22fix_v21wide 설명.

기준: submissions/20260924_int8_quote_port (Public 0.690815618). LLM 호출·프롬프트·출력 예산은 그대로 두고 판정기의
정규식·판정 줄만 바꾼다. 세 변경 모두 양성을 더하는 방향이다.
  1) v8 국가계약 적용: 항목표 v8의 국가 근거인 국가계약법 시행규칙 제25조⑤와 정부 입찰·계약 집행기준 제5조④1은
     시행령 제21조①의 제한사항을 중복해 제한하지 못하게 한다(예외는 제6호 지역 + 제2호 공사 기술·실적뿐).
     판정 줄의 `local` 조건을 뗀다. 무라벨 20,000 +66.
  2) v22 설명회 참석 제한 정규식 정리: 제외어를 발표·평가 벌점·설명회 운영 안내·명시적 부정으로 좁히고,
     '입찰참가자격'의 '참가', 조사가 붙은 부정, 참석 여부 회신 요청을 가린다. 무라벨 20,000 +31,
     바꿔 쓴 제한 문장 주입 80/144 → 144/144.
  3) v21 지분 하한 표현 확장: '최소' 없는 지분율·출자비율·참여비율 하한도 읽는다('분담' 표현 제외).
     무라벨 20,000 변화 0, 바꿔 쓴 지분 문장 주입 32/112 → 104/112.
  dev 판정 변화 0(로컬 4bit, 클라우드 int8 두 실행). 무라벨 750 저장 출력 v8 +3.

이하 int8_quote_port 설명.

기준: submissions/20260924_v20_quote_region35. LLM 호출·프롬프트는 그대로 두고, 서버(vLLM int8) 모델의 출력 형식 차이로
버려지던 사실만 되살린다(2026-09-23 클라우드 int8 출력 950건 분석).
  1) 인용 복원(`_ground_quote`): 전용 호출(기업규모·지역)의 줄 단위 인용 검사(`_verified_lines`)에서, 인용이 원문과
     공백·줄바꿈만 다르면 원문 구간을 그대로 쓴다. int8은 여러 줄 인용을 한 줄로 이어 붙여 정확 일치 검사에서 탈락했다
     (기업규모 전용 호출 자격 인용 113건/949건, 4bit는 줄바꿈이 남아 줄 단위 검사로 살았다).
     본 호출 근거(v1 근거 필수·기업규모 재분류)에는 앞에 붙은 '(공고문)' 같은 문서명만 떼고 정확 일치를 유지한다 —
     여기까지 공백 복원을 넓히면 무라벨에서 v1 오탐 추가·v13 정탐 손실이 생겼고, 이 필드의 공백 불일치는 4bit도
     같은 비율(14.1% vs 13.0%)이라 int8 고유 문제가 아니었다. e열 근거에만 공백 복원(`_evidence_span`)을 쓴다.
  2) v24 업종 축(`text_industry_codes`): 원문 업종 등록 문장의 4자리 업종코드를 meta와 직접 대조한다.
     int8은 공고서 업종코드 칸에 meta 값을 옮기기도 했다(DEV-079: 원문 5210, meta 5246).
  int8 dev 0.8468 → 0.8583, 교차 검증 0.8016 → 0.8327(두 번째 int8 실행 0.8410 → 0.8525). 로컬 4bit dev 0.8706 그대로.

이하 sme_level 설명(이후 후보들의 변경은 각 submissions/*/README.md에 있다).

기준: submissions/20260917_audit_v9. LLM 호출·프롬프트는 그대로 두고 판정기의 기업규모·우선조달 예외 해석만 고친다.
  1) 우선조달 예외(`has_procurement_exception`): '시행령 제2조의3 제1항 제2호에 따라 비영리법인도 참가 가능' 정형 문구는
     제한을 유지한 채 비영리법인만 더 받는 것이라 예외로 보지 않는다. LLM의 예외 판단도 이 정규식 값으로 통일한다.
  2) 기업규모 수준(`classify_level`): 확인서 이름을 지운 본문으로 판단하고, 본문이 '중소기업 또는 소상공인'이어도
     요구 확인서가 소기업·소상공인 확인서뿐이면 소기업 수준. '(중소기업자)' 설명 괄호·'중소기업자 우선조달' 문구 제외.
  3) LLM 기업규모 근거가 메타 '조항호내용'이거나 기업규모 단어가 없는 문장(직생 증명서 등)이면 '없음'.
  4) 정규식 수준(`rx_sme_level`): 참가자격 목록 줄('-「중소기업기본법」제2조제2항에 따른 소기업, …, 창업기업') 인식,
     '유찰로 중소기업자간 확대' 문장 제외, 같은 순위에 두 수준이 있으면 소기업·소상공인 우선.
  로컬 MLX dev: 0.7711 → 0.8174, 교차 검증 0.7438 → 0.7849, 무라벨 표본 정밀도 0.596 → 0.607(정탐 34→37).

이하 audit_v9 설명.

기준: submissions/20260917_item_veto. 변경은 세 묶음이다.
  1) v9(특정 모델명 지정): 물품 공고의 규격서·과업지시서에서 모델·제조사 후보 줄을 정규식으로 뽑고,
     "특정 제품을 지정한 줄인가"만 묻는 전용 LLM 호출을 추가한다(`build_model_messages`).
  2) v24(공고서-메타 불일치): LLM이 읽은 계약방법 비교를 뺀다(오탐 원인). 금액은 LLM이 옮긴 숫자가
     원문에 실제로 있을 때만 비교한다.
  3) 무라벨 250건 표본 검토(labels/train250_audit.csv)에서 찾은 오탐 패턴 수정
     - 지역제한 문장: '이야기 소재'·주소 줄·지역업체 가산점 제외(`rx_region`)
     - 기업규모 수준: 법령·기관·확인서 이름 속 '중소기업'을 지우고 주 자격 문장 우선(`classify_level`·`rx_sme_level`),
       LLM 수준도 LLM 근거 문장으로 재분류
     - v16·v18은 제한경쟁 입찰에만 적용, v10은 줄바꿈을 넘어 직생 요구를 넓게 탐지
     - 품목 전용 호출이 과업 정보 부족으로 "해당없음"을 낸 경우 거부권 미적용
  로컬 MLX dev: 0.7357 → 0.7711, 교차 검증 0.6883 → 0.7438, 무라벨 표본 정밀도 0.386 → 0.596.

이하 item_veto 설명.

기준: submissions/20260917_rule_extract (Public 0.6247556727). 변경은 하나다.
  용역 공고에만 "계약 목적물 품목 판별" 전용 LLM 호출을 추가하고(용역 경쟁제품 29개 전체 제시),
  전용 호출이 "해당없음"이면 경쟁제품에서 제외한다(`build_item_messages`·`decide`).
  로컬 MLX dev 200건: 0.7203 → 0.7357, 2분할 교차 검증 평균 0.6774 → 0.6883.

이하 rule_extract 설명.

기존 후보들은 LLM 한 번에 24개 항목의 위반 여부를 "판단"시켰다. dev 200건을 다시 대조해 보니
라벨은 법령 조건식을 기계적으로 적용한 결과였다(docs/05_study_log/20260917/4. from_scratch_reanalysis.md).
그래서 역할을 나눈다.

  LLM(공고당 1회, 용역은 품목 판별 1회 추가) → 공고문·첨부에서 판정에 필요한 "사실"만 JSON으로 추출
                      (실적 요구금액, 제한 지역 단위, 기업규모 제한 수준, 설명회·마감 일자 …)
  정규식            → 같은 사실을 원문에서 한 번 더 추출(LLM 결손·오류 보완)
  Python 판정기     → 메타 금액·계약유형 + 사실 + 법령패키지 기준으로 v1~v24 판정

평가 서버는 이 파일을 `python script.py`로 그대로 실행합니다.
  입력   ./data/test.jsonl.gz (+ 법령패키지/중기부고시 세부품명 CSV)
  출력   ./output/submission.csv  (열 = id, v1..v24, e1..e24)
  경로   PPS_DATA_DIR · PPS_OUTPUT_DIR · PPS_MODEL_DIR 환경변수 우선

로컬 실행
  python script.py --mock          # 모델 없이 입력·출력 흐름 확인(정규식 사실만으로 판정)
  python script.py --limit 10      # 앞 10건 실행
"""
from __future__ import annotations

# ===== 1. 상수·경로 =====
import argparse
import csv
import gzip
import io
import json
import os
import re
import sys
import time
import unicodedata
from datetime import date
from typing import Any, Dict, Iterator, List, Optional, Tuple

DATA_DIR = os.environ.get("PPS_DATA_DIR", "./data")
OUTPUT_DIR = os.environ.get("PPS_OUTPUT_DIR", "./output")
MODEL_DIR = os.environ.get("PPS_MODEL_DIR", "/opt/models/gemma-4-26B-A4B-it")

ITEMS = [f"v{i}" for i in range(1, 25)]
EVID = [f"e{i}" for i in range(1, 25)]
COLUMNS = ["id"] + ITEMS + EVID
ABSENCE = ["v10", "v11", "v16", "v18", "v20"]          # 부재탐지 항목: 근거 문구 빈칸

SEED = 20260826
MAX_MODEL_LEN = 16384
MAX_TOKENS = 1200                       # 본 호출(추출 JSON) 출력 토큰 예산
# 전용 호출별 출력 예산. dev 200건 실측 길이에 여유를 둔 값이다(중앙값/최대):
#   기업규모 175/400+ · 지역 40/233 · 품목 45/65 · 모델명 16/17
TOKENS_ITEM = 128
TOKENS_MODEL = 128
TOKENS_SME = 512
TOKENS_REGION = 320
PROMPT_BUDGET = MAX_MODEL_LEN - MAX_TOKENS
EVIDENCE_MAX = 500
QUANT = "int8_per_channel_weight_only"

# 법령 금액 기준
NOTICE_AMOUNT = 230_000_000             # 고시금액(물품·용역 2억 3천만 원)
LOCAL_REGION_AMOUNT = 500_000_000       # 지방계약법 시행규칙 제24조 제2호 나목(지역제한 가능 금액)
ONE_HUNDRED_MILLION = 100_000_000
LOCAL_MIN_SHARE, NATIONAL_MIN_SHARE = 5.0, 10.0

PROVINCES = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시",
             "세종특별자치시", "경기도", "강원특별자치도", "강원도", "충청북도", "충청남도", "전북특별자치도",
             "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도", "제주도"]
PROVINCE_ALIAS = {"강원도": "강원특별자치도", "전라북도": "전북특별자치도", "제주도": "제주특별자치도"}
PROVINCE_RE = re.compile("|".join(sorted(PROVINCES, key=len, reverse=True)))


# 2026-09-22 운영 공지(대회 제공 자료 보완): 시·도(세종 제외)가 발주하는 물품·일반용역의 지역제한 기준 3억 5천만 원.
# 시·도 발주는 원문 첫머리가 시·도명으로 시작하는 공고로 식별한다(교육청·기초 토큰 제외). 무라벨 20,000 변경 0건 — 법대로 맞춘 것이다.
PROVINCE_REGION_AMOUNT = 350_000_000
PROVINCE_HEAD_RE = re.compile(r"^\s*(?:%s)(?!\s*(?:교육|\[지역:|\[수요기관\(기초))" % "|".join(p for p in sorted(PROVINCES, key=len, reverse=True) if p != "세종특별자치시"))


def province_issuer(rec: Dict[str, Any]) -> bool:
    if meta(rec, "소관구분") != "지방정부":
        return False
    docs = rec.get("docs") or []
    head = str((docs[0] or {}).get("text") or "")[:120] if docs else ""
    if "기초" in head[:80]:
        return False
    return bool(PROVINCE_HEAD_RE.search(head))


def local_region_amount(rec: Dict[str, Any]) -> int:
    return PROVINCE_REGION_AMOUNT if province_issuer(rec) else LOCAL_REGION_AMOUNT


def log(msg: str) -> None:
    print(f"[rule_extract] {msg}", file=sys.stderr, flush=True)


# ===== 2. 데이터 로더 =====
def _open(path: str):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return io.open(path, "r", encoding="utf-8")


def validate_record(rec: Any) -> None:
    if not isinstance(rec, dict):
        raise ValueError(f"레코드가 object가 아니다: {type(rec).__name__}")
    for k in ("id", "docs", "meta"):
        if k not in rec:
            raise ValueError(f"필수 키 없음: {k}")
    if not isinstance(rec["docs"], list) or not rec["docs"]:
        raise ValueError(f"docs가 비어 있다 (id={rec['id']})")
    for d in rec["docs"]:
        if not isinstance(d, dict) or not isinstance(d.get("text"), str):
            raise ValueError(f"docs 원소 형식 오류 (id={rec['id']})")
    if not isinstance(rec["meta"], dict):
        raise ValueError(f"meta가 object가 아니다 (id={rec['id']})")


def normalize(rec: Dict[str, Any]) -> Dict[str, Any]:
    for d in rec.get("docs", []):
        d["text"] = unicodedata.normalize("NFC", d["text"])
        if isinstance(d.get("type"), str):
            d["type"] = unicodedata.normalize("NFC", d["type"])
    return rec


def iter_records(path: str, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
    n = 0
    with _open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{lineno} JSON 파싱 실패: {e}") from e
            validate_record(rec)
            yield normalize(rec)
            n += 1
            if limit and n >= limit:
                return


def full_text(rec: Dict[str, Any]) -> str:
    return "\n".join(d["text"] for d in rec["docs"])


def meta(rec: Dict[str, Any], key: str) -> Any:
    return rec.get("meta", {}).get(key)


def price(rec: Dict[str, Any]) -> Optional[float]:
    for key in ("입찰추정가격", "배정예산금액"):
        v = meta(rec, key)
        try:
            if v not in (None, ""):
                return float(v)
        except (TypeError, ValueError):
            pass
    return None


def is_local(rec: Dict[str, Any]) -> bool:
    return meta(rec, "적용계약법") == "지방계약법"


def is_negotiation(rec: Dict[str, Any]) -> bool:
    return meta(rec, "낙찰방법") == "협상에의한계약"


def is_goods(rec: Dict[str, Any]) -> bool:
    return "물품" in str(meta(rec, "업무구분") or "")


def local_small_quote(rec: Dict[str, Any]) -> bool:
    # 항목표 비고 "지방 + 소액수의 가능": 지방계약 소액수의견적은 실적·지역 제한 위반 대상에서 제외
    return is_local(rec) and meta(rec, "낙찰방법") == "소액수의견적"


# ===== 3. 법령패키지: 중기간 경쟁제품 세부품명 =====
LIMIT_RE = re.compile(r"추정가격\s*([\d,\.]+)\s*(억|천만|백만)?\s*원\s*미만")
UNIT = {"억": 1e8, "천만": 1e7, "백만": 1e6, "만": 1e4, None: 1}


def load_competitive_table(data_dir: str = DATA_DIR) -> Dict[str, Dict[str, Any]]:
    """세부품명번호 → {이름, 특이사항, 금액한도}. 특이사항의 "추정가격 N억원 미만에 한함"을 금액한도로 읽는다."""
    p = os.path.join(data_dir, "법령패키지", "중기부고시", "중기부고시_경쟁제품_세부품명.csv")
    table: Dict[str, Dict[str, Any]] = {}
    try:
        with io.open(p, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                code = (row.get("세부품명번호") or "").strip()
                if not code:
                    continue
                note = (row.get("특이사항") or "").strip()
                m = LIMIT_RE.search(note)
                limit = float(m.group(1).replace(",", "")) * UNIT[m.group(2)] if m else None
                table[code] = {"name": (row.get("세부품명") or "").strip(), "note": note, "limit": limit,
                               "group": (row.get("제품명") or "").strip(), "category": (row.get("대분류") or "").strip()}
    except OSError:
        pass
    return table


CODE_RE = re.compile(r"(?<!\d)(\d{4})\s?(\d{6})(?!\d)")


def meta_item_codes(rec: Dict[str, Any]) -> List[str]:
    """나라장터 메타 `세부품명번호목록`에 적힌 코드만 돌려준다(본문에서 주워 온 코드와 구분).

    이 목록은 발주기관이 조달 목적물로 직접 입력한 값이라 본문 언급보다 강한 증거다.
    무라벨 750건 라벨 검토: 메타에 경쟁제품 코드가 있는데 본 호출 LLM이 '해당없음'이라 한 건은 **4/4 전부 누락**이었고
    (PPS-D-001079 교탁·018087 무선통신장치·020912 전기자동차용충전장치·005897 대형온습도환경조성실),
    본문에서만 나온 코드는 2/3이었다(018375는 테이프백업장치 공고인데 본문의 정보인프라구축서비스를 주워 왔다).
    """
    src = str(meta(rec, "세부품명번호목록") or "")
    out: List[str] = []
    for m in CODE_RE.finditer(src):
        c = m.group(1) + m.group(2)
        if c not in out:
            out.append(c)
    return out


def codes_in_record(rec: Dict[str, Any]) -> List[str]:
    src = (meta(rec, "세부품명번호목록") or "") + "\n" + full_text(rec)
    seen: List[str] = []
    for m in CODE_RE.finditer(src):
        c = m.group(1) + m.group(2)
        if c not in seen:
            seen.append(c)
    return seen


def title_of(rec: Dict[str, Any]) -> str:
    t = rec["docs"][0]["text"]
    m = re.search(r"(용\s*역\s*명|건\s*명|사\s*업\s*명|공\s*고\s*명|물\s*품\s*명|입찰건명)\s*[:：|]?\s*([^\n]{4,100})", t)
    first = next((ln.strip() for ln in t.split("\n") if len(ln.strip()) >= 6), "")
    return ((m.group(2) if m else "") + " " + first)[:200]


def _bigrams(s: str) -> set:
    s = re.sub(r"[\s\W\d_]+", "", s.replace("서비스", ""))
    return {s[i:i + 2] for i in range(len(s) - 1)}


def candidate_items(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]], k: int = 8) -> List[Tuple[str, str, str]]:
    """LLM이 계약 목적물의 세부품명을 고를 후보: 원문·메타에 적힌 번호 + 공고명과 비슷한 경쟁제품 이름."""
    out: List[Tuple[str, str, str]] = []
    for c in codes_in_record(rec)[:10]:
        it = table.get(c)
        out.append((c, it["name"] if it else "(경쟁제품 목록 외 번호)", it["note"] if it else ""))
    tb = _bigrams(title_of(rec))
    scored = []
    for c, it in table.items():
        nb = _bigrams(it["name"])
        if nb and tb:
            s = len(nb & tb) / len(nb)
            if s >= 0.3:
                scored.append((s, c))
    for _, c in sorted(scored, reverse=True)[:k]:
        if all(c != o[0] for o in out):
            out.append((c, table[c]["name"], table[c]["note"]))
    return out


# ===== 4. 프롬프트 문맥: 판정에 필요한 문장만 모은다 =====
SNIPPET_GROUPS = [
    ("참가자격", r"참가\s*자격|자격\s*요건|입찰\s*참가|참여\s*가능|참가할\s*수"),
    ("실적", r"실적"),
    ("지역", r"주된\s*영업소|본점\s*소재지|본사\s*소재|소재지|지역\s*제한|소재한|소재하"),
    ("기업규모", r"중소기업|소기업|소상공인|중기업|비영리|우선조달"),
    ("직접생산", r"직접생산"),
    ("설명회", r"설명회|현장\s*설명|제안요청서?\s*설명|사업\s*설명|과업\s*설명"),
    ("일정", r"마감|접수\s*기간|제출\s*기간|제출\s*일시|공고\s*기간|개찰"),
    ("공동수급", r"공동수급|공동이행|분담이행|지분"),
    ("SW", r"소프트웨어|대기업|상호출자|중견기업"),
    ("확약서", r"확약서|확약|협약서|공급\s*확인"),
    ("모델", r"모델명|모델\s*:|제조사|상표|브랜드|동등\s*이상|동등제품"),
    ("기관한정", r"대학|산학협력단|기관만|기관에 한|협회|조합원|학교"),
    ("계약개요", r"입찰\s*방법|계약\s*방법|제한경쟁|일반경쟁|지명경쟁|수의|업종|예산|기초금액|추정가격|사업비|긴급"),
]
SNIPPET_LINE_MAX = 320
SNIPPET_GROUP_BUDGET = 900
HEADER_CHARS = 1200


def _clip_line(line: str, m: re.Match) -> str:
    if len(line) <= SNIPPET_LINE_MAX:
        return line
    s = max(0, m.start() - SNIPPET_LINE_MAX // 2)
    return line[s:s + SNIPPET_LINE_MAX]


def build_snippets(rec: Dict[str, Any], scale: float = 1.0) -> str:
    """문서별로 키워드 그룹에 걸린 줄을 모은다. 같은 줄은 한 번만 넣고, 그룹마다 글자 예산을 둔다."""
    used_lines = set()
    blocks = []
    header = rec["docs"][0]["text"][: int(HEADER_CHARS * scale)]
    blocks.append(f"[공고문 머리말]\n{header}")
    for name, pat in SNIPPET_GROUPS:
        rx = re.compile(pat)
        picked, used = [], 0
        for d in rec["docs"]:
            for line in d["text"].split("\n"):
                line = line.strip()
                if len(line) < 6:
                    continue
                m = rx.search(line)
                if not m:
                    continue
                piece = _clip_line(line, m)
                if piece in used_lines or piece in header:
                    continue
                if used + len(piece) > SNIPPET_GROUP_BUDGET * scale:
                    break
                used_lines.add(piece)
                picked.append(f"({d['type']}) {piece}")
                used += len(piece)
        if picked:
            blocks.append(f"[{name}]\n" + "\n".join(picked))
    dropped = rec.get("dropped_doc_counts") or {}
    if dropped:
        blocks.append("[미수록 첨부] " + ", ".join(f"{t} {n}건" for t, n in dropped.items()))
    return "\n\n".join(blocks)


def _fit_pieces(pieces: List[str], budget: int) -> List[str]:
    """예산을 넘으면 앞뒤를 번갈아 담아 머리와 꼬리를 모두 남긴다.
    앞에서부터만 채우면 첨부(뒤쪽 문서)의 문장이 통째로 빠진다 — 09-19까지의 결손 원인."""
    if sum(len(p) for p in pieces) <= budget:
        return pieces
    head: List[str] = []
    tail: List[str] = []
    i, j, used, take_head = 0, len(pieces) - 1, 0, True
    while i <= j:
        p = pieces[i] if take_head else pieces[j]
        if used + len(p) > budget:
            break
        (head if take_head else tail).append(p)
        used += len(p)
        if take_head:
            i += 1
        else:
            j -= 1
        take_head = not take_head
    return head + (["…(중략)…"] if i <= j else []) + tail[::-1]


META_FIELDS = ["적용계약법", "업무구분", "계약방법", "낙찰방법", "배정예산금액", "입찰추정가격",
               "세부품명번호목록", "제한지역코드목록", "지역제한여부", "면허업종제한목록", "조항호내용",
               "공고게시일자", "개찰예정일자"]

SYSTEM_PROMPT = """당신은 공공 입찰공고에서 사실을 정확히 뽑는 추출기다. 위반 여부를 판단하지 말고, 질문한 사실만 JSON으로 답한다.
원문에 없는 내용은 추측하지 않는다. 근거 필드에는 원문 문장을 한 글자도 바꾸지 말고 그대로(200자 이내) 옮기고, 없으면 null.

필드 설명
- 계약목적물_세부품명번호: 이번 계약으로 실제 구매·용역하는 대상에 해당하는 세부품명번호(10자리)를 [세부품명 후보]에서 고른다. 맞는 후보가 없으면 "해당없음".
- 직접생산확인_요구: 입찰참가자격으로 직접생산확인증명서 소지를 요구하면 true(제출서류 목록에만 '해당 시'로 있으면 false).
- 기업규모_제한: 입찰참가자격에서 기업 규모를 제한하는 수준.
  "소기업·소상공인" = 소기업 또는 소상공인만 참가 가능. "중소기업" = 중소기업(중기업 포함, '중·소기업·소상공인' 표현 포함)만 참가 가능. 제한이 없으면 "없음".
- 우선조달_예외사유_기재: 판로지원법 시행령 제2조의3 등 우선조달 예외(비영리법인 참가 허용 등)를 공고에 적었으면 true.
- 실적제한: 입찰참가자격으로 일정 금액·규모 이상의 수행·납품 실적을 요구하면 true(제안서 평가 배점용 실적은 false).
- 실적_요구금액_원: 참가자격 실적의 최소 금액(원 단위 정수). 없으면 null.
- 실적_발주처_공공한정: 인정 실적을 국가·지자체·공공기관·특정기관 발주분으로 한정하면 true(민간 실적도 인정하면 false).
- 지역제한: 입찰참가자격으로 본점·주된 영업소 소재지를 제한하면 true(납품장소·주소 안내는 false).
- 지역_단위: 제한 지역이 시·도 단위면 "시도", 시·군·구 단위면 "시군구"([지역:r1|단위=기초] 토큰, [수요기관(기초자치단체)] 관할구역 포함), 없으면 "없음".
- 지역_시도목록: 소재지로 허용한 시·도 이름 목록.
- 특정기관_한정: 대학·산학협력단·특정 협회 회원 등 특정 기관·단체만 참가할 수 있게 하면 true.
- 특정모델_지정: 규격서·과업지시서가 특정 제조사·상표·모델명을 지정하면 true('동등 이상' 허용 문구와 무관하게 모델명을 적시하면 true).
- 확약서_입찰시제출: 제조사 물품공급·기술지원 확약서를 입찰(서류) 제출 시점이나 마감 전에 보유·제출하도록 요구하면 true.
- 설명회_미참석_참가불가: 현장·사업·제안요청 설명회에 참석한 업체만 입찰(제안)할 수 있으면 true.
- 설명회_개최일: 설명회를 연다면 그 날짜(YYYY-MM-DD). 열지 않거나 날짜가 없으면 null.
- 제안서_마감일: 제안서(또는 입찰서) 제출 마감 날짜(YYYY-MM-DD). 없으면 null.
- 공동수급_최소지분율: 공동수급 구성원 최소 지분율(%) 숫자. 없으면 null.
- 대기업_참여제한_문구: 대기업·상호출자제한기업집단·중견기업의 참여 제한을 적었으면 true.
- 공고서_계약방법: 공고서에 적힌 입찰(계약) 방법.
- 공고서_예산금액_원: 공고서에 적힌 사업예산·기초금액(부가세 포함 총액, 원 단위 정수). 없으면 null.
- 공고서_업종코드: 입찰참가자격 업종 등록에 적힌 4자리 업종코드 목록."""


def extraction_schema() -> Dict[str, Any]:
    s_or_null = {"type": ["string", "null"]}
    i_or_null = {"type": ["integer", "null"]}
    b = {"type": "boolean"}
    props = {
        "계약목적물_세부품명번호": {"type": "string"},
        "직접생산확인_요구": b,
        "기업규모_제한": {"type": "string", "enum": ["없음", "중소기업", "소기업·소상공인"]},
        "기업규모_근거": s_or_null,
        "우선조달_예외사유_기재": b,
        "실적제한": b,
        "실적_요구금액_원": i_or_null,
        "실적_발주처_공공한정": b,
        "실적_근거": s_or_null,
        "지역제한": b,
        "지역_단위": {"type": "string", "enum": ["없음", "시도", "시군구"]},
        "지역_시도목록": {"type": "array", "items": {"type": "string"}},
        "지역_근거": s_or_null,
        "특정기관_한정": b,
        "특정기관_근거": s_or_null,
        "특정모델_지정": b,
        "특정모델_근거": s_or_null,
        "확약서_입찰시제출": b,
        "확약서_근거": s_or_null,
        "설명회_미참석_참가불가": b,
        "설명회_개최일": s_or_null,
        "제안서_마감일": s_or_null,
        "설명회_근거": s_or_null,
        "공동수급_최소지분율": {"type": ["number", "null"]},
        "공동수급_근거": s_or_null,
        "대기업_참여제한_문구": b,
        "공고서_계약방법": {"type": "string", "enum": ["일반경쟁", "제한경쟁", "지명경쟁", "수의계약", "불명"]},
        "공고서_예산금액_원": i_or_null,
        "공고서_업종코드": {"type": "array", "items": {"type": "string"}},
    }
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


def build_user_prompt(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]], scale: float = 1.0) -> str:
    m = rec.get("meta", {})
    meta_lines = "\n".join(f"- {k}: {'미기재' if m.get(k) is None else m.get(k)}" for k in META_FIELDS if k in m)
    cands = candidate_items(rec, table)
    cand_lines = "\n".join(f"- {c} {n}" + (f" ({note})" if note else "") for c, n, note in cands) or "- (후보 없음)"
    return (
        f"[공고명] {title_of(rec)[:120]}\n\n"
        f"[나라장터 입력 메타]\n{meta_lines}\n\n"
        f"[세부품명 후보]\n{cand_lines}\n\n"
        f"[공고 원문 발췌]\n{build_snippets(rec, scale)}\n"
    )


def build_messages(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]], scale: float = 1.0) -> List[Dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(rec, table, scale)}]


# ----- 4-1. 용역 품목 판별 호출 -----
# 경쟁제품 여부(v10~v13)와 판로지원 항목(v14~v18)이 모두 "계약 목적물이 경쟁제품인가"에 달려 있다.
# 첫 호출에서 공고명과 글자가 비슷한 후보만 보여 주자 일반적인 이름(운영위탁서비스·측량용역)을 과하게 골랐고,
# "공연 행사 대행"에는 정작 기타행사기획및대행서비스가 후보에 없었다. 용역 경쟁제품은 29개뿐이라 전체를 보여 준다.
ITEM_SYSTEM_PROMPT = """공공 용역 입찰공고의 계약 목적물(실제로 수행시키는 과업)이 아래 [용역 경쟁제품 목록]의 어느 세부품명에 해당하는지 고른다.
- 과업의 주된 내용이 그 세부품명에 직접 해당할 때만 고른다. 단어가 비슷하거나 부수 업무만 겹치면 "해당없음".
- 공고에 적힌 직접생산확인 세부품명은 참고만 한다. 과업 내용과 맞지 않으면 따르지 않는다.
- 목록의 '운영위탁서비스'·'정보시스템유지관리서비스' 등 정보시스템 계열은 소프트웨어·정보시스템 과업일 때만 해당한다.
- 먼저 계약목적물_요약에 과업을 한 구절로 적고, 세부품명번호를 고른다."""
ITEM_CONTEXT_RE = re.compile(r"용\s*역\s*명|사\s*업\s*명|건\s*명|공\s*고\s*명|과업|사업\s*내용|용역\s*내용|주요\s*내용|"
                             r"사업\s*개요|사업\s*목적|목\s*적|범\s*위|세부품명")
ITEM_CONTEXT_CHARS = 1600


def service_codes(table: Dict[str, Dict[str, Any]]) -> List[str]:
    return [c for c in table if c[:2].isdigit() and int(c[:2]) >= 70]


def item_schema(table: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    return {"type": "object", "additionalProperties": False, "required": ["계약목적물_요약", "세부품명번호"],
            "properties": {"계약목적물_요약": {"type": "string", "maxLength": 60},
                           "세부품명번호": {"type": "string", "enum": service_codes(table) + ["해당없음"]}}}


def build_item_messages(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    picked, used, seen = [], 0, set()
    for d in rec["docs"]:
        for line in d["text"].split("\n"):
            line = line.strip()
            if len(line) < 6 or line in seen or not ITEM_CONTEXT_RE.search(line):
                continue
            piece = line[:240]
            if used + len(piece) > ITEM_CONTEXT_CHARS:
                break
            seen.add(line)
            picked.append(f"({d['type']}) {piece}")
            used += len(piece)
    catalog = "\n".join(
        f"- {c} {table[c]['name']} [{table[c]['group']}]" + (f" ({table[c]['note']})" if table[c]["note"] else "")
        for c in service_codes(table))
    user = (f"[공고명] {title_of(rec)[:120]}\n[추정가격] {meta(rec, '입찰추정가격')}\n\n"
            f"[과업 관련 원문]\n" + ("\n".join(picked) or "(없음)") + f"\n\n[용역 경쟁제품 목록]\n{catalog}\n")
    return [{"role": "system", "content": ITEM_SYSTEM_PROMPT}, {"role": "user", "content": user}]


def needs_item_call(rec: Dict[str, Any]) -> bool:
    return not is_goods(rec)


# ----- 4-2. 물품 특정 모델 지정 판별 호출 (v9) -----
# 본 호출은 긴 발췌 속에서 규격 수치·동등 이상 예시까지 모델 지정으로 읽었다(dev v9 F1 0.31).
# 규격서·과업지시서에서 모델·제조사 후보 줄만 뽑아 짧게 묻는다.
MODEL_SYSTEM_PROMPT = """물품 구매 공고의 규격서·과업지시서에서 뽑은 번호 붙은 줄들이다.
특정 제조사의 특정 제품(모델명·상표·제품명)을 지정해서 그 제품을 납품하게 하는 줄이 있는지 판단한다.
- 해당: "제조사·모델명 : ○○ ○○", "Agilent ICP-OES 5900", "DJI Matrice 4 시리즈 배터리일 것", 제품명에 모델번호를 붙여 구매 품목으로 적은 줄.
- 제외: 용량·전압·감도·인터페이스(USB, RJ-45, ISO, IP55 등) 같은 일반 규격 수치, '동등 이상'·'동등품'·'또는 동등' 허용이 붙은 예시, 제조사 증명서·확약서 제출 요구.
해당하는 줄이 있으면 특정모델_지정=true와 가장 대표적인 줄 번호를, 없으면 false와 null을 낸다."""
MODEL_SPEC_WORDS = re.compile(
    r"(USB|RJ|ISO|IP\d|KS|HDMI|Wi-?Fi|LTE|Type|GHz|MHz|DDR|SSD|HDD|PCIe|LED|LCD|UHD|FHD|mAh|Wh|rpm|RPM|PTO|IEC|IEEE|"
    r"SATA|NVMe|Gbps|Mbps|OLED|VGA|DVI|RS-?\d|M\.2)")
MODEL_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Za-z]*[\-\s]?\d{2,}[A-Za-z0-9\-/]*|[A-Z]{2,}\d+[A-Za-z0-9\-]*|"
                            r"\d{2,}[A-Z]{2,}[A-Za-z0-9\-]*)")
MODEL_HINT_RE = re.compile(r"제조사|모델명|모델\s*[:：]|상표|브랜드|\(([A-Z][a-z]+\s?)+\)")
MODEL_MAX_LINES = 40


def model_candidate_lines(rec: Dict[str, Any]) -> List[str]:
    order = {"규격서": 0, "과업지시서": 1, "제안요청서": 2, "공고문": 3}
    out, seen = [], set()
    for d in sorted(rec["docs"], key=lambda d: order.get(d["type"], 4)):
        for line in d["text"].split("\n"):
            s = line.strip()
            if len(s) < 4 or s in seen:
                continue
            tokens = [t for t in MODEL_TOKEN_RE.findall(s) if not MODEL_SPEC_WORDS.match(t)]
            if tokens or MODEL_HINT_RE.search(s):
                seen.add(s)
                out.append(s[:200])
                if len(out) >= MODEL_MAX_LINES:
                    return out
    return out


def needs_model_call(rec: Dict[str, Any]) -> bool:
    return is_goods(rec) and bool(model_candidate_lines(rec))


def model_schema() -> Dict[str, Any]:
    return {"type": "object", "additionalProperties": False, "required": ["특정모델_지정", "줄번호"],
            "properties": {"특정모델_지정": {"type": "boolean"}, "줄번호": {"type": ["integer", "null"]}}}


def build_model_messages(rec: Dict[str, Any]) -> List[Dict[str, str]]:
    lines = model_candidate_lines(rec)
    body = "\n".join(f"{n}. {s}" for n, s in enumerate(lines, 1))
    user = f"[물품] {title_of(rec)[:100]}\n[세부품명] {meta(rec, '세부품명번호목록')}\n\n[후보 줄]\n{body}\n"
    return [{"role": "system", "content": MODEL_SYSTEM_PROMPT}, {"role": "user", "content": user}]


def apply_model_call(rec: Dict[str, Any], llm: Optional[Dict[str, Any]], model_text: str) -> Optional[Dict[str, Any]]:
    """v9 전용 호출 결과로 본 호출의 특정모델 사실을 덮어쓴다. 줄 번호가 유효할 때만 근거로 쓴다."""
    res = parse_facts(model_text)
    if not res or not needs_model_call(rec):
        return llm
    out = dict(llm or {})
    lines = model_candidate_lines(rec)
    idx = res.get("줄번호")
    line = lines[idx - 1] if isinstance(idx, int) and 1 <= idx <= len(lines) else ""
    out["특정모델_지정"] = bool(res.get("특정모델_지정")) and bool(line)
    out["특정모델_근거"] = line or None
    return out


# ----- 4-3. 기업규모·직접생산 전용 호출 (S2, 2026-09-21 추가) -----
# v10·v11·v12·v13·v14·v15·v16·v17·v18 — 9개 항목이 전부 같은 두 사실에 달려 있다.
#   ① 입찰참가자격의 기업규모 제한 수준  ② 직접생산확인증명서 요구 여부
# 본 호출은 29개 필드를 한 장에 묻기 때문에 이 두 사실에 프롬프트를 쓸 자리가 없었다. 게다가 09-20에
# 본 호출에 필드 하나(시설인력_보유제한)를 더했더니 무관한 항목까지 무너졌다(v1 0.667 → 0.218).
# → 두 사실만 묻는 전용 호출로 분리한다. 법 조문을 프롬프트에 넣고, 스키마에서 '원문 인용'을 판단보다
#   앞에 두어(structured outputs는 스키마 순서대로 디코딩한다) 인용 → 판단 순서를 강제한다.
#   인용이 원문의 부분문자열이 아니면 그 사실을 버린다.
SME_LAW_FILE = "중소기업제품 구매촉진 및 판로지원에 관한 법률 시행령.txt"
SME_LAW_FALLBACK = (
    "제2조의2(중소기업자와의 우선조달계약) ① 1. 추정가격이 1억원 미만인 물품 또는 용역: 소기업 또는 "
    "소상공인 간 제한경쟁입찰. 2. 추정가격이 1억원 이상 고시금액 미만: 중소기업자 간 제한경쟁입찰.\n"
    "제2조의3(우선조달계약에 대한 예외) ① 각 호에 해당하면 우선조달계약을 체결하지 않을 수 있다. "
    "2. 학술·연구·조사·평가 등 용역에 비영리법인의 참가가 필요하다고 인정되는 경우. "
    "4. 특정한 성능·기술·품질이 필요해 우선조달계약 방법으로는 목적 달성이 불가능한 경우. "
    "② 예외에 해당해 우선조달계약 외의 방법으로 계약하려면 그 사유를 입찰공고문에 기재하거나 "
    "국가종합전자조달시스템에 입력하여야 한다.")


def _article_text(body: str, head: str) -> str:
    """법령 원문에서 조문 하나를 잘라 온다(다음 조문 머리글까지)."""
    i = body.find("\n" + head)
    if i < 0:
        return ""
    rest = body[i + 1:]
    m = re.search(r"\n제\d+조(?:의\d+)?\(", rest)
    return rest[: m.start()] if m else rest


def load_sme_law(data_dir: str = DATA_DIR, limit: int = 2600) -> str:
    """배포 법령패키지에서 판로지원법 시행령 제2조의2·제2조의3을 읽는다. 실패하면 요지 상수로 대체한다."""
    try:
        path = os.path.join(data_dir, "법령패키지", "법령", SME_LAW_FILE)
        body = io.open(path, "r", encoding="utf-8").read()
        parts = []
        for head in ("제2조의2(", "제2조의3("):
            t = _article_text(body, head)
            t = re.sub(r"<개정[^>]*>|<신설[^>]*>|\]\]>|\[본조신설[^\]]*\]", " ", t)
            t = re.sub(r"[ \t]+", " ", t)
            t = "\n".join(ln.strip() for ln in t.split("\n") if ln.strip())
            if t:
                parts.append(t[: limit // 2])
        if parts:
            return "\n".join(parts)
    except Exception as e:
        log(f"  ! 법령 발췌 실패 → 요지 상수 사용: {type(e).__name__}: {e}")
    return SME_LAW_FALLBACK


SME_SYSTEM_TMPL = """공공 입찰공고의 '입찰참가자격'에서 아래 세 가지 사실만 뽑는다. 위반 여부는 판단하지 않는다.
반드시 원문 문장을 한 글자도 바꾸지 않고 먼저 인용하고, 그 인용만으로 판단한다.
해당 문장이 원문에 없으면 인용을 빈 문자열로 두고 "없음"/false로 답한다. 원문에 없는 문장을 만들지 않는다.

[근거 법령 — 배포 법령패키지]
{law}

[기업규모_제한 — 참가할 수 있는 업체의 규모를 좁히는 기재만 제한이다]
- "소기업·소상공인" = 소기업 또는 소상공인만 참가 가능. "중소기업" = 중소기업(중기업 포함)까지 참가 가능. 좁히는 기재가 없으면 "없음".
- 법령 이름·기관 이름·확인서 이름 속 '중소기업'은 제한이 아니다(「중소기업제품 구매촉진 및 판로지원에 관한 법률」, 중소기업유통센터 등).
- 본문이 '중소기업 또는 소상공인'이어도 요구하는 확인서가 소기업·소상공인 확인서뿐이면 "소기업·소상공인"이다.
- '중소기업자 우선조달 대상 사업'이라는 안내 문구만 있는 것은 제한이 아니다.
- 가점·평가 배점·하도급·협동조합·부정당업자·신용평가 문장은 참가자격이 아니다.
- '유찰되어 중소기업자간으로 확대한다'는 재공고 문장은 수준 판단에 쓰지 않는다.
- 나라장터 입력값(조항호내용)이 아니라 공고문·첨부 본문에서 찾는다.

[직접생산확인_요구]
- 입찰참가자격으로 직접생산확인증명서 소지·보유를 요구하면 true.
- 제출서류 목록에 '해당 시'·'해당하는 경우'로만 적힌 것은 false.
- '직접생산확인증명서를 별도로 요구하지 않습니다'는 false.

[우선조달_예외_기재]
- 시행령 제2조의3 각 호의 예외 사유를 공고문에 적었으면 true(같은 조 제2항이 기재 의무를 정한다).
- 다만 '제2조의3 제1항 제2호에 따라 비영리법인도 참가 가능'은 기업규모 제한을 그대로 둔 채 비영리법인만 더 받는 것이므로 false.
- '중소기업에 대한 참가자격은 제한하지 않습니다'처럼 제한 자체를 푸는 기재는 true."""

# 전용 호출용 그물. 본 호출 그물과 달리 상한 안에서 문서 전체를 훑고, 자격·기업규모·직생·확인서 어휘만 남긴다.
# 제한의 법률 용어는 정해져 있어(중소기업/소기업/소상공인/중기업) 이 그물이 놓치는 제한 문장은 사실상 없다.
SME_NET_RE = re.compile(
    r"참가\s*자격|자격\s*요건|입찰\s*참가|참여\s*가능|참가\s*제한|응찰\s*자격"
    r"|중소기업|소기업|소상공인|중기업|비영리|우선\s*조달|판로지원"
    r"|직접\s*생산|직생|제조\s*확인"
    r"|확인서|증명서|제출\s*서류|구비\s*서류"
    r"|제\s*2\s*조의\s*[23]|제\s*7\s*조")
SME_NET_CHARS = 5200


def sme_context(rec: Dict[str, Any], budget: int = SME_NET_CHARS) -> str:
    picked, seen = [], set()
    for d in rec["docs"]:
        for line in d["text"].split("\n"):
            line = line.strip()
            if len(line) < 6 or line in seen:
                continue
            m = SME_NET_RE.search(line)
            if not m:
                continue
            seen.add(line)
            picked.append(f"({d['type']}) {_clip_line(line, m)}")
    return "\n".join(_fit_pieces(picked, budget)) or "(해당 문장 없음)"


def sme_schema() -> Dict[str, Any]:
    # 필드 순서 = 디코딩 순서. 인용을 먼저 쓰게 해서 판단을 인용에 묶는다.
    return {"type": "object", "additionalProperties": False,
            "required": ["자격_원문_인용", "기업규모_제한", "직생_원문_인용", "직접생산확인_요구",
                         "예외_원문_인용", "우선조달_예외_기재"],
            "properties": {
                "자격_원문_인용": {"type": "string", "maxLength": 300},
                "기업규모_제한": {"type": "string", "enum": ["없음", "중소기업", "소기업·소상공인"]},
                "직생_원문_인용": {"type": "string", "maxLength": 300},
                "직접생산확인_요구": {"type": "boolean"},
                "예외_원문_인용": {"type": "string", "maxLength": 300},
                "우선조달_예외_기재": {"type": "boolean"},
            }}


def build_sme_messages(rec: Dict[str, Any], law: str) -> List[Dict[str, str]]:
    m = rec.get("meta", {})
    user = (f"[공고명] {title_of(rec)[:120]}\n"
            f"[업무구분] {m.get('업무구분')} · [계약방법] {m.get('계약방법')} · [추정가격] {m.get('입찰추정가격')}\n\n"
            f"[참가자격·기업규모·직접생산 관련 원문]\n{sme_context(rec)}\n")
    return [{"role": "system", "content": SME_SYSTEM_TMPL.format(law=law)},
            {"role": "user", "content": user}]


def _verified_lines(quote: Any, src: str) -> List[str]:
    """인용을 줄 단위로 원문 대조한다. 모델이 떨어져 있는 줄 여러 개를 붙여 인용하면
    통째로는 부분문자열이 아니어서 `clean_evidence`가 전부 버린다(실측: dev 1번 공고)."""
    out: List[str] = []
    for ln in str(quote or "").replace("\r", "").split("\n"):
        ok = clean_evidence(ln.strip(), src) or _ground_quote(unicodedata.normalize("NFC", ln.strip())[:EVIDENCE_MAX], src)
        if ok and len(ok) >= 6 and ok[0] not in "=+@":
            out.append(ok)
    return out


# 전용 호출의 인용 줄에 적용하는 게이트. `rx_sme_level`이 이미 쓰고 있는 제외 규칙과 같다.
# dev 실측(config B): 게이트 없이 반영했더니 v18 정탐 3건을 잃었고 원인은 전부 제출서류 목록 줄이었다
#  — "거. 소기업 또는 소상공인확인서 1부", "12) 중·소기업, 소상공인확인서 중 1부", "· 소기업·소상공인 확인서 1부".
# 서류 목록에 확인서가 있는 것과 참가자격이 그 규모로 제한된 것은 다르다.
SME_LINE_EXCLUDE_RE = re.compile(r"\d+\s*부\b|사본|가점|평가|신용|하도급|제8조의2|부정당|협동조합|경쟁제품|유찰")
# 09-24: 기업규모 조각. ① 확인서 미발급 안내('…확인서를 발급받지 못한 업체에 한함', '…발급되지 않은 경우')는 자격 문장이 아니다.
# ② 입찰방법 머리말('입 찰 방 법: 제한경쟁(소기업·소상공인)')은 참가자격에 기업규모 문장이 따로 없을 때 제한의 근거가 아니다
#    (dev DEV-039: 머리말·서류 목록·미발급 안내만 남은 공고가 v18=1). 다른 자격 줄이 있으면 머리말도 그대로 쓴다
#    (여러 줄로 나뉜 자격 문장을 파서가 못 읽는 공고에서 머리말이 안전망이다 — 무라벨 20,000 판독).
SME_UNISSUED_RE = re.compile(r"발급\s*받지\s*못한|발급\s*되지\s*않은\s*경우")
SME_HEADER_RE = re.compile(r"(입\s*찰|계\s*약)\s*(및\s*계\s*약\s*)?방\s*법\s*[:：]")
SME_NONQUAL_RE = re.compile(r"\d+\s*부\b|사본|가점|평가|신용|하도급|제8조의2|부정당|유찰|신청을?\s*증빙|상생|발급\s*받지\s*못한|발급\s*되지\s*않은\s*경우")
_SME_WORD_RE = re.compile(r"소기업|소상공인|중소기업|중기업")


def sme_header_only(rec: Dict[str, Any]) -> bool:
    """기업규모 낱말이 입찰방법 머리말·서류 목록·미발급 안내에만 있으면 True."""
    for d in rec["docs"]:
        for ln in d["text"].split("\n"):
            if _SME_WORD_RE.search(ln) and not SME_HEADER_RE.search(ln) and not SME_NONQUAL_RE.search(ln) \
                    and SME_BODY_WORD_RE.search(CERT_SMALL_RE.sub(" ", CERT_SME_RE.sub(" ", LAW_NAME_RE.sub(" ", ln)))):
                return False
    return True
# DOT 상수는 이 아래에서 정의되므로 구분점을 직접 적는다.
SME_BODY_WORD_RE = re.compile(r"중\s*[·ㆍ‧․･•/]\s*소기업|중소기업|중기업|소기업|소상공인")


def sme_line_level(line: str) -> Optional[str]:
    """인용 줄 하나를 기업규모 수준으로 인정할지 판단한다.

    확인서 이름만 있는 줄은 제한이 아니다. `classify_level`은 본문이 비어도 확인서 종류만으로 수준을
    돌려주는 갈래가 있어(dev DEV-28 '중·소기업·소상공인 확인서'), 법령·확인서 이름을 지운 본문에
    기업규모 낱말이 남을 때만 수준으로 인정한다.
    """
    if not line or SME_LINE_EXCLUDE_RE.search(line) or SME_UNISSUED_RE.search(line):
        return None
    body = CERT_SMALL_RE.sub(" ", CERT_SME_RE.sub(" ", LAW_NAME_RE.sub(" ", line)))
    if not SME_BODY_WORD_RE.search(body):
        return None
    return classify_level(line)


# 직생 요구도 `regex_facts`와 같은 기준을 쓴다: 소지·보유를 요구해야 하고, 제출서류 목록('1부')·
# 조건부('해당 시')·계약 시 제출·발급 안내는 자격 요구가 아니다.
# dev 실측: 이 게이트가 없어 v12 오탐 2건이 늘었다(DEV-106 '…등록되어 있어야 합니다', DEV-110 '계약시 반드시 제출').
DIRECT_LINE_OK_RE = re.compile(r"소지|보유")
DIRECT_LINE_EXCLUDE_RE = re.compile(r"\d+\s*부\b|해당\s*시|계약\s*시|위반|하도급|요구하지\s*않|타사제품|확인기준을"
                                    r"|공고(한|된|하는)\s*경우|계약\s*예정자|낙찰\s*예정자|입증\s*(서류|자료)")


def apply_sme_call(rec: Dict[str, Any], llm: Optional[Dict[str, Any]], rx: Dict[str, Any],
                   sme_text: str) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], bool]:
    """전용 호출 결과를 사실에 반영한다. 반영 규칙은 두 가지뿐이다.

    ① 기업규모 수준: 양쪽이 '없음'인 칸만 채운다. 이미 잡은 수준은 덮지 않는다
       (수준 재분류는 v15와 v17을 서로 뒤집어 한 변경에 두 방향 위험이 겹친다).
    ② 직접생산확인 요구: 인용이 실재하면 OR.
    두 규칙 모두 **인용한 줄이 원문에 실재할 때만** 적용하고, 수준은 기존 `classify_level`이 그 줄을 같은
    수준으로 인정할 때만 쓴다(모델의 열거값 단독으로는 반영하지 않는다).
    `우선조달_예외_기재`는 수집만 하고 판정에 쓰지 않는다 — 09-18에 LLM이 '비영리법인 참가 가능' 상투문을
    예외로 읽어 dev v15 정탐 3건을 잃은 이력이 있어 정규식 판단을 유지한다(다음 후보에서 따로 측정한다).
    """
    sme = parse_facts(sme_text)
    if not sme:
        return llm, rx, False
    src = full_text(rec)
    said = sme.get("기업규모_제한")
    if said in ("중소기업", "소기업·소상공인"):
        header_only = sme_header_only(rec)
        lines = [ln for ln in _verified_lines(sme.get("자격_원문_인용"), src) if "조항호내용" not in ln
                 and not (header_only and SME_HEADER_RE.search(ln))]
        found: Dict[str, str] = {}
        for ln in lines:
            lv = sme_line_level(ln)
            if lv:
                found.setdefault(lv, ln)
        # 모델이 말한 수준이 인용 줄로 뒷받침되면 그대로, 아니면 인용 줄이 말하는 수준을 쓴다
        # (같은 인용에 두 수준이 섞이면 소기업·소상공인 우선 — `rx_sme_level`과 같은 규칙).
        level, ev = None, ""
        if said in found:
            level, ev = said, found[said]
        elif "소기업·소상공인" in found:
            level, ev = "소기업·소상공인", found["소기업·소상공인"]
        elif "중소기업" in found:
            level, ev = "중소기업", found["중소기업"]
        if level:
            if rx.get("기업규모_제한") in (None, "없음"):
                rx["기업규모_제한"] = level
                rx["기업규모_근거"] = ev
            if llm is not None and llm.get("기업규모_제한") in (None, "없음"):
                llm["기업규모_제한"] = level
                llm["기업규모_근거"] = ev
    if sme.get("직접생산확인_요구"):
        for ln in _verified_lines(sme.get("직생_원문_인용"), src):
            if (re.search(r"직접\s*생산|직생", ln) and DIRECT_LINE_OK_RE.search(ln)
                    and not DIRECT_LINE_EXCLUDE_RE.search(ln)):
                rx["직접생산확인_요구"] = True
                rx["직접생산_언급_넓게"] = True
                if llm is not None:
                    llm["직접생산확인_요구"] = True
                break
    return llm, rx, True


def needs_sme_call(rec: Dict[str, Any]) -> bool:
    return True                                  # 9개 항목의 공통 입력이라 전 공고에 돌린다


# ----- 4-5. 실적 제한 전용 호출 (v2·v3·v4·v8) -----
# 2026-09-21 측정: 정규식 그물로 후보를 만들 수 있는 영역은 거의 소진됐다(손라벨 58건으로 v1·v9·v19·
# 지역제한을 닫고, 판정기 게이트 15개 중 13개를 닫았다). 남은 누락은 정의상 **우리 그물의 어휘로는
# 후보조차 만들 수 없는 문장**이고, 그걸 찾는 방법은 모델이 원문을 넓게 읽는 것뿐이다.
# S1(본 호출에 텍스트를 더 붓기)이 실패한 이유는 커버리지가 아니라 전달 방식이었다 — 29필드 omnibus는
# 제출서류 줄에 오염된다. S2(전용 호출 + 법 조문 + 인용 강제 + 원문 대조)는 작동했다.
# → 같은 패턴을 실적·지역에 적용한다. **규칙을 대체하지 않고 OR로 더한다**(F1/2 정리의 따름정리:
#   새로 잡는 것의 정밀도가 F1/2를 넘으면 합집합이 항상 낫다).
PERF_LAW_FALLBACK = (
    "국가계약법 시행규칙 제25조 ②1호: 공사·제조 또는 용역 등의 실적으로 참가자격을 제한하는 경우 "
    "가목(실적의 규모·양) 및 나목(실적 금액)은 **제조 또는 용역의 경우 추정가격이 고시금액 이상인 계약에 한정**하며, "
    "그 기준은 해당 계약목적물의 규모·양 또는 추정가격의 1배 이내로 한다.\n"
    "지방계약법 시행규칙 제25조 ②1호: 실적의 규모·양은 해당 계약목적물의 3분의 1 이내(상향 필요 시 1배 범위), "
    "실적금액은 추정가격의 1배 이내.")
REGION_LAW_FALLBACK = (
    "국가계약법 시행규칙 제25조 ③: 법인등기부상 **본점소재지**를 기준으로 참가자격을 제한하는 경우 "
    "본점소재지가 해당 공사 등의 현장·납품지가 소재하는 **특별시·광역시·특별자치시·도 또는 특별자치도(시·도)의 "
    "관할구역** 안에 있는 자로 제한해야 한다.\n"
    "지방계약법 시행규칙 제25조 ③: 본점이 해당 현장·납품지가 있는 시·도의 관할구역 안에 있는 자로 제한하여야 하며, "
    "일정한 경우에만 인접 시·도까지 확대할 수 있다.")


def _law_article(data_dir: str, filename: str, head: str, limit: int) -> str:
    try:
        body = io.open(os.path.join(data_dir, "법령패키지", "법령", filename), "r", encoding="utf-8").read()
        t = _article_text(body, head)
        t = re.sub(r"<개정[^>]*>|<신설[^>]*>|\]\]>", " ", t)
        t = re.sub(r"[ \t]+", " ", t)
        return "\n".join(ln.strip() for ln in t.split("\n") if ln.strip())[:limit]
    except Exception:
        return ""


def load_perf_law(data_dir: str = DATA_DIR) -> str:
    a = _law_article(data_dir, "국가를 당사자로 하는 계약에 관한 법률 시행규칙.txt", "제25조(", 1300)
    b = _law_article(data_dir, "지방자치단체를 당사자로 하는 계약에 관한 법률 시행규칙.txt", "제25조(", 1100)
    return ("\n".join(x for x in (a, b) if x)) or PERF_LAW_FALLBACK


def load_region_law(data_dir: str = DATA_DIR) -> str:
    # 지역 기준은 같은 제25조 ③항에 있어 실적 조문과 본문을 공유한다. 별도로 자르지 않고 같은 발췌를 쓴다.
    return load_perf_law(data_dir) or REGION_LAW_FALLBACK


PERF_SYSTEM_TMPL = """공공 입찰공고의 '입찰참가자격'에서 **실적 요구**에 관한 사실만 뽑는다. 위반 여부는 판단하지 않는다.
반드시 원문 문장을 한 글자도 바꾸지 않고 먼저 인용하고, 그 인용만으로 판단한다.
해당 문장이 원문에 없으면 인용을 빈 문자열로 두고 false/null로 답한다. 원문에 없는 문장을 만들지 않는다.

[근거 법령 — 배포 법령패키지]
{law}

[실적제한 = true 로 볼 것]
- 입찰참가자격으로 일정한 규모·양·금액·기간·건수의 수행·납품·제조 실적을 요구하는 문장.
- **금액이 적혀 있지 않아도** `최근 3년 이내 … 실적이 3건 이상 보유 업체`, `최근 5년 내 100톤 이상 납품 실적을 가진 자`,
  `다년간의 관련 사업 수행 경험이 있는 업체`처럼 기간·건수·규모로 구체화되어 있으면 true.

[실적제한 = false 로 볼 것]
- 제안서 **평가 배점**·정성평가·발표 안내에 나오는 실적(`이행실적 평가기준`, `제안사의 유사용역 수행 실적을 제시`).
- **제출서류 목록**의 실적증명서(`실적증명서 1부[서식 3]`, `용역 이행 실적증명서`).
- 법정 일반자격 상투문 `당해 용역을 수행할 수 있는 신용과 실적이 있는 자`(지방계약법 시행령 제13조) — 제한이 아니다.
- 사고 전력·부정당업자 배제(`인사사고가 있는 업체는 입찰서를 제출할 수 없으며`).
- 계약 이행 후의 실적 보고·정산 관련 문장.

[실적_요구금액_원] 참가자격이 요구하는 실적의 최소 금액(원 단위 정수). 적혀 있지 않으면 null. 예산·추정가격을 옮기지 않는다.
[실적_공공한정] 인정하는 실적의 발주처를 국가·지방자치단체·공공기관·교육기관 등으로 한정하면 true. 민간 실적도 인정하면 false."""

REGION_SYSTEM_TMPL = """공공 입찰공고의 '입찰참가자격'에서 **소재지(지역) 제한**에 관한 사실만 뽑는다. 위반 여부는 판단하지 않는다.
반드시 원문 문장을 한 글자도 바꾸지 않고 먼저 인용하고, 그 인용만으로 판단한다.
해당 문장이 원문에 없으면 인용을 빈 문자열로 두고 false/"없음"으로 답한다. 원문에 없는 문장을 만들지 않는다.

[근거 법령 — 배포 법령패키지]
{law}

[지역제한 = true 로 볼 것]
- 입찰에 참가할 수 있는 자를 **법인등기부상 본점·주된 영업소·사업장의 소재지**로 좁히는 문장.
  (`본점 소재지가 …에 있는 업체`, `관내에 주된 영업소를 둔 자`, `○○시에 소재한 업체만 참가 가능`)

[지역제한 = false 로 볼 것]
- **납품 장소·현장 위치·수요기관 주소** 안내.
- **관할 법원·중재지** 조항(`발주처 소재지 관할 법원의 판결`).
- 지역업체 **가산점**·우대 조항(제한이 아니다).
- `보험사(본사에 한함)`처럼 **지점 입찰을 막는** 문장 — 지역이 아니라 조직 형태의 제한이다.
- `본점 사업장의 소재지는 무관하며`처럼 제한이 **없다**고 밝힌 문장.
- 제출서류 목록의 `사업자등록증 사본(본점소재지)`.
- 지역제한경쟁입찰의 **기준일** 설명 상투문(`본점소재지 기준일은 입찰공고일 전일로 하며`).

[지역_단위] 제한 범위가 특별시·광역시·특별자치시·도·특별자치도 단위면 "시도", 시·군·구 단위면 "시군구", 제한이 없으면 "없음".
[지역_시도목록] 참가를 허용한 시·도 이름만 적는다(`서울특별시`, `경기도` 등). 시·군·구 이름은 넣지 않는다."""

PERF_NET_RE = re.compile(
    r"실적|수행\s*경험|납품\s*경험|시공\s*경험|경력"
    r"|참가\s*자격|자격\s*요건|입찰\s*참가|참여\s*가능|응찰")
REGION_NET_RE = re.compile(
    r"본점|본사|주된\s*영업소|사업장|소재지|소재한|소재하|관내|역내|지역\s*제한|지역\s*업체|관할\s*구역"
    r"|참가\s*자격|자격\s*요건|입찰\s*참가|참여\s*가능")
PERF_NET_CHARS = 4500
REGION_NET_CHARS = 3500


def _net_context(rec: Dict[str, Any], rx: "re.Pattern", budget: int) -> str:
    """문서 전체를 훑어 어휘에 걸린 줄을 모으고, 상한을 넘으면 앞뒤를 번갈아 남긴다."""
    picked, seen = [], set()
    for d in rec["docs"]:
        for line in d["text"].split("\n"):
            line = line.strip()
            if len(line) < 6 or line in seen:
                continue
            m = rx.search(line)
            if not m:
                continue
            seen.add(line)
            picked.append(f"({d['type']}) {_clip_line(line, m)}")
    return "\n".join(_fit_pieces(picked, budget)) or "(해당 문장 없음)"


def perf_schema() -> Dict[str, Any]:
    return {"type": "object", "additionalProperties": False,
            "required": ["실적_원문_인용", "실적제한", "실적_요구금액_원", "실적_공공한정"],
            "properties": {"실적_원문_인용": {"type": "string", "maxLength": 300},
                           "실적제한": {"type": "boolean"},
                           "실적_요구금액_원": {"type": ["integer", "null"]},
                           "실적_공공한정": {"type": "boolean"}}}


def region_schema() -> Dict[str, Any]:
    return {"type": "object", "additionalProperties": False,
            "required": ["지역_원문_인용", "지역제한", "지역_단위", "지역_시도목록"],
            "properties": {"지역_원문_인용": {"type": "string", "maxLength": 300},
                           "지역제한": {"type": "boolean"},
                           "지역_단위": {"type": "string", "enum": ["없음", "시도", "시군구"]},
                           "지역_시도목록": {"type": "array", "items": {"type": "string"}}}}


def _call_header(rec: Dict[str, Any]) -> str:
    m = rec.get("meta", {})
    return (f"[공고명] {title_of(rec)[:120]}\n"
            f"[적용계약법] {m.get('적용계약법')} · [업무구분] {m.get('업무구분')} · "
            f"[계약방법] {m.get('계약방법')} · [추정가격] {m.get('입찰추정가격')}\n\n")


def build_perf_messages(rec: Dict[str, Any], law: str) -> List[Dict[str, str]]:
    user = _call_header(rec) + f"[실적·참가자격 관련 원문]\n{_net_context(rec, PERF_NET_RE, PERF_NET_CHARS)}\n"
    return [{"role": "system", "content": PERF_SYSTEM_TMPL.format(law=law)}, {"role": "user", "content": user}]


def build_region_messages(rec: Dict[str, Any], law: str) -> List[Dict[str, str]]:
    user = (_call_header(rec) + f"[나라장터 제한지역 입력] {rec.get('meta', {}).get('제한지역코드목록')}\n\n"
            f"[소재지·참가자격 관련 원문]\n{_net_context(rec, REGION_NET_RE, REGION_NET_CHARS)}\n")
    return [{"role": "system", "content": REGION_SYSTEM_TMPL.format(law=law)}, {"role": "user", "content": user}]


def needs_perf_call(rec: Dict[str, Any]) -> bool:
    """**측정으로 기각(2026-09-21).** dev 200건에서 정탐 0건·오탐 29건이었고, 게이트를 최대로 조여도
    오탐 6건·정탐 0건이었다(dev 0.8307 → 0.8229). 인용문이 전부 **적격심사·이행능력평가의 실적 인정
    기준**이지 참가자격이 아니었다 — `실적만 인정`, `조사이행능력평가 중 연구조사실적`,
    `누적 실적 금액 평가`, `주요 사업실적을 제시해야 한다`.
    4bit 모델은 '참가자격 실적'과 '적격심사 실적'을 구분하지 못한다(본 호출 omnibus에서도 7정탐/42오탐).
    정규식 `rx_performance`는 `EVAL_CONTEXT_RE` + 구체성 표지로 이미 이 구분을 해내고 있다.
    코드는 재현·재검토를 위해 남기고 호출만 끈다."""
    return False


def needs_region_call(rec: Dict[str, Any]) -> bool:
    return True


# 인용 줄 게이트. 2026-09-21 손라벨로 확인한 오탐 패턴을 그대로 쓴다.
PERF_CALL_EXCLUDE_RE = re.compile(
    r"신용과\s*실적|신용\s*및\s*실적|사고|\d+\s*부\b|서식|제출\s*서류|구비\s*서류"
    r"|제안서에|제안사의|발표자|정성|평가\s*기준|배점|가점")
REGION_CALL_EXCLUDE_RE = re.compile(
    r"관할\s*법원|중재|납품\s*장소|가산점|우대|본사에\s*한함|본점에\s*한함|소재지는\s*무관"
    r"|\d+\s*부\b|사업자등록증\s*사본|기준일|공동혁신도시")


def apply_perf_call(rec: Dict[str, Any], llm: Optional[Dict[str, Any]], rx: Dict[str, Any],
                    text: str) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], bool]:
    """실적 전용 호출을 OR로 더한다. 인용 줄이 원문에 실재하고 게이트를 통과할 때만 반영한다."""
    if not needs_perf_call(rec):            # 기각된 호출
        return llm, rx, False
    o = parse_facts(text)
    if not o:
        return llm, rx, False
    src = full_text(rec)
    lines = [ln for ln in _verified_lines(o.get("실적_원문_인용"), src)
             if not PERF_CALL_EXCLUDE_RE.search(ln) and not EVAL_CONTEXT_RE.search(ln)
             and not re.search(r"적격|이행능력|낙찰자|동등이상|누적|제시|증명서", ln)
             and re.search(r"실적|경험|경력", ln)
             # 자격 문장임을 드러내는 어미가 있어야 한다(정규식 rx_performance와 같은 요구)
             and re.search(r"업체|자이어야|자\)|있어야|참가\s*자격|한함|있는 자|보유한 자|한\s*자\b|단체|이어야", ln)]
    if o.get("실적제한") and lines:
        for tgt in (rx, llm):
            if tgt is None:
                continue
            if not tgt.get("실적제한"):
                tgt["실적제한"] = True
                tgt["실적_근거"] = lines[0]
        amt = o.get("실적_요구금액_원")
        # 금액은 정규식이 못 찾았을 때만 채운다(v3은 요구금액 ≥ 예산일 때 발동하므로 덮어쓰면 위험하다).
        if isinstance(amt, int) and amt > 0 and any(f"{amt:,}" in ln or str(amt) in ln for ln in lines):
            for tgt in (rx, llm):
                if tgt is not None and tgt.get("실적_요구금액_원") in (None, 0):
                    tgt["실적_요구금액_원"] = amt
        if o.get("실적_공공한정") and any(PUBLIC_ISSUER_RE.search(ln) for ln in lines):
            for tgt in (rx, llm):
                if tgt is not None:
                    tgt["실적_발주처_공공한정"] = True
    return llm, rx, True


def apply_region_call(rec: Dict[str, Any], llm: Optional[Dict[str, Any]], rx: Dict[str, Any],
                      text: str) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], bool]:
    """지역 전용 호출을 OR로 더한다. 단위는 정규식이 '없음'일 때만 채운다(시군구 재분류는 v6를 뒤집는다)."""
    o = parse_facts(text)
    if not o:
        return llm, rx, False
    src = full_text(rec)
    lines = [ln for ln in _verified_lines(o.get("지역_원문_인용"), src)
             if not REGION_CALL_EXCLUDE_RE.search(ln)
             and re.search(r"본점|본사|주된\s*영업소|사업장|소재|관내|역내"
                           r"|지역\s*(업체|업자|소재)|\[지역:|관할\s*구역", ln)]
    if not (o.get("지역제한") and lines):
        return llm, rx, True
    unit = o.get("지역_단위") if o.get("지역_단위") in ("시도", "시군구") else None
    # 시·군·구 제한은 한 시·도 안에서 이뤄진다 → 시도가 둘 이상이면 단위는 시도다.
    # (무라벨 라벨 검토: PPS-D-002861 `영업소가 대구 및 경북 지역 소재`를 모델이 시군구로 답해 v6 오탐이 났다)
    if unit == "시군구" and len({PROVINCE_ALIAS.get(x, x) for x in (o.get("지역_시도목록") or [])
                                if isinstance(x, str) and x in PROVINCES}) >= 2:
        unit = "시도"
    provs = {PROVINCE_ALIAS.get(x, x) for x in (o.get("지역_시도목록") or [])
             if isinstance(x, str) and x in PROVINCES}
    for tgt in (rx, llm):
        if tgt is None:
            continue
        if not tgt.get("지역제한"):
            tgt["지역제한"] = True
            tgt["지역_근거"] = lines[0]
        if unit and tgt.get("지역_단위") in (None, "없음"):
            tgt["지역_단위"] = unit
        if provs:
            tgt["지역_시도목록"] = sorted(set(tgt.get("지역_시도목록") or []) | provs)
    return llm, rx, True


# ----- 4-6. 물품 품목 전용 호출 (v10~v18의 공통 입력) -----
# 2026-09-21 측정: 후보 생성기(`candidate_items`)의 세부품명 recall이 **33.3%**였다. 메타에 경쟁제품
# 코드가 적힌 81건을 정답으로 쓰고 bigram 부분만 따로 재니, top-8이든 top-615든 33.3%로 같았다
# — 병목은 후보 수가 아니라 ① `s >= 0.3` 문턱과 ② **질의어가 공고명뿐**이라는 점이었다
# (공고명의 10.7%는 익명화로 내용어가 없다). 질의어에 과업·품명 줄을 넣고 문턱을 0.20으로 낮추면
# recall이 **74.1%**로 두 배가 된다.
# 그리고 공고의 75.6%는 원문·메타에 코드가 없어 후보가 전적으로 이 매처에 달려 있고, 용역과 달리
# **물품에는 품목 전용 호출이 없어** 본 호출이 이 후보 목록만 보고 결정한다.
GOODS_QUERY_RE = re.compile(r"용\s*역\s*명|사\s*업\s*명|건\s*명|공\s*고\s*명|과업|사업\s*내용|사업\s*개요|사업\s*목적"
                            r"|주요\s*내용|범\s*위|품\s*명|세부품명|구매\s*내역|물품\s*내역|규격|납품|구입")
GOODS_QUERY_CHARS = 2500
# 문턱을 낮추는 것은 이득이 없다: 질의어를 넓힌 뒤 0.30 → 0.20은 recall 70.4% → 74.1%(+3.7pp)인데
# 후보에 무관한 품목이 섞인다(학술지 구매 공고에 '약품장'·'군용정복'). 문턱은 그대로 두고 질의어만 넓힌다.
GOODS_CAND_THR = 0.30
GOODS_CAND_K = 20


def goods_query(rec: Dict[str, Any]) -> str:
    """세부품명 매칭 질의어: 공고명 + 과업·품명·구매내역 줄."""
    out, used = [title_of(rec)[:200]], 0
    for d in rec["docs"]:
        for ln in d["text"].split("\n"):
            ln = ln.strip()
            if len(ln) < 4 or not GOODS_QUERY_RE.search(ln):
                continue
            out.append(ln[:200])
            used += len(ln)
            if used > GOODS_QUERY_CHARS:
                return " ".join(out)
    return " ".join(out)


def goods_candidates(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> List[str]:
    codes = [c for c in codes_in_record(rec)[:10] if c in table]
    tb = _bigrams(goods_query(rec))
    scored = []
    for c, it in table.items():
        nb = _bigrams(it["name"])
        if nb and tb:
            sc = len(nb & tb) / len(nb)
            if sc >= GOODS_CAND_THR:
                scored.append((sc, c))
    for _, c in sorted(scored, reverse=True)[:GOODS_CAND_K]:
        if c not in codes:
            codes.append(c)
    return codes


GOODS_ITEM_SYSTEM = """물품 구매 공고의 **계약 목적물**이 아래 [중기간 경쟁제품 후보] 중 어느 세부품명에 해당하는지 고른다.
- 이번 계약으로 실제 **구매하는 물품**에 직접 해당할 때만 고른다. 이름이 비슷하거나 부속·소모품만 겹치면 "해당없음".
- 여러 품목을 함께 사는 공고라면 그중 경쟁제품에 해당하는 것이 하나라도 있으면 그것을 고른다.
- 후보의 (특이사항)에 규격·용도·중량 조건이 붙어 있으면 공고의 물품이 그 조건을 만족할 때만 고른다.
- 먼저 계약목적물_요약에 무엇을 사는 계약인지 한 구절로 적고, 그다음 세부품명번호를 고른다.

근거: 중소기업제품 구매촉진 및 판로지원에 관한 법률 제6조·제7조 — 중소벤처기업부장관이 지정·공고한 제품이
중소기업자간 경쟁제품이며, 그 제품을 조달하는 경우 중소기업자간 경쟁입찰에 따라야 한다."""


def goods_item_schema(codes: List[str]) -> Dict[str, Any]:
    return {"type": "object", "additionalProperties": False,
            "required": ["계약목적물_요약", "세부품명번호"],
            "properties": {"계약목적물_요약": {"type": "string", "maxLength": 60},
                           "세부품명번호": {"type": "string", "enum": list(codes) + ["해당없음"]}}}


def build_goods_item_messages(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    cands = goods_candidates(rec, table)
    catalog = "\n".join(
        f"- {c} {table[c]['name']} [{table[c]['group']}]" + (f" ({table[c]['note']})" if table[c]["note"] else "")
        for c in cands) or "- (후보 없음)"
    user = (f"[공고명] {title_of(rec)[:120]}\n[추정가격] {meta(rec, '입찰추정가격')}\n"
            f"[나라장터 세부품명번호목록] {meta(rec, '세부품명번호목록')}\n\n"
            f"[구매 물품 관련 원문]\n{goods_query(rec)[:2200]}\n\n"
            f"[중기간 경쟁제품 후보]\n{catalog}\n")
    return [{"role": "system", "content": GOODS_ITEM_SYSTEM}, {"role": "user", "content": user}]


def needs_goods_item_call(rec: Dict[str, Any]) -> bool:
    """**측정으로 기각(2026-09-21).** 대상: 물품이면서 원문·메타에 경쟁제품 코드가 없는 공고.

    후보 생성기의 recall을 33.3% → 70.4%로 두 배 올리고(질의어를 공고명 → 공고명+과업·품명으로 확장)
    '해당없음'일 때만 채우도록 좁혔는데도 dev에서 **정탐 0 증가 · 오탐 +10**이었다
    (v10 오탐 3→9, v11 1→3, v13 3→5, v18 정탐 6→5; macro 0.8375 → 0.8198).
    09-19의 품목 융합 변형 3종이 같은 방식으로 기각된 것과 같은 실패다 — 후보가 문제가 아니라
    **'이 계약의 목적물이 무엇인가'라는 맥락 판단**을 4bit 모델이 못 한다.
    후보 생성기 개선 자체(`goods_query`·`goods_candidates`)는 유효한 측정이므로 코드를 남긴다.
    """
    return False


def _record_table_codes(rec: Dict[str, Any]) -> List[str]:
    return [c for c in codes_in_record(rec) if c in _TABLE_CACHE]


_TABLE_CACHE: Dict[str, Dict[str, Any]] = {}


def apply_goods_item_call(rec: Dict[str, Any], llm: Optional[Dict[str, Any]], rx: Dict[str, Any],
                          table: Dict[str, Dict[str, Any]], text: str) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any], bool]:
    """전용 호출이 고른 코드는 **양쪽이 '해당없음'일 때만** 채운다(이미 고른 코드는 덮지 않는다)."""
    if not needs_goods_item_call(rec):      # 기각된 호출이므로 저장된 출력이 있어도 반영하지 않는다
        return llm, rx, False
    o = parse_facts(text)
    if not o:
        return llm, rx, False
    code = str(o.get("세부품명번호") or "")
    if code not in table:
        return llm, rx, True
    # 과업 정보가 없어 못 고른 경우의 상투적 요약은 신뢰하지 않는다(용역 전용 호출과 같은 기준)
    if re.search(r"명시되지|없어|없음|불가|알 수 없|확인할 수 없", str(o.get("계약목적물_요약") or "")):
        return llm, rx, True
    for tgt in (rx, llm):
        if tgt is not None and str(tgt.get("계약목적물_세부품명번호") or "해당없음") not in table:
            tgt["계약목적물_세부품명번호"] = code
    return llm, rx, True


# ===== 4-4. 시간 예산 관리자 (S0) =====
# 실행 제한은 2시간이고 09-19 기준은 35분 39초만 썼다. 남은 시간을 쓰되 초과는 제출 오류(일일 횟수 소모)다.
# → 단계별로 남은 시간을 보고 뒤 단계를 스스로 잘라낸다. 그리고 첫 단계 전에 정규식만으로 유효한
#   submission.csv를 먼저 써 두고 단계마다 덮어쓴다(중간에 끊겨도 제출 가능한 파일이 남는다).
BUDGET_SECONDS = float(os.environ.get("PPS_BUDGET_S", 6000))    # 100분(2시간에서 20분 여유)
RESERVE_SECONDS = 180.0                                          # 판정·CSV 기록·검증용


class Budget:
    def __init__(self, total: float = BUDGET_SECONDS):
        self.t0 = time.time()
        self.total = total
        self.stages: List[Tuple[str, float]] = []

    def elapsed(self) -> float:
        return time.time() - self.t0

    def left(self) -> float:
        return self.total - self.elapsed()

    def afford(self, need: float) -> bool:
        return self.left() - need > RESERVE_SECONDS

    def stage(self, name: str, t_start: float) -> None:
        self.stages.append((name, round(time.time() - t_start, 1)))
        log(f"  [예산] {name} {time.time() - t_start:.0f}s · 경과 {self.elapsed():.0f}s / {self.total:.0f}s")


def run_stage(runner, msgs: List[List[Dict[str, str]]], chunk: int, budget: Budget,
              schema: Optional[Dict[str, Any]] = None, label: str = "",
              max_tokens: Optional[int] = None) -> List[str]:
    """청크마다 실측 속도로 남은 시간을 외삽한다. 예산을 넘길 것 같으면 남은 건은 빈 출력으로 둔다
    (빈 출력 = 그 사실은 정규식 값 사용, 판정은 계속 된다)."""
    outs: List[str] = []
    t0 = time.time()
    for s in range(0, len(msgs), chunk):
        part = msgs[s:s + chunk]
        outs.extend(run_chunk(runner, part, schema, max_tokens))
        done = len(outs)
        rate = (time.time() - t0) / max(done, 1)
        remain = rate * (len(msgs) - done)
        log(f"  {label} {done}/{len(msgs)}건 … {time.time() - t0:.0f}s (남은 예상 {remain:.0f}s)")
        if done < len(msgs) and not budget.afford(remain):
            log(f"  ! {label} 예산 부족 → 남은 {len(msgs) - done}건은 정규식 사실만 사용")
            outs.extend("" for _ in range(len(msgs) - done))
            break
    return outs


def fit_to_budget(rec: Dict[str, Any], table, runner, budget: int = PROMPT_BUDGET):
    scale = 1.0
    while True:
        msgs = build_messages(rec, table, scale)
        n = runner.count_tokens(msgs)
        if n <= budget or scale <= 0.3:
            return msgs, n, scale
        scale *= 0.75


# ===== 5. 모델 러너 =====
class VLLMRunner:
    def __init__(self, schema: Dict[str, Any], model_dir: str = MODEL_DIR, quant: Optional[str] = QUANT,
                 max_tokens: int = MAX_TOKENS, seed: int = SEED, gpu_mem: float = 0.92, tp: int = 1):
        t0 = time.time()
        import vllm
        from vllm import LLM, SamplingParams
        from vllm.sampling_params import StructuredOutputsParams

        log(f"vllm {vllm.__version__} · 모델 {model_dir} · quant={quant} · max_model_len={MAX_MODEL_LEN}")
        kw = dict(model=model_dir, tokenizer=model_dir, max_model_len=MAX_MODEL_LEN,
                  gpu_memory_utilization=gpu_mem, seed=seed, tensor_parallel_size=tp, dtype="auto")
        if quant:
            kw["quantization"] = quant
        self.llm = LLM(**kw)
        self.tok = self.llm.get_tokenizer()
        self.sp = SamplingParams(
            temperature=0.0, max_tokens=max_tokens, seed=seed,
            structured_outputs=StructuredOutputsParams(json=schema, disable_any_whitespace=True),
        )
        self.load_seconds = time.time() - t0

    def count_tokens(self, messages: List[Dict[str, str]]) -> int:
        try:
            ids = self.tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=True)
            if hasattr(ids, "keys") and "input_ids" in ids:
                ids = ids["input_ids"]
            return len(ids)
        except Exception:
            return len(self.tok.encode("\n".join(m["content"] for m in messages)))

    def chat(self, batch: List[List[Dict[str, str]]], schema: Optional[Dict[str, Any]] = None,
             max_tokens: Optional[int] = None) -> List[str]:
        sp = self.sp
        if schema is not None:
            from vllm import SamplingParams
            from vllm.sampling_params import StructuredOutputsParams
            # 09-21 측정: 스키마 호출에 128을 고정하고 있었는데 실제 출력은 기업규모 중앙값 175(200건 중
            # 159건이 128 초과), 지역 중앙값 40(46건 초과)이다. structured outputs는 상한에서 잘리면
            # 닫히지 않은 JSON이 나와 `parse_facts`가 버리므로, 그 호출은 조용히 무효가 된다.
            # → 호출마다 실측에 맞는 예산을 준다(상한을 올려도 실제 생성 길이만큼만 비용이 든다).
            sp = SamplingParams(temperature=0.0, max_tokens=max_tokens or 128, seed=SEED,
                                structured_outputs=StructuredOutputsParams(json=schema, disable_any_whitespace=True))
        outs = self.llm.chat(batch, sampling_params=sp, use_tqdm=False)
        return [o.outputs[0].text if o.outputs else "" for o in outs]


class MockRunner:
    """모델 없이 흐름을 확인한다. 빈 출력 → 판정기는 정규식 사실만 사용한다."""
    load_seconds = 0.0

    def __init__(self, schema: Dict[str, Any], **_):
        pass

    def count_tokens(self, messages: List[Dict[str, str]]) -> int:
        return sum(len(m["content"]) for m in messages) // 2

    def chat(self, batch: List[List[Dict[str, str]]], schema: Optional[Dict[str, Any]] = None,
             max_tokens: Optional[int] = None) -> List[str]:
        return ["" for _ in batch]


def run_chunk(runner, batch: List[List[Dict[str, str]]], schema: Optional[Dict[str, Any]] = None,
              max_tokens: Optional[int] = None) -> List[str]:
    try:
        return runner.chat(batch, schema, max_tokens)
    except Exception as e:
        log(f"  ! 청크({len(batch)}건) 실패 → 건 단위 재시도: {type(e).__name__}: {str(e)[:160]}")
    outs = []
    for m in batch:
        try:
            outs.append(runner.chat([m], schema, max_tokens)[0])
        except Exception as e:
            log(f"  ! 건 단위 실패 → 빈 출력: {type(e).__name__}: {str(e)[:160]}")
            outs.append("")
    return outs


def parse_facts(text: str) -> Optional[Dict[str, Any]]:
    text = (text or "").strip()
    if not text:
        return None
    for cand in (text, text[text.find("{"): text.rfind("}") + 1]):
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict):
                return obj
        except (json.JSONDecodeError, ValueError):
            pass
    return None


# ===== 6. 정규식 사실 추출 =====
AMOUNT_RE = re.compile(r"(\d[\d,\.]*)\s*(억|천만|백만|만)?\s*(\d[\d,]*)?\s*(천만|백만|만)?\s*원")
EVAL_CONTEXT_RE = re.compile(r"기재|배점|\d+\s*점|건수|합산|평가|인정|실적만|대상으로|제출\s*-|\|\s*\d")
PUBLIC_ISSUER_RE = re.compile(r"국가|정부|공공기관|지방자치단체|지자체|공기업|대학병원|\[수요기관|기관(이|에서)?\s*발주"
                              r"|광역\s*자치\s*단체|기초\s*자치\s*단체|중앙\s*행정\s*기관|관공서|준정부\s*기관")
# 09-24: 공공 발주처로 한정한 실적 요구는 금액·기간이 없어도 구체적이다(집행기준 제5조④3). 단 '실적이 있는·보유한' 요구여야 한다
# ('실적 조회 후 결정', '대가지급, 실적', '누계공정 실적', '실적내역 증빙' 같은 줄은 요구가 아니다 — 무라벨 판독).
PERF_REQUIRE_RE = re.compile(r"(실적|경험)\s*(이|을)?\s*(있는|있어야|보유|갖춘|가진)")
DATE_FULL_RE = re.compile(r"(20\d{2})\s*[\.\-/년]\s*(\d{1,2})\s*[\.\-/월]\s*(\d{1,2})")
DATE_SHORT_RE = re.compile(r"(?<![\d\.])(\d{1,2})\s*[\.월]\s*(\d{1,2})\s*[\.일]?\s*\(")


PERF_REL_RE = re.compile(
    r"(?:기초\s*금액|추정\s*가격|사업\s*예산(?:\s*금?\s*액)?|총?\s*사업비|사업\s*금액|예산\s*액|배정\s*예산(?:\s*금?\s*액)?"
    r"|(?:입찰\s*)?공고\s*금액|발주\s*금액|용역\s*금액|설계\s*금액"
    r"|(?:본|당해|해당|이번)\s*(?:사업|용역|과업|건|물품|입찰)의?\s*(?:금액|규모|예산|사업비|기초\s*금액|추정\s*가격))"
    r"\s*(?:의|대비|기준)?\s*(?:(\d+(?:\.\d+)?)\s*배\s*수?|(\d{2,3})\s*%)?\s*(?:이상|을\s*초과|초과)")


def relative_perf_multipliers(s: str) -> List[float]:
    out = []
    for mm in PERF_REL_RE.finditer(s):
        if re.search(r"(아래|다음|하기|별표|별첨|표\s*\d*)\s*(의\s*)?$", s[max(0, mm.start() - 8):mm.start()]):
            continue                         # '아래 사업금액 이상'은 표에 적은 별도 금액이다
        out.append(float(mm.group(1)) if mm.group(1) else (float(mm.group(2)) / 100 if mm.group(2) else 1.0))
    return out


THOUSAND_WON_RE = re.compile(r"(?<![\d,.])(\d[\d,]*)\s*천\s*원")
WON_SIGN_RE = re.compile(r"[₩￦]\s*(\d[\d,]*\d)")


def parse_amounts_ext(s: str) -> List[float]:
    """parse_amounts + 천 원 단위('80,000천원 이상')·원화 기호('￦49,000,000') 표기(09-27 R8, v3 실적 금액용)."""
    out = parse_amounts(s)
    for m in THOUSAND_WON_RE.finditer(s):
        try:
            out.append(float(m.group(1).replace(",", "")) * 1000)
        except ValueError:
            pass
    for m in WON_SIGN_RE.finditer(s):
        try:
            out.append(float(m.group(1).replace(",", "")))
        except ValueError:
            pass
    return out


def parse_amounts(s: str) -> List[float]:
    out = []
    for m in AMOUNT_RE.finditer(s):
        try:
            v = float(m.group(1).replace(",", "")) * UNIT.get(m.group(2), 1)
            if m.group(3) and m.group(4):
                v += float(m.group(3).replace(",", "")) * UNIT[m.group(4)]
            out.append(v)
        except ValueError:
            pass
    return out


INSTITUTION_ONLY_RE = re.compile(r"(대학교?|산학\s*협력단|연구\s*기관|\[기관\((대학|대학교|연구기관|산학협력단)\)\])"
                                 r"(\s*(또는|및|,)\s*[^\n]{0,40})?\s*만\s*(입찰\s*)?(에\s*)?(참여|참가|응찰)\s*(가능|할\s*수)")


def _lines(rec: Dict[str, Any], pat: str) -> List[str]:
    rx = re.compile(pat)
    return [ln.strip() for d in rec["docs"] for ln in d["text"].split("\n") if rx.search(ln)]


# 실적 요구의 '구체성' 표지. 09-19까지는 금액(`parse_amounts`)만 인정했는데, 금액 없이 기간·건수로
# 구체화한 실적 요구가 무라벨에서 확인됐다("최근 3년 이내 … 계약실적이 있는 업체",
# "5년 이내 MRAM 소자 개발 및 납품 실적을 보유한 자", "다년간의 관련 사업 수행 경험이 있는 업체").
# 반대로 dev 라벨은 구체성 없는 문장을 실적제한으로 보지 않는다 — 특히 지방계약법 시행령 제13조의
# 상투문 "당해 용역을 수행할 수 있는 신용과 실적이 있는 자"는 법정 일반자격이라 제한이 아니다(DEV-165 v2=0).
PERF_SPECIFIC_RE = re.compile(r"최근\s*\d+\s*(년|개월)|\d+\s*(년|개월)\s*(이내|이상|간)|\d+\s*건\s*이상"
                              r"|\d+\s*회\s*이상|다년간|동일\s*(건|용역|물품)|동종")
# 사고 전력으로 참가를 막는 문장은 실적 요구가 아니다(무라벨 라벨 검토 PPS-D-010354·016385:
# "사고전력(…인사사고에 한함)이 있는 업체는 견적서 제출을 제한", "무사고 운행실적 확인서").
PERF_BOILERPLATE_RE = re.compile(r"신용과\s*실적|신용\s*및\s*실적|사고")
# 09-25 P2: 구체성 표지(금액·기간·건수·동종) 없이 '무엇의 실적'만 적은 자격 줄도 실적 요구다
# (dev DEV-048 "…경북에 소재한 실적이 우수한 업체" v8=1을 규칙이 못 읽어 놓쳤다). 실적 앞에 대상 설명이 있어야 한다 —
# 줄 첫머리의 '실적이 있는 자'는 법정 상투문 '신용과 / 실적이 있는 자'의 줄바꿈 조각일 수 있어 받지 않는다.
# 제외: 인력 경력·자격, 협력방안, 대행사(대행여행사) 요건, '…업체에게 제작' 지시, 제품 사용실적, 인력 구성,
# 인건비 적용계수, 조문 인용(무라벨 20,000 새 적중 판독에서 나온 비자격 문맥).
PERF_VAGUE_RE = re.compile(r"[가-힣A-Za-z0-9)\]][^\n]{0,60}?실적\s*(이|을)?\s*(있는|있어야|보유|갖춘|가진|우수)")
PERF_VAGUE_EXCL_RE = re.compile(r"경력|학위|자격증|기술자|책임자|기술인력|참여\s*인력|투입\s*인력|강사|전문가|에게|하도급|협력"
                                r"|대행\s*(여행)?사\s*(는|가|를|의|에)|대행여행사|현지\s*여행사|사용\s*실적|구성하여야|로\s*구성"
                                r"|적용\s*계수|인건비|제\s*\d+\s*조\s*\(")


def rx_performance(rec: Dict[str, Any]) -> List[str]:
    out = []
    for s in _lines(rec, r"실적|수행\s*경험|납품\s*경험"):
        vague = bool(PERF_VAGUE_RE.search(s)) and not PERF_VAGUE_EXCL_RE.search(s)
        if not re.search(r"이상|보유|있는|갖춘", s) and not vague:
            continue
        if EVAL_CONTEXT_RE.search(s) or PERF_BOILERPLATE_RE.search(s):
            continue
        # 서류 목록·서식 안내는 자격 제한이 아니다(무라벨 라벨 검토: '실적증명서 1부[서식 3]' 류)
        if re.search(r"\d+\s*부\b|서식|제출\s*서류|구비\s*서류", s):
            continue
        # 제안서 작성·발표·정성평가 안내는 자격이 아니다
        if re.search(r"제안서에|제안사의|발표자|정성|제시하며|기술하|열거", s):
            continue
        # 우대·선호·권고는 참가 제한이 아니다('…실적을 보유한 업체를 우대합니다', '(권고사항)')
        if re.search(r"우대|선호|권장|권고", s):
            continue
        if not (vague or parse_amounts(s) or PERF_SPECIFIC_RE.search(s) or relative_perf_multipliers(s) or (public_only_issuer(s) and PERF_REQUIRE_RE.search(s) and not re.search(r"국가관|채용|우선|확인하시|숙지|기술진|인력\s*풀|구성하여", s))):
            continue
        if re.search(r"업체|자이어야|자\)|있어야|참가\s*자격|한함|있는 자|보유한 자|한\s*자\b|단체|인\s*자\b", s):
            out.append(s)
    return out


def rx_region(rec: Dict[str, Any]) -> List[str]:
    out = []
    # '소재'만으로는 "이야기 소재" 같은 문장까지 걸려(무라벨 검토) 영업소·본점·소재지·소재한 업체로 좁힌다.
    for s in _lines(rec, r"주된\s*영업소|본점|소재지|본사|소재한\s*(업체|자|사업자)|소재하(는|고)\s*있는|내에\s*소재"
                           r"|소재\s*(업체|사업자)|관내\s*(에\s*)?(업체|사업자|사업장|본점|주된)|주된\s*사무소|사업장을\s*(둔|두고)"
                           r"|지역\s*(업체|업자)\s*(만|에\s*한|로\s*제한)"):
        # 09-24: 새로 받은 표현('소재 업체', '관내 업체', '주된 사무소', '사업장을 둔', '지역 업체만')은 입찰자 자격 줄만 본다.
        if not re.search(r"주된\s*영업소|본점|소재지|본사|소재한\s*(업체|자|사업자)|소재하(는|고)\s*있는|내에\s*소재", s) \
                and re.search(r"도급자|계약\s*상대자|낙찰자|활용|임차|하도급|협력|가능한|주요\s*내용|과업", s):
            continue
        if re.search(r"주소|위치|장소|납품|설치|전화|☎", s[:40]):
            continue
        if re.search(r"가산|가점|배점|평가|\+\s*\d+(\.\d+)?\s*점|우선\s*선정", s):      # 지역업체 가산점 조건은 참가 제한이 아니다
            continue
        # 참가자격이 아닌 문서·문맥: 각서·확약서·서약서·확인서·동의서 양식, 관할 법원 조항(다른 표현),
        # 과업 내용의 '면소재지', 보험 대상물 소재지, 성과품 목록(무라벨 20,000 meta 지역제한 N인 적중 55건 중 약 22건)
        if re.search(r"각서|서약|확약|확\s*인\s*서|동의서|법원|재판\s*관할|면\s*소재지|보험\s*대상|대상물|성과품", s):
            continue
        # 입찰자가 아닌 협력·분담 업체의 소재지(폐기물 '중간처리업체와 분담이행', '협력업체는 …')와 현지 운행 차량,
        # 입찰참여 확인서의 '본사(인)는'. 이 줄의 시·도가 입찰자 제한 목록에 섞여 v7(인접 확대)·v24(목록 불일치)를 만든다.
        if re.search(r"중간\s*처리\s*업체|처리\s*업체(와|과|\s*또는)|업체(와|과)\s*(공동|분담)|협력\s*업체|현지\s*운행|본사\s*\(\s*인\s*\)", s):
            continue
        # 참가 제한이 아닌 줄: 발주기관·제출장소 주소, 관할법원 조항, 참가신청서 양식 문장
        # (이 줄들이 섞이면 '단위=기초' 토큰 때문에 광역 제한이 시군구로 뒤집힌다 — 무라벨 500 v6 오탐 3건)
        if re.search(r"소재지\s*[:：]", s) and not re.search(r"제한|자격|인\s*자|있는\s*자|한\s*업체|참가|둔\s*자", s):
            continue
        if re.search(r"관할\s*법원|소송", s):
            continue
        if re.search(r"본사는|참가하고자|신청을\s*합니다|신청합니다", s):
            continue
        # 주소 줄: 띄어 쓴 '주 소 :'·'장 소 :', 익명화 자리표시 '[상세주소]'·'[우편번호]', 보험 피보험자·각서 문장.
        # 이 줄의 '단위=기초' 토큰이 지역제한 없는 공고(meta 지역제한여부 N)를 시군구 제한(v6)으로 만든다(무라벨 20,000 표본 30건 중 7건).
        restrict = re.search(r"제한|한함|한정|자격|참가|있는\s*(업체|자)|둔\s*(업체|자)|소재한\s*(업체|자)|만\s*(입찰\s*)?(참여|참가)", s)
        if (re.search(r"주\s*소\s*[:：]|장\s*소\s*[:：]", s[:40]) or re.search(r"\[상세주소\]|\[?우편번호\]?|피보험자|본사\s*\(\s*본인", s)) \
                and not restrict:
            continue
        # '본사'만 걸린 줄은 제한 어휘가 있어야 한다(기관 본사 위치 안내가 대부분이다).
        if not re.search(r"주된\s*영업소|본점|소재지|소재한|소재하|내에\s*소재", s) and not restrict:
            continue
        if PROVINCE_RE.search(s) or "단위=기초" in s or "기초자치단체" in s:
            out.append(s)
    return out


# 법령·규정·기관·확인서 이름 속 "중소기업"·"중·소기업"은 제한 수준이 아니다(무라벨 검토: v17 오탐 9건).
DOT = "·ㆍ‧․･•⋅∙・"
LAW_NAME_RE = re.compile(
    r"[「『｢〔\[][^」』｣〕\]]{0,40}[」』｣〕\]]"
    rf"|중\s*[{DOT}]?\s*소기업\s*범위\s*및\s*확인에?\s*관한\s*규정"
    rf"|중\s*[{DOT}]?\s*소기업\s*[{DOT}]?\s*소상공인\s*및\s*장애인기업\s*확인요령"
    r"|중소기업기본법(\s*시행령)?|중소기업제품\s*[^\s,]*|중소기업\s*공공구매[^\s,]*|중소기업공공구매[^\s,]*"
    r"|중소(기업)?\s*벤처(기업)?\s*부|중소기업청(\s*고시)?|중소기업현황\s*정보시스템|중소기업\s*간주|중소기업중앙회"
    r"|중소기업협동조합|종합정보망")
CERT_SME_RE = re.compile(rf"중\s*[{DOT}/]\s*소기업\s*[{DOT}]?\s*소상공인\s*확인서|중소기업\s*[{DOT}]?\s*소상공인\s*확인서|중소기업\s*확인서(?!\s*\(\s*소기업)"
                         rf"|중기업\s*(또는|및|,|[{DOT}])\s*소기업\s*[{DOT}]?\s*소상공인\s*확인서"
                         r"|중소기업\s*(또는|및)\s*소상공인\s*확인서"
                         rf"|중\s*[{DOT}/]\s*소기업\s*확인서")
CERT_SMALL_RE = re.compile(rf"(?<![중{DOT}])소기업\s*(?:[{DOT}및또는,\s]|이나|혹은)*소상공인\s*확인서|(?<![중{DOT}])소기업\s*확인서"
                           rf"|중소기업\s*확인서\s*\(\s*소기업\s*(?:[{DOT}/,]|또는|및|이나)?\s*소상공인")


def classify_level(sentence: str) -> Optional[str]:
    """제한 문장 하나를 '중소기업'/'소기업·소상공인'으로 분류한다.
    법령·기관·확인서 이름과 '(중소기업자)' 괄호를 지운 본문으로 판단하되, 본문이 '중소기업 또는 소상공인'이어도
    요구 확인서가 소기업·소상공인 확인서뿐이면 소기업 수준으로 본다(dev DEV-076·077 v13, DEV-175 v17)."""
    if not sentence:
        return None
    m_but = re.search(r"다만\s*[,，]?|\(\s*단\s*[,，]", sentence)
    if m_but and m_but.start() > 10:
        head = classify_level(sentence[:m_but.start()])
        if head:
            return head
    small_cert = bool(CERT_SMALL_RE.search(sentence))
    sme_cert = bool(CERT_SME_RE.search(sentence))
    body = CERT_SMALL_RE.sub(" ", CERT_SME_RE.sub(" ", LAW_NAME_RE.sub(" ", sentence)))
    # '소기업 또는 소상공인(중소기업자)간'의 괄호는 설명일 뿐이다('제한경쟁입찰(중소기업자)'의 괄호는 제한 수준이라 남긴다).
    body = re.sub(r"(소기업|소상공인)\s*\(\s*중소기업자?\s*\)", r"\1", body)
    body = re.sub(r"중소기업자?\s*(와의\s*|간\s*|의\s*)?우선\s*조달(계약)?", " ", body)
    body = re.sub(r"중소기업(으로)?\s*간주(되는|된)?|중소기업자로\s*보는", " ", body)
    # '중기업은 참가자격이 없습니다'처럼 중기업을 빼는 문장은 소기업·소상공인 수준이다(무라벨 PPS-D-020600).
    if re.search(r"중기업(은|이)?\s*(참가\s*자격이\s*없|참여\s*(할\s*수\s*)?없|제외|불가)", sentence):
        return "소기업·소상공인"
    # 본문이나 3종 확인서('중기업, 소기업 또는 소상공인 확인서')가 중기업을 낱말로 부르면 중기업이 참가할 수 있다.
    # 확인서 규칙(DEV-076·077·175)은 본문이 포괄어 '중소기업·중·소기업'뿐일 때만 쓴다.
    if "중기업" in body:
        return "중소기업"
    if re.search(rf"중\s*[{DOT}/,]\s*소기업|중소기업(자)?", body):
        return "소기업·소상공인" if small_cert and not sme_cert else "중소기업"
    if re.search(r"소기업|소상공인", body):
        return "소기업·소상공인"
    if sme_cert:
        return "중소기업"
    if small_cert:
        return "소기업·소상공인"
    return None


PRIMARY_LEVEL_RE = re.compile(rf"(따른|의한|규정된|해당하는)\s*(중\s*[{DOT}/]?\s*소기업|중소기업|소기업|소상공인|중기업)")
LISTED_LEVEL_RE = re.compile(
    rf"[\-{DOT}○◦▪]\s*[「｢『]\s*중소기업기본법\s*[」｣』]\s*제\s*2\s*조[^\n]{{0,15}}?(따른|의한)\s*(중소기업|소기업|중기업)"
    # 참가자격 목록의 맨 줄('가. 소기업, 소상공인')은 제한 어휘가 없어도 자격 문장이다(dev DEV-118).
    rf"|^[가-힣]\s*[.)]\s*(중\s*[{DOT}]?\s*소기업|중소기업|소기업|소상공인|중기업)"
    rf"[,、\s{DOT}]*(및|또는)?[\s]*(중소기업|소기업|소상공인|중기업)?\s*$")


def _sme_candidates(rec: Dict[str, Any]) -> List[Tuple[str, str]]:
    """기업규모 문구 후보 (판정용 텍스트, 근거로 쓸 원문 줄).
    한 문장이 두 줄로 나뉜 경우(확인서 이름 뒤 '보유하고 있는 업체')를 위해 다음 줄까지 이어 붙인 형태도
    판정에 쓰지만, 근거는 반드시 원문에 그대로 있는 한 줄이어야 한다(정성평가는 정확한 부분문자열을 요구한다)."""
    pat = re.compile(r"소기업|소상공인|중소기업|중기업")
    out: List[Tuple[str, str]] = []
    for d in rec["docs"]:
        lines = [ln.strip() for ln in d["text"].split("\n")]
        for k, ln in enumerate(lines):
            if not pat.search(ln):
                continue
            s, e = _sentence_span(lines, k)
            if s == k:
                out.append((ln, ln))
                if k + 1 < len(lines) and lines[k + 1]:
                    out.append((_join_lines(lines[k:max(k + 1, e) + 1]), ln))
            else:
                # 세 줄 이상으로 나뉜 자격 문장의 가운데 줄('따른 소상공인으로서 … 발급된')에 다음 줄만 붙여 읽으면 앞 줄의
                # '중소기업 또는'이 빠져 수준을 거꾸로 읽는다(dev DEV-21 v17 누락). 문장 시작부터 끝까지 붙여 판단하고,
                # 조각+다음 줄 창은 만들지 않는다. 줄 단독 후보는 남긴다(자격 동사가 없으면 어차피 채택되지 않는다).
                out.append((ln, ln))
                out.append((_join_lines(lines[s:max(k + 1, e) + 1]), ln))
    return out


# 줄이 앞 줄 문장의 연속인지: 앞 줄이 종결(다·함·음·것·마침표·'…한 자'·'업체'·'(…함)'·줄 끝 '-')로 끝나지 않고,
# 이 줄이 목록 기호·괄호 주석으로 시작하지 않을 때. PDF 추출로 문장 가운데 빈 줄이 하나 끼는 경우도 잇는다.
_SENT_MARK_RE = re.compile(r"^(?:[가-하]\s*[\.\)]|\d{1,3}\s*[\.\)]|\(\s*[\d가-하]{1,2}\s*\)|[①-⑳⑴-⒇㉠-㉭㈀-㈍➀-➓❶-❿]"
                           r"|[\-–—•◦○●◎□■▶▷▸►※❍❏✓✔*◇◆▪◈▣◐◑◉☞➢➤|<\[【]|[ⅰ-ⅹⅠ-Ⅻ]|주\s*\d|[ㅇㆍ·]\s)")
_NOTE_START_RE = re.compile(r"^\(\s*(?:\*|※|주|단|참고|예)")
_SENT_END_RE = re.compile(r"(?:[.。!?:：;\-–—]|다|함|음|것|임|요|[한된는인은을]\s*자|업체|\([^()]*(?:함|음|것|다|임)\s*\.?\))\s*$")


def _continues(lines: List[str], j: int) -> bool:
    if j <= 0 or j >= len(lines) or not lines[j] or _SENT_MARK_RE.match(lines[j]) or _NOTE_START_RE.match(lines[j]):
        return False
    p = j - 1
    if not lines[p] and p >= 1:
        p -= 1
    return bool(lines[p]) and not _SENT_END_RE.search(lines[p])


def _sentence_span(lines: List[str], k: int, back: int = 3, fwd: int = 3) -> Tuple[int, int]:
    s = k
    while s > 0 and k - s < back and _continues(lines, s):
        s -= 1
        if not lines[s] and s > 0:
            s -= 1
    e = k
    while e + 1 < len(lines) and e - k < fwd:
        j = e + 1
        if not lines[j] and j + 1 < len(lines) and _continues(lines, j + 1):
            j += 1
        if not _continues(lines, j):
            break
        e = j
    return s, e


def _join_lines(parts: List[str]) -> str:
    """판정용으로 줄을 잇는다. 낱말 가운데 줄바꿈('소상 ⏎ 공인확인서', '중소 ⏎ 기업')은 공백 없이 붙인다."""
    out = ""
    for x in parts:
        if not x:
            continue
        if out and re.search(r"[가-힣]$", out) and re.match(r"[가-힣]", x):
            out += x
        else:
            out += (" " if out else "") + x
    return out


# 09-24: '…중소기업자만 참여 가능', '소기업 또는 소상공인만 입찰 참여 가능'도 자격 문장이다. 다만 중소기업 가산 적용 제외
# 상투문, 1억 미만 적법 목록(소기업·소상공인·벤처·창업), SW 대기업 참여제한 설명은 아니다(무라벨 20,000 판독 7건).
SME_ONLY_RE = re.compile(r"만\s*(입찰\s*)?(에\s*)?(참여|참가|응찰)\s*(가능|할\s*수|이\s*가능)")
SME_ONLY_EXCLUDE_RE = re.compile(r"가산|적용하지|창업|벤처|대기업|중견기업|소프트웨어")


def rx_sme_level(rec: Dict[str, Any]) -> Tuple[str, str]:
    """참가자격의 기업규모 제한 수준. '~에 따른 (중)소기업 … 소지한 자' 형태의 주 자격 문장을 우선하고,
    확인서 조회 안내·간주 특별법인 문장은 수준 판단에 쓰지 않는다(무라벨 검토)."""
    header_only = sme_header_only(rec)
    primary: Dict[str, str] = {}
    secondary: Dict[str, str] = {}
    notice: Dict[str, str] = {}      # 확인서 조회 안내·간주 특별법인: 제한 존재의 증거로만, 수준은 마지막 순위
    for s, ev_line in _sme_candidates(rec):
        # '유찰로 인해 중소기업자간 제한으로 확대'는 시행령 제2조의2가 허용하는 재공고 확대라 수준 판단에서 뺀다.
        # 09-24: '…중소기업 협동조합으로서 …확인서를 소지한 자'처럼 자격 목록에 협동조합이 함께 적힌 줄은 버리지 않는다.
        if re.search(r"\d+\s*부\b|사본|가점|평가|신용|하도급|제8조의2|부정당|경쟁제품|유찰", s) \
                or (re.search(r"협동조합", s) and not re.search(r"소지한|보유한|소지하여야|자격을\s*구비", s)):
            continue
        if SME_UNISSUED_RE.search(s) or (header_only and SME_HEADER_RE.search(s)):
            continue
        # 참가자격 제목 아래 목록 줄('-「중소기업기본법」제2조제2항에 따른 소기업, …, 창업기업')은 제한 어휘가 없어도 자격 문장이다.
        listed = bool(LISTED_LEVEL_RE.match(s))
        if "창업기업" in s and not listed:
            continue
        if not listed and not re.search(r"한함|한정|제한|소지한|보유(하고|한)|갖춘|등록(한|된)|자이어야|업체이어야"
                                        r"|소지\s*(하여야|해야|업체|자)|소지업체|구비\s*(해야|하여야|한)|자격을\s*구비"
                                        r"|우선\s*조달계약\s*대상|업체일 것|참가\s*자격|경쟁\s*\(|경쟁입찰\s*\(", s) \
                and not (SME_ONLY_RE.search(s) and not SME_ONLY_EXCLUDE_RE.search(s)):
            continue
        level = classify_level(s)
        if level is None:
            continue
        if re.search(r"간주|특별법인|확인(이|하며|되지|이 되지|이 안)|확인서는|확인서가", s):
            bucket = notice
        else:
            bucket = primary if PRIMARY_LEVEL_RE.search(s) else secondary
        bucket.setdefault(level, ev_line)
    # 같은 순위에 두 수준이 모두 있으면 소기업·소상공인을 택한다. 중소기업 문장은 확인서 일반 안내·다른 절의
    # 목록인 경우가 많았다(무라벨 PPS-D-013945: 주 자격은 소기업확인서, 뒤 목록 줄은 중소기업·소상공인 확인서).
    for bucket in (primary, secondary, notice):
        if "소기업·소상공인" in bucket:
            return "소기업·소상공인", bucket["소기업·소상공인"]
        if "중소기업" in bucket:
            return "중소기업", bucket["중소기업"]
    return "없음", ""


def _to_date(y: int, mth: int, d: int) -> Optional[date]:
    try:
        return date(y, mth, d)
    except ValueError:
        return None


def dates_in(s: str, year: int) -> List[date]:
    out = []
    for m in DATE_FULL_RE.finditer(s):
        dt = _to_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if dt:
            out.append(dt)
    if not out:
        for m in DATE_SHORT_RE.finditer(s):
            dt = _to_date(year, int(m.group(1)), int(m.group(2)))
            if dt:
                out.append(dt)
    return out


def posting_year(rec: Dict[str, Any]) -> int:
    v = str(meta(rec, "공고게시일자") or "")
    return int(v[:4]) if v[:4].isdigit() else 2026


# 설명회 줄 전용 날짜 형식: 요일 괄호 없는 '2월 7일 14시', 두 자리 연도 ''26. 2. 7.', 시각이 붙은 '2. 7. 14:00'.
# 마감일 탐색에는 쓰지 않는다(목록 번호 등을 날짜로 읽을 수 있어서).
BRIEF_MD_RE = re.compile(r"(?<![\d\.])(\d{1,2})\s*월\s*(\d{1,2})\s*일")
BRIEF_YY_RE = re.compile(r"['’‘`]\s*(\d{2})\s*[\.\-/]\s*(\d{1,2})\s*[\.\-/]\s*(\d{1,2})")
BRIEF_TIME_RE = re.compile(r"(?<![\d\.])(\d{1,2})\s*\.\s*(\d{1,2})\s*\.?\s*(?=\d{1,2}\s*[:시]|오전|오후)")


def brief_dates(s: str, year: int) -> List[date]:
    ds = dates_in(s, year)
    if ds:
        return ds
    out = []
    for m in BRIEF_YY_RE.finditer(s):
        dt = _to_date(2000 + int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if dt:
            out.append(dt)
    for rx in (BRIEF_MD_RE, BRIEF_TIME_RE):
        if out:
            break
        for m in rx.finditer(s):
            dt = _to_date(year, int(m.group(1)), int(m.group(2)))
            if dt:
                out.append(dt)
    return out


def rx_briefing(rec: Dict[str, Any]) -> Tuple[Optional[date], Optional[date], str]:
    year = posting_year(rec)
    brief, ev = None, ""
    for s in _lines(rec, r"설명회|현장\s*설명|제안요청서?\s*설명\s*[:：]|사업\s*설명\s*[:：]"):
        if re.search(r"미개최|없음|생략|갈음|하지\s*않|개별\s*통보|추후", s):
            continue
        ds = brief_dates(s, year)
        if ds:
            brief, ev = ds[0], s
            break
    # 표가 줄 단위로 풀려 날짜가 다음 줄에 오는 경우가 많아, 키워드 줄 뒤 3줄까지 함께 본다.
    deadline = None
    key = re.compile(r"(제안서|입찰서|가격입찰서).{0,20}(제출|접수)|제출\s*마감|접수\s*마감|마감\s*일시")
    for d in rec["docs"]:
        lines = [ln.strip() for ln in d["text"].split("\n") if ln.strip()]
        for idx, s in enumerate(lines):
            if not key.search(s) or re.search(r"설명회|평가|개찰", s):
                continue
            ds = dates_in(" ".join(lines[idx:idx + 4]), year)
            if ds:
                cand = max(ds)
                if deadline is None or cand > deadline:
                    deadline = cand
    return brief, deadline, ev


SMALL_PROVISO_RE = re.compile(r"제\s*2\s*조의\s*2[^\n]{0,25}?(단서|제?\s*1\s*호\s*(가|나)\s*목)")
EXCEPTION_RE = re.compile(r"제\s*2\s*조의\s*3|우선조달계약.{0,10}(예외|제외)"
                          # 시행령 제7조 제1항의 경쟁입찰 예외를 적용한다고 적은 공고(dev DEV-154)
                          r"|경쟁입찰의?\s*예외|일반물품으로\s*입찰공고")


# 시행령 제2조의3 ②: 우선조달계약 예외 사유는 공고문에 적거나 나라장터에 입력해야 한다.
# 나라장터 입력분이 meta 조항호내용이다. ①4호(특정한 성능·기술·품질이 필요해 우선조달로는 목적 달성 불가)와
# ①3호(수의계약·지명경쟁으로 할 수 있도록 다른 법령이 정한 경우)가 여기에 문자열로 남는다.
META_EXCEPTION_RE = re.compile(r"특수한\s*기술|특정한\s*성능|협상에\s*의한\s*계약|지명경쟁")


def meta_exception(rec: Dict[str, Any]) -> bool:
    return bool(META_EXCEPTION_RE.search(str(meta(rec, "조항호내용") or "")))


def has_procurement_exception(src: str) -> bool:
    """판로지원법 시행령 제2조의3 우선조달 예외를 실제로 적용했는지.
    '제2조의3 제1항 제2호에 따라 비영리법인은 확인서 없이 참가 가능'은 제한을 유지한 채 비영리법인만 더 받는
    정형 문구라 예외로 보지 않는다(dev v15 놓침 3건: DEV-055·079·080)."""
    for m in EXCEPTION_RE.finditer(src):
        if m.group(0).lstrip().startswith("제"):
            context = src[max(0, m.start() - 120):m.end() + 120]
            if not re.search(r"판로지원|구매촉진|우선\s*조달", context):
                continue
        after = src[m.end():m.end() + 120]
        if "비영리" in after or re.search(r"(?<!\d)2\s*호", after[:20]):
            continue
        return True
    return False


# SW진흥법 제48조 + 중소 소프트웨어사업자의 사업 참여 지원에 관한 지침 제3조②: 발주기관은 공고문·제안요청서에
# "대기업 참여제한 하한제도 적용 여부(적용 근거 포함)"를 명시해야 하고, 그 명시는 '대기업'이라는 낱말 없이도 성립한다
# (dev DEV-064 "소프트웨어진흥법 제48조에 따른 소프트웨어사업자의 사업금액별 참여 제한").
# 제48조·"참여 제한"은 단독으로는 보안서약서·계약보증금 상투문에 흔하므로, 같은 줄에 소프트웨어 + 참여제한 +
# 금액/조문 고리가 모두 있고 상투문 낱말이 없을 때만 인정한다(20260920_detection_fixes R1 이식).
SW_LIMIT_RE = re.compile(r"(참여|참가)\s*제한")
SW_LIMIT_HOOK_RE = re.compile(r"제\s*48\s*조(?!\s*의)|사업\s*금액|제한\s*금액|하한")
SW_LIMIT_NOISE_RE = re.compile(r"보안|손해배상|부정당|청렴|금품|향응|계약보증금|하자보증")


def sw_big_limit_noted(src: str) -> bool:
    for line in src.split("\n"):
        if "소프트웨어" not in line:
            continue
        if SW_LIMIT_RE.search(line) and SW_LIMIT_HOOK_RE.search(line) and not SW_LIMIT_NOISE_RE.search(line):
            return True
    return False


# v22: 국가계약법 시행령 제43조⑤(지방 제43조⑥)는 제안요청서 등에 대한 설명을 '할 수 있다'고 하고, 그 설명을 들은 자로
# 참가를 제한하던 조항(국가 ⑥·지방 ⑦)은 삭제됐다. 위반은 **설명회 참석을 입찰·제안서 제출 자격으로 삼는 것**이다.
# 제안서 발표(제안설명회·제안서 설명회) 불참 시 감점·서면평가·0점·평가 제외는 같은 조 ⑧의 제안서 평가 절차라 이 항목이 아니다.
# 무라벨 20,000건 정규식 적중 233건 중 198건이 발표·평가(142)·제안서 설명회(28)·제한 없음 명시(28) 문장이었다
# (dev 양성 5건은 모두 사업·현장설명회 참석 제한이고 이 수정 후에도 5/0/0 유지).
# 09-23 ⑤: 제외어를 '평가·신청·별도 제공·안내' 같은 일반어로 두면 "설명회 미참석 업체는 평가 대상에서 제외",
# "참석 신청 후 참석한 업체에 한하여 입찰 참가" 같은 참석 제한 문장까지 지운다(바꿔 쓴 제한 문장 18종 × 8공고 80/144 → 136/144).
# 제외는 발표·평가 벌점·설명회 운영 안내·명시적 부정으로만 한다. 무라벨 20,000 v22 +34.
# 09-24 검토: '입찰참가자격'의 '참가'는 설명회 참석 표지가 아니다(목차·공동수급 줄이 켜졌다). 부정은 조사가 붙어도
# 읽고("필수사항은 아니나", "필수가 아닙니다"), 참석 여부 회신 요청("참석여부 및 인원 확인 필수")은 운영 안내로 본다.
# "설명회 참석 업체로 제한"은 제한 표지로 읽는다.
BRIEF_RESTRICT_RE = re.compile(r"설명회[^\n]{0,80}((?<!입찰)(?<!입찰\s)참[석가][^\n]{0,30}(한하|한해|만|자격|허용되지|제외|접수하지|불가|없|무효|필수)"
                               r"|미참석|불참|참석하지\s*(아니한|않은)|참석한\s*(자|업체)|참[석가]한?\s*(업체|자|사업자)\s*(로|으로)\s*제한)")
BRIEF_NOT_RESTRICT_RE = re.compile(
    # 제안서 발표·평가 절차(국가 시행령 제43조⑧)와 그 벌점: 참가자격 제한이 아니다
    r"제안서?\s*(평가\s*)?설명|제안\s*설명|제안\s*내용을\s*설명|발표|프레젠테이션|ppt|PPT|질의\s*응답|순서"
    r"|감점|0\s*점|점\s*처리|최저점|서면\s*(심사|평가|대체)"
    # 설명회 운영 안내: 참석 신청 마감·시간·인원·지참물·자료 배부·설명회 미개최
    r"|참석\s*(인원|시간)|지참|자료[^\n]{0,10}(별도\s*)?(제공|배부)|생략|갈음|미실시|실시하지\s*않|개최하지\s*않"
    r"|설명회에\s*참석할\s*수\s*없|참[석가]\s*여부[^\n]{0,20}(확인|회신|통보|알려)"
    # 명시적 부정
    r"|필수\s*(조건|사항)?\s*(은|는|이|가)?\s*아[니닙님]|의무\s*(사항)?\s*(은|는|이|가)?\s*아[니닙님]|불이익|무관|상관\s*없|관계\s*없|관련\s*(이\s*)?없"
    r"|제한\s*(은|이)?\s*없|불참하더라도|불참해도|미참석\s*업체도|미참석자도|업체도\s*(협상|입찰|참가)|독려|참석이\s*불가능할")


def briefing_restriction(src: str) -> Optional["re.Match"]:
    for m in BRIEF_RESTRICT_RE.finditer(src):
        ls = src.rfind("\n", 0, m.start()) + 1
        le = src.find("\n", m.end())
        if not BRIEF_NOT_RESTRICT_RE.search(src[ls:le if le >= 0 else len(src)]):
            return m
    return None


# v4(특정기관 발주 실적 한정): 발주처 목록이 민간에도 열려 있으면 한정이 아니다 — '또는 상장기업·일반 회사·법인·기업 및 단체·금융기관',
# '공공기관 등에서 발주한'(dev DEV-165 라벨 0). 공공 낱말이 부정당업자 제재 조항이나 계약법 법령명에서 온 줄도 제외한다.
PUBLIC_OPEN_RE = re.compile(r"(또는|및|이나|,|·|ㆍ)\s*(일반\s*)?(민간|기업체?|회사|법인|단체|상장|사기업|금융기관|아파트)"
                            r"|등\s*(에서|이|의|으로|에|을)?\s*(발주|시행|수행|납품|계약)"
                            r"|부정당|제재|당사자로\s*하는\s*계약에\s*관한")


def public_only_issuer(s: str) -> bool:
    # '실적이 있는 업체 또는 단체'의 단체·법인은 입찰자 형태이지 발주처가 아니다.
    t = re.sub(r"(업체|자)\s*(또는|및|,)\s*(단체|법인)", r"\1", s)
    return bool(PUBLIC_ISSUER_RE.search(t)) and "민간" not in t and not PUBLIC_OPEN_RE.search(t)


V19_BID_RE = re.compile(r"입찰\s*(서|참가|시|마감|등록)|마감|참가\s*신청|투찰|참가\s*전")
V19_MAKER_RE = re.compile(r"제조|공급|기술\s*지원|A/?S|기술\s*서비스")
V19_EXCL_RE = re.compile(r"본인은|서약|이의를?\s*제기|계약\s*(체결\s*)?(시|전|후|이후)|계약\s*체결|낙찰자\s*(는|로|가)|낙찰\s*후"
                         r"|납품\s*(시|전|후)|해당\s*시|필요\s*시|요청\s*시|제출할\s*수\s*있|청렴|보증금|이행\s*각서|지급\s*확약"
                         r"|근로|노동|고용|불인정|허위")


def regex_facts(rec: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    src = full_text(rec)
    perf = rx_performance(rec)
    region = rx_region(rec)
    level, level_ev = rx_sme_level(rec)
    region_text = " ".join(region) + " " + str(meta(rec, "제한지역코드목록") or "")
    provinces = sorted({PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(" ".join(region))}
                       | {PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(str(meta(rec, "제한지역코드목록") or ""))})
    shares = [float(m.group(5)) for m in re.finditer(
        r"(최소\s*(참여)?\s*지분(율|비율)?|지분(율|비율)?[^\n]{0,15}최소)[^\n%]{0,25}?(\d+(\.\d+)?)\s*%", src)]
    # 09-24 재검토: '최소' 없이 바꿔 쓴 지분 하한("구성원의 지분율은 각 4% 이상", "출자비율은 3% 이상",
    # "최소 참여비율은 5% 이상")도 읽는다. 공동수급·구성원 문맥 줄만 본다. 분담이행방식에는 최소지분율이 없으므로
    # (공동계약운용요령 제9조⑤ 가목, 지방자치단체 입찰 및 계약 집행기준 제6장 1-나-3) '분담' 표현은 읽지 않는다.
    # 무라벨 20,000 판정 변화 0 · dev 판정 변화 0 · 바꿔 쓴 지분 문장 주입 32/112 → 104/112.
    share_extra = [(float(m.group(3)), ln) for ln in _lines(rec, r"공동\s*(수급|도급|이행|계약)|구성원")
                   for m in re.finditer(r"(지분(율|비율)?|참여\s*비율|출자\s*비율)[^\n%]{0,20}?(\d+(\.\d+)?)\s*%\s*(이상|으로|로\s*한)", ln)]
    base_share_min = min(shares) if shares else None
    shares += [v for v, _ in share_extra]
    brief_restrict = briefing_restriction(src)
    brief, deadline, brief_ev = rx_briefing(rec)
    # 09-24: '발급받은·확인을 받은·갖춘·제출한 업체(자)'도 입찰자 자격 어미가 붙으면 직생 요구로 본다.
    # 낙찰자의 공급 의무·제작 조건 문장은 자격이 아니다(무라벨 PPS-D-015111·016529).
    # 09-27: 조건부 안내문('경쟁제품으로 입찰공고한 경우 입찰참가자는 … 보유하여야')과 낙찰 뒤 입증서류·자료
    # ('계약예정자 통보를 받은 업체에 한하여 … 제출', '입증자료(직접생산확인증, 환경마크, GR)를 갖춘 자')는 이 공고의 직생 요구가 아니다
    # (무라벨 20,000에서 조건부 18공고 · 입증서류·자료 약 20공고, 전부 같은 서식 · 무라벨 PPS-D-019104·014423 손라벨 0).
    direct = [s for s in _lines(rec, r"직접생산")
              if not re.search(r"\d+\s*부\b|해당\s*시|공고(한|된|하는)\s*경우|계약\s*예정자|낙찰\s*예정자|입증\s*(서류|자료)", s)
              and (re.search(r"소지|보유", s)
                   or (re.search(r"(발급\s*받은|확인을?\s*받은|갖춘|제출한)\s*(업체|자)\s*(에\s*한|만|이어야|여야|일\s*것|로\s*제한|$|[.)])", s)
                       and not re.search(r"낙찰자|생산한\s*제품|제품을\s*공급|제작하여야|납품하여야", s)))]
    # 부재형 v10용: 줄바꿈으로 '소지'가 다음 줄에 가도 직생 요구로 본다(위반 경고 상투문은 제외). v12(존재형)는 위 좁은 기준을 쓴다.
    direct_broad = False
    for d in rec["docs"]:
        lines = [ln.strip() for ln in d["text"].split("\n") if ln.strip()]
        for k, ln in enumerate(lines):
            if "직접생산" not in ln or re.search(r"위반|하도급|하청|타사제품|확인기준을|요구하지\s*않|해당\s*시|\d+\s*부\b", ln):
                continue
            window = " ".join(lines[k:k + 2])
            if re.search(r"증명서|확인서|증명원", window) and re.search(r"소지|보유|발급|확인되지|자격|제출\s*(이\s*)?가능(한)?\s*(업체|자|사업자)|제출할\s*수\s*있는", window):
                direct_broad = True
                break
        if direct_broad:
            break
    _perf_amounts = [a for s in perf for a in parse_amounts_ext(s)]
    _budget_ref = float(meta(rec, "배정예산금액") or price(rec) or 0)
    if _budget_ref > 0:
        _perf_amounts += [_budget_ref * k for s in perf for k in relative_perf_multipliers(s)]
    comp_codes = [c for c in codes_in_record(rec) if c in table]
    share_line = next((s for s in _lines(rec, r"지분") if re.search(r"\d\s*%", s)), "")
    # 09-25 S2: 제조사 물품공급·기술지원 확약서를 입찰·마감 전에 보유·제출하게 하는 줄(v19). 입찰서 서약문('본인은 …')·
    # 계약 시 제출·낙찰자 의무·해당 시 제출은 아니다(dev DEV-196 서약문 = 0, DEV-035·036·037 = 1).
    commit = [s for s in _lines(rec, r"확약서") if V19_BID_RE.search(s) and V19_MAKER_RE.search(s) and not V19_EXCL_RE.search(s)]
    # 09-24: '대학 또는 산학협력단만 참여 가능', '4년제 대학교만 참여 가능', '[기관(대학)]만 입찰 참여 가능'(dev DEV-01·035·049).
    # 입찰 참여의 주어가 대학·산학협력단·연구기관일 때만 본다(무라벨 20,000: 인원·연구원·낙찰자·제출 문장은 제외).
    inst_only = [s for s in _lines(rec, r"만\s*(입찰\s*)?(에\s*)?(참여|참가|응찰)\s*(가능|할\s*수)")
                 if INSTITUTION_ONLY_RE.search(s) and not re.search(r"인원|연구원\s*만|학생|근무\s*시간|낙찰자|실적|제출", s)]
    if share_extra:
        extra_min, extra_line = min(share_extra, key=lambda t: t[0])
        if base_share_min is None or extra_min < base_share_min:
            share_line = extra_line                  # 판정에 쓴 하한이 나온 줄을 근거로 쓴다
    return {
        "계약목적물_세부품명번호": comp_codes[0] if comp_codes else "해당없음",
        "직접생산확인_요구": bool(direct),
        "직접생산_언급_넓게": direct_broad,
        "기업규모_제한": level,
        "기업규모_근거": level_ev or None,
        "우선조달_예외사유_기재": has_procurement_exception(src),
        "실적제한": bool(perf),
        "실적_요구금액_원": (int(max(_perf_amounts)) if _perf_amounts else None),
        "실적_발주처_공공한정": any(public_only_issuer(s) for s in perf),
        "실적_근거": perf[0] if perf else None,
        "지역제한": bool(region) or meta(rec, "지역제한여부") == "Y",
        "지역_단위": "시군구" if ("단위=기초" in region_text or "기초자치단체" in region_text)
        else ("시도" if provinces else "없음"),
        "지역_시도목록": provinces,
        "지역_근거": region[0] if region else None,
        "특정기관_한정": bool(inst_only),
        "특정기관_근거": inst_only[0] if inst_only else None,
        "특정모델_지정": False,
        "특정모델_근거": None,
        "확약서_입찰시제출": bool(commit),
        "확약서_근거": commit[0] if commit else None,
        # 정규식 전용 키(LLM 스키마에 없어 병합 후에도 남는다): LLM이 '예'라면서 조건에 안 맞는 줄을 인용해도
        # 정규식이 찾은 줄로 v19 조건을 확인할 수 있게 한다(무라벨 750: LLM 확약 '예'인데 인용이 계약 시·서약서인 공고 18건).
        "확약서_근거_정규식": commit[0] if commit else None,
        "설명회_미참석_참가불가": bool(brief_restrict),
        "설명회_개최일": brief.isoformat() if brief else None,
        "제안서_마감일": deadline.isoformat() if deadline else None,
        "설명회_근거": (brief_restrict.group(0) if brief_restrict else brief_ev) or None,
        "공동수급_최소지분율": min(shares) if shares else None,
        "공동수급_근거": share_line or None,
        "대기업_참여제한_문구": bool(re.search(r"대기업|상호출자제한|중견기업", src)) or sw_big_limit_noted(src),
        "공고서_계약방법": "불명",
        "공고서_예산금액_원": None,
        "공고서_업종코드": [],
    }


# ===== 7. 사실 결합 =====
BOOL_KEYS = ["직접생산확인_요구", "우선조달_예외사유_기재", "실적제한", "실적_발주처_공공한정", "지역제한",
             "특정기관_한정", "특정모델_지정", "확약서_입찰시제출", "설명회_미참석_참가불가", "대기업_참여제한_문구"]


# or 모드에서 근거 키 → 그 근거가 뒷받침하는 불리언 키
OR_EVIDENCE_OF = {"특정기관_근거": "특정기관_한정", "확약서_근거": "확약서_입찰시제출"}
# 09-27: v1 LLM 근거가 제한이 아닌 서술이면 근거로 쓰지 않는다(서버 int8 본 호출이 4bit보다 v1을 3배 켜며 생긴 유형) —
# 연구과제 세부 구성 예시('1세부: ΔΔ대학교 A교수'), 괄호 '(주관기관 : …)', '기업, 대학, … 등이 수행하도록'(기업을 한 항목으로 나열한 포괄 서술 — '기업부설연구소'는 해당 없음).
# 무라벨 PPS-D-002024·019877 손라벨 0. dev v1 정답 근거('…만 참여 가능')와 겹치지 않는다.
V1_NOT_RESTRICTION_RE = re.compile(r"\d\s*세부\s*[:：]|^\s*[(（]\s*주관\s*기관\s*[:：]|기업\s*[,，·ㆍ][^\n]{0,40}등이\s*수행하도록")


def merge_facts(llm: Optional[Dict[str, Any]], rx: Dict[str, Any], policy: Dict[str, str]) -> Dict[str, Any]:
    """policy[key] ∈ {llm, rx, or, and}. LLM 출력이 없으면 정규식 사실을 그대로 쓴다."""
    if not llm:
        return dict(rx)
    out = dict(rx)
    for k, v in llm.items():
        if k not in rx:
            continue
        mode = policy.get(k, "llm")
        if k in BOOL_KEYS:
            lv, rv = bool(v), bool(rx[k])
            out[k] = {"llm": lv, "rx": rv, "or": lv or rv, "and": lv and rv}[mode]
        elif mode == "rx":
            out[k] = rx[k]
        elif mode in ("or", "llm_then_rx"):
            pair = OR_EVIDENCE_OF.get(k)
            if pair and not bool(llm.get(pair)) and bool(rx.get(pair)):
                out[k] = rx[k]              # 불리언을 정규식만 참으로 만들었다 → 근거도 정규식 줄
                continue
            empty = v in (None, "", [], "없음", "해당없음", "불명")
            if k == "특정기관_근거" and isinstance(v, str) and V1_NOT_RESTRICTION_RE.search(v):
                empty = True                # 제한이 아닌 서술 → 정규식 근거(없으면 공란 → v1=0)
            out[k] = rx[k] if empty else v
        else:
            out[k] = v
    return out


# 항목별 사실 출처(dev 200건 MLX 비교 결과, README 참고).
#  rx  : 정규식 사실. 규칙형 항목에서 LLM은 평가표 실적·주소 등을 제한으로 읽어 오탐이 많았다.
#  llm : 문맥 판단이 필요한 항목(특정기관·모델명·확약서·경쟁제품 품목·기업규모 수준).
#  or  : 날짜처럼 한쪽이 못 찾으면 다른 쪽 값으로 채운다.  and : 두 쪽이 모두 동의할 때만.
ITEM_SOURCE: Dict[str, str] = {k: "rx" for k in ITEMS}
ITEM_SOURCE.update({"v1": "or", "v9": "llm", "v11": "llm", "v13": "llm", "v15": "llm", "v19": "llm",
                    "v10": "and", "v23": "or"})
# 09-25 안전망: v13·v15는 수준만 'LLM 없음 → 정규식', v19는 확약서 사실을 LLM∨정규식.
ITEM_SOURCE.update({"v13": "llm_or_level", "v15": "llm_or_level", "v19": "or"})
# 09-25: 특정기관_근거도 병합 키다. v1은 'or' 모드인데 근거가 LLM 값으로만 들어가면 LLM이 놓친 줄을 정규식이 잡아도
# 근거 공란으로 v1=0이 된다(주입 시험: LLM 출력 있음 0/60, 없음 60/60). 이 키를 쓰는 판정 줄은 v1뿐이다.
FACT_KEYS = BOOL_KEYS + ["계약목적물_세부품명번호", "기업규모_제한", "실적_요구금액_원", "지역_단위", "지역_시도목록",
                         "설명회_개최일", "제안서_마감일", "공동수급_최소지분율", "특정기관_근거",
                         "확약서_근거"]


def _mode_policy(mode: str) -> Dict[str, str]:
    """출처 모드별 사실 병합 정책. 'llm_or_level'은 기업규모 수준만 LLM이 '없음'일 때 정규식 수준을 쓰고 나머지는 LLM."""
    if mode == "llm_or_level":
        pol = {k: "llm" for k in FACT_KEYS}
        pol["기업규모_제한"] = "or"
        return pol
    return {k: mode for k in FACT_KEYS}


# ===== 8. 법령 판정기 =====
def _norm_date(s: Any) -> Optional[date]:
    if not isinstance(s, str):
        return None
    m = DATE_FULL_RE.search(s)
    return _to_date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def _meta_industry_codes(rec: Dict[str, Any]) -> set:
    return set(re.findall(r"\((\d{4})\)", str(meta(rec, "면허업종제한목록") or "")))


def _meta_method(rec: Dict[str, Any]) -> str:
    return str(meta(rec, "계약방법") or "")


def is_software(rec: Dict[str, Any]) -> bool:
    return "소프트웨어" in str(meta(rec, "면허업종제한목록") or "") or "소프트웨어사업자" in full_text(rec)


def note_ok(rec: Dict[str, Any], it: Dict[str, Any], facts: Dict[str, Any]) -> bool:
    """중기부 고시 특이사항 조건을 공고 원문으로 확인한다. 조건을 읽을 수 없으면 통과시킨다(보수적)."""
    note = it.get("note") or ""
    if not note:
        return True
    if "소프트웨어 진흥법" in note:          # 8111 계열: 소프트웨어사업일 때만 경쟁제품
        # 단, 공고가 그 품목의 직접생산확인증명서를 요구했다면 발주기관이 스스로 경쟁제품으로 다룬 것이다.
        return is_software(rec) or bool(facts.get("직접생산확인_요구"))
    # 나머지 특이사항(규격·중량·용도 조건)은 원문 대조가 불안정해 적용하지 않는다.
    # dev 실험: 조건어 키워드 대조를 일반화하면 v12 오탐 +2·v13 정탐 -1로 교차 검증이 0.7906 → 0.7847로 내려갔다.
    return True


# 시행령 제7조(중소기업자간 경쟁입찰의 예외) ①4호 "특정한 기술·용역이 필요한 경우 등 공공기관의 특별한
# 사정으로 인하여 중소기업자간 경쟁입찰 외의 방법으로 구매"하는 경우. ②항은 그 사유를 입찰공고문에 기재하거나
# 나라장터에 입력하라고 정한다. 공고문에 사유를 적었으면 경쟁제품 분기(v10·v11·v13)를 적용하지 않는다.
# 우선조달 예외(제2조의3)와는 다른 조문이라 v14~v18에는 걸지 않는다.
# 조문 번호만으로는 안 된다: "제7조제1항"은 전자입찰특별유의서 제7조 등 상투문과 겹쳐 dev 200건 중 39건이 걸린다.
# 적용을 선언하는 동사구까지 같은 줄에서 확인한다(dev 2건).
COMPETITIVE_EXEMPT_RE = re.compile(
    r"제\s*7\s*조[^\n]{0,40}?(규정을?\s*적용|예외를?\s*적용|외의\s*방법으로|일반물품으로)"
    r"|일반물품으로\s*입찰공고"
    r"|직접생산확인(품목|증명서)[^\n]{0,24}?(제외하|별도로\s*요구하지\s*않)")


# 고시 특이사항의 "…에 한함" 조건. 조건에 쓰인 낱말이 공고 어디에도 없으면 그 품목으로 단정하지 않는다.
# 경쟁제품 판정이 위반을 만드는 항목(v10·v11·v13)에만 건다 — v12·v14~v18은 경쟁제품이 "아님"이 위반을
# 만들어서 반대로 오탐이 는다(교차 검증 0.7906 → 0.7847로 확인).
ONLY_RE = re.compile(r"([^.·]{2,60}?)에\s*한(?:함|한다|정)")
NOTE_WORD_RE = re.compile(r"[가-힣A-Za-z][가-힣A-Za-z0-9]{1,}")
NOTE_STOP = {"제품", "경우", "적용", "대상", "이내", "이하", "이상", "미만", "초과", "한함", "제외", "포함",
             "다만", "해당", "관련", "기준", "사업", "계약", "체결", "다음", "각목", "항목", "조달청", "방식",
             "추정가격", "억원", "만원", "금액"}


def note_condition_met(rec: Dict[str, Any], it: Dict[str, Any]) -> bool:
    note = it.get("note") or ""
    if not note:
        return True
    txt = full_text(rec)
    for m in ONLY_RE.finditer(note):
        words = [w for w in NOTE_WORD_RE.findall(m.group(1)) if w not in NOTE_STOP and len(w) >= 2]
        if words and not any(w in txt for w in words):
            return False
    return True


def competitive_exempt(rec: Dict[str, Any]) -> bool:
    return bool(COMPETITIVE_EXEMPT_RE.search(full_text(rec)))


# 판로지원법 제6조·제7조: 중기부장관(옛 중소기업청장)이 지정·공고한 제품이 중소기업자간 경쟁제품이다.
# 나라장터 meta 조항호내용에 그 지정 사실이 남는 공고가 있고, 면허업종 '행사대행업'은 목적물이 행사·전시 대행이라는 뜻이다.
# 둘 다 발주기관 자신의 기재이므로, 본 호출이 품목을 못 고른 용역 공고에서 품목 호출의 코드를 인정하는 근거로 쓴다
# (20260920_detection_fixes C3 이식).
META_DESIGNATED_RE = re.compile(r"(중소벤처기업부장관|중소기업청장)[^\n]{0,10}지정")
LICENSE_EVENT_RE = re.compile(r"행사대행")


def meta_designated_competitive(rec: Dict[str, Any]) -> bool:
    return bool(META_DESIGNATED_RE.search(str(meta(rec, "조항호내용") or "")))


def meta_event_license(rec: Dict[str, Any]) -> bool:
    return bool(LICENSE_EVENT_RE.search(str(meta(rec, "면허업종제한목록") or "")))


def is_competitive(facts: Dict[str, Any], rec: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> bool:
    code = str(facts.get("계약목적물_세부품명번호") or "")
    it = table.get(code)
    if not it:
        return False
    p = price(rec)
    if not (it["limit"] is None or p is None or p < it["limit"]):
        return False
    return note_ok(rec, it, facts)


TITLE_BAND_RE = re.compile(r"\((일반경쟁|제한경쟁|수의계약|지명경쟁)\s*[·ㆍ]\s*(\d+)\s*억원?\s*(미만|이상)\)")


# SW 지침 제3조②의 명시 의무에는 금액 하한이 없다(운영 답변: 20억은 v20의 하한이 아니다).
# 다만 is_software는 면허업종 한 줄로도 켜져 비SW 목적물이 섞이므로, 1억 미만은 공고명이 SW 목적물인 입찰만 본다.
# 무라벨 손라벨 60건(labels/train20k_v20_*): 공고명 일치군 SW 19 / 비SW 3 / 불명 2, 불일치군 8 / 10 / 14.
# '전자'(전자입찰공고)·'온라인'(홍보·교육)은 상투어라 넣지 않는다.
SW_OBJECT_RE = re.compile(r"소프트웨어|S/?W|시스템|홈페이지|플랫폼|DB|데이터베이스|전산|서버|라이선스|라이센스|솔루션|정보화"
                          r"|어플리케이션|앱|웹|포털|프로그램|정보망|CATIA|ANSYS|클라우드|네트워크|정보보안|GIS")


def commit_ev_ok(ev: str) -> bool:
    """v19 근거 조건: 확약서를 입찰·마감 시점에 제조·공급·기술지원·A/S 주체로부터 받게 하는 줄."""
    return "확약" in ev and bool(re.search(r"입찰|마감", ev)) and bool(re.search(r"제조|공급|기술지원|A/S", ev))


def judge(rec: Dict[str, Any], facts: Dict[str, Any], table: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    p = price(rec) or 0.0
    # 단가계약 등으로 추정가격이 1원·5원처럼 의미 없는 공고는 금액 구간 판정을 하지 않는다.
    priced = p >= 1_000_000
    local = is_local(rec)
    small_quote = local_small_quote(rec)
    region_limit = local_region_amount(rec) if local else NOTICE_AMOUNT
    budget = float(meta(rec, "배정예산금액") or p or 0)
    comp = is_competitive(facts, rec, table)
    level = facts.get("기업규모_제한") or "없음"
    exception = bool(facts.get("우선조달_예외사유_기재"))
    # 제2조의3 예외는 "우선조달계약을 체결하지 않을 수 있다"는 면책이다. 제한을 두지 않은 것(v16·v18)은
    # 면책되지만, 제한을 두되 금액 구간에 맞지 않는 수준으로 둔 것(v14·v15·v17)은 면책 대상이 아니다.
    absence_exception = exception or meta_exception(rec)
    private_contract = _meta_method(rec) == "수의계약"
    perf = bool(facts.get("실적제한"))
    region = bool(facts.get("지역제한"))
    provinces = {PROVINCE_ALIAS.get(x, x) for x in (facts.get("지역_시도목록") or []) if isinstance(x, str)}
    perf_amount = facts.get("실적_요구금액_원")
    share = facts.get("공동수급_최소지분율")
    v: Dict[str, int] = {k: 0 for k in ITEMS}

    # 근거 문구를 못 댄 특정기관 한정은 인정하지 않는다(무라벨 500 v1 판정 5건 중 2건이 근거 공란)
    v1_ev = clean_evidence(str(facts.get("특정기관_근거") or ""), full_text(rec))
    v["v1"] = int(bool(facts.get("특정기관_한정")) and bool(v1_ev))
    # 실적 제한
    v["v2"] = int(perf and priced and p < NOTICE_AMOUNT and not small_quote)
    v["v3"] = int(perf and isinstance(perf_amount, (int, float)) and budget > 0 and perf_amount >= budget)
    v["v4"] = int(perf and bool(facts.get("실적_발주처_공공한정")))
    # 지역 제한
    v["v5"] = int(region and priced and p >= region_limit)
    v["v6"] = int(region and priced and facts.get("지역_단위") == "시군구" and p < region_limit and not small_quote)
    v["v7"] = int(region and priced and len(provinces) >= 2 and p < region_limit and not small_quote)
    # 지방계약법 시행규칙 제25조 제7항: 실적(1호)과 지역(6호) 중복 제한 금지
    # 국가계약법 시행규칙 제25조⑤(항목표 v8 국가 근거)·집행기준 제5조④1: 국가계약도 실적+지역 중복 제한 금지
    v["v8"] = int(not small_quote and perf and region)
    # '동등 이상' 허용 규격은 특정 모델 지정으로 보지 않는다.
    v["v9"] = int(is_goods(rec) and bool(facts.get("특정모델_지정")) and "동등" not in str(facts.get("특정모델_근거") or ""))
    # 중기간 경쟁제품(판로지원법 제7조 경쟁입찰 규정 — dev에서 수의계약 건은 이 계열 위반 라벨 0건)
    if not private_contract:
        comp_bid = (comp and not competitive_exempt(rec)
                    and note_condition_met(rec, table.get(str(facts.get("계약목적물_세부품명번호") or "")) or {}))
        v["v10"] = int(comp_bid and not facts.get("직접생산확인_요구") and not facts.get("직접생산_언급_넓게"))
        v["v11"] = int(comp_bid and level == "없음" and not exception)
        v["v13"] = int(comp_bid and level == "소기업·소상공인")
    # (09-27 대비판) 소액수의 v10 규칙(판로지원법 제9조①1호)은 09-26 결과에 따라 뺐다.
    v["v12"] = int(bool(facts.get("직접생산확인_요구")) and not comp)
    # 판로지원법 시행령 제2조의2: 1억 미만 소기업·소상공인, 1억~고시금액 중소기업, 고시금액 이상 제한 금지
    # 항목표 비고: 판로지원 예외 면책은 v15~v18에만 달려 있고 v14에는 없다(detection_fixes Y1 이식).
    if not comp and priced and not private_contract:
        v["v14"] = int(p >= NOTICE_AMOUNT and level != "없음")
    if not comp and not exception and priced and not private_contract:
        v["v15"] = int(ONE_HUNDRED_MILLION <= p < NOTICE_AMOUNT and level == "소기업·소상공인")
        # 시행령 제2조의2 ①1·2호는 "제한경쟁입찰에 따라" 체결하라고 정한다. 일반경쟁으로 공고하고
        # 기업규모 제한도 두지 않은 것이 바로 위반 형태이므로 계약방법으로 판단 대상을 거르지 않는다
        # (운영 답변: "일반경쟁 등록만으로 판단 대상에서 제외되지 않는다").
        v["v16"] = int(ONE_HUNDRED_MILLION <= p < NOTICE_AMOUNT and level == "없음" and not absence_exception)
        v["v17"] = int(p < ONE_HUNDRED_MILLION and level == "중소기업" and not SMALL_PROVISO_RE.search(full_text(rec)))
        v["v18"] = int(p < ONE_HUNDRED_MILLION and level == "없음" and not absence_exception)
    if private_contract and not comp and not exception and priced and "소기업" in str(meta(rec, "조항호내용") or ""):
        v["v17"] = int(p < ONE_HUNDRED_MILLION and level == "중소기업" and not SMALL_PROVISO_RE.search(full_text(rec)))
    # 제조사 물품공급·기술지원 확약서를 입찰·마감 시점에 요구한 경우만(계약 시 제출·제출 가능 업체는 제외)
    commit_evs = [str(facts.get("확약서_근거") or ""), str(facts.get("확약서_근거_정규식") or "")]
    v["v19"] = int(is_goods(rec) and bool(facts.get("확약서_입찰시제출")) and any(commit_ev_ok(ev) for ev in commit_evs))
    # 1억 미만은 입찰로 발주한 SW 목적물만: 지침 제3조②의 명시 대상은 "입찰공고문 또는 제안요청서"이고 항목명도
    # '입찰참가자격 (SW)'이다. 09-24에 수의계약 견적 공고까지 넓혔다가 09-27에 되돌렸다 — 09-26 결과가 같은 모양의
    # v10 소액수의(항목명 '…경쟁제품 입찰…')를 채점 범위 밖으로 가리켰고, dev v20 정답 5건도 모두 입찰(1.2억 이상)이다.
    # 무라벨 PPS-D-014146 손라벨 0. 1억 이상 판정은 그대로 둔다.
    small_sw_bid = bool(SW_OBJECT_RE.search(title_of(rec))) and not private_contract
    v["v20"] = int(is_software(rec) and priced and (p >= ONE_HUNDRED_MILLION or small_sw_bid)
                   and not facts.get("대기업_참여제한_문구"))
    v["v21"] = int(isinstance(share, (int, float)) and 0 < share < (LOCAL_MIN_SHARE if local else NATIONAL_MIN_SHARE))
    v["v22"] = int(is_negotiation(rec) and bool(facts.get("설명회_미참석_참가불가")))
    # 지방 낙찰자 결정기준 제7장 제3절 2-다: 설명은 제안서 마감 전일부터 기산해 10/20/40일 전
    brief, deadline = _norm_date(facts.get("설명회_개최일")), _norm_date(facts.get("제안서_마감일"))
    if is_negotiation(rec) and local and brief and deadline and deadline >= brief:
        need = 40 if p >= 1e9 else (20 if p >= ONE_HUNDRED_MILLION else 10)
        v["v23"] = int((deadline - brief).days <= need)
    v["v24"] = int(meta_mismatch(rec, facts))
    return v


# 업종 등록 문장에서 4자리 업종코드를 읽는다: "업종코드: 5210", "(업종코드 : 9999또는9901)", "행사대행업 : 9901",
# "...업(1227)을 등록", "[5246]으로 신고". 마스킹 숫자(0000)·연도(19xx·20xx)는 버린다(4444·9999는 실제 코드).
_CODE_CTX_RE = re.compile(r"업종\s*코드|입찰\s*참가\s*(?:자격)?\s*(?:을|를)?\s*등록|등록한|등록을|업\s*[\(\[（][^\n]{0,40}\d{4}")
_CODE_NUM_RE = re.compile(r"(?<![\d.\-])(?<!\d,)(\d{4})(?![\d,.\-]|\s*(?:년|원|천|만|명|개|호|번|호선|m|㎡|kg))")
_CODE_EXCLUDE_RE = re.compile(r"참여\s*불가|제외|불가능|하지\s*않아도|않더라도|없이도|공동\s*또는\s*분담|분담\s*이행|공동\s*이행")


def text_industry_codes(rec: Dict[str, Any]) -> set:
    """공고서 본문의 업종 등록 문장에 적힌 4자리 업종코드."""
    out = set()
    for d in rec["docs"]:
        for ln in d["text"].split("\n"):
            if "업" not in ln or not _CODE_CTX_RE.search(ln) or _CODE_EXCLUDE_RE.search(ln):
                continue
            for c in _CODE_NUM_RE.findall(ln):
                if c.startswith("20") or c.startswith("19") or c == "0000":   # 연도·마스킹 숫자(meta 업종코드에 19xx·20xx 없음)
                    continue
                out.add(c)
    return out


def meta_mismatch(rec: Dict[str, Any], facts: Dict[str, Any]) -> bool:
    """공고서 기재값과 나라장터 입력값 대조: 예산·업종코드·제목 금액구간.
    LLM이 읽은 계약방법 비교는 dev 오탐 3건·정탐 0건이라 쓰지 않는다(계약방법 불일치는 제목 정규식이 잡는다)."""
    amount = facts.get("공고서_예산금액_원")
    # LLM이 옮긴 금액이 원문에 그대로 있을 때만 비교(숫자 환각 방지)
    if isinstance(amount, (int, float)) and amount > 1_000_000 and f"{int(amount):,}" in full_text(rec):
        known = [float(meta(rec, k)) for k in ("배정예산금액", "입찰추정가격") if meta(rec, k) not in (None, "")]
        if known and all(abs(amount - x) > max(1000.0, x * 0.001) for x in known):
            return True
    codes = {c for c in (facts.get("공고서_업종코드") or []) if isinstance(c, str) and re.fullmatch(r"\d{4}", c)}
    mcodes = _meta_industry_codes(rec)
    # int8 서버 모델은 공고서 업종코드 칸에 meta 값을 그대로 옮기기도 한다(dev DEV-079: 원문 5210, meta 5246).
    # 원문에 업종코드가 적혀 있으면 그 값을 먼저 대조한다.
    tcodes = text_industry_codes(rec)
    if tcodes and mcodes:
        if not tcodes & mcodes:
            return True
    elif codes and mcodes and not codes & mcodes:
        return True
    # 목록 대조만: 공고서가 든 시·도가 meta 제한지역에 없다
    nr = rx_region(rec)
    if nr:
        nprov = {PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(" ".join(nr))}
        mprov = {PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(str(meta(rec, "제한지역코드목록") or ""))}
        if nprov and mprov and nprov - mprov:
            return True
    m = TITLE_BAND_RE.search(rec["docs"][0]["text"][:300])
    p = price(rec)
    if m and m.group(1) != str(meta(rec, "계약방법") or ""):
        return True                       # 제목 괄호의 계약방법이 나라장터 입력과 다르다(결정론적 비교)
    if m and p:
        bound = float(m.group(2)) * 1e8
        if (m.group(3) == "미만" and p >= bound) or (m.group(3) == "이상" and p < bound):
            return True
    return False


def meta_mismatch_evidence(rec: Dict[str, Any], facts: Dict[str, Any], src: str) -> str:
    """v24 판정의 근거 문구. meta_mismatch와 같은 순서로 확인하고, 불일치를 만든 공고문 줄을 그대로 돌려준다.
    v24는 부재탐지 항목이 아니라 정성평가 대상인데 지금까지 근거를 내지 않았다(판정 10건 전부 공란)."""
    def line_with(needle: str) -> str:
        if not needle:
            return ""
        for d in rec["docs"]:
            for ln in d["text"].split("\n"):
                if needle in ln:
                    return clean_evidence(ln.strip(), src)
        return ""

    amount = facts.get("공고서_예산금액_원")
    if isinstance(amount, (int, float)) and amount > 1_000_000 and f"{int(amount):,}" in src:
        known = [float(meta(rec, k)) for k in ("배정예산금액", "입찰추정가격") if meta(rec, k) not in (None, "")]
        if known and all(abs(amount - x) > max(1000.0, x * 0.001) for x in known):
            ev = line_with(f"{int(amount):,}")
            if ev:
                return ev
    codes = {c for c in (facts.get("공고서_업종코드") or []) if isinstance(c, str) and re.fullmatch(r"\d{4}", c)}
    mcodes = _meta_industry_codes(rec)
    tcodes = text_industry_codes(rec)
    if tcodes and mcodes:
        codes = tcodes                    # meta_mismatch와 같은 순서: 원문 업종코드가 있으면 그것으로 대조
    if codes and mcodes and not codes & mcodes:
        for c in sorted(codes):
            ev = line_with(c)
            if ev:
                return ev
    nr = rx_region(rec)
    if nr:
        nprov = {PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(" ".join(nr))}
        mprov = {PROVINCE_ALIAS.get(p, p) for p in PROVINCE_RE.findall(str(meta(rec, "제한지역코드목록") or ""))}
        extra = nprov - mprov
        if nprov and mprov and extra:
            for s in nr:
                if any(PROVINCE_ALIAS.get(x, x) in extra for x in PROVINCE_RE.findall(s)):
                    ev = clean_evidence(s.strip(), src)
                    if ev:
                        return ev
    m = TITLE_BAND_RE.search(rec["docs"][0]["text"][:300])
    if m:
        return clean_evidence(m.group(0), src)
    return ""


# ===== 9. 근거 문구 =====
EVIDENCE_KEYS = {
    "v1": ["특정기관_근거"], "v2": ["실적_근거"], "v3": ["실적_근거"], "v4": ["실적_근거"],
    "v5": ["지역_근거"], "v6": ["지역_근거"], "v7": ["지역_근거"], "v8": ["실적_근거", "지역_근거"],
    "v9": ["특정모델_근거"], "v12": ["기업규모_근거"], "v13": ["기업규모_근거"], "v14": ["기업규모_근거"],
    "v15": ["기업규모_근거"], "v17": ["기업규모_근거"], "v19": ["확약서_근거"], "v21": ["공동수급_근거"],
    "v22": ["설명회_근거"], "v23": ["설명회_근거"],
}


_WS_RE = re.compile(r"\s+")
_QUOTE_DOC_PREFIX_RE = re.compile(r"^[\(\[【<]\s*(?:공고문|규격서|과업지시서|제안요청서|예외공표서)\s*[\)\]】>]\s*[-:·]?\s*")
_WS_INDEX: Dict[str, Tuple[str, List[int]]] = {}


def _ws_index(src: str) -> Tuple[str, List[int]]:
    """공백을 뺀 원문과, 그 글자마다 원문 위치를 돌려준다(공고당 1회 계산해 캐시)."""
    hit = _WS_INDEX.get(src)
    if hit is None:
        if len(_WS_INDEX) > 8:
            _WS_INDEX.clear()
        pos = [i for i, ch in enumerate(src) if not ch.isspace()]
        hit = ("".join(src[i] for i in pos), pos)
        _WS_INDEX[src] = hit
    return hit


def _ground_quote(ev: str, src: str) -> str:
    """모델 인용이 원문과 공백·줄바꿈만 다르거나 앞에 '(공고문)' 같은 문서명을 붙였으면 원문 구간을 그대로 돌려준다.
    int8 서버 모델은 여러 줄 인용을 한 줄로 이어 붙여(무라벨·dev 950건 기업규모 자격 인용 113건) 정확 일치 검사에서 버려졌다."""
    ev = _QUOTE_DOC_PREFIX_RE.sub("", ev).strip()
    if not ev:
        return ""
    if ev in src:
        return ev
    q = _WS_RE.sub("", ev)
    if len(q) < 6:
        return ""
    norm, pos = _ws_index(src)
    k = norm.find(q)
    if k < 0:
        return ""
    span = src[pos[k]: pos[k + len(q) - 1] + 1]
    return span if len(span) <= EVIDENCE_MAX else ""


def clean_evidence(ev: Any, src: str) -> str:
    if not isinstance(ev, str) or not ev:
        return ""
    ev = unicodedata.normalize("NFC", ev).replace("\r", "").strip()[:EVIDENCE_MAX].strip()
    if not ev or ev[0] in "=+@":
        return ""
    if ev in src:
        return ev
    ev = _QUOTE_DOC_PREFIX_RE.sub("", ev).strip()
    return ev if ev and ev[0] not in "=+@" and ev in src else ""


def evidence_for(item: str, rec: Dict[str, Any], llm: Optional[Dict[str, Any]], rx: Dict[str, Any], src: str) -> str:
    if item in ABSENCE:
        return ""
    if item == "v24":
        return meta_mismatch_evidence(rec, {**rx, **{k: v for k, v in (llm or {}).items() if v is not None}}, src)
    if item == "v19":
        for ev in ((llm or {}).get("확약서_근거"), rx.get("확약서_근거_정규식"), rx.get("확약서_근거")):
            ev = clean_evidence(ev, src) or _evidence_span(ev, src)
            if ev and commit_ev_ok(ev):
                return ev
    if item == "v12":
        cand = [s for s in _lines(rec, r"직접생산") if re.search(r"소지|보유", s)]
        return clean_evidence(cand[0], src) if cand else ""
    for key in EVIDENCE_KEYS.get(item, []):
        for facts in (llm or {}, rx):
            ev = clean_evidence(facts.get(key), src) or _evidence_span(facts.get(key), src)
            if ev:
                return ev
    return ""


def _evidence_span(ev: Any, src: str) -> str:
    """근거 문구(e열) 전용: 공백만 다른 인용을 원문 구간으로 돌려준다. 판정에는 쓰지 않는다."""
    if not isinstance(ev, str) or not ev.strip():
        return ""
    ev = _ground_quote(unicodedata.normalize("NFC", ev).replace("\r", "").strip()[:EVIDENCE_MAX], src)
    return ev if ev and ev[0] not in "=+@" else ""


def decide(rec: Dict[str, Any], llm_text: str, table: Dict[str, Dict[str, Any]],
           policy: Optional[Dict[str, str]] = None, item_text: str = "",
           model_text: str = "", sme_text: str = "", perf_text: str = "",
           region_text: str = "", goods_text: str = "") -> Tuple[Dict[str, int], Dict[str, str], bool]:
    llm = parse_facts(llm_text)
    parsed_main = llm is not None
    if model_text:
        llm = apply_model_call(rec, llm, model_text)
    rx = regex_facts(rec, table)
    if llm is not None:
        # 우선조달 예외는 정규식 판단으로 통일한다. LLM은 '비영리법인 참가 가능' 정형 문구도 예외로 읽었다(dev v15 놓침 3건).
        llm = dict(llm, 우선조달_예외사유_기재=rx["우선조달_예외사유_기재"])
    if llm and llm.get("기업규모_제한") in ("중소기업", "소기업·소상공인"):
        raw_ev = str(llm.get("기업규모_근거") or "")
        ev = clean_evidence(raw_ev, full_text(rec))
        level = classify_level(ev)
        if "조항호내용" in raw_ev:
            # 본문이 아닌 메타 조항호내용을 근거로 답한 경우: 라벨은 본문 기준이다(dev DEV-066·067·132·175).
            llm = dict(llm, 기업규모_제한="없음")
        elif level:
            llm = dict(llm, 기업규모_제한=level)
        elif ev:
            # 근거 문장에 기업규모 단어가 없다(직접생산확인증명서 소지 문장 등, dev DEV-060·063 v11).
            llm = dict(llm, 기업규모_제한="없음")
    if sme_text:
        llm, rx, _ = apply_sme_call(rec, llm, rx, sme_text)
    if perf_text:
        llm, rx, _ = apply_perf_call(rec, llm, rx, perf_text)
    if region_text:
        llm, rx, _ = apply_region_call(rec, llm, rx, region_text)
    if goods_text:
        llm, rx, _ = apply_goods_item_call(rec, llm, rx, table, goods_text)
    item = parse_facts(item_text)
    if item and needs_item_call(rec) and item.get("세부품명번호") in (service_codes(table) + ["해당없음"]):
        # 용역 품목: 본 호출이 고른 품목을 쓰되, 전용 호출이 "해당없음"이면 경쟁제품에서 뺀다.
        # 두 판단이 모두 경쟁제품이라고 할 때만 인정(dev: 전용 호출 단독 0.715, 본 호출 단독 0.720, 결합 0.736).
        base = (llm or {}).get("계약목적물_세부품명번호") if llm else rx["계약목적물_세부품명번호"]
        uninformed = bool(re.search(r"명시되지|없어|없음|불가|알 수 없|확인할 수 없|포함되어 있지", str(item.get("계약목적물_요약") or "")))
        veto = item["세부품명번호"] == "해당없음" and not uninformed   # 과업 정보가 없어 못 고른 경우는 거부권 없음
        code = "해당없음" if veto else (base or "해당없음")
        if code == "해당없음" and (meta_designated_competitive(rec) or meta_event_license(rec)) and table.get(str(item["세부품명번호"])):
            # meta가 지정 경쟁제품이라고 적었는데 본 호출만 품목을 못 고른 경우(dev DEV-061)
            code = str(item["세부품명번호"])
        rx["계약목적물_세부품명번호"] = code
        if llm:
            llm["계약목적물_세부품명번호"] = code
    # 물품 공고(전용 품목 호출이 없는 경우)에서 메타 `세부품명번호목록`에 경쟁제품 코드가 있으면
    # 본 호출 LLM의 '해당없음'보다 메타를 믿는다. v11·v13은 `ITEM_SOURCE`가 llm이라 LLM이 품목을
    # 못 고르면 그대로 놓쳤다(무라벨 750건 중 6건, 1,853건 환산 15건).
    if not needs_item_call(rec):
        mcodes = [c for c in meta_item_codes(rec) if c in table]
        if mcodes:
            cur = (llm or {}).get("계약목적물_세부품명번호") if llm else None
            if not cur or cur not in table:
                if llm is not None:
                    llm["계약목적물_세부품명번호"] = mcodes[0]
                if rx.get("계약목적물_세부품명번호") not in table:
                    rx["계약목적물_세부품명번호"] = mcodes[0]

    if policy is not None:                       # 평가용: 모든 사실에 같은 출처 정책을 적용
        hits = judge(rec, merge_facts(llm, rx, policy), table)
    else:
        by_mode = {mode: judge(rec, merge_facts(llm, rx, _mode_policy(mode)), table)
                   for mode in set(ITEM_SOURCE.values())}
        hits = {k: by_mode[ITEM_SOURCE[k]][k] for k in ITEMS}
    src = full_text(rec)
    evid = {k: (evidence_for(k, rec, llm, rx, src) if hits[k] else "") for k in ITEMS}
    return hits, evid, parsed_main


def to_row(rec_id: str, hits: Dict[str, int], evid: Dict[str, str]) -> Dict[str, Any]:
    row = {"id": rec_id}
    for i, v in enumerate(ITEMS, 1):
        row[v] = int(hits[v])
        row[f"e{i}"] = evid.get(v, "") if hits[v] else ""
    return row


# ===== 10. submission.csv 저장·자가검증 =====
def write_csv(rows: List[Dict[str, Any]], path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: unicodedata.normalize("NFC", str(r[k])) for k in COLUMNS})


def validate_csv(path: str, expected_ids: List[str]) -> List[str]:
    errs: List[str] = []
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        rd = csv.reader(f)
        header = next(rd, None)
        rows = list(rd)
    if header != COLUMNS:
        return [f"헤더 불일치: {len(header or [])}열 (기대 {len(COLUMNS)})"]
    if len(rows) != len(expected_ids):
        errs.append(f"행 수 {len(rows)} ≠ 입력 {len(expected_ids)}")
    ids = [r[0] for r in rows]
    if len(set(ids)) != len(ids):
        errs.append("id 중복")
    if set(ids) != set(expected_ids):
        errs.append(f"id 집합 불일치 (누락 {len(set(expected_ids) - set(ids))})")
    absence_idx = {COLUMNS.index("e" + v[1:]) for v in ABSENCE}
    for r in rows:
        if len(r) != len(COLUMNS):
            errs.append(f"{r[0]}: 열 수 {len(r)}")
            continue
        if any(x not in ("0", "1") for x in r[1:25]):
            errs.append(f"{r[0]}: 위반여부에 0/1 아닌 값")
        if any(len(x) > EVIDENCE_MAX for x in r[25:]):
            errs.append(f"{r[0]}: 근거문구 {EVIDENCE_MAX}자 초과")
        if any(r[j] for j in absence_idx):
            errs.append(f"{r[0]}: 부재탐지 항목에 근거문구")
        if any(x.startswith(("=", "+", "@")) for x in r[25:]):
            errs.append(f"{r[0]}: 수식 접두 근거문구")
    return errs


# ===== 11. 실행 =====
def judge_all(recs, table, texts, item_texts, model_texts, sme_texts,
              perf_texts=None, region_texts=None, goods_texts=None) -> Tuple[List[Dict[str, Any]], int]:
    perf_texts = perf_texts or {}
    region_texts = region_texts or {}
    goods_texts = goods_texts or {}
    rows, parsed_ok = [], 0
    for n, rec in enumerate(recs):
        try:
            hits, evid, ok = decide(rec, texts.get(n, ""), table, item_text=item_texts.get(n, ""),
                                    model_text=model_texts.get(n, ""), sme_text=sme_texts.get(n, ""),
                                    perf_text=perf_texts.get(n, ""), region_text=region_texts.get(n, ""),
                                    goods_text=goods_texts.get(n, ""))
            parsed_ok += int(ok)
        except Exception as e:
            log(f"  ! {rec['id']} 판정 실패 → 전항목 0: {type(e).__name__}: {e}")
            hits, evid = {k: 0 for k in ITEMS}, {}
        rows.append(to_row(rec["id"], hits, evid))
    return rows, parsed_ok


def run(input_path: str, out_path: str, runner_cls, limit: Optional[int], chunk: int,
        data_dir: str, budget_s: float = BUDGET_SECONDS, skip_sme: bool = False,
        skip_focus: bool = False, **runner_kw) -> Dict[str, Any]:
    budget = Budget(budget_s)
    recs = list(iter_records(input_path, limit=limit))
    log(f"입력 {len(recs)}건 ← {input_path} · 예산 {budget.total:.0f}s")
    if not recs:
        write_csv([], out_path)
        return {"건수": 0, "자가검증": "PASS"}

    table = load_competitive_table(data_dir)
    _TABLE_CACHE.update(table)
    log(f"중기간 경쟁제품 세부품명 {len(table)}건 로드")
    law = load_sme_law(data_dir)
    perf_law = load_perf_law(data_dir)
    log(f"법령 발췌: 판로지원 시행령 {len(law)}자 · 제한기준 시행규칙 {len(perf_law)}자")

    texts: Dict[int, str] = {}
    item_texts: Dict[int, str] = {}
    model_texts: Dict[int, str] = {}
    sme_texts: Dict[int, str] = {}
    perf_texts: Dict[int, str] = {}
    region_texts: Dict[int, str] = {}
    goods_texts: Dict[int, str] = {}

    # 단계 0: 모델 없이 정규식 사실만으로 유효한 제출 파일을 먼저 만든다.
    # 이후 단계는 이 파일을 덮어쓴다 — 어느 단계에서 끊겨도 49열 CSV가 남는다.
    t0 = time.time()
    rows, _ = judge_all(recs, table, texts, item_texts, model_texts, sme_texts, perf_texts, region_texts, goods_texts)
    write_csv(rows, out_path)
    budget.stage("단계0 정규식 기준선", t0)

    t0 = time.time()
    runner = runner_cls(extraction_schema(), **runner_kw)
    log(f"모델 로드 {runner.load_seconds:.1f}s")
    budget.stage("모델 로드", t0)

    t0 = time.time()
    msgs_all, ntok, shrunk = [], [], 0
    for rec in recs:
        m, n, scale = fit_to_budget(rec, table, runner)
        msgs_all.append(m)
        ntok.append(n)
        shrunk += int(scale < 1.0)
    log(f"프롬프트 토큰 중앙값 {sorted(ntok)[len(ntok) // 2]:,} · 최대 {max(ntok):,} · 예산 축소 {shrunk}건")
    budget.stage("프롬프트 구성", t0)

    t_inf = time.time()
    # 단계 1: 본 호출(사실 추출)
    t0 = time.time()
    outs = run_stage(runner, msgs_all, chunk, budget, label="본 호출")
    texts = {i: o for i, o in enumerate(outs)}
    budget.stage("단계1 본 호출", t0)
    rows, parsed_ok = judge_all(recs, table, texts, item_texts, model_texts, sme_texts, perf_texts, region_texts, goods_texts)
    write_csv(rows, out_path)

    # 단계 2: 용역 품목 판별 전용 호출(검증된 기존 호출)
    item_idx = [i for i, rec in enumerate(recs) if needs_item_call(rec)]
    if item_idx and budget.afford(60.0):
        t0 = time.time()
        item_msgs = [build_item_messages(recs[i], table) for i in item_idx]
        outs = run_stage(runner, item_msgs, chunk, budget, item_schema(table), "품목 호출", TOKENS_ITEM)
        item_texts = {j: o for j, o in zip(item_idx, outs)}
        log(f"품목 판별 호출 {len(item_idx)}건 · 유효 {sum(1 for t in item_texts.values() if parse_facts(t))}건")
        budget.stage("단계2 품목 호출", t0)
    else:
        log(f"  ! 품목 호출 생략(예산 {budget.left():.0f}s)")

    # 단계 3: 물품 모델명 전용 호출(v9)
    model_idx = [i for i, rec in enumerate(recs) if needs_model_call(rec)]
    if model_idx and budget.afford(60.0):
        t0 = time.time()
        model_msgs = [build_model_messages(recs[i]) for i in model_idx]
        outs = run_stage(runner, model_msgs, chunk, budget, model_schema(), "모델명 호출", TOKENS_MODEL)
        model_texts = {j: o for j, o in zip(model_idx, outs)}
        log(f"모델명 판별 호출 {len(model_idx)}건 · 유효 {sum(1 for t in model_texts.values() if parse_facts(t))}건")
        budget.stage("단계3 모델명 호출", t0)
    else:
        log(f"  ! 모델명 호출 생략(예산 {budget.left():.0f}s)")

    rows, parsed_ok = judge_all(recs, table, texts, item_texts, model_texts, sme_texts, perf_texts, region_texts, goods_texts)
    write_csv(rows, out_path)

    # 단계 4: 기업규모·직접생산 전용 호출(S2) — 9개 항목의 공통 입력
    sme_idx = [i for i, rec in enumerate(recs) if needs_sme_call(rec)]
    if sme_idx and not skip_sme and budget.afford(120.0):
        t0 = time.time()
        sme_msgs = [build_sme_messages(recs[i], law) for i in sme_idx]
        stok = sorted(runner.count_tokens(m) for m in sme_msgs)
        log(f"전용 호출 프롬프트 토큰 중앙값 {stok[len(stok) // 2]:,} · 최대 {stok[-1]:,}")
        outs = run_stage(runner, sme_msgs, chunk, budget, sme_schema(), "기업규모 호출", TOKENS_SME)
        sme_texts = {j: o for j, o in zip(sme_idx, outs)}
        ok = sum(1 for t in sme_texts.values() if parse_facts(t))
        log(f"기업규모·직생 호출 {len(sme_idx)}건 · 유효 {ok}건")
        budget.stage("단계4 기업규모 호출", t0)
    else:
        log(f"  ! 기업규모 전용 호출 생략(skip={skip_sme} · 예산 {budget.left():.0f}s)")

    # 단계 5·6: 실적·지역 전용 호출 — 규칙을 대체하지 않고 OR로 더한다
    for tag, idx_fn, msg_fn, schema_fn, store, items in (
            ("실적", needs_perf_call, lambda r: build_perf_messages(r, perf_law), perf_schema, perf_texts, "v2·v3·v4·v8"),
            ("지역", needs_region_call, lambda r: build_region_messages(r, perf_law), region_schema, region_texts, "v5~v8")):
        stage_tokens = TOKENS_REGION if tag == "지역" else 400
        idx = [i for i, rec in enumerate(recs) if idx_fn(rec)]
        if not idx or skip_focus or not budget.afford(120.0):
            log(f"  ! {tag} 전용 호출 생략(skip={skip_focus} · 예산 {budget.left():.0f}s)")
            continue
        t0 = time.time()
        msgs = [msg_fn(recs[i]) for i in idx]
        ntk = sorted(runner.count_tokens(m) for m in msgs)
        log(f"{tag} 전용 호출 프롬프트 토큰 중앙값 {ntk[len(ntk) // 2]:,} · 최대 {ntk[-1]:,}")
        outs = run_stage(runner, msgs, chunk, budget, schema_fn(), f"{tag} 호출", stage_tokens)
        store.update({j: o for j, o in zip(idx, outs)})
        log(f"{tag} 전용 호출 {len(idx)}건 · 유효 {sum(1 for t in store.values() if parse_facts(t))}건 ({items})")
        budget.stage(f"단계 {tag} 호출", t0)

    # 단계 7: 물품 품목 전용 호출 — 후보 생성기 recall 33% → 74% 개선을 실제 선택으로 잇는다
    gidx = [i for i, rec in enumerate(recs) if needs_goods_item_call(rec)]
    if gidx and not skip_focus and budget.afford(90.0):
        t0 = time.time()
        gmsgs = [build_goods_item_messages(recs[i], table) for i in gidx]
        # 후보 목록이 공고마다 달라 스키마도 공고마다 다르다 → 건별로 호출한다
        gouts: List[str] = []
        for i, m in zip(gidx, gmsgs):
            gouts.extend(run_chunk(runner, [m], goods_item_schema(goods_candidates(recs[i], table)), TOKENS_ITEM))
            if len(gouts) % 64 == 0 and not budget.afford(60.0):
                log(f"  ! 물품 품목 호출 예산 부족 → 남은 {len(gidx) - len(gouts)}건 생략")
                gouts.extend("" for _ in range(len(gidx) - len(gouts)))
                break
        goods_texts.update({j: o for j, o in zip(gidx, gouts)})
        log(f"물품 품목 전용 호출 {len(gidx)}건 · 유효 {sum(1 for t in goods_texts.values() if parse_facts(t))}건 (v10~v18)")
        budget.stage("단계 물품품목 호출", t0)
    else:
        log(f"  ! 물품 품목 전용 호출 생략(예산 {budget.left():.0f}s)")

    inf_seconds = time.time() - t_inf

    rows, parsed_ok = judge_all(recs, table, texts, item_texts, model_texts, sme_texts, perf_texts, region_texts, goods_texts)
    assert len(rows) == len(recs)
    write_csv(rows, out_path)
    errs = validate_csv(out_path, [r["id"] for r in recs])
    positives = {v: sum(r[v] for r in rows) for v in ITEMS}
    report = {
        "건수": len(recs), "모델로드_s": round(runner.load_seconds, 1), "추론_s": round(inf_seconds, 1),
        "전체_s": round(budget.elapsed(), 1), "유효JSON": parsed_ok,
        "전용호출_유효": {"기업규모": sum(1 for t in sme_texts.values() if parse_facts(t)),
                          "실적": sum(1 for t in perf_texts.values() if parse_facts(t)),
                          "지역": sum(1 for t in region_texts.values() if parse_facts(t)),
                          "물품품목": sum(1 for t in goods_texts.values() if parse_facts(t))},
        "단계별_s": dict(budget.stages), "항목별_양성": positives,
        "출력": out_path, "자가검증": "PASS" if not errs else errs[:20],
    }
    log(json.dumps(report, ensure_ascii=False))
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="사실 추출 + 법령 판정기")
    ap.add_argument("--data-dir", default=DATA_DIR)
    ap.add_argument("--output-dir", default=OUTPUT_DIR)
    ap.add_argument("--input", default=None, help="기본 = <data-dir>/test.jsonl.gz")
    ap.add_argument("--model-dir", default=MODEL_DIR)
    ap.add_argument("--quantization", default=os.environ.get("PPS_QUANT", QUANT))
    ap.add_argument("--gpu-mem", type=float, default=0.92)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--chunk", type=int, default=128)
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--budget-s", type=float, default=BUDGET_SECONDS, help="추론 총 예산(초). 초과 예상 시 뒤 단계를 생략한다")
    ap.add_argument("--skip-sme", action="store_true", help="기업규모·직생 전용 호출을 끈다(A/B 비교용)")
    ap.add_argument("--skip-focus", action="store_true", help="실적·지역 전용 호출을 끈다(A/B 비교용)")
    a = ap.parse_args()

    input_path = a.input or os.path.join(a.data_dir, "test.jsonl.gz")
    out_path = os.path.join(a.output_dir, "submission.csv")
    quant = None if str(a.quantization).lower() in ("none", "") else a.quantization
    runner_kw = {} if a.mock else dict(model_dir=a.model_dir, quant=quant, max_tokens=a.max_tokens,
                                       seed=SEED, gpu_mem=a.gpu_mem, tp=a.tp)
    report = run(input_path, out_path, MockRunner if a.mock else VLLMRunner,
                 limit=a.limit, chunk=a.chunk, data_dir=a.data_dir,
                 budget_s=a.budget_s, skip_sme=a.skip_sme, skip_focus=a.skip_focus, **runner_kw)
    return 0 if report.get("자가검증") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
