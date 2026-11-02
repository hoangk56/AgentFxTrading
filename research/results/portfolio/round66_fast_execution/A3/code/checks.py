"""Stream A3 post-hoc checks (labelled post-hoc; they choose nothing): leave-one-out t, worst-price-of-the-1 s spot
entry, spot buy of $10k / $30k walking the real taker-buy prints after N + 5 s (VWAP of buyer-taker trades until the
notional is filled, i.e. as if our order had taken that flow), main IS set, hedged D5-L."""
import os, sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3/code")
import numpy as np
import analyze as an
from pull import load_events

OUT = open(os.path.join(an.OUTD, "checks.txt"), "w")
P = lambda *a: (print(*a), print(*a, file=OUT))
E = [e for e in load_events() if e["set"] == "main"]
base, worst, v10, v30 = [], [], [], []
for e in E:
    A = an.load("spot", e["spot"], e["day"]); B = an.load("perp", "BTCUSDT", e["day"])
    r = an.trade(e, 5, e["L"], A, B); base.append(r["net"])
    ae, te = an.after(A, e["N"] + 5000)
    k0, k1 = np.searchsorted(A["t"], [te, te + 1000]); wp = A["p"][k0:k1].max()
    worst.append(r["net"] - (r["gross"] - ((an.after(A, e["L"])[0] / wp - 1) - (an.after(B, e["L"])[0] / an.after(B, e["N"] + 5000)[0] - 1))))
    k = np.searchsorted(A["t"], te); sel = A["m"][k:] == 0
    p, q = A["p"][k:][sel], (A["p"][k:] * A["q"][k:])[sel]; c = np.cumsum(q)
    for tgt, L in ((10000, v10), (30000, v30)):
        j = np.searchsorted(c, tgt); vw = (p[:j + 1] * q[:j + 1]).sum() / q[:j + 1].sum()
        secs = (A["t"][k:][sel][min(j, len(c) - 1)] - te) / 1000
        L.append((r["net"] - (r["gross"] - ((an.after(A, e["L"])[0] / vw - 1) - (an.after(B, e["L"])[0] / an.after(B, e["N"] + 5000)[0] - 1))), secs))
    P(f"{e['coin']:5s} base {1e4*r['net']:7.0f}  worst-1s {1e4*worst[-1]:7.0f}  $10k-walk {1e4*v10[-1][0]:7.0f} ({v10[-1][1]:.1f} s)  $30k-walk {1e4*v30[-1][0]:7.0f} ({v30[-1][1]:.1f} s)")
days = [e["day"] for e in E]
for nm, x in (("declared", base), ("worst of 1 s", worst), ("$10k walk", [a for a, _ in v10]), ("$30k walk", [a for a, _ in v30])):
    m, t, n = an.clt(np.array(x), days); P(f"{nm:13s} mean {1e4*m:7.0f}  t {t:5.2f}  median {1e4*np.median(x):6.0f}")
loo = [an.clt(np.delete(np.array(base), i), np.delete(np.array(days), i)) for i in range(len(base))]
P("leave-one-out (drop coin: mean, t): " + ", ".join(f"{E[i]['coin']} {1e4*m:.0f} / {t:.2f}" for i, (m, t, n) in enumerate(loo)))
