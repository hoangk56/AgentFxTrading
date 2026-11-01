"""Stream BX: list B's frozen k100_H24_cheap trades (lag 0 and lag 1) for IS / VAL -> ../out/events.csv.
Imports B/code/basis.py read-only (cut at 2025-01-01 at load)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "B", "code"))
from basis import load, simulate, CUT  # noqa

H = 3600000
coins = load()
with open(os.path.join(HERE, "..", "out", "events.csv"), "w") as f:
    f.write("lag,perp,h_ms,e_ms,x_ms\n")
    for lag in (0, 1):
        T = simulate(coins, 100, 24, -1, lag=lag)
        for ci, h, e, x in zip(T["ci"], T["h"], T["e"], T["x"]):
            c = coins[ci]
            if c["hours"][e] >= CUT:
                continue
            f.write(f"{lag},{c['perp']},{c['hours'][h]},{c['hours'][e]},{c['hours'][x]}\n")
        print("lag", lag, "trades", len(T["e"]), flush=True)
