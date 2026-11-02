"""Stream CG extras (information only, not declared cells): medians, trimmed means, the opposite (follow) side."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gap  # noqa: E402
from report import CELLS  # noqa: E402

S = {s: gap.load(s) for s in ("BTCUSDT", "ETHUSDT")}
real = gap.run(S, gap.real_anchors())
for name, k, H in CELLS:
    for e in ("IS", "VAL"):
        c = gap.cell(real, k, H, era_=e)
        x = np.sort(c["x"]); n = len(x); q = max(1, int(0.05 * n))
        fol = -(c["gross"]) - c["fund"] - 12.0      # follow side: opposite gross and funding, same cost
        print(f"{name} {e:3s} fade median {np.median(x):+7.1f} trim5% {x[q:-q].mean():+7.1f} win {np.mean(x > 0):.2f} | "
              f"follow net {fol.mean():+7.1f} t {gap.cl_t(fol, c['g']):+5.2f}")
