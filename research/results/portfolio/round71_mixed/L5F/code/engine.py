"""L5F engine: per-coin minute arrays, quarter-hour opening taker-imbalance z, per-mark trade outcomes.
Everything is cut at ts < 2025-01-01."""
import os, glob, numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
NPZ = os.path.join(R, "data", "qh_imbalance", "npz")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT"]
M0 = 1577836800 // 60          # 2020-01-01 minute
M1 = 1735689600 // 60          # 2025-01-01 minute (exclusive)
NM = M1 - M0
ND = NM // 1440                # 1827 days
IS_END_DAY = 731               # 2022-01-01
TAKER = 5.0


def load_minutes(sym):
    c = np.full(NM, np.nan); v = np.full(NM, np.nan); tb = np.full(NM, np.nan)
    for f in sorted(glob.glob(os.path.join(NPZ, f"{sym}_*.npz"))):
        z = np.load(f)
        m = z["m"].astype(np.int64) - M0
        k = (m >= 0) & (m < NM)
        c[m[k]] = z["c"][k]; v[m[k]] = z["v"][k]; tb[m[k]] = z["tb"][k]
    return c, v, tb


def fill_fwd5(c):
    """price at minute i, or the nearest later bar within 5 minutes."""
    out = c.copy()
    for j in range(1, 6):
        nxt = np.full(NM, np.nan); nxt[:-j] = c[j:]
        bad = np.isnan(out); out[bad] = nxt[bad]
    return out


def imbalance_z(v, tb, offset=0):
    """z of the imbalance of the 1m bar opening at quarter-hour mark + offset minutes, vs the same slot on days
    d-30..d-1 (>= 25 valid, sd > 0). Returns (I, z) as days x 96 arrays."""
    idx = np.arange(ND * 96) * 15 + offset
    vv = v[idx]; tt = tb[idx]
    with np.errstate(invalid="ignore", divide="ignore"):
        I = np.where(vv > 0, (2 * tt - vv) / vv, np.nan).reshape(ND, 96)
    ok = ~np.isnan(I)
    X = np.where(ok, I, 0.0)
    c1 = np.concatenate([np.zeros((1, 96)), np.cumsum(X, 0)]); c2 = np.concatenate([np.zeros((1, 96)), np.cumsum(X * X, 0)])
    cn = np.concatenate([np.zeros((1, 96)), np.cumsum(ok, 0)])
    z = np.full((ND, 96), np.nan)
    d = np.arange(30, ND)
    n = cn[d] - cn[d - 30]; s1 = c1[d] - c1[d - 30]; s2 = c2[d] - c2[d - 30]
    with np.errstate(invalid="ignore", divide="ignore"):
        mu = s1 / n; var = (s2 - n * mu * mu) / (n - 1); sd = np.sqrt(var)
        zz = (I[d] - mu) / sd
    zz[(n < 25) | ~(sd > 1e-9)] = np.nan
    z[d] = zz
    return I, z


def funding_cum(sym):
    a = np.loadtxt(os.path.join(R, "data", "binance", "funding", f"{sym}.csv"), delimiter=",", skiprows=1, ndmin=2)
    a = a[a[:, 0] < 1735689600000]
    return a[:, 0], np.concatenate([[0.0], np.cumsum(a[:, 1])])


def fund_between(ft, fc, t_entry_ms, t_exit_ms):
    """sum of funding rates for stamps in (entry, exit]."""
    i0 = np.searchsorted(ft, t_entry_ms, side="right"); i1 = np.searchsorted(ft, t_exit_ms, side="right")
    return fc[i1] - fc[i0]


def coin_panel(sym, ranks, horizons=(4, 12), lat=1, offset=0):
    """Per quarter-hour mark (flattened days*96): z, long gross return (bp, price only), long funding (bp),
    round-trip cost (bp), for each H. Entry = close of the bar opening at mark + offset + lat (lat=1 is the
    declared entry: price ~ mark + 2 min); exit = close of the bar opening at entry_bar + 60 H."""
    c, v, tb = load_minutes(sym)
    cf = fill_fwd5(c)
    I, z = imbalance_z(v, tb, offset)
    marks = np.arange(ND * 96) * 15 + offset
    e = marks + lat
    pe = cf[np.minimum(e, NM - 1)]
    ft, fc = funding_cum(sym)
    if sym in ("BTCUSDT", "ETHUSDT"):
        hs = np.ones(ND)
    else:
        r = ranks[sym]; hs = np.where(r < 20, 3.0, 5.0)
    cost = 2 * (TAKER + hs[marks // 1440])
    out = {"z": z.ravel(), "I": I.ravel(), "cost": cost, "mark": marks, "day": marks // 1440}
    for H in horizons:
        x = e + int(round(60 * H))
        valid = x < NM
        px = np.full(len(e), np.nan); px[valid] = cf[x[valid]]
        g = (px / pe - 1) * 1e4
        tE = (M0 + e + 1) * 60000; tX = (M0 + x + 1) * 60000
        f = fund_between(ft, fc, tE, tX) * 1e4
        out[f"g{H}"] = g; out[f"f{H}"] = f; out[f"x{H}"] = x
    return out


def select_trades(P, k, H):
    """one position per coin at a time; returns indices of marks traded and side."""
    z = P["z"]; g = P[f"g{H}"]; x = P[f"x{H}"]; e = P["mark"] + 1
    cand = np.where((np.abs(z) >= k) & ~np.isnan(g))[0]
    taken = []; free_at = -1
    for i in cand:
        if P["mark"][i] >= free_at:
            taken.append(i); free_at = x[i] + 1
    taken = np.array(taken, dtype=int)
    return taken, np.sign(z[taken])


def net_of(P, idx, side, H, cost_mult=1.0):
    return side * P[f"g{H}"][idx] - side * P[f"f{H}"][idx] - cost_mult * P["cost"][idx]


def cl_t(x, g):
    """cluster-robust t of the mean of x, clusters g."""
    n = len(x)
    if n < 3: return np.nan
    m = x.mean()
    u, inv = np.unique(g, return_inverse=True)
    s = np.bincount(inv, weights=x - m)
    G = len(u)
    var = (s ** 2).sum() / n ** 2 * G / max(G - 1, 1)
    return m / np.sqrt(var) if var > 0 else np.nan
