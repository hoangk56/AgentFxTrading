"""Kraken Futures (no interest leg, no damper): reconstructed funding paid by a long from hourly mark / spot candles,
vs Binance realised funding, by half-year 2021-07..2024-12 (descriptive only, not a cell). Run: python -I kraken_desc.py"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d3

K = os.path.join(d3.DATA, "funding_formulas", "kraken")
SWITCH = 1664452800000   # 2022-09-29 12:00 UTC
H = d3.H

for sym, bsym in (("PI_XBTUSD", "BTCUSDT"), ("PI_ETHUSD", "ETHUSDT")):
    m = d3.rd(os.path.join(K, sym + "_mark_1h.csv")); s = d3.rd(os.path.join(K, sym + "_spot_1h.csv"))
    t, im, is_ = np.intersect1d(m[:, 0].astype(np.int64), s[:, 0].astype(np.int64), return_indices=True)
    ok = t < d3.CUT
    t, prem = t[ok] + H, (m[im, 4] / s[is_, 4] - 1)[ok]          # premium at the hour's close
    pm = dict(zip(t.tolist(), prem.tolist()))
    hours = np.arange(t.min() + 4 * H, d3.CUT, H, dtype=np.int64)
    pay = np.full(len(hours), np.nan)
    for j, h in enumerate(hours):
        if h < SWITCH:
            # 4h period containing h-1h: rate set from the previous 4h window, n = 8, cap 0.1 %/h
            start = ((h - H) // (4 * H)) * 4 * H
            w = [pm.get(int(start - k * H)) for k in range(4)]
            w = [x for x in w if x is not None]
            if len(w) >= 3:
                pay[j] = np.clip(np.mean(w) / 8, -0.001, 0.001)
        else:
            x = pm.get(int(h - H))
            if x is not None:
                pay[j] = np.clip(x / 24, -0.0025, 0.0025)
    fb = d3.rd(os.path.join(d3.BIN, "funding", bsym + ".csv"))
    fb = fb[fb[:, 0] < d3.CUT]
    print(sym, "first hour with premium:", np.datetime64(int(t.min()), "ms"))
    print("  half-year  Kraken long pays (recon) bp/day | Binance long pays bp/day | gap bp/day (%/yr) | share Kraken hourly premium > 0")
    for y in range(2021, 2025):
        for hf in (0, 1):
            a = np.datetime64("%d-%02d-01" % (y, 1 + 6 * hf), "ms").astype(np.int64)
            b = np.datetime64("%d-%02d-01" % (y + hf, 7 if hf == 0 else 1), "ms").astype(np.int64)
            mk = (hours > a) & (hours <= b) & np.isfinite(pay)
            if mk.sum() < 24 * 30:
                continue
            kd = np.nanmean(pay[mk]) * 24 * 1e4
            mb = (fb[:, 0] > a) & (fb[:, 0] <= b)
            ndays = (b - a) / d3.DAY
            bd = fb[mb, 1].sum() / ndays * 1e4
            pp = (np.array([pm.get(int(h)) for h in hours[mk] if int(h) in pm]) > 0).mean()
            print("  %d-H%d   %+6.2f | %+6.2f | %+6.2f (%+5.1f) | %.2f" % (y, hf + 1, kd, bd, bd - kd, (bd - kd) * 3.65, pp))
