"""Stream O: point-in-time universe (top-40 by trailing 30-d perp quote volume, round 63 C xs.daily_universe) and
the coin-day lists to pull from data.binance.vision metrics. Prices only (no metrics, no returns)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "C", "code"))
import xs  # noqa: E402

D0 = (1640995200000 - xs.H0) // xs.DAY   # 2022-01-01 day index
D1 = (xs.END - xs.H0) // xs.DAY          # 2025-01-01 exclusive


def alt_universe(Pn, K=20):
    """[n, nd] bool: the K highest-volume coins of the top-40 excluding BTCUSDT (so ETH + 19 alts)."""
    U, rk = xs.daily_universe(Pn)
    iB = Pn["syms"].index("BTCUSDT")
    A = np.zeros_like(U)
    for d in range(U.shape[1]):
        idx = np.where(U[:, d] & (np.arange(U.shape[0]) != iB))[0]
        idx = idx[np.argsort(rk[idx, d])][:K]
        A[idx, d] = True
    return A, rk


if __name__ == "__main__":
    Pn = xs.load()
    A, rk = alt_universe(Pn, int(sys.argv[1]) if len(sys.argv) > 1 else 20)
    P = Pn["P"]
    r = P[:, 1:] / P[:, :-1] - 1   # r[:, h-1] = return of the bar ending at instant h
    nd = A.shape[1]
    syms = Pn["syms"]
    for p in (0.02, 0.03, 0.04, 0.05):
        cnt = 0
        for d in range(D0, D1):
            h0 = d * 24
            seg = r[:, h0 + 1:h0 + 24]   # bars ending at 02:00..24:00? keep simple count
            hit = np.nanmin(np.where(np.isnan(seg), 0, seg), axis=1) <= -p
            cnt += int((hit & A[:, d]).sum())
        print("p", p, "coin-days with an hourly drop", cnt)
    alt = sorted(d for d in range(D0, D1) if (d - D0) % 2 == 0)
    pairs = set()
    for d in alt:
        for i in np.where(A[:, d])[0]:
            pairs.add((i, d))
    print("tier A coin-days (every 2nd day)", len(pairs), "symbols", len({i for i, _ in pairs}))
