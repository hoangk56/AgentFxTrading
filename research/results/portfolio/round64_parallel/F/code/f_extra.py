"""Stream F: extra diagnostics for the IS-chosen cell and its neighbours (information; no new cells)."""
import os, sys, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import report as Rp  # noqa
z = np.load(os.path.join(Rp.OUT, "cand.npz")); syms = list(z["syms"])
sym, t, r, rb, sig, rank, g, gl, f, fl = (z[k] for k in ("sym", "t", "r", "rb", "sig", "rank", "g", "gl", "f", "fl"))
t = t.astype(np.int64)
ib, ie = syms.index("BTCUSDT"), syms.index("ETHUSDT")
h = np.where((sym == ib) | (sym == ie), 1.0, np.where(rank < 20, 3.0, 5.0)) / 1e4
cost = 10e-4 + 4 * h
day = (Rp.T0 + t * Rp.MIN) // Rp.DAY
ym = np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).strftime("%Y-%m") for d in day])
yr = np.array([int(s[:4]) for s in ym])
a = np.abs(r)
out = []
P = out.append


def cellidx(tn, fn, k):
    with np.errstate(invalid="ignore"):
        th = {"T3": a >= 0.03, "T5": a >= 0.05, "TZ": (a >= 0.01) & (a >= 10 * np.nan_to_num(sig, nan=np.inf))}[tn]
        fi = ((sym != ib) & np.isfinite(rb) & (np.abs(rb) <= 0.2 * a)) if fn == "idio" else np.ones(len(t), bool)
    idx = np.where(th & fi)[0]; idx = idx[Rp.dedup(sym[idx], t[idx])]
    return idx[np.isfinite(g[idx, k])]


def line(nm, net, d):
    m, tt, sd, n = Rp.clt(net, d)
    S = m / sd if sd else np.nan
    return f"{nm}: n {n} net {m*1e4:+.1f} t {tt:+.2f} S {S:+.3f} median {np.median(net)*1e4:+.1f} win {np.mean(net>0)*100:.0f}%"


for cell in ("T5 idio H60", "T5 all H60", "T3 idio H60", "T5 idio H15"):
    tn, fn, Hs = cell.split(); k = Rp.HS.index(int(Hs[1:]))
    idx = cellidx(tn, fn, k)
    net = g[idx, k] - f[idx, k] - cost[idx]
    P(f"\n== {cell}")
    for e, en in ((0, "IS"), (1, "VAL")):
        q = (t[idx] < Rp.VAL0) == (e == 0)
        P(line(en, net[q], day[idx][q]))
        nv = net[q]; dv = day[idx][q]
        ud, inv = np.unique(dv, return_inverse=True); ds = np.bincount(inv, weights=nv)
        o = np.argsort(-ds)
        P(f"  days {len(ud)}; top-5 days {', '.join(dt.datetime.fromtimestamp(ud[i]*86400, dt.timezone.utc).strftime('%Y-%m-%d') + f' {ds[i]*1e4:+.0f}' for i in o[:5])}; "
          f"sum {nv.sum()*1e4:.0f} bp, without top-5 days {(nv.sum()-ds[o[:5]].sum())*1e4:.0f}")
        w = ~np.isin(dv, ud[o[:5]])
        P("  " + line("without top-5 days", nv[w], dv[w]))
        if e == 1:
            w = ~np.isin(ym[idx][q], ["2022-05", "2022-11"])
            m, tt, sd, n = Rp.clt(nv[w], dv[w])
            P("  " + line("VAL without LUNA / FTX months", nv[w], dv[w]) + f" -> power {m/sd*np.sqrt(0.61*n):.2f}")
            w = ~np.isin(syms_arr := np.array(syms)[sym[idx][q]], ["LUNAUSDT", "FTTUSDT"])
            P("  " + line("VAL without LUNA / FTT coins", nv[w], dv[w]))
        for sd_, nm in ((-1, "crash"), (1, "spike")):
            w = np.sign(r[idx][q]) == sd_
            P("  " + line(nm, nv[w], dv[w]))
        w = rank[idx][q] < 20
        P("  " + line("rank < 20", nv[w], dv[w])); P("  " + line("rank 20-39", nv[~w], dv[~w]))
        w = a[idx][q] >= 0.08
        P("  " + line("|r| >= 8%", nv[w], dv[w])); P("  " + line("5% <= |r| < 8%", nv[~w], dv[~w]))
    for y in range(2020, 2025):
        w = yr[idx] == y
        P("  " + line(str(y), net[w], day[idx][w]) + f" | crash {np.mean(net[w & (r[idx]<0)])*1e4:+.0f} spike {np.mean(net[w & (r[idx]>0)])*1e4:+.0f}")
    hl = (yr[idx] >= 2020)
    hh = int(Hs[1:])
    # costs needed to kill it
    for e, en in ((0, "IS"), (1, "VAL")):
        q = (t[idx] < Rp.VAL0) == (e == 0)
        gr = g[idx, k][q] - f[idx, k][q]
        P(f"  {en} break-even round-trip cost {gr.mean()*1e4:.0f} bp (declared {cost[idx][q].mean()*1e4:.0f})")
if __name__ == "__main__":
    print("\n".join(out))
    open(os.path.join(Rp.OUT, "extra.txt"), "w").write("\n".join(out) + "\n")
