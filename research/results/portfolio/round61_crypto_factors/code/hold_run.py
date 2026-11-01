"""Round 61 registered HOLD look for X3 (PREREG_X3_crypto_mom_carry.md). Run once: python -I hold_run.py <perp symbols>."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, factors as X
C = X.C
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
P = X.panel(syms, hold=True)
d0 = int(np.searchsorted(P['days'], C.ERAS['HOLD'][0])); d1 = len(P['days'])
res = {}
for nm, kw in (('base', {}), ('x1.5', {'cost_mult': 1.5}), ('late', {'lag': 1})):
    a, st = X.book(P, 'mom', d0, d1, **kw); b, _ = X.book(P, 'carry', d0, d1, **kw)
    res[nm] = (a, b, 0.5 * (a + b), st)
a, b, r, st = res['base']
y = C.years(P['days'][st])
rs = []
for s in range(500):
    g = np.random.default_rng(s)
    rs.append(0.5 * (X.book(P, 'mom', d0, d1, rng=g)[0] + X.book(P, 'carry', d0, d1, rng=g)[0]).mean())
beat = np.mean(np.array(rs) < r.mean())
print('HOLD weeks %d (%s .. %s)' % (len(r), str(np.datetime64(int(P['days'][st[0]]), 'ms'))[:10], str(np.datetime64(int(P['days'][st[-1]]), 'ms'))[:10]))
print('X3 mean %+.3f%%/wk sd %.2f%% SRwk %.3f t_nw %.2f | x1.5 %+.3f late %+.3f | random beaten %.1f%%' % (
    100 * r.mean(), 100 * r.std(ddof=1), r.mean() / r.std(ddof=1), X.nw_t(r), 100 * res['x1.5'][2].mean(), 100 * res['late'][2].mean(), 100 * beat))
print('X3 per year (sum %%):', {int(k): round(100 * r[y == k].sum(), 1) for k in np.unique(y)})
print('reported: X1 mom mean %+.3f%%/wk t_nw %.2f ; X2 carry mean %+.3f%%/wk t_nw %.2f' % (100 * a.mean(), X.nw_t(a), 100 * b.mean(), X.nw_t(b)))
print('worst week %.1f%%, max drawdown (sum) %.1f%%' % (100 * r.min(), 100 * (np.cumsum(r) - np.maximum.accumulate(np.cumsum(r))).min()))
print('DEMO bar (net > 0):', 'PASS' if r.mean() > 0 else 'FAIL')
