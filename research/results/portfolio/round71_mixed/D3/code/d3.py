"""Round 71 D3: long OKX USDT swap / short Binance USDT-M perp (OKX funding has no interest leg 2020-24).
Cells and rules as declared in ../HYPOTHESES_D3.md (18:01 UTC + amendment 18:09 UTC). Every series is cut at
ts < 2025-01-01 at load. Run: python -I d3.py [calib|run]"""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "data"))
OKX = os.path.join(DATA, "funding_formulas", "okx")
BIN = os.path.join(DATA, "binance")
DAY = 86400000
H = 3600000
T0 = 1577836800000            # 2020-01-01
CUT = 1735689600000           # 2025-01-01: nothing at or after this is loaded
ND = (CUT - T0) // DAY        # 1827 days
IS = (0, (1640995200000 - T0) // DAY)
VAL = ((1640995200000 - T0) // DAY, ND)
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "LTC", "LINK", "BCH", "DOT"]
FEE = 0.0005
HS = {"BTC": 0.0001, "ETH": 0.0001}
OKX_REAL_GAP = (1633046400000, 1642291200000)   # 2021-10-01 .. 2022-01-16: no realised OKX files
CAP = 0.0075


def rd(path):
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        rows = [x for x in r if x]
    return np.array(rows, dtype=float) if rows else np.zeros((0, 2))


def funding_by_day(t, rate):
    """Holding day d gets stamps in (00:00 d, 00:00 d+1]; stamps >= CUT dropped."""
    t = np.asarray(t, dtype=np.int64)
    m = (t < CUT) & (t > T0 - DAY)
    d = (t[m] - 1 - T0) // DAY
    out = np.zeros(ND)
    ok = (d >= 0) & (d < ND)
    np.add.at(out, d[ok], rate[m][ok])
    cnt = np.zeros(ND)
    np.add.at(cnt, d[ok], 1)
    return out, cnt


def okx_hourly(c):
    tr, ix = os.path.join(OKX, c + "_trade_1h.csv"), os.path.join(OKX, c + "_index_1h.csv")
    if not (os.path.exists(tr) and os.path.exists(ix)):
        return None
    a, b = rd(tr), rd(ix)
    a = a[a[:, 0] < CUT]
    b = b[b[:, 0] < CUT]
    common, ia, ib = np.intersect1d(a[:, 0].astype(np.int64), b[:, 0].astype(np.int64), return_indices=True)
    # premium observed at the close of the hour candle (open time + 1h)
    return dict(t_close=common + H, prem=a[ia, 4] / b[ib, 4] - 1.0, close=a[ia, 4], low=a[ia, 3], high=a[ia, 2],
                t_open=common)


def recon_stamps(hh, lag=0):
    """Reconstructed OKX stamps at 00/08/16: mean premium over (T - 8h - lag*8h, T - lag*8h]."""
    if hh is None:
        return np.zeros(0, dtype=np.int64), np.zeros(0)
    tc, p = hh["t_close"], hh["prem"]
    first = (tc.min() // (8 * H) + 1) * 8 * H
    T = np.arange(first, min(tc.max(), CUT - 1) + 1, 8 * H, dtype=np.int64)
    idx = {int(x): i for i, x in enumerate(tc)}
    out_t, out_r = [], []
    for s in T:
        e = s - lag * 8 * H
        vals = [p[idx[int(e - k * H)]] for k in range(8) if int(e - k * H) in idx]
        if len(vals) >= 6:
            out_t.append(s)
            out_r.append(np.clip(np.mean(vals), -CAP, CAP))
    return np.array(out_t, dtype=np.int64), np.array(out_r)


def load(lag=0, clean=False):
    """Panel per coin: mark prices at 00:00 of each day (index d = mark at start of day d, length ND + 1), daily high /
    low of holding day d, funding per holding day for both venues."""
    P = {"BM": np.full((10, ND + 1), np.nan), "OM": np.full((10, ND + 1), np.nan), "BH": np.full((10, ND), np.nan),
         "OL": np.full((10, ND), np.nan), "fB": np.zeros((10, ND)), "fO": np.zeros((10, ND)),
         "nB": np.zeros((10, ND)), "nO": np.zeros((10, ND)), "recon": np.zeros((10, ND), bool)}
    for i, c in enumerate(COINS):
        k = rd(os.path.join(BIN, "perp_1d", c + "USDT.csv"))
        hh_raw = okx_hourly(c)
        if clean and hh_raw is not None:
            # sensitivity added after the first run (2026-11-01 ~18:36 UTC): drop thin early OKX prints
            keep = (np.abs(hh_raw["prem"]) < 0.02) & (hh_raw["t_open"] >= hh_raw["t_open"].min() + 30 * DAY)
            hh_raw = {kk: vv[keep] for kk, vv in hh_raw.items()}
        k = k[k[:, 0] < CUT]
        d = ((k[:, 0] - T0) // DAY).astype(int)
        ok = (d >= 0) & (d < ND)
        P["BM"][i, d[ok] + 1] = k[ok, 4]
        P["BH"][i, d[ok]] = k[ok, 2]
        f = rd(os.path.join(BIN, "funding", c + "USDT.csv"))
        P["fB"][i], P["nB"][i] = funding_by_day(f[:, 0], f[:, 1])
        # OKX marks: 1Dutc candles where present, else 1H close of the 23:00 candle
        hh = hh_raw
        if hh is not None:
            dd = ((hh["t_open"] - T0) // DAY).astype(int)
            last = (hh["t_open"] % DAY) == 23 * H
            m = last & (dd >= 0) & (dd < ND)
            P["OM"][i, dd[m] + 1] = hh["close"][m]
            for j in np.where((dd >= 0) & (dd < ND))[0]:
                v = P["OL"][i, dd[j]]
                P["OL"][i, dd[j]] = hh["low"][j] if np.isnan(v) else min(v, hh["low"][j])
        o = rd(os.path.join(OKX, c + "_1d.csv"))
        o = o[o[:, 0] < CUT]
        d = ((o[:, 0] - T0) // DAY).astype(int)
        ok = (d >= 0) & (d < ND)
        P["OM"][i, d[ok] + 1] = o[ok, 4]
        P["OL"][i, d[ok]] = o[ok, 3]
        # OKX funding: realised where files exist; reconstructed for days without realised stamps
        fr = rd(os.path.join(OKX, c + "_funding.csv"))
        fo, no = funding_by_day(fr[:, 0], fr[:, 1])
        rt, rr = recon_stamps(hh, lag)
        fo2, no2 = funding_by_day(rt, rr)
        use_rec = (no < 2) & (no2 >= 2)
        P["fO"][i] = np.where(use_rec, fo2, fo)
        P["nO"][i] = np.where(use_rec, no2, no)
        P["recon"][i] = use_rec
    # holding day d is valid when both marks (d, d+1) and funding on both venues exist
    P["valid"] = (np.isfinite(P["BM"][:, :-1]) & np.isfinite(P["BM"][:, 1:]) & np.isfinite(P["OM"][:, :-1]) &
                  np.isfinite(P["OM"][:, 1:]) & (P["nB"] >= 1) & (P["nO"] >= 1))
    if clean:
        ratio = P["OM"] / P["BM"] - 1
        okr = np.abs(ratio) < 0.02
        P["valid"] &= okr[:, :-1] & okr[:, 1:]
    P["days"] = T0 + np.arange(ND) * DAY
    return P


def dff_daily():
    r = {}
    with open(os.path.join(DATA, "rates", "DFF.csv")) as f:
        next(f)
        for line in f:
            a, b = line.strip().split(",")
            if b:
                r[a] = float(b)
    days = np.arange(ND) * DAY + T0
    out = np.zeros(ND)
    last = 0.0
    for j, t in enumerate(days.astype("datetime64[ms]").astype("datetime64[D]").astype(str)):
        last = r.get(t, last)
        out[j] = last / 100 / 365
    return out


def f7_mask(P):
    gap = P["fB"] - P["fO"]
    on = np.zeros_like(gap, dtype=bool)
    v = P["valid"]
    for i in range(10):
        for d in range(8, ND):
            w = slice(d - 8, d - 1)            # holding days d-8 .. d-2
            if v[i, w].sum() >= 5:
                on[i, d] = gap[i, w][v[i, w]].mean() > 0
    return on


def simulate(P, coins, mask, era, cost_mult=1.0, late=0, L=2.0):
    """Daily book over the era; returns dict of arrays (r, funding leg, price leg, costs, transfers) and flags."""
    d0, d1 = era
    idx = [COINS.index(c) for c in coins]
    v = P["valid"][idx][:, d0:d1]
    on = mask[idx][:, d0:d1] & v
    if late:
        on = np.concatenate([np.zeros((len(idx), late), bool), on[:, :-late]], axis=1) & v
    n = d1 - d0
    r = np.zeros(n); fl = np.zeros(n); pl = np.zeros(n); cs = np.zeros(n); tr = np.zeros(n)
    liq = 0
    nel = np.maximum(v.sum(0), 1)
    q = np.zeros(len(idx))
    eqB = np.zeros(len(idx)); eqO = np.zeros(len(idx))
    for j in range(n):
        d = d0 + j
        for k, i in enumerate(idx):
            c = COINS[i]
            hs = HS.get(c, 0.0003)
            unit = (FEE + hs) * cost_mult * 2          # both venues, per unit notional traded
            Ni = 1.0 / nel[j]
            B0, O0 = P["BM"][i, d], P["OM"][i, d]
            want = on[k, j]
            if not want:
                if q[k] != 0 and np.isfinite(B0):
                    cs[j] += abs(q[k]) * B0 * unit
                q[k] = 0.0
                continue
            if q[k] == 0:
                q[k] = Ni / B0
                cs[j] += Ni * unit
                eqB[k] = eqO[k] = Ni / L
            elif abs(q[k] * B0 - Ni) > 0.2 * Ni:
                nq = Ni / B0
                cs[j] += abs(nq - q[k]) * B0 * unit
                q[k] = nq
            B1, O1 = P["BM"][i, d + 1], P["OM"][i, d + 1]
            f_b = q[k] * B0 * P["fB"][i, d]
            f_o = q[k] * O0 * P["fO"][i, d]
            dB = -q[k] * (B1 - B0) + f_b
            dO = q[k] * (O1 - O0) - f_o
            fl[j] += f_b - f_o
            pl[j] += q[k] * ((O1 - O0) - (B1 - B0))
            # liquidation-risk flag: intraday adverse move vs the leg's equity
            adv_b = q[k] * (P["BH"][i, d] - B0) if np.isfinite(P["BH"][i, d]) else 0.0
            adv_o = q[k] * (O0 - P["OL"][i, d]) if np.isfinite(P["OL"][i, d]) else 0.0
            if adv_b > 0.9 * eqB[k] or adv_o > 0.9 * eqO[k]:
                liq += 1
            eqB[k] += dB; eqO[k] += dO
            m = Ni / L
            if not (0.5 * m <= eqB[k] <= 1.5 * m and 0.5 * m <= eqO[k] <= 1.5 * m):
                tot = eqB[k] + eqO[k]
                tr[j] += abs(eqB[k] - tot / 2) * 0.0001
                eqB[k] = eqO[k] = tot / 2
        # close everything at the era's last mark
        if j == n - 1:
            for k, i in enumerate(idx):
                if q[k] != 0:
                    hs = HS.get(COINS[i], 0.0003)
                    cs[j] += abs(q[k]) * P["BM"][i, d + 1] * (FEE + hs) * cost_mult * 2
                    q[k] = 0.0
    r = fl + pl - cs - tr
    return dict(r=r, fl=fl, pl=pl, cs=cs, tr=tr, liq=liq, on_share=on.sum() / max(v.sum(), 1),
                days=P["days"][d0:d1], active=v.any(0))


def nw_t(r, lag=10):
    r = np.asarray(r); n = len(r); mu = r.mean(); x = r - mu
    g = np.dot(x, x) / n
    for k in range(1, lag + 1):
        g += 2 * (1 - k / (lag + 1)) * np.dot(x[k:], x[:-k]) / n
    return mu / np.sqrt(g / n) if g > 0 else 0.0


def summ(r):
    r = np.asarray(r)
    sd = r.std(ddof=1)
    return dict(n=len(r), ann=r.mean() * 365, vol=sd * np.sqrt(365), sh=r.mean() / sd * np.sqrt(365) if sd > 0 else 0,
                t=nw_t(r))


def years(days):
    return days.astype("datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
