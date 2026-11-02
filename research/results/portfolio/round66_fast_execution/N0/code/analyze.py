"""Round 66 N0 analysis (rules in ../HYPOTHESES_N0.md): first-hour path of new USDT-M perps, the 8 declared fade cells
(group NEW/OLD x k 1/5 min x X 5/10 %), measured costs, robustness, random benchmark (same coin days 2-30), power.
Reads research/data/perp_launch/{agg,k1m} and local funding files only. Writes ../out/report.txt, cells.json, trades.csv."""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import events as EV  # noqa: E402

R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
D = os.path.join(R, "data", "perp_launch")
FUND = os.path.join(R, "data", "binance")
OUTD = os.path.join(HERE, "..", "out")
os.makedirs(OUTD, exist_ok=True)
MIN, H, DAY = 60000, 3600000, 86400000
END = 1735689600000
KS, XS, GROUPS = (1, 5), (0.05, 0.10), ("NEW", "OLD")
FEE = 0.0010 + 0.0010 + 0.0002  # alt taker 2 x 5 bp, BTC taker 2 x 5 bp, BTC half-spread 2 x 1 bp
HOLD_YEARS, VAL_YEARS = 1.83, 3.0
TAU = [5, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200]  # seconds after T0
NS = 1000


def day_str(d0):
    return str(np.datetime64(int(d0), "ms"))[:10]


def at(A, T):
    i = np.searchsorted(A["t"], T, "right") - 1
    return A["p"][i] if i >= 0 else np.nan


def after(A, T, maxwait=60000):
    i = np.searchsorted(A["t"], T, "left")
    if i < len(A["t"]) and A["t"][i] - T <= maxwait:
        return A["p"][i], int(A["t"][i])
    return np.nan, None


def half_spread(A, t):
    for w in (1000, 5000, 30000):
        a, b = np.searchsorted(A["t"], [t, t + w])
        p, q, m = A["p"][a:b], A["q"][a:b], A["m"][a:b]
        if (~m).any() and m.any():
            vb = np.sum(p[~m] * q[~m]) / np.sum(q[~m]); vs = np.sum(p[m] * q[m]) / np.sum(q[m])
            return max(0.0, (vb - vs) / ((vb + vs) / 2) / 2), w
    a, b = np.searchsorted(A["t"], [t, t + 60000])
    tt, p = A["t"][a:b], A["p"][a:b]
    if not len(tt):
        return np.nan, -1
    bins = (tt - t) // 1000
    rs = [(p[bins == k].max() - p[bins == k].min()) / p[bins == k].min() for k in np.unique(bins)]
    return 0.5 * float(np.median(rs)), 60000


def vwap10k(A, t, buy, usd=10000.0):
    a, b = np.searchsorted(A["t"], [t, t + 60000])
    p, q, m = A["p"][a:b], A["q"][a:b], A["m"][a:b]
    sel = (~m) if buy else m  # buyer-taker trades fill a market buy
    p, q = p[sel], q[sel]
    if not len(p):
        return np.nan
    v = np.cumsum(p * q); j = int(np.searchsorted(v, usd)); j = min(j, len(p) - 1)
    return float(np.sum(p[:j + 1] * q[:j + 1]) / np.sum(q[:j + 1]))


_F = {}


def funding(sym):
    if sym not in _F:
        rows = []
        for sub in ("funding", "funding_window"):
            p = os.path.join(FUND, sub, sym + ".csv")
            if os.path.exists(p):
                rows = [(float(x["t"]), float(x["rate"])) for x in csv.DictReader(open(p))]
                break
        a = np.array(rows) if rows else np.zeros((0, 2))
        _F[sym] = a[a[:, 0] < END] if len(a) else a
    return _F[sym]


def fsum(sym, a, b):
    F = funding(sym)
    if not len(F):
        return 0.0
    w = (F[:, 0] > a) & (F[:, 0] <= b)
    return float(F[w, 1].sum())


