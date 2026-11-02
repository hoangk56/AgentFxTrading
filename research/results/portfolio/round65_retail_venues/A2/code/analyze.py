"""Stream A2 analysis (rules declared in A2/HYPOTHESES_A2.md): price path around the Upbit notice stamp N from Binance
aggTrades, burst onset vs N, the 8 declared cells (d in 2/5/10/30 s x exit N + 5 min / L), robustness, random benchmark,
power. Reads research/data/upbit_latency/npz only (plus local funding files, fapi fundingRate if missing)."""
import csv, json, os, sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A2/code")
import numpy as np
import net
from events import load_events

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
NPZ = os.path.join(net.D, "npz")
OUTD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round65_retail_venues/A2"
H = 3600000
COST = 0.0020
DS = [2, 5, 10, 30]
LATE = {2: 5, 5: 10, 10: 30, 30: 60}
OFFS = [-60, -30, -10, -5, -2, -1, 0, 1, 2, 3, 5, 10, 20, 30, 60, 120, 300]
N_HOLD = 92
_C = {}


def load(sym, day):
    k = (sym, day)
    if k not in _C:
        z = np.load(os.path.join(NPZ, f"{sym}_{day}.npz"))
        _C[k] = {x: z[x] for x in z.files}
    return _C[k]


def at(S, T):  # last trade at or before T
    i = np.searchsorted(S["t"], T, "right") - 1
    return S["p"][i] if i >= 0 else np.nan


def after(S, T):  # first trade at or after T
    i = np.searchsorted(S["t"], T, "left")
    return (S["p"][i], int(S["t"][i])) if i < len(S["t"]) else (np.nan, None)


def slip(S, T):  # half the median 1 s range over bins with trades in [T, T + 60 s)
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


