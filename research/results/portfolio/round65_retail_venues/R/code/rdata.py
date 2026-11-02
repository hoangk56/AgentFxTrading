"""Stream R data layer (../HYPOTHESES_R.md). Hour axis as round 63 C: h = hours since H0 (2019-11-01 00:00 UTC),
P[i, h] = close of the 1h bar that opened at h - 1. Daily universe (top 60 by trailing 30-day perp quote volume) and
the trailing 30-day Upbit share. Every series is cut at ts < 2025-01-01 at load (no HOLD)."""
import csv, glob, json, os
import numpy as np

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
UP = os.path.join(R, "upbit")
OUT = os.path.join(R, "korea_hours")
HOUR = 3600000; DAY = 86400000; B4 = 4 * HOUR
H0 = 1572566400000          # 2019-11-01
CUT = 1735689600000         # 2025-01-01 (HOLD start, exclusive)
NH = (CUT - H0) // HOUR
ND = (CUT - H0) // DAY
IS = (1577836800000, 1640995200000)
VAL = (1640995200000, CUT)
EXCL = {"BTCUSDT", "USDCUSDT", "BUSDUSDT", "TUSDUSDT", "USDPUSDT", "FDUSDUSDT", "DEFIUSDT", "FOOTBALLUSDT",
        "BLUEBIRDUSDT", "BTCDOMUSDT", "BTTUSDT"}  # BTT: 2022 redenomination, Upbit code reused (as stream U)
CACHE = os.path.join(OUT, "panel.npz")


def _read(path):
    """Rows cut at t < CUT, columns by header name -> dict of arrays."""
    with open(path) as f:
        r = csv.reader(f)
        hdr = next(r)
        rows = [x for x in r if x]
    if not rows:
        return {k: np.zeros(0) for k in hdr}
    a = np.array([x[:len(hdr)] for x in rows], dtype=float)
    a = a[a[:, 0] < CUT]
    return {k: a[:, j] for j, k in enumerate(hdr)}


def _b1h(sym):
    cands = [os.path.join(R, "binance_1h_full", "1h", sym + ".csv"), os.path.join(R, "binance_basis", "perp_1h", sym + ".csv"),
             os.path.join(UP, "binance", "perp_1h", sym + ".csv")] + glob.glob(os.path.join(R, "binance", "perp_1h", sym + "_*.csv"))
    best = None
    for p in cands:
        if os.path.exists(p):
            a = _read(p)
            if len(a["t"]) and (best is None or a["t"][0] < best["t"][0] or
                                (a["t"][0] == best["t"][0] and len(a["t"]) > len(best["t"]))):
                best = a
    return best


def _funding(sym):
    for p in (os.path.join(R, "binance_basis", "funding", sym + ".csv"), os.path.join(R, "binance", "funding", sym + ".csv"),
              os.path.join(UP, "binance", "funding", sym + ".csv"), os.path.join(R, "upbit_vol", "funding", sym + ".csv")):
        if os.path.exists(p):
            a = _read(p)
            if len(a["t"]):
                return a
    return None


