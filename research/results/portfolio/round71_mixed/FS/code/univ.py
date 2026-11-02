"""Round 71 FS: point-in-time top-40 no-perp spot universe from daily quote volume (no prices).

U[i, d] (d = days since 2020-01-01): pair i eligible on day d (no USDT-M perp of the coin with first day <= d) with all
30 daily klines d-30..d-1 present, and in the top 40 of eligible pairs by mean quote volume over d-30..d-1.
Writes data/spot_wicks/univ.npz and pull_list.csv (sym, YYYY-MM) for months with any universe day + BTCUSDT every month.
"""
import datetime as dt
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

D0 = 1572566400000  # 2019-11-01


def main():
    z = np.load(os.path.join(C.DATA, "vol1d.npz"))
    syms = list(z["syms"])
    elig = {s: (b, d) for s, b, d in C.eligible_symbols()}
    nd0 = (C.END - D0) // C.DAY
    off = (C.T0 - D0) // C.DAY
    Q = np.full((len(syms), nd0), np.nan)
    di = (z["t"] - D0) // C.DAY
    k = (di >= 0) & (di < nd0)
    Q[z["sym"][k], di[k]] = z["qv"][k]
    ok = np.isfinite(Q)
    cs = np.concatenate([np.zeros((len(syms), 1)), np.cumsum(np.where(ok, Q, 0), 1)], 1)
    cn = np.concatenate([np.zeros((len(syms), 1)), np.cumsum(ok, 1)], 1)
    U = np.zeros((len(syms), C.ND), bool)
    RK = np.full((len(syms), C.ND), -1, np.int16)
    pfd = np.array([elig[s][1] for s in syms])
    for d in range(C.ND):
        j = d + off  # index in Q of day d
        n30 = cn[:, j] - cn[:, j - 30]
        m30 = (cs[:, j] - cs[:, j - 30]) / 30
        e = (n30 == 30) & (pfd > d)
        idx = np.where(e)[0]
        o = idx[np.argsort(-m30[idx], kind="stable")][:40]
        U[o, d] = True
        RK[o, d] = np.arange(len(o))
    days = C.T0 + C.DAY * np.arange(C.ND)
    ym = np.array([dt.datetime.fromtimestamp(x / 1000, dt.timezone.utc).strftime("%Y-%m") for x in days])
    pairs = set()
    for i, s in enumerate(syms):
        for m in np.unique(ym[U[i]]):
            pairs.add((s, m))
    for m in np.unique(ym):
        pairs.add(("BTCUSDT", m))
    pairs = sorted(pairs, key=lambda p: (p[1], p[0]))
    np.savez(os.path.join(C.DATA, "univ.npz"), U=U, rank=RK, syms=np.array(syms))
    with open(os.path.join(C.DATA, "pull_list.csv"), "w") as f:
        f.write("sym,month\n")
        for s, m in pairs:
            f.write(f"{s},{m}\n")
    yr = Counter(m[:4] for _, m in pairs)
    print("symbol-months", len(pairs), dict(sorted(yr.items())), "symbols", len({s for s, _ in pairs}))
    print("universe size per day: min", U.sum(0).min(), "median", np.median(U.sum(0)), "max", U.sum(0).max())
    for y in range(2020, 2025):
        w = np.array([m.startswith(str(y)) for m in ym])
        print(y, "mean size", U[:, w].sum(0).mean().round(1), "distinct", int(U[:, w].any(1).sum()),
              "median 30d qv of rank 39 ($M)", end=" ")
        v = []
        for d in np.where(w)[0][::30]:
            j = d + off
            m30 = (cs[:, j] - cs[:, j - 30]) / 30
            r = np.where(RK[:, d] == RK[:, d].max())[0]
            if len(r):
                v.append(m30[r[0]] / 1e6)
        print(np.round(np.median(v), 2) if v else "na")


if __name__ == "__main__":
    main()
