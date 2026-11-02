"""Stream P analysis. `python analyze.py path` (IS path by bucket) or `python analyze.py cells` (declared cells)."""
import sys
from datetime import date

import numpy as np

from plib import CACHE, OUT

Z = np.load(CACHE / "days.npz")
ORD = Z["date"]
YEAR = np.array([date.fromordinal(int(o)).year for o in ORD])
assert YEAR.max() <= 2024
IS = (YEAR >= 2016) & (YEAR <= 2021)
VAL = (YEAR >= 2022) & (YEAR <= 2024)
FILL_OFF = list(Z["fill_off"])
COMM = 0.6


def surprise():
    g = np.log(Z["fix"] / Z["pre_mid"]) * 1e4
    valid = Z["pre_age"] <= 60
    s = np.full(g.size, np.nan)
    hist = []
    for i in range(g.size):
        if len(hist) >= 10:
            s[i] = g[i] - np.median(hist[-20:])
        if valid[i]:
            hist.append(g[i])
    s[~valid] = np.nan
    return g, s


G, S = surprise()


def fill(off):
    j = FILL_OFF.index(off)
    f = Z["fills"][:, j, :]
    return f[:, 0], f[:, 1], f[:, 2]


def trade(d, h, late=0.0, spread_mult=1.0, comm=COMM, side=None):
    """Per-day net bp for side (default sign(S)); nan where no valid fills."""
    side = np.sign(S) if side is None else side
    eb, ea, el = fill(d + late)
    xb, xa, xl = fill(h + late)
    emid, xmid = (eb + ea) / 2, (xb + xa) / 2
    gross_mid = side * np.log(xmid / emid) * 1e4
    half = ((ea - eb) / 2 / emid + (xa - xb) / 2 / xmid) * 1e4
    net = gross_mid - spread_mult * half - comm
    ok = (el <= 60) & (xl <= 60) & np.isfinite(net) & np.isfinite(S)
    return np.where(ok, net, np.nan), np.where(ok, gross_mid, np.nan), np.where(ok, half, np.nan)


def tstat(x):
    x = x[np.isfinite(x)]
    if x.size < 3:
        return np.nan, np.nan, x.size
    return x.mean(), x.mean() / (x.std(ddof=1) / np.sqrt(x.size)), x.size


def path():
    off = Z["path_off"]
    P = Z["path"]
    pre = Z["pre_mid"]
    rel = np.log(P / pre[:, None]) * 1e4
    edges = [(-np.inf, -15), (-15, -5), (-5, 5), (5, 15), (15, np.inf)]
    lines = ["IS 2016-21. Mean mid change vs the pre-01:15 mid, bp, multiplied by sign(s) (so + = towards the fix);",
             "the |s| < 5 row is unsigned-by-sign(s) too. n days, mean s.",
             "bucket n mean_s | " + " ".join(f"{int(o):+d}s" for o in off)]
    ok = IS & np.isfinite(S)
    masks = [ok & (S <= -15), ok & (S > -15) & (S <= -5), ok & (S > -5) & (S < 5), ok & (S >= 5) & (S < 15),
             ok & (S >= 15)]
    for (lo, hi), m in zip(edges, masks):
        r = rel[m] * np.sign(S[m])[:, None]
        mu = np.nanmean(r, 0)
        se = np.nanstd(r, 0, ddof=1) / np.sqrt(np.isfinite(r).sum(0))
        lines.append(f"({lo},{hi}] n={m.sum()} s={np.mean(S[m]):+.1f} | " + " ".join(f"{a:+.2f}" for a in mu))
        lines.append("      t       | " + " ".join(f"{a / b:+.1f}" for a, b in zip(mu, se)))
    # share of the 0..+30 min move done by each offset, |s| >= 5
    m = IS & np.isfinite(S) & (np.abs(S) >= 5)
    r = rel[m] * np.sign(S[m])[:, None]
    mu = np.nanmean(r, 0)
    i0 = list(off).index(0)
    lines.append("|s|>=5 share of the 0 -> +30 min move done at each offset: " + " ".join(
        f"{int(o):+d}s {(mu[k] - mu[i0]) / (mu[-1] - mu[i0]):.2f}" for k, o in enumerate(off) if o > 0))
    lines.append(f"share of IS days |s|>=5: {np.mean(np.abs(S[IS & np.isfinite(S)]) >= 5):.3f}, "
                 f"|s|>=15: {np.mean(np.abs(S[IS & np.isfinite(S)]) >= 15):.3f}; VAL: "
                 f"{np.mean(np.abs(S[VAL & np.isfinite(S)]) >= 5):.3f} / {np.mean(np.abs(S[VAL & np.isfinite(S)]) >= 15):.3f}")
    lines.append(f"IS sd of s {np.nanstd(S[IS]):.2f} bp, median |g| {np.nanmedian(np.abs(G[IS])):.1f} bp")
    txt = "\n".join(lines)
    print(txt)
    (OUT / "path_IS.txt").write_text(txt + "\n")


CELLS = [(k, d, h) for k in (5, 15) for d in (5, 30) for h in (360, 1800)]
RNG = np.random.default_rng(67)


