"""Brute-force cross-check of mn.zone_trades / mn.simulate on a sample (plain Python loops)."""
import importlib.util, sys
import numpy as np
sp = importlib.util.spec_from_file_location("mn", __file__.replace("check.py", "mn.py"))
mn = importlib.util.module_from_spec(sp); sp.loader.exec_module(mn)
sym = sys.argv[1]
s = mn.Sym(sym)
fb, row = mn.nodes(s, 2)
# brute nodes
p = s.poc; cnt = 0
for i in range(1, len(p)):
    if p[i] == p[i-1] and p[i] >= 0 and s.bstart[i]-s.bstart[i-1] == 30 and not (i >= 2 and p[i-2] == p[i] and s.bstart[i-1]-s.bstart[i-2] == 30):
        cnt += 1
print("nodes vec", len(fb), "brute", cnt)
rng = np.random.default_rng(0)
sel = np.sort(rng.choice(len(fb), 400, replace=False))
z, _ = mn.zone_trades(s, fb[sel], row[sel])
r = mn.simulate(s, z, "2R")
got = {int(f): (int(i), float(n)) for f, i, n in zip(z["fb"], z["i"], r["net"])}
bad = 0; nf = 0
for f, rr in zip(fb[sel], row[sel]):
    lo, hi = s.row_lo(rr), s.row_lo(rr + 1)
    exp_ = s.bstart[f] + 30 + 336 * 30
    cs = cr = 0; typ = None; u = None
    for b in range(f + 1, len(s.bstart)):
        if s.bstart[b] + 30 > exp_: break
        if s.bl[b] > hi: cs += 1
        if s.bh[b] < lo: cr += 1
        if cs == 2: typ, u = 1, b; break
        if cr == 2: typ, u = -1, b; break
    fill = None
    if typ is not None:
        j = s.bfirst[u + 1] if u + 1 < len(s.bstart) else len(s.mmin)
        g0 = s.gcum[min(s.bfirst[f], len(s.mmin)-1)]
        while j < len(s.mmin) and s.mmin[j] < exp_:
            e = hi if typ > 0 else lo
            if (typ > 0 and s.l[j] <= e) or (typ < 0 and s.h[j] >= e):
                if s.gcum[j] == g0 and ((typ > 0 and s.l[j] <= e * (1 - 1e-4)) or (typ < 0 and s.h[j] >= e * (1 + 1e-4))):
                    fill = j
                break
            j += 1
    if fill is not None:
        day = s.mmin[fill] // 1440 - s.d0
        atr = s.atr[day]
        if np.isnan(atr):
            fill = None
    if fill is None:
        if int(f) in got: bad += 1
        continue
    nf += 1
    E = hi if typ > 0 else lo; S = 0.15 * atr; d = typ
    stop, tp = E - d * S, E + d * 2 * S
    end = np.searchsorted(s.mmin, s.mmin[fill] + 1440, side="right") - 1
    if s.gcum[end] != s.gcum[fill]:
        if int(f) in got: bad += 1
        continue
    if (d > 0 and s.l[fill] <= stop) or (d < 0 and s.h[fill] >= stop):
        px, t = stop, 0; ex = fill
    else:
        t = 2; px = s.c[end]; ex = end
        for j in range(fill + 1, end + 1):
            if (d > 0 and s.l[j] <= stop) or (d < 0 and s.h[j] >= stop):
                px = min(stop, s.o[j]) if d > 0 else max(stop, s.o[j]); t = 0; ex = j; break
            if (d > 0 and s.h[j] > tp) or (d < 0 and s.l[j] < tp):
                px = tp; t = 1; ex = j; break
    gross = d * (px - E) / E * 1e4
    fees = 2 + (2 if t == 1 else 5) + (mn.SLIP[sym] if t == 0 else 0)
    a = np.searchsorted(s.fmin, s.mmin[fill], side="right"); b = np.searchsorted(s.fmin, s.mmin[ex], side="right")
    net = gross - fees - d * (s.fcum[b] - s.fcum[a]) * 1e4
    if int(f) not in got or got[int(f)][0] != fill or abs(got[int(f)][1] - net) > 1e-6:
        bad += 1
print("zones checked", len(sel), "filled", nf, "vec filled", len(z["i"]), "mismatches", bad)
