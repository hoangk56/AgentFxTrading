"""Map B's stored trades (B/out/trades_k100_H24_cheap.npz, field ci) to perp names by reproducing the coin order of
B's load() (keep order, EXCL, U.any(), files present, >= WIN rows) without loading the hourly panels. Writes
../out/b_trades_named.csv (perp,t_entry_ms,net,price,fund). Pre-2025 only (B's IS / VAL file)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "B", "code"))
import basis as Bm
from universe import universe
keep, U, R, days = universe(60)
names = []
for i, (perp, spot, fac, _) in enumerate(keep):
    if perp in Bm.EXCL or not U[i].any():
        continue
    pp, sp = os.path.join(Bm.BB, "perp_1h", perp + ".csv"), os.path.join(Bm.BB, "spot_1h", spot + ".csv")
    if not (os.path.exists(pp) and os.path.exists(sp)):
        continue
    if len(Bm._read(pp)) < Bm.WIN or len(Bm._read(sp)) < Bm.WIN:
        continue
    names.append(perp)
T = np.load(os.path.join(HERE, "..", "..", "B", "out", "trades_k100_H24_cheap.npz"))
print("coins", len(names), "max ci", T["ci"].max(), "trades", len(T["ci"]))
with open(os.path.join(HERE, "..", "out", "b_trades_named.csv"), "w") as f:
    f.write("perp,t,net,price,fund\n")
    for ci, t, n_, p, fu in zip(T["ci"], T["t"], T["net"], T["price"], T["fund"]):
        f.write(f"{names[ci]},{int(t)},{n_},{p},{fu}\n")
