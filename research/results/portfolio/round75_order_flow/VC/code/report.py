"""Pool VC outputs. Usage: python -I report.py <eras: IS or IS,VAL> <SYM,SYM,...>  -> prints tables."""
import json
import os
import sys

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
IS_END = 1640995200 // 60
VAL_END = 1735689600 // 60
CELLS = [f"{s}_c{c}_{t}" for s in ("trend", "rej") for c in (2, 3) for t in ("TPV", "2R")]
Y0 = 1577836800 // 60  # 2020-01-01


def year_of(t0):
    # epoch minutes -> calendar year (UTC), exact via numpy datetime64
    return (t0.astype("datetime64[m]").astype("datetime64[Y]").astype(int) + 1970)


def era_mask(t0, era):
    if era == "IS":
        return t0 < IS_END
    if era == "VAL":
        return (t0 >= IS_END) & (t0 < VAL_END)
    return t0 < VAL_END


def tstat(t0, x):
    """Mean / CR1 standard error clustered by UTC day."""
    n = len(x)
    if n < 3:
        return np.nan
    day = (t0 // 1440).astype(np.int64)
    m = x.mean()
    ud, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m)
    G = len(ud)
    if G < 2:
        return np.nan
    se = np.sqrt((g ** 2).sum() * G / (G - 1)) / n
    return m / se if se > 0 else np.nan


def load(syms):
    real, rand = {}, {}
    for s in syms:
        z = np.load(os.path.join(OUT, f"{s}_real.npz"))
        real[s] = {k: z[k] for k in z.files}
        p = os.path.join(OUT, f"{s}_rand.npz")
        if os.path.exists(p):
            z = np.load(p)
            rand[s] = {k: z[k] for k in z.files}
    return real, rand


def pool(real, syms, key):
    parts = [np.c_[real[s][key], np.full(len(real[s][key]), i)] for i, s in enumerate(syms)]
    return np.concatenate(parts) if parts else np.zeros((0, 6))


def summ(a, era):
    a = a[era_mask(a[:, 0], era)]
    if len(a) == 0:
        return dict(n=0)
    t0, net, fees, rbp, kind = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
    r = net / rbp
    x15 = net - 0.5 * fees
    return dict(n=len(a), days=len(np.unique(t0 // 1440)), net=net.mean(), t=tstat(t0, net), R=r.mean(),
                sdR=r.std(ddof=1) if len(r) > 1 else np.nan, sd=net.std(ddof=1) if len(r) > 1 else np.nan,
                stopR=rbp.mean(), win=(net > 0).mean(), tp=(kind == 1).mean(), st=(kind == 0).mean(),
                tm=(kind == 2).mean(), net15=x15.mean(), t15=tstat(t0, x15),
                power=(net.mean() / net.std(ddof=1)) * np.sqrt(len(a) * 22 / 36) if len(a) > 1 else np.nan)


def rand_t(rand, syms, key, era, n_draws):
    """Pooled net t per draw."""
    out = np.full(n_draws, np.nan)
    if not all(s in rand for s in syms):
        return None
    arrs = [rand[s][key] for s in syms]
    for dr in range(n_draws):
        parts = [a[a[:, 0] == dr] for a in arrs]
        p = np.concatenate(parts)
        p = p[era_mask(p[:, 1], era)]
        out[dr] = tstat(p[:, 1], p[:, 2])
    return out


def fmt(d, keys=("n", "days", "net", "t", "R", "win", "tp", "st", "tm", "net15", "t15", "stopR", "power")):
    if d.get("n", 0) == 0:
        return "n 0"
    f = []
    for k in keys:
        v = d[k]
        f.append(f"{k} {v:.0f}" if k in ("n", "days") else (f"{k} {v:.2f}" if k in ("t", "t15", "R", "win", "tp", "st", "tm", "power") else f"{k} {v:.1f}"))
    return " | ".join(f)


def main():
    eras = sys.argv[1].split(",")
    syms = sys.argv[2].split(",")
    real, rand = load(syms)
    n_draws = None
    if rand:
        n_draws = int(max(rand[s][CELLS[0]][:, 0].max() for s in rand) + 1)
    res = {}
    for era in eras:
        print(f"\n===== {era} pooled {syms}")
        for c in CELLS:
            a = pool(real, syms, c)
            d = summ(a, era)
            late = summ(pool(real, syms, c + "_late"), era)
            line = f"{c:16s} {fmt(d)} || late net {late.get('net', np.nan):.1f} t {late.get('t', np.nan):.2f}"
            if n_draws:
                rt = rand_t(rand, syms, c, era, n_draws)
                if rt is not None and d.get("n", 0):
                    pct = 100 * np.mean(rt < d["t"])
                    line += f" || rand pct {pct:.1f} (rand t med {np.nanmedian(rt):.2f}, p95 {np.nanpercentile(rt, 95):.2f})"
                    d["rand_pct"] = pct
                    d["rand_t"] = rt.tolist()
            d["late_net"], d["late_t"] = late.get("net"), late.get("t")
            res[f"{era}|{c}"] = d
            print(line)
        if n_draws:
            mx = np.full(n_draws, -np.inf)
            for c in CELLS:
                mx = np.fmax(mx, np.array(res[f"{era}|{c}"].get("rand_t", [np.nan] * n_draws)))
            print(f"max-over-8-cells null {era}: p50 {np.nanpercentile(mx, 50):.2f} p90 {np.nanpercentile(mx, 90):.2f} "
                  f"p95 {np.nanpercentile(mx, 95):.2f}")
        print(f"--- {era} per symbol")
        for c in CELLS:
            print(c, " ; ".join(f"{s[:3]} " + fmt(summ(real[s][c], era), ("n", "net", "t", "R")) for s in syms))
        print(f"--- {era} per year (pooled)")
        for c in CELLS:
            a = pool(real, syms, c)
            a = a[era_mask(a[:, 0], era)]
            y = year_of(a[:, 0].astype(np.int64))
            print(c, " ; ".join(f"{yy}: n {int((y == yy).sum())} net {a[y == yy, 1].mean():.1f}" for yy in np.unique(y)))
    with open(os.path.join(OUT, f"report_{'_'.join(eras)}_{len(syms)}sym.json"), "w") as fh:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "rand_t"} for k, v in res.items()}, fh, indent=1,
                  default=float)


if __name__ == "__main__":
    main()
