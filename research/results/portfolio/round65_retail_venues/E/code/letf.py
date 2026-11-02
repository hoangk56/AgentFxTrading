"""Round 65 E: HK L&I close rebalancing -> HK50 (cells declared in ../HYPOTHESES_E.md). ts < 2025-01-01 only."""
import sys
import numpy as np
from research.m1 import load

CUT = 1735689600000
M0 = 9 * 60  # first column = 09:00 HKT
NC = 9 * 60  # 09:00 .. 17:59


def hm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m) - M0


def panel():
    d = load("HK50")
    k = d["ts"] < CUT
    ts, bid, ask = d["ts"][k], d["c"][k], d["ca"][k]
    hkt = ts + 8 * 3600_000
    day = hkt // 86_400_000
    mod = (hkt // 60_000) % 1440 - M0
    ok = (mod >= 0) & (mod < NC)
    day, mod, bid, ask = day[ok], mod[ok], bid[ok], ask[ok]
    days = np.unique(day)
    di = np.searchsorted(days, day)
    B = np.full((len(days), NC), np.nan); A = B.copy()
    B[di, mod] = bid; A[di, mod] = ask
    dow = (days + 3) % 7  # 0 = Monday
    keep = (dow < 5) & np.isfinite(B[:, hm("15:44")])
    days, B, A = days[keep], B[keep], A[keep]
    yr = days.astype("datetime64[D]").astype("datetime64[Y]").astype(int) + 1970
    return days, yr, B, A


def prev_ref(B, A):
    mid = (B + A) / 2
    ref = np.where(np.isfinite(mid[:, hm("16:09")]), mid[:, hm("16:09")], mid[:, hm("15:59")])
    P = np.r_[np.nan, ref[:-1]]
    return mid, P


def bigmask(r, q, look=250, minh=120):
    a = np.abs(r)
    out = np.zeros(len(r), bool)
    for i in range(len(r)):
        lo = max(0, i - look)
        h = a[lo:i]; h = h[np.isfinite(h)]
        if len(h) >= minh and np.isfinite(a[i]):
            out[i] = a[i] >= np.quantile(h, q)
    return out


def trade(B, A, side, ent, ex, smult=1.0):
    """side +1 long / -1 short per day (0 = no trade); ent / ex column indices (arrays or ints). Net bp and mid bp."""
    n = len(side)
    ent = np.broadcast_to(ent, n); ex = np.broadcast_to(ex, n)
    ix = np.arange(n)
    be, ae, bx, ax = B[ix, ent], A[ix, ent], B[ix, ex], A[ix, ex]
    me, mx = (be + ae) / 2, (bx + ax) / 2
    he, hx = (ae - be) / 2 * smult, (ax - bx) / 2 * smult
    pe = np.where(side > 0, me + he, me - he)
    px = np.where(side > 0, mx - hx, mx + hx)
    net = side * (px - pe) / me * 1e4
    mid = side * (mx - me) / me * 1e4
    good = (side != 0) & np.isfinite(net)
    return np.where(good, net, np.nan), np.where(good, mid, np.nan)


CELLS = {  # name: (signal bar, follow(+1)/fade(-1), entry bar, exit bar, quantile)
    "C1": ("15:44", 1, "15:45", "15:59", 0.9),
    "C2": ("15:49", 1, "15:50", "15:59", 0.9),
    "C3": ("15:44", 1, "15:45", "16:09", 0.9),
    "C4": ("16:09", 1, "16:10", "16:28", 0.9),
    "C5": ("16:09", -1, "16:28", "17:29", 0.9),
    "C6": ("16:09", 1, "16:10", "16:28", 0.8),
}
