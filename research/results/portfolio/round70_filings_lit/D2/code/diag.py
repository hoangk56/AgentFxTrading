"""Diagnostics on IS / VAL only (python -I diag.py): excess over cash by year, leverage sensitivity, mean DFF by year,
share of the ON book that is spot collateral carry vs perp-perp gap. Output: ../out/diag.txt"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import d2

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
L_ = []


def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); L_.append(s)


A = {a: d2.daily(d2.load(a)) for a in ("BTC", "ETH")}
days = A["BTC"]["days"]; cash = d2.fed_funds(days); yrs = d2.years(days)
on = np.ones(len(days), bool)
for e in ("IS", "VAL"):
    a0, b0 = d2.ERAS[e]
    d0, d1 = int(np.searchsorted(days, a0)), int(np.searchsorted(days, b0))
    yy = yrs[d0:d1]; cs = cash[d0:d1]
    for L in (1.5, 2.0, 3.0):
        C = 2.0 / L
        R = {a: d2.simulate(A[a], d0, d1, on, L=L) for a in ("BTC", "ETH")}
        R["BOTH"] = {"r": 0.5 * (R["BTC"]["r"] + R["ETH"]["r"])}
        for a in ("BTC", "ETH", "BOTH"):
            r = R[a]["r"]; ex = r - cs * C
            st = d2.stats(ex)
            by = {int(y): round(float(100 * ex[yy == y].sum()), 2) for y in np.unique(yy)}
            say(f"{e} {a:4s} ON L {L}: capital {C:.2f} N  net {100*365*r.mean():6.2f}  excess {100*st['ann']:6.2f} "
                f"t {st['t']:5.2f} SR {st['sr']:5.2f}  excess by year {by}")
    say(f"{e} mean DFF by year (%):", {int(y): round(float(100 * 365 * cs[yy == y].mean()), 2) for y in np.unique(yy)})
    for a in ("BTC", "ETH"):
        g = A[a]["gap_pure"][d0:d1]; fb = A[a]["fb"][d0:d1]
        say(f"{e} {a} by year %/yr: pure gap fB-fD {dict((int(y), round(float(100*365*g[yy==y].mean()),2)) for y in np.unique(yy))}"
            f"  Binance funding {dict((int(y), round(float(100*365*fb[yy==y].mean()),2)) for y in np.unique(yy))}")
open(os.path.join(OUT, "diag.txt"), "w").write("\n".join(L_) + "\n")
