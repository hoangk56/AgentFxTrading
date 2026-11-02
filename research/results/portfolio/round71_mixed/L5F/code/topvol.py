"""Rank USDT-M perps by total quote volume over 2020-01-01..2024-12-31 (perp_1d, cut at ts < 2025-01-01)."""
import os, glob, numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
END = 1735689600000; START = 1577836800000
out = []
for f in glob.glob(os.path.join(R, "data", "binance", "perp_1d", "*.csv")):
    s = os.path.basename(f)[:-4]
    try:
        a = np.genfromtxt(f, delimiter=",", skip_header=1, usecols=(0, 6), ndmin=2)
    except Exception:
        continue
    if a.size == 0: continue
    k = (a[:, 0] >= START) & (a[:, 0] < END)
    out.append((np.nansum(a[k, 1]), s, int(a[k, 0].min()) if k.any() else 0))
out.sort(reverse=True)
import datetime as dt
for q, s, t0 in out[:12]:
    print(f"{s:14s} {q/1e9:10.1f} bn  first={dt.datetime.utcfromtimestamp(t0/1000).date() if t0 else '-'}")
