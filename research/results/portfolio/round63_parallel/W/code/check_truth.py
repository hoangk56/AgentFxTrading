"""Settlement check (no prices): does the ISD SOD max fall in the bracket Kalshi settled YES?"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest as B, model as M
evs = B.load_events(); obs = B.Obs()
c = collections.Counter()
for e in evs:
    sod = obs.d[e["city"]][2].get(e["day"])
    yes = [b for b in e["br"] if b["yes"]]
    if sod is None or len(yes) != 1:
        c[(e["city"], "skip")] += 1; continue
    b = yes[0]
    c[(e["city"], "match" if b["lo"] <= sod <= b["hi"] else "miss")] += 1
print(sorted(c.items()))
