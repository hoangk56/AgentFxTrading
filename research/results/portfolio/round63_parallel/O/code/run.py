"""Round 63 stream O: run the 20 declared cells + checks + random benchmark + max-over-cells null.
Usage: python -I run.py [n_rep]. Writes ../out/cells.json, ../out/report.txt."""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E  # noqa: E402
from engine import xs  # noqa: E402

NREP = int(sys.argv[1]) if len(sys.argv) > 1 else 500
rng = np.random.default_rng(63015)


def h1_signals(D, q, p, need_oi=True):
    t = np.arange(2, xs.NH + 1)
    k = t % 24
    t = t[(k >= 2) & (k <= 23) & (t * xs.HOUR + xs.H0 >= E.DISC[0])]
    d = t // 24
    I, T = [], []
    for i in range(D.n):
        a = D.A[i, d]
        if not a.any():
            continue
        tt = t[a]
        with np.errstate(invalid="ignore", divide="ignore"):
            r = D.P[i, tt] / D.P[i, tt - 1] - 1
            doi = D.OIh[i, tt] / D.OIh[i, tt - 1] - 1
        m = r <= -p
        if need_oi:
            m &= doi <= -q
        else:
            m &= np.isfinite(doi)   # same covered hours as the OI rule
        I.append(np.full(m.sum(), i))
        T.append(tt[m])
    return np.concatenate(I), np.concatenate(T)


def h1_pool(D):
    """Eligible hours for H1 random entries: universe coin-day, metrics file pulled (Tier A or B), k 2..23."""
    I, T = [], []
    for i in range(D.n):
        days = np.where(D.cov[i] & D.A[i])[0]
        if len(days) == 0:
            continue
        tt = (24 * days[:, None] + np.arange(2, 24)[None, :]).ravel()
        I.append(np.full(len(tt), i))
        T.append(tt)
    return np.concatenate(I), np.concatenate(T)


def h1_pool_all(D):
    """Information: every universe hour k 2..23 from 2022-01-01 (no metrics coverage condition)."""
    I, T = [], []
    for i in range(D.n):
        days = np.where(D.A[i])[0]
        days = days[(days >= E.univ.D0) & (days < E.univ.D1)]
        if len(days) == 0:
            continue
        tt = (24 * days[:, None] + np.arange(2, 24)[None, :]).ravel()
        I.append(np.full(len(tt), i))
        T.append(tt)
    return np.concatenate(I), np.concatenate(T)


def trades(D, i, t, side, H, lag=0, cm=1.0, overlap=True):
    if overlap:
        keep = E.no_overlap(i, t, H)
        i, t, side = i[keep], t[keep], side[keep]
    g, c, ok = D.legs(i, t, H, lag, cm)
    return dict(i=i[ok], t=t[ok], side=side[ok], r=side[ok] * g[ok] - c[ok], g=side[ok] * g[ok], c=c[ok],
                dropped=int((~ok).sum()))


def summ(tr, mask=None):
    r, t = tr["r"], tr["t"]
    if mask is not None:
        r, t = r[mask], t[mask]
    if len(r) == 0:
        return dict(n=0)
    day = t // 24
    return dict(n=len(r), net=r.mean() * 1e4, t=E.tclust(r, day), sd=r.std(ddof=1) * 1e4 if len(r) > 1 else np.nan,
                days=int(len(np.unique(day))))


def by_era(tr):
    out = {}
    era = E.era_of(tr["t"])
    for e in ("DISC", "VAL"):
        m = era == e
        s = summ(tr, m)
        if s["n"]:
            s["gross"] = tr["g"][m].mean() * 1e4 + 0.0
            s["cost"] = tr["c"][m].mean() * 1e4
        out[e] = s
    yr = E.year_of(tr["t"])
    out["years"] = {int(y): (float(tr["r"][yr == y].mean() * 1e4), int((yr == y).sum())) for y in (2022, 2023, 2024)
                    if (yr == y).any()}
    return out


