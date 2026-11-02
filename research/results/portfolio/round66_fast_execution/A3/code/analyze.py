"""Stream A3 analysis (declared in A3/HYPOTHESES_A3.md): A2-D5L with the alt leg on Binance SPOT. Path around N,
onset, the frozen cell (long spot / short BTCUSDT perp at the first trades >= N + 5 s, exit at the first trades >= L),
unhedged long, costs x1.5, one step late (N + 10 s), random benchmark, capacity. Functions after / at / slip / clt and
the random draw copied from round65 A2/code/analyze.py. Reads research/data/upbit_spot_notice/npz (+ A2's BTCUSDT npz,
read-only) and the local BTCUSDT funding file."""
import csv, json, os, sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3/code")
import numpy as np
from pull import load_events, OUT as NPZ, A2NPZ

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
OUTD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A3"
H = 3600000
FEE_H = 0.0030  # spot 10 bp x 2 + perp 5 bp x 2
FEE_U = 0.0020  # spot 10 bp x 2
CASH = 0.05  # spot leg cash cost per year (reported only)
OFFS = [-60, -30, -10, -5, -2, -1, 0, 1, 2, 3, 5, 10, 20, 30, 60, 120, 300]
_C = {}


def load(kind, sym, day):
    k = (kind, sym, day)
    if k not in _C:
        p = os.path.join(NPZ, f"{kind}_{sym}_{day}.npz")
        if not os.path.exists(p):
            p = os.path.join(A2NPZ, f"{sym}_{day}.npz"); assert kind == "perp"
        z = np.load(p)
        _C[k] = {x: z[x] for x in z.files}
    return _C[k]


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
    rs = [(p[bins == k].max() - p[bins == k].min()) / p[bins == k].min() for k in np.unique(bins)]
    return 0.5 * float(np.median(rs))


_F = None


def fund_btc(a, b):
    global _F
    if _F is None:
        rows = [(float(x["t"]), float(x["rate"])) for x in csv.DictReader(open(os.path.join(R, "binance", "funding", "BTCUSDT.csv")))]
        _F = np.array([r for r in rows if r[0] < 1735689600000])
    assert _F[:, 0].min() < a and _F[:, 0].max() > b
    w = (_F[:, 0] > a) & (_F[:, 0] <= b)
    return float(_F[w, 1].sum())


def clt(x, day):
    x = np.asarray(x, float); n = len(x); m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    if n < 2:
        return m, np.nan, n
    return m, m / (np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n), n


def trade(e, d, X, A, B, costmul=1.0, hedge=True):
    N = e["N"]
    ae, te_a = after(A, N + d * 1000); be, te_b = after(B, N + d * 1000)
    ax, tx_a = after(A, X); bx, tx_b = after(B, X)
    if None in (te_a, tx_a, te_b, tx_b):
        return None
    hold = (tx_a - te_a) / 1000
    if hedge:
        sl = slip(A, te_a) + slip(A, tx_a) + slip(B, te_b) + slip(B, tx_b)
        gross = (ax / ae - 1) - (bx / be - 1); f = fund_btc(te_b, tx_b); fee = FEE_H
    else:
        sl = slip(A, te_a) + slip(A, tx_a); gross = ax / ae - 1; f = 0.0; fee = FEE_U
    net_ = gross + f - costmul * (fee + sl)
    return dict(gross=gross, fund=f, slip=sl, slip_entry_spot=slip(A, te_a), net=net_, lag_a=(te_a - N) / 1000,
                lag_b=(te_b - N) / 1000, hold=hold, cash=CASH * hold / (365 * 86400))


