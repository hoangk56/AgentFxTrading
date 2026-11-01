"""Stream BY: B's frozen cheap-basis rule on Bybit spot vs Bybit linear perp (see ../HYPOTHESES_BY.md).
Universe (Bybit point-in-time top-60 by trailing 30-day linear turnover) and loader producing coin dicts in B's format,
so that B's simulate() runs unchanged. Every series is cut at ts < 2025-01-01 at load."""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "..", "..", "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "..", "B", "code"))
import basis as B   # noqa: E402  (B's frozen module: simulate, reltick, cl_t, summarize, by_year)
from universe import trailing_mean, T0, DAY  # noqa: E402  (re-exported from round 58 carry.py)

BD = os.path.join(RES, "data", "bybit_basis")
BYF = os.path.join(RES, "data", "bybit", "funding")
H = 3600000
CUT = 1735689600000
END = CUT
MIN_TURN = 2000.0
assert B.CUT == CUT


def _read(path):
    with open(path) as f:
        r = csv.reader(f); next(r)
        a = np.array([[float(v) for v in x[:7]] for x in r if x], dtype=float)
    if len(a):
        a = a[a[:, 0] < CUT]
    return a


def cands():
    return list(csv.DictReader(open(os.path.join(BD, "cands.csv"))))


def universe(N=60, min_age=60):
    C = cands()
    nd = (END - T0) // DAY
    days = T0 + DAY * np.arange(nd)
    keep, QV, SF = [], [], []
    for r in C:
        lp, sp = os.path.join(BD, "linear_1d", r["perp"] + ".csv"), os.path.join(BD, "spot_1d", r["spot"] + ".csv")
        if not (os.path.exists(lp) and os.path.exists(sp)):
            continue
        A, S = _read(lp), _read(sp)
        if not len(A) or not len(S):
            continue
        q = np.full(nd, np.nan)
        d = ((A[:, 0] - T0) // DAY).astype(int)
        ok = (d >= 0) & (d < nd)
        q[d[ok]] = A[ok, 6]
        keep.append((r["perp"], r["spot"], float(r["fac"]), int(S[0, 0])))
        QV.append(q)
    QV = np.array(QV)
    n = len(keep)
    first = np.array([np.argmax(~np.isnan(q)) if (~np.isnan(q)).any() else nd for q in QV])
    spot_ok = np.array([k[3] for k in keep])[:, None] <= days[None, :]
    age_ok = np.arange(nd)[None, :] - first[:, None] >= min_age
    tv = trailing_mean(QV, 30)
    tv = np.where(spot_ok & age_ok & ~np.isnan(QV) & ~np.isnan(tv), tv, -np.inf)
    U = np.zeros((n, nd), bool)
    R = np.full((n, nd), 9999)
    for d in range(nd):
        o = np.argsort(-tv[:, d])
        g = o[np.isfinite(tv[o, d])][:N]
        U[g, d] = True
        R[g, d] = np.arange(len(g))
    return keep, U, R, days


def write_windows(path):
    keep, U, R, days = universe(60)
    d0 = np.searchsorted(days, 1577836800000)
    with open(path, "w") as f:
        f.write("perp,spot,fac,a_ms,b_ms,first_day,last_day,member_days\n")
        for i, k in enumerate(keep):
            w = np.where(U[i, d0:])[0] + d0
            if not len(w):
                continue
            a = int(days[w[0]]) - 8 * DAY
            b = min(int(days[w[-1]]) + 3 * DAY - 1, CUT - 1)
            f.write(f"{k[0]},{k[1]},{k[2]:g},{a},{b},{int(days[w[0]])},{int(days[w[-1]])},{len(w)}\n")
    return keep, U, R, days


def funding_path(perp):
    for p in (os.path.join(BYF, perp + ".csv"), os.path.join(BD, "funding", perp + ".csv")):
        if os.path.exists(p):
            return p
    return None


def load(only=None):
    keep, U, R, days = universe(60)
    dff = B._dff()
    coins = []
    for i, (perp, spot, fac, _) in enumerate(keep):
        if not U[i].any() or (only is not None and perp not in only):
            continue
        pp, sp = os.path.join(BD, "linear_1h", perp + ".csv"), os.path.join(BD, "spot_1h", spot + ".csv")
        if not (os.path.exists(pp) and os.path.exists(sp)):
            continue
        A, S = _read(pp), _read(sp)
        if len(A) < B.WIN or len(S) < B.WIN:
            continue
        j0 = int(min(A[0, 0], S[0, 0]) // H)
        j1 = int(max(A[-1, 0], S[-1, 0]) // H) + 1
        n = j1 - j0

        def arr(X, col, scale=1.0):
            o = np.full(n, np.nan)
            o[(X[:, 0] // H).astype(int) - j0] = X[:, col] * scale
            return o
        c = dict(perp=perp, spot=spot, fac=fac, j0=j0, n=n,
                 Fo=arr(A, 1), Fh=arr(A, 2), Fl=arr(A, 3), Fc=arr(A, 4), Fn=arr(A, 6),
                 So=arr(S, 1, fac), Sh=arr(S, 2, fac), Sl=arr(S, 3, fac), Sc=arr(S, 4, fac), Sn=arr(S, 6))
        fp = funding_path(perp)
        fund = np.zeros(n)
        c["has_funding"] = fp is not None
        if fp:
            with open(fp) as f:
                r = csv.reader(f); next(r)
                Fd = np.array([[float(x[0]), float(x[1])] for x in r if x], dtype=float)
            if len(Fd):
                Fd = Fd[Fd[:, 0] < CUT]
                jj = np.rint(Fd[:, 0] / H).astype(int) - j0
                m = (jj >= 0) & (jj < n)
                np.add.at(fund, jj[m], Fd[m, 1])
        c["fcum"] = np.cumsum(fund)
        c["tickF"] = B.reltick(A, j0, n)
        c["tickS"] = B.reltick(S, j0, n)
        with np.errstate(invalid="ignore"):
            valid = ((c["tickF"] <= B.MAX_TICK) & (c["tickS"] <= B.MAX_TICK) & (c["Fn"] >= MIN_TURN) & (c["Sn"] >= MIN_TURN)
                     & (c["Fh"] > c["Fl"]) & (c["Sh"] > c["Sl"]) & (c["Fc"] > 0) & (c["Sc"] > 0))
        c["valid"] = valid
        b = np.where(valid, np.log(c["Fc"] / np.where(valid, c["Sc"], 1.0)), np.nan)
        c["b"] = b
        med = np.full(n, np.nan)
        if n > B.WIN:
            from numpy.lib.stride_tricks import sliding_window_view
            W = sliding_window_view(b[:-1], B.WIN)
            cnt = (~np.isnan(W)).sum(1)
            with np.errstate(all="ignore"):
                mm = np.nanmedian(W, axis=1)
            mm[cnt < B.WIN_MIN] = np.nan
            med[B.WIN:] = mm
        c["m"] = med
        hours = (j0 + np.arange(n)) * H
        dayidx = np.searchsorted(days, hours, side="right") - 1
        prev = np.clip(dayidx - 1, 0, U.shape[1] - 1)
        c["inU"] = U[i, prev] & (dayidx >= 1)
        c["rank"] = R[i, prev]
        c["hours"] = hours
        dd = (hours // DAY).astype(np.int64)
        c["cash"] = np.array([dff.get(x, np.nan) for x in dd])
        c["cash"] = np.where(np.isnan(c["cash"]), 0.0, c["cash"])
        coins.append(c)
    return coins


FEES = 2 * 0.0010 + 2 * 0.00055   # Bybit spot taker 0.10 %, linear taker 0.055 %


def trade_net(c, e, x, side, rank, cost_mult=1.0, borrow=0.40):
    """B's trade_net with Bybit fees (31 bp) instead of Binance (30 bp); everything else identical."""
    Fe, Se, Fx, Sx = c["Fo"][e], c["So"][e], c["Fo"][x], c["So"][x]
    price = side * ((Sx / Se - 1) - (Fx / Fe - 1))
    fund = side * (c["fcum"][x] - c["fcum"][e])
    hrs = (x - e).astype(float)
    cost = cost_mult * (FEES + 4 * B.hs_of(rank))
    carry = c["cash"][e] * hrs / 8760 + (side < 0) * borrow * hrs / 8760
    return price, fund, cost, carry


B.trade_net = trade_net   # B.simulate looks trade_net up in its module namespace


if __name__ == "__main__":
    keep, U, R, days = write_windows(os.path.join(BD, "windows.csv"))
    print("candidates with linear + spot daily:", len(keep))
    for y0, y1 in ((1577836800000, 1609459200000), (1609459200000, 1640995200000), (1640995200000, 1672531200000),
                   (1672531200000, 1704067200000), (1704067200000, 1735689600000)):
        a, b = np.searchsorted(days, y0), np.searchsorted(days, y1)
        print(np.datetime64(y0, "ms").astype("datetime64[Y]"), "mean members/day", U[:, a:b].sum(0).mean().round(1),
              "ever", U[:, a:b].any(1).sum())
