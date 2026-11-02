"""Stream F: cells, statistics, random benchmark, checks (../HYPOTHESES_F.md). Reads out/cand.npz."""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
T0 = 1577836800000
MIN = 60000
DAY = 86400000
VAL0 = (1640995200000 - T0) // MIN
HS = (5, 15, 60)
BP = 1e4


def clt(x, day):
    """mean, day-clustered t, sd, n."""
    x = np.asarray(x, float); n = len(x)
    if n < 3:
        return np.nan, np.nan, np.nan, n
    m = x.mean()
    _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m)
    G = len(g)
    se = np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n
    return m, (m / se if se > 0 else np.nan), x.std(ddof=1), n


def dedup(sym, t):
    o = np.lexsort((t, sym))
    keep = np.zeros(len(t), bool)
    ls, lt = -1, -10 ** 9
    for j in o:
        if sym[j] != ls or t[j] - lt > 60:
            keep[j] = True; ls, lt = sym[j], t[j]
    return keep


def main():
    z = np.load(os.path.join(OUT, "cand.npz"))
    syms = list(z["syms"])
    sym, t, r, rb, sig, rank = z["sym"], z["t"].astype(np.int64), z["r"], z["rb"], z["sig"], z["rank"]
    g, gl, go, f, fl, rnd, rnd_t = z["g"], z["gl"], z["go"], z["f"], z["fl"], z["rnd"], z["rnd_t"].astype(np.int64)
    ibtc, ieth = syms.index("BTCUSDT"), syms.index("ETHUSDT")
    h = np.where((sym == ibtc) | (sym == ieth), 1.0, np.where(rank < 20, 3.0, 5.0)) / BP
    cost = 10 / BP + 4 * h
    day = (T0 + t * MIN) // DAY
    year = 1970 + 0  # placeholder
    import datetime as dt
    yr = np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).year for d in day])
    era = np.where(t < VAL0, 0, 1)
    a = np.abs(r)
    with np.errstate(invalid="ignore"):
        TH = {"T3": a >= 0.03, "T5": a >= 0.05, "TZ": (a >= 0.01) & (a >= 10 * np.nan_to_num(sig, nan=np.inf))}
        idio = (sym != ibtc) & np.isfinite(rb) & (np.abs(rb) <= 0.2 * a)
    FI = {"all": np.ones(len(t), bool), "idio": idio}
    lines = []; cells = []
    P = lines.append
    P(f"candidates {len(t)}  IS {int((era == 0).sum())}  VAL {int((era == 1).sum())}")
    rnd_day = (T0 + rnd_t * MIN) // DAY
    null_max = np.full(rnd.shape[1], -np.inf)
    lux = ((day >= (1583971200000 // DAY)) & (day <= (1584057600000 // DAY)))  # 2020-03-12..13
    marapr = (yr == 2020) & np.isin(np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).month for d in day]), [3, 4])
    ym = np.array([dt.datetime.fromtimestamp(d * 86400, dt.timezone.utc).strftime("%Y-%m") for d in day])
    lunaftx = np.isin(ym, ["2022-05", "2022-11"])
    hdr = ("cell", "IS n", "IS net", "IS t", "IS gross", "VAL n", "VAL net", "VAL t", "VAL gross", "rand% I/V",
           "yrs 20..24", "x1.5 t I/V", "late t I/V", "S_VAL", "pow trade/clust")
    P(" | ".join(hdr))
    for tn, tm in TH.items():
        for fn, fm in FI.items():
            m0 = tm & fm
            idx = np.where(m0)[0]
            keep = dedup(sym[idx], t[idx])
            idx = idx[keep]
            for k, H in enumerate(HS):
                ok = idx[np.isfinite(g[idx, k])]
                net = g[ok, k] - f[ok, k] - cost[ok]
                gross = g[ok, k] - f[ok, k]
                res = {"cell": f"{tn} {fn} H{H}"}
                for e, en in ((0, "IS"), (1, "VAL")):
                    q = era[ok] == e
                    mm, tt, sd, n = clt(net[q], day[ok][q])
                    res[en] = dict(n=int(n), net=mm * BP, t=tt, sd=sd * BP if sd == sd else np.nan, gross=gross[q].mean() * BP if n else np.nan)
                    m15 = clt(gross[q] - 1.5 * cost[ok][q], day[ok][q])
                    okl = ok[q][np.isfinite(gl[ok[q], k])]
                    ml = clt(gl[okl, k] - fl[okl, k] - cost[okl], day[okl])
                    res[en]["x15_t"] = m15[1]; res[en]["x15_net"] = m15[0] * BP
                    res[en]["late_t"] = ml[1]; res[en]["late_net"] = ml[0] * BP
                    # random
                    rr_ = rnd[ok[q], :, k].astype(float) - cost[ok[q]][:, None]
                    rmeans = np.nanmean(rr_, axis=0)
                    res[en]["rand_pct"] = float(np.mean(rmeans < mm)) * 100 if n else np.nan
                    res[en]["rand_mean"] = float(np.nanmean(rmeans)) * BP if n else np.nan
                    if e == 0 and n >= 3:
                        tts = []
                        for j in range(rr_.shape[1]):
                            v = rr_[:, j]; w = np.isfinite(v)
                            tts.append(clt(v[w], rnd_day[ok[q], j][w])[1])
                        null_max = np.maximum(null_max, np.nan_to_num(np.array(tts), nan=-np.inf))
                    # sides
                    for sn, sm in (("crash", r[ok][q] < 0), ("spike", r[ok][q] > 0)):
                        x = clt(net[q][sm], day[ok][q][sm])
                        res[en][sn] = dict(n=int(x[3]), net=x[0] * BP, t=x[1])
                    xo = go[ok[q], k] - f[ok[q], k] - cost[ok[q]]
                    w = np.isfinite(xo)
                    res[en]["open_entry"] = dict(net=float(np.mean(xo[w])) * BP if w.any() else np.nan,
                                                 t=clt(xo[w], day[ok][q][w])[1])
                    # concentration: drop top-3 coins by summed net
                    ss = sym[ok][q]
                    if n >= 3:
                        tot = {s_: net[q][ss == s_].sum() for s_ in np.unique(ss)}
                        top = sorted(tot, key=lambda s_: -tot[s_])[:3]
                        w = ~np.isin(ss, top)
                        x = clt(net[q][w], day[ok][q][w])
                        res[en]["drop_top3"] = dict(coins=[syms[s_] for s_ in top], net=x[0] * BP, t=x[1])
                    ex = lux | marapr if e == 0 else lunaftx
                    w = ~ex[ok][q]
                    x = clt(net[q][w], day[ok][q][w])
                    res[en]["excl"] = dict(net=x[0] * BP, t=x[1], n=int(x[3]))
                    if e == 0:
                        w = ~lux[ok][q]
                        x = clt(net[q][w], day[ok][q][w]); res[en]["excl_0312"] = dict(net=x[0] * BP, t=x[1])
                res["years"] = {int(y): float(net[yr[ok] == y].mean() * BP) if (yr[ok] == y).any() else None for y in range(2020, 2025)}
                res["years_n"] = {int(y): int((yr[ok] == y).sum()) for y in range(2020, 2025)}
                V = res["VAL"]
                S = V["net"] / V["sd"] if V["sd"] and V["sd"] == V["sd"] else np.nan
                res["S_VAL"] = S
                res["power_trade"] = S * np.sqrt(0.61 * V["n"])
                res["power_clust"] = V["t"] * np.sqrt(0.61)
                cells.append(res)
                I = res["IS"]
                yrs = " ".join("na" if res["years"][y] is None else f"{res['years'][y]:+.0f}" for y in range(2020, 2025))
                P(f"{res['cell']} | {I['n']} | {I['net']:+.1f} | {I['t']:+.2f} | {I['gross']:+.1f} | {V['n']} | {V['net']:+.1f} | "
                  f"{V['t']:+.2f} | {V['gross']:+.1f} | {I['rand_pct']:.0f}/{V['rand_pct']:.0f} | {yrs} | "
                  f"{I['x15_t']:+.2f}/{V['x15_t']:+.2f} | {I['late_t']:+.2f}/{V['late_t']:+.2f} | {S:+.3f} | "
                  f"{res['power_trade']:+.2f}/{res['power_clust']:+.2f}")
    real_max = max(c["IS"]["t"] for c in cells if c["IS"]["t"] == c["IS"]["t"])
    nm = null_max[np.isfinite(null_max)]
    P(f"\nmax-over-18 IS t: real {real_max:+.2f}; random null median {np.median(nm):+.2f}, p95 {np.percentile(nm, 95):+.2f}, "
      f"share null >= real {np.mean(nm >= real_max) * 100:.1f} %")
    P("\nper cell detail (IS / VAL): gross, random mean net, sides, open-of-next-bar entry, drop top-3 coins, exclusions")
    for c in cells:
        for en in ("IS", "VAL"):
            x = c[en]
            P(f"{c['cell']} {en}: n {x['n']} net {x['net']:+.1f} gross {x['gross']:+.1f} rand_mean {x['rand_mean']:+.1f} | "
              f"crash {x['crash']['n']} {x['crash']['net']:+.1f} (t {x['crash']['t']:+.2f}) spike {x['spike']['n']} "
              f"{x['spike']['net']:+.1f} (t {x['spike']['t']:+.2f}) | open-entry {x['open_entry']['net']:+.1f} "
              f"(t {x['open_entry']['t']:+.2f}) | x1.5 {x['x15_net']:+.1f} late {x['late_net']:+.1f} | "
              f"drop {x.get('drop_top3', {}).get('coins')} {x.get('drop_top3', {}).get('net', np.nan):+.1f} | "
              f"excl {x['excl']['net']:+.1f} (t {x['excl']['t']:+.2f})")
        P(f"   years n {c['years_n']}")
    open(os.path.join(OUT, "report.txt"), "w").write("\n".join(lines) + "\n")
    json.dump(cells, open(os.path.join(OUT, "cells.json"), "w"), indent=1, default=float)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