def cell_stats(k, d, h, era, lines):
    sel = era & np.isfinite(S) & (np.abs(S) >= k)
    net, gm, half = trade(d, h)
    x = np.where(sel, net, np.nan)
    mu, t, n = tstat(x)
    sd = np.nanstd(x, ddof=1)
    sh = mu / sd
    x15 = np.where(sel, trade(d, h, spread_mult=1.5, comm=COMM * 1.5)[0], np.nan)
    xl60 = np.where(sel, trade(d, h, late=60)[0], np.nan)
    xl30 = np.where(sel, trade(d, h, late=30)[0], np.nan)
    xl025 = np.where(sel, trade(d, h, late=0.25)[0], np.nan)
    # random: n random eligible days of the era, random side
    elig = np.flatnonzero(era & np.isfinite(trade(d, h, side=np.ones(S.size))[0]))
    full_pos = trade(d, h, side=np.ones(S.size))[0]
    full_neg = trade(d, h, side=-np.ones(S.size))[0]
    rnd = np.empty(1000)
    for b in range(1000):
        idx = RNG.choice(elig, n, replace=False)
        sg = RNG.integers(0, 2, n)
        rnd[b] = np.where(sg == 1, full_pos[idx], full_neg[idx]).mean()
    # sign shuffle on own days
    own = np.flatnonzero(np.isfinite(x))
    shf = np.empty(1000)
    for b in range(1000):
        sg = RNG.integers(0, 2, own.size)
        shf[b] = np.where(sg == 1, full_pos[own], full_neg[own]).mean()
    yrs = {}
    for y in np.unique(YEAR[era]):
        yrs[int(y)] = np.nanmean(np.where(YEAR == y, x, np.nan))
    return dict(mu=mu, t=t, n=n, sd=sd, sh=sh, gross=np.nanmean(np.where(sel, gm, np.nan)),
                cost=np.nanmean(np.where(sel, half, np.nan)) + COMM, gm=np.where(sel, gm, np.nan),
                gt=tstat(np.where(sel, gm, np.nan))[1],
                x15=np.nanmean(x15), l60=np.nanmean(xl60), l30=np.nanmean(xl30), l025=np.nanmean(xl025),
                rnd=np.mean(mu > rnd) * 100, shf=np.mean(mu > shf) * 100, yrs=yrs, x=x)


def cells():
    out = ["cell | era | n | gross mid (t) | cost | net (t) | sd | Sharpe/trade | x1.5 | +0.25s | +30s | +60s | "
           "rand % | sign-shuffle % | years"]
    res = {}
    for k, d, h in CELLS:
        name = f"k{k}_d{d}_h{h // 60}"
        for ename, era in (("IS", IS), ("VAL", VAL)):
            r = cell_stats(k, d, h, era, out)
            res[(name, ename)] = r
            yrs = " ".join(f"{y % 100}:{v:+.1f}" for y, v in r["yrs"].items())
            out.append(f"{name} | {ename} | {r['n']} | {r['gross']:+.2f} ({r['gt']:+.2f}) | {r['cost']:.2f} | {r['mu']:+.2f} "
                       f"({r['t']:+.2f}) | {r['sd']:.2f} | {r['sh']:+.3f} | {r['x15']:+.2f} | {r['l025']:+.2f} | "
                       f"{r['l30']:+.2f} | {r['l60']:+.2f} | {r['rnd']:.0f} | {r['shf']:.0f} | {yrs}")
            print(out[-1], flush=True)
    # power at VAL size: Sharpe_VAL * sqrt(450 * q_VAL)
    out.append("")
    out.append("power at VAL size = VAL Sharpe/trade x sqrt(450 x VAL share of fix days with |s|>=k)")
    for k, d, h in CELLS:
        name = f"k{k}_d{d}_h{h // 60}"
        q = np.mean(np.abs(S[VAL & np.isfinite(S)]) >= k)
        pv = res[(name, "VAL")]["sh"] * np.sqrt(450 * q)
        pi = res[(name, "IS")]["sh"] * np.sqrt(450 * np.mean(np.abs(S[IS & np.isfinite(S)]) >= k))
        out.append(f"{name}: q_VAL {q:.3f}, n_HOLD ~{450 * q:.0f}, power IS-size {pi:+.2f}, VAL-size {pv:+.2f}")
    # family null: max IS gross-mid t over 8 cells under a shared per-day sign flip (signal, not cost)
    X = np.array([res[(f"k{k}_d{d}_h{h // 60}", "IS")]["gm"] for k, d, h in CELLS])
    obs = np.nanmax([tstat(r)[1] for r in X])
    mx = np.empty(1000)
    for b in range(1000):
        flip = RNG.choice([-1.0, 1.0], X.shape[1])
        mx[b] = np.nanmax([tstat(r * flip)[1] for r in X])
    out.append(f"family (gross mid): observed max IS t {obs:.2f}; shared sign-flip null median {np.median(mx):.2f}, "
               f"p95 {np.percentile(mx, 95):.2f}, p = {np.mean(mx >= obs):.3f}")
    # cost a cell would need for DEMO (IS net t 2.0) and LIVE (VAL power 3)
    for k, d, h in CELLS:
        nm = f"k{k}_d{d}_h{h // 60}"
        ri, rv = res[(nm, "IS")], res[(nm, "VAL")]
        q = np.mean(np.abs(S[VAL & np.isfinite(S)]) >= k)
        need_demo = ri["gross"] - 2.0 * ri["sd"] / np.sqrt(ri["n"])
        need_live = rv["gross"] - 3.0 * rv["sd"] / np.sqrt(450 * q)
        out.append(f"{nm}: max round-trip cost for IS net t 2.0: {need_demo:+.2f} bp; for VAL power 3: {need_live:+.2f} bp "
                   f"(actual {ri['cost']:.2f} / {rv['cost']:.2f})")
    txt = "\n".join(out)
    print("\n".join(out[-10:]))
    (OUT / "cells.txt").write_text(txt + "\n")
    np.savez(CACHE / "cell_trades.npz", **{f"{a}_{b}": v["x"] for (a, b), v in res.items()}, date=ORD)


if __name__ == "__main__":
    {"path": path, "cells": cells}[sys.argv[1]]()
