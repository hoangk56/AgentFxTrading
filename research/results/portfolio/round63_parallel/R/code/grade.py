"""Stream R grading: 30 declared cells (+ JPALL info), eras PRE / IS / VAL, random benchmark, max-over-cells null.
Usage: python -I grade.py [n_rand=1000] [n_null=200]. Writes ../out/grade.json and ../out/grade.txt."""
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import load, events, POOLS, RULES, ERAS, COST_SIDE, nw_t, moddur, TEN_YEARS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
os.makedirs(OUT, exist_ok=True)
NR = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
NN = int(sys.argv[2]) if len(sys.argv) > 2 else 200
HOLD_Y, VAL_Y = 1.83, 3.0

C, EV = load()
E, ADAY = events(C, EV)
# union calendar
U = sorted(set(d for c in C.values() for d in c.dates))
UIDX = {d: i for i, d in enumerate(U)}
UYEAR = np.array([int(d[:4]) for d in U])
MAP = {c: np.array([UIDX[d] for d in C[c].dates]) for c in C}

CELLS = [(r, p, "") for r in RULES for p in ("US", "JP10", "DE10", "ALL")]
CELLS += [("PRE5-0", p, "SIZE") for p in ("US", "ALL")] + [("POST3", p, "SIZE") for p in ("US", "ALL")]
CELLS += [("POST3", p, "WEAK") for p in ("US", "ALL")]
INFO = [(r, "JPALL", "") for r in RULES]


def tables(c, ten, rule, mult, late):
    """per-anchor arrays over country dates: net, gross, entry index; NaN if invalid."""
    Cc = C[c]; y = Cc.y[ten]; n = len(y); legs = RULES[rule]
    gross = np.zeros(n); carry = np.zeros(n); ok = np.ones(n, bool)
    a = np.arange(n)
    for (o0, o1, s) in legs:
        i0, i1 = a + o0 + late, a + o1 + late
        v = (i0 >= 0) & (i1 < n)
        i0c, i1c = np.clip(i0, 0, n - 1), np.clip(i1, 0, n - 1)
        seg_ok = v.copy()
        for k in range(o0, o1 + 1):
            ik = np.clip(a + k + late, 0, n - 1)
            seg_ok &= ~np.isnan(y[ik])
        ok &= seg_ok
        y0, y1 = y[i0c], y[i1c]
        gross += -s * (y1 - y0) * 100.0
        f = np.where(np.isnan(Cc.fin[i0c]), y0, Cc.fin[i0c])
        md = np.array([moddur(TEN_YEARS[ten], v_ / 100.0) if not np.isnan(v_) else 1.0 for v_ in y0])
        days = Cc.ord[i1c] - Cc.ord[i0c]
        carry += s * (y0 - f) * 100.0 * days / 365.0 / md
    cost = COST_SIDE * 2 * len(legs) * mult
    net = np.where(ok, gross + carry - cost, np.nan)
    gross = np.where(ok, gross, np.nan)
    entry = a + legs[0][0] + late
    return net, gross, carry, entry


TB = {}


def tb(c, ten, rule, mult=1.0, late=0):
    k = (c, ten, rule, mult, late)
    if k not in TB: TB[k] = tables(c, ten, rule, mult, late)
    return TB[k]


def dy(c, ten):
    y = C[c].y[ten]; d = np.full(len(y), np.nan); d[1:] = np.diff(y) * 100.0
    return d


DY = {}


def book(evs, anchors, rule, mult=1.0, late=0):
    """daily union book (gross pieces + (carry - cost) spread) and per-trade arrays (net, gross, entry year)."""
    bk = np.zeros(len(U)); nets, gros, yrs = [], [], []
    legs = RULES[rule]; npc = sum(o1 - o0 for o0, o1, _ in legs)
    groups = {}
    for e, a in zip(evs, anchors):
        groups.setdefault((e["c"], e["ten"]), []).append(a)
    for (c, ten), A in groups.items():
        A = np.array(A)
        net, gross, carry, entry = tb(c, ten, rule, mult, late)
        okm = ~np.isnan(net[A]); A = A[okm]
        if len(A) == 0: continue
        if (c, ten) not in DY: DY[(c, ten)] = dy(c, ten)
        d_ = DY[(c, ten)]
        extra = (net[A] - gross[A]) / npc
        for (o0, o1, s) in legs:
            for k in range(o0 + 1, o1 + 1):
                ik = A + k + late
                np.add.at(bk, MAP[c][ik], -s * d_[ik] + extra)
        nets.append(net[A]); gros.append(gross[A]); yrs.append(C[c].years[entry[A]])
    if not nets: return bk, np.array([]), np.array([]), np.array([], int)
    return bk, np.concatenate(nets), np.concatenate(gros), np.concatenate(yrs)


def cell_events(pool, cond):
    ev = [e for e in E if POOLS[pool](e)]
    if cond == "SIZE": ev = [e for e in ev if e["size"]]
    if cond == "WEAK": ev = [e for e in ev if e["weak"]]
    return ev


def era_stats(bk, nets, gros, yrs, era):
    a, b = ERAS[era]
    m = (yrs >= a) & (yrs <= b)
    um = (UYEAR >= a) & (UYEAR <= b)
    x = bk[um]
    sd = x.std()
    res = dict(n=int(m.sum()), mid=float(np.mean(gros[m])) if m.any() else float("nan"),
               net=float(np.mean(nets[m])) if m.any() else float("nan"),
               sd_tr=float(np.std(nets[m])) if m.sum() > 1 else float("nan"),
               t=nw_t(x), ann_sr=float(x.mean() / sd * math.sqrt(252)) if sd > 0 else float("nan"))
    yp = {int(yy): float(bk[UYEAR == yy].sum()) for yy in range(a, b + 1)}
    res["years"] = yp
    return res


