"""Round 59 B2 registered HOLD look (PREREG_B2_binance_hyperliquid.md). Run once: python -I b2_hold.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, xvenue as X
C = X.C
syms = [l.strip() for l in open('hl_top30.txt') if l.strip()]
P = X.load('hl', syms, hold=True)
U, rank = C.universe(P, N=30)
cash = X.fed_funds(P['days'])
d0, d1 = C.era_slice(P, 'HOLD')
y = C.years(P['days'][d0:d1])
out = {}
for nm, kw in (('base', {}), ('x1.5', {'cost_mult': 1.5}), ('late', {'lag': 1})):
    r, eps, ex, dep = X.simulate(P, U, d0=d0, d1=d1, cash=cash, **kw); out[nm] = (r, eps, ex)
r, eps, ex = out['base']; st = C.stats(r); sx = C.stats(ex)
rs = [C.stats(X.random_book(P, U, eps, d0, d1, rng=np.random.default_rng(s)))['sharpe_a'] for s in range(500)]
beat = np.mean(np.array(rs) < st['sharpe_a'])
py = {int(k): float(r[y == k].sum()) for k in np.unique(y)}
print('HOLD days %d net ann %.2f%% vol %.2f%% t_nw %.2f | excess over cash ann %.2f%% t_nw %.2f | episodes %d' % (st['n'], 100 * st['ann'], 100 * st['vol'], st['t_nw'], 100 * sx['ann'], sx['t_nw'], len(eps)))
print('per year %', {k: round(100 * v, 2) for k, v in py.items()})
print('x1.5 ann %.2f%%  late ann %.2f%%  random beaten %.1f%%  worst days %s' % (100 * out['x1.5'][0].mean() * 365, 100 * out['late'][0].mean() * 365, 100 * beat, np.round(100 * np.sort(r)[:4], 3)))
bars = {'1 net > 0, t_nw >= 2.5, excess over cash > 0': st['ann'] > 0 and st['t_nw'] >= 2.5 and sx['ann'] > 0,
        '2 x1.5 > 0 and late > 0': out['x1.5'][0].mean() > 0 and out['late'][0].mean() > 0,
        '3 every HOLD year > 0': all(v > 0 for v in py.values()),
        '4 beats >= 80 % random': beat >= 0.8}
for k, v in bars.items(): print('  ', 'PASS' if v else 'FAIL', k)
print('VERDICT:', 'PASS' if all(bars.values()) else 'FAIL')
