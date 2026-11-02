"""Stream T step 1: candidate delisting events from local perp_1d / spot_1d / spot_first (dates only).
Rows with ts >= 2025-01-01 are never read. Delisted = last 1d row with n > 0 before 2024-12-30 and every later row up
to the cut has n == 0 (the fapi keeps printing flat zero-trade klines after a settlement)."""
import csv, os, sys, time
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance"
CUT = 1735689600000
def spot_name(perp):
    for pre, fac in (("1000000", 1e6), ("1000", 1e3), ("1M", 1e6)):
        if perp.startswith(pre) and not perp[len(pre):][0].isdigit():
            return perp[len(pre):], fac
    return perp, 1.0
def span(path):
    first = lastact = lastrow = None
    with open(path) as f:
        r = csv.reader(f); h = next(r); ni = h.index("n")
        for x in r:
            t = int(float(x[0]))
            if t >= CUT: break
            lastrow = t
            if float(x[ni]) > 0:
                if first is None: first = t
                lastact = t
    return first, lastact, lastrow
d = lambda t: time.strftime('%Y-%m-%d', time.gmtime(t / 1000)) if t else ""
w = csv.writer(sys.stdout)
w.writerow(["perp", "perp_first", "perp_last_active", "perp_last_row", "spot", "fac", "spot_last_active", "spot_active_at_cut"])
for s in sorted(f[:-4] for f in os.listdir(os.path.join(D, "perp_1d")) if f.endswith(".csv")):
    if "_" in s: continue
    a, b, lr = span(os.path.join(D, "perp_1d", s + ".csv"))
    if b is None or b < 1577836800000 or b >= CUT - 2 * 86400000: continue
    sp, fac = spot_name(s)
    sb = sact = ""
    p = os.path.join(D, "spot_1d", sp + ".csv")
    if os.path.exists(p):
        _, sb0, slr = span(p); sb = d(sb0); sact = (sb0 is not None and sb0 >= CUT - 2 * 86400000)
    w.writerow([s, d(a), d(b), d(lr), sp, fac, sb, sact])
