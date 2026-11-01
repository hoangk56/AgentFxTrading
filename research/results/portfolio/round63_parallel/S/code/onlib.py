"""Overnight / intraday panel for stream S (numpy only). Data cut at 2024-12-31 (file ends 2024-03-11)."""
import os
import numpy as np

DATA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/stooq/panel_sp500.npz"
DFF = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/rates/DFF.csv"

ERAS = {"PRE": ("2004-01-01", "2015-12-31"), "IS": ("2016-01-01", "2021-12-31"),
        "VAL": ("2022-01-01", "2024-12-31")}


class Panel:
    def __init__(self, path=DATA):
        z = np.load(path)
        self.syms = z["syms"]
        dates = z["dates"]
        keep = dates < "2025-01-01"
        assert keep.all()
        self.dates = dates
        self.year = np.array([int(d[:4]) for d in dates])
        self.date_added = z["date_added"]
        O, H, L, C, A, V = (z[k] for k in ["open", "high", "low", "close", "adj_close", "volume"])
        valid = np.isfinite(O) & np.isfinite(C) & np.isfinite(A) & (O > 0) & (C > 0) & (V > 0)
        valid &= (O <= H * 1.005) & (O >= L * 0.995) & (C <= H * 1.005) & (C >= L * 0.995)
        self.raw_valid = valid.copy()
        f = A / C
        Cp = np.vstack([np.full((1, C.shape[1]), np.nan), C[:-1]])
        fp = np.vstack([np.full((1, C.shape[1]), np.nan), f[:-1]])
        Ap = np.vstack([np.full((1, C.shape[1]), np.nan), A[:-1]])
        vp = np.vstack([np.zeros((1, C.shape[1]), bool), valid[:-1]])
        div = 1.0 - fp / f
        div = np.where(np.abs(div) < 0.25, div, np.nan)  # adj-factor glitches
        div = np.where(div > -0.005, np.where(div > 1e-5, div, 0.0), np.nan)  # rounding noise < 1e-5
        self.div = div
        on = O / Cp - 1.0 + div
        idr = C / O - 1.0
        cc = A / Ap - 1.0
        ok = valid & vp & np.isfinite(on) & np.isfinite(cc)
        ok &= np.abs(np.log1p(on)) < np.log(1.4)
        ok &= (C >= 5) & (Cp >= 5)
        # Yahoo fills a missing open with the previous close in old data (12-15 % of name-days 2003-06 vs 2-3 %
        # later): drop exact open == previous close before 2008 (both legs of that day)
        early = (self.dates < "2008-01-01")[:, None]
        fill = early & (np.abs(O / Cp - 1.0) < 1e-9)
        ok &= ~fill
        valid = valid & ~fill
        self.on = np.where(ok, on, np.nan)
        self.id = np.where(valid & (C >= 5) & (np.abs(np.log(C / O)) < np.log(1.4)), idr, np.nan)
        self.cc = np.where(ok, cc, np.nan)
        self.dv = np.where(valid, C * V, np.nan)
        self.close = np.where(valid, C, np.nan)
        self.adj = np.where(self.raw_valid & (C >= 5), A, np.nan)
        self.valid = valid
        self.member = self.date_added[None, :] <= self.dates[:, None]

    def era_mask(self, era):
        a, b = ERAS[era]
        return (self.dates >= a) & (self.dates <= b)


def dff_by_date(dates):
    d, v = [], []
    with open(DFF) as fh:
        next(fh)
        for line in fh:
            p = line.strip().split(",")
            if len(p) < 2 or p[1] in ("", "."):
                continue
            if p[0] >= "2025-01-01":
                break
            d.append(p[0]); v.append(float(p[1]))
    d = np.array(d); v = np.array(v)
    i = np.searchsorted(d, dates, side="right") - 1
    return v[np.clip(i, 0, None)] / 100.0


def nights(dates):
    """calendar nights from close of dates[t-1] to open of dates[t] (for overnight leg ending on t)."""
    dt = np.array(dates, dtype="datetime64[D]")
    n = np.empty(len(dt)); n[0] = 1
    n[1:] = (dt[1:] - dt[:-1]).astype(int)
    return n


def nw_t(x, lag=5):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    n = len(x)
    if n < 10:
        return np.nan
    m = x.mean(); e = x - m
    s = e @ e / n
    for k in range(1, lag + 1):
        w = 1 - k / (lag + 1)
        s += 2 * w * (e[k:] @ e[:-k]) / n
    return m / np.sqrt(s / n)


def rolling_mean_nan(x, n):
    """trailing mean over n rows ignoring NaN; requires >= 0.8 n finite values."""
    v = np.where(np.isfinite(x), x, 0.0)
    c = np.isfinite(x).astype(float)
    cv = np.cumsum(np.vstack([np.zeros((1, x.shape[1])), v]), axis=0)
    cc = np.cumsum(np.vstack([np.zeros((1, x.shape[1])), c]), axis=0)
    out = np.full(x.shape, np.nan)
    s = cv[n:] - cv[:-n]; k = cc[n:] - cc[:-n]
    out[n - 1:] = np.where(k >= 0.8 * n, s / np.maximum(k, 1), np.nan)
    return out


def rolling_median_dv(dv, n=63):
    out = np.full(dv.shape, np.nan)
    for t in range(n, dv.shape[0]):
        out[t] = np.nanmedian(dv[t - n:t], axis=0)  # through t-1
    return out
