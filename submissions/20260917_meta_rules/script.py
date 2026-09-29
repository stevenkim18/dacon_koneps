#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""나라장터 자체입찰 공고 법령 위반사항 모니터링 AI 경진대회 — meta_rules 변형.

submissions/20260916_attachment_excerpt에 아래 4·5를 추가한 버전이다. 시스템 프롬프트,
모델 호출 방식은 attachment_excerpt와 동일하고 후처리(`postprocess`)만 바뀌었다.

4. 금액 구간·업무구분 게이트(`meta_gate`): 고시금액 2.3억·1억 구간이나 물품 여부가
   항목명에 명시된 v2·v5·v9·v13~v19는 조건을 벗어나면 0. dev 200건 양성 중 막히는 건 0건.
5. 판로지원법 항목 규칙 판정(`sme_rule_hits`): v14·v15·v16·v18을 금액 구간 + 중소기업·
   소기업 제한 여부로 판정해 모델 판정과 OR로 합친다.

아래 1~3은 attachment_excerpt에서 이어진 내용이다.

공식 베이스라인(open/baseline/script.py)에 다음 세 가지를 추가한다. 시스템 프롬프트,
모델 호출 방식, JSON 파싱, CSV 저장·자가검증은 베이스라인과 완전히 동일하다.

1. 공고문 4,000자는 그대로 두고, 첨부문서(규격서·과업지시서·제안요청서·예외공표서)에서
   항목 판단에 쓰일 만한 구간만 최대 약 1,000자 짧게 발췌해 덧붙인다(`attachment_excerpts`).
   dev 128건 로컬 MLX 검증: v9(과업지시서 모델명) recall 0%→83%.
2. v22·v23 메타 적용 조건 후처리(`_gate_v22`/`_gate_v23`): 항목표.json의 항목명은
   "계약방법 협상"이라 적혀 있지만 실제 조건은 `낙찰방법=='협상에의한계약'`(v23은 추가로
   `적용계약법=='지방계약법'`)이다. dev 200건 정답 전수 검증 결과 이 조건을 벗어난 양성은
   0건이므로, 벗어나면 0으로 강제해도 재현율 손실이 없다.
3. v13 세부품명번호 대조(`load_sme_competitive_codes`): "소기업·소상공인 확인서 소지자에
   한함" 문구만으로는 v13이 성립하지 않는다 — 그 품목이 법령패키지의 중기간 경쟁제품
   목록에 있을 때만 위반이다. dev 오탐 24건 중 세부품명번호가 있던 13건은 전부 목록 밖
   품목이었고, 진짜 양성 6건은 전부 세부품명번호가 메타에 없어 이 규칙에 걸리지 않는다.

근거: docs/05_study_log/20260917/ 의 재분석 기록.
(배경: submissions/20260916_balanced_context는 문서 예산·법령 조문명·보수적 0 지시를
한 번에 바꿔 원인을 분리할 수 없었다. 이번 세 가지는 각각 독립적으로 검증된 변경이다.)

평가 서버는 이 파일을 `python script.py`로 그대로 실행합니다.
  입력   ./data/test.jsonl.gz (+ 항목표.json · 정답스키마_디코딩.json)
  출력   ./output/submission.csv  (열 = id, v1..v24, e1..e24)
         v = 위반 여부 0/1, e = 근거 문구(원문 부분문자열, 비위반은 빈칸)
  경로   PPS_DATA_DIR · PPS_OUTPUT_DIR · PPS_MODEL_DIR 환경변수 우선

전체 흐름
  데이터 로드 → 프롬프트 구성(공고문 4,000자 + 첨부 발췌 ~1,000자) → vLLM 배치 추론
  → JSON 파싱 → 근거 문구 검증 → submission.csv 저장 → 형식 검증

로컬 실행
  python script.py --mock          # 모델 없이 입력·출력 흐름 확인
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
from collections import Counter
from typing import Any, Dict, Iterator, List, Optional, Tuple

DATA_DIR = os.environ.get("PPS_DATA_DIR", "./data")
OUTPUT_DIR = os.environ.get("PPS_OUTPUT_DIR", "./output")
MODEL_DIR = os.environ.get("PPS_MODEL_DIR", "/opt/models/gemma-4-26B-A4B-it")

ITEMS = [f"v{i}" for i in range(1, 25)]
EVID = [f"e{i}" for i in range(1, 25)]
COLUMNS = ["id"] + ITEMS + EVID
ABSENCE = ["v10", "v11", "v16", "v18", "v20"]          # 부재탐지 항목: 근거 문구 빈칸

