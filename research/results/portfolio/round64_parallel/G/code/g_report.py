"""Stream G: 12 cells (X x H x leg), per-shock baskets, statistics, random benchmark (../HYPOTHESES_G.md).
Reads out/g_rows.npz; writes out/report.txt, out/cells.json, out/shock_<cell>.csv for the IS-best cell."""
import json, os, sys, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "F", "code")))
import report as FR  # noqa: E402  (stream F, read-only: clt)

OUT = os.path.join(HERE, "..", "out")
T0, MIN, DAY = 1577836800000, 60000, 86400000
VAL0 = (1640995200000 - T0) // MIN
HS = (5, 15, 60)
XN = ("X1", "X2")
BP = 1e4
clt = FR.clt
BTC_RT = 14 / BP


def ymd(day):
    return dt.datetime.fromtimestamp(int(day) * 86400, dt.timezone.utc)


def shock_mean(w, j, ns):
    """per-shock mean of w over rows with finite w; nan where none."""
    ok = np.isfinite(w)
    s = np.bincount(j[ok], weights=w[ok], minlength=ns)
    c = np.bincount(j[ok], minlength=ns)
    with np.errstate(invalid="ignore"):
        return np.where(c > 0, s / np.maximum(c, 1), np.nan), c


def build(z, xi, k, leg, sel, cost_mult=1.0, kind="g"):
    """per-row net for rows `sel` of shock set xi, horizon k; kind g (entry e+1), gl (late), go (open e+1)."""
    j = z["j"][sel]
    sd = z[f"s{xi}_side"][j]
    fkey = {"g": "f", "gl": "fl", "go": "f"}[kind]
    ga, fa = z[kind][sel, k], z[fkey][sel, k]
    cost = z["cost"][sel]
    if leg == "U":
        gross = sd * ga - sd * fa
        c = cost
    else:
        b = z["beta"][sel]
        bg, bf = z[f"s{xi}_b{kind}{k}"][j], z[f"s{xi}_b{fkey}{k}"][j]
        gross = sd * (ga - b * bg) - sd * fa + sd * b * bf
        c = cost + b * BTC_RT
    return gross - cost_mult * c, gross, j


