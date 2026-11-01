import sys, numpy as np
from basis import load, simulate, ERAS
coins = load()
k, Hh, side, lag = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
T = simulate(coins, k, Hh, side, lag=lag)
for era in ("IS", "VAL"):
    a, b = ERAS[era]; m = (T["t"] >= a) & (T["t"] < b)
    x = T["net"][m]
    o = np.argsort(-np.abs(x))
    print(era, "n", m.sum(), "mean", x.mean()*1e4, "median", np.median(x)*1e4, "win", (x > 0).mean(),
          "top10 sum share", x[o[:10]].sum() / x.sum(), "trim 1% mean", np.sort(x)[int(.01*len(x)):int(.99*len(x))].mean()*1e4)
    idx = np.where(m)[0][o[:12]]
    for i in idx:
        c = coins[T["ci"][i]]; e, xx, h = T["e"][i], T["x"][i], T["h"][i]
        print(f"  {c['perp']:14s} {np.datetime64(int(T['t'][i]),'ms')} net {T['net'][i]*1e4:8.0f} price {T['price'][i]*1e4:8.0f} fund {T['fund'][i]*1e4:6.0f} hold {xx-e:3d} d {1e4*(c['b'][h]-c['m'][h]):6.0f} Fo {c['Fo'][e]:.5g}->{c['Fo'][xx]:.5g} So {c['So'][e]:.5g}->{c['So'][xx]:.5g} Sn {c['Sn'][h]:.0f} Fn {c['Fn'][h]:.0f} adv {T['adv'][i]:.2f}")
    # coin concentration
    u, inv = np.unique(T["ci"][m], return_inverse=True)
    s = np.bincount(inv, weights=x)
    oo = np.argsort(-s)[:6]
    print("  top coins:", [(coins[u[j]]["perp"], int((inv == j).sum()), round(s[j] * 1e4 / m.sum(), 1)) for j in oo])