DOC_ORDER = ["공고문", "규격서", "과업지시서", "제안요청서", "예외공표서", "기타"]
META_FIELDS = [
    "적용계약법", "업무구분", "계약방법", "낙찰방법", "낙찰하한율",
    "배정예산금액", "입찰추정가격", "소관구분", "공동도급구성방식", "정보화사업여부",
    "세부품명번호목록", "제한지역코드목록", "지역제한여부", "면허업종제한목록", "업종제한여부",
    "조항호내용", "공고게시일자", "개찰예정일자", "긴급공고여부", "입찰방법", "조달방식",
]

SEED = 20260826
MAX_MODEL_LEN = 16384                   # 베이스라인 모델 컨텍스트 길이
MAX_TOKENS = 1536                       # 구조화 출력 토큰 예산
PROMPT_BUDGET = MAX_MODEL_LEN - MAX_TOKENS
EVIDENCE_MAX = 500                      # 근거 문구 셀 글자 수 상한
QUANT = "int8_per_channel_weight_only"  # 평가 서버 양자화 설정


def log(msg: str) -> None:
    print(f"[baseline] {msg}", file=sys.stderr, flush=True)


# ===== 2. 데이터 로더 =====
def _open(path: str):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return io.open(path, "r", encoding="utf-8")


def validate_record(rec: Any) -> None:
    """레코드 1건의 최소 스키마 검사 (id · docs(공고문 1개 이상) · meta)"""
    if not isinstance(rec, dict):
        raise ValueError(f"레코드가 object가 아니다: {type(rec).__name__}")
    for k in ("id", "docs", "meta"):
        if k not in rec:
            raise ValueError(f"필수 키 없음: {k}")
    if not isinstance(rec["id"], str) or not rec["id"]:
        raise ValueError("id가 비어 있다")
    docs = rec["docs"]
    if not isinstance(docs, list) or not docs:
        raise ValueError(f"docs가 비어 있다 (id={rec['id']})")
    for d in docs:
        if not isinstance(d, dict) or not all(k in d for k in ("doc_id", "type", "text")):
            raise ValueError(f"docs 원소 형식 오류 (id={rec['id']})")
        if not isinstance(d["text"], str):
            raise ValueError(f"docs.text가 문자열이 아니다 (id={rec['id']})")
    if not any(d["type"] == "공고문" for d in docs):
        raise ValueError(f"공고문이 없다 (id={rec['id']})")
    if not isinstance(rec["meta"], dict):
        raise ValueError(f"meta가 object가 아니다 (id={rec['id']})")


def normalize(rec: Dict[str, Any]) -> Dict[str, Any]:
    """NFC 정규화 — macOS에서 만든 파일은 한글이 NFD로 저장될 수 있어 문자열 비교가 어긋날 수 있습니다."""
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
    """근거문구 대조용 원문 (프롬프트에 넣은 것과 같은 텍스트 · NFC)"""
    return "\n".join(d["text"] for d in rec["docs"])


def build_context(rec: Dict[str, Any], max_chars: int = 4000) -> str:
    """문서를 프롬프트용 텍스트로 구성합니다.

    공고문을 먼저 배치하고, 나머지 문서는 DOC_ORDER 순서를 따릅니다. `max_chars`를 초과하면
    뒤쪽 문서부터 제외하고 '[미수록 문서]'로 표시합니다. 첫 문서는 길이 상한에 맞게 자릅니다.
    """
    order = {t: i for i, t in enumerate(DOC_ORDER)}
    pool = sorted(rec["docs"], key=lambda d: (order.get(d["type"], len(DOC_ORDER)), d["doc_id"]))

    chunks, used, dropped, truncated = [], 0, Counter(), False
    for i, d in enumerate(pool):
        head = f"[{d['type']}:{d['doc_id']}]\n"
        body = d["text"]
        if used + len(head) + len(body) > max_chars:
            if i == 0:                                   # 첫 문서는 길이 상한에 맞게 자릅니다.
                body = body[: max(0, max_chars - len(head))]
                truncated = True
            else:
                dropped[d["type"]] += 1
                continue
        chunks.append(head + body)
        used += len(head) + len(body)

    for t, n in (rec.get("dropped_doc_counts") or {}).items():
        dropped[t] += n

    text = "\n\n".join(chunks)
    if truncated:
        text += "\n\n[절단] 공고문 뒷부분이 길이 예산으로 잘렸다"
    if dropped:
        text += "\n\n[미수록 문서] " + ", ".join(f"{t} {n}건" for t, n in sorted(dropped.items()))
    return text


ATTACH_TYPES = ("규격서", "과업지시서", "제안요청서", "예외공표서")
# v9(과업지시서 특정 모델명) · v19(확약서) · v22·v23(현장설명회) · v10·v11·v12(직접생산) ·
# v20(SW 사업자) · v13(중기간 경쟁제품)처럼 첨부에서만 확인되는 항목을 겨냥한 앵커.
ATTACH_ANCHORS = ["모델명", "규격", "제품명", "확약서", "현장설명회",
                   "직접생산", "소프트웨어사업자", "중소기업자간 경쟁제품"]
