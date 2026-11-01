"""Stream A: long the session after a first limit-up close (A-share main board), declared grid in HYPOTHESES_A.md.

Run: research/.venv/bin/python -I analyze.py <ashare_dir> <out_dir>
"""
import json
import os
import sys

import numpy as np

TOL = 0.005
R_DRAWS = 1000
IS = (20160101, 20211231)
VAL = (20220101, 20241231)


def rhu(x):
    return np.floor(x * 100 + 0.5 + 1e-7) / 100


def nw_t(x, lag):
    x = np.asarray(x, float)
    n = len(x)
    if n < 5:
        return np.nan
    m = x.mean()
    e = x - m
    s = e @ e / n
    for L in range(1, lag + 1):
        s += 2 * (1 - L / (lag + 1)) * (e[L:] @ e[:-L]) / n
    return m / np.sqrt(s / n) if s > 0 else np.nan


# variant: (entry bar offset, entry kind, exit bar offset, exit kind), offsets relative to the signal bar k
VARIANTS = {
    "X0": (1, "o", 1, "c"), "X1": (1, "o", 2, "o"), "X2": (1, "o", 2, "c"), "X3": (1, "o", 3, "c"),
    "CV1a": (0, "c", 1, "o"), "CV1b": (0, "c", 1, "c"),
    "X1L": (2, "o", 3, "o"), "X2L": (2, "o", 3, "c"), "X3L": (2, "o", 4, "c"),
    "CV1aL": (1, "c", 2, "o"), "CV1bL": (1, "c", 2, "c"),
}
LAG = {"X0": 0, "X1": 1, "X2": 2, "X3": 3, "CV1a": 0, "CV1b": 1}
LATE = {"X0": "X0", "X1": "X1L", "X2": "X2L", "X3": "X3L", "CV1a": "CV1aL", "CV1b": "CV1bL"}


def ymd_to_day(x):
    x = np.asarray(x, np.int64)
    return (np.array([f"{v // 10000:04d}-{v // 100 % 100:02d}-{v % 100:02d}" for v in x], "datetime64[D]")
            .astype(np.int64))


