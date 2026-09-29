#!/usr/bin/env python3
"""submission.csv를 dev 정답과 비교해 항목별 F1과 macro F1을 출력한다(표준 라이브러리만 사용).

  python score_csv.py <submission.csv> <dev_labels.csv>
"""
import csv
import sys

ITEMS = [f"v{i}" for i in range(1, 25)]


def load(path):
    with open(path, encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def main() -> int:
    pred, gold = load(sys.argv[1]), load(sys.argv[2])
    ids = [i for i in gold if i in pred]
    missing = [i for i in gold if i not in pred]
    print(f"채점 {len(ids)}건 · 예측 누락 {len(missing)}건")
    f1s = []
    print(f"{'item':<5} {'F1':>6} {'TP':>3} {'FP':>3} {'FN':>3}")
    for v in ITEMS:
        tp = sum(1 for i in ids if gold[i][v] == "1" and pred[i][v] == "1")
        fp = sum(1 for i in ids if gold[i][v] != "1" and pred[i][v] == "1")
        fn = sum(1 for i in ids if gold[i][v] == "1" and pred[i][v] != "1")
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
        f1s.append(f1)
        print(f"{v:<5} {f1:6.3f} {tp:3d} {fp:3d} {fn:3d}")
    print(f"macro F1 {sum(f1s) / len(f1s):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
