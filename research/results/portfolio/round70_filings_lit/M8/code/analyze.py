"""Stream M8 analysis: path around the 8-K acceptance, 4 declared cells, costs, random benchmark, power.
Reads research/data/btc_treasury_8k/{events.csv,npz/}. Writes M8/results.txt, M8/trades.csv, M8/cells.json."""
import csv, json, os, sys
import numpy as np

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/btc_treasury_8k"
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round70_filings_lit/M8"
END = 1735689600000
N_HOLD = 90
FEE = 10.0  # bp round trip, taker 5 bp a side
CELLS = [(5, 5), (5, 60), (30, 5), (30, 60)]  # (d seconds, H minutes)
LATE = {5: 30, 30: 60}
rng = np.random.default_rng(70)
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    lines.append(s); print(s)


# funding stamps (long pays rate)
F = np.loadtxt("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance/funding/BTCUSDT.csv",
               delimiter=",", skiprows=1)
F = F[F[:, 0] < END]

ev = [e for e in csv.DictReader(open(os.path.join(D, "events.csv")))]
for e in ev:
    e["T"] = int(e["T_ms"]); assert e["T"] < END
    e["day"] = str(np.datetime64(e["T"], "ms"))[:10]
    e["year"] = int(e["day"][:4])
    e["era"] = "IS" if e["year"] <= 2021 else "VAL"
cache = {}


def load(day):
    if day not in cache:
        z = np.load(os.path.join(D, "npz", f"BTCUSDT_{day}.npz"))
        cache[day] = {k: z[k] for k in z.files}
    return cache[day]


def idx_at_or_after(t, ts):
    return int(np.searchsorted(t, ts, side="left"))


def last_at_or_before(t, p, ts):
    i = int(np.searchsorted(t, ts, side="right")) - 1
    return p[i] if i >= 0 else np.nan


def half_spread_bp(z, ts):
    t, p, m = z["t"], z["p"], z["m"]
    a, b = np.searchsorted(t, ts - 5000), np.searchsorted(t, ts + 5000)
    pp, mm = p[a:b], m[a:b]
    if len(pp) < 3:
        return 0.5 * 0.1 / p[min(a, len(p) - 1)] * 1e4
    k = mm[1:] != mm[:-1]
    if k.sum() == 0:
        return 0.5 * 0.1 / pp[0] * 1e4
    sp = np.median(np.abs(np.diff(pp))[k])
    return 0.5 * max(sp, 0.1) / pp[0] * 1e4


def funding_bp(t0, t1):
    k = (F[:, 0] > t0) & (F[:, 0] <= t1)
    return float(F[k, 1].sum() * 1e4)


def trade(e, d, H):
    z = load(e["day"])
    t, p = z["t"], z["p"]
    i = idx_at_or_after(t, e["T"] + d * 1000)
    assert t[i] - e["T"] < d * 1000 + 60000
    j = idx_at_or_after(t, t[i] + H * 60000)
    assert j < len(t) and t[j] - t[i] < H * 60000 + 60000, (e["day"], d, H)
    g = (p[j] / p[i] - 1) * 1e4
    hs = half_spread_bp(z, t[i]) + half_spread_bp(z, t[j])
    fu = funding_bp(t[i], t[j])
    return dict(gross=g, hs=hs, fund=fu, net=g - FEE - hs - fu, x15=g - 1.5 * FEE - 1.5 * hs - fu,
                lag_ms=int(t[i] - e["T"]), entry=p[i])


def cl_t(x, g):
    x = np.asarray(x, float); g = np.asarray(g)
    n = len(x)
    if n < 2:
        return np.nan
    mu = x.mean()
    G = np.unique(g)
    s = np.array([(x[g == k] - mu).sum() for k in G])
    var = (s ** 2).sum() / n ** 2 * len(G) / max(len(G) - 1, 1)
    return mu / np.sqrt(var) if var > 0 else np.nan