class Pool:
    """Precomputed per-coin random-entry pools: g (side-signed part for side +1), c, flag (+1 high / -1 low), day."""

    def __init__(self, D, I, T, H, flag=None):
        g, c, ok = D.legs(I, T, H)
        self.I, self.T, self.g, self.c = I[ok], T[ok], g[ok], c[ok]
        self.flag = flag[ok] if flag is not None else np.ones(ok.sum())
        self.era = E.era_of(self.T)
        self.idx = {}
        for e in ("DISC", "VAL"):
            for i in np.unique(self.I):
                w = np.where((self.I == i) & (self.era == e))[0]
                if len(w):
                    self.idx[(e, i)] = w

    def draw(self, tr, era, sidefun, rng):
        """Random entries: same trade count per coin as tr in this era. Returns (r, day)."""
        m = E.era_of(tr["t"]) == era
        ii, cnt = np.unique(tr["i"][m], return_counts=True)
        sel = []
        for i, n in zip(ii, cnt):
            w = self.idx.get((era, i))
            if w is None:
                continue
            sel.append(w[rng.integers(0, len(w), n)])
        if not sel:
            return np.zeros(0), np.zeros(0)
        s = np.concatenate(sel)
        side = sidefun(self.flag[s])
        return side * self.g[s] - self.c[s], self.T[s] // 24


