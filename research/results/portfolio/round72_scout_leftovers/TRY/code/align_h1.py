"""BtcTurk candle label check on hourly data: corr of the Dukascopy BID hourly return (c/o-1, hour starting at T) with
the BtcTurk candle return labelled T-3600, T (label = start) and T+3600 (label = end). Also checks the Duka record order
(high >= max(open, close) >= min(open, close) >= low). No strategy return."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load  # noqa: E402

t, o, h, l, c, v = load.btcturk_1h()
H = load.duka_h1()
tb, ob, cb, lb, hb, vb = H["BID"]
print("duka BID candles", len(tb), "order ok share",
      np.mean((hb >= np.maximum(ob, cb) - 1e-9) & (lb <= np.minimum(ob, cb) + 1e-9)))
ib = {int(x): i for i, x in enumerate(tb)}
rb = cb / ob - 1
rt = c / o - 1
for lag in (-3600, 0, 3600):
    xs, ys = [], []
    for i, x in enumerate(t):
        j = ib.get(int(x) - lag)
        if j is not None and vb[j] > 0:
            xs.append(rb[j]); ys.append(rt[i])
    print(f"BtcTurk label = Duka hour start + {lag // 3600:+d} h: corr {np.corrcoef(xs, ys)[0, 1]:.3f} n={len(xs)}")
