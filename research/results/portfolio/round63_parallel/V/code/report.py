"""Stream V: grade every declared cell from V/out/sims_<cur>.pkl. Prints the tables used in STREAM_V.md.
Run: python -I report.py > ../out/report.txt"""
import sys, os, pickle, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, vrp

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
IS0, IS1, VAL1 = vrp.ms(vrp.IS_A), vrp.ms(vrp.IS_B), vrp.ms(vrp.VAL_B)
HOLD_WEEKS = 95
RNG = np.random.default_rng(6363)
TAUS = {"V1": None, "V2t10": 0.10, "V2t0": 0.0}


def era_of(t):
    return "IS" if IS0 <= t < IS1 else ("VAL" if IS1 <= t < VAL1 else None)


def year(t):
    return vrp.ymd(t)[:4]


def cash_vec(m_cash, weeks):
    return np.array([m_cash(w) for w in weeks])


class Cash:
    def __init__(self):
        self.d = vrp.load_dff()

    def __call__(self, t):
        import datetime as dt
        d = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc)
        for k in range(10):
            s = (d - dt.timedelta(days=k)).strftime("%Y-%m-%d")
            if s in self.d:
                return self.d[s] / 100.0
        return np.nan


def weekly(cell, weeks, rc, mask):
    P, C = cell["P"][mask].astype(float), cell["C"][mask].astype(float)
    pnl, cap = P.sum(0), C.sum(0)
    ex = np.full(len(weeks), np.nan)
    ok = cap > 0
    ex[ok] = (pnl[ok] - cap[ok] * rc[ok] * 7 / 360) / cap[ok]
    return ex


def stats(ex, weeks, era):
    w = np.array([era_of(x) == era for x in weeks])
    x = ex[w]
    x = x[np.isfinite(x)]
    if len(x) < 5:
        return dict(n=len(x), mean=np.nan, t=np.nan, sh=np.nan)
    return dict(n=len(x), mean=100 * x.mean(), sd=100 * x.std(ddof=1), t=vrp.nw_t(x),
                sh=x.mean() / x.std(ddof=1) * math.sqrt(52), worst=100 * x.min())


def years(ex, weeks):
    out = {}
    for y in ("2021", "2022", "2023", "2024"):
        w = np.array([year(x) == y for x in weeks]) & np.isfinite(ex)
        out[y] = 100 * np.nansum(ex[w])
    return out


def maxdd(ex):
    x = np.nan_to_num(ex)
    c = np.cumsum(x)
    return 100 * float((np.maximum.accumulate(np.concatenate([[0], c])) - np.concatenate([[0], c])).max())


def mask_for(sims, tau):
    if tau is None:
        return np.ones(len(sims), bool)
    return np.array([(s["dvol"] - s["rv30"]) > tau for s in sims])