def main():
    z = dict(np.load(os.path.join(OUT, "g_rows.npz")))
    syms = list(z["syms"])
    ieth = syms.index("ETHUSDT")
    h = np.where(z["sym"] == ieth, 1.0, np.where(z["rank"] < 20, 3.0, 5.0)) / BP
    z["cost"] = 10 / BP + 4 * h
    L = []; P = L.append; cells = []
    nulls = {}
    for xi, xn in enumerate(XN):
        e = z[f"s{xi}_e"]; ns = len(e)
        day = (T0 + e * MIN) // DAY
        yr = np.array([ymd(d).year for d in day]); mo = np.array([ymd(d).strftime("%Y-%m") for d in day])
        era = (e >= VAL0).astype(int)
        isx = z["x"] == xi
        lag = isx & z["lag"]
        nlag = np.bincount(z["j"][lag], minlength=ns)
        nel = np.bincount(z["j"][isx], minlength=ns)
        P(f"{xn}: shocks {ns} (IS {int((era == 0).sum())}, VAL {int((era == 1).sum())}); eligible alts per shock "
          f"median {np.median(nel):.0f}; laggards per shock median {np.median(nlag):.0f}, shocks with >= 1 laggard "
          f"IS {int(((nlag > 0) & (era == 0)).sum())} VAL {int(((nlag > 0) & (era == 1)).sum())}")
        P(f"   shocks per year: " + " ".join(f"{y}:{int((yr == y).sum())}" for y in range(2020, 2025)))
        rd = z[f"s{xi}_rnd"]; rdays = (T0 + rd * MIN) // DAY
        rside = z[f"s{xi}_rside"]
        for k, H in enumerate(HS):
            for leg in ("U", "B"):
                name = f"{xn} H{H} {leg}"
                sel = np.where(lag & np.isfinite(z["g"][:, k]))[0]
                net, gross, j = build(z, xi, k, leg, sel)
                sn, cnt = shock_mean(net, j, ns)
                sg, _ = shock_mean(gross, j, ns)
                s15, _ = shock_mean(build(z, xi, k, leg, sel, 1.5)[0], j, ns)
                sl_ = np.where(lag & np.isfinite(z["gl"][:, k]))[0]
                slt, _ = shock_mean(build(z, xi, k, leg, sl_, kind="gl")[0], z["j"][sl_], ns)
                so_ = np.where(lag & np.isfinite(z["go"][:, k]))[0]
                sop, _ = shock_mean(build(z, xi, k, leg, so_, kind="go")[0], z["j"][so_], ns)
                # information: all eligible alts and leaders, same leg
                sa_ = np.where(isx & np.isfinite(z["g"][:, k]))[0]
                sall, _ = shock_mean(build(z, xi, k, leg, sa_)[0], z["j"][sa_], ns)
                sd_ = np.where(isx & z["lead"] & np.isfinite(z["g"][:, k]))[0]
                sld, _ = shock_mean(build(z, xi, k, leg, sd_)[0], z["j"][sd_], ns)
                # random
                ri = sel
                rg = z["rnd_g"][ri, :, k].astype(float); rf = z["rnd_f"][ri, :, k].astype(float)
                rs = rside[z["j"][ri]]
                cst = z["cost"][ri][:, None]
                if leg == "U":
                    rn = rs * rg - rs * rf - cst
                else:
                    rb_ = z["rnd_beta"][ri].astype(float)
                    rbt = z[f"s{xi}_rbt"][z["j"][ri], :, k]; rbf = z[f"s{xi}_rbf"][z["j"][ri], :, k]
                    rn = rs * (rg - rb_ * rbt) - rs * rf + rs * rb_ * rbf - cst - rb_ * BTC_RT
                NR = rn.shape[1]
                rshock = np.full((ns, NR), np.nan)
                for q in range(NR):
                    rshock[:, q] = shock_mean(rn[:, q], z["j"][ri], ns)[0]
                res = dict(cell=name)
                for en in (0, 1):
                    m = (era == en) & np.isfinite(sn)
                    mm, tt, sdv, n = clt(sn[m], day[m])
                    ts = mm / (sdv / np.sqrt(n)) if n > 2 else np.nan
                    d = dict(n=int(n), trades=int(cnt[m].sum()), net=mm * BP, t=tt, t_shock=ts,
                             sd=sdv * BP, gross=np.nanmean(sg[m]) * BP)
                    for lab, arr in (("x15", s15), ("late", slt), ("open", sop), ("all", sall), ("lead", sld)):
                        mq = (era == en) & np.isfinite(arr)
                        x = clt(arr[mq], day[mq]); d[lab] = dict(net=x[0] * BP, t=x[1], n=int(x[3]))
                    rm = np.array([np.nanmean(rshock[m, q]) for q in range(NR)])
                    d["rand_pct"] = float(np.mean(rm < mm) * 100); d["rand_mean"] = float(np.nanmean(rm) * BP)
                    if en == 0:
                        tq = []
                        for q in range(NR):
                            v = rshock[m, q]; w = np.isfinite(v)
                            tq.append(clt(v[w], rdays[m, q][w])[1] if w.sum() > 2 else np.nan)
                        nulls[name] = np.nan_to_num(np.array(tq), nan=-np.inf)
                    # exclusions
                    if en == 0:
                        ex = {"no_0312": np.isin(day, [18333, 18334]),
                              "no_marapr20": np.isin(mo, ["2020-03", "2020-04"]),
                              "no_0519": day == 18766}
                    else:
                        ex = {"no_luna_ftx": np.isin(mo, ["2022-05", "2022-11"])}
                    for lab, em in ex.items():
                        w = m & ~em
                        x = clt(sn[w], day[w]); d[lab] = dict(net=x[0] * BP, t=x[1], n=int(x[3]))
                    if n > 5:
                        o = np.argsort(-np.abs(sn[m]))[:3]
                        w = np.ones(int(n), bool); w[o] = False
                        x = clt(sn[m][w], day[m][w]); d["drop_top3"] = dict(net=x[0] * BP, t=x[1])
                    res["IS" if en == 0 else "VAL"] = d
                res["years"] = {int(y): (float(np.nanmean(sn[(yr == y) & np.isfinite(sn)]) * BP)
                                         if ((yr == y) & np.isfinite(sn)).any() else None) for y in range(2020, 2025)}
                res["years_n"] = {int(y): int(((yr == y) & np.isfinite(sn)).sum()) for y in range(2020, 2025)}
                V = res["VAL"]
                S = V["net"] / V["sd"] if V["sd"] == V["sd"] and V["sd"] > 0 else np.nan
                res["S_VAL"] = S; res["power_trade"] = S * np.sqrt(0.61 * V["n"])
                res["power_clust"] = V["t"] * np.sqrt(0.61)
                cells.append(res)
                np.save(os.path.join(OUT, f"shock_{xn}_H{H}_{leg}.npy"), np.c_[e, day, era, sn, cnt])
    real_max = max(c["IS"]["t"] for c in cells if c["IS"]["t"] == c["IS"]["t"])
    NM_ = np.max(np.vstack(list(nulls.values())), axis=0)
    P("")
    P("cell | IS shocks/trades | IS net | IS t (day) | IS t (shock) | IS gross | VAL shocks/trades | VAL net | VAL t | "
      "VAL gross | rand% I/V | yrs 20..24 | x1.5 t I/V | late net I/V | S_VAL | power trade/clust")
    for c in cells:
        I, V = c["IS"], c["VAL"]
        yrs = " ".join("na" if c["years"][y] is None else f"{c['years'][y]:+.0f}" for y in range(2020, 2025))
        P(f"{c['cell']} | {I['n']}/{I['trades']} | {I['net']:+.1f} | {I['t']:+.2f} | {I['t_shock']:+.2f} | "
          f"{I['gross']:+.1f} | {V['n']}/{V['trades']} | {V['net']:+.1f} | {V['t']:+.2f} | {V['gross']:+.1f} | "
          f"{I['rand_pct']:.0f}/{V['rand_pct']:.0f} | {yrs} | {I['x15']['t']:+.2f}/{V['x15']['t']:+.2f} | "
          f"{I['late']['net']:+.1f}/{V['late']['net']:+.1f} | {c['S_VAL']:+.3f} | "
          f"{c['power_trade']:+.2f}/{c['power_clust']:+.2f}")
    P(f"\nmax-over-12 IS t: real {real_max:+.2f}; random null median {np.median(NM_):+.2f}, "
      f"p95 {np.percentile(NM_, 95):+.2f}, share null >= real {np.mean(NM_ >= real_max) * 100:.1f} %")
    P("\ndetail per cell (IS / VAL): net (t) | random mean | open-of-e+1 entry | all alts | leaders | exclusions | "
      "drop top 3 shocks")
    for c in cells:
        for en in ("IS", "VAL"):
            x = c[en]
            exs = " ".join(f"{lab} {x[lab]['net']:+.1f} (t {x[lab]['t']:+.2f}, n {x[lab]['n']})"
                           for lab in ("no_0312", "no_marapr20", "no_0519", "no_luna_ftx") if lab in x)
            P(f"{c['cell']} {en}: net {x['net']:+.1f} (t {x['t']:+.2f}) gross {x['gross']:+.1f} sd {x['sd']:.0f} | "
              f"rand {x['rand_mean']:+.1f} | open {x['open']['net']:+.1f} (t {x['open']['t']:+.2f}) | "
              f"all {x['all']['net']:+.1f} (t {x['all']['t']:+.2f}) | lead {x['lead']['net']:+.1f} "
              f"(t {x['lead']['t']:+.2f}) | {exs} | top3 {x.get('drop_top3', {}).get('net', np.nan):+.1f}")
        P(f"   years n {c['years_n']}")
    open(os.path.join(OUT, "report.txt"), "w").write("\n".join(L) + "\n")
    json.dump(cells, open(os.path.join(OUT, "cells.json"), "w"), indent=1, default=float)
    print("\n".join(L))


if __name__ == "__main__":
    main()