# candidate random anchors: non-auction days of the country, by year
CAND = {}
for c in C:
    for yy in range(2003, 2025):
        idx = np.where(C[c].years == yy)[0]
        CAND[(c, yy)] = np.array([i for i in idx if i not in ADAY[c]])
rng = np.random.default_rng(63063)


def rand_anchors(evs, r):
    out = np.empty(len(evs), int)
    for j, e in enumerate(evs):
        cand = CAND[(e["c"], int(e["d"][:4]))]
        out[j] = cand[r.integers(len(cand))]
    return out



def main():
    res = {}
    lines = []
    for cell in CELLS + INFO:
        rule, pool, cond = cell
        evs = cell_events(pool, cond)
        A = np.array([e["i0"] for e in evs])
        out = {}
        for tag, mult, late in (("base", 1.0, 0), ("cost15", 1.5, 0), ("late", 1.0, 1)):
            bk, nets, gros, yrs = book(evs, A, rule, mult, late)
            out[tag] = {era: era_stats(bk, nets, gros, yrs, era) for era in ERAS}
        # random benchmark: mean net per trade, per era, NR seeds (lookup tables)
        bk, nets, gros, yrs = book(evs, A, rule)
        rr = {era: [] for era in ERAS}
        groups = {}
        for j, e in enumerate(evs): groups.setdefault((e["c"], e["ten"]), []).append(j)
        eyr = np.array([int(e["d"][:4]) for e in evs])
        for s in range(NR):
            RA = rand_anchors(evs, rng)
            vals = np.full(len(evs), np.nan)
            for (c, ten), js in groups.items():
                js = np.array(js); vals[js] = tb(c, ten, rule)[0][RA[js]]
            for era, (a, b) in ERAS.items():
                m = (eyr >= a) & (eyr <= b)
                rr[era].append(np.nanmean(vals[m]))
        for era in ERAS:
            out["base"][era]["rand_pct"] = float(np.mean(np.array(rr[era]) < out["base"][era]["net"]) * 100)
            out["base"][era]["rand_mean"] = float(np.mean(rr[era]))
        v = out["base"]["VAL"]
        n_hold = v["n"] / VAL_Y * HOLD_Y
        p_tr = (v["net"] / v["sd_tr"]) * math.sqrt(n_hold) if v["sd_tr"] and v["sd_tr"] > 0 else float("nan")
        p_bk = v["t"] * math.sqrt(HOLD_Y / VAL_Y)
        out["power"] = dict(per_trade=p_tr, book=p_bk, power=min(p_tr, p_bk))
        key = f"{rule}|{pool}|{cond}"
        res[key] = out
        print(key, "done", flush=True)

    # max-over-cells null on IS t (book), NN random calendars, same draw per event across cells
    rng2 = np.random.default_rng(4141)
    EID = {id(e): j for j, e in enumerate(E)}
    maxt = []
    for s in range(NN):
        RA_all = rand_anchors(E, rng2)
        ts = []
        for (rule, pool, cond) in CELLS:
            evs = cell_events(pool, cond)
            A = RA_all[[EID[id(e)] for e in evs]]
            bk, nets, gros, yrs = book(evs, A, rule)
            um = (UYEAR >= 2016) & (UYEAR <= 2021)
            ts.append(nw_t(bk[um]))
        maxt.append(max(ts))
    maxt = np.array(maxt)
    res["_null"] = dict(n=NN, median=float(np.median(maxt)), p95=float(np.percentile(maxt, 95)))
    json.dump(res, open(f"{OUT}/grade.json", "w"), indent=1)


    def f(x, k=2):
        return "nan" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.{k}f}"


    L = ["cell | PRE mid/net (t) | IS n mid/net (t) SR | VAL n mid/net (t) SR | rand IS/VAL % | x1.5 IS/VAL t | late IS/VAL net (t) | yrs+ 16-24 | power"]
    for key, o in res.items():
        if key.startswith("_"): continue
        b = o["base"]; P, I, V = b["PRE"], b["IS"], b["VAL"]
        yrs = {**I["years"], **V["years"]}
        ypos = sum(1 for v in yrs.values() if v > 0)
        L.append(f"{key} | {f(P['mid'])}/{f(P['net'])} ({f(P['t'])}) | {I['n']} {f(I['mid'])}/{f(I['net'])} ({f(I['t'])}) {f(I['ann_sr'])}"
                 f" | {V['n']} {f(V['mid'])}/{f(V['net'])} ({f(V['t'])}) {f(V['ann_sr'])} | {I['rand_pct']:.0f}/{V['rand_pct']:.0f}"
                 f" | {f(o['cost15']['IS']['t'])}/{f(o['cost15']['VAL']['t'])} | {f(o['late']['IS']['net'])} ({f(o['late']['IS']['t'])})/{f(o['late']['VAL']['net'])} ({f(o['late']['VAL']['t'])})"
                 f" | {ypos}/9 | {f(o['power']['power'])}")
    L.append(f"max IS t over {len(CELLS)} cells, {NN} random calendars: median {res['_null']['median']:.2f}, p95 {res['_null']['p95']:.2f}")
    open(f"{OUT}/grade.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
