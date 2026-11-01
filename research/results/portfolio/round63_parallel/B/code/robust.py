"""Information-only robustness for the IS-chosen cell k100_H24_cheap (declared rule unchanged)."""
import numpy as np
from basis import load, simulate, ERAS, cl_t, DAY
from run import crash_mask
coins = load()
names = np.array([c["perp"] for c in coins])
def rep(T, m, label):
    for era in ("IS", "VAL"):
        a, b = ERAS[era]; w = m & (T["t"] >= a) & (T["t"] < b)
        x = T["net"][w]
        print(f"{label:38s} {era} n {w.sum():4d} net {x.mean()*1e4:7.1f} med {np.median(x)*1e4:6.1f} t {cl_t(x, T['t'][w]//DAY):5.2f}")
for lag in (0, 1):
    T = simulate(coins, 100, 24, -1, lag=lag)
    allm = np.ones(len(T["t"]), bool)
    nc = ~crash_mask(T["t"])
    sym = names[T["ci"]]
    big = np.isin(sym, ["TRBUSDT", "LUNAUSDT", "FTTUSDT", "ANCUSDT", "SRMUSDT"])
    frozen = np.array([coins[c]["Fo"][x] == coins[c]["Fo"][x - 1] and coins[c]["Fh"][x - 1] == coins[c]["Fl"][x - 1]
                       for c, x in zip(T["ci"], T["x"])])
    hs = T["x"] - T["e"]
    tag = f"lag{lag}"
    rep(T, allm, tag + " declared")
    rep(T, nc, tag + " ex-crash windows")
    rep(T, nc & ~big & ~frozen & (T["forced"] == 0), tag + " ex-crash, ex TRB/LUNA/FTT/ANC/SRM")
    rep(T, hs == 1, tag + " exits after 1 h")
    rep(T, hs > 1, tag + " holds > 1 h")
    rep(T, T["fund"] == 0, tag + " no stamp crossed")
    if lag == 0:
        for era in ("IS", "VAL"):
            a, b = ERAS[era]; w = (T["t"] >= a) & (T["t"] < b)
            d = np.array([coins[c]["b"][h] - coins[c]["m"][h] for c, h in zip(T["ci"], T["h"])])[w]
            print(era, "deviation at signal bp pct 10/50/90:", np.percentile(d * 1e4, [10, 50, 90]).round(0),
                  "coins", len(np.unique(T["ci"][w])), "fund bp mean", T["fund"][w].mean()*1e4,
                  "adv>25%", (T["adv"][w] > .25).sum(), "adv>50%", (T["adv"][w] > .5).sum(), "forced", T["forced"][w].sum())
            u, inv = np.unique(sym[w], return_inverse=True)
            s = np.bincount(inv, weights=T["net"][w]); o = np.argsort(-s)
            print("  share of era P&L from top 5 coins:", round(s[o[:5]].sum() / s.sum(), 2), list(u[o[:5]]))
            # days concentration
            dd = T["t"][w] // DAY; ud, iv = np.unique(dd, return_inverse=True); sd = np.bincount(iv, weights=T["net"][w])
            print("  share from top 5 days:", round(np.sort(sd)[::-1][:5].sum() / sd.sum(), 2), "days", len(ud))