def summ(rows, key="net"):
    x = np.array([r[key] for r in rows]); g = [r["day"] for r in rows]
    sd = x.std(ddof=1) if len(x) > 1 else np.nan
    return dict(n=len(x), days=len(set(g)), mean=x.mean(), t=cl_t(x, g), med=np.median(x), sr=x.mean() / sd)


# ---------------- path ----------------
OFFS = [-540, -300, -60, -30, -10, -5, 0, 1, 2, 3, 5, 10, 30, 60, 120, 300, 600, 1800, 3600]


def path(e, ref_off):
    z = load(e["day"])
    t, p = z["t"], z["p"]
    r = last_at_or_before(t, p, e["T"] + ref_off * 1000)
    return np.array([(last_at_or_before(t, p, e["T"] + o * 1000) / r - 1) * 1e4 for o in OFFS])


def count_ratio(e):
    z = load(e["day"]); n = z["sec_n"]; s = (e["T"] - int(z["d0"])) // 1000
    base = n[s - 300:s - 10].mean()
    return n[s:s + 10].mean() / max(base, 1e-9), n[s + 10:s + 60].mean() / max(base, 1e-9)


P("# Stream M8 results (python -I; HOLD never loaded: every event T < 2025-01-01, files <= 2024-12-31)")
FR = [e for e in ev if e["cls"] == "FRESH"]
P("events FRESH", len(FR), "by year", {y: sum(e["year"] == y for e in FR) for y in range(2020, 2025)},
  "STALE", sum(e["cls"] == "STALE" for e in ev))
for grp, sel in [("FRESH IS", [e for e in FR if e["era"] == "IS"]), ("FRESH VAL", [e for e in FR if e["era"] == "VAL"]),
                 ("FRESH VAL MSTR", [e for e in FR if e["era"] == "VAL" and e["tk"] == "MSTR"]),
                 ("FRESH VAL other", [e for e in FR if e["era"] == "VAL" and e["tk"] != "MSTR"]),
                 ("FRESH 2024 MSTR", [e for e in FR if e["year"] == 2024 and e["tk"] == "MSTR"]),
                 ("STALE", [e for e in ev if e["cls"] == "STALE"]), ("TSLA10K", [e for e in ev if e["cls"] == "TSLA10K"])]:
    if not sel:
        continue
    A = np.array([path(e, -60) for e in sel])
    P(f"\n## path {grp} n={len(sel)} (bp vs last trade <= T-60s) offsets s: {OFFS}")
    P("median", np.round(np.median(A, 0), 1).tolist())
    P("mean  ", np.round(A.mean(0), 1).tolist())
    B = np.array([path(e, 0) for e in sel])
    k5, k60 = OFFS.index(300), OFFS.index(3600)
    P(f"vs T: mean +5m {B[:, k5].mean():.1f} (sd {B[:, k5].std():.1f}), +60m {B[:, k60].mean():.1f} (sd {B[:, k60].std():.1f}); "
      f"T-9m..T mean {np.mean([path(e, -540)[OFFS.index(0)] for e in sel]):.1f}")
    cr = np.array([count_ratio(e) for e in sel])
    P(f"trade count / s, ratio to [T-300,T-10]: [T,T+10) median {np.median(cr[:, 0]):.2f}, [T+10,T+60) median {np.median(cr[:, 1]):.2f}")
    if grp in ("STALE", "TSLA10K") or len(sel) <= 3:
        for e, row in zip(sel, A):
            P(" ", e["acc_utc"], e["tk"], e["note"], "path", np.round(row, 1).tolist())

