"""Calibrate the OKX funding reconstruction on the IS month 2021-09 (choice of lag fixed here); report the VAL fit
(2022-01-16..2022-12-31, BTC / ETH) as a check only. Run: python -I calib.py"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d3

S09, E09 = 1630454400000, 1633046400000
SV, EV = 1642291200000, 1672531200000


def match(c, lag, a, b):
    hh = d3.okx_hourly(c)
    if hh is None:
        return None
    rt, rr = d3.recon_stamps(hh, lag)
    fr = d3.rd(os.path.join(d3.OKX, c + "_funding.csv"))
    m = (fr[:, 0] >= a) & (fr[:, 0] < b)
    real = dict(zip(fr[m, 0].astype(np.int64), fr[m, 1]))
    rec = dict(zip(rt, rr))
    k = sorted(set(real) & set(rec))
    if len(k) < 20:
        return None
    x = np.array([real[t] for t in k]); y = np.array([rec[t] for t in k])
    return len(k), x.mean() * 1e4, y.mean() * 1e4, np.corrcoef(x, y)[0, 1], np.abs(x - y).mean() * 1e4


if __name__ == "__main__":
    print("coin lag | 2021-09: n, realised mean bp/8h, recon mean, corr, MAE bp")
    best = {0: [], 1: []}
    for c in d3.COINS:
        for lag in (0, 1):
            r = match(c, lag, S09, E09)
            if r:
                best[lag].append(r[3])
                print(c, lag, "| n %d real %.3f rec %.3f corr %.3f mae %.3f" % r)
    for lag in (0, 1):
        print("lag", lag, "mean corr 2021-09", np.mean(best[lag]) if best[lag] else None)
    print("VAL check (not used to choose):")
    for c in ("BTC", "ETH"):
        for lag in (0, 1):
            r = match(c, lag, SV, EV)
            if r:
                print(c, lag, "| n %d real %.3f rec %.3f corr %.3f mae %.3f" % r)
