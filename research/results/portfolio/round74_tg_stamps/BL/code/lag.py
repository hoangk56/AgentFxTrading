"""Post-hoc timing check (labelled post-hoc; it chooses no cell): when does the listing / launch jump happen relative to
the Telegram stamp N? Baseline b = last price at N - 15 min; M = max ln(P / b) over [N - 10 min, N + 5 min]; jump time =
first trade with ln(P / b) >= M / 2 (events with M >= 200 bp L1 / 100 bp L2). Also the largest 10 s rise in the same
window and its start time. Usage: python -I lag.py l1|l2"""
import json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net
from analyze import Series
rule = sys.argv[1]
E = [e for e in json.load(open(os.path.join(net.D, f"{rule}_events.json"))) if not e["edited"]]
thr = 200 if rule == "l1" else 100
res = []
for e in E:
    S = Series(e["src"], e["sym"], e["days"]); N = e["N"]
    b = S.last_at(N - 900000)
    if not np.isfinite(b):
        continue
    k0, k1 = np.searchsorted(S.t, N - 600000), np.searchsorted(S.t, N + 300000)
    if k1 <= k0:
        continue
    lp = np.log(S.p[k0:k1] / b) * 1e4; tt = S.t[k0:k1]
    M = lp.max()
    # largest 10 s rise: for each trade, price 10 s later minus now
    j = np.searchsorted(tt, tt + 10000, side="right") - 1
    rise = lp[j] - lp; i10 = int(np.argmax(rise))
    row = dict(day=e["day"], coin=e["coin"], era=e["era"], M=M, r10=float(rise[i10]), t10=(tt[i10] - N) / 1000)
    if M >= thr:
        h = int(np.argmax(lp >= M / 2)); row["half"] = (tt[h] - N) / 1000
    res.append(row)
for era in ("IS", "VAL"):
    R = [r for r in res if r["era"] == era]
    if not R:
        continue
    H = np.array([r["half"] for r in R if "half" in r]); T10 = np.array([r["t10"] for r in R if r["r10"] >= thr / 2])
    print(f"{rule} {era}: n {len(R)}; half-move time vs N (n {len(H)}): median {np.median(H):+.0f} s, q25 {np.percentile(H,25):+.0f}, "
          f"q75 {np.percentile(H,75):+.0f}, share < 0 {np.mean(H < 0):.2f}, share < -60 s {np.mean(H < -60):.2f}")
    if len(T10):
        print(f"   largest 10 s rise (>= {thr//2} bp, n {len(T10)}) starts: median {np.median(T10):+.0f} s, share before N {np.mean(T10 < 0):.2f}")
    for r in R:
        print(f"   {r['day']} {r['coin']:<10} M {r['M']:+6.0f} half {r.get('half', float('nan')):+7.0f} s  max10s {r['r10']:+5.0f} at {r['t10']:+6.0f} s")
