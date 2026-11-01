"""Round 58 A: delta-neutral perp funding carry (long spot, short USDT-M perp) on Binance daily data.

Panel loader + book simulator, as declared in ../HYPOTHESES_A.md. HOLD (>= 2025-01-01) is cut at load unless
hold=True; only the registered prereg run passes hold=True.
"""
import csv
import os

import numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "binance")
DAY = 86400000
T0 = 1567296000000          # 2019-09-01 00:00 UTC, day index 0
HOLD_START = 1735689600000  # 2025-01-01
ERAS = {
    "IS": (1577836800000, 1640995200000),    # 2020-01-01 .. 2021-12-31
    "VAL": (1640995200000, 1735689600000),   # 2022-01-01 .. 2024-12-31
    "HOLD": (1735689600000, 1793318400000),  # 2025-01-01 .. 2026-10-30
}


def day_of(ms):
    return (np.asarray(ms, dtype=np.int64) - T0) // DAY


def _read(path):
    with open(path) as f:
        r = csv.reader(f)
        head = next(r)
        rows = [x for x in r]
    if not rows:
        return head, np.zeros((0, len(head)))
    return head, np.array(rows, dtype=float)


def spot_name(perp):
    """Perp symbol -> (spot symbol, price factor perp = factor x spot)."""
    for pre, fac in (("1000000", 1e6), ("1000", 1e3), ("1M", 1e6)):
        if perp.startswith(pre) and not perp[len(pre):][0].isdigit():
            return perp[len(pre):], fac
    return perp, 1.0


