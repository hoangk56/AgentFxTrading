"""Stream B: perp-spot basis mean reversion on Binance altcoins (rule declared in ../HYPOTHESES_B.md).
Loads 1h perp + spot klines (research/data/binance_basis), cut at 2025-01-01 at load."""
import csv, os
import numpy as np
from universe import universe, DAY

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "..", "..", "..", "..")
BB = os.path.join(RES, "data", "binance_basis")
BF = os.path.join(RES, "data", "binance", "funding")
H = 3600000
CUT = 1735689600000
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, 1735689600000)}
MIN_TRADES = 20
WIN, WIN_MIN = 168, 120
EXCL = {"BTCUSDT", "ETHUSDT"}


def _read(path):
    with open(path) as f:
        r = csv.reader(f); next(r)
        a = np.array([x for x in r], dtype=float)
    if len(a):
        a = a[a[:, 0] < CUT]
    return a


MAX_TICK = 0.0005
BLOCK = 720


def reltick(X, j0, n):
    """Relative tick per 30-day block of hours: smallest positive gap between distinct o/h/l/c prices / median close."""
    out = np.full(n, np.inf)
    jj = (X[:, 0] // H).astype(int) - j0
    blk = jj // BLOCK
    for bk in np.unique(blk):
        w = blk == bk
        v = np.unique(X[w, 1:5].ravel())
        med = np.median(X[w, 4])
        if len(v) < 2 or not med > 0:
            continue
        g = np.diff(v)
        g = g[g > med * 1e-9]
        if len(g):
            lo, hi = bk * BLOCK, min((bk + 1) * BLOCK, n)
            out[lo:hi] = g.min() / med
    return out


def _dff():
    out = {}
    with open(os.path.join(RES, "data", "rates", "DFF.csv")) as f:
        r = csv.reader(f); next(r)
        for d, v in r:
            try:
                out[np.datetime64(d, "D").astype(np.int64)] = float(v) / 100
            except ValueError:
                pass
    return out


def load():
    keep, U, R, days = universe(60)
    dff = _dff()
    coins = []
    for i, (perp, spot, fac, _) in enumerate(keep):
        if perp in EXCL or not U[i].any():
            continue
        pp, sp = os.path.join(BB, "perp_1h", perp + ".csv"), os.path.join(BB, "spot_1h", spot + ".csv")
        if not (os.path.exists(pp) and os.path.exists(sp)):
            continue
        A, B = _read(pp), _read(sp)
        if len(A) < WIN or len(B) < WIN:
            continue
        j0 = int(min(A[0, 0], B[0, 0]) // H)
        j1 = int(max(A[-1, 0], B[-1, 0]) // H) + 1
        n = j1 - j0
        def arr(X, col, scale=1.0):
            o = np.full(n, np.nan)
            o[(X[:, 0] // H).astype(int) - j0] = X[:, col] * scale
            return o
        c = dict(perp=perp, spot=spot, fac=fac, j0=j0, n=n,
                 Fo=arr(A, 1), Fh=arr(A, 2), Fl=arr(A, 3), Fc=arr(A, 4), Fn=arr(A, 7),
                 So=arr(B, 1, fac), Sc=arr(B, 4, fac), Sn=arr(B, 7))
        # funding: stamp at hour boundary j (rounded) -> fund[j]; cumulative for (e, x] sums
        fp = os.path.join(BF, perp + ".csv")
        if not os.path.exists(fp):
            fp = os.path.join(BB, "funding", perp + ".csv")
        fund = np.zeros(n)
        c["has_funding"] = os.path.exists(fp)
        if c["has_funding"]:
            Fd = _read(fp)
            if len(Fd):
                jj = np.rint(Fd[:, 0] / H).astype(int) - j0
                m = (jj >= 0) & (jj < n)
                np.add.at(fund, jj[m], Fd[m, 1])
        c["fcum"] = np.cumsum(fund)
        c["tickF"] = reltick(A, j0, n)
        c["tickS"] = reltick(B, j0, n)
        valid = (c["tickF"] <= MAX_TICK) & (c["tickS"] <= MAX_TICK) & (c["Fn"] >= MIN_TRADES) & (c["Sn"] >= MIN_TRADES) & (c["Fc"] > 0) & (c["Sc"] > 0)
        b = np.where(valid, np.log(c["Fc"] / np.where(valid, c["Sc"], 1.0)), np.nan)
        c["b"] = b
        # trailing median of previous WIN hours
        med = np.full(n, np.nan)
        if n > WIN:
            from numpy.lib.stride_tricks import sliding_window_view
            W = sliding_window_view(b[:-1], WIN)          # window k covers b[k..k+WIN-1] -> reference for hour k+WIN
            cnt = (~np.isnan(W)).sum(1)
            with np.errstate(all="ignore"):
                mm = np.nanmedian(W, axis=1)
            mm[cnt < WIN_MIN] = np.nan
            med[WIN:] = mm
        c["m"] = med
        hours = (j0 + np.arange(n)) * H
        dayidx = np.searchsorted(days, hours, side="right") - 1      # day of the hour
        prev = np.clip(dayidx - 1, 0, U.shape[1] - 1)                  # universe of the previous day
        c["inU"] = U[i, prev] & (dayidx >= 1)
        c["rank"] = R[i, prev]
        c["hours"] = hours
        dd = (hours // DAY).astype(np.int64)
        c["cash"] = np.array([dff.get(x, np.nan) for x in dd])
        c["cash"] = np.where(np.isnan(c["cash"]), 0.0, c["cash"])
        coins.append(c)
    return coins


def hs_of(rank):
    return np.where(rank < 10, 0.0003, 0.0005)


def trade_net(c, e, x, side, rank, cost_mult=1.0, borrow=0.40):
    """Vectorised net per unit notional for entries at open e, exits at open x (index arrays). side +1 rich
    (short perp / long spot), -1 cheap. Returns dict of components."""
    Fe, Se, Fx, Sx = c["Fo"][e], c["So"][e], c["Fo"][x], c["So"][x]
    price = side * ((Sx / Se - 1) - (Fx / Fe - 1))
    fund = side * (c["fcum"][x] - c["fcum"][e])
    hrs = (x - e).astype(float)
    cost = cost_mult * (0.0030 + 4 * hs_of(rank))
    carry = c["cash"][e] * hrs / 8760 + (side < 0) * borrow * hrs / 8760
    return price, fund, cost, carry


def simulate(coins, k, Hh, side, lag=0, cost_mult=1.0, maker=False):
    """Run the declared rule. Returns structured trades list as dict of arrays."""
    out = {f: [] for f in ("ci", "h", "e", "x", "price", "fund", "cost", "carry", "net", "adv", "forced", "t")}
    kk = k / 1e4
    for ci, c in enumerate(coins):
        b, m, n = c["b"], c["m"], c["n"]
        d = b - m
        with np.errstate(invalid="ignore"):
            ev = np.where(c["inU"] & ~np.isnan(d) & (side * d > kk))[0]
        busy = -1
        for h in ev:
            e = h + 1 + lag
            if e <= busy or e >= n:
                continue
            if np.isnan(c["Fo"][e]) or np.isnan(c["So"][e]):
                continue
            tgt = d[h] / 2
            x = None
            last = min(e + Hh, n - 1)
            for cc in range(e, last):
                dc = b[cc] - m[h]
                if not np.isnan(dc) and side * dc <= side * tgt:
                    x = cc + 1
                    break
            if x is None:
                x = e + Hh
            forced = 0
            if x >= n or np.isnan(c["Fo"][min(x, n - 1)]) or np.isnan(c["So"][min(x, n - 1)]):
                # next bar with both opens within 24 h, else delisting-type exit at last closes (approximated by
                # the last bar with both opens valid before x)
                y = x
                while y < min(n, x + 24) and (np.isnan(c["Fo"][y]) or np.isnan(c["So"][y])):
                    y += 1
                if y < n and y < x + 24:
                    x = y
                else:
                    ok = np.where(~np.isnan(c["Fo"][e + 1:min(x, n)]) & ~np.isnan(c["So"][e + 1:min(x, n)]))[0]
                    if not len(ok):
                        continue
                    x = e + 1 + ok[-1]
                    forced = 1
            busy = x - 1
            out["ci"].append(ci); out["h"].append(h); out["e"].append(e); out["x"].append(x)
            out["forced"].append(forced)
            seg = slice(e, x)
            if side > 0:
                adv = np.nanmax(c["Fh"][seg]) / c["Fo"][e] - 1
            else:
                adv = 1 - np.nanmin(c["Fl"][seg]) / c["Fo"][e]
            out["adv"].append(adv)
            out["t"].append(c["hours"][e])
    T = {f: np.array(v) for f, v in out.items()}
    if len(T["e"]):
        P, Fu, C, Ca = [], [], [], []
        for ci in np.unique(T["ci"]):
            w = np.where(T["ci"] == ci)[0]
            c = coins[ci]
            p, f, co, ca = trade_net(c, T["e"][w], T["x"][w], side, c["rank"][T["h"][w]], cost_mult)
            if maker:
                co = np.full(len(w), 0.0019)
            for arr_, v in ((P, p), (Fu, f), (C, co), (Ca, ca)):
                arr_.append((w, v))
        for name, L in (("price", P), ("fund", Fu), ("cost", C), ("carry", Ca)):
            a = np.zeros(len(T["e"]))
            for w, v in L:
                a[w] = v
            T[name] = a
        T["net"] = T["price"] + T["fund"] - T["cost"] - T["carry"]
    return T


def cl_t(x, day):
    x = np.asarray(x); n = len(x)
    if n < 3:
        return np.nan
    mu = x.mean()
    u, inv = np.unique(day, return_inverse=True)
    s = np.bincount(inv, weights=x - mu)
    G = len(u)
    var = (s ** 2).sum() / n ** 2 * G / max(G - 1, 1)
    return mu / np.sqrt(var) if var > 0 else np.nan


def era_mask(T, era):
    a, b = ERAS[era]
    return (T["t"] >= a) & (T["t"] < b)


def summarize(T, era):
    m = era_mask(T, era)
    x = T["net"][m]
    day = T["t"][m] // DAY
    if not len(x):
        return dict(n=0)
    dsum = np.bincount(np.unique(day, return_inverse=True)[1], weights=x)
    return dict(n=int(len(x)), days=int(len(np.unique(day))), net_bp=x.mean() * 1e4, t=cl_t(x, day),
                sr=x.mean() / x.std(ddof=1) if len(x) > 1 else np.nan,
                sr_day=dsum.mean() / dsum.std(ddof=1) if len(dsum) > 1 else np.nan,
                gross_bp=T["price"][m].mean() * 1e4, fund_bp=T["fund"][m].mean() * 1e4,
                cost_bp=T["cost"][m].mean() * 1e4, carry_bp=T["carry"][m].mean() * 1e4,
                hold_h=(T["x"][m] - T["e"][m]).mean(), forced=int(T["forced"][m].sum()),
                adv25=float((T["adv"][m] > 0.25).mean()), adv50=float((T["adv"][m] > 0.5).mean()))


def by_year(T):
    y = np.asarray(T["t"], dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
    return {int(yy): (int((y == yy).sum()), T["net"][y == yy].mean() * 1e4) for yy in np.unique(y)}
