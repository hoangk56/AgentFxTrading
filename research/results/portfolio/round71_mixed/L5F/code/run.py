"""L5F: run the 6 declared cells, checks, random benchmark, information tables. Writes out/report.txt, out/cells.json."""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
OUT = E.OUT; os.makedirs(OUT, exist_ok=True)
ranks = dict(np.load(os.path.join(OUT, "ranks.npz")))
CELLS = [("A2_4", E.SYMS, 2, 4), ("A2_12", E.SYMS, 2, 12), ("A3_4", E.SYMS, 3, 4), ("A3_12", E.SYMS, 3, 12),
         ("M2_4", E.SYMS[:2], 2, 4), ("M2_12", E.SYMS[:2], 2, 12)]
NREP = 500
rng = np.random.default_rng(71)
lines = []
def p(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); lines.append(s)

P = {}; PL = {}; P15 = {}; PP = {}
for s in E.SYMS:
    P[s] = E.coin_panel(s, ranks, horizons=(0.5, 1, 4, 8, 12), lat=1)
    PL[s] = E.coin_panel(s, ranks, horizons=(4, 12), lat=2)
    P15[s] = E.coin_panel(s, ranks, horizons=(4, 12), lat=16)
    PP[s] = E.coin_panel(s, ranks, horizons=(4, 12), lat=1, offset=7)
    zz = P[s]["z"]; ok = ~np.isnan(zz)
    p(f"{s}: marks with z {ok.sum()}, |z|>=2 {np.mean(np.abs(zz[ok]) >= 2):.4f}, |z|>=3 {np.mean(np.abs(zz[ok]) >= 3):.4f}")

YEARS = [(y, (np.datetime64(f"{y}-01-01") - np.datetime64("2020-01-01")).astype(int),
          (np.datetime64(f"{y + 1}-01-01") - np.datetime64("2020-01-01")).astype(int)) for y in range(2020, 2025)]
ERAS = {"IS": (0, E.IS_END_DAY), "VAL": (E.IS_END_DAY, E.ND)}


def cell_trades(Pd, syms, k, H, sel_from=None):
    rows = []
    for s in syms:
        idx, side = E.select_trades(sel_from[s] if sel_from else Pd[s], k, H)
        rows.append((s, idx, side))
    return rows


def stats(Pd, rows, H, d0, d1, cost_mult=1.0):
    x = []; g = []; gr = []
    for s, idx, side in rows:
        day = Pd[s]["day"][idx]; k = (day >= d0) & (day < d1)
        n = E.net_of(Pd[s], idx[k], side[k], H, cost_mult)
        ok = ~np.isnan(n)
        x.append(n[ok]); g.append(day[k][ok])
        gr.append((side[k] * Pd[s][f"g{H}"][idx[k]] - side[k] * Pd[s][f"f{H}"][idx[k]])[ok])
    x = np.concatenate(x); g = np.concatenate(g); gr = np.concatenate(gr)
    return x, g, gr


res = {}
p("\n== Declared cells (net bp per trade; gross = after funding, before fees + spread) ==")
hdr = "cell era n net t gross sd longshare x1.5t late1t late15t"
p(hdr)
for name, syms, k, H in CELLS:
    rows = cell_trades(P, syms, k, H)
    res[name] = {"rows": rows}
    for era, (d0, d1) in ERAS.items():
        x, g, gr = stats(P, rows, H, d0, d1)
        x15, g15, _ = stats(P, rows, H, d0, d1, 1.5)
        xl, gl, _ = stats(PL, rows, H, d0, d1)
        xq, gq, _ = stats(P15, rows, H, d0, d1)
        ls = np.mean(np.concatenate([r[2][(P[r[0]]["day"][r[1]] >= d0) & (P[r[0]]["day"][r[1]] < d1)] for r in rows]) > 0)
        t = E.cl_t(x, g)
        res[name][era] = dict(n=len(x), net=float(x.mean()), t=float(t), gross=float(gr.mean()), sd=float(x.std()),
                              t15=float(E.cl_t(x15, g15)), tlate=float(E.cl_t(xl, gl)), tlate15=float(E.cl_t(xq, gq)),
                              longshare=float(ls), days=int(len(np.unique(g))))
        r = res[name][era]
        p(f"{name} {era} {r['n']} {r['net']:+.2f} {r['t']:+.2f} {r['gross']:+.2f} {r['sd']:.0f} {ls:.2f} "
          f"{r['t15']:+.2f} {r['tlate']:+.2f} {r['tlate15']:+.2f}")
    yr = []
    for y, d0, d1 in YEARS:
        x, g, gr = stats(P, rows, H, d0, d1); yr.append((y, len(x), float(x.mean()), float(gr.mean())))
    res[name]["years"] = yr
    p(f"{name} years (n, net, gross): " + " | ".join(f"{y}: {n} {m:+.1f} {gg:+.1f}" for y, n, m, gg in yr))
    v = res[name]["VAL"]
    res[name]["power_clust"] = v["t"] * np.sqrt(22 / 36)
    res[name]["power_trade"] = v["net"] / v["sd"] * np.sqrt(v["n"] * 22 / 36)
    p(f"{name} power at VAL size (HOLD 22 mo): clustered {res[name]['power_clust']:+.2f}, per-trade {res[name]['power_trade']:+.2f}")