# ---------------- cells ----------------
P("\n## cells (net bp/trade; fee 10 bp + spread + funding; t clustered by day)")
res = {}
trows = []
for d, H in CELLS:
    name = f"D{d}-{H}m"
    R = []
    for e in FR:
        r = trade(e, d, H); r.update(day=e["day"], year=e["year"], era=e["era"], tk=e["tk"])
        rl = trade(e, LATE[d], H); r["late"] = rl["net"]
        R.append(r)
        trows.append(dict(cell=name, acc_utc=e["acc_utc"], tk=e["tk"], era=e["era"], **{k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k not in ("day", "year", "era", "tk")}))
    res[name] = R
    for era in ("IS", "VAL"):
        S = [r for r in R if r["era"] == era]
        s = summ(S); sg = summ(S, "gross")
        yrs = {y: round(float(np.mean([r["net"] for r in S if r["year"] == y])), 1) for y in sorted(set(r["year"] for r in S))}
        P(f"{name} {era} n {s['n']} ({s['days']}d) gross {sg['mean']:.1f} hs {np.mean([r['hs'] for r in S]):.3f} "
          f"fund {np.mean([r['fund'] for r in S]):.2f} NET {s['mean']:.1f} t {s['t']:.2f} med {s['med']:.1f} SR {s['sr']:.3f} "
          f"x1.5 {np.mean([r['x15'] for r in S]):.1f} late {np.mean([r['late'] for r in S]):.1f} years {yrs} "
          f"lag_med_ms {np.median([r['lag_ms'] for r in S]):.0f} power {s['sr']*np.sqrt(N_HOLD):.2f}")
    S = [r for r in R if r["era"] == "VAL" and r["tk"] == "MSTR"]
    s = summ(S); P(f"   {name} VAL MSTR-only n {s['n']} NET {s['mean']:.1f} t {s['t']:.2f}")
    S = [r for r in R if r["era"] == "VAL" and r["tk"] != "MSTR"]
    s = summ(S); P(f"   {name} VAL others n {s['n']} NET {s['mean']:.1f} t {s['t']:.2f}")

# ---------------- random benchmark ----------------
P("\n## random same-day entries (1,000 sets; gross from 1 s last price; outside [T-2h, T+2h])")
NS = 1000


def sec_gross(e, s0, H):
    z = load(e["day"]); sp = z["sec_p"]
    return (sp[s0 + H * 60] / sp[s0] - 1) * 1e4


rand_t = {}
for d, H in CELLS:
    name = f"D{d}-{H}m"
    for era in ("IS", "VAL"):
        E = [e for e in FR if e["era"] == era]
        obs = np.mean([sec_gross(e, (e["T"] + d * 1000 - int(load(e["day"])["d0"])) // 1000, H) for e in E])
        M = np.zeros(NS); T_ = np.zeros(NS)
        G = np.zeros((NS, len(E)))
        for k, e in enumerate(E):
            z = load(e["day"]); s = (e["T"] - int(z["d0"])) // 1000
            ok = np.r_[np.arange(0, max(s - 7200, 0)), np.arange(min(s + 7200, 86400), 86400 - H * 60 - 1)]
            ok = ok[np.isfinite(z["sec_p"][ok])]
            pick = rng.choice(ok, NS)
            G[:, k] = (z["sec_p"][pick + H * 60] / z["sec_p"][pick] - 1) * 1e4
        days = [e["day"] for e in E]
        M = G.mean(1)
        T_ = np.array([cl_t(G[i] - FEE, days) for i in range(NS)])
        rand_t[(name, era)] = T_
        P(f"{name} {era} obs gross (1s series) {obs:.1f}; random mean {M.mean():.1f} p95 {np.quantile(M,0.95):.1f}; "
          f"obs beats {100*np.mean(M < obs):.0f} %")
for era in ("IS", "VAL"):
    mx = np.max(np.array([rand_t[(f"D{d}-{H}m", era)] for d, H in CELLS]), 0)
    P(f"max-over-4-cells null {era}: 95 % quantile of max net t = {np.quantile(mx, 0.95):.2f}")

with open(os.path.join(OUT, "trades.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(trows[0].keys())); w.writeheader(); w.writerows(trows)
with open(os.path.join(OUT, "results.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
cells = {}
for name, R in res.items():
    for era in ("IS", "VAL"):
        S = [r for r in R if r["era"] == era]; s = summ(S)
        cells[f"{name} {era}"] = {k: (float(v) if not isinstance(v, int) else v) for k, v in s.items()}
json.dump(cells, open(os.path.join(OUT, "cells.json"), "w"), indent=1)
