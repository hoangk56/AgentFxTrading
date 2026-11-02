"""Stream UC analysis (rules declared in UC/HYPOTHESES_UC.md). A2 analyze.py trade / slip / fund / clt logic copied
unchanged; the only differences are the side multiplier (short categories: short alt / long BTC), entry d = 5 s, exits
N + 5 min and N + 60 min, events loaded across two UTC days when the window crosses midnight, and funding requests
clipped to < 2025-01-01. Reads research/data/upbit_census/npz only (plus local funding files)."""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
NPZ = os.path.join(net.D, "npz")
UC = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round68_upbit_census/UC"
H = 3600000
DAYMS = 86400000
END = 1735689600000
IS_END = 1640995200000
COST = 0.0020
OFFS = [-60, -30, -10, -5, -2, -1, 0, 1, 2, 3, 5, 10, 20, 30, 60, 120, 300, 600, 1800]
EXITS = {"5m": 300, "60m": 3600}
D = 5
LATE = 10
NS = 1000
_C = {}


def load1(sym, day):
    k = (sym, day)
    if k not in _C:
        p = os.path.join(NPZ, f"{sym}_{day}.npz")
        if not os.path.exists(p):
            _C[k] = None
        else:
            z = np.load(p)
            _C[k] = None if "miss" in z.files else {x: z[x] for x in z.files}
    return _C[k]


def days_of(N):
    a = (N - 600000) // DAYMS; b = (N + 3665000) // DAYMS
    return [str(np.datetime64(int(k * DAYMS), "ms"))[:10] for k in range(a, b + 1)]


def load(sym, N):
    parts = [load1(sym, d) for d in days_of(N)]
    if any(p is None for p in parts):
        return None
    if len(parts) == 1:
        return parts[0]
    return {"t": np.concatenate([p["t"] for p in parts]), "p": np.concatenate([p["p"] for p in parts])}


def at(S, T):
    i = np.searchsorted(S["t"], T, "right") - 1
    return S["p"][i] if i >= 0 else np.nan


def after(S, T):
    i = np.searchsorted(S["t"], T, "left")
    return (S["p"][i], int(S["t"][i])) if i < len(S["t"]) else (np.nan, None)


def slip(S, T):
    a, b = np.searchsorted(S["t"], [T, T + 60000])
    t, p = S["t"][a:b], S["p"][a:b]
    if not len(t):
        return np.nan
    bins = (t - T) // 1000
    rs = []
    for k in np.unique(bins):
        q = p[bins == k]; rs.append((q.max() - q.min()) / q.min())
    return 0.5 * float(np.median(rs))


_FU = {}


