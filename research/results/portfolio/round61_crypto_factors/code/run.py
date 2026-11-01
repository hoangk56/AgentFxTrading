import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, factors as X
C = X.C
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
P = X.panel(syms)
def era(e):
    a, b = C.ERAS[e]; return int(np.searchsorted(P['days'], a)), int(np.searchsorted(P['days'], b))
R = {}
for kind in ('mom', 'carry'):
    for e in ('IS', 'VAL'):
        d0, d1 = era(e)
        r, st = X.book(P, kind, d0, d1); R[(kind, e)] = r
        y = C.years(P['days'][st])
        r15, _ = X.book(P, kind, d0, d1, cost_mult=1.5); rl, _ = X.book(P, kind, d0, d1, lag=1)
        rs = np.array([X.book(P, kind, d0, d1, rng=np.random.default_rng(s))[0].mean() for s in range(200)])
        print('%-5s %-3s n %d mean %+.2f%%/wk sd %.2f%% SRwk %.3f t_nw %.2f | x1.5 %+.2f late %+.2f | random beaten %.0f%% (med %+.2f) | yrs %s' % (
            kind, e, len(r), 100 * r.mean(), 100 * r.std(ddof=1), r.mean() / r.std(ddof=1), X.nw_t(r), 100 * r15.mean(), 100 * rl.mean(),
            100 * np.mean(rs < r.mean()), 100 * np.median(rs), {int(k): round(100 * r[y == k].sum(), 1) for k in np.unique(y)}), flush=True)
for e in ('IS', 'VAL'):
    a, b = R[('mom', e)], R[('carry', e)]; n = min(len(a), len(b)); c = 0.5 * (a[:n] + b[:n])
    print('X3    %-3s mean %+.2f%%/wk SRwk %.3f t_nw %.2f corr(mom,carry) %.2f' % (e, 100 * c.mean(), c.mean() / c.std(ddof=1), X.nw_t(c), np.corrcoef(a[:n], b[:n])[0, 1]))
