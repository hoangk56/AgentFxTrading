"""Verdict of the 2016-2022 retest of old-lab strategies (research/results/portfolio/prereg_swing_v2.md, R-series).

  python -m research.swing.retest_verdict RUN_DIR [RUN_DIR ...]

Pooled over each strategy's symbols: mean R, t, years with net > 0, share of random-entry seeds beaten on summed R;
pass = mean R > 0 and t >= 2, >= 5 of 7 years net > 0, >= 90 % of seeds beaten."""
import csv
import gzip
import math
import sys
from collections import defaultdict

import numpy as np


def verdict(run_dirs):
    trades = defaultdict(list)
    for d in run_dirs:
        with gzip.open(f"{d}/trades.csv.gz", "rt") as fh:
            for row in csv.DictReader(fh):
                r = float(row["r"])
                if math.isfinite(r):
                    trades[row["strategy"]].append((int(row["year"]), row["symbol"], r, float(row["net"])))
    ctrl = defaultdict(lambda: defaultdict(float))
    for d in run_dirs:
        with open(f"{d}/control.csv") as fh:
            for row in csv.DictReader(fh):
                ctrl[row["strategy"]][int(row["seed"])] += float(row["sum_r"])
    lines = ["| strategy | n | mean R | t | years net > 0 | by year (sum R) | seeds beaten | by symbol mean R | pass |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s, rows in sorted(trades.items()):
        r = np.array([x[2] for x in rows])
        n, mu = len(r), float(r.mean())
        t = mu / (r.std(ddof=1) / math.sqrt(n)) if n > 1 else 0.0
        by_year = defaultdict(float)
        net_year = defaultdict(float)
        for y, _, rr, net in rows:
            by_year[y] += rr
            net_year[y] += net
        pos = sum(1 for v in net_year.values() if v > 0)
        seeds = list(ctrl[s].values())
        beaten = float(np.mean([r.sum() > c for c in seeds])) if seeds else float("nan")
        by_sym = defaultdict(list)
        for _, sym, rr, _ in rows:
            by_sym[sym].append(rr)
        ok = mu > 0 and t >= 2.0 and pos >= 5 and beaten >= 0.9
        lines.append(f"| {s} | {n} | {mu:+.3f} | {t:+.1f} | {pos}/{len(net_year)} | "
                     + ", ".join(f"{y}:{v:+.0f}" for y, v in sorted(by_year.items())) + f" | {beaten:.0%} | "
                     + ", ".join(f"{k}:{np.mean(v):+.3f}" for k, v in sorted(by_sym.items())) + f" | {'PASS' if ok else 'fail'} |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(verdict(sys.argv[1:]))
