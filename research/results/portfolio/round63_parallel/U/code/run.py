"""Stream U: short coin perp + long BTC perp around scheduled token unlocks, as declared in ../HYPOTHESES_U.md.
Prices cut at ts < 2025-01-01 (listings.load_series(hold=False)). Usage: run.py [--split primary|fallback]"""
import datetime, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "round60_new_listings", "code"))
import listings as L  # noqa: E402
import events as EV  # noqa: E402
C = L.C
T0D = C.T0 // C.DAY  # epoch day of index 0
TU = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "token_unlocks")
B = C.DATA
NDAY = int((C.HOLD_START - C.T0) // C.DAY)
ENTRIES = (7, 3)
EXITS = (0, 3)
SIZES = (0.01, 0.03)
COST_A, COST_B = 0.0015, 0.0006
NRAND = 1000
SPLITS = {"primary": {"IS": (18262, 18993), "VAL": (18993, 20089)},     # epoch days 2020-01-01, 2022-01-01, 2025-01-01
          "fallback": {"DISC": (18628, 19539), "VAL2": (19539, 20089)}}  # 2021-01-01, 2023-07-01, 2025-01-01
rng = np.random.default_rng(20261031)


def load(sym):
    F, QV, fu = L.load_series(sym, hold=False)
    p = os.path.join(TU, "funding", sym + ".csv")
    if os.path.exists(p):
        _, a = C._read(p)
        fu = np.zeros(NDAY)
        if len(a):
            d = C.day_of(a[:, 0]); m = (d >= 0) & (d < NDAY)
            np.add.at(fu, d[m], a[m, 1])
    return F, fu


def ymd(epoch_day):
    return datetime.datetime.fromtimestamp(epoch_day * 86400, datetime.timezone.utc).strftime("%Y-%m-%d")


def era_of(day, split):
    for k, (lo, hi) in SPLITS[split].items():
        if lo <= day < hi:
            return k
    return None


def cluster_t(r, keys):
    return L.cluster_t(r, keys)


def stats(rs, days):
    rs = np.asarray(rs); days = np.asarray(days)
    if len(rs) < 3:
        return dict(n=len(rs), mean=np.nan, med=np.nan, sd=np.nan, sr=np.nan, tw=np.nan, td=np.nan, yrs={})
    wk = (days + 3) // 7  # ISO-like week (epoch day 0 = Thursday; +3 makes weeks start Monday)
    yrs = {}
    for r, d in zip(rs, days):
        yrs.setdefault(int(ymd(d)[:4]), []).append(r)
    return dict(n=len(rs), mean=rs.mean(), med=np.median(rs), sd=rs.std(ddof=1), sr=rs.mean() / rs.std(ddof=1),
                tw=cluster_t(rs, wk), td=cluster_t(rs, days), yrs={y: (len(v), float(np.mean(v))) for y, v in sorted(yrs.items())})


def main(split="primary"):
    allcliffs = EV.build(0.005)          # cliffs >= 0.5 % (for "no event nearby" in random draws)
    near = {}
    for e in allcliffs:
        near.setdefault(e["perp"], []).append(e["day"])
    for e in allcliffs:                  # TGE days count as events too
        near.setdefault(e["perp"], []).append(e["tge_day"])
    near = {k: np.array(sorted(set(v))) for k, v in near.items()}
    base = [e for e in EV.build(0.0) if e["day"] < 20089 and e["day"] - 8 >= e["first_perp_day"] + 30]
    syms = sorted({e["perp"] for e in base})
    P = {s: load(s) for s in syms}
    Fb, fb = load("BTCUSDT")
    # random-coin universe (benchmark B)
    universe = []
    for f in sorted(os.listdir(os.path.join(B, "perp_1d"))):
        s = f[:-4]
        if not s.endswith("USDT") or s == "BTCUSDT" or L.base_of(s) in L.EXCL_BASE:
            continue
        universe.append(s)
    U = {}
    for s in universe:
        U[s] = P[s] if s in P else load(s)
    Umat = np.array([U[s][0] for s in universe])
    alive_first = np.array([np.argmax(~np.isnan(r)) if (~np.isnan(r)).any() else NDAY for r in Umat])

    def has_near(sym, day, w=10):
        a = near.get(sym)
        if a is None or not len(a):
            return False
        j = np.searchsorted(a, day - w)
        return j < len(a) and a[j] <= day + w

    def ep(sym, di, ke, kx, late=0, mult=1.0, hedge=True):
        Fa, fa = U[sym] if sym in U else P[sym]
        e = di - 1 - ke + late
        x = di - 1 + kx + late
        if e < 1 or x >= NDAY:
            return None
        res = L.episode(Fa, fa, Fb, fb, e, x - e, side=-1, cost_a=COST_A * mult, cost_b=COST_B * mult, hedge=hedge)
        return res

    report = []
    cells = {}
    for X in SIZES:
        for ke in ENTRIES:
            for kx in EXITS:
                ev = [e for e in base if e["size"] >= X]
                rows, last_exit = [], {}
                for e in ev:
                    di = e["day"] - T0D
                    era = era_of(e["day"], split)
                    if era is None:
                        continue
                    if e["day"] - 1 + kx >= 20089:      # exit must be before 2025-01-01
                        continue
                    if last_exit.get(e["perp"], -1) > di - 1 - ke:
                        continue
                    r = ep(e["perp"], di, ke, kx)
                    if r is None:
                        continue
                    last_exit[e["perp"]] = r[2]
                    rows.append(dict(e, era=era, di=di, r=r[0], adv=r[1],
                                     r15=ep(e["perp"], di, ke, kx, mult=1.5),
                                     rl=ep(e["perp"], di, ke, kx, late=1),
                                     ru=ep(e["perp"], di, ke, kx, hedge=False)))
                cells[(X, ke, kx)] = rows
    # random benchmarks: for each cell and era, NRAND resampled means
    eras = list(SPLITS[split])
    out = {}
    for key, rows in cells.items():
        X, ke, kx = key
        for era in eras:
            rr = [x for x in rows if x["era"] == era]
            if len(rr) < 3:
                out[(key, era)] = dict(st=stats([x["r"] for x in rr], [x["day"] for x in rr]), rows=rr)
                continue
            lo, hi = SPLITS[split][era]
            # A: same coin, random non-event day in the same era
            A = np.full((NRAND, len(rr)), np.nan)
            Bm = np.full((NRAND, len(rr)), np.nan)
            for j, x in enumerate(rr):
                Fa = P[x["perp"]][0]
                live = np.where(~np.isnan(Fa))[0]
                cand = [d for d in range(lo - T0D, hi - T0D) if d - 1 - ke >= x["first_perp_day"] - T0D + 30
                        and d - 1 + kx < NDAY and d - 1 + kx + T0D < 20089 and not np.isnan(Fa[d - 1 - ke])
                        and not np.isnan(Fa[d - 1 + kx]) and not has_near(x["perp"], d + T0D)]
                if cand:
                    pick = rng.choice(cand, NRAND)
                    for k, d in enumerate(pick):
                        res = ep(x["perp"], d, ke, kx)
                        if res is not None:
                            A[k, j] = res[0]
                # B: other coins, same event day
                e0 = x["di"] - 1 - ke
                ok = [i for i, s in enumerate(universe) if s != x["perp"] and alive_first[i] <= e0 - 60
                      and not np.isnan(Umat[i, e0]) and not np.isnan(Umat[i, min(NDAY - 1, x["di"] - 1 + kx)])
                      and not has_near(s, x["day"])]
                if ok:
                    pick = rng.choice(ok, NRAND)
                    for k, i in enumerate(pick):
                        res = ep(universe[i], x["di"], ke, kx)
                        if res is not None:
                            Bm[k, j] = res[0]
            out[(key, era)] = dict(st=stats([x["r"] for x in rr], [x["day"] for x in rr]), rows=rr,
                                   A=np.nanmean(A, axis=1), B=np.nanmean(Bm, axis=1))
    return cells, out, eras


def pct(v, dist):
    return 100.0 * np.mean(dist < v)


def fmt(split):
    cells, out, eras = main(split)
    lines = []
    P = lambda *a: lines.append(" ".join(str(x) for x in a))
    P("# split", split, "computed", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    P("| X | entry | exit | era | n | coins | mean | median | sd | SR/ev | t_week | t_day | x1.5 mean (t_wk) | late mean (t_wk) | unhedged mean | rand A mean / pct | rand B mean / pct | years (n, mean %) |")
    P("|" + "---|" * 18)
    for key in cells:
        X, ke, kx = key
        for era in eras:
            o = out[(key, era)]; s = o["st"]; rr = o["rows"]
            if s["n"] < 3:
                P("| %d %% | t-%d | t+%d | %s | %d | | | | | | | | | | | | | |" % (X * 100, ke, kx, era, s["n"]))
                continue
            d = [x["day"] for x in rr]
            r15 = [x["r15"][0] for x in rr]; rl = [x["rl"][0] if x["rl"] else np.nan for x in rr]
            ru = [x["ru"][0] for x in rr]
            ml = np.array(rl); okl = ~np.isnan(ml)
            s15 = stats(r15, d); sl = stats(ml[okl], np.array(d)[okl])
            yrs = ", ".join("%d: %d, %+.1f" % (y, n, m * 100) for y, (n, m) in s["yrs"].items())
            P("| %d %% | t-%d | t+%d | %s | %d | %d | %+.2f %% | %+.2f %% | %.1f %% | %.3f | %.2f | %.2f | %+.2f %% (%.2f) | %+.2f %% (%.2f) | %+.2f %% | %+.2f %% / %.0f | %+.2f %% / %.0f | %s |" % (
                X * 100, ke, kx, era, s["n"], len({x["perp"] for x in rr}), s["mean"] * 100, s["med"] * 100, s["sd"] * 100,
                s["sr"], s["tw"], s["td"], s15["mean"] * 100, s15["tw"], sl["mean"] * 100, sl["tw"], np.mean(ru) * 100,
                np.nanmean(o["A"]) * 100, pct(s["mean"], o["A"]), np.nanmean(o["B"]) * 100, pct(s["mean"], o["B"]), yrs))
    # max-over-cells null per era (benchmark A, B)
    for era in eras:
        ks = [k for k in cells if out[(k, era)]["st"]["n"] >= 3 and "A" in out[(k, era)]]
        if not ks:
            continue
        best = max(ks, key=lambda k: out[(k, era)]["st"]["mean"])
        mA = np.max(np.array([out[(k, era)]["A"] for k in ks]), axis=0)
        mB = np.max(np.array([out[(k, era)]["B"] for k in ks]), axis=0)
        P("max-over-cells %s: best cell X=%d%% t-%d t+%d mean %+.2f %%; pct vs max of %d random-A cells %.0f, random-B %.0f" % (
            era, best[0] * 100, best[1], best[2], out[(best, era)]["st"]["mean"] * 100, len(ks),
            pct(out[(best, era)]["st"]["mean"], mA), pct(out[(best, era)]["st"]["mean"], mB)))
    # tails + category split per cell
    P("")
    P("| X | entry | exit | era | adverse > 30 % | adverse > 50 % | worst 5 (coin date net) | insider-heavy n / mean / t_wk | rest n / mean / t_wk |")
    P("|" + "---|" * 9)
    for key in cells:
        X, ke, kx = key
        for era in eras:
            rr = out[(key, era)]["rows"]
            if len(rr) < 3:
                continue
            adv = np.array([x["adv"] for x in rr])
            w = sorted(rr, key=lambda x: x["r"])[:5]
            ins = [x for x in rr if x["ins_share"] >= 0.5]; rest = [x for x in rr if x["ins_share"] < 0.5]
            si = stats([x["r"] for x in ins], [x["day"] for x in ins]); sr_ = stats([x["r"] for x in rest], [x["day"] for x in rest])
            P("| %d %% | t-%d | t+%d | %s | %d | %d | %s | %d / %+.2f %% / %.2f | %d / %+.2f %% / %.2f |" % (
                X * 100, ke, kx, era, (adv > 0.3).sum(), (adv > 0.5).sum(),
                "; ".join("%s %s %+.0f %%" % (x["perp"][:-4], ymd(x["day"]), x["r"] * 100) for x in w),
                si["n"], si["mean"] * 100, si["tw"], sr_["n"], sr_["mean"] * 100, sr_["tw"]))
    return "\n".join(lines)


if __name__ == "__main__":
    split = sys.argv[sys.argv.index("--split") + 1] if "--split" in sys.argv else "primary"
    txt = fmt(split)
    print(txt)
    open(os.path.join(HERE, "output_%s.txt" % split), "w").write(txt + "\n")
