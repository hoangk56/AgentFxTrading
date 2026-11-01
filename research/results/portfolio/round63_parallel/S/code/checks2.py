import numpy as np, onlib
P = onlib.Panel()
d = P.div[P.year >= 2016]
d = d[np.isfinite(d)]
for th in [0, 1e-7, 1e-6, 1e-5, 1e-4, 5e-4, 1e-3]:
    print(th, (d > th).sum())
print(np.percentile(d[d > 1e-4], [1, 5, 25, 50, 75, 95, 99]))
# per year count of div > 1e-4 vs number of names
for y in [2005, 2016, 2023]:
    m = P.year == y
    print(y, (P.div[m] > 1e-4).sum(), np.isfinite(P.close[m]).any(0).sum())
