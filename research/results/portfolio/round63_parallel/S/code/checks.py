import numpy as np, onlib
P = onlib.Panel()
O = None
z = np.load(onlib.DATA)
O, C, H, L = z["open"], z["close"], z["high"], z["low"]
Cp = np.vstack([np.full((1, C.shape[1]), np.nan), C[:-1]])
for y in range(2003, 2025):
    m = P.year == y
    v = P.raw_valid[m]
    eqprev = (np.abs(O[m] / Cp[m] - 1) < 1e-9) & v
    flat = (O[m] == C[m]) & (H[m] == L[m]) & v
    names = np.isfinite(C[m]).sum(1)
    print(y, "days", m.sum(), "names med", int(np.median(names)), "valid frac %.4f" % (v.sum() / np.isfinite(C[m]).sum()),
          "open==prevclose %.4f" % (eqprev.sum() / v.sum()), "flat %.5f" % (flat.sum() / v.sum()),
          "div events", int((P.div[m] > 0).sum()), "on nan frac %.4f" % (np.isnan(P.on[m][v]).mean()))
# days with few names
names = np.isfinite(C).sum(1)
print("dates with < 50% of the median name count:", [(P.dates[i], names[i]) for i in np.where(names < 0.5 * np.median(names[-500:]))[0] if P.dates[i] > "2003"][:20])
