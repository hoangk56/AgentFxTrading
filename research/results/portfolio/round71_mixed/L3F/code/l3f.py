"""Round 71 L3F: extreme negative funding, follow the UTC day's sign for 24 h. Declared in ../HYPOTHESES_L3F.md.

Everything is cut at ts < 2025-01-01 at load (HOLD never read).
"""
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", "..", ".."))           # results/portfolio
sys.path.insert(0, os.path.join(RES, "round58_unconstrained_carry", "code"))
import carry  # noqa: E402

DATA = os.path.abspath(os.path.join(RES, "..", "..", "data"))
H = 3600000
DAY = 86400000
T0 = carry.T0                  # 2019-09-01
CUT = 1735689600000            # 2025-01-01
NH = (CUT - T0) // H
IS = (1577836800000, 1640995200000)
VAL = (1640995200000, 1735689600000)


def _rows(path):
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        out = []
        for x in r:
            if int(float(x[0])) >= CUT:
                break
            out.append(x)
    return np.array(out, dtype=float) if out else np.zeros((0, 2))


def load_1h(sym):
    """Return (open, close) arrays of length NH indexed by hour since T0 (NaN where missing)."""
    o = np.full(NH, np.nan)
    c = np.full(NH, np.nan)
    for p in (os.path.join(DATA, "binance_1h_full", "1h", sym + ".csv"),
              os.path.join(DATA, "binance_basis", "perp_1h", sym + ".csv")):
        if os.path.exists(p):
            a = _rows(p)
            if len(a):
                a = a[a[:, 0] < CUT]
                k = ((a[:, 0] - T0) // H).astype(np.int64)
                m = (k >= 0) & (k < NH)
                o[k[m]] = a[m, 1]
                c[k[m]] = a[m, 4]
            return o, c, p
    return o, c, None


def load_funding(sym):
    p = os.path.join(DATA, "binance", "funding", sym + ".csv")
    if not os.path.exists(p):
        return None
    a = _rows(p)
    a = a[a[:, 0] < CUT]
    t = (np.round(a[:, 0] / H) * H).astype(np.int64)
    f = a[:, 1]
    # dedupe same hour
    t, idx = np.unique(t, return_index=True)
    f = f[idx]
    dt = np.diff(t, prepend=t[0] - 8 * H) / H
    dt = np.clip(np.round(dt), 1, 8)
    f8 = f * 8.0 / dt
    return t, f, f8


def build_universe():
    syms = sorted(x[:-4] for x in os.listdir(os.path.join(DATA, "binance", "perp_1d")) if x.endswith(".csv"))
    P = carry.load_panel(syms, hold=False)
    U, rank = carry.universe(P, N=10)
    return P, U, rank


def trailing_pct_flags(t, f8, q):
    """Event flag per stamp: f8 < 0 and f8 <= q-th percentile over [T-180d, T), >= 90 d history, >= 100 stamps."""
    n = len(t)
    ev = np.zeros(n, dtype=bool)
    first = t[0] if n else 0
    lo = 0
    for j in range(n):
        if f8[j] >= 0 or t[j] - first < 90 * DAY:
            # still advance window start
            while lo < j and t[lo] < t[j] - 180 * DAY:
                lo += 1
            continue
        while lo < j and t[lo] < t[j] - 180 * DAY:
            lo += 1
        w = f8[lo:j]
        if len(w) < 100:
            continue
        if f8[j] <= np.percentile(w, q):
            ev[j] = True
    return ev


def day_sign(o, c, T):
    """sign of ln(close of bar ending at T / open of first bar of the UTC day containing T - 1 ms)."""
    kT = (T - T0) // H - 1               # bar [T-1h, T)
    d0 = ((T - 1) // DAY) * DAY
    k0 = (d0 - T0) // H
    if kT < 0 or k0 < 0 or kT >= NH:
        return 0
    a, b = o[k0], c[kT]
    if not (np.isfinite(a) and np.isfinite(b)) or a <= 0:
        return 0
    r = np.log(b / a)
    return int(np.sign(r))


def trade(o, c, ft, ff, T, side, late=0, hold=24):
    """Entry close of bar [T+late h, T+late+1 h), exit close of bar [T+late+hold h, ...). Return (gross price ret,
    funding ret, entry_ms, exit_ms) or None."""
    ke = (T - T0) // H + late
    kx = ke + hold
    if kx >= NH or ke < 0:
        return None
    pe, px = c[ke], c[kx]
    if not (np.isfinite(pe) and np.isfinite(px)) or pe <= 0:
        return None
    te = T0 + (ke + 1) * H
    tx = T0 + (kx + 1) * H
    if tx >= CUT:
        return None
    m = (ft > te) & (ft <= tx)
    fund = -side * ff[m].sum()
    return side * (px / pe - 1.0), fund, te, tx


def cost_rt(sym, rank_val, mult=1.0):
    hs = carry.half_spread(sym, rank_val if rank_val is not None else 9999)
    if sym not in ("BTCUSDT", "ETHUSDT") and rank_val is not None and rank_val < 10:
        hs = 0.0003
    return mult * 2 * (0.0005 + hs)


def cluster_t(x, day):
    x = np.asarray(x)
    if len(x) < 3:
        return np.nan
    mu = x.mean()
    ud, inv = np.unique(day, return_inverse=True)
    s = np.bincount(inv, weights=x - mu)
    G = len(ud)
    var = (s ** 2).sum() / len(x) ** 2 * G / max(G - 1, 1)
    return mu / np.sqrt(var) if var > 0 else np.nan


def nw_t(r, lag=5):
    r = np.asarray(r)
    n = len(r)
    mu = r.mean()
    x = r - mu
    g = np.dot(x, x) / n
    for k in range(1, lag + 1):
        g += 2 * (1 - k / (lag + 1)) * np.dot(x[k:], x[:-k]) / n
    return mu / np.sqrt(g / n) if g > 0 else np.nan
