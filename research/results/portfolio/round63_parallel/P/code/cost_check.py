"""Effective entry cost from taker prints (VAL 2024 only). For each sampled entry (cell, market, t):
buy-equivalent prints of the bought token k in [t, t + 2 h]: taker BUY of k at x -> x; taker SELL of (1-k) at y -> 1 - y
(both cross k's ask). fill = first such print after t; also the size-weighted mean of prints in the window.
Compares (fill - entry price) with the assumed half spread and recomputes returns on the same subset.
argv[1] = trades_primary.json"""
import sys, os, json, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import cash, half_spread, FRICTION, ymd

PR = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket/prints"
T = json.load(open(sys.argv[1]))
by = collections.defaultdict(list)
for x in T:
    fn = f"{PR}/{x['id']}_{int(x['t'])}.json"
    if not os.path.exists(fn):
        continue
    pr = json.load(open(fn))
    k, t = x["tok"], int(x["t"])
    buys = []
    for z in pr:
        try:
            ts, px, oi = int(z["timestamp"]), float(z["price"]), int(z["outcomeIndex"])
        except Exception:
            continue
        if not (t <= ts <= t + 7200):
            continue
        if z["side"] == "BUY" and oi == k:
            buys.append((ts, px, float(z["size"] or 0)))
        elif z["side"] == "SELL" and oi == 1 - k:
            buys.append((ts, 1 - px, float(z["size"] or 0)))
    buys.sort()
    rec = dict(x)
    rec["has"] = bool(buys)
    if buys:
        rec["first"] = buys[0][1]
        w = np.array([b[2] for b in buys])
        rec["vwap"] = float(np.average([b[1] for b in buys], weights=w)) if w.sum() > 0 else buys[0][1]
    by[x["cell"]].append(rec)

for cell, lst in by.items():
    n = len(lst)
    h = [r for r in lst if r["has"]]
    print(f"\n{cell}: sampled {n}, with a buy-side print in [t, t+2h]: {len(h)}")
    if not h:
        continue
    for lo, hi in ((0.80, 0.90), (0.90, 0.95), (0.95, 0.97), (0.97, 0.99)):
        s = [r for r in h if lo - 1e-9 <= r["p"] < hi - 1e-9]
        if s:
            d = np.array([r["first"] - r["p"] for r in s])
            print(f"  [{lo:.2f},{hi:.2f}) n{len(s):4d}  fill-mid: median {100 * np.median(d):+.2f}c  mean {100 * d.mean():+.2f}c  "
                  f"p75 {100 * np.percentile(d, 75):+.2f}c   assumed h {100 * half_spread((lo + hi) / 2, 1):.2f}c")
    rm, rf, rv = [], [], []
    for r in h:
        c = cash(r["t"], r["closed"])
        rm.append(r["payout"] / (r["p"] + half_spread(r["p"], 1)) - 1 - FRICTION - c)
        rf.append(r["payout"] / min(max(r["first"], 0.01), 0.9999) - 1 - FRICTION - c)
        rv.append(r["payout"] / min(max(r["vwap"], 0.01), 0.9999) - 1 - FRICTION - c)
    print(f"  same subset, mean net excess: model (mid + h) {100 * np.mean(rm):+.2f}%   first print {100 * np.mean(rf):+.2f}%   vwap 2h {100 * np.mean(rv):+.2f}%")
    nh = [r for r in lst if not r["has"]]
    if nh:
        print(f"  entries without a print (no evidence of fill): mean model return {100 * np.mean([r['ret'] for r in nh]):+.2f}%  vs with print {100 * np.mean([r['ret'] for r in h]):+.2f}%")