def build(base):
    z = dict(np.load(os.path.join(base, "panel_ov.npz")))
    dates, O, H, C, A, AF, ipo = z["dates"], z["O"], z["H"], z["C"], z["A"], z["AF"], z["ipo"]
    assert dates.max() < 20250101
    dday = ymd_to_day(dates)
    ipo_day = ymd_to_day(np.where(ipo > 0, ipo, 19900101))
    nd, ns = C.shape
    g = {v: np.full((nd, ns), np.nan, np.float32) for v in VARIANTS}
    cst = {v: np.full((nd, ns), np.nan, np.float32) for v in VARIANTS}
    F = {k: np.zeros((nd, ns), bool) for k in ("S", "T", "first20", "first60", "base", "pool", "cvbase")}
    gap = np.full((nd, ns), np.nan, np.float32)
    tv60 = np.full((nd, ns), np.nan)
    price = np.full((nd, ns), np.nan, np.float32)
    nshift = 0
    for j in range(ns):
        b = np.where(np.isfinite(C[:, j]))[0]
        n = len(b)
        if n < 62:
            continue
        o, h, c, a = O[b, j], H[b, j], C[b, j], A[b, j]
        af = AF[b, j].copy()
        # forward / backward fill missing factors; all missing -> 1
        if np.isnan(af).all():
            af[:] = 1.0
        else:
            idx = np.where(np.isfinite(af), np.arange(n), 0)
            np.maximum.accumulate(idx, out=idx)
            af = af[idx]
            first = np.argmax(np.isfinite(af))
            af[:first] = af[first]
        pc = np.r_[np.nan, c[:-1] * af[:-1] / af[1:]]  # ex-rights reference previous close
        Lu, Ld = rhu(pc * 1.1), rhu(pc * 0.9)
        up = np.abs(c - Lu) < TOL
        dn = np.abs(c - Ld) < TOL
        touch = (h >= Lu - TOL) & ~up
        upc = np.r_[0, np.cumsum(up)]
        k = np.arange(n)
        f20 = np.zeros(n, bool)
        f60 = np.zeros(n, bool)
        f20[60:] = (upc[60:n] - upc[40:n - 20]) == 0
        f60[60:] = (upc[60:n] - upc[0:n - 60]) == 0
        adj = np.zeros(n, bool)
        adj[:-1] = b[1:] == b[:-1] + 1
        fill_next = np.zeros(n, bool)
        fill_next[:-1] = o[1:] < Lu[1:] - TOL
        hist = (k >= 60) & (dday[b] - ipo_day[j] >= 120)
        F["S"][b, j] = up & hist
        F["T"][b, j] = touch & hist
        F["first20"][b, j] = f20
        F["first60"][b, j] = f60
        F["base"][b, j] = hist & adj & fill_next
        F["cvbase"][b, j] = hist & adj
        F["pool"][b, j] = hist & adj & ~up & ~dn
        gp = np.full(n, np.nan)
        gp[:-1] = (o[1:] * af[1:]) / (c[:-1] * af[:-1]) - 1
        gap[b, j] = gp
        aa = np.where(np.isfinite(a), a, 0.0)
        cs = np.r_[0, np.cumsum(aa)]
        t60 = np.full(n, np.nan)
        t60[59:] = (cs[60:] - cs[:-60]) / 60
        tv60[b, j] = t60
        price[b, j] = c
        dts = dates[b]
        for name, (eo, ek, xo, xk) in VARIANTS.items():
            ei = k + eo
            xi = k + xo
            okk = xi < n
            ent = np.full(n, np.nan)
            ent[okk] = (o if ek == "o" else c)[ei[okk]]
            if ek == "o" and eo >= 2:  # late open entry must be fillable too
                ok2 = np.zeros(n, bool)
                ok2[okk] = o[ei[okk]] < Lu[ei[okk]] - TOL
                ent[~ok2] = np.nan
            px = o if xk == "o" else c
            ex = np.full(n, np.nan)
            ex[okk] = px[xi[okk]]
            xidx = np.where(okk, xi, 0)
            bad = np.where(np.isfinite(ent) & np.isfinite(ex) & (ex <= Ld[xidx] + TOL))[0]
            for kk in bad:  # cannot sell at limit-down: next open, up to 10 sessions
                i = kk + xo
                p = px[i]
                tries = 0
                while p <= Ld[i] + TOL and tries < 10:
                    i += 1
                    tries += 1
                    nshift += 1
                    if i >= n:
                        p = np.nan
                        break
                    p = o[i]
                if i < n and np.isfinite(p):
                    ex[kk] = p
                    xidx[kk] = i
                else:
                    ex[kk] = np.nan
            eidx = np.where(okk, ei, 0)
            gr = (ex * af[xidx]) / (ent * af[eidx]) - 1
            exd = dts[xidx]
            stamp = np.where(exd >= 20230828, 5.0, 10.0)
            half_tick = 0.005 / ent * 1e4
            cost = (3 + 0.7 + 10 + half_tick) + (3 + 0.7 + 5 + half_tick + stamp)
            g[name][b, j] = gr
            cst[name][b, j] = cost / 1e4
    # Connect proxy: trailing 60-day traded value >= 40th pct of the day's cross-section
    conn = np.zeros((nd, ns), bool)
    for i in range(nd):
        x = tv60[i]
        m = np.isfinite(x)
        if m.sum() >= 50:
            conn[i] = m & (x >= np.percentile(x[m], 40))
    return dict(dates=dates, g=g, cst=cst, F=F, gap=gap, conn=conn, price=price, nshift=nshift)


def cells(P, univ, first="first20"):
    F = P["F"]
    U = P["conn"] if univ == "conn" else np.ones_like(P["conn"])
    fb = F[first] & F["base"] & U
    out = {}
    for x in ("X0", "X1", "X2", "X3"):
        out[f"{x}_ALL"] = (x, fb & (F["S"] | F["T"]))
        out[f"{x}_S"] = (x, fb & F["S"])
        out[f"{x}_T"] = (x, fb & F["T"])
    cvb = F[first] & F["cvbase"] & U & F["T"]
    out["CV1a"] = ("CV1a", cvb)
    out["CV1b"] = ("CV1b", cvb)
    out["CV2"] = ("X2", fb & F["S"] & (P["gap"] >= 0.03))
    return out, U


CAND = [f"{x}_{c}" for x in ("X1", "X2", "X3") for c in ("ALL", "S", "T")] + ["CV1a", "CV1b", "CV2"]


