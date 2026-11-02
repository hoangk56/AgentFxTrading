"""Stream A4 post-hoc checks (labelled post-hoc; they choose nothing), H5-L on the 7 VAL events: F1 aggressor-side
fill and F2 worst price of the 1 s (A2's checks.py fill modes, Bybit side field: buy = 1 is a taker buy), a $10k /
$30k alt buy walking the real taker-buy prints after N + 5 s (A3's walk), leave-one-out t, trimmed mean, median,
largest single-print jumps near the entry (bad-print check), and the share of the event-day alt volume in the hold."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import analyze as an
from pull import load_events

OUT = open(os.path.join(an.OUTD, "checks.txt"), "w")
P = lambda *a: (print(*a), print(*a, file=OUT))


def fill(S, T, side, mode):
    t, p, b = S["t"], S["p"], S["buy"]
    i = np.searchsorted(t, T, "left")
    if mode == 0:
        return p[i], int(t[i])
    if mode == 1:  # taker-buy prints are at the ask, taker-sell at the bid
        want = 1 if side > 0 else 0
        j = i + np.argmax(b[i:i + 200000] == want)
        return p[j], int(t[j])
    j = np.searchsorted(t, T + 1000, "left")
    q = p[i:max(j, i + 1)]
    return (q.max() if side > 0 else q.min()), int(t[i])


def trade(e, A, B, mode, d=5):
    T = e["N"] + d * 1000; X = e["L"]
    ae, tae = fill(A, T, +1, mode); be, tbe = fill(B, T, -1, mode)
    ax, tax = fill(A, X, -1, mode); bx, tbx = fill(B, X, +1, mode)
    sl = an.slip(A, tae) + an.slip(A, tax) + an.slip(B, tbe) + an.slip(B, tbx)
    g = (ax / ae - 1) - (bx / be - 1)
    f = -an.fund(e["bsym"], tae, tax) + an.fund("BTCUSDT", tbe, tbx)
    return g + f - an.COST - sl


E = load_events(); days = [e["day"] for e in E]
res = {k: [] for k in ("F0", "F1", "F2", "W10", "W30")}; secs = {10000: [], 30000: []}
P("# A4 post-hoc checks, H5-L (net bp). F0 declared, F1 aggressor side, F2 worst of the 1 s, Wx = $x alt buy walking taker-buy prints")
for e in E:
    dd = sorted({e["day"], e["Lday"]})
    A = an.load(e["bsym"], dd); B = an.load("BTCUSDT", dd)
    for m, k in ((0, "F0"), (1, "F1"), (2, "F2")):
        res[k].append(trade(e, A, B, m))
    base = an.trade(e, 5, e["L"], A, B)
    ae, te = an.after(A, e["N"] + 5000)
    k0 = np.searchsorted(A["t"], te); sel = A["buy"][k0:] == 1
    p = A["p"][k0:][sel]; q = (A["p"][k0:] * A["q"][k0:])[sel]; tt = A["t"][k0:][sel]; c = np.cumsum(q)
    for tgt, key in ((10000, "W10"), (30000, "W30")):
        j = min(np.searchsorted(c, tgt), len(c) - 1); vw = (p[:j + 1] * q[:j + 1]).sum() / q[:j + 1].sum()
        res[key].append(base["net"] + (ae / vw - 1) * (an.after(A, e["L"])[0] / ae))  # ax/vw - ax/ae
        secs[tgt].append((tt[j] - te) / 1000)
    # bad-print check: largest |log jump| between consecutive alt prints in [N, N + 10 s]
    i0, i1 = np.searchsorted(A["t"], [e["N"], e["N"] + 10000])
    lj = np.abs(np.diff(np.log(A["p"][i0:i1]))) if i1 - i0 > 1 else np.array([0.0])
    # share of the day's alt trades that fall in the 40 min window around N (in the N-day file)
    P(f"{e['coin']:6s} F0 {1e4*res['F0'][-1]:7.0f} F1 {1e4*res['F1'][-1]:7.0f} F2 {1e4*res['F2'][-1]:7.0f} "
      f"$10k {1e4*res['W10'][-1]:7.0f} ({secs[10000][-1]:.1f} s)  $30k {1e4*res['W30'][-1]:7.0f} ({secs[30000][-1]:.1f} s)  "
      f"max 1-print jump N..N+10s {1e4*lj.max():.0f} bp, prints {i1-i0}")
P("\nfill        mean      t   median   SR    power@4.3  power@11.0")
for k, x in res.items():
    x = np.array(x); m, t, n = an.clt(x, days); sr = x.mean() / x.std(ddof=1)
    P(f"{k:6s}  {1e4*m:8.0f} {t:6.2f} {1e4*np.median(x):7.0f} {sr:6.2f} {sr*np.sqrt(an.N_HOLD):8.2f} {sr*np.sqrt(an.N_HOLD24):9.2f}")
x0 = np.array(res["F0"]); s = np.sort(x0)
P(f"\ntrimmed (drop min and max) mean {1e4*s[1:-1].mean():.0f}; median {1e4*np.median(x0):.0f}; min {1e4*x0.min():.0f}")
loo = [an.clt(np.delete(x0, i), np.delete(np.array(days), i)) for i in range(len(x0))]
P("leave-one-out (drop coin: mean / t): " + ", ".join(f"{E[i]['coin']} {1e4*m:.0f} / {t:.2f}" for i, (m, t, n) in enumerate(loo)))
lx = np.log1p(x0); m, t, n = an.clt(lx, days)
P(f"log-return version of net (log(1 + net)): mean {1e4*m:.0f} bp, t {t:.2f}")
