"""Information checks (rule unchanged): open == previous close share on Bybit 1h bars, one-hour-late by year,
trades exiting after 1 h vs longer, spot vs perp leg of the convergence."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import by
B = by.B
from basis import simulate, cl_t, DAY
coins = by.load()
eq = {"F": [0, 0], "S": [0, 0]}
for c in coins:
    for leg, o, cl in (("F", c["Fo"], c["Fc"]), ("S", c["So"], c["Sc"])):
        ok = c["inU"][1:] & ~np.isnan(o[1:]) & ~np.isnan(cl[:-1])
        eq[leg][0] += (np.isclose(o[1:], cl[:-1], rtol=1e-9, atol=0) & ok).sum(); eq[leg][1] += ok.sum()
print("open == previous close share: perp %.3f spot %.3f" % (eq["F"][0] / eq["F"][1], eq["S"][0] / eq["S"][1]))
for lag in (0, 1):
    T = simulate(coins, 100, 24, -1, lag=lag)
    y = np.asarray(T["t"], dtype="datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
    for yy in np.unique(y):
        w = y == yy
        print(f"lag{lag} {yy} n {w.sum()} net {T['net'][w].mean()*1e4:.1f} median {np.median(T['net'][w])*1e4:.1f} t {cl_t(T['net'][w], T['t'][w]//DAY):.2f}")
    if lag == 0:
        L = T["x"] - T["e"]
        for lab, w in (("exit after 1 h", L == 1), ("hold > 1 h", L > 1)):
            for era in ("IS", "VAL"):
                m = w & B.era_mask(T, era)
                print(lab, era, m.sum(), round(T["net"][m].mean() * 1e4, 1), round(cl_t(T["net"][m], T["t"][m] // DAY), 2))
        # leg split: spot return (short) and perp return (long) over the hold
        sp, pp = [], []
        for i in range(len(T["e"])):
            c = coins[T["ci"][i]]; e, x = T["e"][i], T["x"][i]
            sp.append(-(c["So"][x] / c["So"][e] - 1)); pp.append(c["Fo"][x] / c["Fo"][e] - 1)
        sp, pp = np.array(sp), np.array(pp)
        for era in ("IS", "VAL"):
            m = B.era_mask(T, era)
            print("legs", era, "short-spot leg %.1f bp, long-perp leg %.1f bp" % (sp[m].mean() * 1e4, pp[m].mean() * 1e4))
