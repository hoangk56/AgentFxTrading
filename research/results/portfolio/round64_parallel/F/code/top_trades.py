"""Stream F: list the largest trades of a cell with their 1m path (diagnostics)."""
import os, sys, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import report as Rp, events as Ev  # noqa
cell = sys.argv[1]; top = int(sys.argv[2]) if len(sys.argv) > 2 else 15
tn, fn, Hs = cell.split(); k = Rp.HS.index(int(Hs[1:]))
z = np.load(os.path.join(Rp.OUT, "cand.npz")); syms = list(z["syms"])
sym, t, r, rb, sig, rank, g, f = z["sym"], z["t"].astype(np.int64), z["r"], z["rb"], z["sig"], z["rank"], z["g"], z["f"]
ib, ie = syms.index("BTCUSDT"), syms.index("ETHUSDT")
a = np.abs(r)
with np.errstate(invalid="ignore"):
    th = {"T3": a >= 0.03, "T5": a >= 0.05, "TZ": (a >= 0.01) & (a >= 10 * np.nan_to_num(sig, nan=np.inf))}[tn]
    fi = ((sym != ib) & np.isfinite(rb) & (np.abs(rb) <= 0.2 * a)) if fn == "idio" else np.ones(len(t), bool)
idx = np.where(th & fi)[0]; idx = idx[Rp.dedup(sym[idx], t[idx])]; idx = idx[np.isfinite(g[idx, k])]
o = idx[np.argsort(-np.abs(g[idx, k]))][:top]
x = g[idx, k]
print(f"n {len(idx)} mean {x.mean()*1e4:+.1f} median {np.median(x)*1e4:+.1f} trim5% {np.mean(np.sort(x)[int(.05*len(x)):int(.95*len(x))])*1e4:+.1f} "
      f"win {np.mean(x>0)*100:.0f}% sum {x.sum()*1e4:.0f} sum top10 {np.sort(x)[-10:].sum()*1e4:.0f} bottom10 {np.sort(x)[:10].sum()*1e4:.0f}")
cache = {}
for j in o:
    s = syms[sym[j]]
    if s not in cache: cache[s] = Ev.load_sym(s)
    c = cache[s][0]; e = t[j]
    path = [c[e - 1], c[e], c[e + 1], c[e + 2], c[e + 6], c[e + 16], c[e + 61]]
    p0 = path[0]
    ts = dt.datetime.fromtimestamp((Ev.T0 + e * 60000) / 1000, dt.timezone.utc)
    print(f"{s:14s} {ts:%Y-%m-%d %H:%M} r {r[j]*1e4:+6.0f} btc {rb[j]*1e4:+5.0f} gross {g[j,k]*1e4:+7.0f} | path vs c[e-1] (bp): "
          + " ".join(f"{(p/p0-1)*1e4:+.0f}" for p in path[1:]) + f" | n_trades {cache[s][2][e]} qv {cache[s][3][e]:.0f}")
