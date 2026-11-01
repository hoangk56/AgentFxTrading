"""Round 63 stream O engine (../HYPOTHESES_O.md): 20 declared cells (H1 OI flush, H2 crowding fade, H3 taker
continuation / reversal) on the K = 16 point-in-time alt universe, Binance perp VWAP fills, BTC-hedged.
Every series ends before 2025-01-01 (xs.load cut, metrics days <= 2024-12-31)."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import univ  # noqa: E402
from univ import xs  # noqa: E402

OUT = os.path.join(HERE, "..", "out")
MET = os.path.join(xs.R, "data", "binance_metrics", "hourly.npz")
DISC = (1640995200000, 1688169600000)   # 2022-01-01 .. 2023-07-01
VAL = (1688169600000, 1735689600000)    # 2023-07-01 .. 2025-01-01
ERAS = {"DISC": DISC, "VAL": VAL}
K = 16
TAKER, BTC_HS = 0.0005, 0.0001
HOLD_MONTHS, VAL_MONTHS = 22.0, 18.0


def h_of(ms):
    return (ms - xs.H0) // xs.HOUR


class Data:
    def __init__(self):
        Pn = xs.load()
        self.Pn = Pn
        self.P, self.V = Pn["P"], Pn["V"]
        self.syms = Pn["syms"]
        self.n = len(self.syms)
        self.iB = self.syms.index("BTCUSDT")
        self.iE = self.syms.index("ETHUSDT")
        self.A, self.rk = univ.alt_universe(Pn, K)
        self.beta = xs.betas(Pn)
        self.CF = np.cumsum(Pn["FR"], axis=1)
        z = np.load(MET)
        self.OIh, self.TPh, self.TKh, self.GAh, self.cov = z["OIh"], z["TPh"], z["TKh"], z["GAh"], z["cov"]
        nd = self.A.shape[1]
        self.tierA = np.zeros(nd, dtype=bool)
        self.tierA[univ.D0:univ.D1:2] = True
        self.dff = np.zeros(nd)
        import csv
        dmap = {}
        for r in csv.DictReader(open(os.path.join(xs.R, "data", "rates", "DFF.csv"))):
            try:
                dmap[r["observation_date"]] = float(r["DFF"])
            except ValueError:
                pass
        from datetime import datetime, timedelta, timezone
        base = datetime(2019, 11, 1, tzinfo=timezone.utc)
        last = 0.0
        for d in range(nd):
            k = (base + timedelta(days=d)).strftime("%Y-%m-%d")
            last = dmap.get(k, last)
            self.dff[d] = last / 100.0

    # ---- trade arithmetic -------------------------------------------------------------------------------------
    def legs(self, i, t, H, lag=0, cm=1.0):
        """Return (g, c, ok): side-signed part g (alt minus beta BTC, funding) and cost + cash c, per $1 alt."""
        e, x = t + lag, t + H + lag
        ok = (x <= xs.NH) & (t >= 1)
        x = np.minimum(x, xs.NH)
        e = np.minimum(e, xs.NH)
        V, iB = self.V, self.iB
        with np.errstate(invalid="ignore", divide="ignore"):
            ra = V[i, x] / V[i, e] - 1
            rb = V[iB, x] / V[iB, e] - 1
        b = self.beta[i, t]
        fa = self.CF[i, x] - self.CF[i, e]
        fb = self.CF[iB, x] - self.CF[iB, e]
        g = ra - b * rb - fa + b * fb
        d = t // 24
        hs = np.where(self.rk[i, d] < 20, 0.0003, 0.0005)
        hs = np.where(i == self.iE, 0.0001, hs)
        c = cm * (2 * (TAKER + hs) + 2 * (TAKER + BTC_HS) * np.abs(b)) + self.dff[d] / 365.0 * H / 24.0
        ok = ok & np.isfinite(g) & np.isfinite(c)
        return g, c, ok

    def gross(self, i, t, H, lag=0):
        e, x = t + lag, np.minimum(t + H + lag, xs.NH)
        with np.errstate(invalid="ignore", divide="ignore"):
            return self.V[i, x] / self.V[i, e] - 1 - self.beta[i, t] * (self.V[self.iB, x] / self.V[self.iB, e] - 1)


def no_overlap(i, t, H):
    """Keep the first signal per coin, skip signals while that coin's position (H hours) is open."""
    order = np.lexsort((t, i))
    keep = np.zeros(len(t), dtype=bool)
    last_i, last_x = -1, -1
    for k in order:
        if i[k] != last_i:
            last_i, last_x = i[k], -1
        if t[k] >= last_x:
            keep[k] = True
            last_x = t[k] + H
    return keep


# ---- percentiles against the coin's own previous 30 calendar days (Tier-A days) -------------------------------
def percentiles(D, X, inst_k):
    """For every covered Tier-A coin-day (i, d) and instants t = 24 d + k (k in inst_k), percentile of X[i, t] against
    X[i, 24 dd + 1 .. 24 dd + 24] for days dd in d-30..d-1 (>= 8 days with data). Returns arrays i, t, pct."""
    I, T, Q = [], [], []
    ks = np.array(inst_k)
    for i in range(D.n):
        days = np.where(D.cov[i] & D.tierA)[0]
        if len(days) == 0:
            continue
        row = X[i]
        for d in days:
            lo = 24 * (d - 30) + 1
            w = row[lo:24 * d + 1].reshape(30, 24)
            okd = np.sum(np.any(np.isfinite(w), axis=1))
            if okd < 8:
                continue
            w = np.sort(w[np.isfinite(w)])
            tt = 24 * d + ks
            x = row[tt]
            fin = np.isfinite(x)
            if not fin.any():
                continue
            lo_c = np.searchsorted(w, x[fin], "left")
            hi_c = np.searchsorted(w, x[fin], "right")
            q = (lo_c + 0.5 * (hi_c - lo_c)) / len(w)
            I.append(np.full(fin.sum(), i))
            T.append(tt[fin])
            Q.append(q)
    if not I:
        return np.zeros(0, int), np.zeros(0, int), np.zeros(0)
    return np.concatenate(I), np.concatenate(T), np.concatenate(Q)


# ---- statistics --------------------------------------------------------------------------------------------------
def tclust(r, day):
    n = len(r)
    if n < 3:
        return np.nan
    m = r.mean()
    _, inv = np.unique(day, return_inverse=True)
    S = np.bincount(inv, weights=r - m)
    G = len(S)
    if G < 2:
        return np.nan
    v = np.sum(S ** 2) / n ** 2 * G / (G - 1)
    return m / np.sqrt(v) if v > 0 else np.nan


def era_of(t):
    ms = xs.H0 + t * xs.HOUR
    return np.where(ms < DISC[1], "DISC", "VAL")


def year_of(t):
    ms = xs.H0 + t * xs.HOUR
    return 2022 + (ms >= 1672531200000).astype(int) + (ms >= 1704067200000).astype(int)
