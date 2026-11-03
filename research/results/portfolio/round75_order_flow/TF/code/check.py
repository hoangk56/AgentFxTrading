"""Slow, independent re-implementation of departure / test / 2R execution for a few random zones (consistency check)."""
import importlib.util, numpy as np, sys
spec = importlib.util.spec_from_file_location('tf', 'tf.py'); tf = importlib.util.module_from_spec(spec); spec.loader.exec_module(tf)
sym = sys.argv[1]
D = tf.Data(sym); Z = tf.make_zones(D, 5)
dirn, tmin, filled, entry = tf.tests(D, Z)
rng = np.random.default_rng(1)
pick = rng.choice(np.flatnonzero(filled & (dirn != 0)), 40, replace=False)
res, com = tf.execute(D, dirn[pick], tmin[pick], entry[pick], Z['bar'][pick])
bad = 0
for n, zi in enumerate(pick):
    k = D.k; lo = np.exp(Z['lo'][zi] * k / 1e4); hi = np.exp((Z['hi'][zi] + 1) * k / 1e4); j = Z['bar'][zi]
    up = dn = 0; d = 0
    for b in range(j + 1, j + 337):
        lo_b = np.nanmin(D.l[b*30:b*30+30]); hi_b = np.nanmax(D.h[b*30:b*30+30])
        up += lo_b > hi; dn += hi_b < lo
        if up >= 2: d, db = 1, b; break
        if dn >= 2: d, db = -1, b; break
    tm = None
    for mi in range((db + 1) * 30, (j + 337) * 30):
        if (d > 0 and D.l[mi] <= hi) or (d < 0 and D.h[mi] >= lo): tm = mi; break
    ok = (d == dirn[zi]) and (tm == tmin[zi])
    if n in com['idx']:
        q = list(com['idx']).index(n)
        e = hi if d > 0 else lo
        atr = D.atr[(D.t0 + tm) // 1440 - D.D0]; R = 0.15 * atr; st = e - d * R; tp = e + d * 2 * R
        kind = 0; x = None
        for i in range(1440):
            m = tm + i
            if (d > 0 and D.l[m] <= st) or (d < 0 and D.h[m] >= st):
                px = st if i == 0 else (min(st, D.o[m]) if d > 0 else max(st, D.o[m])); px *= (1 - d * D.slip / 1e4); kind = 1; x = m; break
            if i > 0 and ((d > 0 and D.h[m] > tp) or (d < 0 and D.l[m] < tp)): px = tp; kind = 2; x = m; break
        if kind == 0: x = D.lastvalid[tm + 1439]; px = D.c[x]
        g = d * (px / e - 1) * 1e4 - 2 - (2 if kind == 2 else 5) - d * D.funding(D.t0 + tm, D.t0 + x) * 1e4
        r = res['2R']['base']
        ok &= (kind == r['kind'][q]) and abs(g - r['net'][q]) < 1e-6
    bad += not ok
print(sym, 'mismatches', bad, 'of', len(pick))
