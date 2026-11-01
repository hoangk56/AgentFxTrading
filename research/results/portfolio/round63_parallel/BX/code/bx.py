"""Stream BX: B's frozen k100_H24_cheap signal hedged with the Bybit linear perp (rule in ../HYPOTHESES_BX.md).
Long Binance perp / short Bybit perp, entry / exit at B's hours. Everything cut at 2025-01-01 at load (B's CUT).
Usage: python bx.py [reps]  -> prints tables, writes ../out/bx_results.json and ../out/bx_trades_<cell>_lag<l>.npz"""
import csv, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "B", "code"))
from basis import load, simulate, hs_of, cl_t, ERAS, CUT, H  # noqa
from universe import DAY  # noqa

RES = os.path.join(HERE, "..", "..", "..", "..", "..")
YK = os.path.join(RES, "data", "bybit_1h", "kline")
YF1 = os.path.join(RES, "data", "bybit", "funding")
YF2 = os.path.join(RES, "data", "bybit_1h", "funding")
OUT = os.path.join(HERE, "..", "out")
FEE = 0.0021          # Binance perp 0.05 % x 2 + Bybit 0.055 % x 2
HS_Y = 0.0005         # Bybit half-spread per side
V50 = 0.0050


def _csv(path, cols):
    with open(path) as f:
        r = csv.reader(f); hdr = next(r)
        a = np.array([[float(x[i]) for i in cols] for x in r], dtype=float)
    return a[a[:, 0] < CUT] if len(a) else a


