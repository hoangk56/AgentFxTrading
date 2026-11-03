"""Stream MN statistics. Usage: python -I stats.py IS | ALL  [SYM ...]
IS prints only the IS era (read first); ALL prints IS, VAL, 2020-24, years, symbols, stress, late, random percentiles."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
IS_END_MIN = 1640995200 // 60
CELLS = ("n2_TPV", "n2_2R", "n3_TPV", "n3_2R")
VAL_MONTHS, HOLD_MONTHS = 36, 22


def ct(x, day):
    """Mean, t clustered by UTC day, n."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 3:
        return np.nan, np.nan, n
    m = x.mean()
    _, inv = np.unique(day, return_inverse=True)
    r = np.bincount(inv, weights=x - m)
    se = np.sqrt((r ** 2).sum()) / n
    return m, (m / se if se > 0 else np.nan), n


def group_t(g, day, x, ng):
    """Clustered t per group g (0..ng-1)."""
    key = g.astype(np.int64) * 100000 + day
    uk, inv = np.unique(key, return_inverse=True)
    s = np.bincount(inv, weights=x)
    c = np.bincount(inv)
    gk = uk // 100000
    N = np.bincount(gk, weights=c, minlength=ng)
    S = np.bincount(gk, weights=s, minlength=ng)
    m = S / np.maximum(N, 1)
    res = s - c * m[gk]
    se = np.sqrt(np.bincount(gk, weights=res ** 2, minlength=ng)) / np.maximum(N, 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return m / se, N


def era_mask(mins, era):
    if era == "IS":
        return mins < IS_END_MIN
    if era == "VAL":
        return mins >= IS_END_MIN
    return np.ones(len(mins), bool)


def load(syms):
    real, rand = {}, {}
    for s in syms:
        z = np.load(os.path.join(OUT, f"{s}_real.npz"))
        real[s] = {c: {k.split("__")[1]: z[k] for k in z.files if k.startswith(c + "__")} for c in CELLS}
        r = np.load(os.path.join(OUT, f"{s}_rand.npz"))
        rand[s] = {k: r[k] for k in r.files}
    return real, rand


def pooled(real, cell, field="net"):
    x, mins, sym = [], [], []
    for s, d in real.items():
        x.append(d[cell][field])
        mins.append(d[cell]["min"])
        sym.append(np.full(len(d[cell]["min"]), s))
    return np.concatenate(x), np.concatenate(mins), np.concatenate(sym)


def rand_t(rand, era, ndraw=200):
    """t per (draw, cell), pooled over symbols."""
    g, day, x = [], [], []
    for s, r in rand.items():
        m = era_mask(r["min"], era)
        g.append(r["draw"][m].astype(np.int64) * 4 + r["cell"][m])
        day.append(r["min"][m] // 1440)
        x.append(r["net"][m].astype(float))
    t, n = group_t(np.concatenate(g), np.concatenate(day), np.concatenate(x), ndraw * 4)
    return t.reshape(ndraw, 4), n.reshape(ndraw, 4)


def line(name, x, mins, R=None):
    m, t, n = ct(x, mins // 1440)
    rr = f" {np.mean(x / R):+.3f}R" if R is not None and n else ""
    return f"{name:<28} n {n:>5}  net {m:+7.2f} bp{rr}  t {t:+5.2f}"


def main():
    mode = sys.argv[1]
    syms = sys.argv[2:] or ["BTCUSDT", "ETHUSDT"]
    real, rand = load(syms)
    eras = ["IS"] if mode == "IS" else ["IS", "VAL", "ALL"]
    rt = {e: rand_t(rand, e) for e in eras}
    print(f"symbols: {' '.join(syms)}")
    for e in eras:
        print(f"\n=== era {e} (pooled) ===")
        tr = []
        for ci, c in enumerate(CELLS):
            x, mins, sym = pooled(real, c)
            R, _, _ = pooled(real, c, "R")
            msk = era_mask(mins, e)
            m, t, n = ct(x[msk], mins[msk] // 1440)
            tr.append(t)
            rts = rt[e][0][:, ci]
            pct = 100 * np.mean(rts < t)
            sd = x[msk].std()
            st, _, _ = pooled(real, c, "stress")
            lt_, _, _ = pooled(real, c, "late")
            ms, ts, _ = ct(st[msk], mins[msk] // 1440)
            ml, tl, _ = ct(lt_[msk], mins[msk] // 1440)
            typ, _, _ = pooled(real, c, "typ")
            sh = [np.mean(typ[msk] == k) for k in (0, 1, 2)]
            print(f"{line(c, x[msk], mins[msk], R[msk])}  sd {sd:6.1f}  win {np.mean(x[msk] > 0):.2f}  "
                  f"stop/tp/time {sh[0]:.2f}/{sh[1]:.2f}/{sh[2]:.2f}  R {np.median(R[msk]):.0f}bp  "
                  f"rand pct {pct:5.1f} (rand t med {np.nanmedian(rts):+.2f}, 95% {np.nanpercentile(rts, 95):+.2f}, "
                  f"rand n med {np.median(rt[e][1][:, ci]):.0f})")
            print(f"{'':<28} stress x1.5 net {ms:+7.2f} t {ts:+5.2f} | one step late net {ml:+7.2f} t {tl:+5.2f}")
            if e == "VAL":
                months = VAL_MONTHS
                hold_n = n / months * HOLD_MONTHS
                print(f"{'':<28} power at VAL size = {m / sd:+.4f} x sqrt({hold_n:.0f}) = "
                      f"{m / sd * np.sqrt(hold_n):+.2f}; HOLD t at 1/4 of VAL size ~ "
                      f"{m / 4 / sd * np.sqrt(hold_n):+.2f}")
            for s in syms:
                ms_ = msk & (sym == s)
                print("   " + line(s, x[ms_], mins[ms_], R[ms_]))
        best = int(np.nanargmax(tr))
        mx = np.nanmax(rt[e][0], axis=1)
        print(f"best cell {CELLS[best]} t {tr[best]:+.2f}; max-over-4-cells random null: median {np.nanmedian(mx):+.2f}, "
              f"95% {np.nanpercentile(mx, 95):+.2f}; real best beats {100 * np.mean(mx < tr[best]):.1f}% of draws")
    if mode != "IS":
        print("\n=== years (pooled net bp, t) ===")
        for c in CELLS:
            x, mins, _ = pooled(real, c)
            yb = np.array([1577836800, 1609459200, 1640995200, 1672531200, 1704067200]) // 60
            yr = 2019 + np.searchsorted(yb, mins, side="right")
            parts = []
            for y in range(2020, 2025):
                k = yr == y
                m, t, n = ct(x[k], mins[k] // 1440)
                parts.append(f"{y}: {m:+6.2f} ({t:+.2f}, {n})")
            npos = sum(1 for y in range(2020, 2025) if x[yr == y].mean() > 0)
            print(f"{c:<8} " + "  ".join(parts) + f"  positive {npos}/5")


if __name__ == "__main__":
    main()
