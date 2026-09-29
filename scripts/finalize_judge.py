#!/usr/bin/env python3
"""judge_combo 후보에 실험으로 고른 JUDGE_VARIANT·JUDGE_POLICY를 넣고, mock 검증과 ZIP까지 한 번에 만든다.

  python scripts/finalize_judge.py --variant plain --policy '{"v1": "or", ...}'
  python scripts/finalize_judge.py --variant rag --policy-file policy.json

- `submissions/20260924_judge_combo/script.py`의 두 상수 줄만 바꾼다(나머지 코드는 그대로).
- mock 실행(종료코드 0·자가검증 PASS)을 확인하고, plain이면 script.py·requirements.txt, rag면 model/까지 압축한다.
- 압축 안팎 해시를 비교하고 SHA-256을 출력한다. 하나라도 실패하면 종료코드 1.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAND = ROOT / "submissions" / "20260924_judge_combo"
ITEMS = [f"v{i}" for i in range(1, 25)]
CHOICES = {"rule", "judge", "or", "and"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["plain", "rag"], required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--policy")
    g.add_argument("--policy-file")
    a = ap.parse_args()
    policy = json.loads(a.policy) if a.policy else json.loads(Path(a.policy_file).read_text(encoding="utf-8"))
    policy = {v: policy.get(v, "rule") for v in ITEMS}
    bad = {v: p for v, p in policy.items() if p not in CHOICES}
    if bad:
        print("잘못된 정책 값:", bad)
        return 1

    path = CAND / "script.py"
    src = path.read_text(encoding="utf-8")
    src, n1 = re.subn(r'^JUDGE_VARIANT = .*$', f'JUDGE_VARIANT = "{a.variant}"', src, count=1, flags=re.M)
    src, n2 = re.subn(r'^JUDGE_POLICY: Dict\[str, str\] = .*$',
                      "JUDGE_POLICY: Dict[str, str] = " + json.dumps(policy, ensure_ascii=False)
                      + "   # scripts/judge_combine.py 결과(클라우드 int8 실험)", src, count=1, flags=re.M)
    if n1 != 1 or n2 != 1:
        print("상수 줄을 찾지 못했다", n1, n2)
        return 1
    path.write_text(src, encoding="utf-8")
    changed = {v: p for v, p in policy.items() if p != "rule"}
    print(f"정책 반영: 변형 {a.variant} · rule 아닌 항목 {len(changed)}개 {changed}")

    with tempfile.TemporaryDirectory() as out:
        env = dict(os.environ, PPS_DATA_DIR=str(ROOT / "open" / "data"), PPS_OUTPUT_DIR=out)
        env.pop("PPS_CASES", None)
        r = subprocess.run([sys.executable, "script.py", "--mock"], cwd=CAND, env=env, capture_output=True, text=True)
        log = r.stdout + r.stderr
        (CAND / "mock_validation.log").write_text(log + f"\nexit {r.returncode}\n", encoding="utf-8")
        ok = r.returncode == 0 and '"자가검증": "PASS"' in log
        print(f"mock: 종료코드 {r.returncode} · 자가검증 {'PASS' if ok else 'FAIL'}")
        if not ok:
            print(log[-2000:])
            return 1

    files = ["script.py", "requirements.txt"] + (["model/cases.json"] if a.variant == "rag" else [])
    zp = CAND / "submit.zip"
    if zp.exists():
        zp.unlink()
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(CAND / f, f)
    with zipfile.ZipFile(zp) as z:
        names = z.namelist()
        same = all(sha(z.read(f)) == sha((CAND / f).read_bytes()) for f in files)
    print(f"ZIP: {names} · 압축 안팎 해시 {'일치' if same else '불일치'} · {zp.stat().st_size:,}바이트")
    print(f"SHA-256 {sha(zp.read_bytes())}")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
