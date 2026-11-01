"""Descriptive check for rule (b): quotes on brackets already decided by the observed max (margin 1 F)."""
import sys, os, collections, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest as B
evs = B.load_events(); obs = B.Obs()
c = collections.Counter(); asks = []; bids = []
for e in evs:
    t0 = obs.t0(e["city"], e["day"])
    for T in range(10, 24):
        s = obs.state(e["city"], e["day"], T)
        if s is None: continue
        Mx = s[0] - 1
        for b in e["br"]:
            q = B.quote(b, t0 + T * 3600)
            if q is None: c["noquote"] += 1; continue
            if b["hi"] < Mx:
                c["dead"] += 1
                if q[0] is not None: c["dead_with_bid"] += 1; bids.append(q[0])
                if b["yes"]: c["dead_but_settled_yes"] += 1
            elif b["hi"] == 999 and b["lo"] <= Mx:
                c["won"] += 1
                if q[1] is not None: c["won_with_ask"] += 1; asks.append(q[1])
                if not b["yes"]: c["won_but_settled_no"] += 1
print(dict(c))
print("dead bids", sorted(bids)[:20]); print("won asks", np.percentile(asks, [0, 10, 50, 90]) if asks else None, len(asks))