def series(P, var, mask, cmult=1.0, exclude=None):
    g, c = P["g"][var], P["cst"][var]
    r = g - cmult * c
    m = mask & np.isfinite(r)
    cnt = m.sum(1)
    rows = np.where(cnt > 0)[0]
    d = P["dates"][rows]
    net = np.array([r[i][m[i]].mean() for i in rows])
    gross = np.array([g[i][m[i]].mean() for i in rows])
    keep = np.ones(len(rows), bool)
    if exclude:
        keep = ~((d >= exclude[0]) & (d <= exclude[1]))
    return d[keep], net[keep], gross[keep], cnt[rows][keep]


def era_stats(d, x, lag, era):
    m = (d >= era[0]) & (d <= era[1])
    xs = x[m]
    if len(xs) < 5:
        return dict(n=int(len(xs)), mean_bp=np.nan, t=np.nan)
    return dict(n=int(len(xs)), mean_bp=float(xs.mean() * 1e4), t=float(nw_t(xs, lag)),
                sd_bp=float(xs.std() * 1e4), sharpe_d=float(xs.mean() / xs.std()))


def random_bench(P, var, mask, U, lag, rng, draws=R_DRAWS):
    """Per date, draw the same number of pool stocks (same universe, same entry/exit, same costs)."""
    g, c = P["g"][var], P["cst"][var]
    r = g - c
    pool = P["F"]["pool"] & U & np.isfinite(r)
    if var.startswith("X"):
        pool &= P["F"]["base"]
    m = mask & np.isfinite(r)
    cnt = m.sum(1)
    rows = np.where(cnt > 0)[0]
    d = P["dates"][rows]
    sims = np.full((draws, len(rows)), np.nan)
    poolmean = np.full(len(rows), np.nan)
    for a, i in enumerate(rows):
        pv = r[i][pool[i]]
        if len(pv) < 5:
            continue
        poolmean[a] = pv.mean()
        sims[:, a] = pv[rng.integers(0, len(pv), (draws, cnt[i]))].mean(1)
    res = {}
    for nm, era in (("IS", IS), ("VAL", VAL)):
        em = (d >= era[0]) & (d <= era[1]) & np.isfinite(poolmean)
        s = sims[:, em]
        means = s.mean(1)
        ts = np.array([nw_t(row, lag) for row in s])
        res[nm] = dict(means=means, ts=ts, poolmean_bp=float(np.nanmean(poolmean[em]) * 1e4), em=em, rows=rows)
    return res


