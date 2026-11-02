"""Stream Q: derivative-vs-derivative basis on Binance (rules declared in ../HYPOTHESES_Q.md).
Loads 1h klines on one global hourly grid 2020-01-01..2024-12-31 (every series cut at ts < 2025-01-01 at load).
Q1 = COIN-M perp vs USDT-M perp; Q2 = delivery future (COIN-M or USDT-M quarterly) vs USDT-M perp, term premium removed
with the trailing median of the annualised basis; Q2b = last-24 h convergence to delivery."""
import csv, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "..", "..", "..", "..")
CM = os.path.join(RES, "data", "binance_cm")
BB = os.path.join(RES, "data", "binance_basis")
BF = os.path.join(RES, "data", "binance", "funding")
H = 3600000
M = 60000
DAY = 86400000
CUT = 1735689600000
T0 = 1577836800000
J0, J1 = T0 // H, CUT // H
N = J1 - J0
YR = 365.25 * DAY
ERAS = {"IS": (T0, 1640995200000), "VAL": (1640995200000, CUT)}
MIN_TRADES = 20
WIN, WIN_MIN = 168, 120
FEE = 0.0005


def _read(path):
    with open(path) as f:
        r = csv.reader(f); next(r)
        a = np.array([x for x in r], dtype=float)
    if len(a):
        a = a[(a[:, 0] < CUT) & (a[:, 0] >= T0)]
    return a


