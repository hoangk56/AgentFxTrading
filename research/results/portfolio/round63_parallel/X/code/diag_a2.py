"""Post-hoc diagnostic (labelled, not a declared cell): where does A2's gross settle->open drift sit?
Per contract: open(t+1) - settle(t) for M1, M2, M3 (ETPs sell M1, buy M2, don't trade M3), and by roll-dose tercile."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vxdata as V
P, RAW = V.build_panel()
D = P['dates']; ERA, YR = V.era(D)
last = P['K'] == P['N']
d = {k: P['nO' + k] - P['S' + k] for k in '123'}
for e in ('PRE', 'IS', 'VAL'):
    m = (ERA == e) & ~last
    s = []
    for k in '123':
        x = d[k][m]; x = x[~np.isnan(x)]
        s.append('M%s %+.4f (t %+.2f)' % (k, x.mean(), V.nw_t(x)))
    sp = (d['2'] - d['3'])[m]; sp = sp[~np.isnan(sp)]
    s.append('M2-M3 %+.4f (t %+.2f)' % (sp.mean(), V.nw_t(sp)))
    sp = (d['1'] - d['2'])[m]; sp = sp[~np.isnan(sp)]
    s.append('M1-M2 %+.4f (t %+.2f)' % (sp.mean(), V.nw_t(sp)))
    print(e, ' | '.join(s))
    for y in np.unique(YR[m]):
        my = m & (YR == y)
        sp = (d['1'] - d['2'])[my]; sp = sp[~np.isnan(sp)]
        print('   ', y, 'M1-M2 settle->open %+.4f (t %+.2f)' % (sp.mean(), V.nw_t(sp)))