def stats(S, c):
    v = np.array([r[c]["net"] for r in S]); days = [r["day"] for r in S]
    m, t, n = clt(v, days)
    sr = v.mean() / v.std(ddof=1) if n > 1 else np.nan
    yrs = {}
    for r in S:
        yrs.setdefault(r["year"], []).append(r[c]["net"])
    return dict(n=n, days=len(set(days)), net=1e4 * m, t=t, sr=sr, median=1e4 * np.median(v),
                gross=1e4 * np.mean([r[c]["gross"] for r in S]), slip=1e4 * np.mean([r[c]["slip"] for r in S]),
                fund=1e4 * np.mean([r[c]["fund"] for r in S]), cash=1e4 * np.mean([r[c]["cash"] for r in S]),
                years=" ".join(f"{y}:{1e4*np.mean(x):+.0f}({len(x)})" for y, x in sorted(yrs.items())),
                yrs_pos=f"{sum(np.mean(x) > 0 for x in yrs.values())}/{len(yrs)}")


def main():
    E = load_events()
    out = open(os.path.join(OUTD, "results.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    rows = []
    for e in E:
        A = load("spot", e["spot"], e["day"]); B = load("perp", "BTCUSDT", e["day"]); N = e["N"]
        ra, rb = at(A, N - 60000), at(B, N - 60000)
        path = {o: float(np.log(at(A, N + o * 1000) / ra) - np.log(at(B, N + o * 1000) / rb)) for o in OFFS}
        raw = {o: float(np.log(at(A, N + o * 1000) / ra)) for o in OFFS}
        a0, a1 = np.searchsorted(A["t"], [N - 300000, N + 300000])
        ta, pa = A["t"][a0:a1], A["p"][a0:a1]
        r_ = np.log(pa / ra) - np.log(B["p"][np.searchsorted(B["t"], ta, "right") - 1] / rb)
        hit = np.where(r_ >= 0.02)[0]
        on_a = (ta[hit[0]] - N) / 1000 if len(hit) else None
        tgt = path[60]; comp = {}
        c0, c1 = np.searchsorted(A["t"], [N - 60000, N + 60000])
        tc, pc = A["t"][c0:c1], A["p"][c0:c1]
        rc = np.log(pc / ra) - np.log(B["p"][np.searchsorted(B["t"], tc, "right") - 1] / rb)
        for fr in (0.5, 0.9):
            j = np.where(rc >= fr * tgt)[0] if tgt > 0 else []
            comp[fr] = (tc[j[0]] - N) / 1000 if len(j) else None
        n_pre = int(((A["t"] >= N - 60000) & (A["t"] < N)).sum())
        # capacity: buyer-taker spot notional (USDT) in the 1 s / 5 s after N + 5 s; is_buyer_maker == 0 -> buyer took
        cap = {}
        for w in (1, 5):
            k0, k1 = np.searchsorted(A["t"], [N + 5000, N + 5000 + w * 1000])
            sel = A["m"][k0:k1] == 0
            cap[w] = float((A["p"][k0:k1][sel] * A["q"][k0:k1][sel]).sum())
        pre_rng = slip(A, N - 600000)  # half median 1 s range in N - 10 min .. N - 9 min (calm baseline)
        row = dict(e, path=path, raw=raw, on_a=on_a, c50=comp[0.5], c90=comp[0.9], n_pre60=n_pre, cap1=cap[1], cap5=cap[5],
                   pre_slip=pre_rng)
        for d in (2, 5, 10, 30):
            row[f"H{d}"] = trade(e, d, e["L"], A, B)
            row[f"U{d}"] = trade(e, d, e["L"], A, B, hedge=False)
        row["H5x15"] = trade(e, 5, e["L"], A, B, 1.5)
        row["U5x15"] = trade(e, 5, e["L"], A, B, 1.5, hedge=False)
        rows.append(row)

    P("# Stream A3 results (bp unless noted). main = declared event set (5, all IS); info = JST / T / GAL (never for a verdict)")
    P("\n## Per event: onset a (s vs N), completion of r(N+60 s) (s), path r = spot vs BTC (bp vs N - 60 s), capacity")
    P("coin set  era day        L-N(min) pre60n onA    c50    c90   r(-1) r(0) r(+1) r(+2) r(+5) r(+10) r(+30) r(+60) r(+300) raw(+5) raw(+60)  cap1s($)  cap5s($) slipE(bp) base(bp)")
    f = lambda v: "  --  " if v is None else f"{v:6.1f}"
    for r in rows:
        p = r["path"]
        P(f"{r['coin']:5s} {r['set']:4s} {r['era']:3s} {r['day']} {(r['L']-r['N'])/60000:7.1f} {r['n_pre60']:5d} {f(r['on_a'])} {f(r['c50'])} {f(r['c90'])} "
          + " ".join(f"{1e4*p[o]:5.0f}" for o in (-1, 0, 1, 2, 5, 10, 30, 60, 300))
          + f" {1e4*r['raw'][5]:6.0f} {1e4*r['raw'][60]:6.0f} {r['cap1']:9.0f} {r['cap5']:9.0f} {1e4*r['H5']['slip_entry_spot']:7.1f} {1e4*r['pre_slip']:6.1f}")
    for nm, S in (("main IS (n 5)", [r for r in rows if r["set"] == "main"]), ("all 8 (main + info, 2020-24)", rows)):
        P(f"\n## Path {nm}: r(t) spot vs BTC, bp vs N - 60 s: q25 / median / q75 / mean | raw spot median")
        for o in OFFS:
            v = 1e4 * np.array([r["path"][o] for r in S]); w = 1e4 * np.array([r["raw"][o] for r in S])
            P(f"  t {o:+5d}s  {np.percentile(v,25):7.0f} {np.median(v):7.0f} {np.percentile(v,75):7.0f} {v.mean():7.0f} | {np.median(w):7.0f}")
        for k in ("on_a", "c50", "c90"):
            v = np.array([r[k] for r in S if r[k] is not None])
            if len(v):
                P(f"  {k}: n {len(v)}/{len(S)}  median {np.median(v):.1f} s  min {v.min():.1f}  max {v.max():.1f}")

    P("\n## Per-event trades (net bp; hedged H = long spot / short BTC perp, 30 bp + 4 slips + BTC funding; U = unhedged long, 20 bp + 2 slips)")
    P("coin set  era  hold(min) lagA(s) lagB(s)  H5 gross  slip   fund   H5 net  H10 net  H5x1.5 |  U5 net  U10 net | H2 net H30 net")
    for r in rows:
        h = r["H5"]
        P(f"{r['coin']:5s} {r['set']:4s} {r['era']:3s} {h['hold']/60:8.1f} {h['lag_a']:6.2f} {h['lag_b']:6.2f} {1e4*h['gross']:8.0f} {1e4*h['slip']:5.0f} {1e4*h['fund']:6.1f} "
          f"{1e4*h['net']:8.0f} {1e4*r['H10']['net']:8.0f} {1e4*r['H5x15']['net']:7.0f} | {1e4*r['U5']['net']:7.0f} {1e4*r['U10']['net']:8.0f} | {1e4*r['H2']['net']:6.0f} {1e4*r['H30']['net']:6.0f}")

    P("\n## Summary (t clustered by notice day; VAL main set n = 0, so no bar can be tested)")
    P("set              cell  n(days) gross  slip  fund  cash    net      t  median    SR   years(net)")
    summ = {}
    groups = [("main IS", [r for r in rows if r["set"] == "main" and r["era"] == "IS"]),
              ("main VAL", [r for r in rows if r["set"] == "main" and r["era"] == "VAL"]),
              ("info IS (JST)", [r for r in rows if r["set"] == "info" and r["era"] == "IS"]),
              ("info VAL (T,GAL)", [r for r in rows if r["set"] == "info" and r["era"] == "VAL"]),
              ("all 8 pooled", rows)]
    for g, S in groups:
        if not S:
            P(f"{g:16s}  --    0      (no events)"); continue
        for c in ("H5", "H5x15", "H10", "U5", "U5x15", "U10"):
            q = stats(S, c); summ[(g, c)] = q
            P(f"{g:16s} {c:6s} {q['n']:2d}({q['days']:2d}) {q['gross']:6.0f} {q['slip']:5.0f} {q['fund']:5.1f} {q['cash']:5.2f} {q['net']:6.0f} {q['t']:6.2f} {q['median']:7.0f} {q['sr']:5.2f}  {q['years']}")

    rng = np.random.default_rng(66); NS = 1000
    P(f"\n## Random benchmark ({NS} draw sets, same coin / day, gross; percentile of the event gross mean)")
    for c, hedge in (("H5", True), ("U5", False)):
        G = np.full((NS, len(rows)), np.nan)
        for j, r in enumerate(rows):
            A = load("spot", r["spot"], r["day"]); B = load("perp", "BTCUSDT", r["day"]); d0 = int(A["d0"])
            hold = (r["L"] - r["N"]) // 1000 - 5
            z0 = (r["N"] - 900000 - d0) // 1000; z1 = (max(r["N"] + 1800000, r["L"] + H) - d0) // 1000
            ok = np.array([u for u in range(0, 86400 - hold) if u + hold < z0 or u > z1])
            ok = ok[np.isfinite(A["sec_p"][ok]) & np.isfinite(B["sec_p"][ok]) & np.isfinite(A["sec_p"][ok + hold])]
            u = rng.choice(ok, NS)
            G[:, j] = (A["sec_p"][u + hold] / A["sec_p"][u] - 1) - (hedge * (B["sec_p"][u + hold] / B["sec_p"][u] - 1))
        for g, idx in (("main IS", [j for j, r in enumerate(rows) if r["set"] == "main"]), ("all 8", list(range(len(rows))))):
            ev = np.mean([rows[j][c]["gross"] for j in idx])
            pct = 100 * np.mean(G[:, idx].mean(1) < ev)
            summ[(g if g != "all 8" else "all 8 pooled", c)]["rand_pct"] = pct
            P(f"  {c} {g:8s} event gross {1e4*ev:7.0f}  random mean {1e4*G[:, idx].mean():6.0f}  beats {pct:5.1f} %")

    m = [r for r in rows if r["set"] == "main"]
    sr = summ[("main IS", "H5")]["sr"]
    P("\n## Power (A2 arithmetic: SR per trade x sqrt(n_HOLD))")
    P(f"  VAL main n = 0: SR at VAL size undefined -> power undefined (LIVE / DEMO cannot be tested).")
    for nh in (1, 2, 5):
        P(f"  using the IS SR {sr:.2f} as if it were VAL's: n_HOLD {nh} -> power {sr*np.sqrt(nh):.2f}; SR needed for power 3: {3/np.sqrt(nh):.2f}")
    P(f"  capacity main: buyer-taker spot notional 1 s after N + 5 s median ${np.median([r['cap1'] for r in m]):,.0f}, 5 s ${np.median([r['cap5'] for r in m]):,.0f}")
    json.dump({f"{g}|{c}": v for (g, c), v in summ.items()}, open(os.path.join(OUTD, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(OUTD, "trades.csv"), "w") as fh:
        w = csv.writer(fh)
        w.writerow(["coin", "set", "era", "day", "N", "L", "on_a_s", "c50_s", "c90_s", "cap1", "cap5"] + [f"r{o}" for o in OFFS]
                   + [f"{c}_{k}" for c in ("H5", "H10", "U5", "U10") for k in ("gross", "slip", "fund", "net")])
        for r in rows:
            w.writerow([r["coin"], r["set"], r["era"], r["day"], r["N"], r["L"], r["on_a"], r["c50"], r["c90"], round(r["cap1"]), round(r["cap5"])]
                       + [round(1e4 * r["path"][o], 1) for o in OFFS]
                       + [round(1e4 * r[c][k], 1) for c in ("H5", "H10", "U5", "U10") for k in ("gross", "slip", "fund", "net")])
    out.close()


if __name__ == "__main__":
    main()
