"""Hand-trace a few ETH trend trades (sanity check of the pipeline)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vc
d = vc.Data("ETHUSDT")
legs = vc.trend_legs(d)
z, _ = vc.zones_from_legs(d, legs, 3)
tests = vc.first_tests(d, z)
for (i, filled, ent, s, j) in tests[:4]:
    zz = [q for q in z if q[0] == j][0]
    a, b, sl = [l for l in legs if l[1] == j][0]
    r0, pr = vc.profile(d, a, b)
    print("leg bars", a, b, "side", s, "open", d.bo[a], "close", d.bc[b], "atr", round(d.atr_at(d.bs[b]), 1))
    print("  profile rows", r0, "..", r0 + len(pr) - 1, "median", round(np.median(pr), 1), "max row", r0 + int(np.argmax(pr)),
          "zone rows", zz[1], zz[2], "price", round(d.rp(zz[1]), 2), round(d.rp(zz[2], True), 2))
    fc = d.bs[j] + 30
    k = np.searchsorted(d.bs, fc)
    print("  next bars lows", np.round(d.bl[k:k + 4], 2), "highs", np.round(d.bh[k:k + 4], 2))
    print("  test min", d.mn[i], "(+%d min after formation)" % (d.mn[i] - fc), "l/h", d.ml[i], d.mh[i], "filled", filled, "entry", round(ent, 2))
    D = 0.15 * d.atr_at(d.mn[i])
    print("  stop", round(ent - s * D, 2), "TPV", round(vc.tp_price(d, ent, D, s, d.mn[i], "TPV"), 2), "2R", round(ent + s * 2 * D, 2))
tr = vc.simulate(d, tests, "TPV")
print(tr[:4])
