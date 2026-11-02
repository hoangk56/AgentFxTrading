"""Stream A2 post-hoc execution checks (labelled post-hoc in STREAM_A2.md; they do not pick a cell):
 F0 declared fill (first trade >= T), F1 aggressor-side fill (long alt entry = first buyer-taker trade, BTC short entry =
 first seller-taker trade; exits mirrored), F2 worst price of the second after T (alt entry = max, alt exit = min,
 BTC the opposite). Same 20 bp + declared slippage + funding. Also fill-time gaps, capacity (buyer-taker alt notional in
 the first 1 s / 5 s after N + d), trimmed and leave-one-out stats, C3 correlation."""
import csv, os, sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A2/code")
import numpy as np
import analyze as Z
from events import load_events

OUT = open(os.path.join(Z.OUTD, "checks.txt"), "w")
P = lambda *a: (print(*a), print(*a, file=OUT))


def fill(S, T, side, mode):
    """side +1 = we buy (pay the ask), -1 = we sell. Returns (price, time)."""
    t, p, m = S["t"], S["p"], S["m"]
    i = np.searchsorted(t, T, "left")
    if mode == 0:
        return p[i], int(t[i])
    if mode == 1:  # buyer-taker trades (m == 0) print at the ask; seller-taker (m == 1) at the bid
        want = 0 if side > 0 else 1
        j = i + np.argmax(m[i:i + 200000] == want)
        return p[j], int(t[j])
    j = np.searchsorted(t, T + 1000, "left")
    q = p[i:max(j, i + 1)]
    return (q.max() if side > 0 else q.min()), int(t[i])


def trade(e, d, X, A, B, mode):
    N = e["N"]; T = N + d * 1000
    ae, tae = fill(A, T, +1, mode); be, tbe = fill(B, T, -1, mode)
    ax, tax = fill(A, X, -1, mode); bx, tbx = fill(B, X, +1, mode)
    sl = Z.slip(A, tae) + Z.slip(A, tax) + Z.slip(B, tbe) + Z.slip(B, tbx)
    g = (ax / ae - 1) - (bx / be - 1)
    f = -Z.fund(e["perp"], tae, tax) + Z.fund("BTCUSDT", tbe, tbx)
    return g + f - Z.COST - sl, (tae - T) / 1000


E = load_events()
res = {}
for e in E:
    A = Z.load(e["perp"], e["day"]); B = Z.load("BTCUSDT", e["day"])
    for d in Z.DS:
        for xn in ("5m", "L"):
            X = e["N"] + 300000 if xn == "5m" else e["L"]
            for mode in (0, 1, 2):
                res[(e["coin"], e["day"], d, xn, mode)] = trade(e, d, X, A, B, mode)
P("# A2 post-hoc execution checks (net bp / trade, t clustered by day; F0 declared, F1 aggressor side, F2 worst of the 1 s)")
P("cell     era   F0 net   t     F1 net   t     F2 net   t     F1 SR  F1 pow  F0 trim10 F0 med  F0 min-loo-t  maxgap s")
for d in Z.DS:
    for xn in ("5m", "L"):
        for era in ("IS", "VAL"):
            S = [e for e in E if e["era"] == era]; days = [e["day"] for e in S]
            line = f"D{d}-{xn:3s} {era:4s}"
            vals = {}
            for mode in (0, 1, 2):
                x = np.array([res[(e["coin"], e["day"], d, xn, mode)][0] for e in S]); vals[mode] = x
                m, t, n = Z.clt(x, days); line += f" {1e4*m:7.0f} {t:5.2f}"
            x1 = vals[1]; sr1 = x1.mean() / x1.std(ddof=1)
            x0 = np.sort(vals[0]); k = max(1, len(x0) // 10)
            trim = x0[k:-k].mean()
            loo = min(Z.clt(np.delete(vals[0], i), np.delete(np.array(days), i))[1] for i in range(len(S)))
            gap = max(res[(e["coin"], e["day"], d, xn, 0)][1] for e in S)
            line += f"  {sr1:5.2f} {sr1*np.sqrt(Z.N_HOLD) if era=='VAL' else float('nan'):6.2f}  {1e4*trim:7.0f} {1e4*np.median(vals[0]):6.0f}   {loo:5.2f}     {gap:5.2f}"
            P(line)

P("\n# Capacity: buyer-taker alt notional (USDT) in [N + d, N + d + 1 s] and [N + d, N + d + 5 s]; median / q25 per era")
for d in Z.DS:
    for era in ("IS", "VAL"):
        a1, a5 = [], []
        for e in [e for e in E if e["era"] == era]:
            A = Z.load(e["perp"], e["day"]); T = e["N"] + d * 1000
            for w, acc in ((1000, a1), (5000, a5)):
                i, j = np.searchsorted(A["t"], [T, T + w])
                mm = A["m"][i:j] == 0
                acc.append(float((A["p"][i:j][mm] * A["q"][i:j][mm]).sum()))
        P(f"  d {d:2d} {era:4s} 1 s: median {np.median(a1):11,.0f} q25 {np.percentile(a1,25):11,.0f}   5 s: median {np.median(a5):11,.0f} q25 {np.percentile(a5,25):11,.0f}")

# year-by-year for the declared choice D5-L and D5-5m under F1
P("\n# Years under F1 (aggressor-side fills)")
for c in ((5, "L"), (5, "5m"), (2, "5m"), (10, "L")):
    ys = {}
    for e in E:
        ys.setdefault(e["year"], []).append(res[(e["coin"], e["day"], c[0], c[1], 1)][0])
    P(f"  D{c[0]}-{c[1]}: " + " ".join(f"{y} {1e4*np.mean(v):+.0f} ({len(v)})" for y, v in sorted(ys.items())))

# C3 correlation on overlapping days (D5-L declared choice, F0)
c3 = None
for root, _, files in os.walk("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio"):
    if "trades_C3_gotobi_jpy_basket.csv" in files and "hold" not in root:
        c3 = os.path.join(root, "trades_C3_gotobi_jpy_basket.csv"); break
P("\n# C3 file:", c3)
if c3:
    R = list(csv.DictReader(open(c3)))
    P("  C3 columns:", list(R[0].keys())[:12], "rows", len(R))
    OUT.flush()
