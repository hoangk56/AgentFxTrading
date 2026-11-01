"""Run every declared cell, robustness, random benchmarks and the calibration null. Prints a report to stdout.
Usage: python -I run.py [out.json]"""
import sys, os, json, collections, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import *

U, drop = load_universe()
print("universe loaded", len(U), "markets; dropped", dict(drop))
print("by era:", collections.Counter(era_of(r["closed"]) for r in U))

CELLS = {}
for side in ("all", "Y", "N"):
    for thr in (0.80, 0.90):
        for T in (7 * DAY, DAY):
            CELLS[f"P1-{side}-thr{thr:.2f}-T{T // DAY}d"] = (lambda r, late=0, T=T, thr=thr, side=side: p1_trade(r, T, thr, side, late), H)
for L in (H, 12 * H):
    CELLS[f"P2a-L{L // H}h"] = (lambda r, late=0, L=L: p2a_trade(r, L, late), H)
CELLS["P2b-first95"] = (lambda r, late=0: p2b_trade(r, late), H)
PRIMARY = ["P1-all-thr0.90-T1d", "P2a-L1h", "P2b-first95"]


def run_cell(gen, mult=1.0, late=0, pred=None):
    rows = []
    for r in U:
        if pred is not None and not pred(r):
            continue
        tr = gen(r, late)
        if tr is None:
            continue
        rows.append((r, tr, ret(r, tr, mult)))
    return rows


def years(evs):
    out = {}
    for y in (2023, 2024):
        s = [e for e in evs if e["year"] == y]
        out[y] = ctstat([e["ret"] for e in s], [e["day"] for e in s]) + (len(s),)
    return out


res = {}
print("\n=== all cells, base cost (h 1c / 0.5c, friction 5 bp, minus DFF) ===")
for name, (gen, lateh) in CELLS.items():
    rows = run_cell(gen)
    evs = aggregate(rows)
    a, b = summarize(evs, "IS"), summarize(evs, "VAL")
    res[name] = dict(IS=a, VAL=b, rows=rows, evs=evs)
    print(f"{name:22s} IS  {fmt(a)}\n{'':22s} VAL {fmt(b)}")

print("\n=== robustness: costs x1.5 / x2, one step late, vol >= 10k, gross (no spread) ===")
for name, (gen, lateh) in CELLS.items():
    line = [name]
    for lab, kw in (("x1.5", dict(mult=1.5)), ("x2", dict(mult=2.0)), ("late", dict(late=lateh)),
                    ("v10k", dict(pred=lambda r: r["vol"] >= 10000)), ("mid", dict(mult=0.0))):
        evs = aggregate(run_cell(gen, **kw))
        a, b = summarize(evs, "IS"), summarize(evs, "VAL")
        line.append(f"{lab}: IS {100 * a['mean']:+.2f}% t{a['t']:+.1f} | VAL {100 * b['mean']:+.2f}% t{b['t']:+.1f}")
    print("  ".join(line))

print("\n=== per year / quarter, primary cells ===")
for name in PRIMARY + ["P1-all-thr0.80-T1d", "P1-all-thr0.90-T7d", "P1-all-thr0.80-T7d", "P2a-L12h"]:
    evs = res[name]["evs"]
    qs = collections.defaultdict(list)
    for e in evs:
        qs[e["q"]].append(e)
    print(name, " | ".join(f"{q} n{len(v)} {100 * np.mean([e['ret'] for e in v]):+.2f}%" for q, v in sorted(qs.items())))

print("\n=== by category (info, not selection) ===")
for name in PRIMARY:
    evs = res[name]["evs"]
    for era in ("IS", "VAL"):
        cs = collections.defaultdict(list)
        for e in evs:
            if e["era"] == era:
                cs[e["cat"]].append(e)
        print(name, era, " | ".join(
            f"{c} n{len(v)} {100 * np.mean([e['ret'] for e in v]):+.2f}% t{ctstat([e['ret'] for e in v], [e['day'] for e in v])[1]:+.1f}"
            for c, v in sorted(cs.items())))

print("\n=== by entry price band (info) ===")
for name in ["P1-all-thr0.80-T1d", "P1-all-thr0.80-T7d", "P2a-L1h", "P2a-L12h"]:
    rows = res[name]["rows"]
    for era in ("IS", "VAL"):
        parts = []
        for lo, hi in ((0.80, 0.90), (0.90, 0.95), (0.95, 0.97), (0.97, 0.99)):
            sub = [x for x in rows if era_of(x[0]["closed"]) == era and lo - 1e-9 <= x[1]["p"] < hi - 1e-9]
            if sub:
                ev = aggregate(sub)
                m, t = ctstat([e["ret"] for e in ev], [e["day"] for e in ev])
                parts.append(f"[{lo:.2f},{hi:.2f}) n{len(ev)} {100 * m:+.2f}% t{t:+.1f}")
        print(name, era, " | ".join(parts))

