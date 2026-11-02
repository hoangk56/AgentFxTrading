"""Stream W7 (information, after grading): path of d = ln(spot / ref perp) from the +15 min signal to past the
withdrawal clock, by the sign / size of d at the signal. Same reference as the signal. Run with python -I."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import analyze as A
evs = A.load_events()
OFF = [("S", 0), ("S+5m", 5), ("S+30m", 30), ("S+2h", 120), ("S+6h", 360), ("S+12h", 720), ("W-1h", None), ("W", None),
       ("W+1h", None), ("W+4h", None)]
for m in (15, 60):
    buckets = {"d<=-50": [], "-50<d<50": [], "d>=+50": []}
    for e in evs:
        s = A.signal(e, m)
        if s is None:
            continue
        row = []
        for nm, mm in OFF:
            if mm is not None:
                t = s["S"] + mm * 60000
            else:
                t = e["W"] + {"W-1h": -60, "W": 0, "W+1h": 60, "W+4h": 240}[nm] * 60000
            a, b = e["sp"].mid(t), s["rf"].mid(t)
            row.append(1e4 * np.log(a / (s["f"] * b)) if np.isfinite(a) and np.isfinite(b) else np.nan)
        k = "d<=-50" if s["d"] <= -50 else ("d>=+50" if s["d"] >= 50 else "-50<d<50")
        buckets[k].append(row)
    print(f"signal +{m} min: median d (bp) | " + " | ".join(n for n, _ in OFF))
    for k, v in buckets.items():
        v = np.array(v)
        if len(v):
            print(f"  {k} (n {len(v)}): " + " | ".join(f"{x:+.0f}" for x in np.nanmedian(v, axis=0)))
