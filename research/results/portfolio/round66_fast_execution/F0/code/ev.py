"""Round 66 F0: F's registered event set (T5 idio, de-duplicated), from F/out/cand.npz (read-only).

Selection copied from round64_parallel/F/code/report.py (thresholds, idio filter, dedup). No returns are used here.
Minute axis: t = minutes since 2020-01-01 00:00 UTC; bar t opens at T0 + t min. Event bar e closes at T0 + (e+1) min.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))  # research/
CAND = os.path.join(R, "results/portfolio/round64_parallel/F/out/cand.npz")
T0 = 1577836800000
MIN = 60000
DAY = 86400000
VAL0 = (1640995200000 - T0) // MIN
END = 1735689600000
BP = 1e4


def dedup(sym, t):
    o = np.lexsort((t, sym))
    keep = np.zeros(len(t), bool)
    ls, lt = -1, -10 ** 9
    for j in o:
        if sym[j] != ls or t[j] - lt > 60:
            keep[j] = True; ls, lt = sym[j], t[j]
    return keep


def events():
    """indices into cand.npz of the T5 idio de-duplicated events, plus the arrays needed."""
    z = np.load(CAND)
    syms = list(z["syms"])
    sym, t, r, rb, rank = z["sym"], z["t"].astype(np.int64), z["r"], z["rb"], z["rank"]
    ibtc, ieth = syms.index("BTCUSDT"), syms.index("ETHUSDT")
    a = np.abs(r)
    idio = (sym != ibtc) & np.isfinite(rb) & (np.abs(rb) <= 0.2 * a)
    idx = np.where((a >= 0.05) & idio)[0]
    idx = idx[dedup(sym[idx], t[idx])]
    idx = idx[np.argsort(t[idx], kind="stable")]
    h = np.where((sym == ibtc) | (sym == ieth), 1.0, np.where(rank < 20, 3.0, 5.0)) / BP
    close_e = T0 + (t + 1) * MIN  # ms, close of the event bar = open of e+1
    return dict(z=z, idx=idx, syms=syms, sym=sym, t=t, r=r, h=h, close_e=close_e,
                era=np.where(t < VAL0, 0, 1), day=(T0 + t * MIN) // DAY)
