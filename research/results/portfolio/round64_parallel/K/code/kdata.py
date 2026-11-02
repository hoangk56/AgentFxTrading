"""Stream K data layer: Upbit 240-min candles + Binance perp 1h closes on a 4h grid, funding, 1m fills.
Everything is cut at ts < 2025-01-01 at load."""
import csv, glob, io, json, os, zipfile
import numpy as np

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
UP = os.path.join(R, "upbit")
H = 3600000
B4 = 4 * H
M = 60000
DAY = 86400000
CUT = 1735689600000
G0 = 1576800000000  # 2019-12-20 00:00 UTC
ERAS = {"IS": (1546300800000, 1640995200000), "VAL": (1640995200000, CUT)}  # IS starts 2019 (data from 2019-12)
GRID = np.arange(G0, CUT, B4)  # 4h bucket starts
MAP = json.load(open(os.path.join(UP, "raw", "map_perp.json")))
SCALE = {s: (1000.0 if s.startswith("1000") and not s.startswith("1000000") else 1.0) for s in MAP.values()}


def _read(path, ncol=None):
    with open(path) as f:
        r = csv.reader(f); next(r)
        a = np.array([x[:ncol] if ncol else x for x in r if x], dtype=float)
    if len(a):
        a = a[a[:, 0] < CUT]
    return a


def upbit(coin):
    p = os.path.join(UP, "m240", coin + ".csv")
    if not os.path.exists(p):
        return None
    return _read(p)


def b1h(sym):
    """Binance perp 1h klines (t start, o, h, l, c): the local file that starts earliest."""
    cands = [os.path.join(R, "binance_1h_full", "1h", sym + ".csv"), os.path.join(R, "binance_basis", "perp_1h", sym + ".csv"),
             os.path.join(UP, "binance", "perp_1h", sym + ".csv")] + glob.glob(os.path.join(R, "binance", "perp_1h", sym + "_*.csv"))
    best = None
    for p in cands:
        if os.path.exists(p):
            a = _read(p, 5)
            if len(a) and (best is None or a[0, 0] < best[0, 0] or (a[0, 0] == best[0, 0] and len(a) > len(best))):
                best = a
    return best


def funding(sym):
    for p in (os.path.join(R, "binance_basis", "funding", sym + ".csv"), os.path.join(R, "binance", "funding", sym + ".csv"),
              os.path.join(UP, "binance", "funding", sym + ".csv")):
        if os.path.exists(p):
            a = _read(p, 2)
            if len(a):
                return a
    return np.zeros((0, 2))


def on_grid(a, col, offset):
    """Values of column col of array a (rows keyed by t) at times GRID + offset; NaN where absent."""
    out = np.full(len(GRID), np.nan)
    if a is None or not len(a):
        return out
    idx = ((a[:, 0] - G0 - offset) // B4).astype(np.int64)
    ok = ((a[:, 0] - G0 - offset) % B4 == 0) & (idx >= 0) & (idx < len(GRID))
    out[idx[ok]] = a[ok, col]
    return out


def panel():
    """Per coin dict with 4h arrays: uc (Upbit close), ukrw, bc (Binance close at bucket end), hc1 (Binance close of
    the 1h bar starting at bucket end = 1h-late fill), r (residual premium)."""
    ub = upbit("BTC")
    bb = b1h("BTCUSDT")
    UB = on_grid(ub, 4, 0)
    BB = on_grid(bb, 4, 3 * H)        # 1h bar starting t+3h closes at bucket end
    BB1 = on_grid(bb, 4, 4 * H)       # 1h bar starting at bucket end
    coins = []
    for coin, sym in sorted(MAP.items()):
        if coin in ("BTC", "USDC"):
            continue
        u = upbit(coin)
        if u is None or not len(u):
            continue
        b = b1h(sym)
        if b is None or not len(b):
            continue
        c = dict(coin=coin, sym=sym)
        c["uc"] = on_grid(u, 4, 0)
        c["ukrw"] = on_grid(u, 5, 0)
        c["bc"] = on_grid(b, 4, 3 * H) / SCALE[sym]
        c["hc1"] = on_grid(b, 4, 4 * H) / SCALE[sym]
        c["r"] = np.log(c["uc"] / UB) - np.log(c["bc"] / BB)
        c["uleg"] = np.log(c["uc"] / UB)
        c["bleg"] = np.log(c["bc"] / BB)
        c["first_up"] = u[0, 0]
        c["first_b"] = b[0, 0]
        coins.append(c)
    return coins, dict(UB=UB, BB=BB, BB1=BB1)


def btc_1m():
    """BTCUSDT perp 1m closes keyed by minute index from G0 (from data.binance.vision monthly zips), cached npz."""
    cache = os.path.join(UP, "binance", "btc_1m.npz")
    if os.path.exists(cache):
        return np.load(cache)["c"]
    n = (CUT - G0) // M
    out = np.full(n, np.nan)
    for p in sorted(glob.glob(os.path.join(UP, "binance", "btc_1m_zip", "*.zip"))):
        with zipfile.ZipFile(p) as z:
            for nm in z.namelist():
                for x in csv.reader(io.TextIOWrapper(z.open(nm))):
                    if not x or not x[0].isdigit():
                        continue
                    t = int(x[0])
                    if t > 10 ** 14:
                        t //= 1000
                    if G0 <= t < CUT:
                        out[(t - G0) // M] = float(x[4])
    np.savez_compressed(cache, c=out)
    return out


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
