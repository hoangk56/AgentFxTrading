"""Per-coin table for B's current universe (out/current_universe_borrow.csv) and VAL-event-weighted coverage today."""
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coins  # noqa: E402
import coverage as cvg  # noqa: E402

V = dict(bybit=cvg.bybit(), okx=cvg.okx(), gate=cvg.gate(), kucoin=cvg.kucoin(), binance_flag=cvg.binance())
cur = coins.current_universe()
G = cvg.D + '/gate/hlr'
gmax = {}
for c in cur:
    p = f'{G}/{c}.json'
    if os.path.exists(p):
        rs = [float(x['rate']) for x in json.load(open(p)).get('rates', []) if x.get('rate')]
        if rs:
            gmax[c] = max(rs) * 8760
with open(cvg.OUT + '/current_universe_borrow.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['coin', 'bybit_rate_yr', 'bybit_cap_usdt', 'okx_rate_yr', 'okx_cap_usdt', 'gate_rate_yr',
                'gate_rate_max100h_yr', 'gate_cap_usdt', 'kucoin_mode', 'binance_margin_pair'])
    for c in cur:
        g = lambda v, k: (lambda n: '' if n is None else round(V[v][n][k], 4))(cvg.names(V[v], c))  # noqa: E731
        kn = cvg.names(V['kucoin'], c)
        w.writerow([c, g('bybit', 'rate_yr'), g('bybit', 'cap_usdt'), g('okx', 'rate_yr'), g('okx', 'cap_usdt'),
                    g('gate', 'rate_yr'), round(gmax.get(c, float('nan')), 4), g('gate', 'cap_usdt'),
                    V['kucoin'][kn]['mode'] if kn else '', int(bool(cvg.names(V['binance_flag'], c)))])
gm = np.array(list(gmax.values()))
print('gate current: max-over-100h rate median %.1f%%/yr, share > 40%%: %.2f, n %d' % (100 * np.median(gm), np.mean(gm > .4), len(gm)))
ev = coins.val_events()
for v, tab in V.items():
    k = sum(1 for _, sp, *_ in ev if cvg.names(tab, coins.base_of(sp)))
    print(f'{v}: VAL events whose coin is borrowable/margin today {k}/{len(ev)} ({100 * k / len(ev):.0f}%)')
both = sum(1 for c in cur if cvg.names(V['bybit'], c) or cvg.names(V['gate'], c))
print('current covered by Bybit or Gate:', both, '/', len(cur))
for c in ('TRB', 'UMA', 'OM', 'REN', 'FTT', 'SRM', 'LUNA', 'PEOPLE'):
    print(c, {v: bool(cvg.names(V[v], c)) for v in V})
