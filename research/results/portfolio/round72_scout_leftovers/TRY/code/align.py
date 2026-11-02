"""Which hour does a BtcTurk 1h candle label cover? Correlate the Dukascopy 06:00->06:59 mid return with the BtcTurk
candle return (c/o - 1) labelled 06:00 (label = start) and 07:00 (label = end). No strategy return is computed."""
import datetime as dt
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load  # noqa: E402

t, o, h, l, c, v = load.btcturk_1h()
idx = {int(x): i for i, x in enumerate(t)}
x, y6, y7, y5 = [], [], [], []
d = dt.date(2018, 7, 10)
while d < dt.date(2025, 1, 1):
    r = load.duka_hour(d)
    if r is not None and len(r[0]) > 20:
        ms, a, b = r
        mid = (a + b) / 2
        base = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.UTC).timestamp())
        ks = [idx.get(base + hh * 3600) for hh in (5, 6, 7)]
        if all(k is not None for k in ks):
            x.append(mid[-1] / mid[0] - 1)
            y5.append(c[ks[0]] / o[ks[0]] - 1); y6.append(c[ks[1]] / o[ks[1]] - 1); y7.append(c[ks[2]] / o[ks[2]] - 1)
    d += dt.timedelta(days=1)
x = np.array(x)
for name, y in (("label 05:00", y5), ("label 06:00 (start-label)", y6), ("label 07:00 (end-label)", y7)):
    print(f"{name}: corr with Duka 06-07 mid return = {np.corrcoef(x, np.array(y))[0, 1]:.3f}  n={len(x)}")
