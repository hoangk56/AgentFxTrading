"""Registered HOLD look for PREREG_DRAFT_D2_ON (coordinator only, run once). NOT run by stream D2.
Steps (coordinator): D2_HOLD=1 python -I pull.py ; D2_HOLD=1 python -I parse.py ; D2_HOLD=1 python -I hold_run.py
Requires local Binance 1h (binance_1h_full/1h) and funding (binance/funding) files covering 2025-01-01..2026-10-29."""
import os, sys
if os.environ.get("D2_HOLD") != "1":
    sys.exit("refusing: HOLD run needs D2_HOLD=1 (coordinator only)")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import d2

A = {a: d2.daily(d2.load(a)) for a in ("BTC", "ETH")}
days = A["BTC"]["days"]
assert days[-1] == d2.CUT
cash = d2.fed_funds(days); yrs = d2.years(days)
d0, d1 = int(np.searchsorted(days, d2.ERAS["HOLD"][0])), int(np.searchsorted(days, d2.ERAS["HOLD"][1]))
on = np.ones(len(days), bool)
late = np.concatenate([[False], on[:-1]])
cs = cash[d0:d1]; yy = yrs[d0:d1]
for a in ("BTC", "ETH"):
    print(a, "missing marks FD/FB/S:", A[a]["miss_FD"], A[a]["miss_FB"], A[a]["miss_S"])


def book(cost_mult=1.0, mask=on):
    R = {a: d2.simulate(A[a], d0, d1, mask, L=2.0, cost_mult=cost_mult) for a in ("BTC", "ETH")}
    R["BOTH"] = {"r": 0.5 * (R["BTC"]["r"] + R["ETH"]["r"]),
                 "fundB": 0.5 * (R["BTC"]["fundB"] + R["ETH"]["fundB"]),
                 "fundD": 0.5 * (R["BTC"]["fundD"] + R["ETH"]["fundD"]),
                 "price": 0.5 * (R["BTC"]["price"] + R["ETH"]["price"]),
                 "cost": 0.5 * (R["BTC"]["cost"] + R["ETH"]["cost"]), "liq": R["BTC"]["liq"] + R["ETH"]["liq"]}
    return R


R = book(); R15 = book(1.5); RL = book(mask=late)
for a in ("BOTH", "BTC", "ETH"):  # BOTH is the registered cell; BTC / ETH reported only
    r = R[a]["r"]; st = d2.stats(r); ex = d2.stats(r - cs * 1.0)
    print(f"HOLD {a} ON: net {100*st['ann']:.2f} %/yr t_nw {st['t']:.2f} SR {st['sr']:.2f} maxdd {100*st['maxdd']:.2f} | "
          f"excess over DFF (C = N) {100*ex['ann']:.2f} t {ex['t']:.2f} | x1.5 {100*d2.stats(R15[a]['r'])['ann']:.2f} "
          f"late {100*d2.stats(RL[a]['r'])['ann']:.2f}")
    print("   net by year", {int(y): round(float(100 * r[yy == y].sum()), 2) for y in np.unique(yy)},
          "excess by year", {int(y): round(float(100 * (r - cs)[yy == y].sum()), 2) for y in np.unique(yy)})
    print("   decomposition %/yr", {k: round(float(100 * 365 * R[a][k].mean()), 2) for k in ("fundB", "fundD", "price", "cost")},
          "liq-check days", len(R[a]["liq"]))
