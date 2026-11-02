"""Stream U data layer (declared in ../HYPOTHESES_U.md). Upbit KRW 240-min value + Binance perp 1h close / qvol on
hour and 4h grids. Copies the needed pieces of stream K's kdata (read-only use of K's data files). Cut ts < 2025-01-01."""
import csv, glob, json, os
import numpy as np

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
UP = os.path.join(R, "upbit")
UV = os.path.join(R, "upbit_vol")
H = 3600000; B4 = 4 * H; M = 60000; DAY = 86400000
CUT = 1735689600000
G0 = 1576800000000  # 2019-12-20 00:00 UTC (K's pull floor)
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, CUT)}
GRID = np.arange(G0, CUT, B4)          # 4h bucket starts
NH = (CUT - G0) // H                   # hours on the 1h grid
MAP = json.load(open(os.path.join(UP, "raw", "map_perp.json")))
SKIP = {"BTC", "USDC", "BTT"}


def scale(sym):
    return 1000.0 if sym.startswith("1000") and not sym.startswith("1000000") else 1.0


def _read(path, ncol=None):
    with open(path) as f:
        r = csv.reader(f); next(r)
        a = np.array([x[:ncol] if ncol else x for x in r if x], dtype=float)
    if len(a):
        a = a[a[:, 0] < CUT]
    return a


def upbit(coin):
    p = os.path.join(UP, "m240", coin + ".csv")
    return _read(p) if os.path.exists(p) else None


def b1h(sym):
    """t, o, h, l, c, qvol of the local file that starts earliest (as kdata.b1h, plus qvol)."""
    cands = [os.path.join(R, "binance_1h_full", "1h", sym + ".csv"), os.path.join(R, "binance_basis", "perp_1h", sym + ".csv"),
             os.path.join(UP, "binance", "perp_1h", sym + ".csv")] + glob.glob(os.path.join(R, "binance", "perp_1h", sym + "_*.csv"))
    best = None
    for p in cands:
        if os.path.exists(p):
            with open(p) as f:
                hdr = f.readline().strip().split(",")
            a = _read(p)
            if len(a):
                a = a[:, [hdr.index(x) for x in ("t", "o", "h", "l", "c", "qvol")]]
            if len(a) and (best is None or a[0, 0] < best[0, 0] or (a[0, 0] == best[0, 0] and len(a) > len(best))):
                best = a
    return best