def _daily_qvol():
    files = sorted(glob.glob(os.path.join(R, "binance", "perp_1d", "*.csv")))
    syms = [os.path.basename(f)[:-4] for f in files]
    Q = np.full((len(syms), ND), np.nan)
    first = np.full(len(syms), 10 ** 6, dtype=np.int64)
    for i, f in enumerate(files):
        a = _read(f)
        if not len(a["t"]):
            continue
        d = ((a["t"] - H0) // DAY).astype(np.int64)
        first[i] = d[0]
        m = d >= 0
        Q[i, d[m]] = a["qvol"][m]
    return syms, Q, first


def universe(syms, Q, first, N=60, min_age=60):
    n = len(syms)
    U = np.zeros((n, ND), dtype=bool)
    rk = np.full((n, ND), 9999)
    excl = np.array([s in EXCL for s in syms])
    import warnings
    for d in range(30, ND):
        with np.errstate(invalid="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tv = np.nanmean(Q[:, d - 30:d], axis=1)
        ok = np.isfinite(tv) & (d - first >= min_age) & ~np.isnan(Q[:, d - 1]) & ~excl
        idx = np.where(ok)[0]
        idx = idx[np.argsort(-tv[idx])][:N]
        U[idx, d] = True
        rk[idx, d] = np.arange(len(idx))
    return U, rk


def _upbit_daily(coin):
    p = os.path.join(UP, "m240", coin + ".csv")
    if not os.path.exists(p):
        return None
    a = _read(p)
    if not len(a["t"]):
        return None
    d = ((a["t"] - H0) // DAY).astype(np.int64)
    m = (d >= 0) & ((a["t"] - H0) % B4 == 0)
    krw = np.zeros(ND); cnt = np.zeros(ND)
    np.add.at(krw, d[m], a["krw"][m]); np.add.at(cnt, d[m], 1)
    close = np.full(ND, np.nan)
    last = m & (((a["t"] - H0) % DAY) == 5 * B4)     # bucket 20-24 UTC: close at day end
    close[d[last]] = a["c"][last]
    return dict(krw=krw, cnt=cnt, close=close, first=int(d[m][0]) if m.any() else 10 ** 6)


def build():
    syms_all, Q, first = _daily_qvol()
    U, rk = universe(syms_all, Q, first)
    keep = np.where(U.any(axis=1))[0]
    syms = [syms_all[i] for i in keep] + ["BTCUSDT"]
    U = np.vstack([U[keep], np.zeros((1, ND), dtype=bool)])
    rk = np.vstack([rk[keep], np.full((1, ND), 9999)])
    QD = np.vstack([Q[keep], Q[syms_all.index("BTCUSDT")][None]])
    n = len(syms)
    P = np.full((n, NH + 1), np.nan)
    FR = np.zeros((n, NH + 1))
    nofund = []
    for i, s in enumerate(syms):
        a = _b1h(s)
        h = ((a["t"] - H0) // HOUR).astype(np.int64)
        m = (h >= 0) & ((a["t"] - H0) % HOUR == 0)
        P[i, h[m] + 1] = a["c"][m]
        f = _funding(s)
        if f is None:
            nofund.append(s); continue
        hs = np.round((f["t"] - H0) / HOUR).astype(np.int64)
        m = (hs >= 0) & (hs <= NH)
        np.add.at(FR[i], hs[m], f["rate"][m])
    # KRW -> USD per day: Upbit KRW-BTC close at day end / Binance BTCUSDT close at day end
    ub = _upbit_daily("BTC")
    iB = syms.index("BTCUSDT")
    bclose = P[iB, ((np.arange(ND) + 1) * 24)]
    krwusd = ub["close"] / bclose
    inv = {v: k for k, v in json.load(open(os.path.join(UP, "raw", "map_perp.json"))).items()}
    USD = np.full((n, ND), np.nan)      # Upbit daily value in USD (NaN = no Upbit day), only mapped coins
    UF = np.full(n, 10 ** 6, dtype=np.int64)
    for i, s in enumerate(syms):
        c = inv.get(s)
        if c is None or c in ("BTC", "USDC"):
            continue
        u = _upbit_daily(c)
        if u is None:
            continue
        v = np.where(u["cnt"] >= 6, u["krw"] / krwusd, np.nan)
        v[np.arange(ND) < u["first"]] = np.nan
        USD[i] = v; UF[i] = u["first"]
    np.savez(CACHE, P=P, FR=FR, QD=QD, U=U, rk=rk, USD=USD, UF=UF, syms=np.array(syms), nofund=np.array(nofund))
    return load()


def load():
    if not os.path.exists(CACHE):
        return build()
    z = np.load(CACHE, allow_pickle=False)
    D = {k: z[k] for k in z.files}
    D["syms"] = list(D["syms"]); D["nofund"] = list(D["nofund"])
    return D


def shares(D):
    """[n, ND] trailing 30-day share (days d-30..d-1), NaN if not measured (rules in HYPOTHESES_R.md)."""
    USD, QD, UF = D["USD"], D["QD"], D["UF"]
    n = USD.shape[0]
    S = np.full((n, ND), np.nan)
    cu = np.concatenate([np.zeros((n, 1)), np.cumsum(np.nan_to_num(USD), axis=1)], axis=1)
    cn = np.concatenate([np.zeros((n, 1)), np.cumsum(np.isfinite(USD), axis=1)], axis=1)
    cq = np.concatenate([np.zeros((n, 1)), np.cumsum(np.nan_to_num(QD), axis=1)], axis=1)
    d = np.arange(30, ND)
    num = cu[:, d] - cu[:, d - 30]; cnt = cn[:, d] - cn[:, d - 30]; den = cq[:, d] - cq[:, d - 30]
    with np.errstate(invalid="ignore", divide="ignore"):
        s = num / den
    ok = (cnt >= 20) & (den > 0) & (UF[:, None] <= d[None, :] - 30)
    S[:, 30:] = np.where(ok, s, np.nan)
    return S


if __name__ == "__main__":
    D = build()
    S = shares(D)
    U = D["U"]
    dd = np.arange(ND)
    for era, (a, b) in (("IS", IS), ("VAL", VAL)):
        m = (H0 + dd * DAY >= a) & (H0 + dd * DAY < b)
        nA = (U & np.isfinite(S))[:, m].sum(0)
        print(era, "universe size mean", U[:, m].sum(0).mean(), "A size mean/min/max", nA.mean(), nA.min(), nA.max())
    print("symbols", len(D["syms"]), "no funding", D["nofund"])
