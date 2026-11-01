"""Exact-ish test of net > 0 for bounded binary returns: simulate outcomes with win probability q_i set so that each
trade's expected net excess return is exactly 0 (q_i = cost_i x (1 + friction + cash_i)); p = P(sim event-mean >= obs).
z = NormalDist().inv_cdf(1 - p). Same costs as the base run (h 1c / 0.5c)."""
import sys, os
from statistics import NormalDist
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A

U, _ = A.load_universe()
cells = {
    "P1-all-thr0.90-T1d": lambda r: A.p1_trade(r, A.DAY, 0.90, "all"),
    "P1-all-thr0.90-T7d": lambda r: A.p1_trade(r, 7 * A.DAY, 0.90, "all"),
    "P1-N-thr0.90-T7d": lambda r: A.p1_trade(r, 7 * A.DAY, 0.90, "N"),
    "P1-Y-thr0.90-T7d": lambda r: A.p1_trade(r, 7 * A.DAY, 0.90, "Y"),
    "P2a-L1h": lambda r: A.p2a_trade(r, A.H),
    "P2a-L12h": lambda r: A.p2a_trade(r, 12 * A.H),
    "P2b-first95": lambda r: A.p2b_trade(r),
}
rng = np.random.default_rng(631)
NS = 20000
for name, g in cells.items():
    for era in ("IS", "VAL"):
        rows = []
        for r in U:
            if A.era_of(r["closed"]) != era:
                continue
            tr = g(r)
            if tr is not None:
                rows.append((r, tr))
        cost = np.array([min(tr["p"] + A.half_spread(tr["p"], 1.0), 0.9999) for _, tr in rows])
        cash = np.array([A.cash(tr["t"], r["closed"]) for r, tr in rows])
        pay = np.array([r["final"][tr["tok"]] for r, tr in rows])
        q = np.minimum(cost * (1 + A.FRICTION + cash), 1.0)
        evk = [r["event"] for r, _ in rows]
        uniq = {e: i for i, e in enumerate(dict.fromkeys(evk))}
        ei = np.array([uniq[e] for e in evk])
        cnt = np.bincount(ei)
        obs = (np.bincount(ei, weights=pay / cost - 1 - A.FRICTION - cash) / cnt).mean()
        sims = np.empty(NS)
        for s in range(NS):
            w = rng.random(len(q)) < q
            sims[s] = (np.bincount(ei, weights=w / cost - 1 - A.FRICTION - cash) / cnt).mean()
        p = (np.sum(sims >= obs) + 1) / (NS + 1)
        losers = int(np.sum(pay == 0))
        print(f"{name:20s} {era:3s} n_ev {len(uniq):5d} trades {len(rows):5d} losers {losers:4d} (expected at net 0: {np.sum(1 - q):6.1f})  "
              f"obs {100 * obs:+.2f}%  p(net<=0) {p:.4f}  z {NormalDist().inv_cdf(1 - p):+.2f}")
