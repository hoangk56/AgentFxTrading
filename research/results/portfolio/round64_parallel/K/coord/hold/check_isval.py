"""k2rule on stream K's IS / VAL events (k2_events.csv, L < 2024-12-28) must reproduce K2 H72 e1h: IS n 11 +1094, VAL n 29 +423."""
import csv, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k2rule as k
ev = [r for r in csv.DictReader(open(os.path.join(k.R, "upbit", "k2_events.csv"))) if int(r["L"]) < 1735689600000 - 4 * k.DAY]
rows = []
for r in ev:
    x = k.trade(r["sym"], int(r["L"]))
    if x: rows.append(x)
a = np.array(rows)
for lab, lo, hi in (("IS", 0, 1640995200000), ("VAL", 1640995200000, 1735689600000)):
    q = a[(a[:, 0] >= lo) & (a[:, 0] < hi)]
    m, t, n = k.clt(q[:, 3], (q[:, 0] // k.DAY).astype(int))
    print(f"{lab} n {n} net {m*1e4:+.0f} bp t {t:.2f}")
