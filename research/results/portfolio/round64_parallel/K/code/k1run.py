"""K1 run: trades for the 16 declared cells, 1m fills (fapi alt, vision BTC), funding, costs, stats, random benchmark.
Usage: python -I k1run.py count | fetch | run"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kdata import GRID, B4, H, M, DAY, G0, ERAS, panel, funding, btc_1m, cl_t, year_of
import k1, fills

COST = 0.0032          # 4 taker fills x 5 bp + 2 x 5 bp alt half-spread + 2 x 1 bp BTC half-spread
LATE = 5 * M


def all_trades(coins):
    return {k1.cell_name(*c): (c, k1.gen_trades(coins, *c)) for c in k1.CELLS}


def needs(coins, TR):
    need = {}
    for cell, (_, T) in TR.items():
        for t in T:
            s = coins[t["ci"]]["sym"]
            for x in (t["Te"], t["Tx"]):
                need.setdefault(s, set()).update({x, x + LATE})
    return need


def fsum(F, a, b):
    if not len(F):
        return 0.0
    w = (F[:, 0] > a + 30000) & (F[:, 0] <= b + 30000)
    return float(F[w, 1].sum())


def price_trades(coins, base, T, side, mode, btc, caches, FU, cost_mult=1.0):
    rows = []
    for t in T:
        c = coins[t["ci"]]
        sym = c["sym"]
        if mode == "h1":
            ae, ax = c["hc1"][t["i"]], c["hc1"][t["j"]]
            be, bx = base["BB1"][t["i"]], base["BB1"][t["j"]]
            fe, fx = t["Te"] + H, t["Tx"] + H
        else:
            lag = 0 if mode == "m1" else LATE
            sc = 1000.0 if sym.startswith("1000") else 1.0
            ae = fills.price_at(caches[sym], t["Te"] + lag) / sc
            ax = fills.price_at(caches[sym], t["Tx"] + lag) / sc
            be = btc_px(btc, t["Te"] + lag); bx = btc_px(btc, t["Tx"] + lag)
            fe, fx = t["Te"] + lag + M, t["Tx"] + lag + M
        if not all(np.isfinite([ae, ax, be, bx])):
            continue
        price = side * ((ax / ae - 1) - (bx / be - 1))
        fund = side * (fsum(FU["BTCUSDT"], fe, fx) - fsum(FU[sym], fe, fx))
        cost = COST * cost_mult
        du = c["uleg"][t["j"]] - c["uleg"][t["i"]]
        db = c["bleg"][t["j"]] - c["bleg"][t["i"]]
        rows.append((t["Te"], t["ci"], price, fund, cost, price + fund - cost, t["Tx"] - t["Te"], t["forced"], du, db, t["s"]))
    a = np.array(rows, dtype=float) if rows else np.zeros((0, 11))
    return a


def btc_px(btc, t):
    i = (t - G0) // M
    for d in range(5):
        if 0 <= i + d < len(btc) and np.isfinite(btc[i + d]):
            return btc[i + d]
    return np.nan


def stats(a, era):
    lo, hi = ERAS[era]
    w = (a[:, 0] >= lo) & (a[:, 0] < hi)
    x = a[w]
    if len(x) < 3:
        return dict(n=len(x))
    day = (x[:, 0] // DAY).astype(np.int64)
    net = x[:, 5]
    yrs = year_of(x[:, 0])
    by = {int(y): (int((yrs == y).sum()), float(net[yrs == y].mean() * 1e4)) for y in np.unique(yrs)}
    return dict(n=len(x), days=len(np.unique(day)), gross=x[:, 2].mean() * 1e4, fund=x[:, 3].mean() * 1e4,
                cost=x[:, 4].mean() * 1e4, net=net.mean() * 1e4, t=cl_t(net, day), sr=net.mean() / net.std(ddof=1),
                hold_h=x[:, 6].mean() / H, forced=float(x[:, 7].mean()), du=np.nanmean(x[:, 8]) * 1e4,
                db=np.nanmean(x[:, 9]) * 1e4, s=x[:, 10].mean() * 1e4, years=by)


def random_bench(coins, base, a, side, draws=500, seed=7):
    """Gross h1-fill price P&L of actual trades vs same coin, same quarter, same holding, random entry bucket."""
    rng = np.random.default_rng(seed)
    q = ((GRID - G0) // (91 * DAY)).astype(np.int64)
    act = a[:, 2]
    ci = a[:, 1].astype(int)
    ib = ((a[:, 0] - B4 - G0) // B4).astype(int)
    nb = (a[:, 6] // B4).astype(int)
    pools = {}
    res = np.zeros(draws)
    out = np.full((draws, len(a)), np.nan)
    for k in range(len(a)):
        c = coins[ci[k]]
        key = (ci[k], q[ib[k]], nb[k])
        if key not in pools:
            idx = np.where(q == q[ib[k]])[0]
            idx = idx[idx + nb[k] < len(GRID)]
            ok = np.isfinite(c["hc1"][idx]) & np.isfinite(c["hc1"][idx + nb[k]]) & np.isfinite(base["BB1"][idx]) & np.isfinite(base["BB1"][idx + nb[k]])
            pools[key] = idx[ok]
        P = pools[key]
        if not len(P):
            continue
        s = rng.choice(P, draws)
        e = s + nb[k]
        out[:, k] = side * ((c["hc1"][e] / c["hc1"][s] - 1) - (base["BB1"][e] / base["BB1"][s] - 1))
    res = np.nanmean(out, axis=1)
    return res


if __name__ == "__main__":
    mode = sys.argv[1]
    coins, base = panel()
    allc = len(coins)
    coins = k1.prep(coins)
    TR = all_trades(coins)
    if mode == "count":
        print(allc, "coins with data,", len(coins), "kept after collision guard")
        for name, (_, T) in TR.items():
            print(name, len(T))
        need = needs(coins, TR)
        print("syms", len(need), "timestamps", sum(len(v) for v in need.values()))
        sys.exit()
    if mode == "fetch":
        fills.fetch(needs(coins, TR))
        sys.exit()
    btc = btc_1m()
    FU = {c["sym"]: funding(c["sym"]) for c in coins}
    FU["BTCUSDT"] = funding("BTCUSDT")
    caches = {c["sym"]: fills.load(c["sym"]) for c in coins}
    import json
    res = {}
    for name, (cell, T) in TR.items():
        side = cell[1]
        A = {m: price_trades(coins, base, T, side, m, btc, caches, FU) for m in ("m1", "m5", "h1")}
        A15 = price_trades(coins, base, T, side, "m1", btc, caches, FU, 1.5)
        res[name] = {}
        for era in ("IS", "VAL"):
            d = stats(A["m1"], era)
            d["net_x15"] = stats(A15, era).get("net")
            d["net_m5"] = stats(A["m5"], era).get("net"); d["t_m5"] = stats(A["m5"], era).get("t")
            d["net_h1"] = stats(A["h1"], era).get("net"); d["gross_h1"] = stats(A["h1"], era).get("gross")
            lo, hi = ERAS[era]
            a = A["h1"][(A["h1"][:, 0] >= lo) & (A["h1"][:, 0] < hi)]
            if len(a) >= 5:
                rb = random_bench(coins, base, a, side)
                d["rand_pct"] = float((rb < a[:, 2].mean()).mean() * 100)
                d["rand_med"] = float(np.median(rb) * 1e4)
            res[name][era] = d
        np.save(os.path.join(os.path.dirname(__file__), "..", f"trades_{name}.npy"), A["m1"])
        print(name, {e: {k: (round(v, 2) if isinstance(v, float) else v) for k, v in res[name][e].items()} for e in res[name]}, flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(__file__), "..", "k1_results.json"), "w"), indent=1, default=float)