def fund(sym, a, b):
    if sym not in _FU:
        rows = []
        for sub in ("funding", "funding_window"):
            p = os.path.join(R, "binance", sub, sym + ".csv")
            if os.path.exists(p):
                rows += [(float(x["t"]), float(x["rate"])) for x in csv.DictReader(open(p))]
        _FU[sym] = np.array(sorted(set(r for r in rows if r[0] < END))) if rows else np.zeros((0, 2))
    F = _FU[sym]
    if not len(F) or F[:, 0].min() > a or F[:, 0].max() < b - 9 * H:
        e = min(b + DAYMS, END - 1)
        r, s = net.opener(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={a - DAYMS}&endTime={e}&limit=1000")
        body = r.read() if r else b"[]"
        if r:
            net.log(r.url, s, len(body), "GET"); r.close()
        js = json.loads(body)
        F = np.array([(float(x["fundingTime"]), float(x["fundingRate"])) for x in js if int(x["fundingTime"]) < END]) if js else np.zeros((0, 2))
        _FU[sym] = F
    if not len(F):
        return 0.0
    w = (F[:, 0] > a) & (F[:, 0] <= b)
    return float(F[w, 1].sum())


def clt(x, day):
    x = np.asarray(x, float); n = len(x); m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    return m, m / (np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n), n


def trade(e, d, X, A, B, side, costmul=1.0):
    """A2's trade(); side +1 = long alt / short BTC, -1 = short alt / long BTC (funding signs follow the side)."""
    N = e["N"]
    ae, te_a = after(A, N + d * 1000); be, te_b = after(B, N + d * 1000)
    ax, tx_a = after(A, X); bx, tx_b = after(B, X)
    if te_a is None or tx_a is None or te_b is None or tx_b is None or tx_a - X > 60000 or tx_b - X > 60000:
        return None
    sl = slip(A, te_a) + slip(A, tx_a) + slip(B, te_b) + slip(B, tx_b)
    gross = side * ((ax / ae - 1) - (bx / be - 1))
    f = side * (-fund(e["perp"], te_a, tx_a) + fund("BTCUSDT", te_b, tx_b))
    net_ = gross + f - costmul * (COST + sl)
    return dict(gross=gross, fund=f, slip=sl, net=net_, lag_a=(te_a - N) / 1000)


def load_events():
    out = []
    for r in csv.DictReader(open(os.path.join(UC, "pull_list.csv"))):
        N = int(r["N"]); assert N + 3665000 < END
        out.append(dict(nid=r["nid"], coin=r["coin"], perp=r["perp"], cat=r["cat"], side={"long": 1, "short": -1}.get(r["side"], 0),
                        N=N, era="IS" if N < IS_END else "VAL", year=r["N_utc"][:4], day=r["N_utc"][:10], testable=r["testable"] == "1"))
    return out


def main():
    E = load_events()
    out = open(os.path.join(UC, "results.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    rows = []
    for e in E:
        A = load(e["perp"], e["N"]); B = load("BTCUSDT", e["N"])
        if A is None or B is None:
            continue
        N = e["N"]
        ra, rb = at(A, N - 60000), at(B, N - 60000)
        if not (np.isfinite(ra) and np.isfinite(rb)):
            continue
        path = {o: float(np.log(at(A, N + o * 1000) / ra) - np.log(at(B, N + o * 1000) / rb)) for o in OFFS}
        row = dict(e, path=path)
        sd = e["side"] if e["side"] else 1
        for d in (D, LATE):
            for xn, x in EXITS.items():
                row[f"D{d}-{xn}"] = trade(e, d, N + x * 1000, A, B, sd)
                row[f"D{d}-{xn}-x15"] = trade(e, d, N + x * 1000, A, B, sd, 1.5)
        rows.append(row)
    cats = sorted(set(r["cat"] for r in rows))
    P("# Stream UC results (bp). Events with data:", len(rows), "of", len(E))
    for c in cats:
        for era in ("IS", "VAL"):
            S = [r for r in rows if r["cat"] == c and r["era"] == era]
            if not S:
                continue
            P(f"\n## Path {c} {era} (n {len(S)}, days {len(set(r['day'] for r in S))}): r(t) = ln alt/BTC since N - 60 s, bp, RAW sign (not side-adjusted): q25 / median / q75 / mean / median |r|")
            for o in OFFS:
                v = 1e4 * np.array([r["path"][o] for r in S]); v = v[np.isfinite(v)]
                P(f"  t {o:+5d}s  {np.percentile(v,25):7.0f} {np.median(v):7.0f} {np.percentile(v,75):7.0f} {v.mean():7.0f} {np.median(np.abs(v)):7.0f}")
            dv = 1e4 * np.array([r["path"][1800] - r["path"][5] for r in S]); dv = dv[np.isfinite(dv)]
            P(f"  move N+5s -> N+30min: mean {dv.mean():.0f}  median {np.median(dv):.0f}  median |.| {np.median(np.abs(dv)):.0f}")

    P("\n## Cells (testable categories; side-adjusted; net bp per trade; 20 bp + slippage + real funding; t clustered by notice day)")
    P("cell                era  n(days)  gross  slip  fund    net     t  median    SR   x1.5  late(d10)  years(net,n)                 power")
    cells = {}
    tcats = sorted(set(r["cat"] for r in rows if r["testable"]))
    nhold = json.load(open(os.path.join(UC, "nhold.json")))
    for c in tcats:
        for xn in EXITS:
            k = f"D{D}-{xn}"
            for era in ("IS", "VAL"):
                S = [r for r in rows if r["cat"] == c and r["era"] == era and r[k] is not None and r[f"D{LATE}-{xn}"] is not None]
                if len(S) < 3:
                    continue
                net_ = np.array([r[k]["net"] for r in S]); days = [r["day"] for r in S]
                m, t, n = clt(net_, days); sr = net_.mean() / net_.std(ddof=1)
                yrs = {}
                for r in S:
                    yrs.setdefault(r["year"], []).append(r[k]["net"])
                ys = " ".join(f"{y}:{1e4*np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
                pw = sr * np.sqrt(nhold[c]) if era == "VAL" else np.nan
                q = dict(n=n, days=len(set(days)), net=1e4 * m, t=t, sr=sr, gross=1e4 * np.mean([r[k]["gross"] for r in S]),
                         slip=1e4 * np.mean([r[k]["slip"] for r in S]), fund=1e4 * np.mean([r[k]["fund"] for r in S]),
                         median=1e4 * np.median(net_), x15=1e4 * np.mean([r[k + "-x15"]["net"] for r in S]),
                         late=1e4 * np.mean([r[f"D{LATE}-{xn}"]["net"] for r in S]), years=ys,
                         yrs_pos=f"{sum(np.mean(v) > 0 for v in yrs.values())}/{len(yrs)}", power=pw)
                cells[(c, xn, era)] = q
                P(f"{c+' '+k:19s} {era:4s} {n:3d}({q['days']:3d}) {q['gross']:6.1f} {q['slip']:5.1f} {q['fund']:5.1f} {q['net']:6.1f} {t:5.2f} {q['median']:6.1f} {sr:5.2f} {q['x15']:6.1f} {q['late']:6.1f}  {ys:30s} {pw:5.2f}")

    # random benchmark: same coin, same day, random seconds outside [N - 15 min, N + 75 min]; same hold; gross, side-adjusted
    rng = np.random.default_rng(68)
    P(f"\n## Random benchmark ({NS} draw sets; same coin / same UTC day of N, random second, same hold; side-adjusted gross; max-over-categories null)")
    G = {}
    for xn, x in EXITS.items():
        hold = x - D
        M = np.full((NS, len(rows)), np.nan)
        for j, r in enumerate(rows):
            if not r["testable"]:
                continue
            A = load1(r["perp"], r["day"]); B = load1("BTCUSDT", r["day"]); d0 = int(A["d0"])
            zs = [((q["N"] - 900000 - d0) // 1000, (q["N"] + 4500000 - d0) // 1000) for q in rows if q["perp"] == r["perp"] and q["day"] == r["day"]]
            u = np.arange(0, 86400 - hold)
            ok = np.ones(len(u), bool)
            for z0, z1 in zs:
                ok &= (u + hold < z0) | (u > z1)
            u = u[ok]
            u = u[np.isfinite(A["sec_p"][u]) & np.isfinite(B["sec_p"][u]) & np.isfinite(A["sec_p"][u + hold]) & (A["sec_n"][u] > 0)]
            if not len(u):
                continue
            s = rng.choice(u, NS)
            sd = r["side"] if r["side"] else 1
            M[:, j] = sd * ((A["sec_p"][s + hold] / A["sec_p"][s] - 1) - (B["sec_p"][s + hold] / B["sec_p"][s] - 1))
        G[xn] = M
    nullmax = {}
    for era in ("IS", "VAL"):
        maxt = np.full(NS, -np.inf)
        for c in tcats:
            for xn in EXITS:
                k = f"D{D}-{xn}"
                idx = [j for j, r in enumerate(rows) if r["cat"] == c and r["era"] == era and r[k] is not None and r[f"D{LATE}-{xn}"] is not None and np.isfinite(G[xn][0, j])]
                if (c, xn, era) not in cells or len(idx) < 3:
                    continue
                ev = np.mean([rows[j][k]["gross"] for j in idx])
                pct = 100 * np.mean(np.nanmean(G[xn][:, idx], 1) < ev)
                cells[(c, xn, era)]["rand_pct"] = pct
                cost = np.array([COST + rows[j][k]["slip"] for j in idx]); days = [rows[j]["day"] for j in idx]
                ts = np.array([clt(G[xn][s, idx] - cost, days)[1] for s in range(NS)])
                maxt = np.maximum(maxt, ts)
                P(f"  {c+' '+k:19s} {era:4s} event gross {1e4*ev:7.1f}  random mean {1e4*np.nanmean(G[xn][:, idx]):7.1f}  beats {pct:5.1f} %  (cell net t {cells[(c, xn, era)]['t']:.2f})")
        nullmax[era] = float(np.percentile(maxt, 95)) if np.isfinite(maxt).any() else float("nan")
        P(f"  {era}: 95th pct of the max-over-categories-and-exits net t under the random null = {nullmax[era]:.2f}")
    json.dump({"|".join(k): v for k, v in cells.items()} | {"nullmax": nullmax}, open(os.path.join(UC, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(UC, "trades.csv"), "w") as f:
        w = csv.writer(f)
        cols = [f"D{d}-{xn}" for d in (D, LATE) for xn in EXITS]
        w.writerow(["nid", "coin", "perp", "cat", "side", "era", "day", "N"] + [f"r{o}" for o in OFFS]
                   + [f"{c}_{q}" for c in cols for q in ("gross", "slip", "fund", "net")])
        for r in rows:
            w.writerow([r["nid"], r["coin"], r["perp"], r["cat"], r["side"], r["era"], r["day"], r["N"]]
                       + [round(1e4 * r["path"][o], 1) for o in OFFS]
                       + [("" if r[c] is None else round(1e4 * r[c][q], 1)) for c in cols for q in ("gross", "slip", "fund", "net")])
    out.close()


if __name__ == "__main__":
    main()
