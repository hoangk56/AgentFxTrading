"""Coordinator check of PREREG_DRAFT_F (IS / VAL only): adverse-fill stress on the frozen cell T5 idio H60.
Entry/exit variants: (a) frozen: close e+1 -> close e+61; (b) mean OHLC of bar e+2 -> mean OHLC of bar e+62;
(c) worst extreme of bar e+2 (long: high, short: low) -> worst extreme of bar e+62 (long: low, short: high)."""
import os, sys, glob, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(F, "code"))
import report as rp  # noqa
R = os.path.abspath(os.path.join(F, "..", "..", "..", ".."))
D = os.path.join(R, "data", "binance_1m_wicks", "npz")
T0, MIN, DAY, VAL0, BP = rp.T0, rp.MIN, rp.DAY, rp.VAL0, 1e4
NM = (1735689600000 - T0) // MIN
z = np.load(os.path.join(F, "out", "cand.npz"))
syms = list(z["syms"]); sym, t, r, rb, rank = z["sym"], z["t"].astype(np.int64), z["r"], z["rb"], z["rank"]
g, f = z["g"], z["f"]
ib = syms.index("BTCUSDT"); ie = syms.index("ETHUSDT")
a = np.abs(r)
m0 = (a >= 0.05) & (sym != ib) & np.isfinite(rb) & (np.abs(rb) <= 0.2 * a)
idx = np.where(m0)[0]; idx = idx[rp.dedup(sym[idx], t[idx])]
idx = idx[np.isfinite(g[idx, 2])]
h = np.where((sym == ib) | (sym == ie), 1.0, np.where(rank < 20, 3.0, 5.0)) / BP
cost = 10 / BP + 4 * h
side = -np.sign(r)
res = {k: np.full(len(t), np.nan) for k in ("a", "b", "c")}
res["a"][idx] = g[idx, 2] - f[idx, 2] - cost[idx]
for s in np.unique(sym[idx]):
    files = sorted(glob.glob(os.path.join(D, f"{syms[s]}_*.npz")))
    O = np.full(NM, np.nan); H = O.copy(); L = O.copy(); C = O.copy()
    for fn in files:
        q = np.load(fn); tt = q["m"].astype(np.int64) - T0 // MIN; k = (tt >= 0) & (tt < NM)
        O[tt[k]] = q["o"][k]; H[tt[k]] = q["h"][k]; L[tt[k]] = q["l"][k]; C[tt[k]] = q["c"][k]
    j = idx[sym[idx] == s]; e = t[j]; sd = side[j]
    mb_in = (O[e+2] + H[e+2] + L[e+2] + C[e+2]) / 4; mb_out = (O[e+62] + H[e+62] + L[e+62] + C[e+62]) / 4
    res["b"][j] = sd * (mb_out / mb_in - 1) - f[j, 2] - cost[j]
    w_in = np.where(sd > 0, H[e+2], L[e+2]); w_out = np.where(sd > 0, L[e+62], H[e+62])
    res["c"][j] = sd * (w_out / w_in - 1) - f[j, 2] - cost[j]
day = (T0 + t * MIN) // DAY
yr = np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).year for d in day])
era = np.where(t < VAL0, 0, 1)
for k in ("a", "b", "c"):
    for e, en in ((0, "IS"), (1, "VAL")):
        q = idx[(era[idx] == e) & np.isfinite(res[k][idx])]
        m, tt, sdv, n = rp.clt(res[k][q], day[q])
        print(f"{k} {en} n {n} net {m*BP:+.1f} t {tt:.2f} S {m/sdv:.3f} median {np.median(res[k][q])*BP:+.1f}")
q = idx
print("years (a):", {int(y): round(float(np.nanmean(res['a'][q][yr[q] == y]) * BP), 1) for y in np.unique(yr[q])})
hr = ((t[q] % 1440) // 60)
print("hour-of-day n:", np.bincount(hr, minlength=24).tolist())
cs = np.bincount(sym[q], weights=res["a"][q]); top = np.argsort(-cs)[:8]
print("top coins share of total:", [(syms[i], round(float(cs[i] / res['a'][q].sum()), 3)) for i in top])
print("coins with events:", len(np.unique(sym[q])), "events", len(q))
# events per day concentration
_, cnt = np.unique(day[q], return_counts=True); print("days", len(cnt), "max events/day", cnt.max(), "share days>=5 events", float((cnt[cnt>=5]).sum()/cnt.sum()))
