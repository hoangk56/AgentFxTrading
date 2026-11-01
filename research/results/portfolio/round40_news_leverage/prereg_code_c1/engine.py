"""Trades for declared cells: entry next CN trading day 01:45 UTC; exits S (07:59 UTC same day) or h CN days later
at 01:45 UTC. IC 2016-24 (cut at load); PRE 2012-15 on Dukascopy bid (USDCNH, AUDUSD, XAUUSD) at mid = bid change."""
import sys, datetime as dt, pickle, os
sys.path.insert(0, "/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r40/C")
import numpy as np
import lib

# risk-off side per target: -1 means "risk-off => short this symbol"
RISK = {"HK50": 1, "USDCNH": -1, "AUDUSD": 1, "JP225": 1, "XAUUSD": -1, "US500": 1}
TARGETS = list(RISK)
HS = ("S", "h1", "h3", "h5")
VAR = {"base": {}, "x15": {"sx": 1.5}, "lat": {"lat": 1}, "late": {}}

_PRE = {}


def load_pre(sym):
    if sym in _PRE:
        return _PRE[sym]
    base = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/duka"
    if sym == "USDCNH":
        ts, b = [], []
        for y in (2012, 2013, 2014, 2015):
            z = np.load(f"{base}/m1_r30/USDCNH_{y}.npz")
            ts.append(z["ts"]); b.append(z["bci"].astype(float))
        ts, b = np.concatenate(ts), np.concatenate(b)
    else:
        z = np.load(f"{base}/m1c/{sym}.npz")
        ts, b = z["ts"], z["bid"].astype(float)
    k = np.isfinite(b) & (b > 0) & (ts < 1451606400000)  # PRE only (< 2016)
    _PRE[sym] = (ts[k], b[k])
    return _PRE[sym]


def pre_trade(sym, side, ti, to, tol=10):
    ts, b = load_pre(sym)
    i = np.searchsorted(ts, ti); j = np.searchsorted(ts, to)
    if i >= len(ts) or j >= len(ts) or ts[i] - ti > tol * 60000 or ts[j] - to > tol * 60000 or j <= i:
        return None
    return side * (b[j] / b[i] - 1) * 1e4


def windows(D, i, h, late=False):
    """signal day index i -> (t_in, t_out) or None"""
    if i + 1 >= len(D):
        return None
    e = D[i + 1]
    hh, mm = (5, 0) if late else (1, 45)
    if h == "S":
        return lib.ms(e, hh, mm), lib.ms(e, 7, 59)
    k = int(h[1])
    if i + 1 + k >= len(D):
        return None
    t_in = lib.ms(e, hh, mm)
    j = i + 1 + k
    while j > i + 1 and lib.ms(D[j], hh, mm) - t_in > 120 * 3600000:  # 5 x 24 h hold cap
        j -= 1
    if j == i + 1:
        return None
    return t_in, lib.ms(D[j], hh, mm)


def all_trades(D, cache):
    """precompute for every CN day i, target, hold: long-side (mid, net) per variant (net for short computed too)."""
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    res = {}
    for sym in TARGETS:
        for h in HS:
            tab = {}
            for i, d in enumerate(D):
                if d.year < 2012:
                    continue
                row = {}
                for vn, kw in VAR.items():
                    w = windows(D, i, h, late=(vn == "late"))
                    if w is None:
                        break
                    if d.year < 2016 or D[i + 1].year < 2016:
                        if sym in ("USDCNH", "AUDUSD", "XAUUSD") and vn == "base" and D[i + 1].year < 2016:
                            m = pre_trade(sym, 1, *w)
                            if m is not None:
                                row["pre"] = m
                        continue
                    for side in (1, -1):
                        kw2 = {k: v for k, v in kw.items()}
                        r = lib.trade(sym, side, w[0], w[1], **kw2)
                        if r is not None:
                            row[(side, vn)] = r
                if row:
                    tab[d] = row
            res[(sym, h)] = tab
            print(sym, h, len(tab), flush=True)
    pickle.dump(res, open(cache, "wb"))
    return res
