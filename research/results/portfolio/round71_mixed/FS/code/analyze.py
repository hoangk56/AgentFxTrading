"""Round 71 FS: cells X5 / X8 x H15 / H60 with aggTrade entry, measured half-spreads, checks (../HYPOTHESES_FS.md).

Inputs: out/cand.npz (events.py), data/spot_wicks/agg/*.npz + agg_progress.json (pull_agg.py), vol1d.npz (listing day).
Output: out/report.txt, out/cells.json, out/trades.npz (small).
"""
import datetime as dt
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

MIN, BP, T0 = C.MIN, C.BP, C.T0
HK = {15: 0, 60: 1}
FEE = 20 / BP


def clt(x, day):
    x = np.asarray(x, float); n = len(x)
    if n < 3:
        return np.nan, np.nan, np.nan, n
    m = x.mean()
    _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m)
    G = len(g)
    se = np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n
    return m, (m / se if se > 0 else np.nan), x.std(ddof=1), n


def dedup(sym, t):
    o = np.lexsort((t, sym))
    keep = np.zeros(len(t), bool)
    ls, lt = -1, -10 ** 9
    for j in o:
        if sym[j] != ls or t[j] - lt > 60:
            keep[j] = True; ls, lt = sym[j], t[j]
    return keep


def spread_w(T, P, Q, M, a, b):
    k0 = np.searchsorted(T, a, "left"); k1 = np.searchsorted(T, b, "left")
    p, q, m = P[k0:k1], Q[k0:k1], M[k0:k1]
    if (~m).sum() == 0 or m.sum() == 0:
        return np.nan
    vb = (p[~m] * q[~m]).sum() / q[~m].sum(); vs = (p[m] * q[m]).sum() / q[m].sum()
    return (vb - vs) / ((vb + vs) / 2)


def half_sp(T, P, Q, M, a, widths, fallback):
    """measured half-spread over [a, a + w) for the first width with both sides, floored at 0; else fallback."""
    for w in widths:
        s = spread_w(T, P, Q, M, a, a + w)
        if np.isfinite(s):
            return max(s / 2, 0.0), w
    return fallback, -1


def yr_of(day):
    return np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).year for d in day])


