"""Daily P&L correlation of an X cell (1m-priced net, by exit UTC day) with C3 (r by exit day), IS / VAL only.
usage: python corr_c3.py <split> <cell>"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xv  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out')
C3 = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/trades_C3_gotobi_jpy_basket.csv'
split, cell = sys.argv[1], sys.argv[2]
T = dict(np.load(os.path.join(OUT, f'trades1m_{split}_{cell}.npz')))
ok = np.isfinite(T['net1m'])
# exit day: entry time + hold hours
xd = ((T['t'] + (T['x'] - T['e']) * xv.H) // xv.DAY)[ok]
xn = T['net1m'][ok]
c3 = {}
for r in csv.DictReader(open(C3)):
    d = np.datetime64(r['t_out_utc'][:10], 'D').astype(np.int64)
    if d * xv.DAY >= xv.CUT:
        continue
    c3[d] = c3.get(d, 0.0) + float(r['r'])
for era in ('IS', 'VAL'):
    a, b = xv.SPLITS[split][era]
    days = np.arange(max(a, 1577836800000) // xv.DAY, b // xv.DAY)
    xs = np.zeros(len(days))
    np.add.at(xs, np.searchsorted(days, xd[(xd >= days[0]) & (xd <= days[-1])]), xn[(xd >= days[0]) & (xd <= days[-1])])
    cs = np.array([c3.get(d, 0.0) for d in days])
    both = (xs != 0) & (cs != 0)
    print(era, 'calendar corr', round(float(np.corrcoef(xs, cs)[0, 1]), 3), 'days both active', int(both.sum()),
          'corr on both-active days', round(float(np.corrcoef(xs[both], cs[both])[0, 1]), 3) if both.sum() > 2 else None)
