"""Stream Q grid run. Usage: python -I run.py need|grade [reps]
need : 1h screen of the 15 declared cells, writes ../out/need_m1.txt (days of 1m data to pull) and screen counts.
grade: prices every trade on 1m bars (entry T+1 min, late T+2 min, info T+5 min, exit X+1 min), bad-print guard,
       stats per era / year, x1.5, random benchmark on 1h opens, max-over-cells null. Writes ../out/cells.json and
       ../out/trades_<cell>.csv."""
import csv, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I drops the script dir; code dir holds only our code
import q
from q import H, M, DAY, J0, N, FEE, ERAS, cl_t

OUT = os.path.join(q.HERE, "..", "out")
os.makedirs(OUT, exist_ok=True)
CELLS = [("Q1", k, Hh) for k in (30, 60, 100) for Hh in (24, 72)] + \
        [("Q2", k, Hh) for k in (30, 60, 100) for Hh in (24, 72)] + [("Q2b", k, 0) for k in (10, 20, 30)]
HOLD_YEARS = 1.83


def name(c):
    return f"{c[0]}_k{c[1]}" + (f"_H{c[2]}" if c[0] != "Q2b" else "")


def ms(j):
    return int((J0 + j) * H)


def day_of(t):
    return str(np.datetime64(int(t), "ms"))[:10]