MODEL_CODE_RE = re.compile(r"[A-Za-z]{1,10}[-_/]?\d{2,6}[A-Za-z0-9-]*")
EXCERPT_WINDOW = 120     # 앵커 앞뒤로 자르는 글자 수
EXCERPT_PAD = 40         # 모델 코드류 앞뒤 여백(앵커보다 좁게)
ATTACHMENT_BUDGET_RATIO = 4   # max_chars // 4 ≈ 기본 4,000자 기준 첨부 발췌 1,000자


def _excerpt_spans(text: str, budget: int) -> List[Tuple[int, int]]:
    """앵커 키워드·모델 코드 주변 구간을 찾아 겹치면 합치고, 예산 안에서 자릅니다.
    앵커가 하나도 없으면 문서 서두만 짧게 보여줍니다(첨부 존재 자체는 드러내되 과다 인용은 피함)."""
    hits: List[Tuple[int, int]] = []
    for kw in ATTACH_ANCHORS:
        i = text.find(kw)
        if i >= 0:
            hits.append((max(0, i - EXCERPT_WINDOW), min(len(text), i + len(kw) + EXCERPT_WINDOW)))
    for m in MODEL_CODE_RE.finditer(text):
        hits.append((max(0, m.start() - EXCERPT_PAD), min(len(text), m.end() + EXCERPT_PAD)))
        if len(hits) >= 12:                          # 과도한 코드 매치 방지
            break
    if not hits:
        return [(0, min(len(text), 200))]
    hits.sort()
    merged = [hits[0]]
    for s, e in hits[1:]:
        ls, le = merged[-1]
        if s <= le + 20:                              # 20자 이내로 붙어 있으면 이어 붙인다
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s, e))
    spans, used = [], 0
    for s, e in merged:
        if used >= budget:
            break
        e = min(e, s + (budget - used))
        if e > s:
            spans.append((s, e))
            used += e - s
    return spans


