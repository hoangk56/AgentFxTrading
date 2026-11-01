"""Round 63 stream C: data checks on the 1h panel (coverage vs 1d klines, gaps, extreme 1h moves). No HOLD data."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xs  # noqa: E402

Pn = xs.load()
P = Pn["P"]
syms = Pn["syms"]
r = P[:, 1:] / P[:, :-1] - 1
nd = Pn["QD"].shape[1]
print("symbols", len(syms))
bad = []
for i, s in enumerate(syms):
    have_d = ~np.isnan(Pn["QD"][i])
    hours = ~np.isnan(P[i, 1:]).reshape(-1)[: nd * 24].reshape(nd, 24)
    cov = hours.sum(1)
    miss_days = int((have_d & (cov < 20)).sum())
    ext = int((np.abs(r[i]) > 0.3).sum())
    if miss_days or ext:
        bad.append((s, miss_days, ext, float(np.nanmax(np.abs(r[i])))))
print("symbol, days with 1d bar but < 20 1h bars, hours with |r| > 30 %, max |r|")
for b in sorted(bad, key=lambda x: -x[1] - x[2]):
    print(*b)
fr = Pn["FR"]
print("funding stamps per symbol (median)", int(np.median((fr != 0).sum(1))))
