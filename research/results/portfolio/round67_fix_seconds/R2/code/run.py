"""Stream R2: price the 6 declared cells, checks, random benchmark, max-over-cells null (../HYPOTHESES_R2.md).
Inputs: research/data/upbit_rotation/plan.json, raw/ (fapi 1m), binance_1m_wicks/npz, korea_hours/panel.npz (FR).
Run with python -I (raw files are untrusted data). Output: ../r2_output.txt, ../r2_results.json,
research/data/upbit_rotation/trades.npz."""
import json, os, glob, datetime
import numpy as np

RES = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research"
DATA = os.path.join(RES, "data", "upbit_rotation")
NPZ = os.path.join(RES, "data", "binance_1m_wicks", "npz")
PANEL = os.path.join(RES, "data", "korea_hours", "panel.npz")
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.abspath(os.path.join(HERE, ".."))
MIN = 60000; HOUR = 3600000; DAY = 86400000
CUT = 1735689600000; H0 = 1572566400000
TAKER = 5e-4
EXITS = ("L", "L1H", "L6H")
HEDGES = ("BTC", "LOW")
CELLS = [h + "-" + x for h in HEDGES for x in EXITS]
NBOOK = 2000
N_HOLD = 19.5


def hs(rank, sym):
    if sym == "BTCUSDT":
        return 1e-4
    return 3e-4 if rank < 20 else 5e-4


def mon(t):
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc).strftime("%Y-%m")


