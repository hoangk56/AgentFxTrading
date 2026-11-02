"""Episode counts per era and descriptive premium stats (no returns). Run after premium.py."""
import datetime as dt
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load  # noqa: E402
import premium  # noqa: E402

D = dict(np.load(os.path.join(load.ROOT, "days.npz")))
day, p = D["day"], D["p"]
fin = np.isfinite(p)
yrs = np.array([dt.date.fromordinal(int(x)).year for x in day])
print("valid days", len(day), "with premium", fin.sum(), "ask fallback days", int(D["ask_fallback"].sum()))
print("median 07:00 spread by year (bp):", {int(y): round(s * 1e4, 1) for y, s in D["med_spread"]})
print("premium percentiles by year (%): p10 p50 p90 max")
for y in range(2018, 2025):
    m = fin & (yrs == y)
    q = np.percentile(p[m] * 100, [10, 50, 90, 100])
    print(y, m.sum(), " ".join(f"{x:.2f}" for x in q))
IS_END = dt.date(2022, 1, 1).toordinal()
for k in (0.01, 0.02):
    sig = fin & (p > k)
    ep = premium.episodes(sig)
    print(f"\nk={k:.0%}: signal days by year", {int(y): int((sig & (yrs == y)).sum()) for y in range(2018, 2025)})
    for era, m in (("IS", day < IS_END), ("VAL", day >= IS_END)):
        e = np.unique(ep[sig & m])
        print(f"  {era}: signal days {int((sig & m).sum())}, episodes {len(e)}")
    for u in np.unique(ep[sig]):
        ii = np.flatnonzero(ep == u)
        print(f"   ep{u}: {dt.date.fromordinal(int(day[ii[0]]))} .. {dt.date.fromordinal(int(day[ii[-1]]))}  days {len(ii)}  "
              f"max p {p[ii].max() * 100:.2f}%")
