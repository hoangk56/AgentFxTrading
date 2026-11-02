"""QC (no returns): minute coverage per coin-year, taker-buy sanity, missing mark bars."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
for s in E.SYMS:
    c, v, tb = E.load_minutes(s)
    first = np.argmax(~np.isnan(c))
    out = []
    for y in range(5):
        a = y * 525600 + (1440 if y >= 1 else 0); b = a + (527040 if y == 0 or y == 4 else 525600)
        a2 = max(a, first)
        seg = c[a2:b]
        out.append(f"{2020 + y}: miss {np.isnan(seg).mean():.4f}" if len(seg) else f"{2020 + y}: n/a")
    ok = ~np.isnan(v)
    print(s, "first", np.datetime64(int(E.M0 + first), "m"), "| " + " ".join(out),
          "| tb>v", int((tb[ok] > v[ok] * 1.0001).sum()), "tb==0 share", round(float((tb[ok] == 0).mean()), 4),
          "v==0 share", round(float((v[ok] == 0).mean()), 4))
