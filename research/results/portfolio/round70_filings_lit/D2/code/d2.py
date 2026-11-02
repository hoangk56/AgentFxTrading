"""Round 70 D2: long Deribit inverse perp / short Binance USDT perp, daily book (declared in ../HYPOTHESES_D2.md).
All series cut at ts < 2025-01-01 at load. Run with python -I."""
import os, csv
import numpy as np

DATA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
DER = os.path.join(DATA, "deribit_funding")
# HOLD switch (D2_HOLD=1) exists only for the coordinator's single registered HOLD run; never set by this stream.
HOLD = os.environ.get("D2_HOLD") == "1"
CUT = 1793318400000 if HOLD else 1735689600000  # 2026-10-30 00:00 UTC (HOLD end, covers 2026-10-29) / 2025-01-01
SUF = "hold_" if HOLD else ""
H = 3600000
DAY = 86400000
T0 = 1577836800000 - 40 * DAY  # 2019-11-22 (warm-up for the 7-day signal)
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, 1735689600000)}
if HOLD:
    ERAS["HOLD"] = (1735689600000, CUT)

FEE_B, HS_B = 0.0005, 0.0001
FEE_D, HS_D = 0.00075, 0.0001
SPOT = 0.0010


def _read(p):
    with open(p) as f:
        r = csv.reader(f)
        next(r)
        a = np.array([x for x in r], dtype=float)
    return a[a[:, 0] < CUT]


def hourly(a, col, nh):
    """Values on an hourly grid from T0 (index = (t - T0) / H), NaN where missing."""
    out = np.full(nh, np.nan)
    i = np.round((a[:, 0] - T0) / H).astype(int)
    m = (i >= 0) & (i < nh)
    out[i[m]] = a[m, col]
    return out


def load(asset):
    nh = (CUT - T0) // H + 1  # includes the 2025-01-01 00:00 hour end (= close of the last 2024 bar)
    der_f = _read(os.path.join(DER, f"funding_{SUF}{asset}-PERPETUAL.csv"))
    der_c = _read(os.path.join(DER, f"chart1h_{SUF}{asset}-PERPETUAL.csv"))
    # HOLD: the coordinator's copy of binance_1h_full extended to 2026-10-29 (coord/hold_binance_1h.py); else unchanged
    bpath = (os.path.join(DATA, "deribit_funding", "hold_binance_1h", f"{asset}USDT.csv") if HOLD
             else os.path.join(DATA, "binance_1h_full", "1h", f"{asset}USDT.csv"))
    bin_c = _read(bpath)
    bin_f = _read(os.path.join(DATA, "binance", "funding", f"{asset}USDT.csv"))
    X = {}
    # hour-end grids: value at index k refers to time T0 + k H
    X["S"] = hourly(der_f, 1, nh)                 # Deribit index at hour end
    X["i1"] = hourly(der_f, 2, nh)                # Deribit funding over the hour ending here
    # 1h bars are stamped at open; their close is the price at open + 1h
    sh = lambda a, c: hourly(np.column_stack([a[:, 0] + H, a[:, c]]), 1, nh)
    X["FD"], X["FDh"], X["FDl"] = sh(der_c, 4), sh(der_c, 2), sh(der_c, 3)
    X["FB"], X["FBh"], X["FBl"] = sh(bin_c, 4), sh(bin_c, 2), sh(bin_c, 3)
    X["rB"] = hourly(bin_f, 1, nh)                # Binance stamp rate at its hour (NaN = no stamp)
    X["rB"][np.isnan(X["rB"])] = 0.0
    X["nh"] = nh
    return X


