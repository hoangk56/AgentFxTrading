"""Round 63 stream C: intraday cross-sectional books on Binance USDT-M perps (../HYPOTHESES_C.md).

Hour axis: index h = hours since H0 (2019-11-01 00:00 UTC). P[i, h] = price at instant h = close of the 1h bar that
opened at h - 1. V[i, h] = VWAP of the bar opening at h. Every series is cut at ts < 2025-01-01 at load (no HOLD).
"""
import csv
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
D1H = os.path.join(R, "data", "binance_1h_full", "1h")
B = os.path.join(R, "data", "binance")
HOUR = 3600000
DAY = 86400000
H0 = 1572566400000          # 2019-11-01
END = 1735689600000         # 2025-01-01 (HOLD start, exclusive)
NH = (END - H0) // HOUR
IS = (1577836800000, 1640995200000)
VAL = (1640995200000, 1735689600000)
CACHE = os.path.join(R, "data", "binance_1h_full", "panel_cache.npz")


def _arr(path):
    with open(path) as f:
        rows = list(csv.reader(f))[1:]
    if not rows:
        return np.zeros((0, 8))
    return np.array(rows, dtype=float)


def load(refresh=False):
    if os.path.exists(CACHE) and not refresh:
        z = np.load(CACHE, allow_pickle=False)
        P = {k: z[k] for k in z.files}
        P["syms"] = list(P["syms"])
        return P
    syms = [r["sym"] for r in csv.DictReader(open(os.path.join(R, "data", "binance_1h_full", "symbols.csv")))]
    syms = [s for s in syms if os.path.exists(os.path.join(D1H, s + ".csv"))]
    n = len(syms)
    P = np.full((n, NH + 1), np.nan, dtype=np.float64)
    V = np.full((n, NH + 1), np.nan)
    QV = np.full((n, NH + 1), np.nan)   # quote volume of the bar opening at h
    FR = np.zeros((n, NH + 1))          # funding rate of a stamp at instant h
    nd = (END - H0) // DAY
    QD = np.full((n, nd), np.nan)       # daily perp quote volume (1d klines), day 0 = 2019-11-01
    first_day = np.zeros(n, dtype=np.int64)  # first 1d kline (may be before H0 -> negative)
    for i, s in enumerate(syms):
        a = _arr(os.path.join(D1H, s + ".csv"))
        a = a[a[:, 0] < END]
        h = ((a[:, 0] - H0) // HOUR).astype(np.int64)
        m = h >= 0
        a, h = a[m], h[m]
        P[i, h + 1] = a[:, 4]
        with np.errstate(invalid="ignore", divide="ignore"):
            V[i, h] = np.where(a[:, 5] > 0, a[:, 6] / a[:, 5], a[:, 4])
        QV[i, h] = a[:, 6]
        f = _arr(os.path.join(B, "funding", s + ".csv"))
        if len(f):
            f = f[f[:, 0] < END]
            hs = np.round((f[:, 0] - H0) / HOUR).astype(np.int64)
            m = (hs >= 0) & (hs <= NH)
            np.add.at(FR[i], hs[m], f[m, 1])
        d = _arr(os.path.join(B, "perp_1d", s + ".csv"))
        d = d[d[:, 0] < END]
        first_day[i] = int((d[0, 0] - H0) // DAY) if len(d) else 10 ** 6
        dd = ((d[:, 0] - H0) // DAY).astype(np.int64)
        m = dd >= 0
        QD[i, dd[m]] = d[m, 6]
    np.savez(CACHE, P=P, V=V, QV=QV, FR=FR, QD=QD, first_day=first_day, syms=np.array(syms))
    return dict(P=P, V=V, QV=QV, FR=FR, QD=QD, first_day=first_day, syms=syms)


def daily_universe(Pn, N=40, min_age=60):
    """[n, nd] bool: top N by mean daily quote volume over days d-30..d-1, listed >= min_age days; plus [n, nd] rank."""
    QD = Pn["QD"]
    n, nd = QD.shape
    U = np.zeros((n, nd), dtype=bool)
    rk = np.full((n, nd), 9999)
    for d in range(30, nd):
        with np.errstate(invalid="ignore"):
            tv = np.nanmean(QD[:, d - 30:d], axis=1)
        ok = np.isfinite(tv) & (d - Pn["first_day"] >= min_age) & ~np.isnan(QD[:, d - 1])
        idx = np.where(ok)[0]
        idx = idx[np.argsort(-tv[idx])][:N]
        U[idx, d] = True
        rk[idx, d] = np.arange(len(idx))
    return U, rk


def ffill(x):
    """Forward fill along axis 1 (for exit prices after a last bar)."""
    n, m = x.shape
    idx = np.where(~np.isnan(x), np.arange(m)[None, :], 0)
    np.maximum.accumulate(idx, axis=1, out=idx)
    out = x[np.arange(n)[:, None], idx]
    return out


def betas(Pn, win=720, shrink=0.5):
    """Trailing beta of hourly returns vs BTC using returns up to instant h (inclusive), [n, NH+1]."""
    P = Pn["P"]
    r = P[:, 1:] / P[:, :-1] - 1
    r = np.concatenate([np.full((P.shape[0], 1), np.nan), r], axis=1)
    b = r[Pn["syms"].index("BTCUSDT")][None, :]
    ok = ~np.isnan(r) & ~np.isnan(b)
    x = np.where(ok, b, 0.0)
    y = np.where(ok, r, 0.0)

    def rs(z):
        c = np.cumsum(z, axis=1)
        return c - np.concatenate([np.zeros((z.shape[0], win)), c[:, :-win]], axis=1)
    cnt, sx, sy = rs(ok.astype(float)), rs(x), rs(y)
    sxx, sxy = rs(x * x), rs(x * y)
    with np.errstate(invalid="ignore", divide="ignore"):
        cov = sxy / cnt - sx * sy / cnt ** 2
        var = sxx / cnt - (sx / cnt) ** 2
        beta = cov / var
    beta = np.where(cnt >= win / 2, beta, np.nan)
    return shrink * beta + (1 - shrink) * 1.0


class Ctx:
    """Precomputed arrays shared by all cells."""

    def __init__(self, Pn):
        self.Pn = Pn
        self.P = Pn["P"]
        self.Pf = ffill(self.P)
        self.Vf = ffill(Pn["V"])
        self.syms = Pn["syms"]
        self.n = len(self.syms)
        self.U, self.rk = daily_universe(Pn)
        self.beta = betas(Pn)
        self.CF = np.cumsum(Pn["FR"], axis=1)
        self.iB = self.syms.index("BTCUSDT")
        hs = np.full(self.n, 0.0005)
        self.big = np.array([s in ("BTCUSDT", "ETHUSDT") for s in self.syms])
        QV = np.where(np.isnan(Pn["QV"]), 0.0, Pn["QV"])
        self.cQV = np.concatenate([np.zeros((self.n, 1)), np.cumsum(QV, axis=1)], axis=1)  # cQV[:, h] = sum bars < h

    def half_spread(self, d):
        """[n] half-spread on day d: BTC/ETH 1 bp, volume rank < 20 3 bp, else 5 bp."""
        hs = np.where(self.rk[:, d] < 20, 0.0003, 0.0005)
        return np.where(self.big, 0.0001, hs)


def signal(cx, t, J, kind):
    """Signal at instant t (vector [n]), NaN outside universe / missing data. kind: raw | resid."""
    P = cx.P
    d = (t * HOUR) // DAY
    u = cx.U[:, d] & ~np.isnan(P[:, t]) & ~np.isnan(P[:, t - J])
    r = P[:, t] / P[:, t - J] - 1
    if kind == "resid":
        rb = r[cx.iB]
        r = r - cx.beta[:, t] * rb
    return np.where(u, r, np.nan)


def vol_surprise(cx, t, J):
    """Quote volume over bars [t-J, t) / mean J-hour volume over the 720 h before."""
    a = cx.cQV[:, t] - cx.cQV[:, t - J]
    b = (cx.cQV[:, t - J] - cx.cQV[:, t - J - 720]) * J / 720.0
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(b > 0, a / b, np.nan)


def rebalance_times(J, H, t0=IS[0], t1=VAL[1]):
    h0 = (t0 - H0) // HOUR
    h1 = (t1 - H0) // HOUR
    ts = np.arange(h0, h1)
    return ts[(ts % 24) % H == 0] if H <= 24 else ts[::H]


def precompute(cx, J, H, kind, family, rng=None):
    """Return dict of per-rebalance arrays for one cell: S [K, n] signal oriented so that LOW = long."""
    ts = rebalance_times(J, H)
    S = np.full((len(ts), cx.n), np.nan)
    for k, t in enumerate(ts):
        s = signal(cx, t, J, kind)
        if family in ("VLO", "VHI"):
            vs = vol_surprise(cx, t, J)
            ok = ~np.isnan(s) & ~np.isnan(vs)
            s = np.where(ok, s, np.nan)
            med = np.nanmedian(vs[ok]) if ok.sum() >= 8 else np.nan
            keep = (vs < med) if family == "VLO" else (vs >= med)
            s = np.where(keep, s, np.nan)
        S[k] = s
    if family in ("MOM", "VHI"):
        S = -S          # long winners: low (-r) = long
    return ts, S


def weights(S, q, rng=None):
    """Equal-weight long the q lowest / short the q highest of each row; zero if < 2q valid. rng -> shuffled ranks."""
    K, n = S.shape
    W = np.zeros((K, n))
    valid = ~np.isnan(S)
    nv = valid.sum(1)
    X = S.copy()
    if rng is not None:
        X = np.where(valid, rng.random(S.shape), np.nan)
    lo = np.argsort(np.where(valid, X, np.inf), axis=1)[:, :q]
    hi = np.argsort(np.where(valid, -X, np.inf), axis=1)[:, :q]
    rows = np.arange(K)[:, None]
    W[rows, lo] = 1.0 / q
    W[rows, hi] = -1.0 / q
    W[nv < 2 * q] = 0.0
    return W


def mats(cx, ts, H, lag=0, exe="close"):
    """Matrices that do not depend on the ranking: forward return, entry ok, funding over the hold, half-spread."""
    e = ts + lag
    x = np.minimum(e + H, cx.P.shape[1] - 1)
    if exe == "close":
        pe, px = cx.Pf[:, e], cx.Pf[:, x]
        ok = ~np.isnan(cx.P[:, e])
    else:   # VWAP of the bar opening at e (the hour after the signal when lag = 0 ... see HYPOTHESES)
        pe, px = cx.Vf[:, e], cx.Vf[:, x]
        ok = ~np.isnan(cx.Pn["V"][:, e])
    ret = (px / pe - 1).T
    ret = np.where(np.isnan(ret), 0.0, ret)
    fu = (cx.CF[:, x] - cx.CF[:, e]).T
    days = ((ts * HOUR) // DAY).astype(np.int64)
    hs = np.where(cx.rk[:, days].T < 20, 0.0003, 0.0005)
    hs = np.where(cx.big[None, :], 0.0001, hs)
    return dict(ret=ret, ok=ok.T, fu=fu, hs=hs, tms=H0 + ts * HOUR)


def book(M, W, fee=0.0005, spread=True, cost_mult=1.0, funding=True):
    """Per-rebalance net returns per $1 of one side (long side $1, short side $1), plus components."""
    Wk = np.where(M["ok"], W, 0.0)
    L = np.where(Wk > 0, Wk, 0.0)
    S_ = np.where(Wk < 0, Wk, 0.0)
    lt = L.sum(1, keepdims=True)
    st = -S_.sum(1, keepdims=True)
    both = (lt > 0) & (st > 0)
    Wk = np.where(both, L / np.where(lt > 0, lt, 1) + S_ / np.where(st > 0, st, 1), 0.0)
    gross = (Wk * M["ret"]).sum(1)
    fund = -(Wk * M["fu"]).sum(1) if funding else np.zeros(len(gross))
    dW = np.abs(np.diff(np.vstack([np.zeros((1, Wk.shape[1])), Wk]), axis=0))
    c = fee + (M["hs"] if spread else 0.0)
    cost = cost_mult * (dW * c).sum(1)
    net = gross + fund - cost
    return dict(net=net, gross=gross, fund=fund, cost=cost, tms=M["tms"], turn=dW.sum(1) / 4.0, W=Wk)


def daily(r, tms):
    d = (tms // DAY).astype(np.int64)
    u, inv = np.unique(d, return_inverse=True)
    s = np.zeros(len(u))
    np.add.at(s, inv, r)
    return u, s


def tstats(r, tms):
    u, s = daily(r, tms)
    n = len(s)
    mu, sd = s.mean(), s.std(ddof=1)
    t_day = mu / sd * np.sqrt(n) if sd > 0 else 0.0
    xc = s - mu
    v = (xc * xc).mean()
    for L in range(1, 6):
        v += 2 * (1 - L / 6) * (xc[L:] * xc[:-L]).mean()
    t_nw = mu / np.sqrt(v / n) if v > 0 else 0.0
    return dict(n_days=n, mean_day=mu, sd_day=sd, t_day=t_day, t_nw=t_nw, t=min(t_day, t_nw),
                sr_day=mu / sd if sd > 0 else 0.0)


def era_mask(tms, era):
    return (tms >= era[0]) & (tms < era[1])


def years(r, tms):
    y = (tms.astype("datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970)
    return {int(k): float(r[y == k].sum()) for k in np.unique(y)}