def load_prices(plan):
    need = {}
    for p in plan:
        for s in [0] + p["shifts"]:
            t0 = p["t_in"] + s * DAY - 4 * MIN; t1 = p["exits"][2] + s * DAY + 8 * MIN
            for sym in p["hi"] + p["lo"] + ["BTCUSDT"]:
                need.setdefault(sym, set()).update({mon(t0), mon(t1)})
    have = set(os.listdir(NPZ))
    raw = {}
    for fn in glob.glob(os.path.join(DATA, "raw", "*.json")):
        sym = os.path.basename(fn).rsplit("_", 1)[0]
        raw.setdefault(sym, []).append(fn)
    PX = {}
    for sym, ms in need.items():
        M, C = [], []
        for m in ms:
            f = os.path.join(NPZ, "%s_%s.npz" % (sym, m))
            if sym + "_" + m + ".npz" in have:
                z = np.load(f)
                M.append(z["m"].astype(np.int64)); C.append(z["c"].astype(float))
        for fn in raw.get(sym, []):
            a = json.load(open(fn))
            if not isinstance(a, list) or not a:
                continue
            t = np.array([int(x[0]) for x in a], dtype=np.int64)
            assert t.max() < CUT
            M.append(t // MIN); C.append(np.array([float(x[4]) for x in a]))
        if not M:
            continue
        m = np.concatenate(M); c = np.concatenate(C)
        ok = np.isfinite(c) & (c > 0) & (m * MIN < CUT)
        m, c = m[ok], c[ok]
        m, i = np.unique(m, return_index=True)
        PX[sym] = (m, c[i])
    return PX


def px(PX, sym, T):
    """price at instant T = close of the bar opening at T - 1 min, forward fill <= 5 bars."""
    if sym not in PX:
        return np.nan
    m, c = PX[sym]
    b = T // MIN - 1
    i = np.searchsorted(m, b, side="right") - 1
    if i < 0 or b - m[i] > 5:
        return np.nan
    return c[i]


def fsum(FRc, si, a, b):
    """sum of funding stamps at hours with time in (a, b]."""
    if si is None:
        return 0.0
    h1 = (a - H0) // HOUR + 1; h2 = (b - H0) // HOUR
    if h2 < h1:
        return 0.0
    return FRc[si, h2 + 1] - FRc[si, h1]


def leg(PX, FRc, sidx, syms, ranks, Te, X):
    r, f, c = [], [], []
    for s, rk in zip(syms, ranks):
        a = px(PX, s, Te); b = px(PX, s, X)
        if np.isfinite(a) and np.isfinite(b):
            r.append(b / a - 1); f.append(fsum(FRc, sidx.get(s), Te, X)); c.append(2 * (TAKER + hs(rk, s)))
    if not r:
        return np.nan, np.nan, np.nan, 0
    return np.mean(r), np.mean(f), np.mean(c), len(r)


def price_trade(PX, FRc, sidx, p, s, j, hedge, de=0, dx=0):
    Te = p["t_in"] + s * DAY + de * MIN
    X = p["exits"][j] + s * DAY + dx * MIN
    if X <= Te:
        return None
    rh, fh, ch, nh = leg(PX, FRc, sidx, p["hi"], p["hi_rank"], Te, X)
    if hedge == "BTC":
        rl, fl, cl, nl = leg(PX, FRc, sidx, ["BTCUSDT"], [0], Te, X)
    else:
        rl, fl, cl, nl = leg(PX, FRc, sidx, p["lo"], p["lo_rank"], Te, X)
    if nh == 0 or nl == 0:
        return None
    # long hedge, short high-share basket; funding: long pays rate, short receives
    gross = rl - rh
    fund = fh - fl
    return dict(gross=gross, fund=fund, cost=ch + cl, nh=nh, nl=nl)


def cl_t(x, day):
    x = np.asarray(x, float); n = len(x)
    if n < 3:
        return np.nan
    mu = x.mean()
    u, inv = np.unique(day, return_inverse=True)
    s = np.bincount(inv, weights=x - mu)
    G = len(u)
    var = (s ** 2).sum() / n ** 2 * G / max(G - 1, 1)
    return mu / np.sqrt(var) if var > 0 else np.nan


def stats(v, day):
    v = np.asarray(v, float)
    if len(v) == 0:
        return dict(n=0)
    sd = v.std(ddof=1) if len(v) > 1 else np.nan
    return dict(n=int(len(v)), mean_bp=1e4 * v.mean(), med_bp=1e4 * np.median(v), t=cl_t(v, day),
                sr=v.mean() / sd if sd > 0 else np.nan, days=int(len(np.unique(day))))


def main():
    plan = json.load(open(os.path.join(DATA, "plan.json")))
    z = np.load(PANEL, allow_pickle=False)
    psyms = list(z["syms"]); FR = z["FR"]
    FRc = np.concatenate([np.zeros((FR.shape[0], 1)), np.cumsum(FR, axis=1)], axis=1)
    sidx = {s: i for i, s in enumerate(psyms)}
    PX = load_prices(plan)
    out = []
    pr = lambda *a: out.append(" ".join(str(x) for x in a))
    pr("R2 run", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "notices", len(plan))
    era = np.array([p["era"] for p in plan]); day = np.array([p["d"] for p in plan])
    year = np.array([int(mon(p["N"])[:4]) for p in plan])
    ndraw = min(len(p["shifts"]) for p in plan)
    pr("draws per notice (min)", ndraw)

    # ---- descriptive path (gross, short hi / long hedge), IS first; instants relative to entry
    pr("\n## Path: gross bp of long hedge / short high tercile from P0 = price at entry - 4 min (before N)")
    offs = [("entry", 0), ("+5m", 5), ("+15m", 15), ("+30m", 30), ("+60m", 60)]
    for hedge in HEDGES:
        for e in ("IS", "VAL"):
            rows = []
            for k in np.where(era == e)[0]:
                p = plan[k]
                vals = []
                for name, o in offs:
                    q = dict(p); q = {**p, "t_in": p["t_in"] - 4 * MIN, "exits": [p["t_in"] + o * MIN] * 3}
                    r = price_trade(PX, FRc, sidx, q, 0, 0, hedge)
                    vals.append(np.nan if r is None else r["gross"])
                for j in range(3):
                    q = {**p, "t_in": p["t_in"] - 4 * MIN}
                    r = price_trade(PX, FRc, sidx, q, 0, j, hedge)
                    vals.append(np.nan if r is None else r["gross"])
                # same instants on the random days (mean over draws)
                rv = []
                for s in p["shifts"]:
                    vv = []
                    for name, o in offs:
                        q = {**p, "t_in": p["t_in"] - 4 * MIN, "exits": [p["t_in"] + o * MIN] * 3}
                        r = price_trade(PX, FRc, sidx, q, s, 0, hedge)
                        vv.append(np.nan if r is None else r["gross"])
                    for j in range(3):
                        q = {**p, "t_in": p["t_in"] - 4 * MIN}
                        r = price_trade(PX, FRc, sidx, q, s, j, hedge)
                        vv.append(np.nan if r is None else r["gross"])
                    rv.append(vv)
                rows.append((vals, np.nanmean(np.array(rv, float), axis=0)))
            A = np.array([r[0] for r in rows], float); B = np.array([r[1] for r in rows], float)
            names = [n for n, _ in offs] + list(EXITS)
            pr(f"{hedge} {e} n {len(A)}: " + " | ".join(
                f"{nm} {1e4*np.nanmean(A[:, i]):+.0f}/{1e4*np.nanmedian(A[:, i]):+.0f} (rand {1e4*np.nanmean(B[:, i]):+.0f})"
                for i, nm in enumerate(names)))

    # ---- declared cells
    res = {}
    trades = {}
    for hedge in HEDGES:
        for j, xn in enumerate(EXITS):
            cell = hedge + "-" + xn
            R = []
            for k, p in enumerate(plan):
                a = price_trade(PX, FRc, sidx, p, 0, j, hedge)
                b = price_trade(PX, FRc, sidx, p, 0, j, hedge, de=1, dx=1)
                c5 = price_trade(PX, FRc, sidx, p, 0, j, hedge, de=5)
                rnd = []
                for s in p["shifts"]:
                    r = price_trade(PX, FRc, sidx, p, s, j, hedge)
                    rnd.append((np.nan, np.nan) if r is None else (r["gross"], r["gross"] + r["fund"] - a["cost"] if a else np.nan))
                R.append(dict(a=a, late=b, late5=c5, rnd=np.array(rnd, float)))
            trades[cell] = R
            cr = {}
            for e in ("IS", "VAL"):
                ks = [k for k in np.where(era == e)[0] if R[k]["a"] is not None]
                g = np.array([R[k]["a"]["gross"] for k in ks]); f = np.array([R[k]["a"]["fund"] for k in ks])
                c = np.array([R[k]["a"]["cost"] for k in ks]); net = g + f - c
                dd = day[ks]
                st = stats(net, dd); st.update(gross_bp=1e4 * g.mean(), fund_bp=1e4 * f.mean(), cost_bp=1e4 * c.mean())
                st["net_x15_bp"] = 1e4 * (g + f - 1.5 * c).mean()
                kl = [k for k in ks if R[k]["late"] is not None]
                st["late_bp"] = 1e4 * np.mean([R[k]["late"]["gross"] + R[k]["late"]["fund"] - R[k]["late"]["cost"] for k in kl])
                st["late_t"] = cl_t([R[k]["late"]["gross"] + R[k]["late"]["fund"] - R[k]["late"]["cost"] for k in kl], day[kl])
                k5 = [k for k in ks if R[k]["late5"] is not None]
                st["late5_bp"] = 1e4 * np.mean([R[k]["late5"]["gross"] + R[k]["late5"]["fund"] - R[k]["late5"]["cost"] for k in k5]) if k5 else np.nan
                st["late5_n"] = len(k5)
                if len(net) > 1:
                    b = np.argmax(net); st["drop_best_bp"] = 1e4 * np.delete(net, b).mean()
                # random percentile of gross mean
                rg = np.array([R[k]["rnd"][:, 0] for k in ks])
                rng = np.random.default_rng(670 + len(ks))
                pick = rng.integers(0, rg.shape[1], size=(NBOOK, len(ks)))
                rm = np.nanmean(rg[np.arange(len(ks))[None, :], pick], axis=1)
                st["rand_pct"] = 100.0 * np.mean(rm < g.mean())
                st["rand_mean_bp"] = 1e4 * np.nanmean(rg)
                st["hold_min_med"] = float(np.median([(plan[k]["exits"][j] - plan[k]["t_in"]) / MIN for k in ks]))
                st["nh_mean"] = float(np.mean([R[k]["a"]["nh"] for k in ks]))
                st["by_year"] = {int(y): 1e4 * net[year[ks] == y].mean() for y in np.unique(year[ks])}
                st["by_year_n"] = {int(y): int((year[ks] == y).sum()) for y in np.unique(year[ks])}
                cr[e] = st
            yr = {**cr["IS"]["by_year"], **cr["VAL"]["by_year"]}
            cr["years_pos"] = f"{sum(v > 0 for v in yr.values())}/{len(yr)}"
            cr["power"] = cr["VAL"]["sr"] * np.sqrt(N_HOLD) if np.isfinite(cr["VAL"]["sr"]) else np.nan
            res[cell] = cr

    # ---- max-over-cells null on IS (random books, net of the real trade's cost)
    for e in ("IS", "VAL"):
        ks = np.where(era == e)[0]
        rng = np.random.default_rng(67067)
        pick = rng.integers(0, ndraw, size=(NBOOK, len(ks)))
        T = np.full((NBOOK, len(CELLS)), np.nan)
        for ci, cell in enumerate(CELLS):
            M = np.array([trades[cell][k]["rnd"][:ndraw, 1] for k in ks])
            V = M[np.arange(len(ks))[None, :], pick]
            for b in range(NBOOK):
                v = V[b]; okk = np.isfinite(v)
                T[b, ci] = cl_t(v[okk], day[ks][okk])
        mx = np.nanmax(T, axis=1)
        res["maxnull_" + e] = dict(median=float(np.nanmedian(mx)), p95=float(np.nanpercentile(mx, 95)))

    pr("\n## Cells (net bp per notice; t clustered by notice day)")
    pr("cell | era | n | net | t | SR | gross | fund | cost | x1.5 | late(+1 bar) net / t | late5 | drop best | rand % | rand mean | hold med min")
    for cell in CELLS:
        for e in ("IS", "VAL"):
            s = res[cell][e]
            pr(f"{cell} | {e} | {s['n']} | {s['mean_bp']:+.1f} | {s['t']:+.2f} | {s['sr']:+.3f} | {s['gross_bp']:+.1f} | "
               f"{s['fund_bp']:+.1f} | {s['cost_bp']:.1f} | {s['net_x15_bp']:+.1f} | {s['late_bp']:+.1f} / {s['late_t']:+.2f} | "
               f"{s['late5_bp']:+.1f} (n {s['late5_n']}) | {s.get('drop_best_bp', np.nan):+.1f} | {s['rand_pct']:.0f} | "
               f"{s['rand_mean_bp']:+.1f} | {s['hold_min_med']:.0f}")
        yr = {**res[cell]["IS"]["by_year"], **res[cell]["VAL"]["by_year"]}
        yn = {**res[cell]["IS"]["by_year_n"], **res[cell]["VAL"]["by_year_n"]}
        pr(f"   years {res[cell]['years_pos']}: " + ", ".join(f"{y} {v:+.0f} (n {yn[y]})" for y, v in sorted(yr.items()))
           + f" | power {res[cell]['power']:.2f}")
    pr("max-over-6-cells null of t (random books):", {e: res["maxnull_" + e] for e in ("IS", "VAL")})
    ispick = max(CELLS, key=lambda c: res[c]["IS"]["t"])
    pr("IS pick (highest IS t):", ispick)
    res["is_pick"] = ispick
    # per-trade detail for the IS pick and the BTC cells
    pr("\n## Per notice (net bp): " + " | ".join(CELLS))
    for k, p in enumerate(plan):
        v = []
        for cell in CELLS:
            a = trades[cell][k]["a"]
            v.append("nan" if a is None else f"{1e4*(a['gross']+a['fund']-a['cost']):+.0f}")
        pr(p["nid"], p["era"], mon(p["N"]), ",".join(p["coins"]), "|", " ".join(v))
    txt = "\n".join(out)
    open(os.path.join(OUTD, "r2_output.txt"), "w").write(txt + "\n")
    print(txt)

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        return o
    json.dump(clean(res), open(os.path.join(OUTD, "r2_results.json"), "w"), indent=1)
    # trades for C3 correlation (daily P&L), outside results/
    rows = []
    for cell in CELLS:
        for k, p in enumerate(plan):
            a = trades[cell][k]["a"]
            if a is not None:
                rows.append((CELLS.index(cell), p["t_in"], p["exits"][EXITS.index(cell.split("-")[1])],
                             a["gross"] + a["fund"] - a["cost"]))
    np.save(os.path.join(DATA, "trades.npy"), np.array(rows, float))


if __name__ == "__main__":
    main()
