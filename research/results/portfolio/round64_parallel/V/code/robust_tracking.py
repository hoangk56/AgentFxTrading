"""Tracking shortfall ex crash windows (B's own list: 2022-05 LUNA, 2022-11 FTX) and share of events with shortfall > 0."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracking  # noqa: E402


def ms(s):
    return int((np.datetime64(s) - np.datetime64('1970-01-01')) / np.timedelta64(1, 'ms'))


CRASH = [(ms('2022-05-01'), ms('2022-06-01')), (ms('2022-11-01'), ms('2022-12-01'))]

for v in ('bybit', 'okx', 'kucoin'):
    ev = tracking.coins.val_events()
    B, V = {}, {}
    sf, gh = [], []
    for perp, sp, h, e, x in ev:
        if any(a <= h < b for a, b in CRASH):
            continue
        c = tracking.coins.base_of(sp)
        Bb = B.setdefault(sp, tracking.load_binance(sp))
        Vv = V.setdefault(c, tracking.load_venue(v, c))
        if all(t in Vv and t in Bb for t in (h, e, x)):
            import math
            pre = [math.log(Vv[t][1] / Bb[t][1]) for t in range(h - 24 * 3600000, h, 3600000) if t in Vv and t in Bb]
            if len(pre) >= 12:
                med = float(np.median(pre))
                gh.append(1e4 * (math.log(Vv[h][1] / Bb[h][1]) - med))
                sf.append(1e4 * (math.log(Vv[x][0] / Vv[e][0]) - math.log(Bb[x][0] / Bb[e][0])))
    sf, gh = np.array(sf), np.array(gh)
    print(f'{v}: ex-crash n {len(sf)}  shortfall mean {sf.mean():.1f} median {np.median(sf):.1f} share>0 {np.mean(sf > 0):.2f}'
          f'  gap_h mean {gh.mean():.1f} median {np.median(gh):.1f}  corr(gap_h, shortfall) {np.corrcoef(gh, sf)[0, 1]:.2f}')
