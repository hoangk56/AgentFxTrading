"""Stream A4 analysis (declared in A4/HYPOTHESES_A4.md): A2-D5L on Bybit. Path around N, onset, the frozen cell (long
the Bybit alt perp / short Bybit BTCUSDT at the first trades >= N + 5 s, exit at the first trades >= L), unhedged long
(info), costs x1.5, one step late (N + 10 s), random benchmark, capacity, power. Functions at / after / slip / clt /
trade and the random draw copied from round65 A2/code/analyze.py; only the fee (Bybit 5.5 bp a side), the data loader
(Bybit npz, N day + L day merged when L is on the next UTC day) and the funding source (Bybit) differ."""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from pull import load_events, OUT as NPZ

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
OUTD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/A4"
H = 3600000
END = 1735689600000
COST = 4 * 0.00055  # Bybit non-VIP taker 5.5 bp x 4 fills
COST_U = 2 * 0.00055
OFFS = [-60, -30, -10, -5, -2, -1, 0, 1, 2, 3, 5, 10, 20, 30, 60, 120, 300]
N_HOLD = 7 / 3 * (669 / 365)  # 2022-24 pace x HOLD length (2025-01-01..2026-10-29)
N_HOLD24 = 6 * (669 / 365)    # 2024 pace (info)


def load(sym, days):
    parts = [dict(np.load(os.path.join(NPZ, f"{sym}_{d}.npz"))) for d in days]
    S = {k: np.concatenate([p[k] for p in parts]) for k in ("t", "p", "q", "buy", "sec_p", "sec_n")}
    o = np.argsort(S["t"], kind="stable")
    for k in ("t", "p", "q", "buy"):
        S[k] = S[k][o]
    S["d0"] = int(parts[0]["d0"])
    assert S["t"].max() < END
    return S


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


def fund(sym, a, b):  # sum of real Bybit funding rates at stamps in (a, b]
    if sym not in _FU:
        for d in ("bybit/funding", "bybit_basis/funding", "upbit_bybit_notice/funding"):
            p = os.path.join(R, d, sym + ".csv")
            if os.path.exists(p):
                rows = [(float(x["t"]), float(x["rate"])) for x in csv.DictReader(open(p))]
                _FU[sym] = np.array([r for r in rows if r[0] < END]); break
    F = _FU[sym]
    assert F[:, 0].min() < a and F[:, 0].max() > b - 9 * H, sym
    w = (F[:, 0] > a) & (F[:, 0] <= b)
    return float(F[w, 1].sum())


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
    if hedge:
        sl = slip(A, te_a) + slip(A, tx_a) + slip(B, te_b) + slip(B, tx_b)
        gross = (ax / ae - 1) - (bx / be - 1)
        f = -fund(e["bsym"], te_a, tx_a) + fund("BTCUSDT", te_b, tx_b); fee = COST
    else:
        sl = slip(A, te_a) + slip(A, tx_a); gross = ax / ae - 1; f = -fund(e["bsym"], te_a, tx_a); fee = COST_U
    net_ = gross + f - costmul * (fee + sl)
    return dict(gross=gross, fund=f, slip=sl, slip_entry_alt=slip(A, te_a), net=net_, lag_a=(te_a - N) / 1000,
                lag_b=(te_b - N) / 1000, hold=(tx_a - te_a) / 1000)


def stats(S, c):
    v = np.array([r[c]["net"] for r in S]); days = [r["day"] for r in S]
    m, t, n = clt(v, days)
    sr = v.mean() / v.std(ddof=1) if n > 1 else np.nan
    yrs = {}
    for r in S:
        yrs.setdefault(r["year"], []).append(r[c]["net"])
    return dict(n=n, days=len(set(days)), net=1e4 * m, t=t, sr=sr, median=1e4 * np.median(v),
                gross=1e4 * np.mean([r[c]["gross"] for r in S]), slip=1e4 * np.mean([r[c]["slip"] for r in S]),
                fund=1e4 * np.mean([r[c]["fund"] for r in S]),
                years=" ".join(f"{y}:{1e4*np.mean(x):+.0f}({len(x)})" for y, x in sorted(yrs.items())),
                yrs_pos=f"{sum(np.mean(x) > 0 for x in yrs.values())}/{len(yrs)}")