def main(base, outdir):
    os.makedirs(outdir, exist_ok=True)
    P = build(base)
    rng = np.random.default_rng(63)
    report = {"nshift_limitdown": int(P["nshift"]), "n_stocks": int(P["conn"].shape[1])}
    lines = []
    for univ in ("conn", "all"):
        cs, U = cells(P, univ)
        report[univ] = {}
        maxt_null = {"IS": np.full((R_DRAWS, len(CAND)), np.nan), "VAL": np.full((R_DRAWS, len(CAND)), np.nan)}
        for name, (var, mask) in cs.items():
            lag = LAG[var]
            d, net, gross, cnt = series(P, var, mask)
            rec = {"events": int(cnt.sum()), "dates": int(len(d))}
            for nm, era in (("IS", IS), ("VAL", VAL)):
                rec[nm] = era_stats(d, net, lag, era)
                rec[nm]["gross_bp"] = era_stats(d, gross, lag, era)["mean_bp"]
                em = (d >= era[0]) & (d <= era[1])
                rec[nm]["events"] = int(cnt[em].sum())
            years = {}
            for y in range(2016, 2025):
                ym = (d >= y * 10000) & (d < (y + 1) * 10000)
                years[y] = float(net[ym].mean() * 1e4) if ym.any() else None
            rec["years_bp"] = years
            dS, netS, _, _ = series(P, var, mask, cmult=1.5)
            rec["x1.5"] = {nm: era_stats(dS, netS, lag, era) for nm, era in (("IS", IS), ("VAL", VAL))}
            dE, netE, _, _ = series(P, var, mask, exclude=(20200201, 20200430))
            rec["ex2020FebApr_IS"] = era_stats(dE, netE, lag, IS)
            lv = LATE[var]
            dL, netL, _, _ = series(P, lv, mask)
            rec["late"] = {nm: era_stats(dL, netL, lag, era) for nm, era in (("IS", IS), ("VAL", VAL))}
            if name in CAND or name == "X0_ALL":
                rb = random_bench(P, var, mask, U, lag, rng)
                for nm in ("IS", "VAL"):
                    rule = rec[nm]["mean_bp"] / 1e4
                    rec[nm]["pct_beats_random"] = float((rb[nm]["means"] < rule).mean() * 100)
                    rec[nm]["random_mean_bp"] = float(rb[nm]["means"].mean() * 1e4)
                    rec[nm]["pool_mean_bp"] = rb[nm]["poolmean_bp"]
                    if name in CAND:
                        maxt_null[nm][:, CAND.index(name)] = rb[nm]["ts"]
            report[univ][name] = rec
        for nm in ("IS", "VAL"):
            mx = np.nanmax(maxt_null[nm], 1)
            report[univ][f"maxt_null_p95_{nm}"] = float(np.percentile(mx, 95))
        # N=60 robustness for every candidate (cheap)
        cs60, _ = cells(P, univ, first="first60")
        report[univ]["N60"] = {}
        for name in CAND:
            var, mask = cs60[name]
            d, net, _, cnt = series(P, var, mask)
            report[univ]["N60"][name] = {nm: era_stats(d, net, LAG[var], era) for nm, era in (("IS", IS), ("VAL", VAL))}
    # per-stock tick cost actually paid (median half tick bp at the entry, conn ALL X2 events)
    cs, _ = cells(P, "conn")
    m = cs["X2_ALL"][1]
    pr = P["price"]
    report["entry_close_price_median"] = float(np.nanmedian(pr[m]))
    report["half_tick_bp_median"] = float(np.nanmedian(0.005 / pr[m] * 1e4))
    report["cost_bp_median_X2"] = float(np.nanmedian(P["cst"]["X2"][m]) * 1e4)
    with open(os.path.join(outdir, "results.json"), "w") as f:
        json.dump(report, f, indent=1, default=float)
    # text table
    for univ in ("conn", "all"):
        lines.append(f"\n== universe {univ}  (max-t null p95 IS {report[univ]['maxt_null_p95_IS']:.2f}, "
                     f"VAL {report[univ]['maxt_null_p95_VAL']:.2f})")
        lines.append(f"{'cell':9s} {'evIS':>6s} {'dIS':>5s} {'grIS':>7s} {'netIS':>7s} {'tIS':>6s} {'rnd%':>5s} "
                     f"{'evVAL':>6s} {'grV':>7s} {'netV':>7s} {'tV':>6s} {'rnd%':>5s} {'x1.5IS':>7s} {'x1.5V':>7s} "
                     f"{'lateIS':>7s} {'lateV':>7s} {'N60tIS':>6s} {'sdIS':>6s} yrs+")
        for name, rec in report[univ].items():
            if not isinstance(rec, dict) or "IS" not in rec:
                continue
            yp = sum(1 for v in rec["years_bp"].values() if v is not None and v > 0)
            n60 = report[univ]["N60"].get(name, {}).get("IS", {}).get("t", np.nan)
            lines.append(
                f"{name:9s} {rec['IS']['events']:6d} {rec['IS']['n']:5d} {rec['IS']['gross_bp']:7.1f} "
                f"{rec['IS']['mean_bp']:7.1f} {rec['IS']['t']:6.2f} {rec['IS'].get('pct_beats_random', np.nan):5.1f} "
                f"{rec['VAL']['events']:6d} {rec['VAL']['gross_bp']:7.1f} {rec['VAL']['mean_bp']:7.1f} "
                f"{rec['VAL']['t']:6.2f} {rec['VAL'].get('pct_beats_random', np.nan):5.1f} "
                f"{rec['x1.5']['IS']['mean_bp']:7.1f} {rec['x1.5']['VAL']['mean_bp']:7.1f} "
                f"{rec['late']['IS']['mean_bp']:7.1f} {rec['late']['VAL']['mean_bp']:7.1f} {n60:6.2f} "
                f"{rec['IS'].get('sd_bp', np.nan):6.0f} {yp}/9")
        lines.append("years (net bp per date-basket):")
        for name, rec in report[univ].items():
            if isinstance(rec, dict) and "years_bp" in rec:
                lines.append(f"  {name:9s} " + " ".join(
                    f"{y}:{v:7.1f}" if v is not None else f"{y}:   na" for y, v in rec["years_bp"].items()))
    lines.append(f"\nlimit-down exit shifts: {report['nshift_limitdown']}; stocks: {report['n_stocks']}; "
                 f"median entry-day close {report['entry_close_price_median']:.2f} CNY, half tick "
                 f"{report['half_tick_bp_median']:.1f} bp/side, median round-trip cost X2 {report['cost_bp_median_X2']:.1f} bp")
    txt = "\n".join(lines)
    open(os.path.join(outdir, "results.txt"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
