"""Check the scaled-iv mark-to-market (entry straddle iv x DVOL(t)/DVOL(entry)) against Deribit marks of the same
BTC 30d instruments on later days (08:00-09:00 trades, research/data/deribit/BTC_daily)."""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, vrp

m = vrp.Mkt("BTC")
D = vrp.load_trades("BTC", "daily")
Q = pickle.load(open("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/deribit/quotes_BTC.pkl", "rb"))
err = []
for q in Q[(30, False)]:
    for d in range(1, 30, 3):
        t0 = q["f0"] + d * vrp.DAY + 8 * vrp.H
        if t0 + 2 * vrp.DAY > q["T"]:
            break
        a, b = np.searchsorted(D["ts"], [t0, t0 + vrp.H])
        sl = slice(a, b)
        sel = (D["exp"][sl] == q["T"]) & (D["k"][sl] == q["K"]) & np.isfinite(D["mark"][sl])
        if not sel.any():
            continue
        i = np.where(sel)[0][0] + a
        S, tau = D["idx"][i], (q["T"] - D["ts"][i]) / vrp.DAY / 365
        sig = q["sig"] * m.dvol_at((D["ts"][i] // vrp.H) * vrp.H) / q["dvol"]
        model = float(vrp.bs(S, q["K"], tau, sig, int(D["cp"][i]))[0])
        err.append((model - D["mark"][i] * S) / S)
err = np.array(err) * 100
print(f"n {len(err)} legs; model - mark, % of spot: median {np.median(err):+.2f}, median |err| {np.median(np.abs(err)):.2f}, p90 |err| {np.percentile(np.abs(err), 90):.2f}")
