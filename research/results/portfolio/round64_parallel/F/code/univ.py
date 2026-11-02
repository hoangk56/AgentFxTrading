"""Stream F: point-in-time top-40 USDT-M perp universe (round 63 C xs.daily_universe on round 63 C's panel cache).

Writes research/data/binance_1m_wicks/univ.npz: U [n, nd] bool, rank [n, nd], syms, day0 ms; and pull_list.csv of
(sym, YYYY-MM) months where the symbol is in the top 40 on any day (plus BTCUSDT every month).
No prices are used (only daily quote volume and listing age).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(R, "results/portfolio/round63_parallel/C/code"))
import xs  # noqa
OUT = os.path.join(R, "data", "binance_1m_wicks")
DAY = 86400000

if __name__ == "__main__":
    P = xs.load()
    U, rk = xs.daily_universe(P, N=40, min_age=60)
    syms = P["syms"]
    nd = U.shape[1]
    days = xs.H0 + DAY * np.arange(nd)
    import datetime as dt
    ym = np.array([dt.datetime.utcfromtimestamp(d / 1000).strftime("%Y-%m") for d in days])
    sel = days >= xs.IS[0]
    pairs = set()
    for i, s in enumerate(syms):
        for m in np.unique(ym[sel & U[i]]):
            pairs.add((s, m))
    for m in np.unique(ym[sel]):
        pairs.add(("BTCUSDT", m))
    pairs = sorted(pairs, key=lambda p: (p[1], p[0]))
    np.savez(os.path.join(OUT, "univ.npz"), U=U, rank=rk, syms=np.array(syms), day0=xs.H0)
    with open(os.path.join(OUT, "pull_list.csv"), "w") as f:
        f.write("sym,month\n")
        for s, m in pairs:
            f.write(f"{s},{m}\n")
    from collections import Counter
    c = Counter(m[:4] for _, m in pairs)
    print(len(pairs), "symbol-months", dict(c), "symbols", len({s for s, _ in pairs}))
