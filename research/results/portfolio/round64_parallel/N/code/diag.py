"""Diagnostics for config P (info): liquidation events, stale / data-end unwinds, uncovered B trades, big coins."""
import numpy as np
from inventory import load, simulate, settled_mask, sim_coin, DAY, H
BASE = dict(N=1.25, lo=1.0, hi=1.5, m=0.5, cost_mult=1.0, guard=True, hyst=48)
coins = load(); T = simulate(coins, 100, 24, -1)
p = dict(BASE)
ts = lambda c, j: str(np.datetime64(int(c["hours"][j]), "ms"))[:13]
liq, stale = [], {"dataend": 0, "cutend": 0, "gap": 0}
for ci, c in enumerate(coins):
    s = settled_mask(c)
    r = sim_coin(c, c["inU"].copy(), p, s)
    if r is None:
        continue
    for j in np.where(r["cost"]["liq"] > 0)[0]:
        if j > 0:
            liq.append((c["perp"], ts(c, j - 1), round(c["Fh"][j - 1] / c["Fo"][j - 1] - 1, 3), round(c["Fo"][j] / c["Fo"][j - 1] - 1, 3),
                        round(np.nanmax([c["So"][j] / c["So"][j - 1] - 1]), 3), round(r["cost"]["liq"][j] + r["price"][j], 3)))
    vb = np.where(~np.isnan(c["Fo"]) & ~np.isnan(c["So"]))[0]
    for j in np.where(r["kind"] == 2)[0]:
        if j >= vb[-1]:
            stale["cutend" if c["hours"][j] >= 1735689600000 - 3 * DAY else "dataend"] += 1
        else:
            stale["gap"] += 1
    w = np.where(T["ci"] == ci)[0]
    for k in w:
        if r["cover"][T["e"][k]] < 1:
            print("uncovered", c["perp"], ts(c, T["e"][k]), round(T["net"][k] * 1e4), "cover", r["cover"][T["e"][k]])
    if c["perp"] in ("UNFIUSDT", "LUNAUSDT", "ANCUSDT", "TRBUSDT"):
        cp = np.cumsum(r["price"]); 
        big = np.argsort(-np.abs(r["price"]))[:5]
        print(c["perp"], [(ts(c, j), round(r["price"][j], 3), c["Fo"][j - 1], c["Fo"][j], c["So"][j - 1], c["So"][j]) for j in big])
print("liq events", len(liq))
for x in liq:
    print(" ", x)
print("stale", stale)