def main():
    E = load_events()
    out = open(os.path.join(OUTD, "results.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    rows = []
    for e in E:
        days = sorted({e["day"], e["Lday"]})
        A = load(e["bsym"], days); B = load("BTCUSDT", days); N = e["N"]
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
        cap = {}
        for w in (1, 5):  # taker-buy alt notional (USDT) in the w s after N + 5 s
            k0, k1 = np.searchsorted(A["t"], [N + 5000, N + 5000 + w * 1000])
            sel = A["buy"][k0:k1] == 1
            cap[w] = float((A["p"][k0:k1][sel] * A["q"][k0:k1][sel]).sum())
        pre = slip(A, N - 600000)
        row = dict(e, path=path, raw=raw, on_a=on_a, c50=comp[0.5], c90=comp[0.9], n_pre60=n_pre, cap1=cap[1], cap5=cap[5],
                   pre_slip=pre, _A=A, _B=B)
        for d in (2, 5, 10, 30):
            row[f"H{d}"] = trade(e, d, e["L"], A, B)
        row["H5x15"] = trade(e, 5, e["L"], A, B, 1.5)
        row["U5"] = trade(e, 5, e["L"], A, B, hedge=False)
        row["U10"] = trade(e, 10, e["L"], A, B, hedge=False)
        row["H5-5m"] = trade(e, 5, N + 300000, A, B)
        rows.append(row)

    P("# Stream A4 results (bp unless noted). Bybit alt perp vs Bybit BTCUSDT. 7 events, all VAL (IS n = 0)")
    P("\n## Per event: onset a (s vs N), completion of r(N+60 s) (s), path r = alt vs BTC (bp vs N - 60 s), capacity")
    P("coin   day        L-N(min) pre60n onA    c50    c90   r(-1) r(0) r(+1) r(+2) r(+5) r(+10) r(+30) r(+60) r(+300) raw(+5) cap1s($)  cap5s($) slipE(bp) base(bp)")
    f = lambda v: "  --  " if v is None else f"{v:6.1f}"
    for r in rows:
        p = r["path"]
        P(f"{r['coin']:6s} {r['day']} {(r['L']-r['N'])/60000:7.1f} {r['n_pre60']:5d} {f(r['on_a'])} {f(r['c50'])} {f(r['c90'])} "
          + " ".join(f"{1e4*p[o]:5.0f}" for o in (-1, 0, 1, 2, 5, 10, 30, 60, 300))
          + f" {1e4*r['raw'][5]:6.0f} {r['cap1']:9.0f} {r['cap5']:9.0f} {1e4*r['H5']['slip_entry_alt']:7.1f} {1e4*r['pre_slip']:6.1f}")
    groups = [("VAL main (n 7)", rows), ("VAL main without ME", [r for r in rows if r["coin"] != "ME"])]
    for nm, S in groups:
        P(f"\n## Path {nm}: r(t) alt vs BTC, bp vs N - 60 s: q25 / median / q75 / mean | raw alt median")
        for o in OFFS:
            v = 1e4 * np.array([r["path"][o] for r in S]); w = 1e4 * np.array([r["raw"][o] for r in S])
            P(f"  t {o:+5d}s  {np.percentile(v,25):7.0f} {np.median(v):7.0f} {np.percentile(v,75):7.0f} {v.mean():7.0f} | {np.median(w):7.0f}")
        for k in ("on_a", "c50", "c90"):
            v = np.array([r[k] for r in S if r[k] is not None])
            if len(v):
                P(f"  {k}: n {len(v)}/{len(S)}  median {np.median(v):.1f} s  min {v.min():.1f}  max {v.max():.1f}")

    P("\n## Per-event trades (net bp; H = long alt / short BTC, 22 bp + 4 slips + funding; U = unhedged long, 11 bp + 2 slips + alt funding)")
    P("coin    hold(min) lagA(s) lagB(s) H5 gross  slip   fund   H5 net  H10 net  H5x1.5 |  U5 net  U10 net | H2 net H30 net H5-5m")
    for r in rows:
        h = r["H5"]
        P(f"{r['coin']:6s} {h['hold']/60:8.1f} {h['lag_a']:6.2f} {h['lag_b']:6.2f} {1e4*h['gross']:8.0f} {1e4*h['slip']:5.0f} {1e4*h['fund']:6.1f} "
          f"{1e4*h['net']:8.0f} {1e4*r['H10']['net']:8.0f} {1e4*r['H5x15']['net']:7.0f} | {1e4*r['U5']['net']:7.0f} {1e4*r['U10']['net']:8.0f} | "
          f"{1e4*r['H2']['net']:6.0f} {1e4*r['H30']['net']:6.0f} {1e4*r['H5-5m']['net']:6.0f}")

    P("\n## Summary (t clustered by notice day; IS n = 0, so no bar can be tested)")
    P("set                  cell   n(days) gross  slip  fund    net      t  median    SR   years(net)")
    summ = {}
    for g, S in groups:
        for c in ("H5", "H5x15", "H10", "H2", "H30", "H5-5m", "U5", "U10"):
            q = stats(S, c); summ[(g, c)] = q
            P(f"{g:20s} {c:6s} {q['n']:2d}({q['days']:2d}) {q['gross']:6.0f} {q['slip']:5.0f} {q['fund']:5.1f} {q['net']:6.0f} {q['t']:6.2f} {q['median']:7.0f} {q['sr']:5.2f}  {q['years']}")

    rng = np.random.default_rng(66); NS = 1000
    P(f"\n## Random benchmark ({NS} draw sets, same coin / day(s), gross; percentile of the event gross mean)")
    for c, hedge in (("H5", True), ("U5", False)):
        G = np.full((NS, len(rows)), np.nan)
        for j, r in enumerate(rows):
            A, B = r["_A"], r["_B"]; d0 = A["d0"]; T = len(A["sec_p"])
            hold = (r["L"] - r["N"]) // 1000 - 5
            z0 = (r["N"] - 900000 - d0) // 1000; z1 = (max(r["N"] + 1800000, r["L"] + H) - d0) // 1000
            ok = np.array([u for u in range(0, T - hold) if u + hold < z0 or u > z1])
            ok = ok[np.isfinite(A["sec_p"][ok]) & np.isfinite(B["sec_p"][ok]) & np.isfinite(A["sec_p"][ok + hold])]
            if not len(ok):
                P(f"  {r['coin']}: no random window (hold {hold} s)"); continue
            u = rng.choice(ok, NS)
            G[:, j] = (A["sec_p"][u + hold] / A["sec_p"][u] - 1) - (hedge * (B["sec_p"][u + hold] / B["sec_p"][u] - 1))
        for g, S in groups:
            idx = [j for j, r in enumerate(rows) if r in S and np.isfinite(G[0, j])]
            ev = np.mean([rows[j][c]["gross"] for j in idx])
            pct = 100 * np.mean(G[:, idx].mean(1) < ev)
            summ[(g, c)]["rand_pct"] = pct; summ[(g, c)]["rand_n"] = len(idx)
            P(f"  {c} {g:20s} n {len(idx)} event gross {1e4*ev:7.0f}  random mean {1e4*G[:, idx].mean():6.0f}  beats {pct:5.1f} %")

    sr = summ[("VAL main (n 7)", "H5")]["sr"]
    P("\n## Power (A2 arithmetic: SR per trade (VAL) x sqrt(n_HOLD))")
    P(f"  n_HOLD at the 2022-24 pace (7 / 3 yr x 1.83 yr) = {N_HOLD:.1f}: power {sr*np.sqrt(N_HOLD):.2f}; SR needed {3/np.sqrt(N_HOLD):.2f}")
    P(f"  info, 2024 pace (6 / yr): n_HOLD {N_HOLD24:.1f}: power {sr*np.sqrt(N_HOLD24):.2f}; SR needed {3/np.sqrt(N_HOLD24):.2f}")
    P(f"  capacity: taker-buy alt notional 1 s after N + 5 s median ${np.median([r['cap1'] for r in rows]):,.0f}, 5 s ${np.median([r['cap5'] for r in rows]):,.0f}")
    json.dump({f"{g}|{c}": v for (g, c), v in summ.items()}, open(os.path.join(OUTD, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(OUTD, "trades.csv"), "w") as fh:
        w = csv.writer(fh)
        w.writerow(["coin", "day", "N", "L", "on_a_s", "c50_s", "c90_s", "cap1", "cap5"] + [f"r{o}" for o in OFFS]
                   + [f"{c}_{k}" for c in ("H5", "H10", "U5") for k in ("gross", "slip", "fund", "net")])
        for r in rows:
            w.writerow([r["coin"], r["day"], r["N"], r["L"], r["on_a"], r["c50"], r["c90"], round(r["cap1"]), round(r["cap5"])]
                       + [round(1e4 * r["path"][o], 1) for o in OFFS]
                       + [round(1e4 * r[c][k], 1) for c in ("H5", "H10", "U5") for k in ("gross", "slip", "fund", "net")])
    out.close()


if __name__ == "__main__":
    main()
