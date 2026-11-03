"""Round 75 stream AB report: pool the per-symbol outputs of ab.py.

    report.py IS          -> IS tables only (read first)
    report.py ALL         -> IS + VAL, years, symbols, costs x1.5, one step late, random percentiles, power
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
SYMS = [s for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT") if os.path.exists(os.path.join(OUT, f"{s}_rand.npz"))]
IS_DAYS = 731  # 2020-01-01 .. 2021-12-31
CELLS = [f"{c}_m{m}_{tp}" for c in ("C1", "C2", "BON") for m in (4, 8) for tp in ("TPV", "2R")]
CTRLS = ["N0_TPV", "N0_2R", "N0m_TPV", "N0m_2R"]
ALLC = CELLS + CTRLS
YEARS = np.array([np.datetime64("2020-01-01") + np.timedelta64(int(d), "D") for d in range(1827)]).astype(
    "datetime64[Y]").astype(int) + 1970


def tstat_days(day, x):
    if len(x) < 2:
        return np.nan
    S = np.bincount(day, weights=x)
    n = np.bincount(day).astype(float)
    g = n > 0
    mu = S.sum() / n.sum()
    G = g.sum()
    var = np.sum((S[g] - n[g] * mu) ** 2) / n.sum() ** 2 * G / max(G - 1, 1)
    return mu / np.sqrt(var) if var > 0 else np.nan


def tstat_sums(S, n):
    """S, n: (..., days). Clustered t along the last axis."""
    N = n.sum(-1)
    mu = S.sum(-1) / np.maximum(N, 1)
    G = (n > 0).sum(-1)
    var = ((S - n * mu[..., None]) ** 2).sum(-1) / np.maximum(N, 1) ** 2 * G / np.maximum(G - 1, 1)
    return np.where(var > 0, mu / np.sqrt(np.where(var > 0, var, 1)), np.nan)


def load_real():
    rec = {}
    for s in SYMS:
        z = np.load(os.path.join(OUT, f"{s}_real.npz"))
        off = int(z["off"])
        for v in ("base", "late", "eslip"):
            for c in ALLC:
                g = lambda f: z[f"{v}|{c}|{f}"]
                rec[(s, v, c)] = dict(day=g("e") // 1440 + off, gross=g("gross"), fund=g("fund"), fee=g("fee"),
                                      R=g("R"), kind=g("kind"), lev=g("lev"), side=g("side"))
    return rec


def pooled(rec, v, c, syms, era, mult=1.0, lev=None, side=None):
    days, net, R = [], [], []
    for s in syms:
        r = rec[(s, v, c)]
        m = (r["day"] < IS_DAYS) if era == "IS" else (r["day"] >= IS_DAYS) if era == "VAL" else np.ones(len(r["day"]), bool)
        if lev is not None:
            m &= r["lev"] == lev
        if side is not None:
            m &= r["side"] == side
        x = r["gross"][m] + r["fund"][m] - mult * r["fee"][m]
        days.append(r["day"][m])
        net.append(x)
        R.append(x / r["R"][m])
    return np.concatenate(days), np.concatenate(net), np.concatenate(R)


def stats(d, x, xr):
    n = len(x)
    if n == 0:
        return dict(n=0, net=np.nan, netR=np.nan, t=np.nan, sd=np.nan)
    return dict(n=n, net=x.mean(), netR=xr.mean(), t=tstat_days(d, x), sd=x.std(ddof=1) if n > 1 else np.nan)


def main(mode):
    rec = load_real()
    eras = ["IS"] if mode == "IS" else ["IS", "VAL"]
    lines = [f"symbols pooled: {', '.join(SYMS)}"]
    # random draws: pooled day sums across symbols, (draws, cells, days, 2)
    rs = [np.load(os.path.join(OUT, f"{s}_rand.npz")) for s in SYMS]
    cells = list(rs[0]["cells"])
    nd = min(r["sums"].shape[0] for r in rs)
    sums = sum(r["sums"][:nd].astype(np.float64) for r in rs)
    real = sum(r["real"].astype(np.float64) for r in rs)
    sl = {"IS": slice(0, IS_DAYS), "VAL": slice(IS_DAYS, None)}
    rt = {e: tstat_sums(sums[:, :, sl[e], 0], sums[:, :, sl[e], 1]) for e in eras}  # (draws, cells)
    realt = {e: tstat_sums(real[:, sl[e], 0], real[:, sl[e], 1]) for e in eras}
    lines.append(f"random draws: {nd}")
    hdr = f"{'cell':14s} " + " ".join(
        f"| {e}: {'n':>5s} {'net bp':>7s} {'R':>6s} {'t':>5s} {'x1.5 t':>6s} {'late':>6s} {'late t':>6s} "
        f"{'rnd%':>5s} {'rnd med t':>9s}" for e in eras)
    lines += ["", "Pooled (base costs; x1.5 = fees x1.5; late = one step late; rnd% = percentile of real t among random"
              " levels)", hdr]
    summ = {}
    for c in ALLC:
        row = f"{c:14s} "
        for e in eras:
            st = stats(*pooled(rec, "base", c, SYMS, e))
            s15 = stats(*pooled(rec, "base", c, SYMS, e, mult=1.5))
            sl8 = stats(*pooled(rec, "late", c, SYMS, e))
            ci = cells.index(c)
            pct = 100 * np.mean(rt[e][:, ci] < realt[e][ci])
            summ[(c, e)] = dict(st=st, s15=s15, late=sl8, pct=pct)
            row += (f"| {e}: {st['n']:5d} {st['net']:7.2f} {st['netR']:6.3f} {st['t']:5.2f} {s15['t']:6.2f} "
                    f"{sl8['net']:6.2f} {sl8['t']:6.2f} {pct:5.1f} {np.nanmedian(rt[e][:, ci]):9.2f}")
        lines.append(row)
    # max-over-cells null
    lines += ["", "Max-over-cells null (12 verdict cells): real max t vs the distribution of max t across random draws"]
    ci = [cells.index(c) for c in CELLS]
    for e in eras:
        mx = np.nanmax(rt[e][:, ci], axis=1)
        rm = np.nanmax(realt[e][ci])
        lines.append(f"  {e}: real max t {rm:.2f}; random max t median {np.median(mx):.2f}, 95th {np.percentile(mx, 95):.2f}"
                     f"; real max beats {100 * np.mean(mx < rm):.1f} % of draws")
    # per symbol
    lines += ["", "Per symbol (base): n / net bp / t"]
    for c in ALLC:
        row = f"{c:14s} "
        for e in eras:
            for s in SYMS:
                st = stats(*pooled(rec, "base", c, [s], e))
                row += f"| {e} {s[:3]} {st['n']:5d} {st['net']:7.2f} {st['t']:5.2f} "
        lines.append(row)
    if mode != "IS":
        lines += ["", "Years (pooled base net bp per trade; n)"]
        for c in ALLC:
            d, x, _ = pooled(rec, "base", c, SYMS, "ALL")
            y = YEARS[d]
            parts = [f"{yy}: {x[y == yy].mean():7.2f} ({np.sum(y == yy):4d})" if np.any(y == yy) else f"{yy}: -" for yy in
                     range(2020, 2025)]
            pos = sum(1 for yy in range(2020, 2025) if np.any(y == yy) and x[y == yy].mean() > 0)
            lines.append(f"{c:14s} " + " ".join(parts) + f"  pos {pos}/5")
        lines += ["", "Power at VAL size (net mean / sd x sqrt(n_VAL x 22 / 36)); entry-slip variant net"]
        for c in ALLC:
            st = summ[(c, "VAL")]["st"]
            pw = st["net"] / st["sd"] * np.sqrt(st["n"] * 22 / 36) if st["n"] > 1 else np.nan
            es = [stats(*pooled(rec, "eslip", c, SYMS, e))["net"] for e in eras]
            lines.append(f"{c:14s} VAL n {st['n']:5d} mean {st['net']:7.2f} sd {st['sd']:7.1f} power {pw:5.2f} "
                         f"(HOLD t at 1/4 VAL size ~{pw / 4:5.2f}) | entry-slip net IS {es[0]:6.2f} VAL {es[1]:6.2f}")
    # by level type and side (information)
    lines += ["", "By level (0 POC, 1 VAH, 2 VAL) and side, base net bp / t"]
    for c in ["C1_m4_TPV", "C1_m4_2R", "BON_m4_TPV", "C2_m4_TPV", "N0_TPV", "N0m_TPV"]:
        row = f"{c:14s} "
        for e in eras:
            for lv in range(3):
                st = stats(*pooled(rec, "base", c, SYMS, e, lev=lv))
                row += f"| {e} L{lv} {st['n']:5d} {st['net']:6.2f} {st['t']:5.2f} "
            for sd in (1, -1):
                st = stats(*pooled(rec, "base", c, SYMS, e, side=sd))
                row += f"| {e} {'long' if sd > 0 else 'short'} {st['n']:5d} {st['net']:6.2f} {st['t']:5.2f} "
        lines.append(row)
    # exit mix
    lines += ["", "Exit mix pooled ALL eras (stop / tp / time) and mean R size bp"]
    for c in ALLC:
        k = np.concatenate([rec[(s, "base", c)]["kind"] for s in SYMS])
        R = np.concatenate([rec[(s, "base", c)]["R"] for s in SYMS])
        b = np.bincount(k, minlength=3) / max(len(k), 1)
        lines.append(f"{c:14s} stop {b[0]:.2f} tp {b[1]:.2f} time {b[2]:.2f} R {R.mean():6.1f} bp")
    txt = "\n".join(lines)
    with open(os.path.join(OUT, f"report_{mode}.txt"), "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "IS")
