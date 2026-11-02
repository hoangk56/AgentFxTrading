"""Round 66 F0: cells E0 / E1 / E3 x H15 / H60 on F's T5-idio events, measured spread / slippage (../HYPOTHESES_F0.md).

Inputs (read-only): F/out/cand.npz (go, f, rnd), research/data/binance_1m_wicks/npz (kline open of e+1),
research/data/binance/funding via round 63 C's panel cache, research/data/wick_aggtrades/npz + progress.json.
Output: ../out/report.txt, ../out/cells.json, ../out/sample_rows.npz (small).
"""
import datetime as dt
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ev  # noqa: E402

R = ev.R
sys.path.insert(1, os.path.join(R, "results/portfolio/round63_parallel/C/code"))
import xs  # noqa: E402

OUT = os.path.join(HERE, "..", "out")
KL = os.path.join(R, "data", "binance_1m_wicks", "npz")
AG = os.path.join(R, "data", "wick_aggtrades")
MIN, BP = ev.MIN, ev.BP
HK = {15: 1, 60: 2}
LAT = (1, 3, 10)
NOTIONAL = 10000.0


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


def funding_sum(cumfr, te, tx):
    h1 = np.floor((te - xs.H0) / 3600000).astype(np.int64) + 1
    h2 = np.floor((tx - xs.H0) / 3600000).astype(np.int64)
    h1 = np.clip(h1, 0, len(cumfr) - 1); h2 = np.clip(h2 + 1, 0, len(cumfr) - 1)
    return np.where(h2 > h1, cumfr[h2] - cumfr[h1], 0.0)


