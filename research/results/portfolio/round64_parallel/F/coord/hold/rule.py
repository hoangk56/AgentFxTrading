"""Coordinator re-implementation of the frozen cell T5 idio H60 (PREREG_DRAFT_F), for any window.
Must reproduce stream F's IS / VAL numbers exactly (check mode) before it is used on HOLD."""
import csv, glob, os, datetime as dt
import numpy as np

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", ".."))
MIN, DAY, HOUR, BP = 60000, 86400000, 3600000, 1e4
H0 = 1572566400000  # xs day / hour origin (2019-11-01)


def load_sym(D, s, T0, NM):
    c = np.full(NM, np.nan); o = c.copy(); h = c.copy(); l = c.copy(); n = np.zeros(NM, np.int32); qv = np.zeros(NM)
    for f in sorted(glob.glob(os.path.join(D, f"{s}_*.npz"))):
        z = np.load(f)
        t = z["m"].astype(np.int64) - T0 // MIN
        k = (t >= 0) & (t < NM); t = t[k]
        c[t] = z["c"][k]; o[t] = z["o"][k]; h[t] = z["h"][k]; l[t] = z["l"][k]; n[t] = z["n"][k]; qv[t] = z["qv"][k]
    return c, o, h, l, n, qv


def ret1(c):
    r = np.full(len(c), np.nan); r[1:] = c[1:] / c[:-1] - 1; return r


def px_at(c, last, t):
    NM = len(c); t = np.asarray(t); good = t < NM; tt = np.where(good, t, 0); j = last[tt]
    return np.where((j >= 0) & (tt - j <= 5) & good, c[np.maximum(j, 0)], np.nan)


FUND_DIRS = [os.path.join(R, "data", "binance", "funding")]  # hold_run.py prepends the HOLD funding folder


def funding_hours(sym):
    ps = [os.path.join(d, sym + ".csv") for d in FUND_DIRS if os.path.exists(os.path.join(d, sym + ".csv"))]
    if not ps:
        return None
    p = ps[0]
    rows = list(csv.reader(open(p)))[1:]
    if not rows:
        return None
    a = np.array(rows, dtype=float)
    return np.round((a[:, 0] - H0) / HOUR).astype(np.int64), a[:, 1]


def fund(fh, te_ms, tx_ms):
    if fh is None:
        return np.zeros(len(te_ms))
    hs, fr = fh
    h1 = np.floor((te_ms - H0) / HOUR).astype(np.int64) + 1
    h2 = np.floor((tx_ms - H0) / HOUR).astype(np.int64)
    out = np.zeros(len(te_ms))
    for k in range(len(te_ms)):
        out[k] = fr[(hs >= h1[k]) & (hs <= h2[k])].sum()
    return out


