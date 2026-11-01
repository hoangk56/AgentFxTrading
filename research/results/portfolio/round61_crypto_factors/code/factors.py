"""Round 61: weekly long-short factor books on Binance USDT-M perps (../HYPOTHESES.md). HOLD cut unless hold=True."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round58_unconstrained_carry", "code"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round60_new_listings", "code"))
import carry as C  # noqa: E402
import listings as Lm  # noqa: E402


def panel(syms, hold=False):
    syms = [s for s in syms if Lm.base_of(s) not in Lm.EXCL_BASE]
    ser = [Lm.load_series(s, hold) for s in syms]
    F = np.array([x[0] for x in ser])
    QV = np.array([x[1] for x in ser])
    FU = np.array([x[2] for x in ser])
    nd = F.shape[1]
    days = C.T0 + C.DAY * np.arange(nd, dtype=np.int64)
    return dict(syms=syms, F=F, qv=QV, fund=FU, days=days)


def universe_on(P, d, N=40, min_age=60):
    F = P["F"]
    tv = np.nanmean(P["qv"][:, max(0, d - 29):d + 1], axis=1) if d >= 0 else None
    first = P.setdefault("_first", np.array([np.argmax(~np.isnan(r)) if (~np.isnan(r)).any() else F.shape[1] for r in F]))
    ok = (~np.isnan(F[:, d])) & (d - first >= min_age) & np.isfinite(tv)
    idx = np.where(ok)[0]
    return idx[np.argsort(-tv[idx])][:N]


def signals(P, d, kind):
    F = P["F"]
    if kind == "mom":
        return F[:, d] / F[:, d - 28] - 1
    if kind == "carry":
        f = P["fund"][:, d - 6:d + 1]
        return -np.nanmean(f, axis=1)
    raise ValueError(kind)


def book(P, kind, d0, d1, q=8, cost_mult=1.0, lag=0, rng=None):
    """Weekly returns over rebalance closes in [d0, d1). rng -> shuffled signal (random benchmark)."""
    F, fu, syms = P["F"], P["fund"], P["syms"]
    days = P["days"]
    wd = days.astype("datetime64[ms]").astype("datetime64[D]").astype(int)  # 1970-01-01 = Thursday
    reb = [d for d in range(max(d0, 30), d1 - 7) if wd[d] % 7 == 3]   # Sunday candles (close = Monday 00:00 UTC)
    prev_w = {}
    out, starts = [], []
    for d in reb:
        ds = d + lag
        U = universe_on(P, d)
        s = signals(P, d, kind)[U]
        good = ~np.isnan(s)
        U, s = U[good], s[good]
        if len(U) < 2 * q:
            continue
        if rng is not None:
            s = rng.permutation(s)
        o = np.argsort(-s)
        longs, shorts = U[o[:q]], U[o[-q:]]
        w = {i: 1.0 / q for i in longs}
        for i in shorts:
            w[i] = w.get(i, 0) - 1.0 / q
        r = 0.0
        for i, wi in w.items():
            for dd in range(ds + 1, ds + 8):
                if dd >= F.shape[1] or np.isnan(F[i, dd]) or np.isnan(F[i, dd - 1]):
                    continue
                f = fu[i, dd]
                r += wi * ((F[i, dd] / F[i, dd - 1] - 1) - (0.0 if np.isnan(f) else f))
        turn = 0.0
        for i in set(w) | set(prev_w):
            hs = 0.0001 if syms[i] in ("BTCUSDT", "ETHUSDT") else 0.0003
            turn += abs(w.get(i, 0) - prev_w.get(i, 0)) * (0.0005 + hs)
        r -= cost_mult * turn
        prev_w = w
        out.append(r)
        starts.append(d)
    return np.array(out), np.array(starts)


def nw_t(r, lag=4):
    r = np.asarray(r); n = len(r); mu = r.mean(); x = r - mu
    g = np.dot(x, x) / n
    for k in range(1, lag + 1):
        g += 2 * (1 - k / (lag + 1)) * np.dot(x[k:], x[:-k]) / n
    return mu / np.sqrt(g / n)
