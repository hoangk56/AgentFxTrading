"""B1 on IS (2020-06..2021-12) and VAL (2022-24); HOLD stays cut. Usage: python -I b1.py bybit"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, xvenue as X
C = X.C
venue = sys.argv[1]
syms = [l.strip() for l in open('universe_syms.txt') if l.strip()]
P = X.load(venue, syms)
U, rank = C.universe(P, N=30)
cash = X.fed_funds(P['days'])
eras = {'IS': (int(np.searchsorted(P['days'], 1590969600000)), C.era_slice(P, 'IS')[1]), 'VAL': C.era_slice(P, 'VAL')}
if venue == 'hl':
    eras = {'DISC': (int(np.searchsorted(P['days'], 1685577600000)), C.era_slice(P, 'VAL')[1])}
cov = np.mean(~np.isnan(P['F2'][U]))
print('pair coverage of universe days: %.0f%%' % (100 * cov))
for era, (d0, d1) in eras.items():
    y = C.years(P['days'][d0:d1])
    for name, kw in (('base', {}), ('cost1.5', {'cost_mult': 1.5}), ('late1d', {'lag': 1})):
        r, eps, ex, dep = X.simulate(P, U, d0=d0, d1=d1, cash=cash, **kw)
        st = C.stats(r); sx = C.stats(ex)
        print(era, name, 'ann %.2f%% vol %.2f%% tNW %.2f | excess ann %.2f%% tNW %.2f | deployed %.0f%% eps %d' % (
            100 * st['ann'], 100 * st['vol'], st['t_nw'], 100 * sx['ann'], sx['t_nw'], 100 * dep.mean() * 10, len(eps)),
            {int(k): round(100 * r[y == k].sum(), 2) for k in np.unique(y)})
    r, eps, ex, dep = X.simulate(P, U, d0=d0, d1=d1, cash=cash)
    rs = [C.stats(X.random_book(P, U, eps, d0, d1, rng=np.random.default_rng(s)))['sharpe_a'] for s in range(300)]
    print('  random median SRa %.2f, beaten %.1f%%; worst days %s' % (np.median(rs), 100 * np.mean(np.array(rs) < C.stats(r)['sharpe_a']), np.round(100 * np.sort(r)[:4], 3)))
    sides = np.array([e[3] for e in eps]); print('  short-Binance share %.0f%%' % (100 * np.mean(sides > 0)))
    hold = np.array([e[2] - e[1] for e in eps]); print('  median hold %d d' % np.median(hold))