def load_panel(syms, hold=False, need_spot=True):
    """Return dict of [n_sym, n_day] arrays: S (spot close x factor), F (perp close), fund (sum of stamps in the UTC day),
    qv (perp quote volume), nstamp; plus 'syms', 'days' (ms of day start)."""
    end = ERAS["HOLD"][1] if hold else HOLD_START
    nd = int((end - T0) // DAY)
    n = len(syms)
    S = np.full((n, nd), np.nan)
    F = np.full((n, nd), np.nan)
    QV = np.full((n, nd), np.nan)
    FU = np.zeros((n, nd))
    NS = np.zeros((n, nd))
    for i, s in enumerate(syms):
        p = os.path.join(DATA, "perp_1d", s + ".csv")
        if os.path.exists(p):
            _, a = _read(p)
            if len(a):
                d = day_of(a[:, 0])
                m = (d >= 0) & (d < nd)
                F[i, d[m]] = a[m, 4]
                QV[i, d[m]] = a[m, 6]
        sp, fac = spot_name(s)
        p = os.path.join(DATA, "spot_1d", sp + ".csv")
        if os.path.exists(p):
            _, a = _read(p)
            if len(a):
                d = day_of(a[:, 0])
                m = (d >= 0) & (d < nd)
                S[i, d[m]] = a[m, 4] * fac
        p = os.path.join(DATA, "funding", s + ".csv")
        if os.path.exists(p):
            _, a = _read(p)
            if len(a):
                d = day_of(a[:, 0])
                m = (d >= 0) & (d < nd)
                np.add.at(FU[i], d[m], a[m, 1])
                np.add.at(NS[i], d[m], 1)
    # funding exists only where we have stamps; mark days with perp but no stamps as NaN funding
    FU[NS == 0] = np.nan
    return dict(S=S, F=F, fund=FU, qv=QV, nstamp=NS, syms=list(syms),
                days=T0 + DAY * np.arange(nd, dtype=np.int64))


def trailing_mean(x, L):
    """Mean over the last L days including today, NaN-aware (needs >= L/2 valid)."""
    v = np.where(np.isnan(x), 0.0, x)
    c = np.where(np.isnan(x), 0.0, 1.0)
    cv = np.cumsum(v, axis=1)
    cc = np.cumsum(c, axis=1)
    sv = cv - np.concatenate([np.zeros((x.shape[0], L)), cv[:, :-L]], axis=1)
    sc = cc - np.concatenate([np.zeros((x.shape[0], L)), cc[:, :-L]], axis=1)
    out = np.where(sc >= max(1, L / 2), sv / np.maximum(sc, 1), np.nan)
    return out


def universe(P, N=30, min_age=60, vol_win=30):
    """Boolean [n, nd]: listed >= min_age days (perp), spot + perp + funding valid today, top N by trailing perp qvol."""
    F, S, qv = P["F"], P["S"], P["qv"]
    n, nd = F.shape
    valid = ~np.isnan(F) & ~np.isnan(S) & (S > 0) & (F > 0)
    first = np.full(n, nd)
    for i in range(n):
        w = np.where(~np.isnan(F[i]))[0]
        if len(w):
            first[i] = w[0]
    age_ok = np.arange(nd)[None, :] - first[:, None] >= min_age
    tv = trailing_mean(qv, vol_win)
    tv = np.where(valid & age_ok, tv, -np.inf)
    tv = np.where(np.isnan(tv), -np.inf, tv)
    U = np.zeros((n, nd), dtype=bool)
    rank = np.zeros((n, nd), dtype=int) + 9999
    for d in range(nd):
        order = np.argsort(-tv[:, d])
        good = order[np.isfinite(tv[order, d])][:N]
        U[good, d] = True
        rank[good, d] = np.arange(len(good))
    return U, rank


def half_spread(sym, rank):
    if sym in ("BTCUSDT", "ETHUSDT"):
        return 0.0001
    return 0.0003 if rank < 10 else 0.0005


def episode_pnl(P, i, e, x):
    """Daily P&L per unit entry notional for a position entered at close of day e, exited at close of day x (> e).
    Returns array of length x - e for days e+1..x (excluding costs)."""
    S, F, fu = P["S"][i], P["F"][i], P["fund"][i]
    d = np.arange(e + 1, x + 1)
    # constant notional (rebalanced daily to 1 unit; rebalancing cost ignored, it is a small fraction of the drift)
    q = 1.0 / S[d - 1]
    dS = S[d] - S[d - 1]
    dF = F[d] - F[d - 1]
    f = np.where(np.isnan(fu[d]), 0.0, fu[d])
    return q * (dS - dF) + q * F[d - 1] * f


def simulate(P, U, rank, L=7, th_in=0.20, th_out=0.0, K=10, cost_mult=1.0, lag=0, only=None, d0=0, d1=None):
    """Run the A2 rule. Returns (book daily returns over [d0, d1), list of episodes (i, e, x, cost_in+out))."""
    F, S = P["F"], P["S"]
    n, nd = F.shape
    d1 = nd if d1 is None else d1
    sig = trailing_mean(P["fund"], L) * 365.0
    if lag:
        sig = np.concatenate([np.full((n, lag), np.nan), sig[:, :-lag]], axis=1)
    allowed = np.ones(n, dtype=bool)
    if only is not None:
        allowed = np.array([s in only for s in P["syms"]])
    book = np.zeros(nd)
    held = {}   # i -> (entry day, cost per side)
    eps = []
    for d in range(d0, d1):
        # 1) mark held positions over day d (entered at close of an earlier day)
        for i in list(held):
            e, c = held[i]
            if np.isnan(F[i, d]) or np.isnan(S[i, d]):
                # data ends: forced exit at the last valid close (d - 1), already marked
                book[d - 1] -= c / K
                eps.append((i, e, d - 1, 2 * c))
                del held[i]
                continue
            q = 1.0 / S[i, d - 1]   # constant notional, see episode_pnl
            f = P["fund"][i, d]
            f = 0.0 if np.isnan(f) else f
            book[d] += (q * ((S[i, d] - S[i, d - 1]) - (F[i, d] - F[i, d - 1])) + q * F[i, d - 1] * f) / K
        if d == d1 - 1:
            break
        # 2) exits at close of d
        for i in list(held):
            s = sig[i, d]
            if np.isnan(s) or s < th_out:
                e, c = held[i]
                book[d] -= c / K
                eps.append((i, e, d, 2 * c))
                del held[i]
        # 3) entries at close of d
        free = K - len(held)
        if free > 0:
            cand = np.where(U[:, d] & allowed & ~np.isnan(sig[:, d]) & (sig[:, d] > th_in))[0]
            cand = [i for i in cand if i not in held and not np.isnan(S[i, d]) and not np.isnan(F[i, d])]
            cand.sort(key=lambda i: -sig[i, d])
            for i in cand[:free]:
                c = cost_mult * (0.0015 + 2 * half_spread(P["syms"][i], rank[i, d]))
                held[i] = (d, c)
                book[d] -= c / K
    # close what is still open at the era end (cost charged on the last day)
    for i, (e, c) in held.items():
        book[d1 - 1] -= c / K
        eps.append((i, e, d1 - 1, 2 * c))
    return book[d0:d1], eps


def stats(r, days_ms=None):
    r = np.asarray(r)
    n = len(r)
    mu, sd = r.mean(), r.std(ddof=1)
    sh = mu / sd if sd > 0 else 0.0
    # Newey-West t (lag 10) on daily returns
    x = r - mu
    lag = 10
    g = np.dot(x, x) / n
    for k in range(1, lag + 1):
        g += 2 * (1 - k / (lag + 1)) * np.dot(x[k:], x[:-k]) / n
    t_nw = mu / np.sqrt(g / n) if g > 0 else 0.0
    eq = np.cumsum(r)
    dd = (eq - np.maximum.accumulate(eq)).min()
    return dict(n=n, ann=mu * 365, vol=sd * np.sqrt(365), sharpe_d=sh, sharpe_a=sh * np.sqrt(365),
                t=sh * np.sqrt(n), t_nw=t_nw, maxdd=dd)


def era_slice(P, era):
    a, b = ERAS[era]
    days = P["days"]
    d0 = int(np.searchsorted(days, a))
    d1 = int(np.searchsorted(days, b))
    return d0, d1


def years(days_ms):
    return np.asarray(days_ms, dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970


def random_book(P, U, rank, eps, d0, d1, K=10, cost_mult=1.0, rng=None):
    """Same episode count and durations as `eps`, coins drawn from that day's universe, entry days drawn at random in
    [d0, d1 - dur). Returns the daily book over [d0, d1)."""
    rng = np.random.default_rng() if rng is None else rng
    book = np.zeros(d1)
    syms = P["syms"]
    for (_, e, x, _) in eps:
        dur = x - e
        if dur <= 0:
            continue
        for _try in range(50):
            e2 = int(rng.integers(d0, max(d0 + 1, d1 - dur)))
            pool = np.where(U[:, e2])[0]
            if not len(pool):
                continue
            i = int(rng.choice(pool))
            x2 = e2 + dur
            seg = slice(e2, x2 + 1)
            if np.isnan(P["S"][i, seg]).any() or np.isnan(P["F"][i, seg]).any():
                continue
            c = cost_mult * (0.0015 + 2 * half_spread(syms[i], rank[i, e2]))
            book[e2 + 1:x2 + 1] += episode_pnl(P, i, e2, x2) / K
            book[e2] -= c / K
            book[x2] -= c / K
            break
    return book[d0:d1]
