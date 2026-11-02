"""IS thinness check (declared in HYPOTHESES_X.md): coverage and SIGNAL COUNTS only, no returns.
usage: python count.py  -> out/count.txt"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xv  # noqa: E402
import basis  # noqa: E402

t0 = time.time()
coins = xv.attach_venues(basis.load())
out = []
yrs = range(2020, 2025)
for y in yrs:
    a = np.datetime64(f'{y}-01-01').astype('datetime64[ms]').astype(np.int64)
    b = np.datetime64(f'{y + 1}-01-01').astype('datetime64[ms]').astype(np.int64)
    uh = sum(int((c['inU'] & (c['hours'] >= a) & (c['hours'] < b)).sum()) for c in coins)
    cov = sum(int((c['inU'] & (c['nv'] >= 2) & (c['hours'] >= a) & (c['hours'] < b)).sum()) for c in coins)
    per_v = {v: sum(int((c['inU'] & (c['hours'] >= a) & (c['hours'] < b) &
                         (~np.isnan(c['R'][c['venues'].index(v)]) if v in c['venues'] else False)).sum())
                    for c in coins) for v in xv.VENUES}
    out.append(f'{y}: universe coin-hours {uh}, with >= 2 usable venues {cov} ({cov / max(uh, 1):.1%}); per venue {per_v}')
for k in (30, 60, 100):
    for Hh in (6, 24):
        T = xv.simulate(coins, k, Hh, +1)
        line = [f'cheap k{k}_H{Hh}:']
        for sp in ('main', 'alt'):
            for era in ('IS', 'VAL'):
                m = xv.era_mask(T['t'], sp, era)
                line.append(f'{sp}-{era} n {int(m.sum())} days {len(np.unique(T["t"][m] // xv.DAY))}')
        out.append(' | '.join(line))
out.append(f'coins {len(coins)}, with any venue {sum(1 for c in coins if c["venues"])}; load+count {time.time() - t0:.0f} s')
txt = '\n'.join(out)
print(txt)
open(os.path.join(os.path.dirname(__file__), '..', 'out', 'count.txt'), 'w').write(txt + '\n')
