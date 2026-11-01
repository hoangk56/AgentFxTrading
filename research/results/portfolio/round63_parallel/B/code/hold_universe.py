"""HOLD look (PREREG_B_cheap_basis.md): the frozen universe.py with only END moved to the HOLD end (2026-10-30 00:00
UTC). Writes ../universe60_hold.csv (symbols in the top-60 on any day 2025-01-01..2026-10-29, with first / last HOLD
universe day, same columns as universe60.csv) and checks that the pre-2025 universe is unchanged."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import universe as U_mod

HOLD_A, HOLD_B = 1735689600000, 1793318400000
OLD_END = U_mod.END


def hold_universe():
    U_mod.END = HOLD_B
    return U_mod.universe(60)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                                               "universe60_hold.csv")
    keep, U, R, days = hold_universe()
    # consistency: pre-2025 universe identical to the registered one
    U_mod.END = OLD_END
    keep0, U0, R0, days0 = U_mod.universe(60)
    U_mod.END = HOLD_B
    idx = {k[0]: i for i, k in enumerate(keep)}
    same = all((U[idx[k[0]], :U0.shape[1]] == U0[i]).all() and (R[idx[k[0]], :U0.shape[1]] == R0[i]).all()
               for i, k in enumerate(keep0))
    print("pre-2025 universe identical:", same, "| symbols", len(keep0), "->", len(keep))
    d0 = np.searchsorted(days, HOLD_A)
    ever = U[:, d0:].any(1)
    excl = {"BTCUSDT", "ETHUSDT"}
    print("ever in HOLD universe:", ever.sum(), "(incl BTC/ETH)", "days", U.shape[1] - d0,
          "mean members/day", U[:, d0:].sum(0).mean().round(1))
    with open(out, "w") as f:
        for i in np.where(ever)[0]:
            k = keep[i]
            w = np.where(U[i, d0:])[0] + d0
            f.write(f"{k[0]},{k[1]},{k[2]:g},{int(days[w[0]])},{int(days[w[-1]] + U_mod.DAY)}\n")
    print("wrote", out)