def fund(sym, a, b):  # sum of real funding rates at stamps in (a, b]
    if sym not in _FU:
        p = os.path.join(R, "binance", "funding", sym + ".csv")
        rows = []
        if os.path.exists(p):
            rows = [(float(x["t"]), float(x["rate"])) for x in csv.DictReader(open(p))]
        _FU[sym] = np.array(rows) if rows else np.zeros((0, 2))
    F = _FU[sym]
    if not len(F) or F[:, 0].min() > a or F[:, 0].max() < b - 9 * H:
        r, s = net.opener(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={a - 86400000}&endTime={b + 86400000}&limit=1000")
        body = r.read() if r else b"[]"
        if r:
            net.log(r.url, s, len(body), "GET"); r.close()
        js = json.loads(body)
        F = np.array([(float(x["fundingTime"]), float(x["fundingRate"])) for x in js]) if js else np.zeros((0, 2))
        _FU[sym] = F
    if not len(F):
        return 0.0
    w = (F[:, 0] > a) & (F[:, 0] <= b)
    return float(F[w, 1].sum())


def clt(x, day):
    x = np.asarray(x, float); n = len(x); m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    return m, m / (np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n), n


def trade(e, d, X, A, B, costmul=1.0):
    N = e["N"]
    ae, te_a = after(A, N + d * 1000); be, te_b = after(B, N + d * 1000)
    ax, tx_a = after(A, X); bx, tx_b = after(B, X)
    if te_a is None or tx_a is None or te_b is None or tx_b is None:
        return None
    sl = slip(A, te_a) + slip(A, tx_a) + slip(B, te_b) + slip(B, tx_b)
    gross = (ax / ae - 1) - (bx / be - 1)
    f = -fund(e["perp"], te_a, tx_a) + fund("BTCUSDT", te_b, tx_b)
    net_ = gross + f - costmul * (COST + sl)
    return dict(gross=gross, fund=f, slip=sl, net=net_, lag_a=(te_a - N) / 1000, hold=(tx_a - te_a) / 1000)


def main():
    E = load_events()
    out = open(os.path.join(OUTD, "results.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    rows = []
    for e in E:
        A = load(e["perp"], e["day"]); B = load("BTCUSDT", e["day"]); N = e["N"]
        ra, rb = at(A, N - 60000), at(B, N - 60000)
        path = {o: float(np.log(at(A, N + o * 1000) / ra) - np.log(at(B, N + o * 1000) / rb)) for o in OFFS}
        # onset (a): first alt trade with r >= 2 %
        a0, a1 = np.searchsorted(A["t"], [N - 300000, N + 300000])
        ta, pa = A["t"][a0:a1], A["p"][a0:a1]
        ib = np.searchsorted(B["t"], ta, "right") - 1
        r = np.log(pa / ra) - np.log(B["p"][ib] / rb)
        hit = np.where(r >= 0.02)[0]
        on_a = (ta[hit[0]] - N) / 1000 if len(hit) else None
        # onset (b): 1 s trade-count burst
        s0, s1 = np.searchsorted(A["t"], [N - 600000, N + 300000])
        bins = (A["t"][s0:s1] - (N - 600000)) // 1000
        cnt = np.bincount(bins, minlength=900)[:900]
        base = np.median(cnt[:540]); thr = max(10, 10 * base)
        w = np.where(cnt[300:] >= thr)[0]
        on_b = int(w[0]) - 300 if len(w) else None
        # completion: first time r reaches 50 % / 90 % of r(N + 60 s), from N - 60 s
        tgt = path[60]
        c0, c1 = np.searchsorted(A["t"], [N - 60000, N + 60000])
        tc, pc = A["t"][c0:c1], A["p"][c0:c1]
        rc = np.log(pc / ra) - np.log(B["p"][np.searchsorted(B["t"], tc, "right") - 1] / rb)
        comp = {}
        for fr in (0.5, 0.9):
            j = np.where(rc >= fr * tgt)[0] if tgt > 0 else []
            comp[fr] = (tc[j[0]] - N) / 1000 if len(j) else None
        n_pre = int(((A["t"] >= N - 60000) & (A["t"] < N)).sum())
        row = dict(e, path=path, on_a=on_a, on_b=on_b, base=float(base), c50=comp[0.5], c90=comp[0.9], n_pre60=n_pre)
        for d in DS + [60]:
            for xn, X in (("5m", N + 300000), ("L", e["L"])):
                row[f"D{d}-{xn}"] = trade(e, d, X, A, B)
                row[f"D{d}-{xn}-x15"] = trade(e, d, X, A, B, 1.5)
        rows.append(row)

    P("# Stream A2 results (bp unless noted). Events", len(rows), "IS", sum(r["era"] == "IS" for r in rows))
    P("\n## Per event: onset (s vs N), completion (s), path r (bp vs N - 60 s)")
    P("coin      era  day         N-L(min) base/s  onA    onB   c50    c90   r(-1)  r(0)  r(+2)  r(+5)  r(+10) r(+30) r(+60) r(+300)")
    for r in rows:
        f = lambda v: "  --  " if v is None else f"{v:6.1f}"
        p = r["path"]
        P(f"{r['coin']:9s} {r['era']:4s} {r['day']} {(r['L']-r['N'])/60000:7.1f} {r['base']:6.1f} {f(r['on_a'])} {f(r['on_b'])} {f(r['c50'])} {f(r['c90'])} "
          + " ".join(f"{1e4*p[o]:6.0f}" for o in (-1, 0, 2, 5, 10, 30, 60, 300)))
    for era in ("IS", "VAL"):
        S = [r for r in rows if r["era"] == era]
        P(f"\n## Path {era} (n {len(S)}): r(t) vs ref N - 60 s, bp: q25 / median / q75 / mean")
        for o in OFFS:
            v = 1e4 * np.array([r["path"][o] for r in S])
            P(f"  t {o:+5d}s  {np.percentile(v,25):7.0f} {np.median(v):7.0f} {np.percentile(v,75):7.0f} {v.mean():7.0f}")
        for k in ("on_a", "on_b", "c50", "c90"):
            v = np.array([r[k] for r in S if r[k] is not None])
            P(f"  {k}: n {len(v)}/{len(S)}  median {np.median(v):.1f} s  min {v.min():.1f}  max {v.max():.1f}  share < 0: {np.mean(v<0):.2f}")
        P(f"  trades in N-60..N (alt): median {np.median([r['n_pre60'] for r in S]):.0f}")

    P("\n## Cells (net bp per trade; costs 20 bp + slippage + real funding; t clustered by notice day)")
    P("cell     era  n(days)  gross   slip  fund    net      t   median   SR    x1.5   late   years(net)            power")
    cells = {}
    for d in DS:
        for xn in ("5m", "L"):
            c = f"D{d}-{xn}"
            for era in ("IS", "VAL"):
                S = [r for r in rows if r["era"] == era and r[c] is not None]
                net_ = np.array([r[c]["net"] for r in S]); days = [r["day"] for r in S]
                m, t, n = clt(net_, days); sr = net_.mean() / net_.std(ddof=1)
                x15 = np.mean([r[c + "-x15"]["net"] for r in S])
                late = np.mean([r[f"D{LATE[d]}-{xn}"]["net"] for r in S])
                yrs = {}
                for r in S:
                    yrs.setdefault(r["year"], []).append(r[c]["net"])
                ys = " ".join(f"{y}:{1e4*np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
                pw = sr * np.sqrt(N_HOLD) if era == "VAL" else np.nan
                cells[(c, era)] = dict(n=n, days=len(set(days)), net=1e4 * m, t=t, sr=sr, x15=1e4 * x15, late=1e4 * late,
                                       gross=1e4 * np.mean([r[c]["gross"] for r in S]), slip=1e4 * np.mean([r[c]["slip"] for r in S]),
                                       fund=1e4 * np.mean([r[c]["fund"] for r in S]), median=1e4 * np.median(net_),
                                       years=ys, yrs_pos=f"{sum(np.mean(v)>0 for v in yrs.values())}/{len(yrs)}", power=pw)
                q = cells[(c, era)]
                P(f"{c:8s} {era:4s} {n:3d}({q['days']:2d}) {q['gross']:7.0f} {q['slip']:5.0f} {q['fund']:5.0f} {q['net']:7.0f} {t:6.2f} {q['median']:7.0f} {sr:6.2f} {q['x15']:6.0f} {q['late']:6.0f}  {ys:22s} {pw:5.2f}")

    # random benchmark: same coin, same day, random seconds outside the event zone, same nominal hold
    rng = np.random.default_rng(65)
    NS = 1000
    P(f"\n## Random benchmark ({NS} draw sets, same coin / day, gross; percentile of the event gross mean; max-over-cells t null)")
    rand = {}
    for d in DS:
        for xn in ("5m", "L"):
            c = f"D{d}-{xn}"
            G = np.full((NS, len(rows)), np.nan)
            for j, r in enumerate(rows):
                A = load(r["perp"], r["day"]); B = load("BTCUSDT", r["day"]); d0 = int(A["d0"])
                hold = 300 - d if xn == "5m" else (r["L"] - r["N"]) // 1000 - d
                z0 = (r["N"] - 900000 - d0) // 1000; z1 = (max(r["N"] + 1800000, r["L"] + H) - d0) // 1000
                ok = np.array([u for u in range(0, 86400 - hold) if u + hold < z0 or u > z1])
                ok = ok[np.isfinite(A["sec_p"][ok]) & np.isfinite(B["sec_p"][ok]) & np.isfinite(A["sec_p"][ok + hold])]
                u = rng.choice(ok, NS)
                G[:, j] = (A["sec_p"][u + hold] / A["sec_p"][u] - 1) - (B["sec_p"][u + hold] / B["sec_p"][u] - 1)
            rand[c] = G
    best = {}
    for era in ("IS", "VAL"):
        idx = [j for j, r in enumerate(rows) if r["era"] == era]
        days = [rows[j]["day"] for j in idx]
        maxt = np.full(NS, -np.inf)
        for c, G in rand.items():
            ev = np.mean([rows[j][c]["gross"] for j in idx])
            pct = 100 * np.mean(G[:, idx].mean(1) < ev)
            cells[(c, era)]["rand_pct"] = pct
            cost = np.array([COST + rows[j][c]["slip"] for j in idx])
            ts = np.array([clt(G[s, idx] - cost, days)[1] for s in range(NS)])
            maxt = np.maximum(maxt, ts)
            P(f"  {c:8s} {era:4s} event gross {1e4*ev:7.0f}  random mean {1e4*G[:, idx].mean():6.0f}  beats {pct:5.1f} %")
        best[era] = float(np.percentile(maxt, 95))
        P(f"  {era}: 95th pct of max-over-8-cells net t under the random null = {best[era]:.2f}")
    json.dump({f"{c}|{e}": v for (c, e), v in cells.items()}, open(os.path.join(OUTD, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(OUTD, "trades.csv"), "w") as f:
        w = csv.writer(f)
        w.writerow(["coin", "era", "day", "N", "L", "on_a_s", "on_b_s", "c50_s", "c90_s"] + [f"r{o}" for o in OFFS]
                   + [f"{c}_{k}" for d in DS for c in (f"D{d}-5m", f"D{d}-L") for k in ("gross", "slip", "fund", "net")])
        for r in rows:
            w.writerow([r["coin"], r["era"], r["day"], r["N"], r["L"], r["on_a"], r["on_b"], r["c50"], r["c90"]]
                       + [round(1e4 * r["path"][o], 1) for o in OFFS]
                       + [round(1e4 * r[c][k], 1) for d in DS for c in (f"D{d}-5m", f"D{d}-L") for k in ("gross", "slip", "fund", "net")])
    out.close()


if __name__ == "__main__":
    main()