def daily(X):
    """Daily arrays; mark d = T0 + d DAY (00:00 UTC). Day d = (mark d, mark d+1]."""
    nd = (X["nh"] - 1) // 24 + 1
    idx = np.arange(nd) * 24  # hour index of mark d
    D = {"days": T0 + np.arange(nd) * DAY}
    for k in ("FD", "FB", "S"):
        v = X[k].copy()
        # forward-fill a missing hour at a mark from the previous hour (rare); count them
        miss = np.isnan(v[idx])
        D["miss_" + k] = int(miss[nd // 2:].sum())
        for j in np.where(miss)[0]:
            for b in range(1, 4):
                if idx[j] - b >= 0 and not np.isnan(v[idx[j] - b]):
                    v[idx[j]] = v[idx[j] - b]
                    break
        D[k] = v[idx]
    fbu = np.zeros(nd); fb = np.zeros(nd); fd_coin = np.zeros(nd); fd = np.zeros(nd)
    hiB = np.full(nd, np.nan); loD = np.full(nd, np.nan); hiD = np.full(nd, np.nan); loB = np.full(nd, np.nan)
    sigB = np.zeros(nd); sigD = np.zeros(nd)
    for d in range(nd - 1):
        h = slice(idx[d] + 1, idx[d] + 25)  # hours ending in (mark d, mark d+1]
        r = X["rB"][h]
        p = X["FB"][h]
        p = np.where(np.isnan(p), D["FB"][d], p)
        fbu[d] = np.sum(r * p)          # USD per coin short
        fb[d] = np.sum(r)
        i1 = np.nan_to_num(X["i1"][h])
        s = X["S"][h]
        s = np.where(np.isnan(s), D["S"][d], s)
        fd_coin[d] = np.sum(i1 / s)     # coins per USD of V
        fd[d] = np.sum(i1)
        hiB[d] = np.nanmax(X["FBh"][h]); loB[d] = np.nanmin(X["FBl"][h])
        hiD[d] = np.nanmax(X["FDh"][h]); loD[d] = np.nanmin(X["FDl"][h])
        # signal info for the decision at mark d+1: hours ending in (mark d - 1h, mark d+1 - 1h]
        g = slice(idx[d], idx[d] + 24)
        sigB[d + 1] = np.sum(X["rB"][g]); sigD[d + 1] = np.sum(np.nan_to_num(X["i1"][g]))
    D.update(fbu=fbu, fb=fb, fd_coin=fd_coin, fd=fd, hiB=hiB, loB=loB, hiD=hiD, loD=loD)
    # trailing 7-day mean of the daily gap known at mark d (uses days ending by 23:00 before mark d)
    gap = sigB - sigD
    c = np.concatenate([[0.0], np.cumsum(gap)])
    s7 = np.full(nd, np.nan)
    for d in range(8, nd):
        s7[d] = (c[d + 1] - c[d - 6]) / 7.0
    D["s7"] = s7
    D["gap_pure"] = fb - fd
    return D


def simulate(D, d0, d1, on, L=2.0, cost_mult=1.0, N=1.0, usd_coll=False):
    """on[d]: book on during day d (decided at mark d). Marks d0..d1 inclusive; returns days d0..d1-1; the closing
    trades at mark d1 are charged to day d1-1."""
    m = N / L
    fB = cost_mult * (FEE_B + HS_B); fD = cost_mult * (FEE_D + HS_D); fS = cost_mult * SPOT
    FB, FD, S = D["FB"], D["FD"], D["S"]
    n = d1 - d0 + 1
    r = np.zeros(n); fundB = np.zeros(n); fundD = np.zeros(n); cost = np.zeros(n)
    nrebal = 0; ntransfer = 0; liq = []
    # setup at mark d0: buy m of coins (spot), USDT m on Binance, Deribit synthetic USD
    M = m / S[d0]; UB = m; qB = 0.0; V = -M * S[d0]
    cost[0] += fS * m + fD * abs(V)
    state = False
    for k in range(n):
        d = d0 + k
        # trades at mark d
        want = bool(on[d]) if k < n - 1 else False  # flat at the era's last mark
        E_D = M * S[d]
        if (E_D < 0.6 * m or E_D > 1.6 * m or UB < 0.6 * m or UB > 1.6 * m) and k < n - 1:
            mv = abs(E_D - m)
            cost[k] += fS * mv
            M = m / S[d]; UB = m  # surplus / deficit to the bank
            ntransfer += 1
        tgt_qB = N / FB[d] if want else 0.0
        tgt_V = (N - M * S[d]) if want else -M * S[d]
        delta_gap = abs((M * S[d] + V) - (qB * FB[d]))
        if want != state or delta_gap > 0.05 * N or (want and not 0.8 * N <= qB * FB[d] <= 1.2 * N) or k == n - 1:
            cost[k] += fB * abs(tgt_qB - qB) * FB[d] + fD * abs(tgt_V - V)
            if want == state:
                nrebal += 1
            qB, V, state = tgt_qB, tgt_V, want
        if k == n - 1:
            cost[k] += fD * abs(V) + fS * M * S[d]  # close the synthetic USD and sell the coins
            cost[k - 1] += cost[k]
            r[k - 1] -= cost[k]
            break
        # liquidation check over day d (intraday extremes vs equity minus 1 % maintenance)
        if state:
            lossB = qB * (D["hiB"][d] - FB[d])
            xD = max(0.0, 1.0 - D["loD"][d] / FD[d])
            lossD = N * xD
            if lossB > UB - 0.01 * N or lossD > M * S[d] - 0.01 * N:
                liq.append((int(D["days"][d]), round(lossB / N, 3), round(lossD / N, 3)))
        # P&L over day d
        E0 = UB + M * S[d]
        fb_usd = qB * D["fbu"][d]
        UB += -qB * (FB[d + 1] - FB[d]) + fb_usd
        fd_c = V * D["fd_coin"][d]
        M += V * (1.0 / FD[d] - 1.0 / FD[d + 1]) - fd_c
        E1 = UB + M * S[d + 1]
        fundB[k] = fb_usd / N
        fundD[k] = fd_c * S[d + 1] / N
        r[k] = (E1 - E0) / N - cost[k]
    r, fundB, fundD, cost = r[:-1], fundB[:-1], fundD[:-1], cost[:-1]
    price = r + cost - fundB + fundD
    return dict(r=r, fundB=fundB, fundD=fundD, cost=cost, price=price, nrebal=nrebal, ntransfer=ntransfer, liq=liq)


def simulate_usd(D, d0, d1, on, L=2.0, cost_mult=1.0, N=1.0):
    """Descriptive only (not a cell): the 'pure' pair, Deribit collateral treated as USD-stable, long V = N inverse
    (as with USDC collateral, possible on Deribit only from 2022). Same trade / cost rules, no transfers modelled."""
    fB = cost_mult * (FEE_B + HS_B); fD = cost_mult * (FEE_D + HS_D)
    FB, FD, S = D["FB"], D["FD"], D["S"]
    n = d1 - d0
    r = np.zeros(n); fundB = np.zeros(n); fundD = np.zeros(n)
    state = False; qB = 0.0; V = 0.0
    for k in range(n):
        d = d0 + k
        want = bool(on[d])
        tq = N / FB[d] if want else 0.0; tv = N if want else 0.0
        if want != state or (want and not 0.95 * N <= qB * FB[d] <= 1.05 * N):
            r[k] -= fB * abs(tq - qB) * FB[d] + fD * abs(tv - V)
            qB, V, state = tq, tv, want
        fundB[k] = qB * D["fbu"][d] / N
        fundD[k] = V * D["fd_coin"][d] * S[d + 1] / N
        r[k] += (-qB * (FB[d + 1] - FB[d]) + V * (1.0 / FD[d] - 1.0 / FD[d + 1]) * FD[d + 1]) / N + fundB[k] - fundD[k]
    r[-1] -= fB * qB * FB[d1] + fD * abs(V)
    return dict(r=r, fundB=fundB, fundD=fundD, price=r - fundB + fundD)


def stats(r):
    r = np.asarray(r); n = len(r)
    mu, sd = r.mean(), r.std(ddof=1)
    x = r - mu; lag = 10
    g = np.dot(x, x) / n
    for k in range(1, lag + 1):
        g += 2 * (1 - k / (lag + 1)) * np.dot(x[k:], x[:-k]) / n
    t = mu / np.sqrt(g / n) if g > 0 else 0.0
    eq = np.cumsum(r)
    return dict(n=n, ann=mu * 365, vol=sd * np.sqrt(365), sr=(mu / sd * np.sqrt(365)) if sd > 0 else 0.0, t=t,
                maxdd=(eq - np.maximum.accumulate(eq)).min())


def fed_funds(days_ms):
    rows = [x for x in csv.reader(open(os.path.join(DATA, "rates", "DFF.csv")))][1:]
    ff = {x[0]: float(x[1]) for x in rows if x[1] not in ("", ".")}
    out, last = [], 0.0
    for t in days_ms:
        k = str(np.datetime64(int(t), "ms"))[:10]
        last = ff.get(k, last)
        out.append(last / 100 / 365)
    return np.array(out)


def years(days_ms):
    return np.asarray(days_ms, dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
