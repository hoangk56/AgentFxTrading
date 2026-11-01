"""Stream O: metrics coverage per half-year on the pulled coin-days (share of hours with a valid field)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E  # noqa: E402
from engine import xs  # noqa: E402

z = np.load(E.MET)
cov = z["cov"]
nd = cov.shape[1]
print("period        coin-days  OI   topPos  globAcc  taker   (share of instants k 2..23 with a value)")
for y in (2022, 2023, 2024):
    for hh in (0, 1):
        from datetime import datetime, timezone
        a = int((datetime(y, 1 + 6 * hh, 1, tzinfo=timezone.utc).timestamp() * 1000 - xs.H0) // xs.DAY)
        b = int((datetime(y + hh, 7 if hh == 0 else 1, 1, tzinfo=timezone.utc).timestamp() * 1000 - xs.H0) // xs.DAY)
        ii, dd = np.where(cov[:, a:b])
        dd = dd + a
        if len(ii) == 0:
            continue
        tt = (24 * dd[:, None] + np.arange(2, 24)[None, :])
        out = []
        for f in ("OIh", "TPh", "GAh", "TKh"):
            X = z[f]
            out.append(np.isfinite(X[ii[:, None], tt]).mean())
        print(f"{y}H{hh+1}       {len(ii):6d}   " + "  ".join(f"{v:5.2f}" for v in out))