def attach_bybit(coins):
    for c in coins:
        p = c["perp"]; n, j0 = c["n"], c["j0"]
        c["Yo"] = np.full(n, np.nan); c["Yc"] = np.full(n, np.nan); c["Yv"] = np.zeros(n)
        c["ycum"] = np.zeros(n); c["ysym"] = None; c["yscale"] = np.nan
        kp = os.path.join(YK, p + ".csv")
        if not os.path.exists(kp):
            continue
        with open(kp) as f:
            r = csv.reader(f); next(r); rows = list(r)
        if not rows:
            continue
        c["ysym"] = rows[0][7]
        A = np.array([[float(x) for x in row[:6]] for row in rows])
        A = A[A[:, 0] < CUT]
        jj = (A[:, 0] // H).astype(int) - j0
        m = (jj >= 0) & (jj < n)
        c["Yo"][jj[m]] = A[m, 1]; c["Yc"][jj[m]] = A[m, 4]; c["Yv"][jj[m]] = A[m, 5]
        # scale (level check only): median of Bybit close / Binance perp close, rounded to a power of 10
        ok = ~np.isnan(c["Yc"]) & ~np.isnan(c["Fc"]) & (c["Fc"] > 0)
        if ok.sum():
            c["yscale"] = 10.0 ** np.rint(np.log10(np.median(c["Yc"][ok] / c["Fc"][ok])))
        fund = np.zeros(n)
        for fp in (os.path.join(YF1, p + ".csv"), os.path.join(YF1, c["ysym"] + ".csv"), os.path.join(YF2, p + ".csv")):
            if os.path.exists(fp):
                F = _csv(fp, (0, 1))
                if len(F):
                    k = np.rint(F[:, 0] / H).astype(int) - j0
                    mm = (k >= 0) & (k < n)
                    np.add.at(fund, k[mm], F[mm, 1])
                c["yfund_src"] = fp
                break
        c["ycum"] = np.cumsum(fund)


def ybar(c, j):
    return (j < c["n"]) and not np.isnan(c["Yo"][j])


def bx_trades(coins, T, cost_mult=1.0):
    """BX P&L on B's trades T. Returns dict of arrays over covered trades plus coverage counters."""
    out = {f: [] for f in ("ci", "h", "e", "x", "xy", "t", "pF", "pY", "fF", "fY", "cost", "carry", "net", "spr",
                           "Bnet", "Bprice", "pS", "adv")}
    nc = dict(total=len(T["e"]), not_listed=0, no_entry=0, no_exit=0)
    for i in range(len(T["e"])):
        ci, h, e, x = int(T["ci"][i]), int(T["h"][i]), int(T["e"][i]), int(T["x"][i])
        c = coins[ci]
        if c["ysym"] is None:
            nc["not_listed"] += 1; continue
        if not (ybar(c, e) and c["Yv"][e] > 0):
            nc["no_entry"] += 1; continue
        xy = x
        while xy < min(c["n"], x + 24) and not ybar(c, xy):
            xy += 1
        if not ybar(c, xy):
            nc["no_exit"] += 1; continue
        pF = c["Fo"][x] / c["Fo"][e] - 1
        pY = c["Yo"][xy] / c["Yo"][e] - 1
        pS = c["So"][x] / c["So"][e] - 1
        fF = -(c["fcum"][x] - c["fcum"][e])          # long Binance receives -rate
        fY = c["ycum"][xy] - c["ycum"][e]            # short Bybit receives +rate
        cost = cost_mult * (FEE + 2 * hs_of(c["rank"][h]) + 2 * HS_Y)
        carry = c["cash"][e] * (x - e) / 8760
        spr = np.log(c["Yc"][h] / c["yscale"] / c["Fc"][h]) if not np.isnan(c["Yc"][h]) else np.nan
        seg = slice(e, max(x, xy))
        adv = np.nanmax(c["Yo"][seg] if (xy - e) > 0 else [c["Yo"][e]]) / c["Yo"][e] - 1   # rough Bybit short adverse
        vals = dict(ci=ci, h=h, e=e, x=x, xy=xy, t=c["hours"][e], pF=pF, pY=pY, fF=fF, fY=fY, cost=cost, carry=carry,
                    net=pF - pY + fF + fY - cost - carry, spr=spr, Bnet=T["net"][i], Bprice=T["price"][i], pS=pS, adv=adv)
        for k, v in vals.items():
            out[k].append(v)
    R = {k: np.array(v) for k, v in out.items()}
    return R, nc


def sel(R, m):
    return {k: v[m] for k, v in R.items()}


def summ(R, era, key="net"):
    a, b = ERAS[era]
    m = (R["t"] >= a) & (R["t"] < b)
    x = R[key][m]; day = R["t"][m] // DAY
    if len(x) < 2:
        return dict(n=int(len(x)))
    u, inv = np.unique(day, return_inverse=True)
    dsum = np.bincount(inv, weights=x)
    return dict(n=int(len(x)), days=int(len(u)), coins=int(len(np.unique(R["ci"][m]))), net_bp=x.mean() * 1e4,
                med_bp=float(np.median(x) * 1e4), t=cl_t(x, day), sr=x.mean() / x.std(ddof=1),
                sr_day=dsum.mean() / dsum.std(ddof=1) if len(dsum) > 1 else np.nan,
                win=float((x > 0).mean()),
                price_bp=(R["pF"][m] - R["pY"][m]).mean() * 1e4, fundF_bp=R["fF"][m].mean() * 1e4,
                fundY_bp=R["fY"][m].mean() * 1e4, cost_bp=R["cost"][m].mean() * 1e4, carry_bp=R["carry"][m].mean() * 1e4,
                B_same_bp=R["Bnet"][m].mean() * 1e4, B_price_bp=R["Bprice"][m].mean() * 1e4,
                spotminusY_bp=(R["pS"][m] - R["pY"][m]).mean() * 1e4)


def by_year(R):
    y = np.asarray(R["t"], dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
    return {int(yy): (int((y == yy).sum()), float(R["net"][y == yy].mean() * 1e4),
                      float(cl_t(R["net"][y == yy], R["t"][y == yy] // DAY)) if (y == yy).sum() > 2 else None)
            for yy in np.unique(y)}


def random_null(coins, R, era, reps, rng, var_mask=None):
    """Matched random entries (same coin, era, hold length; coin in universe; Binance and Bybit bars present)."""
    a, b = ERAS[era]
    m = (R["t"] >= a) & (R["t"] < b)
    if var_mask is not None:
        m &= var_mask
    ci, L = R["ci"][m], (R["x"] - R["e"])[m]
    nets = np.full((reps, len(ci)), np.nan); days = np.zeros((reps, len(ci)), np.int64)
    for c_ in np.unique(ci):
        c = coins[c_]
        ok = c["inU"] & ~np.isnan(c["Fo"]) & ~np.isnan(c["Yo"]) & (c["Yv"] > 0) & (c["hours"] >= a) & (c["hours"] < b)
        pool = np.where(ok)[0]
        w = np.where(ci == c_)[0]
        if not len(pool):
            continue
        e = pool[rng.integers(0, len(pool), size=(reps, len(w)))]
        x = np.minimum(e + L[w][None, :], c["n"] - 1)
        pF = c["Fo"][x] / c["Fo"][e] - 1
        pY = c["Yo"][x] / c["Yo"][e] - 1
        f = -(c["fcum"][x] - c["fcum"][e]) + (c["ycum"][x] - c["ycum"][e])
        cost = FEE + 2 * hs_of(c["rank"][e]) + 2 * HS_Y
        v = pF - pY + f - cost - c["cash"][e] * (x - e) / 8760
        nets[:, w] = v
        days[:, w] = c["hours"][e] // DAY
    means, ts = np.full(reps, np.nan), np.full(reps, np.nan)
    for r in range(reps):
        ok = ~np.isnan(nets[r])
        if ok.sum() > 2:
            means[r] = nets[r, ok].mean(); ts[r] = cl_t(nets[r, ok], days[r, ok])
    return means, ts


def main(reps=1000):
    coins = load()
    attach_bybit(coins)
    names = np.array([c["perp"] for c in coins])
    res = {"cells": {}}
    Rs = {}
    for lag in (0, 1):
        T = simulate(coins, 100, 24, -1, lag=lag)
        keep = T["t"] < CUT
        T = {k: (v[keep] if hasattr(v, "__len__") and len(v) == len(keep) else v) for k, v in T.items()}
        R, nc = bx_trades(coins, T)
        R15, _ = bx_trades(coins, T, 1.5)
        for era in ("IS", "VAL"):
            a, b = ERAS[era]
            mT = (T["t"] >= a) & (T["t"] < b)
            Tn = {k: (v[mT] if hasattr(v, "__len__") and len(v) == len(mT) else v) for k, v in T.items()}
            _, nce = bx_trades(coins, Tn)
            res.setdefault("coverage", {})[f"lag{lag}_{era}"] = nce
        for cell, msk in (("P", np.ones(len(R["t"]), bool)), ("V50", R["spr"] >= V50)):
            Rc, R15c = sel(R, msk), sel(R15, msk)
            Rs[(cell, lag)] = Rc
            np.savez(os.path.join(OUT, f"bx_trades_{cell}_lag{lag}.npz"), sym=names[Rc["ci"]], **Rc)
            d = res["cells"].setdefault(cell, {})
            for era in ("IS", "VAL"):
                s = summ(Rc, era)
                s15 = summ(R15c, era)
                if lag == 0:
                    s["x1.5_bp"], s["x1.5_t"] = s15.get("net_bp"), s15.get("t")
                    d[era] = s
                else:
                    d[era]["late_n"], d[era]["late_bp"] = s.get("n"), s.get("net_bp")
                    d[era]["late_med"], d[era]["late_t"] = s.get("med_bp"), s.get("t")
            if lag == 0:
                d["years"] = by_year(Rc)
    rng = np.random.default_rng(6301)
    for era in ("IS", "VAL"):
        tm = []
        for cell in ("P", "V50"):
            R = Rs[(cell, 0)]
            if res["cells"][cell][era].get("n", 0) < 3:
                tm.append(np.full(reps, np.nan)); continue
            means, ts = random_null(coins, R, era, reps, rng)
            act = res["cells"][cell][era]["net_bp"] / 1e4
            res["cells"][cell][era]["beats_random"] = float(np.nanmean(means < act))
            res["cells"][cell][era]["random_mean_bp"] = float(np.nanmean(means) * 1e4)
            tm.append(ts)
        mx = np.nanmax(np.array(tm), axis=0)
        res.setdefault("maxnull", {})[era] = dict(p50=float(np.nanpercentile(mx, 50)), p95=float(np.nanpercentile(mx, 95)))
    # power at VAL size (VAL = 3 years; HOLD ~1.8 years)
    for cell in ("P", "V50"):
        v = res["cells"][cell]["VAL"]
        if v.get("n", 0) > 2:
            v["power_trade"] = v["sr"] * np.sqrt(1.8 * v["n"] / 3)
            v["power_day"] = v["sr_day"] * np.sqrt(1.8 * v["days"] / 3)
    # info: Bybit-Binance spread at the signal, scale / symbol map
    R = Rs[("P", 0)]
    for era in ("IS", "VAL"):
        a, b = ERAS[era]; m = (R["t"] >= a) & (R["t"] < b) & ~np.isnan(R["spr"])
        if m.sum():
            res.setdefault("spread_at_signal_bp_p10_50_90", {})[era] = list(np.percentile(R["spr"][m] * 1e4, [10, 50, 90]))
            res.setdefault("share_V50", {})[era] = float((R["spr"][m] >= V50).mean())
    res["symbols"] = {c["perp"]: [c["ysym"], c["yscale"], os.path.basename(os.path.dirname(c.get("yfund_src", "x/none")))]
                      for c in coins if c["ysym"]}
    tradedP = np.unique(names[Rs[("P", 0)]["ci"]])
    res["coins_with_bybit_funding_missing"] = [s for s in tradedP if "yfund_src" not in coins[list(names).index(s)]]
    with open(os.path.join(OUT, "bx_results.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res["coverage"], indent=0))
    for cell in ("P", "V50"):
        for era in ("IS", "VAL"):
            s = res["cells"][cell][era]
            print(cell, era, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()})
        print(cell, "years", res["cells"][cell]["years"])
    print("maxnull", res["maxnull"])
    print("spread", res.get("spread_at_signal_bp_p10_50_90"), res.get("share_V50"))
    print("missing funding", res["coins_with_bybit_funding_missing"])


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