def trades(D, U, RK, usyms, T0, END, syms_to_scan, cut_end):
    """Frozen rule; returns dict of arrays for accepted, de-duplicated trades with entry minute index t (vs T0)."""
    NM = (END - T0) // MIN
    day_of_t = (T0 + np.arange(NM, dtype=np.int64) * MIN - H0) // DAY
    cb = load_sym(D, "BTCUSDT", T0, NM)[0]; rb = ret1(cb)
    out = {k: [] for k in ("sym", "t", "r", "net", "gross", "cost", "late", "ohlc")}
    for s in syms_to_scan:
        if s == "BTCUSDT":
            continue
        i = usyms.index(s)
        c, o, h, l, n, qv = load_sym(D, s, T0, NM)
        if np.isnan(c).all():
            continue
        r = ret1(c)
        idx = np.where(~np.isnan(c), np.arange(NM), -1); np.maximum.accumulate(idx, out=idx); last = idx
        dd = np.clip(day_of_t, 0, U.shape[1] - 1)
        inU = U[i, dd]; rank = RK[i, dd]
        with np.errstate(invalid="ignore"):
            a = np.abs(r)
            m = (a >= 0.05) & inU & np.isfinite(rb) & (np.abs(rb) <= 0.2 * a)
        e = np.where(m)[0]
        e = e[(e >= 1) & (e + 2 + 60 < NM)]
        e = e[T0 + e * MIN < cut_end]
        rr = r[e]; nxt = o[e + 1]; half = c[e - 1] * (1 + rr / 2)
        g = (n[e] >= 10) & (qv[e] > 0) & ~np.isnan(nxt) & np.where(rr < 0, nxt <= half, nxt >= half)
        e = e[g]
        keep = []; lt = -10 ** 9
        for x in e:
            if x - lt > 60:
                keep.append(x); lt = x
        e = np.array(keep, dtype=np.int64)
        if len(e) == 0:
            continue
        rr = r[e]; side = -np.sign(rr)
        pe = c[e + 1]; x = px_at(c, last, e + 61)
        ok = np.isfinite(x / pe)
        e, rr, side, pe, x = e[ok], rr[ok], side[ok], pe[ok], x[ok]
        if len(e) == 0:
            continue
        fh = funding_hours(s)
        te = T0 + (e + 2) * MIN
        f = side * fund(fh, te, te + 60 * MIN)
        hh = np.where(s == "ETHUSDT", 1.0, np.where(rank[e] < 20, 3.0, 5.0)) / BP
        cost = 10 / BP + 4 * hh
        gross = side * (x / pe - 1) - f
        pl = c[e + 2]; xl = px_at(c, last, e + 62)
        fl = side * fund(fh, te + MIN, te + MIN + 60 * MIN)
        late = side * (xl / pl - 1) - fl - cost
        mi = (o[e + 2] + h[e + 2] + l[e + 2] + c[e + 2]) / 4; mo = (o[e + 62] + h[e + 62] + l[e + 62] + c[e + 62]) / 4
        ohlc = side * (mo / mi - 1) - f - cost
        for k, v in (("sym", np.full(len(e), i)), ("t", e), ("r", rr), ("net", gross - cost), ("gross", gross),
                     ("cost", cost), ("late", late), ("ohlc", ohlc)):
            out[k].append(v)
    return {k: (np.concatenate(v) if v else np.zeros(0)) for k, v in out.items()}


def clt(x, day):
    x = np.asarray(x, float); ok = np.isfinite(x); x, day = x[ok], np.asarray(day)[ok]; n = len(x)
    if n < 3:
        return np.nan, np.nan, n
    m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    se = np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n
    return m, m / se, n


def summary(T, T0, label):
    day = (T0 + T["t"].astype(np.int64) * MIN) // DAY
    yr = np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).year for d in day])
    L = []
    m, t, n = clt(T["net"], day); L.append(f"{label} n {n} net {m*BP:+.1f} bp t {t:.2f} median {np.median(T['net'])*BP:+.1f}"
                                        f" S {m/np.std(T['net'], ddof=1):.3f}")
    m15, t15, _ = clt(T["gross"] - 1.5 * T["cost"], day); L.append(f"  x1.5 net {m15*BP:+.1f} t {t15:.2f}")
    ml, tl, nl = clt(T["late"], day); L.append(f"  2 bars late net {ml*BP:+.1f} t {tl:.2f} n {nl}")
    mo, to, no = clt(T["ohlc"], day); L.append(f"  mean-OHLC fills net {mo*BP:+.1f} t {to:.2f} n {no}")
    for y in np.unique(yr):
        q = yr == y; my, ty, ny = clt(T["net"][q], day[q]); L.append(f"  {y}: n {ny} net {my*BP:+.1f} t {ty:.2f}")
    cr = T["r"] < 0
    L.append(f"  crash n {cr.sum()} net {np.mean(T['net'][cr])*BP:+.1f} / spike n {(~cr).sum()} net {np.mean(T['net'][~cr])*BP:+.1f}")
    return L, dict(m=m, t=t, n=n, m15=m15, ml=ml, mo=mo, yr={int(y): float(np.mean(T['net'][yr == y])) for y in np.unique(yr)})