print("\n=== without the US election week (2024-11-04..11-10 resolutions) ===")
for name in PRIMARY:
    evs = [e for e in res[name]["evs"] if not (dt.date(2024, 11, 4) <= e["day"] <= dt.date(2024, 11, 10))]
    print(name, "VAL", fmt(summarize(evs, "VAL")))

# ---------- random benchmarks ----------------------------------------------------------
rng = np.random.default_rng(63)
NDRAW = 2000


def rand_tok_returns(r, t):
    p0 = price_at(r, t)
    if p0 is None or not (r["closed"] > t + H):
        return None
    out = []
    for tok, p in ((0, p0), (1, 1 - p0)):
        p = min(max(p, 0.01), 0.99)
        out.append(r["final"][tok] / (p + half_spread(p, 1.0)) - 1 - FRICTION - cash(t, r["closed"]))
    return out


def entry_time_fn(name):
    if name.startswith("P1"):
        T = 7 * DAY if name.endswith("T7d") else DAY
        return lambda r: r["end"] - T
    if name.startswith("P2a"):
        L = 12 * H if "L12h" in name else H
        return lambda r: r["end"] + L
    return None


print("\n=== random benchmarks (2,000 draws): R1 same markets+timing, random token; R2 random same-category markets at same timing, random token ===")
for name in PRIMARY + ["P1-all-thr0.80-T1d", "P1-all-thr0.90-T7d", "P1-all-thr0.80-T7d", "P2a-L12h"]:
    rows, evs = res[name]["rows"], res[name]["evs"]
    for era in ("IS", "VAL"):
        obs = summarize(evs, era)["mean"]
        sub = [x for x in rows if era_of(x[0]["closed"]) == era]
        if not sub:
            continue
        # R1: per trade, the two-token returns at the rule's entry time
        ev_ix = collections.defaultdict(list)
        pairs = []
        for r, tr, _ in sub:
            p0 = tr["p"] if tr["tok"] == 0 else 1 - tr["p"]
            rr = []
            for tok, p in ((0, p0), (1, 1 - p0)):
                p = min(max(p, 0.01), 0.99)
                rr.append(r["final"][tok] / (p + half_spread(p, 1.0)) - 1 - FRICTION - cash(tr["t"], r["closed"]))
            ev_ix[r["event"]].append(len(pairs))
            pairs.append(rr)
        P = np.array(pairs)
        groups = list(ev_ix.values())
        draws = []
        for _ in range(NDRAW):
            pick = rng.integers(0, 2, len(P))
            x = P[np.arange(len(P)), pick]
            draws.append(np.mean([x[g].mean() for g in groups]))
        r1 = float(np.mean(obs > np.array(draws)))
        # R2: random eligible events of the same category, same timing function
        tf = entry_time_fn(name)
        r2 = float("nan")
        if tf is not None:
            pool = collections.defaultdict(list)  # cat -> list of (event, [pair returns])
            byev = collections.defaultdict(list)
            for r in U:
                if era_of(r["closed"]) != era:
                    continue
                rr = rand_tok_returns(r, tf(r))
                if rr is not None:
                    byev[(r["cat"], r["event"])].append(rr)
            for (c, e), lst in byev.items():
                pool[c].append(np.array(lst))
            need = collections.Counter(e["cat"] for e in evs if e["era"] == era)
            draws2 = []
            for _ in range(NDRAW):
                vals = []
                for c, k in need.items():
                    if not pool[c]:
                        continue
                    for j in rng.integers(0, len(pool[c]), k):
                        A = pool[c][j]
                        vals.append(A[np.arange(len(A)), rng.integers(0, 2, len(A))].mean())
                draws2.append(np.mean(vals))
            r2 = float(np.mean(obs > np.array(draws2)))
            print(f"{name:22s} {era}: obs {100 * obs:+.2f}%  R1 beats {100 * r1:.1f}% (draw mean {100 * np.mean(draws):+.2f}%)  R2 beats {100 * r2:.1f}% (draw mean {100 * np.mean(draws2):+.2f}%)")
        else:
            print(f"{name:22s} {era}: obs {100 * obs:+.2f}%  R1 beats {100 * r1:.1f}% (draw mean {100 * np.mean(draws):+.2f}%)")

