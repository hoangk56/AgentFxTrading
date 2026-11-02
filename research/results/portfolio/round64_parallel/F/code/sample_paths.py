"""Stream F: random sample of a cell's events with their 1m path and minute volumes (diagnostics)."""
import os, sys, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from f_extra import cellidx  # noqa
import report as Rp, events as Ev  # noqa
from f_extra import cellidx, z, syms, sym, t, r, rb, g  # noqa
cell = sys.argv[1]; ns = int(sys.argv[2])
tn, fn, Hs = cell.split(); k = Rp.HS.index(int(Hs[1:]))
idx = cellidx(tn, fn, k)
rng = np.random.default_rng(1)
o = np.sort(rng.choice(idx, ns, replace=False))
cache = {}
for j in o:
    s = syms[sym[j]]
    if s not in cache: cache[s] = Ev.load_sym(s)
    c, op, n, qv, _ = cache[s]; e = t[j]
    p0 = c[e - 1]
    ts = dt.datetime.fromtimestamp((Ev.T0 + e * 60000) / 1000, dt.timezone.utc)
    pth = " ".join(f"{(c[e+d]/p0-1)*1e4:+.0f}" for d in (0, 1, 2, 3, 5, 10, 20, 30, 45, 61))
    med_qv = np.nanmedian(qv[e - 60:e])
    print(f"{s:12s} {ts:%Y-%m-%d %H:%M} r {r[j]*1e4:+5.0f} btc {rb[j]*1e4:+4.0f} g {g[j,k]*1e4:+6.0f} | e..e+61: {pth} | "
          f"qv e {qv[e]/1e3:.0f}k e+1 {qv[e+1]/1e3:.0f}k med60 {med_qv/1e3:.0f}k n e/e+1 {n[e]}/{n[e+1]}")
