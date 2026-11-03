"""Pooled tables for stream SI.  python -I analyze.py <ERA> [SYM ...]  (default all three that have outputs)."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
SYMS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CELLS = [("f0", "TPV"), ("f0", "2R"), ("fmed", "TPV"), ("fmed", "2R")]


def ct(x, day):
    """Mean and t clustered by day (CR0)."""
    n = len(x)
    if n < 3:
        return (np.nan, np.nan)
    mu = x.mean()
    ud, inv = np.unique(day, return_inverse=True)
    s = np.bincount(inv, weights=x - mu)
    se = np.sqrt((s ** 2).sum()) / n
    return mu, mu / se if se > 0 else np.nan


def load_real(era, syms):
    R = {}
    for s in syms:
        p = os.path.join(OUT, f"{s}_{era}_real.npz")
        if os.path.exists(p):
            R[s] = dict(np.load(p))
    return R


def get(R, s, tag):
    z = R[s]
    if f"{tag}__net" not in z:
        return None
    return {k.split("__")[1]: v for k, v in z.items() if k.startswith(tag + "__")}


def summarize(tr, stress=False):
    net = tr["gross"] - 1.5 * (tr["slip"] + tr["fee"]) + tr["fund"] if stress else tr["net"]
    day = tr["fill_min"] // 1440
    mu, t = ct(net, day)
    return len(net), mu, t, (net / tr["rbp"]).mean(), net.std(ddof=1) if len(net) > 1 else np.nan


def gross_mean(tr):
    return tr["gross"].mean()


def pool(trs):
    trs = [t for t in trs if t is not None]
    if not trs:
        return None
    return {k: np.concatenate([t[k] for t in trs]) for k in trs[0]}


def years(tr):
    y = 1970 + (tr["fill_min"] / 525960.0).astype(int)  # approx; refine below
    import datetime
    y = np.array([datetime.datetime.fromtimestamp(int(m) * 60, datetime.UTC).year for m in tr["fill_min"]])
    out = {}
    for yy in np.unique(y):
        k = y == yy
        out[int(yy)] = (int(k.sum()), tr["net"][k].mean(), ct(tr["net"][k], tr["fill_min"][k] // 1440)[1])
    return out


def rand_t(era, syms):
    """Per draw, per cell pooled t of the random benchmark; returns array [draws, cells] or None."""
    parts = []
    nd = None
    for s in syms:
        p = os.path.join(OUT, f"{s}_{era}_rand.npz")
        if not os.path.exists(p):
            return None
        z = np.load(p)
        parts.append(z)
        nd = int(z["ndraws"]) if nd is None else min(nd, int(z["ndraws"]))
    T = np.full((nd, len(CELLS)), np.nan)
    day = np.concatenate([z["day"] for z in parts])
    net = np.concatenate([z["net"] for z in parts]).astype(float)
    dr = np.concatenate([z["draw"] for z in parts])
    cl = np.concatenate([z["cell"] for z in parts])
    o = np.lexsort((cl, dr))
    day, net, dr, cl = day[o], net[o], dr[o], cl[o]
    key = dr.astype(np.int64) * 10 + cl
    uk, st = np.unique(key, return_index=True)
    en = np.r_[st[1:], len(key)]
    for kk, a, b in zip(uk, st, en):
        d, c = kk // 10, kk % 10
        if d < nd:
            T[d, c] = ct(net[a:b], day[a:b])[1]
    return T


def main():
    era = sys.argv[1]
    syms = [s for s in (sys.argv[2:] or SYMS)]
    R = load_real(era, syms)
    syms = [s for s in syms if s in R]
    print(f"== SI {era}  symbols: {', '.join(syms)}")
    hdr = f"{'cell':<22}{'sym':<8}{'n':>6}{'net bp':>8}{'t':>7}{'net R':>8}{'sd bp':>7}{'x1.5 bp':>9}{'x1.5 t':>7}{'late bp':>9}{'late t':>7}{'gross':>7}{'R bp':>6}"
    print(hdr)
    real_t = {}
    for n in (3, 4):
        for fm, tpm in CELLS:
            base = f"{fm}_n{n}_{tpm}_base"
            late = f"{fm}_n{n}_{tpm}_late"
            for s in syms + ["POOL"]:
                if s == "POOL":
                    tb = pool([get(R, x, base) for x in syms])
                    tl = pool([get(R, x, late) for x in syms])
                else:
                    tb, tl = get(R, s, base), get(R, s, late)
                if tb is None:
                    continue
                nn, mu, t, mr, sd = summarize(tb)
                _, ms, ts, _, _ = summarize(tb, stress=True)
                _, ml, tlt, _, _ = summarize(tl) if tl is not None else (0, np.nan, np.nan, 0, 0)
                print(f"{base[:-5]:<22}{s[:3]:<8}{nn:>6}{mu:>8.2f}{t:>7.2f}{mr:>8.3f}{sd:>7.0f}{ms:>9.2f}{ts:>7.2f}"
                      f"{ml:>9.2f}{tlt:>7.2f}{gross_mean(tb):>7.2f}{tb['rbp'].mean():>6.0f}")
                if s == "POOL" and n == 3:
                    real_t[(fm, tpm)] = t
            print()
    print("exit mix / years (pooled, n3 cells):")
    for fm, tpm in CELLS:
        tb = pool([get(R, x, f"{fm}_n3_{tpm}_base") for x in syms])
        if tb is None:
            continue
        mix = np.bincount(tb["kind"], minlength=3) / len(tb["kind"])
        ys = years(tb)
        side = {sd: tb["net"][tb["side"] == sd].mean() for sd in (1, -1)}
        print(f"  {fm}_{tpm}: stop {mix[0]:.2f} tp {mix[1]:.2f} time {mix[2]:.2f}; long {side[1]:.2f} short {side[-1]:.2f}; "
              + "; ".join(f"{y}: n {v[0]} {v[1]:.2f} bp t {v[2]:.2f}" for y, v in ys.items()))
    T = rand_t(era, syms)
    if T is not None:
        print(f"\nrandom benchmark ({T.shape[0]} draws, pooled {', '.join(syms)}):")
        for ci, c in enumerate(CELLS):
            rt = T[:, ci]
            pct = 100 * np.mean(rt < real_t.get(c, np.nan))
            print(f"  {c[0]}_{c[1]}: real t {real_t.get(c, np.nan):.2f}; random t median {np.nanmedian(rt):.2f}, "
                  f"p95 {np.nanpercentile(rt, 95):.2f}; real beats {pct:.1f} %")
        mx = np.nanmax(T, axis=1)
        best = max(real_t.values())
        print(f"  max-over-4-cells null: median {np.median(mx):.2f}, p95 {np.percentile(mx, 95):.2f}; best real t "
              f"{best:.2f} beats {100 * np.mean(mx < best):.1f} %")


if __name__ == "__main__":
    main()