def kline_open(sym, t):
    """open of bar t+1 (minutes since T0) from F's 1m npz."""
    tm = ev.T0 + (t + 1) * MIN
    ym = str(np.datetime64(int(tm), "ms"))[:7]
    z = np.load(os.path.join(KL, f"{sym}_{ym}.npz"))
    k = np.where(z["m"].astype(np.int64) == tm // MIN)[0]
    return float(z["o"][k[0]]) if len(k) else np.nan


def first_at(T, P, t0, mask=None):
    k = np.searchsorted(T, t0, "left")
    if mask is None:
        return (P[k], T[k]) if k < len(T) else (np.nan, np.nan)
    sub = np.where(mask[k:])[0]
    return (P[k + sub[0]], T[k + sub[0]]) if len(sub) else (np.nan, np.nan)


def vwap_at(T, P, Q, t0, mask, notional=NOTIONAL, cap=10000):
    k0 = np.searchsorted(T, t0, "left"); k1 = np.searchsorted(T, t0 + cap, "left")
    sel = np.arange(k0, k1)[mask[k0:k1]]
    if not len(sel):
        return np.nan
    v = P[sel] * Q[sel]
    cs = np.cumsum(v)
    j = np.searchsorted(cs, notional)
    j = min(j, len(sel) - 1)
    return cs[j] / Q[sel][:j + 1].sum()


def spread_w(T, P, Q, M, a, b):
    k0 = np.searchsorted(T, a, "left"); k1 = np.searchsorted(T, b, "left")
    p, q, m = P[k0:k1], Q[k0:k1], M[k0:k1]
    if (~m).sum() == 0 or m.sum() == 0:
        return np.nan
    vb = (p[~m] * q[~m]).sum() / q[~m].sum(); vs = (p[m] * q[m]).sum() / q[m].sum()
    return (vb - vs) / ((vb + vs) / 2)


def main():
    os.makedirs(OUT, exist_ok=True)
    E = ev.events(); z = E["z"]; idx = E["idx"]; syms = E["syms"]
    side = -np.sign(E["r"]); h = E["h"]
    yr = np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).year for d in E["day"]])
    P = xs.load(); FR = P["FR"]; psyms = P["syms"]
    go, f, rnd, rnd_t = z["go"], z["f"], z["rnd"], z["rnd_t"].astype(np.int64)
    rnd_day = (ev.T0 + rnd_t * MIN) // ev.DAY
    # funding correction: stamps in (close_e, close_e + 1 min], which F's f (from close_{e+1}) leaves out
    df = np.zeros(len(E["t"]))
    for s in np.unique(E["sym"][idx]):
        nm = syms[s]
        cumfr = np.concatenate([[0.0], np.cumsum(FR[psyms.index(nm)])]) if nm in psyms else np.zeros(FR.shape[1] + 1)
        j = idx[E["sym"][idx] == s]
        df[j] = side[j] * funding_sum(cumfr, E["close_e"][j].astype(float), E["close_e"][j].astype(float) + MIN)
    lines = []; Pl = lines.append
    Pl(f"events {len(idx)} IS {(E['era'][idx] == 0).sum()} VAL {(E['era'][idx] == 1).sum()}; "
       f"events with a stamp in (close_e, close_e+1m]: {(df[idx] != 0).sum()}")

    # ---- aggTrades sample
    prog = json.load(open(os.path.join(AG, "progress.json")))
    samp = [int(j) for j in prog["done_events"]]
    S = {}  # per sample event values
    cache = {}
    for j in samp:
        files = prog["ev_files"][str(j)]
        parts = []
        for fn in files:
            p = os.path.join(AG, "npz", fn + ".npz")
            if os.path.exists(p):
                if fn not in cache:
                    cache.clear(); a = np.load(p); cache[fn] = (a["t"], a["p"], a["q"].astype(float), a["m"])
                parts.append(cache[fn])
        if not parts:
            continue
        T = np.concatenate([x[0] for x in parts]); Pp = np.concatenate([x[1] for x in parts])
        Q = np.concatenate([x[2] for x in parts]); M = np.concatenate([x[3] for x in parts])
        o = np.argsort(T, kind="stable"); T, Pp, Q, M = T[o], Pp[o], Q[o], M[o]
        ce = int(E["close_e"][j]); sd = side[j]
        if not len(T) or T[-1] < ce + 62 * MIN:
            continue
        mine = (M == (sd < 0))      # taker side we would take at entry (buy = buyer taker = not buyer-maker)
        close_side = ~mine
        row = {"o_kl": kline_open(syms[E["sym"][j]], int(E["t"][j]))}
        row["p0"], row["t0"] = first_at(T, Pp, ce)
        for L in (0,) + LAT:
            row[f"pa{L}"], row[f"ta{L}"] = first_at(T, Pp, ce + L * 1000)
            row[f"ps{L}"], _ = first_at(T, Pp, ce + L * 1000, mine)
            row[f"pv{L}"] = vwap_at(T, Pp, Q, ce + L * 1000, mine)
        for H in (15, 60):
            tx = ce + (H + 1) * MIN
            row[f"xs{H}"], _ = first_at(T, Pp, tx, close_side)
            row[f"xv{H}"] = vwap_at(T, Pp, Q, tx, close_side)
            row[f"spx{H}"] = spread_w(T, Pp, Q, M, tx, tx + 10000)
        for a_, b_ in ((0, 1), (1, 3), (3, 10), (10, 60)):
            row[f"sp{a_}_{b_}"] = spread_w(T, Pp, Q, M, ce + a_ * 1000, ce + b_ * 1000)
        row["sp_pre"] = spread_w(T, Pp, Q, M, ce - 120000, ce - 60000)  # minute e-1
        row["sp_ev_last5"] = spread_w(T, Pp, Q, M, ce - 5000, ce)
        S[j] = row
    sj = np.array(sorted(S), np.int64)
    Pl(f"aggTrades sample: pulled events {len(samp)}, usable {len(sj)} (IS {(E['era'][sj] == 0).sum()}, "
       f"VAL {(E['era'][sj] == 1).sum()}); pull {prog['seconds']:.0f} s, {prog['bytes'] / 1e6:.0f} MB streamed")
    col = lambda k: np.array([S[j][k] for j in sj], float)  # noqa: E731

    # ---- QC and measured spread / slippage
    o_kl, p0 = col("o_kl"), col("p0")
    qc = np.abs(p0 / o_kl - 1)
    Pl(f"QC first aggTrade >= close_e vs kline open e+1: equal (|d| < 1e-9) {np.mean(qc < 1e-9) * 100:.1f} %, "
       f"median |d| {np.nanmedian(qc) * BP:.2f} bp, p95 {np.nanpercentile(qc, 95) * BP:.2f} bp")
    lat0 = (col("t0") - E["close_e"][sj]) / 1000
    Pl(f"time of first trade after close_e: median {np.nanmedian(lat0):.3f} s, p90 {np.nanpercentile(lat0, 90):.3f} s, "
       f"max {np.nanmax(lat0):.1f} s")
    Pl("\nmeasured spread (buyer-taker VWAP - seller-taker VWAP) / mid, bp, full spread; half = /2  [n with both sides]")
    hs = h[sj] * BP
    for k in ("sp_pre", "sp_ev_last5", "sp0_1", "sp1_3", "sp3_10", "sp10_60", "spx15", "spx60"):
        for en, e_ in (("IS", 0), ("VAL", 1)):
            v = col(k)[E["era"][sj] == e_] * BP; v = v[np.isfinite(v)]
            Pl(f"  {k:12s} {en:3s} n {len(v):4d} median {np.median(v):+7.1f} mean {np.mean(v):+7.1f} "
               f"p75 {np.percentile(v, 75):+7.1f} p90 {np.percentile(v, 90):+7.1f}")
    Pl(f"  model half-spread h: median {np.median(hs):.1f} bp; declared entry 3h = {3 * np.median(hs):.0f} bp half "
       f"(full {6 * np.median(hs):.0f}), stress 5h = {5 * np.median(hs):.0f} half")
    Pl("\nentry slippage vs the any-side first trade at the same latency, side-signed bp (cost to us > 0)")
    for L in (0,) + LAT:
        for kk, nm in ((f"ps{L}", "first taker-side trade"), (f"pv{L}", "$10k taker-side VWAP")):
            v = side[sj] * (col(kk) / col(f"pa{L}") - 1) * BP
            for en, e_ in (("IS", 0), ("VAL", 1)):
                w = v[(E["era"][sj] == e_) & np.isfinite(v)]
                Pl(f"  L={L:2d}s {nm:24s} {en:3s} n {len(w):4d} median {np.median(w):+6.1f} mean {np.mean(w):+7.1f} "
                   f"p90 {np.percentile(w, 90):+7.1f}")
    for L in LAT:
        v = side[sj] * (col(f"pa{L}") / o_kl - 1) * BP
        for en, e_ in (("IS", 0), ("VAL", 1)):
            w = v[(E["era"][sj] == e_) & np.isfinite(v)]
            Pl(f"  price drift kline o_(e+1) -> any-side first trade at {L:2d}s (side-signed, + = we pay more by waiting) "
               f"{en} median {np.median(w):+6.1f} mean {np.mean(w):+7.1f}")
    pa0 = col("pa0")
    for en, e_ in (("IS", 0), ("VAL", 1)):
        q = E["era"][sj] == e_
        v = side[sj][q] * (pa0[q] / o_kl[q] - 1) * BP
        Pl(f"  kline o_(e+1) vs first aggTrade >= close_e: {en} differ > 1 bp {np.mean(np.abs(v) > 1) * 100:.1f} %, "
           f"side-signed mean {np.nanmean(v):+.1f} median {np.nanmedian(v):+.1f} bp (+ = the kline open is cheaper "
           f"than any tradable price)")

    # ---- returns
    def gross_entry(jj, k, pe):
        """side x (exit / pe - 1) with F's kline exit x = o (1 + side go)."""
        o = o_kl_all[jj]
        x = o * (1 + side[jj] * go[jj, k])
        return side[jj] * (x / pe - 1)

    o_kl_all = np.full(len(E["t"]), np.nan); o_kl_all[sj] = o_kl
    fund = lambda jj, k: f[jj, k] + df[jj]  # noqa: E731
    cost_decl = 10 / BP + 4 * h; cost_5h = 10 / BP + 6 * h
    era, day = E["era"], E["day"]
    cells = []
    late_of = {"E0": "E1", "E0a": "E1", "E1": "E3", "E3": "E10"}

    def net_of(name, H, jj, cost):
        k = HK[H]
        if name == "E0":
            g = go[jj, k]
        else:
            L = 0 if name == "E0a" else int(name[1:])
            pe = np.array([S[j][f"pa{L}"] for j in jj]); g = gross_entry(jj, k, pe)
        return g - fund(jj, k) - cost[jj]

    def realfill(name, H, jj, kind):
        k = HK[H]; L = 0 if name in ("E0", "E0a") else int(name[1:])
        pe = np.array([S[j][f"p{kind}{L}"] for j in jj]); px = np.array([S[j][f"x{kind}{H}"] for j in jj])
        return side[jj] * (px / pe - 1) - fund(jj, k) - 10 / BP

    null_max = np.full(rnd.shape[1], -np.inf)
    Pl("\ncells (net bp / trade, t clustered by entry day)")
    hdr = "cell | era | n | net | t | S | median | gross | x1.5 | 5h stress | late (next L) | real 1st | real $10k | rand %"
    Pl(hdr)
    for name, base in (("E0", idx), ("E0s", sj), ("E0a", sj), ("E1", sj), ("E3", sj)):
        for H in (15, 60):
            nm = "E0" if name == "E0s" else name
            k = HK[H]
            jj = base[np.isfinite(go[base, k])]
            if nm != "E0":
                jj = jj[np.isfinite([S[j][f"pa{0 if nm == 'E0a' else int(nm[1:])}"] for j in jj])]
            net = net_of(nm, H, jj, cost_decl)
            res = {"cell": f"{name} H{H}", "years": {}}
            for e_, en in ((0, "IS"), (1, "VAL")):
                q = era[jj] == e_; dq = day[jj][q]
                m, t, sd, n = clt(net[q], dq)
                gross = (net[q] + cost_decl[jj][q]).mean()
                x15 = clt(net[q] - 0.5 * cost_decl[jj][q], dq)
                s5 = clt(net_of(nm, H, jj[q], cost_5h), dq)
                lt = late_of[nm]
                if nm == "E0" and name == "E0":
                    lt_v = (np.nan, np.nan)  # E1 exists only on the sample: reported on E0s
                else:
                    lt_v = clt(net_of(lt, H, jj[q], cost_decl), dq)
                if name == "E0":
                    rf1 = rf10 = (np.nan, np.nan)
                else:
                    a1 = realfill(nm, H, jj[q], "s"); w1 = np.isfinite(a1); rf1 = clt(a1[w1], dq[w1])
                    a2 = realfill(nm, H, jj[q], "v"); w2 = np.isfinite(a2); rf10 = clt(a2[w2], dq[w2])
                rr_ = rnd[jj[q], :, k].astype(float) - cost_decl[jj[q]][:, None]
                rpct = float(np.mean(np.nanmean(rr_, axis=0) < m)) * 100
                if e_ == 0:
                    tts = np.array([clt(rr_[:, i][np.isfinite(rr_[:, i])], rnd_day[jj[q], i][np.isfinite(rr_[:, i])])[1]
                                    for i in range(rr_.shape[1])])
                    if name not in ("E0s", "E0a"):
                        null_max = np.maximum(null_max, np.nan_to_num(tts, nan=-np.inf))
                res[en] = dict(n=int(n), net=m * BP, t=t, sd=sd * BP, S=m / sd, median=float(np.median(net[q])) * BP,
                               gross=gross * BP, x15=x15[0] * BP, x15_t=x15[1], s5=s5[0] * BP, s5_t=s5[1],
                               late=lt_v[0] * BP, late_t=lt_v[1], rf1=rf1[0] * BP, rf1_t=rf1[1], rf10=rf10[0] * BP,
                               rf10_t=rf10[1], rand=rpct,
                               crash=float(net[q][E["r"][jj][q] < 0].mean()) * BP,
                               spike=float(net[q][E["r"][jj][q] > 0].mean()) * BP)
                Pl(f"{res['cell']} | {en} | {n} | {m * BP:+.1f} | {t:+.2f} | {m / sd:+.3f} | {np.median(net[q]) * BP:+.0f} | "
                   f"{gross * BP:+.1f} | {x15[0] * BP:+.1f} ({x15[1]:+.2f}) | {s5[0] * BP:+.1f} ({s5[1]:+.2f}) | "
                   f"{lt_v[0] * BP:+.1f} ({lt_v[1]:+.2f}) | {rf1[0] * BP:+.1f} ({rf1[1]:+.2f}) | "
                   f"{rf10[0] * BP:+.1f} ({rf10[1]:+.2f}) | {rpct:.0f}")
            for y in range(2020, 2025):
                w = yr[jj] == y
                res["years"][y] = (float(net[w].mean()) * BP if w.any() else None, int(w.sum()))
            V = res["VAL"]
            res["n_fwd_trade"] = (3 / V["S"]) ** 2 if V["S"] > 0 else np.inf
            res["n_fwd_clust"] = V["n"] * (3 / V["t"]) ** 2 if V["t"] > 0 else np.inf
            res["months_fwd"] = max(res["n_fwd_trade"], res["n_fwd_clust"]) / (2080 / 22)
            Pl(f"   years " + " ".join(f"{y}:{'na' if v[0] is None else f'{v[0]:+.0f}'}(n{v[1]})" for y, v in res['years'].items())
               + f" | crash/spike IS {res['IS']['crash']:+.0f}/{res['IS']['spike']:+.0f} VAL {V['crash']:+.0f}/{V['spike']:+.0f}"
               + f" | fwd n trade {res['n_fwd_trade']:.0f} clust {res['n_fwd_clust']:.0f} -> {res['months_fwd']:.1f} months")
            cells.append(res)
    real = [c for c in cells if not c["cell"].startswith("E0s")]
    rmax = max(c["IS"]["t"] for c in real)
    nm_ = null_max[np.isfinite(null_max)]
    Pl(f"\nmax-over-6 IS t: real {rmax:+.2f} ({[c['cell'] for c in real if c['IS']['t'] == rmax][0]}); "
       f"null median {np.median(nm_):+.2f} p95 {np.percentile(nm_, 95):+.2f}")
    # sample representativeness: F's g (close e+1 entry) H60 on sample vs all, both eras
    for e_, en in ((0, "IS"), (1, "VAL")):
        a = idx[era[idx] == e_]; b = sj[era[sj] == e_]
        ga = z["g"][a, 2] - f[a, 2] - cost_decl[a]; gb = z["g"][b, 2] - f[b, 2] - cost_decl[b]
        ga, gb = ga[np.isfinite(ga)], gb[np.isfinite(gb)]
        Pl(f"representativeness {en}: F's e+1-close H60 net all {ga.mean() * BP:+.1f} (n {len(ga)}) vs sample "
           f"{gb.mean() * BP:+.1f} (n {len(gb)})")
    open(os.path.join(OUT, "report.txt"), "w").write("\n".join(lines) + "\n")
    json.dump(cells, open(os.path.join(OUT, "cells.json"), "w"), indent=1, default=float)
    np.savez(os.path.join(OUT, "sample_rows.npz"), j=sj, **{k: col(k) for k in S[sj[0]]})
    print("\n".join(lines))


if __name__ == "__main__":
    main()