def main():
    cash = Cash()
    lines = []
    pr = lambda *a: lines.append(" ".join(str(x) for x in a))
    allcells = {}
    null_inputs = {}
    for cur in ("BTC", "ETH"):
        fn = f"{OUT}/sims_{cur}.pkl"
        if not os.path.exists(fn):
            pr("missing", fn); continue
        R = pickle.load(open(fn, "rb"))
        weeks = R["weeks"]
        rc = cash_vec(cash, weeks)
        pr(f"\n===== {cur}: IS term ratio sig/DVOL {R['ratio']}, IS median half spread {R['hsmed']}")
        for tenor in (7, 30):
            base24 = R[(tenor, 24, "base")]["sims"]
            # pricing diagnostics
            routes = [tuple(s["route"]) for s in base24]
            pr(f"-- {cur} {tenor}d pricing: n {len(base24)}, both legs from marks {sum(r == ('mark', 'mark') for r in routes)}, "
               f"iv fallback {sum('iv' in r for r in routes)}; median half spread {100*np.nanmedian([s['hs'] for s in base24]):.2f} % of premium")
            mod = R[(tenor, 24, "model")]
            r1 = np.array([mp / tp - 1 for _, _, mp, tp in mod])
            pr(f"   BS @ DVOL x IS ratio vs trade price: median {100*np.median(r1):+.1f} %, median |err| {100*np.median(np.abs(r1)):.1f} %, "
               f"p90 |err| {100*np.percentile(np.abs(r1), 90):.1f} %")
            dv = np.array([s["dvol"] for s in base24]); sg = np.array([s["sig"] for s in base24])
            pr(f"   entry straddle iv / DVOL: median {np.median(sg/dv):.3f}; BS @ raw DVOL would overprice by ~{100*np.median(dv/sg-1):.1f} %")
            for era in ("IS", "VAL"):
                e = [s for s in base24 if era_of(s["f0"]) == era]
                spread = np.array([s["dvol"] - s["rv30"] for s in e])
                pr(f"   {era}: mean DVOL {100*np.mean([s['dvol'] for s in e]):.1f}, mean RV30 {100*np.mean([s['rv30'] for s in e]):.1f}, "
                   f"DVOL-RV30 mean {100*spread.mean():+.1f} pts, share > 10 pts {np.mean(spread > 0.10):.2f}, share > 0 {np.mean(spread > 0):.2f}")
            for hh in (24, 4):
                cellb = R[(tenor, hh, "base")]
                sims = cellb["sims"]
                # cost breakdown (% of C per trade)
                capv = np.array([s["cap"] for s in sims])
                comp = dict(prem=np.mean([s["prem"] for s in sims] / capv), intr=np.mean([s["intr"] for s in sims] / capv),
                            hedge=np.mean([s["hedge"] for s in sims] / capv), fund=np.mean([s["fund"] for s in sims] / capv),
                            hs=np.mean([s["P"] * (s["hs"] if np.isfinite(s["hs"]) else 0.02) for s in sims] / capv),
                            optfee=np.mean([s["fee"] for s in sims] / capv),
                            hedgefee=np.mean([0.0005 * s["traded"] for s in sims] / capv),
                            final=np.mean([s["final"] for s in sims] / capv))
                pr(f"   [{cur} {tenor}d H{hh}] per trade % of C: premium {100*comp['prem']:.2f}, payoff -{100*comp['intr']:.2f}, "
                   f"hedge {100*comp['hedge']:+.2f}, funding {100*comp['fund']:+.2f}; costs: half spread {100*comp['hs']:.3f}, "
                   f"option fees {100*comp['optfee']:.3f}, hedge taker {100*comp['hedgefee']:.3f}; net {100*comp['final']:+.2f}")
                for vname, tau in TAUS.items():
                    key = f"{cur}-{tenor}d-H{hh}-{vname}"
                    res = {}
                    for var in ("base", "cost15", "late"):
                        cell = R[(tenor, hh, var)]
                        mk = mask_for(cell["sims"], tau)
                        ex = weekly(cell, weeks, rc, mk)
                        res[var] = dict(ex=ex, IS=stats(ex, weeks, "IS"), VAL=stats(ex, weeks, "VAL"), yrs=years(ex, weeks),
                                        dd=maxdd(ex), mk=mk)
                    allcells[key] = res
                    null_inputs[key] = res["base"]["ex"]
                    # random benchmark
                    sims_b = cellb["sims"]
                    mk = res["base"]["mk"]
                    rnd = {}
                    for era in ("IS", "VAL"):
                        ein = np.array([era_of(s["f0"]) == era for s in sims_b])
                        if tau is None:
                            mod = R[(tenor, hh, "model")]
                            rule = np.array([x for f, x, _, _ in mod if era_of(f) == era])
                            pool = np.array([x for t, x in R[(tenor, hh, "pool")] if era_of(t) == era])
                            n = len(rule)
                            draws = np.array([pool[RNG.integers(0, len(pool), n)].mean() for _ in range(500)])
                            rnd[era] = (100 * rule.mean(), 100 * np.mean(draws < rule.mean()))
                        else:
                            xs = np.array([s["ex"] for s in sims_b])[ein]
                            sel = xs[mk[ein]]
                            n = len(sel)
                            if n < 3:
                                rnd[era] = (np.nan, np.nan); continue
                            draws = np.array([xs[RNG.choice(len(xs), n, replace=False)].mean() for _ in range(1000)])
                            rnd[era] = (100 * sel.mean(), 100 * np.mean(draws < sel.mean()))
                    res["rnd"] = rnd
                    b = res["base"]
                    frac_val = b["VAL"]["n"] / max(1, sum(era_of(w) == "VAL" for w in weeks))
                    power = (b["VAL"]["sh"] / math.sqrt(52)) * math.sqrt(HOLD_WEEKS * frac_val) if np.isfinite(b["VAL"]["sh"]) else np.nan
                    res["power"] = power
                    pr(f"{key:22s} IS n {b['IS']['n']:3d} mean {b['IS']['mean']:+.3f}% t {b['IS']['t']:+.2f} SR {b['IS']['sh']:+.2f} | "
                       f"VAL n {b['VAL']['n']:3d} mean {b['VAL']['mean']:+.3f}% t {b['VAL']['t']:+.2f} SR {b['VAL']['sh']:+.2f} | "
                       f"x1.5 IS {res['cost15']['IS']['mean']:+.3f} VAL {res['cost15']['VAL']['mean']:+.3f} | late IS {res['late']['IS']['mean']:+.3f} "
                       f"VAL {res['late']['VAL']['mean']:+.3f} | yrs " + " ".join(f"{y}:{v:+.1f}" for y, v in b["yrs"].items()) +
                       f" | rnd IS {rnd['IS'][1]:.0f}% VAL {rnd['VAL'][1]:.0f}% | power {power:.2f} | maxDD {b['dd']:.1f}% of C")
                # tails for V1
                b = allcells[f"{cur}-{tenor}d-H{hh}-V1"]["base"]
                ex = b["ex"]
                order = np.argsort(np.nan_to_num(ex, nan=9))[:5]
                pr(f"   tail V1 {cur} {tenor}d H{hh}: worst weeks " + ", ".join(f"{vrp.ymd(weeks[i])} {100*ex[i]:+.1f}%" for i in order))
                for lab, d in (("2021-05 crash", "2021-05-14"), ("LUNA", "2022-05-06"), ("3AC", "2022-06-10"), ("FTX", "2022-11-04")):
                    i = [vrp.ymd(w) for w in weeks].index(d) if d in [vrp.ymd(w) for w in weeks] else None
                    if i is not None:
                        pr(f"      {lab} week {d}: {100*ex[i]:+.1f}% of C")
                need = np.array([s["need_max"] for s in sims])
                mtm = np.array([s["mtm_min"] for s in sims])
                pr(f"   margin: peak capital needed to stay above maintenance (x S0): median {np.median(need):.3f}, max {need.max():.3f}; "
                   f"trades needing > 0.5 S0 (C): {int((need > 0.5).sum())}/{len(need)}; worst intra-trade MTM {100*mtm.min():.1f}% of C")
    # V3 strangles (addendum 14:41 UTC) and the descriptive variance premium
    for cur in ("BTC", "ETH"):
        fn = f"{OUT}/sims3_{cur}.pkl"
        if not os.path.exists(fn):
            pr("missing", fn); continue
        R = pickle.load(open(fn, "rb"))
        weeks = R["weeks"]
        rc = cash_vec(cash, weeks)
        D = np.array([(f, a, b, c) for f, a, b, c in R["desc"]])
        for era in ("IS", "VAL"):
            w = np.array([era_of(f) == era for f in D[:, 0]])
            pr(f"   {cur} {era} Fridays: DVOL {100*D[w,1].mean():.1f}, realised next 30 d {100*D[w,2].mean():.1f}, trailing RV30 {100*D[w,3].mean():.1f}; "
               f"DVOL^2 - RV_next^2 mean {1e4*np.mean(D[w,1]**2 - D[w,2]**2):+.0f} var pts; DVOL > RV_next share {np.mean(D[w,1] > D[w,2]):.2f}")
        for tenor in (7, 30):
            key = f"{cur}-{tenor}d-H24-V3"
            res = {}
            for var in ("base", "cost15", "late"):
                cell = R[(tenor, 24, var)]
                mk = np.ones(len(cell["sims"]), bool)
                ex = weekly(cell, weeks, rc, mk)
                res[var] = dict(ex=ex, IS=stats(ex, weeks, "IS"), VAL=stats(ex, weeks, "VAL"), yrs=years(ex, weeks), dd=maxdd(ex), mk=mk)
            sims = R[(tenor, 24, "base")]["sims"]
            capv = np.array([x["cap"] for x in sims])
            pr(f"   [{key}] per trade % of C: premium {100*np.mean([x['prem'] for x in sims]/capv):.2f}, payoff -{100*np.mean([x['intr'] for x in sims]/capv):.2f}, "
               f"hedge {100*np.mean([x['hedge'] for x in sims]/capv):+.2f}, funding {100*np.mean([x['fund'] for x in sims]/capv):+.2f}, "
               f"half spread {100*np.nanmedian([x['hs'] for x in sims]):.1f} % of premium, option fees {100*np.mean([x['fee'] for x in sims]/capv):.3f}, "
               f"median leg deltas {np.median([x['dc'] for x in sims]):+.2f} / {np.median([x['dp'] for x in sims]):+.2f}, "
               f"leg iv / DVOL call {np.median([x['sigc']/x['dvol'] for x in sims]):.2f} put {np.median([x['sigp']/x['dvol'] for x in sims]):.2f}")
            b = res["base"]
            frac_val = b["VAL"]["n"] / max(1, sum(era_of(w) == "VAL" for w in weeks))
            res["power"] = (b["VAL"]["sh"] / math.sqrt(52)) * math.sqrt(HOLD_WEEKS * frac_val)
            res["rnd"] = {"IS": (np.nan, np.nan), "VAL": (np.nan, np.nan)}
            allcells[key] = res
            null_inputs[key] = b["ex"]
            ex = b["ex"]
            order = np.argsort(np.nan_to_num(ex, nan=9))[:5]
            need = np.array([x["need_max"] for x in sims]); mtm = np.array([x["mtm_min"] for x in sims])
            pr(f"{key:22s} IS n {b['IS']['n']:3d} mean {b['IS']['mean']:+.3f}% t {b['IS']['t']:+.2f} SR {b['IS']['sh']:+.2f} | "
               f"VAL n {b['VAL']['n']:3d} mean {b['VAL']['mean']:+.3f}% t {b['VAL']['t']:+.2f} SR {b['VAL']['sh']:+.2f} | "
               f"x1.5 IS {res['cost15']['IS']['mean']:+.3f} VAL {res['cost15']['VAL']['mean']:+.3f} | late IS {res['late']['IS']['mean']:+.3f} "
               f"VAL {res['late']['VAL']['mean']:+.3f} | yrs " + " ".join(f"{y}:{v:+.1f}" for y, v in b["yrs"].items()) +
               f" | power {res['power']:.2f} | maxDD {b['dd']:.1f}% of C")
            pr(f"   tail: worst weeks " + ", ".join(f"{vrp.ymd(weeks[i])} {100*ex[i]:+.1f}%" for i in order) +
               f"; capital needed max {need.max():.3f} x S0, > C in {int((need > 0.5).sum())}/{len(need)}; worst MTM {100*mtm.min():.1f}% of C")
    # max-over-cells null (base cells, all 24)
    keys = list(null_inputs)
    if keys:
        R0 = pickle.load(open(f"{OUT}/sims_BTC.pkl", "rb"))
        weeks = R0["weeks"]
        for era in ("IS", "VAL"):
            w = np.array([era_of(x) == era for x in weeks])
            M = np.array([null_inputs[k][w] for k in keys])  # cells x weeks
            mu = np.nanmean(M, 1, keepdims=True)
            Z = M - mu
            nW = Z.shape[1]
            obs = max(vrp.nw_t(M[i]) for i in range(len(keys)))
            mx = []
            for _ in range(1000):
                starts = RNG.integers(0, nW - 3, int(math.ceil(nW / 4)))
                idx = np.concatenate([np.arange(s, s + 4) for s in starts])[:nW]
                Zb = Z[:, idx]
                mx.append(max(vrp.nw_t(Zb[i]) for i in range(len(keys))))
            mx = np.array(mx)
            pr(f"max-over-{len(keys)}-cells null {era}: observed best NW t {obs:.2f}; null p50 {np.percentile(mx,50):.2f}, p95 {np.percentile(mx,95):.2f}")
    print("\n".join(lines))
    js = {k: {var: {e: {kk: (float(vv) if isinstance(vv, (int, float, np.floating)) else vv) for kk, vv in v[var][e].items()}
                    for e in ("IS", "VAL")} | {"yrs": v[var]["yrs"], "dd": v[var]["dd"]} for var in ("base", "cost15", "late")}
          | {"rnd": {e: list(map(float, v["rnd"][e])) for e in v["rnd"]}, "power": float(v["power"])} for k, v in allcells.items()}
    json.dump(js, open(f"{OUT}/cells.json", "w"), indent=1)


if __name__ == "__main__":
    main()
