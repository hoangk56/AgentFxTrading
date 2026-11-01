import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, factors as X
C = X.C
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
P = X.panel(syms)
c3 = {}
for r in csv.DictReader(open('../../trades_C3_gotobi_jpy_basket.csv')):
    k = r['t_out_utc'][:10]; c3[k] = c3.get(k, 0) + float(r['r'])
def era(e):
    a, b = C.ERAS[e]; return int(np.searchsorted(P['days'], a)), int(np.searchsorted(P['days'], b))
for e in ('IS', 'VAL'):
    d0, d1 = era(e)
    out = {}
    for nm, kw in (('base', {}), ('x1.5', {'cost_mult': 1.5}), ('late', {'lag': 1})):
        a, st = X.book(P, 'mom', d0, d1, **kw); b, _ = X.book(P, 'carry', d0, d1, **kw); out[nm] = 0.5 * (a + b)
    r = out['base']; y = C.years(P['days'][st])
    rs = []
    for s in range(200):
        g = np.random.default_rng(s)
        rs.append(0.5 * (X.book(P, 'mom', d0, d1, rng=g)[0] + X.book(P, 'carry', d0, d1, rng=g)[0]).mean())
    rs = np.array(rs)
    # C3 weekly correlation
    wk = {}
    for k, v in c3.items():
        t = np.datetime64(k, 'ms').astype(np.int64)
        i = np.searchsorted(P['days'][st], t, side='right') - 1
        if 0 <= i < len(st) and t < P['days'][st[i]] + 8 * C.DAY: wk[i] = wk.get(i, 0) + v
    cv = np.array([wk.get(i, 0) for i in range(len(r))])
    print(e, 'n %d mean %+.2f%%/wk SRwk %.3f t_nw %.2f | x1.5 %+.2f late %+.2f | yrs %s | random beaten %.1f%% | worst wk %.1f%% | corr C3 wk %.2f' % (
        len(r), 100 * r.mean(), r.mean() / r.std(ddof=1), X.nw_t(r), 100 * out['x1.5'].mean(), 100 * out['late'].mean(),
        {int(k): round(100 * r[y == k].sum(), 1) for k in np.unique(y)}, 100 * np.mean(rs < r.mean()), 100 * r.min(), np.corrcoef(r, cv)[0, 1]))
