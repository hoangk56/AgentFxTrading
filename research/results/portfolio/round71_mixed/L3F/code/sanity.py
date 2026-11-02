import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3f
s = "BTCUSDT"
ft, ff, f8 = l3f.load_funding(s)
o, c, src = l3f.load_1h(s)
print(src, "last funding", ft[-1].astype("datetime64[ms]"), "nan close share", np.isnan(c[(l3f.IS[0]-l3f.T0)//l3f.H:]).mean())
ev = l3f.trailing_pct_flags(ft, f8, 5)
k = np.where(ev & (ft >= l3f.IS[0]))[0][:8]
for j in k:
    T = ft[j]; sg = l3f.day_sign(o, c, T); tr = l3f.trade(o, c, ft, ff, T, sg)
    kT = (T - l3f.T0)//l3f.H
    print(T.astype("datetime64[ms]"), "f %.5f" % ff[j], "sign", sg, "P_T %.1f entry %.1f exit %.1f" % (c[kT-1], c[kT], c[kT+24]),
          "ret %.4f fund %.5f" % (tr[0], tr[1]))
