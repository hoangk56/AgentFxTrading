"""Post-hoc control for K2 (not a cell, not used to choose anything): is the listing fade just a generic fade of any
alt that ran up >= X vs BTC in 24 h? Short alt / long BTC on 1h closes (enter at the close of the hour the run-up is
measured, i.e. at a bar close; gross, no costs), hold 24 / 72 h, one trade per coin per hold window, universe = the
K1/K2 Upbit universe perps excluding the 40 K2 listing windows (+-7 d)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kdata import MAP, H, DAY, ERAS, cl_t, year_of
import k2

hb = k2.h1_alt("BTCUSDT")
ev = k2.load_events()
excl = {}
for e in ev:
    excl.setdefault(e["sym"], []).append(e["L"])
for X in (0.10, 0.20):
    for hold in (24, 72):
        res = []
        for s in sorted(set(MAP.values()) - {"USDCUSDT", "BTCUSDT", "BTTUSDT"}):
            a = k2.h1_alt(s)
            ts = sorted(a)
            nxt = 0
            for t in ts:
                if t < nxt:
                    continue
                t0 = t - 24 * H
                if t0 not in a or t not in hb or t0 not in hb or (t + hold * H) not in a or (t + hold * H) not in hb:
                    continue
                if any(abs(t - L) < 7 * DAY for L in excl.get(s, [])):
                    continue
                run = (a[t] / a[t0] - 1) - (hb[t] / hb[t0] - 1)
                if run < X:
                    continue
                g = -((a[t + hold * H] / a[t] - 1) - (hb[t + hold * H] / hb[t] - 1))
                res.append((t, g))
                nxt = t + hold * H
        r = np.array(res)
        for era in ("IS", "VAL"):
            lo, hi = ERAS[era]
            x = r[(r[:, 0] >= lo) & (r[:, 0] < hi)]
            print(f"runup>={X:.2f} H{hold} {era} n {len(x)} gross {x[:,1].mean()*1e4:+.0f} bp t {cl_t(x[:,1], (x[:,0]//DAY).astype(int)):+.2f} median {np.median(x[:,1])*1e4:+.0f}")
