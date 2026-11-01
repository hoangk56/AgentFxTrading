"""Round 63 stream C: tables from ../out/cells.json + ../out/null_*.npz -> ../out/report.txt (IS / VAL only)."""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402

res = json.load(open(os.path.join(run.OUT, "cells.json")))
cl = ["|".join(map(str, c)) for c in run.cells()]
null = {}
for f in glob.glob(os.path.join(run.OUT, "null_*.npz")):
    z = np.load(f)
    null[str(z["cell"])] = z["out"]
L = []
p = L.append


def pct(x, arr):
    return 100.0 * (arr < x).mean()


p("cell (fam|sig|J|H) | IS net bp/reb, t, gross, cost, fund, turn | VAL net bp/reb, t, gross | late1 IS/VAL t | "
  "x1.5 IS/VAL t | vwap IS/VAL t | maker IS/VAL t | years + | rnd% IS/VAL | power reb/day | verdict")
rows = []
for k in cl:
    o = res[k]
    b = o["base"]; I, V = b["IS"], b["VAL"]
    yrs = b["years"]; ypos = sum(1 for v in yrs.values() if v > 0)
    nl = null.get(k)
    rIS = pct(I["mean_reb_bp"] / 1e4, nl[:, 1]) if nl is not None else np.nan
    rVA = pct(V["mean_reb_bp"] / 1e4, nl[:, 2]) if nl is not None else np.nan
    pw = min(b["power_reb"], b["power_day"])
    common = (I["mean_reb_bp"] > 0 and V["mean_reb_bp"] > 0 and o["cost15"]["IS"]["mean_reb_bp"] > 0
              and o["cost15"]["VAL"]["mean_reb_bp"] > 0 and o["late1"]["IS"]["mean_reb_bp"] > 0
              and o["late1"]["VAL"]["mean_reb_bp"] > 0)
    live = common and I["t"] >= 2.5 and V["t"] >= 1.5 and ypos >= 4 and min(rIS, rVA) >= 95 and pw >= 3
    demo = common and I["t"] >= 2.0 and min(rIS, rVA) >= 90
    verdict = "LIVE" if live else ("DEMO" if demo else "none")
    rows.append((k, I["t"], verdict))
    p(f"{k:16s} | {I['mean_reb_bp']:7.2f} {I['t']:6.2f} {I['gross_reb_bp']:7.2f} {I['cost_reb_bp']:6.2f} "
      f"{I['fund_reb_bp']:6.2f} {I['turn']:.2f} | {V['mean_reb_bp']:7.2f} {V['t']:6.2f} {V['gross_reb_bp']:7.2f} | "
      f"{o['late1']['IS']['t']:6.2f} {o['late1']['VAL']['t']:6.2f} | {o['cost15']['IS']['t']:6.2f} "
      f"{o['cost15']['VAL']['t']:6.2f} | {o['vwap']['IS']['t']:6.2f} {o['vwap']['VAL']['t']:6.2f} | "
      f"{o['maker']['IS']['t']:6.2f} {o['maker']['VAL']['t']:6.2f} | {ypos}/5 | {rIS:5.1f} {rVA:5.1f} | "
      f"{b['power_reb']:5.2f} {b['power_day']:5.2f} | {verdict}")
p("")
p("gross-only (no cost, no funding) t IS / VAL, mean bp per rebalance:")
for k in cl:
    g = res[k]["gross_only"]
    p(f"{k:16s} IS {g['IS']['mean_reb_bp']:7.2f}bp t{g['IS']['t']:6.2f} | VAL {g['VAL']['mean_reb_bp']:7.2f}bp "
      f"t{g['VAL']['t']:6.2f} | sd/day IS {100 * g['IS']['sd_day']:.2f}%")
p("")
p("years (net sum of rebalance returns, per $1 per side):")
for k in cl:
    p(f"{k:16s} " + " ".join(f"{y}:{100 * v:8.1f}%" for y, v in res[k]["base"]["years"].items()))
p("")
p("funding-stamp split (H < 24), net bp per rebalance IS / VAL, stamp vs non-stamp instants:")
for k in cl:
    o = res[k]
    if "split_stamp" in o:
        s, ns = o["split_stamp"], o["split_nonstamp"]
        p(f"{k:16s} stamp IS {s['IS']['mean_reb_bp']:7.2f} VAL {s['VAL']['mean_reb_bp']:7.2f} | non IS "
          f"{ns['IS']['mean_reb_bp']:7.2f} VAL {ns['VAL']['mean_reb_bp']:7.2f}")
if len(null) == len(cl):
    nm = np.stack([null[k][:, 0] for k in cl], axis=1)
    mx = nm.max(1)
    best = max(rows, key=lambda r: r[1])
    p("")
    p(f"max-over-54-cells null (IS t): best real cell {best[0]} t {best[1]:.2f}; null max t median "
      f"{np.median(mx):.2f}, 95th {np.percentile(mx, 95):.2f}; share of shuffles with max >= best: "
      f"{(mx >= best[1]).mean():.3f}")
p("")
p("verdicts: " + (", ".join(f"{k}={v}" for k, _, v in rows if v != "none") or "none (no cell reaches DEMO or LIVE)"))
txt = "\n".join(L)
open(os.path.join(run.OUT, "report.txt"), "w").write(txt)
print(txt)
