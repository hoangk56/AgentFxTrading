"""Summaries for stream A from cache/rows.pkl: per cell and era (net, t clustered by notice day, SR, years, x1.5 costs,
late entry, random percentiles), descriptive split, chained A-then-K2 (information), power at VAL size."""
import os, sys, json, pickle, csv
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import k2rule as K
A = os.path.join(os.path.dirname(__file__), "..")
CACHE = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_announce/cache"
d = pickle.load(open(os.path.join(CACHE, "rows.pkl"), "rb")); rows = d["rows"]
rng = np.random.default_rng(6502)
NH = 32 / 3 * 1.83
out = []; lines = []
cells = [f"A{E}-{X}" for X in ("L", "L1h") for E in (1, 5, 15)]


def stats(x, day):
    x = np.asarray(x, float) * 1e4
    if len(x) < 2:
        return dict(n=len(x), net=float(x.mean()) if len(x) else np.nan, t=np.nan, sd=np.nan, sr=np.nan, med=np.nan, days=len(set(day)))
    m, t, n = K.clt(x, day)
    return dict(n=n, net=m, t=t, sd=float(x.std(ddof=1)), sr=m / x.std(ddof=1), med=float(np.median(x)), days=len(set(day)))


for c in cells:
    for era in ("IS", "VAL"):
        sub = [r for r in rows if r["era"] == era and c in r["cells"]]
        if not sub:
            out.append(dict(cell=c, era=era, n=0)); continue
        cc = [r["cells"][c] for r in sub]; day = [r["day"] for r in sub]
        s = stats([x["net"] for x in cc], day)
        s.update(cell=c, era=era, price=1e4 * np.mean([x["price"] for x in cc]), fund=1e4 * np.mean([x["fund"] for x in cc]),
                 net15=1e4 * np.mean([x["net15"] for x in cc]), late=1e4 * np.nanmean([x["late"] for x in cc]),
                 hold_min=float(np.median([(x["tx"] - x["te"]) / 60000 for x in cc])))
        g = np.array([x["price"] for x in cc])
        for key in ("rs", "ro"):
            ok = [i for i, x in enumerate(cc) if len(x[key])]
            act = g[ok].mean()
            dr = np.array([np.mean([rng.choice(cc[i][key]) for i in ok]) for _ in range(500)])
            s["rand_" + key] = 100 * float((dr < act).mean())
        yrs = {}
        for r, x in zip(sub, cc):
            yrs.setdefault(r["year"], []).append(x["net"] * 1e4)
        s["years"] = {y: (len(v), round(float(np.mean(v)))) for y, v in sorted(yrs.items())}
        s["years_pos"] = f'{sum(np.mean(v) > 0 for v in yrs.values())}/{len(yrs)}'
        s["power"] = s["sr"] * np.sqrt(NH) if era == "VAL" and np.isfinite(s["sr"]) else np.nan
        s["trades"] = [(r["coin"], r["N_utc"][:10], round(x["net"] * 1e4)) for r, x in zip(sub, cc)]
        out.append(s)

for s in out:
    if s["n"] == 0:
        lines.append(f'{s["cell"]:8s} {s["era"]:3s} n 0'); continue
    lines.append(f'{s["cell"]:8s} {s["era"]:3s} n {s["n"]:2d} ({s["days"]} d) hold {s["hold_min"]:5.0f}m price {s["price"]:+6.0f} fund {s["fund"]:+5.0f} '
                 f'net {s["net"]:+6.0f} t {s["t"]:+.2f} med {s["med"]:+6.0f} sd {s["sd"]:5.0f} SR {s["sr"]:+.2f} x1.5 {s["net15"]:+6.0f} '
                 f'late5 {s["late"]:+6.0f} randSame {s["rand_rs"]:.0f} randOther {s["rand_ro"]:.0f} yrs {s["years_pos"]} {s["years"]} power {s["power"]:.2f}')
    lines.append("         " + str(s["trades"]))

# descriptive split (gross alt - BTC, bp)
lines.append("\nDescriptive split, gross long alt / short BTC on Binance perps (bp): mean / median")
for era in ("IS", "VAL"):
    sub = [r for r in rows if r["era"] == era]
    for k in ("pre24", "pre1h", "N_N1", "N1_L", "L_L1h"):
        v = np.array([r["desc"][k] for r in sub], float) * 1e4; v = v[np.isfinite(v)]
        lines.append(f'  {era:3s} {k:6s} n {len(v):2d} mean {v.mean():+7.0f} median {np.median(v):+7.0f}' if len(v) else f'  {era} {k} n 0')
    lags = [r["lag_min"] for r in sub]
    lines.append(f'  {era:3s} lag N->L min: median {np.median(lags):.0f}, min {min(lags):.0f}, max {max(lags):.0f}')

# chained (information only)
lines.append("\nChained A then K2 (information only): A long N+E -> K2 entry fill (L_hour + 61 min), then K2 short 72 h; net bp")
for era in ("IS", "VAL"):
    sub = [r for r in rows if r["era"] == era]
    for E in (1, 5, 15):
        a = np.array([r["chain"][E][0] for r in sub], float) * 1e4; k = np.array([r["chain"][E][1] for r in sub], float) * 1e4
        ok = np.isfinite(a) & np.isfinite(k); day = [r["day"] for r, o in zip(sub, ok) if o]
        sa = stats(a[ok] / 1e4, day); sk = stats(k[ok] / 1e4, day); sc = stats((a[ok] + k[ok]) / 1e4, day)
        lines.append(f'  {era:3s} E{E:2d} n {ok.sum():2d}: A leg {sa["net"]:+6.0f} (t {sa["t"]:+.2f}), K2 leg {sk["net"]:+6.0f} (t {sk["t"]:+.2f}), '
                     f'chain {sc["net"]:+6.0f} (t {sc["t"]:+.2f}, SR {sc["sr"]:+.2f})')

lines.append(f'\nDropped (L unknown): {d["dropped"]}. n_HOLD at VAL pace = {NH:.1f}.')
lines.append("Events: " + ", ".join(f'{r["coin"]} {r["N_utc"][:16]} lag {r["lag_min"]:.0f}m L={r["Lsrc"]} src={r["src"]}' for r in rows))
txt = "\n".join(lines)
open(os.path.join(A, "results.txt"), "w").write(txt + "\n")
json.dump(out, open(os.path.join(A, "cells.json"), "w"), indent=1, default=float)
with open(os.path.join(A, "trades.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cell", "era", "coin", "perp", "notice_utc", "nid", "lag_min", "hold_min", "price_bp", "fund_bp", "net_bp", "net15_bp", "late5_bp"])
    for r in rows:
        for c, x in r["cells"].items():
            w.writerow([c, r["era"], r["coin"], r["perp"], r["N_utc"], r["nid"], round(r["lag_min"]), round((x["tx"] - x["te"]) / 60000)] +
                       [round(1e4 * x[k], 1) for k in ("price", "fund", "net", "net15", "late")])
print(txt)