def series(path):
    """Hourly o, c, n arrays on the global grid (nan where missing)."""
    A = _read(path)
    o, c, nn = (np.full(N, np.nan) for _ in range(3))
    if len(A):
        j = (A[:, 0] // H).astype(int) - J0
        o[j], c[j], nn[j] = A[:, 1], A[:, 4], A[:, 7]
    return dict(o=o, c=c, n=nn)


def fcum(path):
    """Cumulative funding on the hour grid; path may be a list (stamps de-duplicated by hour)."""
    fund = np.zeros(N)
    paths = path if isinstance(path, list) else [path]
    seen = set()
    for path in paths:
        if not (path and os.path.exists(path)):
            continue
        F = _read(path)
        if len(F):
            jj0 = np.rint(F[:, 0] / H).astype(int)
            keep = np.array([j not in seen for j in jj0], bool)
            seen |= set(jj0.tolist())
            F = F[keep]
        if len(F):
            jj = np.rint(F[:, 0] / H).astype(int) - J0
            m = (jj >= 0) & (jj < N)
            np.add.at(fund, jj[m], F[m, 1])
    return np.cumsum(fund)


def um_funding_path(sym):
    for p in (os.path.join(BF, sym + ".csv"), os.path.join(BB, "funding", sym + ".csv")):
        if os.path.exists(p):
            return p
    return None


def hs(sym, market):
    big = sym.startswith("BTC") or sym.startswith("ETH")
    perp = sym.endswith("_PERP") or (market == "um" and "_" not in sym)
    if market == "um":
        return (0.00005 if big else 0.0002) if perp else 0.00015
    if perp:
        return 0.0001 if big else 0.0003
    return 0.0002 if big else 0.0005


def trailing_median(y):
    med = np.full(N, np.nan)
    from numpy.lib.stride_tricks import sliding_window_view
    W = sliding_window_view(y[:-1], WIN)
    cnt = (~np.isnan(W)).sum(1)
    with np.errstate(all="ignore"):
        mm = np.nanmedian(W, axis=1)
    mm[cnt < WIN_MIN] = np.nan
    med[WIN:] = mm
    return med


def expiry_ms(sym):
    d = re.search(r"_(\d{6})$", sym).group(1)
    return int(np.datetime64(f"20{d[:2]}-{d[2:4]}-{d[4:]}T08:00", "ms").astype(np.int64))


def _um_cache():
    cache = {}

    def get(coin):
        if coin not in cache:
            sym = coin + "USDT"
            p = os.path.join(CM, "um_klines_1h", sym + ".csv")
            if not os.path.exists(p):
                p = os.path.join(BB, "perp_1h", sym + ".csv")
            s = series(p) if os.path.exists(p) else None
            if s is not None:
                s["sym"] = sym
                s["fcum"] = fcum(um_funding_path(sym))
            cache[coin] = s
        return cache[coin]
    return get


def build_pair(kind, coin, Asym, Amarket, A, U, afc=None):
    valid = (A["n"] >= MIN_TRADES) & (U["n"] >= MIN_TRADES) & (A["c"] > 0) & (U["c"] > 0)
    with np.errstate(all="ignore"):
        base = np.where(valid, np.log(A["c"] / np.where(valid, U["c"], 1.0)), np.nan)
    hours = (J0 + np.arange(N)) * H
    if kind == "Q1":
        w = np.ones(N)
        xmax, exp = N, None
    else:
        exp = expiry_ms(Asym)
        tau = (exp - (hours + H)) / YR          # years to expiry at the close of hour j
        w = np.where(tau > 0, tau, np.nan)
        xmax = int((exp // H) - J0 - 2)         # exit no later than 2 h before expiry
    with np.errstate(all="ignore"):
        y = base / w
    med = trailing_median(y)
    d = base - med * w
    return dict(kind=kind, coin=coin, A=Asym, Amarket=Amarket, U=U["sym"], Ao=A["o"], Ac=A["c"], Uo=U["o"], Uc=U["c"],
                base=base, w=w, med=med, d=d, xmax=xmax, exp=exp, afc=afc, ufc=U["fcum"], hours=hours,
                hsA=hs(Asym, Amarket), hsU=hs(U["sym"], "um"))


def load():
    """Returns list of pairs: Q1 (COIN-M perp vs USDT-M perp) and Q2 (quarterlies vs USDT-M perp)."""
    um = _um_cache()
    pairs = []
    d1 = os.path.join(CM, "cm_klines_1h")
    for f in sorted(os.listdir(d1)):
        if not f.endswith(".csv"):
            continue
        sym = f[:-4]
        coin = sym.split("USD_")[0]
        U = um(coin)
        if U is None:
            continue
        A = series(os.path.join(d1, f))
        if sym.endswith("_PERP"):
            afc = fcum([os.path.join(CM, "cm_fundingRate_-", f), os.path.join(CM, "cm_funding_dapi", f)])
            pairs.append(build_pair("Q1", coin, sym, "cm", A, U, afc))
        else:
            pairs.append(build_pair("Q2", coin, sym, "cm", A, U))
    d2 = os.path.join(CM, "um_klines_1h")
    if os.path.isdir(d2):
        for f in sorted(os.listdir(d2)):
            sym = f[:-4]
            if not f.endswith(".csv") or "_" not in sym:
                continue
            coin = sym.split("USDT_")[0]
            U = um(coin)
            A = series(os.path.join(d2, f))
            pairs.append(build_pair("Q2", coin, sym, "um", A, U))
    return pairs


def simulate(pairs, kind, k, Hh, lag=0):
    """1h screen of the declared rule. Entry hour e = h + 1 + lag (priced later on 1m bars at e*H + 1 min), exit hour x.
    Returns dict of arrays (pair index, h, e, x, side) with side = +1 long A / short USDT-M perp, -1 the reverse."""
    out = {f: [] for f in ("pi", "h", "e", "x", "side", "d")}
    kk = k / 1e4
    for pi, p in enumerate(pairs):
        if p["kind"] != kind:
            continue
        d, base, w, med = p["d"], p["base"], p["w"], p["med"]
        with np.errstate(invalid="ignore"):
            ok = ~np.isnan(d) & (np.abs(d) > kk)
            if kind == "Q2":
                ok &= p["w"] >= 3 / 365.25
        ev = np.where(ok)[0]
        busy = -1
        for h in ev:
            e = h + 1 + lag
            if e <= busy or e >= min(N, p["xmax"]):
                continue
            if np.isnan(p["Ao"][e]) or np.isnan(p["Uo"][e]):
                continue
            s = np.sign(d[h])
            tgt = d[h] / 2
            last = min(e + Hh, p["xmax"], N - 1)
            x = None
            for cc in range(e, last):
                r = base[cc] - med[h] * w[cc]
                if not np.isnan(r) and s * r <= s * tgt:
                    x = cc + 1
                    break
            if x is None:
                x = last
            y = x
            while y < min(N, x + 24, p["xmax"] + 1) and (np.isnan(p["Ao"][y]) or np.isnan(p["Uo"][y])):
                y += 1
            if y >= N or np.isnan(p["Ao"][y]) or np.isnan(p["Uo"][y]) or y <= e:
                continue
            x = y
            busy = x - 1
            for f_, v in (("pi", pi), ("h", h), ("e", e), ("x", x), ("side", -s), ("d", d[h])):
                out[f_].append(v)
    return {f: np.array(v) for f, v in out.items()}


def legs_net(p, e, x, side, Ae, Ax, Ue, Ux, cost_mult=1.0):
    """Net per unit notional for side (+1 long A, short U). Prices given (1h opens or 1m opens)."""
    price = side * ((Ax / Ae - 1) - (Ux / Ue - 1))
    fu = side * (p["ufc"][x] - p["ufc"][e])          # short U receives U funding when side = +1
    if p["afc"] is not None:
        fu = fu - side * (p["afc"][x] - p["afc"][e])  # long A pays A funding
    cost = cost_mult * (4 * FEE + 2 * (p["hsA"] + p["hsU"]))
    return price, fu, np.full(np.shape(price), cost)


def q2b_events(pairs, k):
    """Last-24 h convergence: signal at the close of the hour ending 24 h before expiry."""
    out = []
    for pi, p in enumerate(pairs):
        if p["kind"] != "Q2":
            continue
        h = int(p["exp"] // H - J0 - 25)       # hour h closes at exp - 24 h
        if h < 0 or h >= N:
            continue
        b = p["base"][h]
        if np.isnan(b) or abs(b) <= k / 1e4:
            continue
        out.append((pi, h, -np.sign(b), b))
    return out


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
