"""Round 75 stream TF statistics. Usage: stats.py ERAS [SYMS]   e.g. stats.py IS  or  stats.py IS,VAL BTCUSDT,ETHUSDT,SOLUSDT
Reads ../out/<SYM>_trades.npz. Prints tables (markdown) for the requested eras only."""
import os
import sys

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
IS_END = 1640995200 // 60
CELLS = [(5, "TPV"), (5, "2R"), (10, "TPV"), (10, "2R")]


def tstat(x, day):
    n = len(x)
    if n < 3:
        return np.nan
    m = x.mean()
    ud, inv = np.unique(day, return_inverse=True)
    G = len(ud)
    S = np.bincount(inv, weights=x - m)
    var = G / max(G - 1, 1) * (S ** 2).sum()
    return x.sum() / np.sqrt(var) if var > 0 else np.nan


def era_mask(fmin, era):
    return fmin < IS_END if era == "IS" else fmin >= IS_END


def get(z, R, tp, mode, who, f):
    return z[f"R{R}_{tp}_{mode}_{who}_{f}"]


def pooled(zs, R, tp, mode, who, era, fee_mul=1.0):
    xs, ds, rs = [], [], []
    for z in zs:
        fm = get(z, R, tp, mode, who, "fmin")
        k = era_mask(fm, era)
        net = get(z, R, tp, mode, who, "net")[k] - (fee_mul - 1) * get(z, R, tp, mode, who, "fee")[k]
        xs.append(net); ds.append(fm[k] // 1440); rs.append(get(z, R, tp, mode, who, "rbp")[k])
    x, d, r = np.concatenate(xs), np.concatenate(ds), np.concatenate(rs)
    return x, d, r


def years(fmin):
    import time
    return np.array([time.gmtime(int(m) * 60).tm_year for m in fmin], dtype=int)


def main():
    eras = sys.argv[1].split(",")
    syms = sys.argv[2].split(",") if len(sys.argv) > 2 else ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    zs = [np.load(os.path.join(OUT, f"{s}_trades.npz")) for s in syms]
    ndraw = 1 + max(int(k.split("_")[3][1:]) for k in zs[0].files if "_d" in k and k.split("_")[3].startswith("d"))
    print(f"symbols {syms}, draws {ndraw}\n")
    for era in eras:
        print(f"## {era}\n")
        print("| cell | n | trades/day | net bp | net R | sd R | t | fees x1.5 t (net) | late t (net) | years +/all | random pct | rnd median t |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        best = None
        rand_t = np.zeros((ndraw, len(CELLS)))
        real_t = []
        for ci, (R, tp) in enumerate(CELLS):
            x, d, r = pooled(zs, R, tp, "base", "real", era)
            t = tstat(x, d)
            xs, _, _ = pooled(zs, R, tp, "base", "real", era, 1.5)
            xl, dl, _ = pooled(zs, R, tp, "late", "real", era)
            fm = np.concatenate([get(z, R, tp, "base", "real", "fmin")[era_mask(get(z, R, tp, "base", "real", "fmin"), era)] for z in zs])
            yy = years(fm)
            ys = [x[yy == y].sum() for y in np.unique(yy)]
            for dr in range(ndraw):
                xr, drr, _ = pooled(zs, R, tp, "base", f"d{dr}", era)
                rand_t[dr, ci] = tstat(xr, drr)
            pct = 100 * np.mean(rand_t[:, ci] < t)
            span = (fm.max() - fm.min()) / 1440 if len(fm) else np.nan
            xR = x / r
            real_t.append(t)
            print(f"| R{R} {tp} | {len(x)} | {len(x) / span / len(syms):.2f}/sym | {x.mean():+.2f} | {xR.mean():+.3f} | {xR.std():.2f} | {t:+.2f} | "
                  f"{tstat(xs, d):+.2f} ({xs.mean():+.2f}) | {tstat(xl, dl):+.2f} ({xl.mean():+.2f}) | "
                  f"{sum(v > 0 for v in ys)}/{len(ys)} | {pct:.1f} | {np.median(rand_t[:, ci]):+.2f} |")
        mx = rand_t.max(1)
        bi = int(np.nanargmax(real_t))
        print(f"\nmax-over-4-cells null: best real cell {CELLS[bi]} t {real_t[bi]:+.2f}; random max t median {np.median(mx):+.2f}, "
              f"95th {np.percentile(mx, 95):+.2f}; real best beats {100 * np.mean(mx < real_t[bi]):.1f} % of draws\n")
        # per symbol
        print("| cell | " + " | ".join(f"{s} n / net bp / t" for s in syms) + " |")
        print("|---|" + "---|" * len(syms))
        for R, tp in CELLS:
            row = []
            for z in zs:
                x, d, _ = pooled([z], R, tp, "base", "real", era)
                row.append(f"{len(x)} / {x.mean():+.2f} / {tstat(x, d):+.2f}")
            print(f"| R{R} {tp} | " + " | ".join(row) + " |")
        # per year
        print("\n| cell | " + "per year: n / net bp / t" + " |\n|---|---|")
        for R, tp in CELLS:
            x, d, _ = pooled(zs, R, tp, "base", "real", era)
            fm = np.concatenate([get(z, R, tp, "base", "real", "fmin")[era_mask(get(z, R, tp, "base", "real", "fmin"), era)] for z in zs])
            yy = years(fm)
            parts = [f"{y}: {np.sum(yy == y)} / {x[yy == y].mean():+.1f} / {tstat(x[yy == y], d[yy == y]):+.2f}" for y in np.unique(yy)]
            print(f"| R{R} {tp} | " + "; ".join(parts) + " |")
        # information: side of the big trades x test direction
        print("\n| cell | zone side | direction | n | net bp | t |\n|---|---|---|---|---|---|")
        for R, tp in CELLS:
            X, Dd, NB, NS, DI = [], [], [], [], []
            for z in zs:
                fm = get(z, R, tp, "base", "real", "fmin")
                k = era_mask(fm, era)
                X.append(get(z, R, tp, "base", "real", "net")[k]); Dd.append(fm[k] // 1440)
                NB.append(get(z, R, tp, "base", "real", "nbuy")[k]); NS.append(get(z, R, tp, "base", "real", "nsell")[k])
                DI.append(get(z, R, tp, "base", "real", "dirn")[k])
            X, Dd, NB, NS, DI = map(np.concatenate, (X, Dd, NB, NS, DI))
            side = np.where(NS == 0, "buy", np.where(NB == 0, "sell", "mixed"))
            for sd in ("buy", "sell", "mixed"):
                for di, dn in ((1, "long (support)"), (-1, "short (resistance)")):
                    k = (side == sd) & (DI == di)
                    if k.sum():
                        print(f"| R{R} {tp} | {sd} | {dn} | {k.sum()} | {X[k].mean():+.2f} | {tstat(X[k], Dd[k]):+.2f} |")
        # exit mix and power
        print("\n| cell | stop % | TP % | time % | mean R stop (bp) | power at VAL-size (HOLD n = pace x 22/36) | power at 1/4 size |\n|---|---|---|---|---|---|---|")
        for R, tp in CELLS:
            x, d, r = pooled(zs, R, tp, "base", "real", era)
            kind = np.concatenate([get(z, R, tp, "base", "real", "kind")[era_mask(get(z, R, tp, "base", "real", "fmin"), era)] for z in zs])
            nyears = 2.0 if era == "IS" else 3.0
            hold_n = len(x) / (nyears * 12) * 22
            pw = x.mean() / x.std() * np.sqrt(hold_n)
            print(f"| R{R} {tp} | {100 * np.mean(kind == 1):.0f} | {100 * np.mean(kind == 2):.0f} | {100 * np.mean(kind == 0):.0f} | {r.mean():.1f} | {pw:+.2f} (HOLD n {hold_n:.0f}) | {pw / 4:+.2f} |")
        print()


if __name__ == "__main__":
    main()