def main():
    t0 = time.time()
    D = E.Data()
    print("data", round(time.time() - t0), "s", flush=True)
    cells = {}
    pools = {}
    # ---- percentiles for H2 (top position ratio) and H3 (taker) --------------------------------------------------
    i2, t2, q2 = E.percentiles(D, D.TPh, range(2, 25))   # k 24 = 00:00 of day d+1 (the H2 decision instant)
    i3, t3, q3 = E.percentiles(D, D.TKh, range(2, 24))
    uni2 = D.A[i2, t2 // 24]
    uni3 = D.A[i3, t3 // 24]
    i2, t2, q2 = i2[uni2], t2[uni2], q2[uni2]
    i3, t3, q3 = i3[uni3], t3[uni3], q3[uni3]
    print("pct", len(i2), len(i3), round(time.time() - t0), "s", flush=True)
    dec2 = (t2 % 24) == 0
    rnd2 = ~dec2          # random hours for H2: k 2..23
    I1, T1 = h1_pool(D)
    for H in (4, 24, 72):
        if H in (4, 24):
            pools[("H1", H)] = Pool(D, I1, T1, H)
            pools[("H3", H)] = Pool(D, i3, t3, H, np.where(q3 > 0.5, 1.0, -1.0))
        if H in (24, 72):
            pools[("H2", H)] = Pool(D, i2[rnd2], t2[rnd2], H, np.where(q2[rnd2] > 0.5, 1.0, -1.0))
    print("pools", round(time.time() - t0), "s", flush=True)
    specs = []
    for q in (0.02, 0.04):
        for p in (0.03, 0.05):
            I, T = h1_signals(D, q, p)
            for H in (4, 24):
                specs.append((f"H1 q{int(q*100)} p{int(p*100)} H{H}", "H1", H, I, T, np.ones(len(I)),
                              lambda f: np.ones(len(f))))
    for a in (0.10, 0.025):
        m = dec2 & ((q2 >= 1 - a) | (q2 <= a))
        side = np.where(q2[m] >= 1 - a, -1.0, 1.0)
        for H in (24, 72):
            specs.append((f"H2 a{a*100:g} H{H}", "H2", H, i2[m], t2[m], side, lambda f: -f))
    for b in (0.02, 0.005):
        m = (q3 >= 1 - b) | (q3 <= b)
        hi = np.where(q3[m] >= 1 - b, 1.0, -1.0)
        for H in (4, 24):
            specs.append((f"H3C b{b*100:g} H{H}", "H3", H, i3[m], t3[m], hi, lambda f: f))
            specs.append((f"H3R b{b*100:g} H{H}", "H3", H, i3[m], t3[m], -hi, lambda f: -f))
    null_t = {}
    for name, fam, H, I, T, side, sidefun in specs:
        tr = trades(D, I, T, side, H)
        res = by_era(tr)
        res["dropped"] = tr["dropped"]
        res["x1.5"] = by_era(trades(D, I, T, side, H, cm=1.5))
        res["late"] = by_era(trades(D, I, T, side, H, lag=1))
        pool = pools[(fam, H)]
        for e in ("DISC", "VAL"):
            if res[e]["n"] < 3:
                continue
            mu, tt = np.empty(NREP), np.empty(NREP)
            for k in range(NREP):
                r, dd = pool.draw(tr, e, sidefun, rng)
                mu[k] = r.mean()
                tt[k] = E.tclust(r, dd)
            res[e]["rand_pct"] = float(np.mean(mu < res[e]["net"] / 1e4) * 100)
            res[e]["rand_med_bp"] = float(np.median(mu) * 1e4)
            if e == "DISC":
                null_t[name] = tt
        # power at VAL size: per-trade Sharpe x sqrt(expected HOLD trades), and the clustered version
        v = res["VAL"]
        if v["n"] >= 3:
            fac = HOLD_FAC[fam]
            v["n_hold_est"] = v["n"] * fac
            v["power_trade"] = v["net"] / v["sd"] * np.sqrt(v["n"] * fac)
            v["power_clust"] = v["t"] * np.sqrt(fac)
        cells[name] = res
        print(name, json.dumps({e: {k: (round(x, 2) if isinstance(x, float) else x) for k, x in res[e].items()}
                                for e in ("DISC", "VAL")}), round(time.time() - t0), "s", flush=True)
    # ---- max-over-cells null on DISCOVERY net t ---------------------------------------------------------------------
    names = [s[0] for s in specs if s[0] in null_t]
    M = np.vstack([null_t[n] for n in names])
    mx = np.nanmax(M, axis=0)
    real = max(cells[n]["DISC"]["t"] for n in names if np.isfinite(cells[n]["DISC"]["t"]))
    nullres = dict(real_max_disc_t=float(real), null_median=float(np.median(mx)), null_p95=float(np.percentile(mx, 95)),
                   real_pctile=float(np.mean(mx < real) * 100), n_cells=len(names))
    # ---- information: H1 price-only control, H1 random over all universe hours ------------------------------------
    info = {}
    Ia, Ta = h1_pool_all(D)
    for p in (0.03, 0.05):
        I, T = h1_signals(D, 0, p, need_oi=False)
        for H in (4, 24):
            info[f"H1 price-only p{int(p*100)} H{H}"] = by_era(trades(D, I, T, np.ones(len(I)), H))
    for H in (4, 24):
        tr = trades(D, Ia, Ta, np.ones(len(Ia)), H, overlap=False)
        info[f"long-hedged every universe hour H{H}"] = by_era(tr)
    os.makedirs(E.OUT, exist_ok=True)

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, np.integer):
            return int(o)
        return o
    json.dump(clean(dict(cells=cells, null=nullres, info=info, nrep=NREP)), open(os.path.join(E.OUT, "cells.json"), "w"),
              indent=1)
    np.savez(os.path.join(E.OUT, "null_disc_t.npz"), M=M, names=np.array(names))
    print("null", nullres, flush=True)
    print("done", round(time.time() - t0), "s", flush=True)


# expected HOLD trades per VAL trade: HOLD 22 months vs VAL 18; Tier A covers half the days for H2 / H3
HOLD_FAC = {"H1": E.HOLD_MONTHS / E.VAL_MONTHS, "H2": 2 * E.HOLD_MONTHS / E.VAL_MONTHS,
            "H3": 2 * E.HOLD_MONTHS / E.VAL_MONTHS}

if __name__ == "__main__":
    import warnings
    warnings.simplefilter("ignore")
    main()