def load_k(sym):
    p = os.path.join(D, "k1m", sym + ".npz")
    if not os.path.exists(p):
        return None
    z = np.load(p)
    return {k: z[k] for k in z.files}


BTC = load_k("BTCUSDT")


def btc_open(T):  # open of the BTC 1m bar containing T
    i = np.searchsorted(BTC["ot"], (T // MIN) * MIN)
    if i < len(BTC["ot"]) and BTC["ot"][i] == (T // MIN) * MIN:
        return BTC["o"][i]
    return np.nan


def clt(x, day):
    x = np.asarray(x, float); n = len(x)
    if n < 2:
        return (x.mean() if n else np.nan), np.nan, n
    m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    se = np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n
    return m, (m / se if se > 0 else np.nan), n


def trade(A, sym, T0, k, s, delay=2000, costmul=1.0, real=False):
    ae, te = after(A, T0 + k * MIN + delay)
    ax, tx = after(A, T0 + H)
    if te is None or tx is None:
        return None
    be, bx = btc_open(te), btc_open(tx)
    if not (np.isfinite(be) and np.isfinite(bx)):
        return None
    he, we = half_spread(A, te); hx, wx = half_spread(A, tx)
    fund = -s * fsum(sym, te, tx) + s * fsum("BTCUSDT", te, tx)
    if real:
        ae = vwap10k(A, te, buy=(s > 0)); ax = vwap10k(A, tx, buy=(s < 0))
        gross = s * (ax / ae - 1) - s * (bx / be - 1)
        return dict(net=gross + fund - FEE)
    gross = s * (ax / ae - 1) - s * (bx / be - 1)
    cost = FEE + he + hx
    return dict(gross=gross, fund=fund, he=he, hx=hx, we=we, cost=cost, net=gross + fund - costmul * cost,
                lag=(te - T0 - k * MIN) / 1000)


def random_pool(sym, d0, k, sign, X):
    K = load_k(sym)
    if K is None or not len(K["ot"]):
        return None
    ot, o, c = K["ot"], K["o"], K["c"]
    lo = np.searchsorted(ot, d0 + DAY); hi = np.searchsorted(ot, d0 + 30 * DAY)
    u = np.arange(lo, max(lo, hi - 60))
    u = u[(u + 59 < len(ot))]
    u = u[ot[u + 59] - ot[u] == 59 * MIN]
    if not len(u):
        return None
    bi = np.searchsorted(BTC["ot"], ot)
    okb = (bi < len(BTC["ot"])) & (BTC["ot"][np.minimum(bi, len(BTC["ot"]) - 1)] == ot)
    u = u[okb[u + k - 1] & okb[u + 59]]
    mv = np.log(c[u + k - 1] / o[u])
    side = -sign
    bc = BTC["c"]
    g = side * (c[u + 59] / c[u + k - 1] - 1) - side * (bc[bi[u + 59]] / bc[bi[u + k - 1]] - 1)
    same = np.sign(mv) == sign
    pool = g[same & (np.abs(mv) >= X)]
    small = False
    if len(pool) < 5:
        idx = np.where(same)[0]
        idx = idx[np.argsort(-np.abs(mv[idx]))[:10]]
        pool = g[idx]; small = True
    return pool, small


def main():
    E = EV.events()
    out = open(os.path.join(OUTD, "report.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    rows, miss = [], []
    for e in E:
        fn = os.path.join(D, "agg", f"{e['sym']}_{day_str(e['day0'])}.npz")
        if not os.path.exists(fn):
            miss.append((e["sym"], "no file")); continue
        z = np.load(fn)
        A = {k: z[k] for k in ("t", "p", "q", "m")}
        if not len(A["t"]):
            miss.append((e["sym"], "empty")); continue
        T0 = int(A["t"][0]); P0 = float(A["p"][0])
        if T0 - e["day0"] < 1000:
            miss.append((e["sym"], "first trade at 00:00:00")); continue
        r = dict(e, T0=T0, P0=P0, hhmm=str(np.datetime64(T0, "ms"))[11:19], files=list(z["files"]),
                 n2h=len(A["t"]), n1m=int(np.sum(A["t"] < T0 + MIN)))
        r["path"] = {tau: float(np.log(at(A, T0 + tau * 1000) / P0)) for tau in TAU}
        r["hs0"] = half_spread(A, T0)[0]
        for k in KS:
            m = float(np.log(at(A, T0 + k * MIN) / P0)); r[f"m{k}"] = m
            s = -1 if m > 0 else 1
            r[f"s{k}"] = s
            r[f"T{k}"] = trade(A, e["sym"], T0, k, s)
            r[f"T{k}x15"] = trade(A, e["sym"], T0, k, s, costmul=1.5)
            r[f"T{k}late"] = trade(A, e["sym"], T0, k, s, delay=62000)
            r[f"T{k}real"] = trade(A, e["sym"], T0, k, s, real=True)
            r[f"T{k}d0"] = trade(A, e["sym"], T0, k, s, delay=0)
            r[f"T{k}d10"] = trade(A, e["sym"], T0, k, s, delay=10000)
            ae, te = after(A, T0 + k * MIN + 2000)
            r[f"sp{k}"] = {tau: (float(s * np.log(at(A, te + tau * 1000) / ae)) if te else np.nan)
                           for tau in (1, 5, 30, 60, 300, 600, 1800, 3600 - 60 * k - 2)}
        rows.append(r)
    P("# Round 66 N0 results (bp unless noted). HOLD never loaded.")
    P(f"events in list {len(E)}, analysed {len(rows)}, missing {len(miss)}: {miss}")
    from collections import Counter
    P("analysed by era/group:", dict(Counter((r["era"], r["group"]) for r in rows)))
    P("launch clock (UTC hh:mm, top):", Counter(r["hhmm"][:5] for r in rows).most_common(8))
    P("second-of-minute of T0: share < 5 s", np.mean([int(r["hhmm"][6:8]) < 5 for r in rows]).round(2),
      " median trades in first minute", np.median([r["n1m"] for r in rows]))

    P("\n## Path ln(P(T0 + tau) / P0), bp: median [q25, q75] (mean |.|), by era x group")
    for era in ("IS", "VAL"):
        for g in GROUPS + ("ALL",):
            S = [r for r in rows if r["era"] == era and (g == "ALL" or r["group"] == g)]
            P(f"  {era} {g} n {len(S)}")
            for tau in TAU:
                v = 1e4 * np.array([r["path"][tau] for r in S])
                v = v[np.isfinite(v)]
                P(f"    +{tau:5d}s  {np.median(v):7.0f} [{np.percentile(v, 25):6.0f}, {np.percentile(v, 75):6.0f}]  mean|.| {np.mean(np.abs(v)):6.0f}")
            hs = 1e4 * np.array([r["hs0"] for r in S]); hs = hs[np.isfinite(hs)]
            P(f"    half-spread in the first second after T0: median {np.median(hs):.0f}, mean {hs.mean():.0f}")
    P("\n## Share of events with |m_k| >= X (by era x group)")
    for era in ("IS", "VAL"):
        for g in GROUPS:
            S = [r for r in rows if r["era"] == era and r["group"] == g]
            P(f"  {era} {g} n {len(S)}: " + "  ".join(f"k{k} X{int(X*100)}: {np.mean([abs(r[f'm{k}']) >= X for r in S]):.2f} "
                                                      f"(up {np.mean([r[f'm{k}'] >= X for r in S]):.2f})" for k in KS for X in XS))

    def cell_rows(era, g, k, X):
        return [r for r in rows if r["era"] == era and (g == "ALL" or r["group"] == g) and abs(r[f"m{k}"]) >= X
                and r[f"T{k}"] is not None]

    P("\n## Cells: net bp / trade (fees 22 bp + measured alt half-spread at entry and exit + real funding); t clustered by launch day")
    P("cell              era  n(days) gross  hs_e  hs_x  fund    net      t  median   SR   x1.5   late  real$10k d0     d10   up / down (n)        years                         power")
    cells = {}
    for g in GROUPS + ("ALL",):
        for k in KS:
            for X in XS:
                name = f"{g}-k{k}-X{int(X * 100)}"
                for era in ("IS", "VAL"):
                    S = cell_rows(era, g, k, X)
                    if not S:
                        P(f"{name:17s} {era:4s} n 0"); continue
                    net = np.array([r[f"T{k}"]["net"] for r in S]); days = [r["day0"] for r in S]
                    m, t, n = clt(net, days)
                    sr = net.mean() / net.std(ddof=1) if n > 1 else np.nan
                    # real-fill rows: an event with no aggressor-side trade within 60 s of a fill is left out (nanmean)
                    f = lambda key: 1e4 * np.nanmean([r[key]["net"] for r in S if r[key] is not None])
                    yrs = {}
                    for r in S:
                        yrs.setdefault(r["year"], []).append(r[f"T{k}"]["net"])
                    ys = " ".join(f"{y}:{1e4 * np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
                    up = [r[f"T{k}"]["net"] for r in S if r[f"m{k}"] > 0]; dn = [r[f"T{k}"]["net"] for r in S if r[f"m{k}"] < 0]
                    pw = sr * np.sqrt(n / VAL_YEARS * HOLD_YEARS) if era == "VAL" else np.nan
                    q = dict(n=n, days=len(set(days)), net=1e4 * m, t=t, sr=sr, median=1e4 * np.median(net),
                             gross=1e4 * np.mean([r[f"T{k}"]["gross"] for r in S]), he=1e4 * np.mean([r[f"T{k}"]["he"] for r in S]),
                             hx=1e4 * np.mean([r[f"T{k}"]["hx"] for r in S]), fund=1e4 * np.mean([r[f"T{k}"]["fund"] for r in S]),
                             he_med=1e4 * np.median([r[f"T{k}"]["he"] for r in S]),
                             x15=f(f"T{k}x15"), late=f(f"T{k}late"), real=f(f"T{k}real"), d0=f(f"T{k}d0"), d10=f(f"T{k}d10"),
                             up=1e4 * np.mean(up) if up else np.nan, nup=len(up), dn=1e4 * np.mean(dn) if dn else np.nan, ndn=len(dn),
                             years=ys, yrs_pos=f"{sum(np.mean(v) > 0 for v in yrs.values())}/{len(yrs)}", power=pw,
                             worst=1e4 * net.min(), best=1e4 * net.max())
                    cells[(name, era)] = q
                    P(f"{name:17s} {era:4s} {n:3d}({q['days']:3d}) {q['gross']:6.0f} {q['he']:5.0f} {q['hx']:5.0f} {q['fund']:5.0f} {q['net']:6.0f} {t:6.2f} {q['median']:6.0f} {sr:5.2f} {q['x15']:6.0f} {q['late']:6.0f} {q['real']:6.0f} {q['d0']:6.0f} {q['d10']:6.0f}  {q['up']:+5.0f}({len(up)}) / {q['dn']:+5.0f}({len(dn)})  {ys:30s} {pw:5.2f}")
                    P(f"{'':17s}      worst {q['worst']:.0f} best {q['best']:.0f} median entry half-spread {q['he_med']:.1f}")

    P("\n## Side-signed path after the entry (bp, ln(P(te + tau) / P_entry) x side): median / mean, declared cells pooled over groups")
    for k in KS:
        for X in XS:
            for era in ("IS", "VAL"):
                S = cell_rows(era, "ALL", k, X)
                taus = list(S[0][f"sp{k}"].keys()) if S else []
                P(f"  k{k} X{int(X*100)} {era} n {len(S)}: " + "  ".join(
                    f"+{tau}s {np.nanmedian([r[f'sp{k}'][tau] for r in S])*1e4:.0f}/{np.nanmean([r[f'sp{k}'][tau] for r in S])*1e4:.0f}" for tau in taus))

    # random benchmark
    rng = np.random.default_rng(6602)
    P(f"\n## Random benchmark: same coin, days 2-30, same-sign k-min 1m move >= X, fade to u + 60 min, BTC-hedged gross ({NS} draw sets)")
    pools = {}
    nsmall = Counter()
    for r in rows:
        for k in KS:
            for X in XS:
                if abs(r[f"m{k}"]) >= X and r[f"T{k}"] is not None:
                    res = random_pool(r["sym"], r["day0"], k, np.sign(r[f"m{k}"]), X)
                    pools[(r["sym"], k, X)] = res
                    if res is None or res[1]:
                        nsmall[(k, X, "none" if res is None else "small")] += 1
    P("  pools missing / small (k, X):", dict(nsmall))
    maxt = {era: np.full(NS, -np.inf) for era in ("IS", "VAL")}
    realmax = {"IS": -np.inf, "VAL": -np.inf}
    for g in GROUPS + ("ALL",):
        for k in KS:
            for X in XS:
                name = f"{g}-k{k}-X{int(X * 100)}"
                for era in ("IS", "VAL"):
                    S = [r for r in cell_rows(era, g, k, X) if pools.get((r["sym"], k, X)) is not None]
                    if len(S) < 2:
                        continue
                    G = np.array([rng.choice(pools[(r["sym"], k, X)][0], NS) for r in S]).T  # NS x n
                    ev = np.mean([r[f"T{k}"]["gross"] for r in S])
                    pct = 100 * np.mean(G.mean(1) < ev)
                    cells[(name, era)]["rand_pct"] = pct
                    cells[(name, era)]["rand_mean"] = 1e4 * G.mean()
                    cells[(name, era)]["rand_n"] = len(S)
                    P(f"  {name:17s} {era:4s} n {len(S):3d} event gross {1e4 * ev:7.0f}  random mean {1e4 * G.mean():6.0f}  beats {pct:5.1f} %")
                    if g != "ALL":
                        cost = np.array([r[f"T{k}"]["cost"] - r[f"T{k}"]["fund"] for r in S])
                        days = [r["day0"] for r in S]
                        ts = np.array([clt(G[j] - cost, days)[1] for j in range(NS)])
                        ts = np.where(np.isfinite(ts), ts, -np.inf)
                        maxt[era] = np.maximum(maxt[era], ts)
                        realmax[era] = max(realmax[era], cells[(name, era)]["t"])
    for era in ("IS", "VAL"):
        P(f"  {era}: max-over-8-cells net t: real {realmax[era]:.2f}; random null median {np.median(maxt[era]):.2f}, p95 {np.percentile(maxt[era], 95):.2f}")

    json.dump({f"{c}|{e}": v for (c, e), v in cells.items()}, open(os.path.join(OUTD, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(OUTD, "trades.csv"), "w") as f:
        w = csv.writer(f)
        w.writerow(["sym", "era", "group", "year", "T0_utc", "P0", "n_first_min"] + [f"path{t}s" for t in TAU]
                   + [f"{x}{k}" for k in KS for x in ("m", "side", "net", "gross", "he", "hx", "fund")])
        for r in rows:
            rr = [r["sym"], r["era"], r["group"], r["year"], str(np.datetime64(r["T0"], "ms")), r["P0"], r["n1m"]]
            rr += [round(1e4 * r["path"][t], 1) for t in TAU]
            for k in KS:
                T = r[f"T{k}"]
                rr += [round(1e4 * r[f"m{k}"], 1), r[f"s{k}"]] + ([round(1e4 * T[x], 1) for x in ("net", "gross", "he", "hx", "fund")] if T else [""] * 5)
            w.writerow(rr)
    out.close()


if __name__ == "__main__":
    main()
