"""Stream R post hoc (information only, no new cells graded): per-year book sums for key cells incl. PRE, per-tenor
POST3 / PRE5-1 / CYC for the US, a max-over-cells null on MID (gross) IS t, and the random-day mean gross per cell.
Writes ../out/posthoc.txt."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade as G
from lib import nw_t

L = []
KEY = [("CYC", "US", ""), ("POST3", "US", ""), ("PRE5-1", "US", ""), ("PRE5-1", "ALL", ""), ("CYC", "ALL", ""),
       ("POST3", "US", "WEAK"), ("POST3", "ALL", "WEAK")]
L.append("per-year book sum, yield bp net (DV01 units; one unit per trade)")
L.append("cell | " + " ".join(f"{y % 100:02d}" for y in range(2004, 2025)))
for rule, pool, cond in KEY:
    evs = G.cell_events(pool, cond)
    A = np.array([e["i0"] for e in evs])
    bk, nets, gros, yrs = G.book(evs, A, rule)
    row = [f"{bk[G.UYEAR == y].sum():+.0f}" for y in range(2004, 2025)]
    L.append(f"{rule}|{pool}|{cond} | " + " ".join(row))
    for lab, late in (("late", 1),):
        bk2, n2, g2, y2 = G.book(evs, A, rule, 1.0, late)
        L.append(f"   {lab}: " + " ".join(f"{bk2[G.UYEAR == y].sum():+.0f}" for y in range(2004, 2025)))

L.append("\nUS per tenor: mean net yield bp per trade (n) PRE / IS / VAL")
for rule in ("PRE5-1", "PRE5-0", "POST3", "CYC"):
    for ten in ("2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"):
        net, gross, carry, entry = G.tb("US", ten, rule)
        evs = [e for e in G.E if e["c"] == "US" and e["ten"] == ten]
        A = np.array([e["i0"] for e in evs]); v = net[A]; yy = G.C["US"].years[entry[A]]
        cells = []
        for era, (a, b) in G.ERAS.items():
            m = (yy >= a) & (yy <= b) & ~np.isnan(v)
            cells.append(f"{v[m].mean():+.2f} ({m.sum()})" if m.any() else "nan")
        L.append(f"{rule} {ten}: " + " / ".join(cells))

# max-over-cells null on gross (mid) IS t
rng = np.random.default_rng(777)
EID = {id(e): j for j, e in enumerate(G.E)}
um = (G.UYEAR >= 2016) & (G.UYEAR <= 2021)


def mid_t(evs, A, rule):
    bk, nets, gros, yrs = G.book(evs, A, rule, 0.0)  # mult 0 -> no cost (carry kept)
    return nw_t(bk[um])


act = {}
for cell in G.CELLS:
    evs = G.cell_events(cell[1], cell[2]); A = np.array([e["i0"] for e in evs])
    act[cell] = mid_t(evs, A, cell[0])
mx = []
for s in range(200):
    RA = G.rand_anchors(G.E, rng)
    ts = []
    for cell in G.CELLS:
        evs = G.cell_events(cell[1], cell[2]); A = RA[[EID[id(e)] for e in evs]]
        ts.append(mid_t(evs, A, cell[0]))
    mx.append(max(ts))
mx = np.array(mx)
best = max(act, key=act.get)
L.append(f"\nmax IS t at mid (no cost) over {len(G.CELLS)} cells, 200 random calendars: median {np.median(mx):.2f}, p95 "
         f"{np.percentile(mx, 95):.2f}; actual best {best} {act[best]:.2f} (p {np.mean(mx >= act[best]):.3f})")
L.append("actual mid IS t per cell: " + ", ".join(f"{k[0]}|{k[1]}|{k[2]} {v:+.2f}" for k, v in act.items()))
open(os.path.join(G.OUT, "posthoc.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