def attachment_excerpts(rec: Dict[str, Any], budget: int) -> str:
    """첨부문서(규격서·과업지시서·제안요청서·예외공표서)에서 항목 판단에 쓰일 구간만
    짧게 발췌합니다. `build_context`가 다루는 공고문 예산과는 별개의 예산을 씁니다."""
    if budget <= 0:
        return ""
    docs = [d for d in rec["docs"] if d["type"] in ATTACH_TYPES]
    if not docs:
        return ""
    order = {t: i for i, t in enumerate(DOC_ORDER)}
    docs = sorted(docs, key=lambda d: (order.get(d["type"], len(DOC_ORDER)), d["doc_id"]))
    per_doc = max(150, budget // len(docs))
    parts, used = [], 0
    for d in docs:
        if used >= budget:
            break
        remain = min(per_doc, budget - used)
        spans = _excerpt_spans(d["text"], remain)
        body = " […] ".join(d["text"][s:e] for s, e in spans)
        if not body:
            continue
        head = f"[{d['type']}:{d['doc_id']} 발췌]\n"
        parts.append(head + body)
        used += len(head) + len(body)
    if not parts:
        return ""
    return "[첨부 발췌]\n" + "\n\n".join(parts)


def format_meta(rec: Dict[str, Any]) -> str:
    """나라장터 메타를 한 줄짜리 목록으로. 값이 없는 필드는 '미기재'로 표시합니다."""
    m = rec.get("meta", {})
    lines = []
    for k in META_FIELDS:
        if k in m:
            v = m[k]
            lines.append(f"- {k}: {'미기재' if v is None else v}")
    return "\n".join(lines)


# ===== 3. 항목표·디코딩 스키마 =====
# data/에 항목표.json·정답스키마_디코딩.json이 동봉됩니다.
# 항목명·근거조문·비고는 항목표.json 에 있으니 여기에 사본을 두지 않습니다.


def item_table(data_dir: str = DATA_DIR) -> Dict[str, Dict[str, Any]]:
    p = os.path.join(data_dir, "항목표.json")
    if not os.path.exists(p):
        raise FileNotFoundError(f"{p} 가 없습니다 — data/ 를 그대로 둔 채 실행하세요.")
    return json.load(io.open(p, encoding="utf-8"))["항목"]


def decode_schema(data_dir: str = DATA_DIR) -> Dict[str, Any]:
    """베이스라인의 구조화 출력에 사용할 JSON Schema를 불러옵니다."""
    p = os.path.join(data_dir, "정답스키마_디코딩.json")
    if os.path.exists(p):
        s = json.load(io.open(p, encoding="utf-8"))
        return s["properties"]["판정"] if "판정" in s.get("properties", {}) else s
    props = {}
    for v in ITEMS:
        props[v] = {
            "type": "object", "additionalProperties": False,
            "required": ["위반여부", "근거문구"],
            "properties": {
                "위반여부": {"type": "integer", "enum": [0, 1]},
                "근거문구": {"type": "null"} if v in ABSENCE else {"type": ["string", "null"]},
            },
        }
    return {"type": "object", "additionalProperties": False, "required": list(ITEMS), "properties": props}


# ===== 4. 프롬프트 구성 =====
# 베이스라인 프롬프트는 출력 형식과 항목 목록을 구성합니다.
SYSTEM_HEAD = """당신은 공공 입찰공고의 법령 위반 여부를 점검한다.
공고문과 첨부 문서, 그리고 나라장터 입력 메타를 함께 읽고 아래 24개 항목 각각에 대해
위반 여부(1/0)와 근거 문구를 판정한다.

지켜야 할 것
1. 24개 항목 전부에 답한다. 판단이 어려운 항목도 비워 두지 말고 0으로 낸다.
2. 근거 문구는 반드시 **주어진 문서에 그대로 있는 문장**을 옮긴다. 요약하거나 고쳐 쓰지 않는다.
   원문에 없는 문구는 근거로 인정되지 않는다. 500자를 넘기지 않는다.
3. 아래 '근거 없음' 표시가 붙은 항목은 **있어야 할 문구가 없는 것**이 위반이다.
   인용할 원문이 존재하지 않으므로 근거 문구를 null로 둔다.

판정할 24개 항목"""

SYSTEM_TAIL = """
출력은 JSON 하나로만 낸다. 키는 v1~v24, 각 값은 {"위반여부": 0 또는 1, "근거문구": 문자열 또는 null}이다.
설명이나 머리말을 덧붙이지 않는다."""


def build_system_prompt(tbl: Dict[str, Dict[str, Any]]) -> str:
    lines = []
    for v in ITEMS:
        it = tbl[v]
        tag = "  [근거 없음 — null]" if it["부재탐지"] else ""
        note = f" ({it['비고']})" if it.get("비고") else ""
        lines.append(f"- {v}: {it['항목명']}{note}{tag}")
    return SYSTEM_HEAD + "\n" + "\n".join(lines) + "\n" + SYSTEM_TAIL


def build_user_prompt(rec: Dict[str, Any], max_chars: int) -> str:
    """공고문(max_chars, 베이스라인과 동일)에 첨부 발췌(별도의 작은 예산)를 덧붙입니다.
    fit_to_budget이 max_chars를 줄이면 첨부 예산도 같은 비율로 함께 줄어듭니다."""
    doc_block = build_context(rec, max_chars=max_chars)
    attach = attachment_excerpts(rec, budget=max(0, max_chars // ATTACHMENT_BUDGET_RATIO))
    if attach:
        doc_block = doc_block + "\n\n" + attach
    return (
        f"[공고 ID] {rec['id']}\n\n"
        f"[나라장터 입력 메타]\n{format_meta(rec)}\n\n"
        f"[문서]\n{doc_block}\n"
    )


def build_messages(rec: Dict[str, Any], system_prompt: str, max_chars: int) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": build_user_prompt(rec, max_chars)},
    ]


# ===== 5. 모델 러너 (vLLM offline / mock) =====
class VLLMRunner:
    """평가 서버의 모델을 vLLM offline API로 실행합니다."""

    def __init__(self, schema: Dict[str, Any], model_dir: str = MODEL_DIR, quant: Optional[str] = QUANT,
                 max_tokens: int = MAX_TOKENS, seed: int = SEED, gpu_mem: float = 0.92, tp: int = 1):
        t0 = time.time()
        import vllm                                    # --mock 실행 시 vllm이 없어도 되도록 지연 import
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
            if hasattr(ids, "keys") and "input_ids" in ids:   # transformers 버전에 따라 dict가 반환되는 경우
                ids = ids["input_ids"]
            return len(ids)
        except Exception:
            return len(self.tok.encode("\n".join(m["content"] for m in messages)))

    def chat(self, batch: List[List[Dict[str, str]]]) -> List[str]:
        outs = self.llm.chat(batch, sampling_params=self.sp, use_tqdm=False)
        return [o.outputs[0].text if o.outputs else "" for o in outs]


class MockRunner:
    """모델 없이 입력·출력 및 제출 형식을 확인합니다."""
    load_seconds = 0.0

    def __init__(self, schema: Dict[str, Any], **_):
        pass

    def count_tokens(self, messages: List[Dict[str, str]]) -> int:
        return sum(len(m["content"]) for m in messages) // 2     # Mock 실행용 간이 추정치

    def _one(self, _messages: List[Dict[str, str]]) -> str:
        out = {v: {"위반여부": 0, "근거문구": None} for v in ITEMS}
        return json.dumps(out, ensure_ascii=False)

    def chat(self, batch: List[List[Dict[str, str]]]) -> List[str]:
        return [self._one(m) for m in batch]


def fit_to_budget(rec: Dict[str, Any], system_prompt: str, runner, max_chars: int,
                  budget: int = PROMPT_BUDGET) -> Tuple[List[Dict[str, str]], int, int]:
    """설정된 토큰 예산에 맞게 문서 글자 수를 조정합니다."""
    while True:
        msgs = build_messages(rec, system_prompt, max_chars)
        n = runner.count_tokens(msgs)
        if n <= budget or max_chars <= 2000:
            return msgs, n, max_chars
        max_chars = int(max_chars * min(0.85, budget / n * 0.95))


def run_chunk(runner, batch: List[List[Dict[str, str]]]) -> List[str]:
    """배치 실패 시 건별로 재시도하고, 처리하지 못한 건은 빈 출력으로 반환합니다."""
    try:
        return runner.chat(batch)
    except Exception as e:
        log(f"  ! 청크({len(batch)}건) 실패 → 건 단위 재시도: {type(e).__name__}: {str(e)[:160]}")
    outs = []
    for m in batch:
        try:
            outs.append(runner.chat([m])[0])
        except Exception as e:
            log(f"  ! 건 단위 실패 → 빈 출력: {type(e).__name__}: {str(e)[:160]}")
            outs.append("")
    return outs


# ===== 6. 파싱·후처리 =====
FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)


def extract_json(text: str) -> Optional[Any]:
    text = (text or "").strip()
    if not text:
        return None
    for cand in (text, *(m.group(1) for m in FENCE.finditer(text))):
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            pass
    i, j = text.find("{"), text.rfind("}")
    if i >= 0 and j > i:
        try:
            return json.loads(text[i:j + 1])
        except json.JSONDecodeError:
            return None
    return None


def parse_judgment(text: str) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    """모델 출력을 24항목 판정으로 정리합니다. 빠진 항목은 0/None으로 채우고 결손 목록을 함께 반환합니다."""
    obj = extract_json(text)
    if isinstance(obj, dict) and isinstance(obj.get("판정"), dict):
        obj = obj["판정"]
    out, missing = {}, []
    for v in ITEMS:
        raw = obj.get(v) if isinstance(obj, dict) else None
        if not isinstance(raw, dict):
            missing.append(v)
            out[v] = {"위반여부": 0, "근거문구": None}
            continue
        hit = raw.get("위반여부", raw.get("violation", 0))
        if isinstance(hit, bool):
            hit = int(hit)
        if isinstance(hit, str):
            hit = 1 if hit.strip() in ("1", "위반", "true", "True") else 0
        if hit not in (0, 1):
            hit = 1 if hit else 0
        ev = raw.get("근거문구", raw.get("evidence"))
        if ev is not None and not isinstance(ev, str):
            ev = str(ev)
        out[v] = {"위반여부": int(hit), "근거문구": ev}
    return out, missing


def clean_evidence(ev: Optional[str], src: str) -> str:
    """근거문구 셀 규약: NFC · 앞뒤 공백 제거 · 500자 상한 · 수식 접두(=,+,@)면 빈칸 ·
    원문 부분문자열이 아니면 빈칸(원문에 없는 근거는 채점에서 인정되지 않습니다)."""
    if not ev:
        return ""
    ev = unicodedata.normalize("NFC", ev).replace("\r", "").strip()
    if not ev or ev[0] in "=+@":
        return ""
    ev = ev[:EVIDENCE_MAX]
    return ev if ev in src else ""


# ===== 6-1. 메타 기반 결정론적 후처리 규칙 (dev 200건 정답 전수로 검증) =====
# 근거: docs/05_study_log/20260917/2. dev_reanalysis_v13_v22_v23.md
#
# v22·v23: 항목표.json의 항목명은 "계약방법 협상"이라고 적혀 있지만, dev 200건에는
# `계약방법` 필드에 '협상'이라는 값 자체가 없다(제한경쟁/수의계약/일반경쟁뿐). 실제
# 적용 조건은 `낙찰방법=='협상에의한계약'`이며(v23은 추가로 `적용계약법=='지방계약법'`),
# dev 200건 양성 전부(v22 5건·v23 5건)가 이 조건을 만족하고 예외는 0건이었다.
# → 조건을 벗어나면 위반이 아니라고 "확정"할 수 있으므로 0으로 강제해도 재현율 손실이 없다.
ITEM_CODE_RE = re.compile(r"\[(\d+)\]")


def _meta_item_codes(rec: Dict[str, Any]) -> List[str]:
    raw = rec.get("meta", {}).get("세부품명번호목록")
    return ITEM_CODE_RE.findall(raw) if isinstance(raw, str) else []


def _gate_v22(rec: Dict[str, Any]) -> bool:
    return rec.get("meta", {}).get("낙찰방법") == "협상에의한계약"


def _gate_v23(rec: Dict[str, Any]) -> bool:
    return _gate_v22(rec) and rec.get("meta", {}).get("적용계약법") == "지방계약법"


def load_sme_competitive_codes(data_dir: str = DATA_DIR) -> set:
    """법령패키지의 중기간 경쟁제품 세부품명번호 목록(v13 오탐 억제용).

    v13(중기간 경쟁제품 소기업·소상공인 제한)은 "소기업·소상공인 확인서 소지자에 한함"
    같은 문구만으로는 성립하지 않는다 — 그 품목이 이 목록에 등재된 중기간 경쟁제품일
    때만 위반이다(일반물품이면 다른 조항 대상이거나 적법한 예외일 수 있다). dev 오탐
    24건 중 세부품명번호가 있던 13건은 전부 이 목록에 없는 품목이었고, 진짜 양성 6건은
    전부 세부품명번호가 메타에 없어(None) 이 규칙으로 걸러지지 않는다(재현율 손실 없음).
    파일이 없거나 형식이 다르면 빈 집합을 반환해 판정에 영향을 주지 않는다."""
    p = os.path.join(data_dir, "법령패키지", "중기부고시", "중기부고시_경쟁제품_세부품명.csv")
    codes = set()
    try:
        with io.open(p, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                c = (row.get("세부품명번호") or "").strip()
                if c:
                    codes.add(c)
    except OSError:
        pass
    return codes


# ===== 6-2. 금액 구간·업무구분 게이트와 판로지원법 항목 규칙 판정 =====
# 근거: docs/05_study_log/20260917/3. meta_price_gates_and_sme_rules.md
#
# 고시금액(법령패키지 "재정경제부장관이 정하는 고시금액"): 물품·용역 2억 3천만 원.
# 항목명에 금액 구간·대상이 명시된 항목은 구간을 벗어나면 위반이 성립하지 않는다.
# dev 200건 정답 전수 대조 결과 아래 게이트에 막히는 양성은 0건이었다.
NOTICE_AMOUNT = 230_000_000
ONE_HUNDRED_MILLION = 100_000_000


def _price(rec: Dict[str, Any]) -> Optional[float]:
    p = rec.get("meta", {}).get("입찰추정가격")
    try:
        return float(p) if p is not None and p != "" else None
    except (TypeError, ValueError):
        return None


def _goods(rec: Dict[str, Any]) -> bool:
    return "물품" in str(rec.get("meta", {}).get("업무구분") or "")


def meta_gate(v: str, rec: Dict[str, Any]) -> bool:
    """False면 이 공고에서 항목 v는 위반이 성립할 수 없다. 메타가 비어 있으면 막지 않는다."""
    p = _price(rec)
    if v in ("v9", "v19"):                       # 과업지시서 모델명·물품공급 확약서: 물품 공고
        return _goods(rec) if rec.get("meta", {}).get("업무구분") else True
    if p is None:
        return True
    if v in ("v2", "v13"):                       # 고시금액 미만
        return p < NOTICE_AMOUNT
    if v in ("v5", "v14"):                       # 고시금액 이상
        return p >= NOTICE_AMOUNT
    if v in ("v15", "v16"):                      # 1억 이상 ~ 고시금액 미만
        return ONE_HUNDRED_MILLION <= p < NOTICE_AMOUNT
    if v in ("v17", "v18"):                      # 1억 미만
        return p < ONE_HUNDRED_MILLION
    return True


# 판로지원법 계열(v14·v15·v16·v18)은 모델이 거의 잡지 못한다(로컬 MLX F1 0). 금액 구간과
# 중소기업·소기업 제한 여부만으로 판정하는 규칙의 dev 200건 결과:
#   v14 고시금액 이상 + 조항호내용에 중소기업 제한 → F1 0.36 (tp 4, fp 10)
#   v15 1억~고시금액 + 조항호내용에 소기업·소상공인 제한(중기업 제외) → F1 0.33 (tp 2, fp 4)
#   v16 1억~고시금액 + 본문에 중소기업·소기업 제한 문구 없음 → F1 0.50 (tp 3, fp 3)
#   v18 1억 미만 + 본문에 소기업·소상공인 문구 없음 → F1 0.43 (tp 3, fp 4)
# 규칙과 평가가 같은 dev라 낙관적 추정이다. v17은 쓸 만한 규칙이 없어 제외했다.
SMALL_RE = re.compile(r"소기업|소상공인")
SME_RE = re.compile(r"중소기업(자)?(?!.{0,5}경쟁제품)")
SME_EVIDENCE_RE = re.compile(r"[^\n]*(?:중소기업|소기업|소상공인)[^\n]*")


def sme_rule_hits(rec: Dict[str, Any], src: str) -> Dict[str, int]:
    p = _price(rec)
    if p is None:
        return {}
    clause = str(rec.get("meta", {}).get("조항호내용") or "")
    clause_any = any(k in clause for k in ("소기업", "중기업", "중소기업"))
    clause_small_only = "소기업" in clause and "중기업" not in clause
    ge = p >= NOTICE_AMOUNT
    mid = ONE_HUNDRED_MILLION <= p < NOTICE_AMOUNT
    lt1 = p < ONE_HUNDRED_MILLION
    has_small = bool(SMALL_RE.search(src))
    return {
        "v14": int(ge and clause_any),
        "v15": int(mid and clause_small_only),
        "v16": int(mid and not has_small and not SME_RE.search(src)),
        "v18": int(lt1 and not has_small),
    }


def sme_rule_evidence(src: str) -> str:
    """규칙으로 켠 v14·v15의 근거 후보: 중소기업·소기업 제한이 나온 첫 줄(원문 그대로)."""
    m = SME_EVIDENCE_RE.search(src)
    return m.group(0).strip()[:EVIDENCE_MAX] if m else ""


def postprocess(judgment: Dict[str, Dict[str, Any]], rec: Dict[str, Any],
                sme_codes: Optional[set] = None) -> Dict[str, Dict[str, Any]]:
    """후처리: ① 부재탐지 5항목 근거 빈칸 고정 ② 위반이 아니면 근거 빈칸 ③ 근거문구 원문 대조(NFC)
    ④ 메타로 적용 대상이 아님이 확정된 v22·v23·v13은 0으로 강제(위 근거 참고)
    ⑤ 금액 구간·업무구분 게이트 ⑥ v14·v15·v16·v18은 규칙 판정을 모델 판정에 OR로 합친다."""
    src = unicodedata.normalize("NFC", full_text(rec))
    codes = _meta_item_codes(rec)
    rules = sme_rule_hits(rec, src)
    out = {}
    for v in ITEMS:
        cell = dict(judgment.get(v, {"위반여부": 0, "근거문구": None}))
        hit = 1 if cell.get("위반여부") == 1 else 0
        if v in rules:                                   # 규칙 OR 모델(모델 판정도 아래 게이트를 거친다)
            hit = int(hit or rules[v])
        if hit == 1:
            if v == "v22" and not _gate_v22(rec):
                hit = 0
            elif v == "v23" and not _gate_v23(rec):
                hit = 0
            elif v == "v13" and sme_codes and codes and not any(c in sme_codes for c in codes):
                hit = 0
            elif not meta_gate(v, rec):
                hit = 0
        ev = "" if (hit == 0 or v in ABSENCE) else clean_evidence(cell.get("근거문구"), src)
        if hit == 1 and not ev and v in rules and v not in ABSENCE:
            ev = clean_evidence(sme_rule_evidence(src), src)
        out[v] = {"위반여부": hit, "근거문구": ev}
    return out


def to_row(rec_id: str, judgment: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row = {"id": rec_id}
    for i, v in enumerate(ITEMS, 1):
        row[v] = judgment[v]["위반여부"]
        row[f"e{i}"] = judgment[v]["근거문구"]
    return row


def empty_row(rec_id: str) -> Dict[str, Any]:
    return to_row(rec_id, {v: {"위반여부": 0, "근거문구": ""} for v in ITEMS})


# ===== 7. submission.csv 저장·자가검증 =====
def write_csv(rows: List[Dict[str, Any]], path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="") as f:   # UTF-8(BOM 없음) · RFC4180 quoting
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: unicodedata.normalize("NFC", str(r[k])) for k in COLUMNS})


def validate_csv(path: str, expected_ids: List[str]) -> List[str]:
    """자가검증: 열 49 · 행 수 = 입력 건수 · id 유일·일치 · v 0/1 · e 500자 이하 · 부재탐지 e 빈칸"""
    errs: List[str] = []
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        rd = csv.reader(f)
        header = next(rd, None)
        rows = list(rd)
    if header != COLUMNS:
        errs.append(f"헤더 불일치: {len(header or [])}열 (기대 {len(COLUMNS)})")
        return errs
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


# ===== 8. 실행 =====
def run(input_path: str, out_path: str, runner_cls, limit: Optional[int], chunk: int,
        max_chars: int, data_dir: str, **runner_kw) -> Dict[str, Any]:
    t_all = time.time()
    recs = list(iter_records(input_path, limit=limit))
    log(f"입력 {len(recs)}건 ← {input_path}")
    if not recs:
        write_csv([], out_path)
        return {"건수": 0}

    tbl, schema = item_table(data_dir), decode_schema(data_dir)
    system_prompt = build_system_prompt(tbl)
    sme_codes = load_sme_competitive_codes(data_dir)
    log(f"중기간 경쟁제품 세부품명번호 {len(sme_codes)}건 로드(v13 오탐 억제용)")
    runner = runner_cls(schema, **runner_kw)
    log(f"모델 로드 {runner.load_seconds:.1f}s")

    # 전건 메시지 구성(길이 예산 맞춤)
    msgs_all, shrunk, ntok = [], 0, []
    for rec in recs:
        m, n, mc = fit_to_budget(rec, system_prompt, runner, max_chars)
        msgs_all.append(m)
        ntok.append(n)
        shrunk += int(mc < max_chars)
    log(f"프롬프트 토큰 중앙값 {sorted(ntok)[len(ntok) // 2]:,} · 최대 {max(ntok):,} · 예산 축소 {shrunk}건")

    # 배치 추론
    t_inf = time.time()
    texts: List[str] = []
    for s in range(0, len(msgs_all), chunk):
        texts.extend(run_chunk(runner, msgs_all[s:s + chunk]))
        log(f"  {min(s + chunk, len(msgs_all))}/{len(msgs_all)}건 … {time.time() - t_inf:.0f}s")
    inf_seconds = time.time() - t_inf

    # 파싱·후처리 → 행
    rows, invalid, filled, ev_kept, ev_dropped = [], 0, 0, 0, 0
    for rec, text in zip(recs, texts):
        try:
            parsed, missing = parse_judgment(text)
            invalid += int(len(missing) == 24)
            filled += len(missing)
            before = sum(1 for v in ITEMS if parsed[v]["근거문구"] and parsed[v]["위반여부"] == 1 and v not in ABSENCE)
            final = postprocess(parsed, rec, sme_codes=sme_codes)
            kept = sum(1 for v in ITEMS if final[v]["근거문구"])
            ev_kept += kept
            ev_dropped += max(0, before - kept)          # 규칙이 채운 근거가 있으면 kept가 더 클 수 있다
            rows.append(to_row(rec["id"], final))
        except Exception as e:                           # 한 건의 실패가 전체 실행을 막지 않도록
            log(f"  ! {rec['id']} 후처리 실패 → 전항목 0: {type(e).__name__}: {e}")
            rows.append(empty_row(rec["id"]))
    assert len(rows) == len(recs)

    write_csv(rows, out_path)
    errs = validate_csv(out_path, [r["id"] for r in recs])
    report = {
        "건수": len(recs), "모델로드_s": round(runner.load_seconds, 1), "추론_s": round(inf_seconds, 1),
        "건당_s": round(inf_seconds / len(recs), 2), "전체_s": round(time.time() - t_all, 1),
        "유효JSON": len(recs) - invalid, "메운_항목수": filled,
        "근거_유지": ev_kept, "근거_원문불일치_폐기": ev_dropped,
        "출력": out_path, "자가검증": "PASS" if not errs else errs,
    }
    log(json.dumps(report, ensure_ascii=False))
    if invalid:
        log("[주의] 유효 JSON이 아닌 출력이 있습니다. 구조화 출력 설정과 JSON Schema를 확인하세요.")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="24개 항목의 법령 위반 여부 판정 베이스라인")
    ap.add_argument("--data-dir", default=DATA_DIR)
    ap.add_argument("--output-dir", default=OUTPUT_DIR)
    ap.add_argument("--input", default=None, help="기본 = <data-dir>/test.jsonl.gz")
    ap.add_argument("--model-dir", default=MODEL_DIR, help="로컬에서는 HF ID(google/gemma-4-26B-A4B-it)도 가능")
    ap.add_argument("--quantization", default=os.environ.get("PPS_QUANT", QUANT),
                    help="채점 서버 = int8_per_channel_weight_only · 'none'이면 미양자화")
    ap.add_argument("--gpu-mem", type=float, default=0.92)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--chunk", type=int, default=128, help="LLM.chat 한 번에 넘길 건수")
    ap.add_argument("--max-chars", type=int, default=4000, help="문서 글자 수의 초기 상한(토큰 예산에 맞춰 자동 조정)")
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--mock", action="store_true", help="모델 없이 흐름만 확인")
    a = ap.parse_args()

    input_path = a.input or os.path.join(a.data_dir, "test.jsonl.gz")
    out_path = os.path.join(a.output_dir, "submission.csv")
    quant = None if str(a.quantization).lower() in ("none", "") else a.quantization
    runner_kw = {} if a.mock else dict(model_dir=a.model_dir, quant=quant, max_tokens=a.max_tokens,
                                       seed=SEED, gpu_mem=a.gpu_mem, tp=a.tp)
    report = run(input_path, out_path, MockRunner if a.mock else VLLMRunner,
                 limit=a.limit, chunk=a.chunk, max_chars=a.max_chars, data_dir=a.data_dir, **runner_kw)
    return 0 if report.get("자가검증") in ("PASS", None) else 1


if __name__ == "__main__":
    sys.exit(main())
