"""Stream CG report: declared cells, eras, years, costs, late, splits, random benchmarks (../HYPOTHESES_CG.md)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gap  # noqa: E402

CELLS = [("G2_1d", 0.02, 1440), ("G2_3d", 0.02, 4320), ("G4_1d", 0.04, 1440), ("G4_3d", 0.04, 4320)]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")


def fmt(c):
    x = c["x"]
    if len(x) < 3:
        return f"n {len(x)}"
    return (f"n {len(x):3d} cl {len(np.unique(c['g'])):3d} net {x.mean():+7.1f} t {gap.cl_t(x, c['g']):+5.2f} "
            f"gross {c['gross'].mean():+7.1f} fund {c['fund'].mean():+5.1f} hit {c['hit'].mean():.2f} "
            f"hold {c['hrs'].mean():4.1f}h sd {x.std(ddof=1):5.0f} closed {c['nclosed']}")


def main():
    os.makedirs(OUT, exist_ok=True)
    S = {s: gap.load(s) for s in ("BTCUSDT", "ETHUSDT")}
    real = gap.run(S, gap.real_anchors())
    # event list (small csv; contains no 2025-26 data)
    with open(os.path.join(OUT, "events.csv"), "w") as fh:
        fh.write("sym,friday,m_pct,side,g3d_bp,f3d_bp,hit3d,hrs3d,g1d_bp,f1d_bp,hit1d\n")
        for sym, f, r in real:
            v = r[0]
            if v == "closed":
                fh.write(f"{sym},{f},{100 * r['m']:.3f},{r['s']:+.0f},closed,,,,,,\n")
                continue
            a, b = v[4320], v[1440]
            fh.write(f"{sym},{f},{100 * r['m']:.3f},{r['s']:+.0f},{a[0]:.1f},{a[1]:.1f},{a[2]},{a[3]:.1f},"
                     f"{b[0]:.1f},{b[1]:.1f},{b[2]}\n")

    print("=== declared cells (pooled BTC + ETH, cost 12 bp RT, funding incl.) ===")
    res = {}
    for name, k, H in CELLS:
        for e in ("IS", "VAL"):
            for lab, kw in (("base", {}), ("x1.5", {"cmult": 1.5}), ("late", {"late": 1}),
                            ("late+x1.5", {"late": 1, "cmult": 1.5})):
                c = gap.cell(real, k, H, era_=e, **kw)
                res[(name, e, lab)] = c
                print(f"{name:6s} {e:3s} {lab:10s} {fmt(c)}")
        print()

    print("=== by year (base) ===")
    for name, k, H in CELLS:
        c = gap.cell(real, k, H)
        line = []
        for y in range(2020, 2025):
            m = c["yr"] == y
            line.append(f"{y}: {c['x'][m].mean():+6.0f} (n {m.sum():2d})" if m.sum() else f"{y}: -")
        pos = sum(1 for y in range(2020, 2025) if (c["yr"] == y).sum() and c["x"][c["yr"] == y].mean() > 0)
        print(f"{name:6s} " + " | ".join(line) + f"  positive years {pos}/5")
    print()

    print("=== split by coin (base, information) ===")
    for name, k, H in CELLS:
        for sym in ("BTCUSDT", "ETHUSDT"):
            rr = [r for r in real if r[0] == sym]
            for e in ("IS", "VAL"):
                print(f"{name:6s} {sym} {e:3s} {fmt(gap.cell(rr, k, H, era_=e))}")
    print()

    print("=== sign split (base, pooled IS+VAL): fade after weekend rally (short) vs after drop (long) ===")
    for name, k, H in CELLS:
        for sd in (-1, 1):
            rr = [r for r in real if r[2]["s"] == sd]
            for e in ("IS", "VAL"):
                print(f"{name:6s} side {sd:+d} {e:3s} {fmt(gap.cell(rr, k, H, era_=e))}")
    print()

    print("=== power at VAL size ===")
    for name, k, H in CELLS:
        c = res[(name, "VAL", "base")]
        x = c["x"]
        S_ = x.mean() / x.std(ddof=1)
        nH = 0.61 * len(x)
        tv = gap.cl_t(x, c["g"])
        print(f"{name:6s} S/trade {S_:+.3f} n_H {nH:5.1f} power {S_ * np.sqrt(nH):+.2f} "
              f"clustered power t_VAL*sqrt(.61) {tv * np.sqrt(0.61):+.2f}  needed S {3 / np.sqrt(nH):.2f}")
    print()

    print("=== random benchmark (a): weekday 16:00 CT anchors, 49 h pseudo gap ===")
    wk = {}
    for wd, nm in enumerate(("Mon", "Tue", "Wed", "Thu")):
        wk[nm] = gap.run(S, gap.weekday_anchors(wd))
    for name, k, H in CELLS:
        for e in ("IS", "VAL"):
            rm = res[(name, e, "base")]["x"].mean()
            s = " ".join(f"{nm} {gap.cell(wk[nm], k, H, era_=e)['x'].mean():+6.1f}" for nm in wk)
            beat = np.mean([gap.cell(wk[nm], k, H, era_=e)["x"].mean() < rm for nm in wk])
            print(f"{name:6s} {e:3s} real {rm:+6.1f} | {s} | beats {beat:.2f}")
    print()

    print("=== random benchmark (b): hour-of-week placebo, 49 h pseudo gap ===")
    excl = set(range(94, 142))      # within 24 h of the Friday close (Mon 00 UTC + ~117.5 h)
    anchors = [a for a in range(168) if a not in excl]
    pl = {}
    for a in anchors:
        pl[a] = gap.run(S, gap.how_anchors(a))
    for e in ("IS", "VAL"):
        best_real, best_pl = -1e9, []
        mat = np.full((len(anchors), len(CELLS)), np.nan)
        for j, (name, k, H) in enumerate(CELLS):
            rm = res[(name, e, "base")]["x"].mean()
            best_real = max(best_real, rm)
            v = np.array([gap.cell(pl[a], k, H, era_=e)["x"].mean() if len(gap.cell(pl[a], k, H, era_=e)["x"])
                          else np.nan for a in anchors])
            mat[:, j] = v
            print(f"{name:6s} {e:3s} real {rm:+6.1f} placebo median {np.nanmedian(v):+6.1f} "
                  f"p90 {np.nanpercentile(v, 90):+6.1f} random % {100 * np.nanmean(v < rm):5.1f} (n anchors {len(v)})")
        bp = np.nanmax(mat, axis=1)
        print(f"max-over-4 {e}: best real {best_real:+6.1f}, beats {100 * np.nanmean(bp < best_real):.1f} % of anchors' best")
    print()
    print("=== placebo event counts (k = 2 %, IS / VAL, median over anchors) ===")
    for e in ("IS", "VAL"):
        print(e, "real", len(res[("G2_3d", e, "base")]["x"]), "placebo median",
              np.median([len(gap.cell(pl[a], 0.02, 4320, era_=e)["x"]) for a in anchors]))


if __name__ == "__main__":
    main()