def hour_grid(a, col):
    out = np.full(NH, np.nan)
    if a is None or not len(a):
        return out
    idx = ((a[:, 0] - G0) // H).astype(np.int64)
    ok = ((a[:, 0] - G0) % H == 0) & (idx >= 0) & (idx < NH)
    out[idx[ok]] = a[ok, col]
    return out


def four_grid(a, col):
    out = np.full(len(GRID), np.nan)
    if a is None or not len(a):
        return out
    idx = ((a[:, 0] - G0) // B4).astype(np.int64)
    ok = ((a[:, 0] - G0) % B4 == 0) & (idx >= 0) & (idx < len(GRID))
    out[idx[ok]] = a[ok, col]
    return out


def status():
    st = {}
    for line in open(os.path.join(UP, "pull_m240.out")):
        p = line.split()
        if len(p) == 4:
            st[p[0]] = p[3]
    return st


def k2_L():
    out = {}
    with open(os.path.join(UP, "k2_events.csv")) as f:
        for x in csv.DictReader(f):
            out[x["coin"]] = int(x["L"])
    return out


def funding(sym):
    for p in (os.path.join(R, "binance_basis", "funding", sym + ".csv"), os.path.join(R, "binance", "funding", sym + ".csv"),
              os.path.join(UP, "binance", "funding", sym + ".csv"), os.path.join(UV, "funding", sym + ".csv")):
        if os.path.exists(p):
            a = _read(p, 2)
            if len(a):
                return a
    return np.zeros((0, 2))


def btc_1m():
    return np.load(os.path.join(UP, "binance", "btc_1m.npz"))["c"]


def cl_t(x, day):
    x = np.asarray(x, dtype=float); n = len(x)
    if n < 3:
        return np.nan
    mu = x.mean()
    u, inv = np.unique(day, return_inverse=True)
    s = np.bincount(inv, weights=x - mu)
    G = len(u)
    var = (s ** 2).sum() / n ** 2 * G / max(G - 1, 1)
    return mu / np.sqrt(var) if var > 0 else np.nan


def year_of(t):
    return np.asarray(t, dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970


def panel():
    """Per coin: 4h arrays D (share deviation), krw24, RU (alt/BTC 24h run-up at T), ok (exclusions passed), and the
    hourly close array hc (close of the 1h bar starting at hour h, price-scaled). T = GRID + 4h."""
    from numpy.lib.stride_tricks import sliding_window_view as swv
    st = status(); L2 = k2_L()
    hb = hour_grid(b1h("BTCUSDT"), 4)
    T = GRID + B4
    hT = (T - G0) // H                      # hour index of T; close at T = bar starting hT - 1
    coins = []
    for coin, sym in sorted(MAP.items()):
        if coin in SKIP:
            continue
        u = upbit(coin)
        b = b1h(sym)
        if u is None or not len(u) or b is None or not len(b):
            continue
        krw = four_grid(u, 5)
        k24 = np.full(len(GRID), np.nan)
        k24[5:] = swv(krw, 6).sum(axis=1)      # NaN if any bucket missing
        hq = hour_grid(b, 5); hc = hour_grid(b, 4) / scale(sym)
        q24 = np.full(len(GRID), np.nan)
        cq = np.concatenate([[0], np.cumsum(np.nan_to_num(hq))]); cn = np.concatenate([[0], np.cumsum(np.isfinite(hq))])
        lo = hT - 24; hi = np.minimum(hT, NH)
        okk = lo >= 0
        n = np.zeros(len(GRID)); s = np.zeros(len(GRID))
        n[okk] = cn[hi[okk]] - cn[lo[okk]]; s[okk] = cq[hi[okk]] - cq[lo[okk]]
        good = okk & (n >= 22) & (s > 0)
        q24[good] = s[good] * 24.0 / n[good]
        S = np.log(k24) - np.log(q24)
        # trailing median of S over the 180 buckets ending at T - 24 h (index j-6-179 .. j-6)
        D = np.full(len(GRID), np.nan)
        W = swv(S, 180)                       # W[i] = S[i .. i+179]; for bucket j we need i = j - 185
        cnt = np.isfinite(W).sum(axis=1)
        import warnings
        with np.errstate(all="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            med = np.nanmedian(np.where(cnt[:, None] >= 120, W, np.nan), axis=1)
        j = np.arange(185, len(GRID))
        D[j] = S[j] - med[j - 185]
        c1 = np.where(hT - 1 < NH, hc[np.minimum(hT - 1, NH - 1)], np.nan)
        c0 = np.where(hT - 25 >= 0, hc[np.maximum(hT - 25, 0)], np.nan)
        b1 = hb[np.minimum(hT - 1, NH - 1)]; b0 = hb[np.maximum(hT - 25, 0)]
        RU = (c1 / c0) / (b1 / b0) - 1
        ok = np.isfinite(D) & (k24 >= 1e9) & np.isfinite(RU)
        if st.get(coin) == "history_start":
            ok &= ~((T >= u[0, 0]) & (T < u[0, 0] + 30 * DAY))
        if coin in L2:
            ok &= ~((T >= L2[coin]) & (T < L2[coin] + 30 * DAY))
        coins.append(dict(coin=coin, sym=sym, D=D, k24=k24, RU=RU, ok=ok, hc=hc))
    return coins, hb, T


def events(coins, T, k, ru, hold):
    """Event list (coin idx, j) for one cell: D >= ln k [and RU >= 10 %], 7-day cooldown per coin."""
    lk = np.log(k)
    out = []
    lim = CUT - (2 * H + hold * H + 10 * M)
    for ci, c in enumerate(coins):
        sig = c["ok"] & (c["D"] >= lk) & (T < lim)
        if ru:
            sig &= c["RU"] >= 0.10
        last = -10 ** 15
        for j in np.flatnonzero(sig):
            if T[j] >= last + 7 * DAY:
                out.append((ci, int(j))); last = T[j]
    return out
