"""Stream B grid run: 12 declared cells, IS / VAL summaries, costs x1.5, one step late, maker info, random benchmark and
max-over-cells null. Writes ../out/cells.json and ../out/trades_<cell>.npz."""
import json, os, sys, time
import numpy as np
from basis import load, simulate, summarize, by_year, cl_t, trade_net, ERAS, DAY

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
os.makedirs(OUT, exist_ok=True)
CELLS = [(k, Hh, s) for s in (1, -1) for k in (30, 60, 100) for Hh in (4, 24)]
CRASH = [("2020-03-01", "2020-04-01"), ("2021-05-17", "2021-05-25"), ("2022-05-07", "2022-05-21"),
         ("2022-11-06", "2022-11-21")]


def name(c):
    return f"k{c[0]}_H{c[1]}_{'rich' if c[2] > 0 else 'cheap'}"


def crash_mask(t):
    m = np.zeros(len(t), bool)
    for a, b in CRASH:
        a = np.datetime64(a, "ms").astype(np.int64); b = np.datetime64(b, "ms").astype(np.int64)
        m |= (t >= a) & (t < b)
    return m


def sub(T, m):
    return {k: (v[m] if hasattr(v, "__len__") and len(v) == len(m) else v) for k, v in T.items()}


def random_null(coins, T, side, era, reps, rng):
    """Matched random entries: same coin, same era, same hold length, same side. Returns (means, ts) arrays."""
    a, b = ERAS[era]
    m = (T["t"] >= a) & (T["t"] < b)
    ci, L = T["ci"][m], (T["x"] - T["e"])[m]
    means, ts = np.full(reps, np.nan), np.full(reps, np.nan)
    if not m.sum():
        return means, ts
    pools = {}
    for c_ in np.unique(ci):
        c = coins[c_]
        ok = c["inU"] & ~np.isnan(c["Fo"]) & ~np.isnan(c["So"]) & (c["hours"] >= a) & (c["hours"] < b)
        pools[c_] = np.where(ok)[0]
    nets = np.full((reps, len(ci)), np.nan)
    days = np.zeros((reps, len(ci)), np.int64)
    for c_ in np.unique(ci):
        w = np.where(ci == c_)[0]
        pool = pools[c_]
        c = coins[c_]
        if not len(pool):
            continue
        e = pool[rng.integers(0, len(pool), size=(reps, len(w)))]
        x = np.minimum(e + L[w][None, :], c["n"] - 1)
        p, f, co, ca = trade_net(c, e.ravel(), x.ravel(), side, c["rank"][e.ravel()])
        v = (p + f - co - ca).reshape(e.shape)
        nets[:, w] = v
        days[:, w] = c["hours"][e] // DAY
    for r in range(reps):
        ok = ~np.isnan(nets[r])
        means[r] = nets[r, ok].mean()
        ts[r] = cl_t(nets[r, ok], days[r, ok])
    return means, ts


def main(reps=1000):
    t0 = time.time()
    coins = load()
    print("coins", len(coins), "load s", round(time.time() - t0), flush=True)
    res, trades = {}, {}
    for c in CELLS:
        T = simulate(coins, *c)
        TL = simulate(coins, *c, lag=1)
        TM = simulate(coins, *c, maker=True)
        r = {}
        for era in ("IS", "VAL"):
            s = summarize(T, era)
            T15 = dict(T); T15["net"] = T["net"] - 0.5 * T["cost"]
            s["net_x1.5_bp"] = summarize(T15, era).get("net_bp")
            s["t_x1.5"] = summarize(T15, era).get("t")
            sl = summarize(TL, era)
            s["late_net_bp"], s["late_t"] = sl.get("net_bp"), sl.get("t")
            s["maker_net_bp"] = summarize(TM, era).get("net_bp")
            nc = ~crash_mask(T["t"])
            s["nocrash"] = {k: summarize(sub(T, nc), era).get(k) for k in ("n", "net_bp", "t")}
            r[era] = s
        r["years"] = by_year(T)
        res[name(c)] = r
        trades[name(c)] = T
        np.savez(os.path.join(OUT, f"trades_{name(c)}.npz"), **{k: v for k, v in T.items()})
        print(name(c), {e: (r[e].get("n"), round(r[e].get("net_bp", np.nan), 1), round(r[e].get("t", np.nan), 2))
                        for e in ("IS", "VAL")}, flush=True)
    # random benchmark per cell and era, and max-over-cells null (IS and VAL)
    rng = np.random.default_rng(63)
    nulls = {}
    for era in ("IS", "VAL"):
        tmat = []
        for c in CELLS:
            T = trades[name(c)]
            means, ts = random_null(coins, T, c[2], era, reps, rng)
            act = res[name(c)][era].get("net_bp", np.nan) / 1e4
            res[name(c)][era]["beats_random"] = float(np.nanmean(means < act)) if res[name(c)][era].get("n") else None
            res[name(c)][era]["random_mean_bp"] = float(np.nanmean(means) * 1e4)
            tmat.append(ts)
        tmat = np.array(tmat)
        mx = np.nanmax(tmat, axis=0)
        nulls[era] = dict(max_t_p50=float(np.nanpercentile(mx, 50)), max_t_p95=float(np.nanpercentile(mx, 95)))
        print(era, nulls[era], flush=True)
    with open(os.path.join(OUT, "cells.json"), "w") as f:
        json.dump(dict(cells=res, nulls=nulls, reps=reps, ncoins=len(coins)), f, indent=1, default=float)
    print("done s", round(time.time() - t0))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
