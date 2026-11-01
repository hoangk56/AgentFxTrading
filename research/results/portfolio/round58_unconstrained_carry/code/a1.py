import sys; sys.path.insert(0, '.')
import numpy as np, carry as C
P = C.load_panel(['BTCUSDT', 'ETHUSDT'])
for i, s in enumerate(P['syms']):
    for era in ('IS', 'VAL'):
        d0, d1 = C.era_slice(P, era)
        r = C.episode_pnl(P, i, d0 - 1, d1 - 1)
        c = 2 * (0.0015 + 2 * 0.0001)
        r = r.copy(); r[0] -= c / 2; r[-1] -= c / 2
        st = C.stats(r)
        f = np.nanmean(P['fund'][i, d0:d1]) * 365
        print(s, era, 'fund %.1f%%/yr' % (100 * f), ' '.join('%s=%.3f' % (k, v) for k, v in st.items()))
        # per year
        yrs = C.years(P['days'][d0:d1])
        print('   ', {int(y): round(100 * r[yrs == y].sum(), 2) for y in np.unique(yrs)})
