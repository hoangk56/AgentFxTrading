"""Info: config P inventory P&L inside B windows (steps e+1..x of each covered B trade) vs outside, per era (Q/yr)."""
import numpy as np
from inventory import load, simulate, settled_mask, sim_coin, ERAS
P = dict(N=1.25, lo=1.0, hi=1.5, m=0.5, cost_mult=1.0, guard=True, hyst=48)
YRS = {"IS": 731 / 365.25, "VAL": 1096 / 365.25}
coins = load(); T = simulate(coins, 100, 24, -1)
acc = {e: dict(in_pf=0.0, in_cost=0.0, out_pf=0.0, out_cost=0.0, b_pf=0.0, b_cost=0.0) for e in ERAS}
for ci, c in enumerate(coins):
    r = sim_coin(c, c["inU"].copy(), P, settled_mask(c))
    if r is None:
        continue
    pf = r["price"] + r["fund"]; co = sum(r["cost"].values())
    inw = np.zeros(c["n"], bool)
    for k in np.where(T["ci"] == ci)[0]:
        if r["cover"][T["e"][k]] > 0:
            inw[T["e"][k] + 1:T["x"][k] + 1] = True
            for e, (a, b) in ERAS.items():
                if a <= T["t"][k] < b:
                    acc[e]["b_pf"] += T["price"][k] + T["fund"][k]; acc[e]["b_cost"] += T["cost"][k]
    for e, (a, b) in ERAS.items():
        w = (c["hours"] >= a) & (c["hours"] < b)
        acc[e]["in_pf"] += pf[w & inw].sum(); acc[e]["in_cost"] += co[w & inw].sum()
        acc[e]["out_pf"] += pf[w & ~inw].sum(); acc[e]["out_cost"] += co[w & ~inw].sum()
for e, d in acc.items():
    print(e, {k: round(v / YRS[e], 2) for k, v in d.items()})
