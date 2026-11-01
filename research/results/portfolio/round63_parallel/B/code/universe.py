"""Stream B: point-in-time universe = top-N USDT-M perps by trailing 30-day perp quote volume, listed >= 60 days,
with a Binance spot pair (spot_first.csv) live that day, stablecoins excluded. Uses perp 1d data only (no returns).
Cut at 2025-01-01."""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "round58_unconstrained_carry", "code"))
from carry import spot_name, trailing_mean, T0, DAY  # noqa

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "data", "binance")
END = 1735689600000
STABLE = {"USDC", "BUSD", "TUSD", "USDP", "FDUSD", "DAI", "EUR", "GBP", "AEUR", "USDE", "PAXG", "BTCDOM"}


def load_daily():
    syms = sorted(f[:-4] for f in os.listdir(os.path.join(DATA, "perp_1d")) if f.endswith("USDT.csv"))
    sf = {}
    with open(os.path.join(DATA, "spot_first.csv")) as f:
        for row in csv.reader(f):
            try:
                sf[row[0]] = int(row[1])
            except ValueError:
                pass
    nd = (END - T0) // DAY
    keep, QV = [], []
    for s in syms:
        sp, fac = spot_name(s)
        if sp not in sf or sp[:-4] in STABLE or s[:-4] in STABLE:
            continue
        q = np.full(nd, np.nan)
        with open(os.path.join(DATA, "perp_1d", s + ".csv")) as f:
            r = csv.reader(f); next(r)
            for row in r:
                d = (int(row[0]) - T0) // DAY
                if 0 <= d < nd:
                    q[d] = float(row[6])
        keep.append((s, sp, fac, sf[sp]))
        QV.append(q)
    return keep, np.array(QV)


def universe(N=60, min_age=60):
    keep, QV = load_daily()
    n, nd = QV.shape
    first = np.array([np.argmax(~np.isnan(q)) if (~np.isnan(q)).any() else nd for q in QV])
    days = T0 + DAY * np.arange(nd)
    spot_ok = np.array([k[3] for k in keep])[:, None] <= days[None, :]
    age_ok = np.arange(nd)[None, :] - first[:, None] >= min_age
    tv = trailing_mean(QV, 30)
    tv = np.where(spot_ok & age_ok & ~np.isnan(QV) & ~np.isnan(tv), tv, -np.inf)
    U = np.zeros((n, nd), bool)
    R = np.full((n, nd), 9999)
    for d in range(nd):
        o = np.argsort(-tv[:, d])
        g = o[np.isfinite(tv[o, d])][:N]
        U[g, d] = True
        R[g, d] = np.arange(len(g))
    return keep, U, R, days


if __name__ == "__main__":
    keep, U, R, days = universe(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
    d0 = np.searchsorted(days, 1577836800000)
    ever = U[:, d0:].any(1)
    print("ever in universe 2020-24:", ever.sum())
    print("member-days:", U[:, d0:].sum())
    for y0, y1 in ((1577836800000, 1609459200000), (1609459200000, 1640995200000), (1640995200000, 1672531200000),
                   (1672531200000, 1704067200000), (1704067200000, 1735689600000)):
        a, b = np.searchsorted(days, y0), np.searchsorted(days, y1)
        print(y0, "mean members/day", U[:, a:b].sum(0).mean().round(1), "ever", U[:, a:b].any(1).sum())
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            for i in np.where(ever)[0]:
                k = keep[i]
                w = np.where(U[i, d0:])[0] + d0
                f.write(f"{k[0]},{k[1]},{k[2]:g},{int(days[w[0]])},{int(days[w[-1]] + DAY)}\n")
