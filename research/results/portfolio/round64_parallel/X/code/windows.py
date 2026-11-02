"""Pull windows per coin: B's point-in-time universe membership days (2020-24), merged when gaps <= 8 days, each
window extended 8 days before (168 h warm-up), end <= 2024-12-31 23:59:59 UTC. Uses perp 1d volumes only."""
import os, sys, json
import numpy as np
B = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round63_parallel/B/code'
sys.path.insert(0, B)
from universe import universe, DAY  # noqa

T_IS = 1577836800000
CUT = 1735689600000

def windows():
    keep, U, R, days = universe(60)
    out = {}
    for i, (perp, spot, fac, _) in enumerate(keep):
        if perp in ('BTCUSDT', 'ETHUSDT'):
            continue
        # membership on day d is used for hours of day d+1 (B uses the previous day's universe)
        w = np.where(U[i] & (days >= T_IS - DAY))[0]
        if not len(w):
            continue
        segs = []
        a = b = w[0]
        for d in w[1:]:
            if d - b <= 8:
                b = d
            else:
                segs.append((a, b)); a = b = d
        segs.append((a, b))
        out[spot[:-4]] = dict(perp=perp, spot=spot, fac=fac,
                              win=[(int(max(days[a] + DAY - 8 * DAY, T_IS - 8 * DAY)), int(min(days[b] + 2 * DAY, CUT) - 1))
                                   for a, b in segs])
    return out

if __name__ == '__main__':
    W = windows()
    json.dump(W, open(sys.argv[1], 'w'), indent=0)
    hrs = sum((b - a) // 3600000 for v in W.values() for a, b in v['win'])
    print(len(W), 'coins', hrs, 'coin-hours')