# ---------- calibration null: outcome ~ Bernoulli(entry price); max-over-cells ------------
# The clustered t is unreliable here (bounded, skewed returns; a band with no loser gives t ~ 40). The calibration
# null asks: if the entry price were the true probability (outcomes independent across markets), how often would the
# event-mean excess return be >= the observed one, with the same costs? z = standardized mean under that null.
from statistics import NormalDist
print("\n=== calibration null (outcome ~ Bernoulli(entry price), same costs), 2,000 sims; per-cell p, z, power ===")
NS = 2000
cell_names = list(CELLS)
CAL = {}
for era in ("IS", "VAL"):
    obs_m, mu, sd = {}, {}, {}
    sims = np.full((NS, len(cell_names)), np.nan)
    for j, name in enumerate(cell_names):
        rows = [x for x in res[name]["rows"] if era_of(x[0]["closed"]) == era]
        if len(rows) < 5:
            continue
        ev = aggregate(rows)
        obs_m[name] = float(np.mean([e["ret"] for e in ev]))
        p = np.array([tr["p"] for _, tr, _ in rows])
        cst = np.minimum(np.array([p_ + half_spread(p_, 1.0) for p_ in p]), 0.9999)
        cash_ = np.array([cash(tr["t"], r["closed"]) for r, tr, _ in rows])
        evk = [r["event"] for r, _, _ in rows]
        uniq = {e: i for i, e in enumerate(dict.fromkeys(evk))}
        ei = np.array([uniq[e] for e in evk])
        cnt = np.bincount(ei)
        for s_ in range(NS):
            win = rng.random(len(p)) < p
            x = win / cst - 1 - FRICTION - cash_
            sims[s_, j] = (np.bincount(ei, weights=x) / cnt).mean()
        mu[name], sd[name] = float(np.mean(sims[:, j])), float(np.std(sims[:, j]))
    Z = {}
    for j, name in enumerate(cell_names):
        if name not in obs_m:
            continue
        pv = (np.sum(sims[:, j] >= obs_m[name]) + 1) / (NS + 1)
        z = (obs_m[name] - mu[name]) / sd[name] if sd[name] > 0 else float("nan")
        Z[name] = z
        summ = summarize(res[name]["evs"], era)
        sd_ev = max(summ["sd"], sd[name] * math.sqrt(summ["n"]))  # per-event sd: observed or Bernoulli model, larger
        sh = summ["mean"] / sd_ev if sd_ev > 0 else float("nan")
        znet = obs_m[name] / sd[name] if sd[name] > 0 else float("nan")
        fwd = 1.75 * summ["n"] if era == "VAL" else float("nan")
        CAL[(era, name)] = dict(p=float(pv), z=float(z), znet=float(znet), null_mean=mu[name], sharpe=sh, power=sh * math.sqrt(fwd) if fwd == fwd else float("nan"))
        print(f"{era} {name:22s} obs mean {100 * obs_m[name]:+.2f}%  null mean {100 * mu[name]:+.2f}%  p {pv:.4f}  z_edge {z:+.2f}  z_net {znet:+.2f}  t_cl {summ['t']:+.2f}  n {summ['n']}"
              + (f"  Sharpe/event {sh:+.3f}  power(1.75 x n_VAL={fwd:.0f}) {sh * math.sqrt(fwd):+.2f}" if era == "VAL" else ""))
    zs = {k: v for k, v in Z.items() if v == v}
    if zs:
        zsim = (sims - np.array([mu.get(n, np.nan) for n in cell_names])) / np.array([sd.get(n, np.nan) or np.nan for n in cell_names])
        mx = np.nanmax(zsim, axis=1)
        best = max(zs.items(), key=lambda kv: kv[1])
        print(f"{era} max-over-{len(zs)}-cells: best {best[0]} z {best[1]:+.2f}; null max z 95th pct {np.percentile(mx, 95):+.2f}; p {np.mean(mx >= best[1]):.4f}")

if len(sys.argv) > 1:
    keep = {k: dict(IS=v["IS"], VAL=v["VAL"], cal={e: CAL.get((e, k)) for e in ("IS", "VAL")}) for k, v in res.items()}
    json.dump(keep, open(sys.argv[1], "w"), indent=1, default=str)
    # per-trade file for the primary cells (no 2025+ data exists in it)
    out = []
    for name in PRIMARY:
        for r, tr, x in res[name]["rows"]:
            out.append(dict(cell=name, id=r["id"], cond=r["cond"], event=r["event"], cat=r["cat"], tok=tr["tok"],
                            p=tr["p"], t=tr["t"], closed=r["closed"], payout=r["final"][tr["tok"]], ret=x))
    json.dump(out, open(os.path.join(os.path.dirname(sys.argv[1]), "trades_primary.json"), "w"))