# per-coin detail
p("\n== Per coin (net / gross bp, n) ==")
for name, syms, k, H in CELLS[:4]:
    for s, idx, side in res[name]["rows"]:
        out = []
        for era, (d0, d1) in ERAS.items():
            x, g, gr = stats(P, [(s, idx, side)], H, d0, d1)
            out.append(f"{era} n {len(x)} net {x.mean():+.1f} gross {gr.mean():+.1f} t {E.cl_t(x, g):+.2f}")
        p(f"{name} {s}: " + " ; ".join(out))

# random benchmark
p("\n== Random entries (500 reps): share of reps with mean net below real; max-over-cells IS t null ==")
pools = {}
for s in E.SYMS:
    for H in (4, 12):
        for era, (d0, d1) in ERAS.items():
            day = P[s]["day"]
            ok = (~np.isnan(P[s]["z"])) & (~np.isnan(P[s][f"g{H}"])) & (day >= d0) & (day < d1)
            pools[(s, H, era)] = np.where(ok)[0]
null_t = np.zeros((NREP, len(CELLS))); null_m = {}
for ci, (name, syms, k, H) in enumerate(CELLS):
    for era, (d0, d1) in ERAS.items():
        spec = []
        for s, idx, side in res[name]["rows"]:
            day = P[s]["day"][idx]; kk = (day >= d0) & (day < d1)
            n = int(kk.sum()); ls = float((side[kk] > 0).mean()) if n else 0.5
            spec.append((s, n, ls))
        means = np.zeros(NREP); ts = np.zeros(NREP)
        for r in range(NREP):
            xs = []; gs = []
            for s, n, ls in spec:
                if n == 0: continue
                pool = pools[(s, H, era)]
                ii = pool[rng.integers(0, len(pool), n)]
                sd = np.where(rng.random(n) < ls, 1.0, -1.0)
                xs.append(E.net_of(P[s], ii, sd, H)); gs.append(P[s]["day"][ii])
            xs = np.concatenate(xs); gs = np.concatenate(gs)
            means[r] = xs.mean()
            if era == "IS": ts[r] = E.cl_t(xs, gs)
        pct = float((means < res[name][era]["net"]).mean())
        res[name][era]["rand_pct"] = pct; res[name][era]["rand_med"] = float(np.median(means))
        if era == "IS": null_t[:, ci] = ts
        p(f"{name} {era}: real {res[name][era]['net']:+.2f}, random median {np.median(means):+.2f}, beats {100 * pct:.1f} %")
mx = null_t.max(1); real_mx = max(res[n]["IS"]["t"] for n, *_ in CELLS)
p(f"max-over-6-cells IS t: real {real_mx:+.2f}; null median {np.median(mx):+.2f}, p95 {np.percentile(mx, 95):+.2f}; "
  f"real at {100 * (mx < real_mx).mean():.1f} pct")

# information: all signals (no position rule), sign-weighted gross by horizon
p("\n== Information: all |z|>=2 marks, sign-weighted price return (bp, before funding/costs), clustered t ==")
for era, (d0, d1) in ERAS.items():
    for grp, syms in (("all6", E.SYMS), ("BTC+ETH", E.SYMS[:2])):
        out = []
        for H in (0.5, 1, 4, 8, 12):
            xs = []; gs = []
            for s in syms:
                z = P[s]["z"]; day = P[s]["day"]
                k = (np.abs(z) >= 2) & ~np.isnan(P[s][f"g{H}"]) & (day >= d0) & (day < d1)
                xs.append(np.sign(z[k]) * P[s][f"g{H}"][k]); gs.append(day[k])
            xs = np.concatenate(xs); gs = np.concatenate(gs)
            out.append(f"{H}h {xs.mean():+.2f} (t {E.cl_t(xs, gs):+.2f})")
        p(f"{era} {grp} n~{len(xs)}: " + " | ".join(out))

p("\n== Information: placebo minute (:07/:22/:37/:52), same k=2 cells ==")
for name, syms, k, H in CELLS:
    if k != 2: continue
    rows = cell_trades(PP, syms, k, H)
    out = []
    for era, (d0, d1) in ERAS.items():
        x, g, gr = stats(PP, rows, H, d0, d1)
        out.append(f"{era} n {len(x)} net {x.mean():+.2f} t {E.cl_t(x, g):+.2f} gross {gr.mean():+.2f}")
    p(f"placebo {name}: " + " ; ".join(out))

p("\n== Information: reversal side of the declared cells (net = -gross - cost) ==")
for name, syms, k, H in CELLS:
    out = []
    for era, (d0, d1) in ERAS.items():
        x, g, gr = stats(P, res[name]["rows"], H, d0, d1)
        cost = gr - x
        xr = -gr - cost
        out.append(f"{era} net {xr.mean():+.2f} t {E.cl_t(xr, g):+.2f}")
    p(f"rev {name}: " + " ; ".join(out))

open(os.path.join(OUT, "report.txt"), "w").write("\n".join(lines) + "\n")
for n in res: res[n].pop("rows", None)
json.dump(res, open(os.path.join(OUT, "cells.json"), "w"), indent=1, default=float)
