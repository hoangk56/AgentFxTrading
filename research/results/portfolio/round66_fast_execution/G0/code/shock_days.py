"""G0: candidate BTC shock windows from F's 1m npz (read-only), ts < 2025-01-01.
A 60-s window lies inside two consecutive 1m bars, so max(h[t-1],h[t]) / min(l[t-1],l[t]) - 1 >= X is a superset of
every real-time trigger (trailing-60 s move >= X). Writes code/../out/cand_minutes.npz (minutes, days). No returns."""
import os, glob, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(os.path.join(HERE, *[".."] * 5, "data", "binance_1m_wicks", "npz"))
OUT = os.path.join(HERE, "..", "out"); os.makedirs(OUT, exist_ok=True)
END_MIN = 1735689600000 // 60000
ms, hs, ls = [], [], []
for f in sorted(glob.glob(os.path.join(D, "BTCUSDT_*.npz"))):
    z = np.load(f); m = z["m"].astype(np.int64); k = m < END_MIN
    ms.append(m[k]); hs.append(z["h"][k].astype(float)); ls.append(z["l"][k].astype(float))
m = np.concatenate(ms); h = np.concatenate(hs); l = np.concatenate(ls)
o = np.argsort(m); m, h, l = m[o], h[o], l[o]
cont = np.r_[False, np.diff(m) == 1]
hh = np.maximum(h, np.r_[h[:1], h[:-1]]); ll = np.minimum(l, np.r_[l[:1], l[:-1]])
rng2 = np.where(cont, hh / ll - 1, h / l - 1)
for X in (0.01, 0.015, 0.02):
    t = m[rng2 >= X]
    days = np.unique(t // 1440)
    isd = days < (1640995200000 // 86400000)
    print(f"X {X}: cand minutes {len(t)}, days {len(days)} (IS {isd.sum()}, VAL {(~isd).sum()}); by year",
          np.unique((days * 86400 // 31557600 + 1970).astype(int), return_counts=True))
t = m[rng2 >= 0.01]
np.savez(os.path.join(OUT, "cand_minutes.npz"), m=t)
