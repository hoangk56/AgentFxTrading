"""Diagnostics for stream A: excess over the same-date random pool, gross t, max-t null on gross, the open-gap premium
the long cannot earn, unfillable one-price opens, limit-down frequency.

Run: research/.venv/bin/python -I diag.py <ashare_dir> <out_dir>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import analyze as A  # noqa: E402


def main(base, outdir):
    P = A.build(base)
    rng = np.random.default_rng(7)
    out = []
    dates = P["dates"]
    for univ in ("conn", "all"):
        cs, U = A.cells(P, univ)
        out.append(f"\n== {univ}: per-date excess over the same-date pool mean (same exits, same costs), gross t")
        out.append(f"{'cell':7s} {'exIS':>7s} {'t':>6s} {'exVAL':>7s} {'t':>6s} {'grossIS':>8s} {'tG_IS':>6s} {'grossV':>7s} {'tG_V':>6s}")
        maxnull = {"IS": [], "VAL": []}
        for name in A.CAND + ["X0_T"]:
            var, mask = cs[name]
            lag = A.LAG[var]
            g, c = P["g"][var], P["cst"][var]
            r = g - c
            pool = P["F"]["pool"] & U & np.isfinite(r)
            if var.startswith("X"):
                pool &= P["F"]["base"]
            m = mask & np.isfinite(r)
            rows = np.where(m.sum(1) > 0)[0]
            ex = np.array([r[i][m[i]].mean() - (r[i][pool[i]].mean() if pool[i].sum() >= 5 else np.nan) for i in rows])
            gr = np.array([g[i][m[i]].mean() for i in rows])
            d = dates[rows]
            ok = np.isfinite(ex)
            rec = []
            for era in (A.IS, A.VAL):
                em = (d >= era[0]) & (d <= era[1]) & ok
                rec += [ex[em].mean() * 1e4, A.nw_t(ex[em], lag)]
            for era in (A.IS, A.VAL):
                em = (d >= era[0]) & (d <= era[1])
                rec += [gr[em].mean() * 1e4, A.nw_t(gr[em], lag)]
            out.append(f"{name:7s} " + " ".join(f"{v:7.1f}" if k % 2 == 0 else f"{v:6.2f}" for k, v in enumerate(rec)))
            if name in A.CAND:
                # gross random draws for the max-t null on gross returns
                gpool = P["F"]["pool"] & U & np.isfinite(g)
                if var.startswith("X"):
                    gpool &= P["F"]["base"]
                for nm, era in (("IS", A.IS), ("VAL", A.VAL)):
                    rr = rows[(d >= era[0]) & (d <= era[1])]
                    sims = np.zeros((300, len(rr)))
                    for a, i in enumerate(rr):
                        pv = g[i][gpool[i]]
                        k = m[i].sum()
                        sims[:, a] = pv[rng.integers(0, len(pv), (300, k))].mean(1) if len(pv) else np.nan
                    maxnull[nm].append([A.nw_t(s[np.isfinite(s)], lag) for s in sims])
        for nm in ("IS", "VAL"):
            mx = np.nanmax(np.array(maxnull[nm]), 0)
            out.append(f"max-t null on GROSS returns over the 12 cells, {nm}: p95 {np.percentile(mx, 95):.2f}")
    # open-gap premium (C_t -> O_{t+1}) on first limit-up closes, and unfillable opens
    F = P["F"]
    S1 = F["S"] & F["first20"] & F["cvbase"]
    gap = P["gap"]
    for nm, era in (("IS", A.IS), ("VAL", A.VAL)):
        em = (dates >= era[0]) & (dates <= era[1])
        s = S1[em]
        gp = gap[em][s]
        filled = (F["base"][em] & S1[em]).sum()
        out.append(f"{nm}: first sealed limit-ups {s.sum()}, mean open gap C_t->O_t+1 {np.nanmean(gp) * 1e4:.0f} bp, median "
                   f"{np.nanmedian(gp) * 1e4:.0f} bp; one-price limit-up open (unfillable) {1 - filled / s.sum():.1%}")
        T1 = F["T"] & F["first20"] & F["cvbase"]
        gt = gap[em][T1[em]]
        out.append(f"{nm}: first touched-only {T1[em].sum()}, mean open gap {np.nanmean(gt) * 1e4:.0f} bp")
    # limit-down close frequency (sanity for the exit shift count)
    nbar = np.isfinite(P["g"]["X0"]).sum()
    out.append(f"limit-down exit shifts {P['nshift']} over {nbar} stock-days x 11 variants")
    txt = "\n".join(out)
    open(os.path.join(outdir, "diag.txt"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
