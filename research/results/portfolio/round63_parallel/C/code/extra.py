"""Round 63 stream C: per-year gross (price only) and break-even cost per side for selected cells; universe slice
(volume rank 0-19 vs 20-39) for REV raw 1|1 and 1|24. IS / VAL only. Writes ../out/extra.txt."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run, xs  # noqa
cx = xs.Ctx(xs.load())
L = []
for c in [("REV", "raw", 1, 1), ("REV", "raw", 1, 4), ("REV", "raw", 1, 24), ("REV", "raw", 4, 1), ("VLO", "raw", 1, 1),
          ("VLO", "raw", 24, 24)]:
    fam, kind, J, H = c
    ts, S = xs.precompute(cx, J, H, kind, fam)
    W = xs.weights(S, run.q_of(fam))
    M = xs.mats(cx, ts, H)
    b = xs.book(M, W, fee=0.0, spread=False, funding=False)
    y = b["tms"].astype("datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970
    parts = []
    for yy in range(2020, 2025):
        m = y == yy
        g = b["gross"][m].mean() * 1e4
        tv = b["turn"][m].mean()
        parts.append(f"{yy}: g {g:6.2f}bp be {g / (4 * tv) if tv > 0 else 0:5.2f}bp")
    L.append(f"{'|'.join(map(str, c)):14s} gross per rebalance and break-even cost per side per trade: " + "; ".join(parts))
    if c in [("REV", "raw", 1, 1), ("REV", "raw", 1, 24)]:
        days = ((ts * xs.HOUR) // xs.DAY).astype(np.int64)
        rk = cx.rk[:, days].T
        for nm, msk in (("rank 0-19", rk < 20), ("rank 20-39", (rk >= 20) & (rk < 40))):
            S2 = np.where(msk, S, np.nan)
            W2 = xs.weights(S2, 4)
            b2 = xs.book(M, W2, fee=0.0, spread=False, funding=False)
            for era, rr in (("IS", xs.IS), ("VAL", xs.VAL)):
                m = xs.era_mask(b2["tms"], rr)
                st = xs.tstats(b2["gross"][m], b2["tms"][m])
                L.append(f"   {nm} q=4 {era}: gross {1e4 * b2['gross'][m].mean():6.2f}bp t {st['t']:5.2f} turn "
                         f"{b2['turn'][m].mean():.2f}")
txt = "\n".join(L)
open(os.path.join(run.OUT, "extra.txt"), "w").write(txt)
print(txt)
