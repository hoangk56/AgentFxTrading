"""Minute coverage and spread of IC HK50 around the HK close (no returns). ts < 2025-01-01."""
import numpy as np
from research.m1 import load
CUT = 1735689600000
d = load("HK50")
k = d["ts"] < CUT
ts = d["ts"][k]; sm = d["smean"][k]; c = d["c"][k]
hkt = ts + 8 * 3600_000
mod = (hkt // 60000) % 1440
yr = (hkt // 86400000 * 86400 ).astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970
print("first", np.datetime64(int(ts[0]), "ms"), "n", len(ts))
mins = [9*60+15, 9*60+30, 12*60-1, 13*60, 15*60+30, 15*60+44, 15*60+45, 15*60+50, 15*60+55, 15*60+59, 16*60, 16*60+5, 16*60+9, 16*60+10, 16*60+15, 16*60+29, 16*60+30, 16*60+45, 17*60+15, 17*60+16, 17*60+30]
for y in range(2016, 2025):
    ny = len(np.unique(hkt[(yr == y)] // 86400000))
    row = []
    for m in mins:
        s = (yr == y) & (mod == m)
        row.append(f"{s.sum()/max(ny,1):.2f}/{np.median(sm[s]/c[s]*1e4) if s.any() else np.nan:.1f}")
    print(y, ny, " ".join(row))
print("cols", [f"{m//60:02d}:{m%60:02d}" for m in mins])