def trades_for(pairs, c):
    """List of dict trades (1h screen) for cell c."""
    kind, k, Hh = c
    out = []
    if kind == "Q2b":
        for pi, h, side, b in q.q2b_events(pairs, k):
            p = pairs[pi]
            out.append(dict(pi=pi, h=h, e=h + 1, x=int(p["exp"] // H - J0), side=side, d=b))
        return out
    T = q.simulate(pairs, kind, k, Hh)
    for i in range(len(T["e"])):
        out.append(dict(pi=int(T["pi"][i]), h=int(T["h"][i]), e=int(T["e"][i]), x=int(T["x"][i]),
                        side=float(T["side"][i]), d=float(T["d"][i])))
    return out


class M1:
    def __init__(self):
        self.cache = {}

    def day(self, market, sym, d):
        key = (market, sym, d)
        if key not in self.cache:
            p = os.path.join(q.CM, "m1", market, sym, d + ".csv")
            a = None
            if os.path.exists(p) and os.path.getsize(p) > 10:
                a = np.loadtxt(p, delimiter=",", skiprows=1, ndmin=2)
                if not len(a):
                    a = None
            self.cache[key] = a
        return self.cache[key]

    def bar(self, market, sym, t, field, slack=5):
        """o / c of the 1m bar starting at t; if missing, the next bar starting within `slack` minutes."""
        for s in range(slack + 1):
            tt = t + s * M
            a = self.day(market, sym, day_of(tt))
            if a is None:
                continue
            i = np.searchsorted(a[:, 0], tt)
            if i < len(a) and a[i, 0] == tt:
                return a[i, 1 if field == "o" else 2]
        return np.nan

    def mean_close(self, market, sym, a_t, b_t):
        a = self.day(market, sym, day_of(a_t))
        if a is None:
            return np.nan
        w = (a[:, 0] >= a_t) & (a[:, 0] < b_t)
        return a[w, 2].mean() if w.sum() >= 20 else np.nan


def need(pairs):
    lines, counts = set(), {}
    for c in CELLS:
        T = trades_for(pairs, c)
        counts[name(c)] = {era: int(sum(1 for t in T if a <= ms(t["e"]) < b)) for era, (a, b) in ERAS.items()}
        for t in T:
            p = pairs[t["pi"]]
            te, tx = ms(t["e"]), ms(t["x"])
            for mk, sym in ((p["Amarket"], p["A"]), ("um", p["U"])):
                for tt in (te - M, te + M, te + 5 * M, tx + M, tx - 30 * M):
                    lines.add((mk, sym, day_of(tt)))
    with open(os.path.join(OUT, "need_m1.txt"), "w") as f:
        for x in sorted(lines):
            f.write(" ".join(x) + "\n")
    print(json.dumps(counts, indent=0))
    print("days to pull", len(lines))


def price_1m(pairs, c, T, m1):
    """Adds 1m-priced nets to each trade: net (T+1), late (T+2), info5 (T+5), guard flag."""
    kind = c[0]
    rows = []
    for t in T:
        p = pairs[t["pi"]]
        te, tx = ms(t["e"]), ms(t["x"])
        A, Am, U = p["A"], p["Amarket"], p["U"]
        r = dict(t)
        r.update(A=A, U=U, coin=p["coin"], te=te, tx=tx, guard=0, net=np.nan, late=np.nan, info5=np.nan)
        if m1 is None:
            Ax = Ux = np.nan
        g_ok = m1 is not None
        for mk, sym, c1h in ([] if m1 is None else ((Am, A, p["Ac"][t["h"]]), ("um", U, p["Uc"][t["h"]]))):
            c1m = m1.bar(mk, sym, te - M, "c", slack=0)
            if np.isnan(c1m) or abs(np.log(c1h / c1m)) > 1e-4:
                g_ok = False
        if m1 is None:
            pass
        elif kind == "Q2b":
            Ax = m1.mean_close(Am, A, tx - 30 * M, tx)
            Ux = m1.bar("um", U, tx + M, "o")
        else:
            Ax = m1.bar(Am, A, tx + M, "o")
            Ux = m1.bar("um", U, tx + M, "o")
        r["guard"] = int(g_ok)
        for lab, dl in (() if m1 is None else (("net", 1), ("late", 2), ("info5", 5))):
            Ae = m1.bar(Am, A, te + dl * M, "o", slack=0)
            Ue = m1.bar("um", U, te + dl * M, "o", slack=0)
            price, fu, cost = leg(p, kind, t, Ae, Ax, Ue, Ux)
            r[lab] = price + fu - cost
            if lab == "net":
                r.update(price=price, fund=fu, cost=cost)
        # 1h-open version (the random benchmark's price source)
        if kind == "Q2b":
            Ax1, Ux1 = p["Ac"][t["x"] - 1], p["Uo"][t["x"]]
        else:
            Ax1, Ux1 = p["Ao"][t["x"]], p["Uo"][t["x"]]
        pr, fu, co = leg(p, kind, t, p["Ao"][t["e"]], Ax1, p["Uo"][t["e"]], Ux1)
        r["net1h"] = pr + fu - co
        r.update(price1h=pr, fund=fu, cost=co)
        rows.append(r)
    return rows


def leg(p, kind, t, Ae, Ax, Ue, Ux):
    side = t["side"]
    price = side * ((Ax / Ae - 1) - (Ux / Ue - 1))
    fu = side * (p["ufc"][t["x"]] - p["ufc"][t["e"]])
    if p["afc"] is not None:
        fu -= side * (p["afc"][t["x"]] - p["afc"][t["e"]])
    if kind == "Q2b":
        cost = 4 * FEE + 2 * p["hsU"] + p["hsA"]
    else:
        cost = 4 * FEE + 2 * (p["hsA"] + p["hsU"])
    return price, fu, cost


def stats(rows, key="net", cost_mult=1.0):
    x = np.array([r[key] + (1 - cost_mult) * r["cost"] for r in rows], float)
    day = np.array([r["te"] // DAY for r in rows])
    ok = ~np.isnan(x)
    x, day = x[ok], day[ok]
    if len(x) < 2:
        return dict(n=int(len(x)))
    u, inv = np.unique(day, return_inverse=True)
    ds = np.bincount(inv, weights=x)
    return dict(n=int(len(x)), days=int(len(u)), net_bp=x.mean() * 1e4, med_bp=float(np.median(x) * 1e4),
                t=cl_t(x, day), win=float((x > 0).mean()), sr=x.mean() / x.std(ddof=1),
                sr_day=ds.mean() / ds.std(ddof=1) if len(ds) > 1 else np.nan)


def random_null(pairs, c, rows, era, reps, rng):
    kind = c[0]
    a, b = ERAS[era]
    R = [r for r in rows if a <= r["te"] < b]
    means, ts = np.full(reps, np.nan), np.full(reps, np.nan)
    if len(R) < 2:
        return means, ts
    nets = np.full((reps, len(R)), np.nan)
    days = np.zeros((reps, len(R)), np.int64)
    by = {}
    for i, r in enumerate(R):
        by.setdefault(r["pi"], []).append(i)
    for pi, idx in by.items():
        p = pairs[pi]
        hrs = p["hours"]
        if kind == "Q2b":
            eh = int(p["exp"] // H - J0)
            pool = np.arange(max(eh - 72, 0), eh - 2)
            pool = pool[~np.isnan(p["base"][pool])]
        else:
            ok = ~np.isnan(p["d"]) & (hrs >= a) & (hrs < b)
            if kind == "Q2":
                ok &= p["w"] >= 3 / 365.25
            pool = np.where(ok)[0]
        if not len(pool):
            continue
        for i in idx:
            L = R[i]["x"] - R[i]["e"]
            cand = pool[rng.integers(0, len(pool), size=(reps, 20))]
            e = cand + 1
            x = np.full_like(e, int(p["exp"] // H - J0)) if kind == "Q2b" else e + L
            lim = min(N - 1, p["xmax"]) if kind != "Q2b" else N - 1
            xc = np.minimum(x, lim)
            if kind == "Q2b":
                Ax = p["Ac"][xc - 1]
            else:
                Ax = p["Ao"][xc]
            v = (x <= lim) & ~np.isnan(p["Ao"][np.minimum(e, N - 1)]) & ~np.isnan(p["Uo"][np.minimum(e, N - 1)]) & \
                ~np.isnan(Ax) & ~np.isnan(p["Uo"][xc])
            first = np.argmax(v, axis=1)
            good = v[np.arange(reps), first]
            ee = e[np.arange(reps), first]; xx = xc[np.arange(reps), first]; rr = cand[np.arange(reps), first]
            if kind == "Q2b":
                side = -np.sign(p["base"][rr])
            else:
                side = -np.sign(p["d"][rr])
            Ae, Ue = p["Ao"][ee], p["Uo"][ee]
            Axx = p["Ac"][xx - 1] if kind == "Q2b" else p["Ao"][xx]
            Ux = p["Uo"][xx]
            price = side * ((Axx / Ae - 1) - (Ux / Ue - 1))
            fu = side * (p["ufc"][xx] - p["ufc"][ee])
            if p["afc"] is not None:
                fu -= side * (p["afc"][xx] - p["afc"][ee])
            cost = 4 * FEE + (2 * p["hsU"] + p["hsA"] if kind == "Q2b" else 2 * (p["hsA"] + p["hsU"]))
            nets[:, i] = np.where(good, price + fu - cost, np.nan)
            days[:, i] = hrs[np.minimum(ee, N - 1)] // DAY
    for r_ in range(reps):
        ok = ~np.isnan(nets[r_])
        if ok.sum() >= 2:
            means[r_] = nets[r_, ok].mean()
            ts[r_] = cl_t(nets[r_, ok], days[r_, ok])
    return means, ts


def year_of(t):
    return int(str(np.datetime64(int(t), "ms"))[:4])


def grade(pairs, reps):
    m1 = M1()
    res, allrows = {}, {}
    sel = {}
    for r in csv.DictReader(open(os.path.join(OUT, "selection.csv"))):
        sel.setdefault(r["cell"], set()).add((int(r["pi"]), int(r["e"])))
    for c in CELLS:
        T = [t for t in trades_for(pairs, c) if (t["pi"], t["e"]) in sel.get(name(c), set())]
        rows = price_1m(pairs, c, T, m1)
        allrows[name(c)] = rows
        keep = [r for r in rows if r["guard"] and not np.isnan(r["net"])]
        out = dict(screen_n={}, dropped_guard={}, dropped_nan={})
        for era, (a, b) in ERAS.items():
            E = [r for r in rows if a <= r["te"] < b]
            K = [r for r in keep if a <= r["te"] < b]
            out["screen_n"][era] = len(E)
            out["dropped_guard"][era] = sum(1 for r in E if not r["guard"])
            out["dropped_nan"][era] = sum(1 for r in E if r["guard"] and np.isnan(r["net"]))
            s = stats(K)
            s["x1.5"] = stats(K, cost_mult=1.5).get("net_bp")
            s["t_x1.5"] = stats(K, cost_mult=1.5).get("t")
            sl = stats(K, "late"); s["late_bp"], s["late_t"] = sl.get("net_bp"), sl.get("t")
            s5 = stats(K, "info5"); s["info5_bp"], s["info5_t"] = s5.get("net_bp"), s5.get("t")
            s1 = stats(K, "net1h"); s["net1h_bp"], s["net1h_t"] = s1.get("net_bp"), s1.get("t")
            if K:
                s["price_bp"] = float(np.nanmean([r["price"] for r in K]) * 1e4)
                s["fund_bp"] = float(np.nanmean([r["fund"] for r in K]) * 1e4)
                s["cost_bp"] = float(np.nanmean([r["cost"] for r in K]) * 1e4)
                s["hold_h"] = float(np.mean([r["x"] - r["e"] for r in K]))
                s["coins"] = {}
                for r in K:
                    s["coins"].setdefault(r["A"], [0, 0.0])
                    s["coins"][r["A"]][0] += 1; s["coins"][r["A"]][1] += r["net"] * 1e4
            out[era] = s
        yrs = {}
        for r in keep:
            yrs.setdefault(year_of(r["te"]), []).append(r["net"])
        out["years"] = {y: (len(v), float(np.mean(v) * 1e4)) for y, v in sorted(yrs.items())}
        sv = out["VAL"]
        if sv.get("n", 0) > 2:
            nh = HOLD_YEARS * sv["n"] / 3
            dh = HOLD_YEARS * sv["days"] / 3
            sv["power_trade"] = sv["sr"] * np.sqrt(nh)
            sv["power_day"] = sv["sr_day"] * np.sqrt(dh)
        res[name(c)] = out
        with open(os.path.join(OUT, f"trades_{name(c)}.csv"), "w") as f:
            cols = ["A", "U", "coin", "te", "tx", "h", "e", "x", "side", "d", "guard", "price", "fund", "cost", "net",
                    "late", "info5", "net1h"]
            w = csv.writer(f); w.writerow(cols)
            for r in rows:
                w.writerow([r.get(k) for k in cols])
        print(name(c), {e: (out[e].get("n"), round(out[e].get("net_bp", np.nan), 1), round(out[e].get("t", np.nan), 2))
                        for e in ERAS}, flush=True)
    with open(os.path.join(OUT, "cells_1m.json"), "w") as f:
        json.dump(dict(cells=res), f, indent=1, default=float)


def era_rows(rows, era):
    a, b = ERAS[era]
    return [r for r in rows if a <= r["te"] < b]


def screen(pairs, reps):
    """Addendum 2 step 1: all 15 cells on 1h opens; random benchmark; selection of trades for 1m pricing."""
    res, allrows = {}, {}
    for c in CELLS:
        rows = price_1m(pairs, c, trades_for(pairs, c), None)
        rows = [r for r in rows if not np.isnan(r["net1h"])]
        allrows[name(c)] = rows
        late = []
        if c[0] != "Q2b":
            TL = q.simulate(pairs, c[0], c[1], c[2], lag=1)
            TT = [dict(pi=int(TL["pi"][i]), h=int(TL["h"][i]), e=int(TL["e"][i]), x=int(TL["x"][i]),
                       side=float(TL["side"][i]), d=float(TL["d"][i])) for i in range(len(TL["e"]))]
            late = [r for r in price_1m(pairs, c, TT, None) if not np.isnan(r["net1h"])]
        out = {}
        for era in ERAS:
            K = era_rows(rows, era)
            s_ = stats(K, "net1h")
            s_["x1.5"] = stats(K, "net1h", 1.5).get("net_bp")
            s_["hour_late_bp"] = stats(era_rows(late, era), "net1h").get("net_bp") if late else None
            s_["hour_late_t"] = stats(era_rows(late, era), "net1h").get("t") if late else None
            if K:
                s_["price_bp"] = float(np.mean([r["price1h"] for r in K]) * 1e4)
                s_["fund_bp"] = float(np.mean([r["fund"] for r in K]) * 1e4)
                s_["cost_bp"] = float(np.mean([r["cost"] for r in K]) * 1e4)
            out[era] = s_
        yrs = {}
        for r in rows:
            yrs.setdefault(year_of(r["te"]), []).append(r["net1h"])
        out["years"] = {y: (len(v), float(np.mean(v) * 1e4)) for y, v in sorted(yrs.items())}
        res[name(c)] = out
        print(name(c), {e: (out[e].get("n"), round(out[e].get("net_bp", np.nan), 1), round(out[e].get("t", np.nan), 2),
                            round(out[e].get("price_bp", np.nan), 1)) for e in ERAS}, flush=True)
    rng = np.random.default_rng(64)
    nulls = {}
    for era in ERAS:
        tm = []
        for c in CELLS:
            K = allrows[name(c)]
            means, ts = random_null(pairs, c, K, era, reps, rng)
            act = [r["net1h"] for r in era_rows(K, era)]
            o = res[name(c)][era]
            if act and not np.all(np.isnan(means)):
                o["beats_random"] = float(np.nanmean(means < np.mean(act)))
                o["random_mean_bp"] = float(np.nanmean(means) * 1e4)
            tm.append(ts)
        with np.errstate(all="ignore"):
            mx = np.nanmax(np.array(tm), axis=0)
        nulls[era] = dict(max_t_p50=float(np.nanpercentile(mx, 50)), max_t_p95=float(np.nanpercentile(mx, 95)))
        print(era, nulls[era], flush=True)
    # selection (addendum 2 step 2)
    best = {}
    for c in CELLS:
        tI = res[name(c)]["IS"].get("t", np.nan)
        if not np.isnan(tI) and (c[0] not in best or tI > best[c[0]][1]):
            best[c[0]] = (name(c), tI)
    full = {b[0] for b in best.values()} | {name(c) for c in CELLS if res[name(c)]["IS"].get("net_bp", -1) > 0}
    rs = np.random.default_rng(64)
    sel, lines = [], set()
    for c in CELLS:
        cap = 400 if name(c) in full else 150
        for era in ERAS:
            K = era_rows(allrows[name(c)], era)
            idx = np.arange(len(K)) if len(K) <= cap else np.sort(rs.choice(len(K), cap, replace=False))
            for i in idx:
                r = K[i]
                sel.append((name(c), r["pi"], r["e"]))
                p = pairs[r["pi"]]
                for mk, sym in ((p["Amarket"], p["A"]), ("um", p["U"])):
                    tts = (r["te"] - M, r["te"] + M, r["te"] + 5 * M, r["tx"] + M)
                    if c[0] == "Q2b":
                        tts += (r["tx"] - 30 * M,)
                    for tt in tts:
                        lines.add((mk, sym, day_of(tt)))
    with open(os.path.join(OUT, "selection.csv"), "w") as f:
        w = csv.writer(f); w.writerow(["cell", "pi", "e"]); w.writerows(sel)
    with open(os.path.join(OUT, "need_m1.txt"), "w") as f:
        for x in sorted(lines):
            f.write(" ".join(x) + "\n")
    res["_selection"] = dict(best=best, full=sorted(full), trades=len(sel), days=len(lines))
    print("selection", res["_selection"], flush=True)
    with open(os.path.join(OUT, "cells_1h.json"), "w") as f:
        json.dump(dict(cells=res, nulls=nulls, reps=reps), f, indent=1, default=float)


if __name__ == "__main__":
    t0 = time.time()
    pairs = q.load()
    print("pairs", len(pairs), {k: sum(1 for p in pairs if p["kind"] == k) for k in ("Q1", "Q2")}, "load s",
          round(time.time() - t0), flush=True)
    if sys.argv[1] == "need":
        need(pairs)
    elif sys.argv[1] == "screen":
        screen(pairs, int(sys.argv[2]) if len(sys.argv) > 2 else 1000)
    else:
        grade(pairs, int(sys.argv[2]) if len(sys.argv) > 2 else 1000)
