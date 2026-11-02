"""Pre-entry pump of example listings, K2's definition on Binance local 1h perp bars (cut ts < 2025-01-01):
run = alt(L+1h)/alt(L-24h) - BTC(L+1h)/BTC(L-24h), prices = 1h bar opens. L = first venue 1h candle with volume > 0.
Also: pre-open part (L-24h -> L), first venue hour, and the venue's first-hour premium vs Binance relative to L+48h
(prem = (V/B at L) / (V/B at L+48h) - 1; FX drift over 2 days ignored)."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from candles import parse, fmt
from perps import perp_starts
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
D = R + "/retail_venues"
H = 3600000
PS = perp_starts()
CUT = 1735689600000


def b1h(sym):
    rows = {}
    for p in [R + f"/binance/perp_1h/{sym}_1735689599999.csv", R + f"/binance_basis/perp_1h/{sym}.csv", R + f"/binance_1h_full/1h/{sym}.csv"]:
        if not os.path.exists(p):
            continue
        for line in open(p).read().split("\n")[1:]:
            if line:
                f = line.split(","); t = int(f[0])
                if t < CUT:
                    rows[t] = float(f[1])
    return rows


BTC = b1h("BTCUSDT")
out = []
for p in sorted(glob.glob(D + "/*/w1h_*")):
    v = p.split("/")[-2]
    parts = os.path.basename(p)[4:-5].split("_")
    if v == "bitkub" and parts[1] == "THB":
        continue  # early BTC windows at created_at (not used)
    coin = parts[0]
    rows = [r for r in parse(v, p) if r[5] > 0]
    if not rows:
        print(f"{v:8s} {coin:6s} no traded 1h candle in window"); continue
    L = rows[0][0] // H * H
    sym = PS[coin][1]
    A = b1h(sym)
    a0, a1, aL = A.get(L - 24 * H), A.get(L + H), A.get(L)
    b0, b1, bL = BTC.get(L - 24 * H), BTC.get(L + H), BTC.get(L)
    run = pre = np.nan
    if None not in (a0, a1, b0, b1, aL, bL):
        run = (a1 / a0 - 1) - (b1 / b0 - 1)
        pre = (aL / a0 - 1) - (bL / b0 - 1)
    # venue premium vs Binance: first venue close vs close 48 h later
    vmap = {r[0] // H * H: r[4] for r in rows}
    prem = np.nan
    a48 = A.get(L + 49 * H); aL1 = A.get(L + H)
    if L + 48 * H in vmap and a48 and aL1:
        prem = (vmap[L] / aL1) / (vmap[L + 48 * H] / a48) - 1
    vol1 = rows[0][5]
    out.append((v, coin, fmt(L), (L - PS[coin][0]) // (24 * H), run, pre, prem))
    print(f"{v:8s} {coin:6s} L {fmt(L)} perp age {(L - PS[coin][0]) // (24 * H):5d} d  run(L-24h->L+1h) {run * 100:+6.1f} %  "
          f"pre-open {pre * 100:+6.1f} %  venue 1st-hour prem {prem * 100:+6.1f} %  first venue o/c {rows[0][1]:g}/{rows[0][4]:g}")
json.dump(out, open(D + "/pump_examples.json", "w"))
import collections
by = collections.defaultdict(list)
for o in out:
    by[o[0]].append(o)
for v, l in by.items():
    r = np.array([o[4] for o in l], float); pm = np.array([o[6] for o in l], float)
    print(f"SUMMARY {v:8s} n {len(l)} run mean {np.nanmean(r) * 100:+.1f} % median {np.nanmedian(r) * 100:+.1f} %  prem median {np.nanmedian(pm) * 100:+.1f} %")