def main():
    z = np.load(os.path.join(C.DATA, "cand.npz"))
    syms = list(z["syms"])
    sym, t, r = z["sym"], z["t"].astype(np.int64), z["r"]
    N = len(t)
    ce = T0 + (t + 1) * MIN
    prog = json.load(open(os.path.join(C.DATA, "agg_progress.json")))
    done = set(int(j) for j in prog["done_events"])
    p0 = np.full(N, np.nan); lat = np.full(N, np.nan); hin = np.full(N, np.nan); hin_w = np.zeros(N, int)
    hinl = np.full(N, np.nan); hout = np.full((N, 2), np.nan); notl = np.full(N, np.nan); has = np.zeros(N, bool)
    cache = {}
    for j in sorted(done):
        parts = []
        for fn in prog["ev_files"][str(j)]:
            p = os.path.join(C.DATA, "agg", fn + ".npz")
            if os.path.exists(p):
                if fn not in cache:
                    if len(cache) > 8:
                        cache.clear()
                    a = np.load(p); cache[fn] = (a["t"], a["p"], a["q"].astype(float), a["m"])
                parts.append(cache[fn])
        if not parts:
            continue
        T = np.concatenate([x[0] for x in parts]); P = np.concatenate([x[1] for x in parts])
        Q = np.concatenate([x[2] for x in parts]); M = np.concatenate([x[3] for x in parts])
        o = np.argsort(T, kind="stable"); T, P, Q, M = T[o], P[o], Q[o], M[o]
        c0 = int(ce[j])
        k = np.searchsorted(T, c0, "left")
        if k >= len(T):
            continue
        has[j] = True
        p0[j] = P[k]; lat[j] = (T[k] - c0) / 1000
        t_in = int(T[k])
        hin[j], hin_w[j] = half_sp(T, P, Q, M, t_in, (1000, 10000, 60000), 50 / BP)
        k1 = np.searchsorted(T, t_in + 1000, "left")
        notl[j] = float((P[k:k1] * Q[k:k1]).sum())
        hinl[j], _ = half_sp(T, P, Q, M, c0 + MIN, (1000, 10000, 60000), 50 / BP)
        for H, kk in HK.items():
            hout[j, kk], _ = half_sp(T, P, Q, M, c0 + (H + 1) * MIN, (10000, 60000), 25 / BP)
    tradable = has & (lat <= 60)
    with np.errstate(invalid="ignore"):
        dqc = np.abs(p0 / z["o1"] - 1)
    qc_line = (f"QC first aggTrade >= close_e vs spot kline open of e+1: equal (|d| < 1e-9) {np.nanmean(dqc[has] < 1e-9) * 100:.1f} %, "
               f"|d| > 10 bp {np.nanmean(dqc[has] > 1e-3) * 100:.1f} %")
    guard = tradable & (p0 <= z["cprev"] * (1 + r / 2))
    day = (T0 + t * MIN) // C.DAY
    yr = yr_of(day)
    era = np.where(t < C.VAL0, 0, 1)
    ym = np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).strftime("%Y-%m") for d in day])
    # listing day per symbol (first spot daily kline)
    v = np.load(os.path.join(C.DATA, "vol1d.npz"))
    vs = list(v["syms"]); first = {}
    for i, s in enumerate(vs):
        w = v["t"][v["sym"] == i]
        first[s] = w.min() // C.DAY if len(w) else -10 ** 6  # epoch days, as day
    age = np.array([day[j] - first.get(syms[sym[j]], -10 ** 6) for j in range(N)])
    X = {15: z["x15"], 60: z["x60"]}
    rnd, rnd_t = z["rnd"], z["rnd_t"].astype(np.int64)
    rnd_day = (T0 + rnd_t * MIN) // C.DAY
    L = []; P_ = L.append
    P_(f"candidates (r <= -5 %, idio, >= 10 trades, in universe) {N}: IS {(era == 0).sum()} VAL {(era == 1).sum()}")
    P_(f"  aggTrades pulled for {len(done)}; with a trade after close_e {has.sum()}; tradable (first trade <= 60 s) "
       f"{tradable.sum()}; guard passed {guard.sum()}")
    for en, e_ in (("IS", 0), ("VAL", 1)):
        q = tradable & (era == e_)
        P_(f"  {en}: first-trade latency median {np.median(lat[q]):.3f} s p90 {np.percentile(lat[q], 90):.2f} s; "
           f"hs_in median {np.median(hin[q]) * BP:.1f} mean {np.mean(hin[q]) * BP:.1f} bp (width 1 s {np.mean(hin_w[q] == 1000) * 100:.0f} %, "
           f"10 s {np.mean(hin_w[q] == 10000) * 100:.0f} %, 60 s {np.mean(hin_w[q] == 60000) * 100:.0f} %, fallback "
           f"{np.mean(hin_w[q] == -1) * 100:.0f} %); hs_out60 median {np.median(hout[q, 1]) * BP:.1f} mean "
           f"{np.mean(hout[q, 1]) * BP:.1f}; USD in entry second median {np.median(notl[q]):,.0f}")
    P_("  " + qc_line)
    cells = []
    null_max = np.full(rnd.shape[1], -np.inf)
    P_("\ncell | era | n | net | t | S | median | gross | x1.5 (t) | late e+1 close (t) | rand % | crash-day share")
    for Xp in (5, 8):
        base = np.where(guard & (r <= -Xp / 100))[0]
        base = base[dedup(sym[base], t[base])]
        for H in (15, 60):
            kk = HK[H]
            jj = base[np.isfinite(X[H][base])]
            g = X[H][jj] / p0[jj] - 1
            cost = FEE + hin[jj] + hout[jj, kk]
            net = g - cost
            gl = X[H][jj] / z["c1"][jj] - 1
            netl = gl - FEE - hinl[jj] - hout[jj, kk]
            res = {"cell": f"X{Xp} H{H}", "years": {}}
            for e_, en in ((0, "IS"), (1, "VAL")):
                q = era[jj] == e_; dq = day[jj][q]
                m, tt, sd, n = clt(net[q], dq)
                x15 = clt(g[q] - 1.5 * cost[q], dq)
                wl = np.isfinite(netl[q])
                lt = clt(netl[q][wl], dq[wl])
                rr = rnd[jj[q], :, kk].astype(float) - cost[q][:, None]
                rmeans = np.nanmean(rr, axis=0)
                rpct = float(np.mean(rmeans < m)) * 100 if n else np.nan
                if e_ == 0 and n >= 3:
                    tts = []
                    for i in range(rr.shape[1]):
                        w = np.isfinite(rr[:, i])
                        tts.append(clt(rr[w, i], rnd_day[jj[q], i][w])[1])
                    null_max = np.maximum(null_max, np.nan_to_num(np.array(tts, float), nan=-np.inf))
                dd =dict(zip(*np.unique(dq, return_counts=True)))
                crash_share = float(np.mean([dd[d] >= 5 for d in dq])) if n else np.nan
                # concentration
                ss = sym[jj][q]
                ex = {}
                if n >= 5:
                    tot = {s_: net[q][ss == s_].sum() for s_ in np.unique(ss)}
                    top = sorted(tot, key=lambda s_: -tot[s_])[:3]
                    w = ~np.isin(ss, top); x = clt(net[q][w], dq[w])
                    ex["drop_top3_coins"] = ([syms[s_] for s_ in top], x[0] * BP, x[1])
                    dtot = {d_: net[q][dq == d_].sum() for d_ in np.unique(dq)}
                    topd = sorted(dtot, key=lambda d_: -dtot[d_])[:5]
                    w = ~np.isin(dq, topd); x = clt(net[q][w], dq[w])
                    ex["drop_top5_days"] = ([str(np.datetime64(int(d_), "D")) for d_ in topd], x[0] * BP, x[1])
                    if e_ == 0:
                        # dq = days since epoch: 2020-03-12, 2020-03-13, 2021-05-19
                        bad = np.isin(dq, [1583971200000 // C.DAY, 1584057600000 // C.DAY, 1621382400000 // C.DAY])
                    else:
                        bad = np.isin(ym[jj][q], ["2022-05", "2022-11"])
                    x = clt(net[q][~bad], dq[~bad]); ex["excl_crash_days"] = (int((~bad).sum()), x[0] * BP, x[1])
                    nl = age[jj][q] < 90
                    x = clt(net[q][~nl], dq[~nl]); y_ = clt(net[q][nl], dq[nl])
                    ex["listed_ge90d"] = (int((~nl).sum()), x[0] * BP, x[1]); ex["listed_lt90d"] = (int(nl.sum()), y_[0] * BP, y_[1])
                    nc = len(np.unique(ss)); pos = np.mean([net[q][ss == s_].mean() > 0 for s_ in np.unique(ss)])
                    ex["coins"] = (nc, float(pos))
                    ex["win"] = float(np.mean(net[q] > 0))
                    ex["hs_in_median"] = float(np.median(hin[jj][q])) * BP
                    ex["gross_median"] = float(np.median(g[q])) * BP
                res[en] = dict(n=int(n), net=m * BP, t=tt, sd=sd * BP, S=m / sd if sd else np.nan,
                               median=float(np.median(net[q])) * BP if n else np.nan,
                               gross=float(g[q].mean()) * BP if n else np.nan, cost=float(cost[q].mean()) * BP if n else np.nan,
                               x15=x15[0] * BP, x15_t=x15[1], late=lt[0] * BP, late_t=lt[1], rand=rpct,
                               rand_mean=float(np.nanmean(rmeans)) * BP if n else np.nan, crash_share=crash_share, **ex)
                P_(f"{res['cell']} | {en} | {n} | {m * BP:+.1f} | {tt:+.2f} | {res[en]['S']:+.3f} | {res[en]['median']:+.0f} | "
                   f"{res[en]['gross']:+.1f} | {x15[0] * BP:+.1f} ({x15[1]:+.2f}) | {lt[0] * BP:+.1f} ({lt[1]:+.2f}) | "
                   f"{rpct:.0f} (rand mean {res[en]['rand_mean']:+.1f}) | {crash_share:.2f}")
            for y in range(2020, 2025):
                w = yr[jj] == y
                res["years"][y] = (float(net[w].mean()) * BP if w.any() else None, int(w.sum()))
            V = res["VAL"]
            n24 = res["years"][2024][1]
            nH_val = 0.61 * V["n"]; nH_24 = n24 * 22 / 12
            res["nH_val"], res["nH_2024"] = nH_val, nH_24
            res["power_trade"] = V["S"] * np.sqrt(nH_val) if V["n"] else np.nan
            res["power_trade_2024rate"] = V["S"] * np.sqrt(nH_24) if V["n"] else np.nan
            res["power_clust"] = V["t"] * np.sqrt(0.61) if V["n"] else np.nan
            P_("   years " + " ".join(f"{y}:{'na' if v_[0] is None else f'{v_[0]:+.0f}'}(n{v_[1]})" for y, v_ in res["years"].items())
               + f" | power trade {res['power_trade']:+.2f} (2024 rate {res['power_trade_2024rate']:+.2f}, n_H {nH_24:.0f}) "
               f"clust {res['power_clust']:+.2f}")
            for en in ("IS", "VAL"):
                x = res[en]
                if "coins" in x:
                    P_(f"   {en}: coins {x['coins'][0]} (+ {x['coins'][1] * 100:.0f} %), win {x['win'] * 100:.0f} %, gross median "
                       f"{x['gross_median']:+.0f}, hs_in med {x['hs_in_median']:.1f}, cost mean {x['cost']:.1f} | drop top3 "
                       f"{x['drop_top3_coins'][0]} {x['drop_top3_coins'][1]:+.1f} ({x['drop_top3_coins'][2]:+.2f}) | drop top5 days "
                       f"{x['drop_top5_days'][1]:+.1f} ({x['drop_top5_days'][2]:+.2f}) {x['drop_top5_days'][0]} | excl crash days n "
                       f"{x['excl_crash_days'][0]} {x['excl_crash_days'][1]:+.1f} ({x['excl_crash_days'][2]:+.2f}) | listed>=90d n "
                       f"{x['listed_ge90d'][0]} {x['listed_ge90d'][1]:+.1f} ({x['listed_ge90d'][2]:+.2f}) <90d n {x['listed_lt90d'][0]} "
                       f"{x['listed_lt90d'][1]:+.1f}")
            cells.append(res)
            np.savez(os.path.join(C.OUT, f"trades_X{Xp}_H{H}.npz"), j=jj, sym=sym[jj], t=t[jj], r=r[jj], net=net, g=g,
                     cost=cost, netl=netl, hin=hin[jj], notl=notl[jj])
    rmax = max(c["IS"]["t"] for c in cells if np.isfinite(c["IS"]["t"]))
    nm = null_max[np.isfinite(null_max)]
    P_(f"\nmax-over-4 IS t: real {rmax:+.2f}; null median {np.median(nm):+.2f} p95 {np.percentile(nm, 95):+.2f}, "
       f"share null >= real {np.mean(nm >= rmax) * 100:.1f} %")
    open(os.path.join(C.OUT, "report.txt"), "w").write("\n".join(L) + "\n")
    json.dump(cells, open(os.path.join(C.OUT, "cells.json"), "w"), indent=1, default=str)
    print("\n".join(L))


if __name__ == "__main__":
    main()
