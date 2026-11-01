"""Diagnostic: EW basket overnight (Yahoo opens) vs IC US500 CFD mid 15:59 -> 09:30 New York, 2016-2024."""
import sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading")
import numpy as np
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from research import m1
z = m1.load("US500")
keep = z["ts"] < int(datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
ts = z["ts"][keep]; mid = (z["c"][keep] + z["ca"][keep]) / 2
ny = ZoneInfo("America/New_York")
b = np.load("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round63_parallel/S/out_books.npz")
dates = b["dates"]; b_on = b["b_on"]
tsset = {int(t): i for i, t in enumerate(ts)}
def px(d, hh, mm):
    y, mo, dd = map(int, d.split("-"))
    t = int(datetime(y, mo, dd, hh, mm, tzinfo=ny).timestamp() * 1000)
    i = tsset.get(t)
    return mid[i] if i is not None else np.nan
x, y = [], []
for t in range(1, len(dates) - 1):
    if dates[t] < "2016-02-01" or not np.isfinite(b_on[t]):
        continue
    c0 = px(dates[t], 15, 59); o1 = px(dates[t + 1], 9, 30)
    if np.isfinite(c0) and np.isfinite(o1):
        x.append(b_on[t]); y.append(o1 / c0 - 1)
x = np.array(x); y = np.array(y)
print("n", len(x), "corr %.3f" % np.corrcoef(x, y)[0, 1], "mean bp basket %.2f US500 %.2f" % (x.mean() * 1e4, y.mean() * 1e4),
      "sd bp %.1f %.1f" % (x.std() * 1e4, y.std() * 1e4))
