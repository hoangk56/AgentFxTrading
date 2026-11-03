"""Stream U analysis: revisit statistic (unfinished vs finished, matched) and the 8 declared trade cells.

Usage: python -I analyze.py [SYM ...]   (default: every turns_<SYM>.npz in U/out)  -> prints, and writes out/results.txt
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
HS = (12, 48)
NPERM = 1000
rng = np.random.default_rng(75_021)
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def load(syms):
    parts = []
    for si, sym in enumerate(syms):
        z = dict(np.load(os.path.join(OUT, f"turns_{sym}.npz")))
        n = len(z["tc"])
        z["sym"] = np.full(n, si)
        isw = z["era"] == 0
        rel = z["dist_bp"] / z["atr30_bp"]
        z["rel"] = rel
        de = np.quantile(rel[isw], np.linspace(0, 1, 11)[1:-1])
        ae = np.quantile(z["atr30_bp"][isw], [1 / 3, 2 / 3])
        z["dec"] = np.searchsorted(de, rel, side="right")
        z["ter"] = np.searchsorted(ae, z["atr30_bp"], side="right")
        parts.append(z)
    keys = [k for k in parts[0] if np.ndim(parts[0][k]) == 1]
    d = {k: np.concatenate([p[k] for p in parts]) for k in keys}
    d["day"] = d["tc"] // 1440
    # matching strata for the statistic (era handled by subsetting) and for the permutation (era included)
    d["strat"] = ((d["sym"] * 2 + (d["side"] > 0)) * 10 + d["dec"]) * 3 + d["ter"]
    d["pstrat"] = d["strat"] * 2 + d["era"]
    return d


def matched(y, unf, strat, day):
    """ATT-style matched difference unfinished - finished within strata; day-clustered SE (fixed stratum weights)."""
    y = y.astype(float)
    us = np.unique(strat)
    ok = np.zeros(len(y), bool)
    a = np.zeros(len(y))
    mu = np.zeros(len(y))
    nu_tot = 0
    parts = []
    for s in us:
        w = strat == s
        iu, ifn = w & unf, w & ~unf
        if iu.sum() == 0 or ifn.sum() == 0:
            continue
        ok |= w
        parts.append((s, iu, ifn))
        nu_tot += iu.sum()
    est = 0.0
    for s, iu, ifn in parts:
        nu, nf = iu.sum(), ifn.sum()
        mu_u, mu_f = y[iu].mean(), y[ifn].mean()
        est += nu / nu_tot * (mu_u - mu_f)
        a[iu] = 1.0 / nu_tot
        a[ifn] = -(nu / nu_tot) / nf
        mu[iu], mu[ifn] = mu_u, mu_f
    infl = a * (y - mu)
    infl[~ok] = 0
    ud, inv = np.unique(day[ok], return_inverse=True)
    se = np.sqrt(np.sum(np.bincount(inv, weights=infl[ok]) ** 2))
    pu = y[ok & unf].mean() if (ok & unf).any() else np.nan
    return est, est / se if se > 0 else np.nan, pu, pu - est, int((ok & unf).sum()), int((ok & ~unf).sum())


def tclust(x, day):
    x = np.asarray(x, float)
    if len(x) < 3:
        return np.nan, np.nan
    ud, inv = np.unique(day, return_inverse=True)
    m = x.mean()
    s = np.bincount(inv, weights=x - m)
    se = np.sqrt(np.sum(s ** 2)) / len(x)
    return m, (m / se if se > 0 else np.nan)


def greedy(sel_idx, tc, xm, sym):
    """One open trade per symbol: indices (sorted by tc) of trades taken."""
    taken = []
    for s in np.unique(sym[sel_idx]):
        ii = sel_idx[sym[sel_idx] == s]
        t, x = tc[ii], xm[ii]
        nxt = np.searchsorted(t, x, side="right")
        j = 0
        n = len(ii)
        while j < n:
            taken.append(ii[j])
            j = nxt[j]
    return np.sort(np.array(taken, dtype=np.int64))


def main(syms):
    d = load(syms)
    P("symbols", syms, "turns", len(d["tc"]), "unfinished share", round(d["unf"].mean(), 3))
    for si, s in enumerate(syms):
        w = d["sym"] == si
        P(f"  {s}: turns {w.sum()}, unf share {d['unf'][w].mean():.3f}, touched row before confirmation "
          f"{d['pre_touch'][w].mean():.3f}, median dist {np.median(d['rel'][w]):.2f} ATR30 / "
          f"{np.median(d['dist_bp'][w]):.1f} bp, median ATR30 {np.median(d['atr30_bp'][w]):.1f} bp")
    # raw distance by label (why matching matters)
    for lab, nm in ((True, "unf"), (False, "fin")):
        w = d["unf"] == lab
        P(f"  {nm}: median dist {np.median(d['rel'][w]):.3f} ATR30, mean ATR30 {d['atr30_bp'][w].mean():.1f} bp")

    # ---------------- 1. statistic ----------------
    P("\n== 1. Revisit statistic: P(trade back into the level row within H bars), matched unf - fin ==")
    P("group | H | n_unf n_fin | P(unf) | P(fin matched) | D (pts) | t(day)")

    def stat_rows(label, w, var="rev"):
        for h in HS:
            y = d[f"{var}{h}"]
            est, t, pu, pf, nu, nf = matched(y[w], d["unf"][w], d["strat"][w], d["day"][w])
            P(f"{label} | {h} | {nu} {nf} | {100 * pu:.1f} | {100 * pf:.1f} | {100 * est:+.2f} | {t:.2f}")

    for era, nm in ((0, "IS"), (1, "VAL")):
        stat_rows(f"pooled {nm}", d["era"] == era)
    for era, nm in ((0, "IS"), (1, "VAL")):
        for si, s in enumerate(syms):
            stat_rows(f"{s} {nm}", (d["era"] == era) & (d["sym"] == si))
        for sd, snm in ((1, "highs"), (-1, "lows")):
            stat_rows(f"{snm} {nm}", (d["era"] == era) & (d["side"] == sd))
    for y in range(2020, 2025):
        stat_rows(f"year {y}", d["year"] == y)
    P("info: beyond the extreme (high > swing high / low < swing low)")
    for era, nm in ((0, "IS"), (1, "VAL")):
        stat_rows(f"ext pooled {nm}", d["era"] == era, var="ext")
    P("info: excluding turns that touched the row before confirmation")
    for era, nm in ((0, "IS"), (1, "VAL")):
        stat_rows(f"no-pretouch {nm}", (d["era"] == era) & ~d["pre_touch"])
    # permutation null of the matched difference, pooled per era
    P("permutation (labels shuffled within strata, 200 draws): percentile of real D")
    for era, nm in ((0, "IS"), (1, "VAL")):
        w = d["era"] == era
        for h in HS:
            y = d[f"rev{h}"][w].astype(float)
            st = d["strat"][w]
            lab = d["unf"][w]
            real = matched(y, lab, st, d["day"][w])[0]
            null = []
            order = np.argsort(st, kind="stable")
            bounds = np.r_[0, np.flatnonzero(np.diff(st[order])) + 1, len(st)]
            for _ in range(200):
                pl = lab.copy()
                for a, b in zip(bounds[:-1], bounds[1:]):
                    seg = order[a:b]
                    pl[seg] = lab[seg][rng.permutation(b - a)]
                null.append(matched(y, pl, st, d["day"][w])[0])
            null = np.array(null)
            P(f"  {nm} H{h}: D {100 * real:+.2f} pts, null sd {100 * null.std():.2f}, percentile "
              f"{100 * (null < real).mean():.1f}")
    # revisit by distance decile (pooled IS + VAL), raw rates
    P("raw revisit rate by distance decile (pooled, H48): decile | P(unf) n | P(fin) n")
    for dec in range(10):
        w = d["dec"] == dec
        u, f = w & d["unf"], w & ~d["unf"]
        P(f"  {dec} | {100 * d['rev48'][u].mean():.1f} {u.sum()} | {100 * d['rev48'][f].mean():.1f} {f.sum()}")

    # ---------------- 2. trade cells ----------------
    P("\n== 2. Trade cells: enter toward the level at confirmation, TP one row before it, symmetric stop ==")
    cells = []
    for h in HS:
        for flt in ("D0", "D1"):
            base = np.isfinite(d[f"net{h}"])
            if flt == "D1":
                base &= np.isfinite(d["datr_bp"]) & (d["tp_bp"] >= 0.10 * d["datr_bp"]) & \
                        (d["tp_bp"] <= 0.30 * d["datr_bp"])
            cells.append((f"H{h}-{flt}", h, base))

    def cell_stats(idx, h):
        r = {}
        for era in (0, 1):
            ii = idx[d["era"][idx] == era]
            x = d[f"net{h}"][ii]
            m, t = tclust(x, d["day"][ii])
            ms, ts = tclust(d[f"str{h}"][ii], d["day"][ii])
            li = ii[np.isfinite(d[f"late{h}"][ii])]
            ml, tl = tclust(d[f"late{h}"][li], d["day"][li])
            rr = (x / d["tp_bp"][ii]).mean() if len(ii) else np.nan
            r[era] = dict(n=len(ii), m=m, t=t, sd=x.std() if len(x) else np.nan, R=rr, ms=ms, ts=ts, ml=ml, tl=tl,
                          tp=np.median(d["tp_bp"][ii]) if len(ii) else np.nan,
                          win=(d[f"net{h}"][ii] > 0).mean() if len(ii) else np.nan)
        return r

    real = {}
    P("cell label | era | n | net bp | t | net R | median TP bp | win | x1.5 net (t) | late net (t)")
    for name, h, base in cells:
        for lab, lnm in ((True, "unf"), (False, "fin")):
            idx = greedy(np.flatnonzero(base & (d["unf"] == lab)), d["tc"], d[f"xm{h}"], d["sym"])
            r = cell_stats(idx, h)
            real[(name, lab)] = (idx, r)
            for era, enm in ((0, "IS"), (1, "VAL")):
                q = r[era]
                P(f"{name} {lnm} | {enm} | {q['n']} | {q['m']:+.2f} | {q['t']:.2f} | {q['R']:+.3f} | {q['tp']:.1f} | "
                  f"{q['win']:.3f} | {q['ms']:+.2f} ({q['ts']:.2f}) | {q['ml']:+.2f} ({q['tl']:.2f})")
        # difference unf - fin
        for era, enm in ((0, "IS"), (1, "VAL")):
            ru, rf = real[(name, True)][1][era], real[(name, False)][1][era]
            se = np.sqrt((ru["m"] / ru["t"]) ** 2 + (rf["m"] / rf["t"]) ** 2)
            P(f"{name} unf-fin | {enm} | diff {ru['m'] - rf['m']:+.2f} bp | t {(ru['m'] - rf['m']) / se:.2f}")

    P("by year (net bp per trade, n) and by symbol, unfinished cells and controls")
    for name, h, base in cells:
        for lab, lnm in ((True, "unf"), (False, "fin")):
            idx = real[(name, lab)][0]
            yr = []
            for y in range(2020, 2025):
                ii = idx[d["year"][idx] == y]
                yr.append(f"{y}: {d[f'net{h}'][ii].mean():+.2f} ({len(ii)})")
            sy = []
            for si, s in enumerate(syms):
                for era, enm in ((0, "IS"), (1, "VAL")):
                    ii = idx[(d["sym"][idx] == si) & (d["era"][idx] == era)]
                    m, t = tclust(d[f"net{h}"][ii], d["day"][ii])
                    sy.append(f"{s[:3]} {enm} {m:+.2f} t {t:.2f} n {len(ii)}")
            npos = sum(d[f"net{h}"][idx[d["year"][idx] == y]].mean() > 0 for y in range(2020, 2025))
            P(f"{name} {lnm}: years+ {npos}/5 | " + " ; ".join(yr))
            P("   " + " ; ".join(sy))

    # permutation benchmark for the unfinished cells
    P(f"permutation benchmark ({NPERM} draws, labels shuffled within symbol x era x side x distance decile x ATR "
      "tercile): percentile of real unf-cell t, and of real unf - fin diff")
    st = d["pstrat"]
    order = np.argsort(st, kind="stable")
    bounds = np.r_[0, np.flatnonzero(np.diff(st[order])) + 1, len(st)]
    nullt = {(c[0], e): [] for c in cells for e in (0, 1)}
    nulld = {(c[0], e): [] for c in cells for e in (0, 1)}
    nullmax = {0: [], 1: []}
    lab0 = d["unf"]
    for it in range(NPERM):
        pl = lab0.copy()
        for a, b in zip(bounds[:-1], bounds[1:]):
            seg = order[a:b]
            pl[seg] = lab0[seg][rng.permutation(b - a)]
        mx = {0: -np.inf, 1: -np.inf}
        for name, h, base in cells:
            iu = greedy(np.flatnonzero(base & pl), d["tc"], d[f"xm{h}"], d["sym"])
            ifn = greedy(np.flatnonzero(base & ~pl), d["tc"], d[f"xm{h}"], d["sym"])
            for era in (0, 1):
                a1 = iu[d["era"][iu] == era]
                a2 = ifn[d["era"][ifn] == era]
                m1, t1 = tclust(d[f"net{h}"][a1], d["day"][a1])
                m2, _ = tclust(d[f"net{h}"][a2], d["day"][a2])
                nullt[(name, era)].append(t1)
                nulld[(name, era)].append(m1 - m2)
                mx[era] = max(mx[era], t1)
        for era in (0, 1):
            nullmax[era].append(mx[era])
    for era, enm in ((0, "IS"), (1, "VAL")):
        rmax = -np.inf
        for name, h, base in cells:
            ru, rf = real[(name, True)][1][era], real[(name, False)][1][era]
            rmax = max(rmax, ru["t"])
            nt, nd = np.array(nullt[(name, era)]), np.array(nulld[(name, era)])
            P(f"  {enm} {name}: real t {ru['t']:.2f} pct {100 * (nt < ru['t']).mean():.1f} | real diff "
              f"{ru['m'] - rf['m']:+.2f} pct {100 * (nd < ru['m'] - rf['m']).mean():.1f} | null t 95th "
              f"{np.quantile(nt, 0.95):.2f}")
        nm_ = np.array(nullmax[era])
        P(f"  {enm} max-over-4-cells: real max t {rmax:.2f}, null 95th {np.quantile(nm_, 0.95):.2f}, pct "
          f"{100 * (nm_ < rmax).mean():.1f}")
    P("power at VAL size (unf cells): mean / sd x sqrt(n_VAL x 22 / 36)")
    for name, h, base in cells:
        q = real[(name, True)][1][1]
        P(f"  {name}: {q['m'] / q['sd'] * np.sqrt(q['n'] * 22 / 36):.2f}")
    with open(os.path.join(OUT, "results_" + "_".join(s[:3] for s in syms) + ".txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    syms = sys.argv[1:] or sorted(os.path.basename(p)[6:-4] for p in glob.glob(os.path.join(OUT, "turns_*.npz")))
    main(syms)
