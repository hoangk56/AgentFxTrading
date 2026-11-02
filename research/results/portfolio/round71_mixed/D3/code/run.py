"""Grade the 6 declared cells. Run: python -I run.py LAG  (LAG fixed by calib.py on 2021-09)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d3

LAG = int(sys.argv[1]) if len(sys.argv) > 1 else 0
CLEAN = "clean" in sys.argv
P = d3.load(LAG, clean=CLEAN)
dff = d3.dff_daily()
ON = P["valid"].copy()
F7 = d3.f7_mask(P)
ASSETS = {"BTC": ["BTC"], "ETH": ["ETH"], "B10": d3.COINS}
ERAS = {"IS": d3.IS, "VAL": d3.VAL}
rng = np.random.default_rng(71)


def trim(res):
    a = np.where(res["active"])[0]
    s = a[0] if len(a) else 0
    return s


def cell(assets, mask, era, **kw):
    res = d3.simulate(P, ASSETS[assets], mask, era, **kw)
    s = trim(res)
    out = {k: (v[s:] if isinstance(v, np.ndarray) else v) for k, v in res.items()}
    out["dff"] = dff[era[0] + s: era[1]]
    return out


print("Descriptive (holding-day funding, bp per day; valid days only)")
for c in ("BTC", "ETH"):
    i = d3.COINS.index(c)
    for y in range(2020, 2025):
        m = P["valid"][i] & (d3.years(P["days"]) == y)
        if m.sum() == 0:
            continue
        rec = P["recon"][i][m].mean()
        print(" %s %d days %d  Binance %.2f  OKX %.2f  gap %.2f bp/day  (OKX reconstructed share %.2f)" % (
            c, y, m.sum(), P["fB"][i][m].mean() * 1e4, P["fO"][i][m].mean() * 1e4,
            (P["fB"][i][m] - P["fO"][i][m]).mean() * 1e4, rec))
# share of Binance stamps exactly at the anchor, by year (BTC)
fb = d3.rd(os.path.join(d3.BIN, "funding", "BTCUSDT.csv"))
fo = d3.rd(os.path.join(d3.OKX, "BTC_funding.csv"))
for y in range(2020, 2025):
    a, b = np.datetime64("%d-01-01" % y, "ms").astype(np.int64), np.datetime64("%d-01-01" % (y + 1), "ms").astype(np.int64)
    mb = (fb[:, 0] >= a) & (fb[:, 0] < min(b, d3.CUT))
    mo = (fo[:, 0] >= a) & (fo[:, 0] < min(b, d3.CUT))
    print(" BTC %d Binance stamps at 0.0001: %.2f (n %d); OKX realised stamps within 0.5 bp of 0.0001: %s" % (
        y, (np.abs(fb[mb, 1] - 1e-4) < 1e-9).mean() if mb.sum() else np.nan, mb.sum(),
        "%.2f (n %d)" % ((np.abs(fo[mo, 1] - 1e-4) < 5e-5).mean(), mo.sum()) if mo.sum() else "n/a"))

rows = []
series = {}
for a in ASSETS:
    for rn, mask in (("ON", ON), ("F7", F7)):
        name = "%s-%s" % (a, rn)
        for e, era in ERAS.items():
            res = cell(a, mask, era)
            s = d3.summ(res["r"])
            ex2 = d3.summ(res["r"] - res["dff"])
            ex3 = d3.summ(res["r"] - res["dff"] * 2 / 3)
            c15 = d3.summ(cell(a, mask, era, cost_mult=1.5)["r"])
            lt = d3.summ(cell(a, mask, era, late=1)["r"])
            yy = d3.years(res["days"])
            ys = {int(y): res["r"][yy == y].mean() * 365 for y in np.unique(yy)}
            # random benchmark
            if rn == "F7":
                draws = []
                for _ in range(500):
                    sh = np.zeros_like(mask)
                    for i in range(10):
                        seg = mask[i, era[0]:era[1]]
                        sh[i, era[0]:era[1]] = np.roll(seg, rng.integers(1, len(seg)))
                    draws.append(d3.simulate(P, ASSETS[a], sh, era)["r"].mean())
                rnd = (np.array(draws) < res["r"].mean()).mean()
            else:
                rnd = float(res["r"].mean() > 0)
            series[(name, e)] = res["r"]
            rows.append((name, e, s, ex2, ex3, c15, lt, ys, rnd, res))
            print("%-8s %-3s n %4d net %+6.2f%% vol %5.2f%% Sh %+5.2f t_nw %+5.2f | ex.cash L2 %+6.2f%% t %+5.2f L3 %+6.2f%% "
                  "| x1.5 %+6.2f%% late %+6.2f%% | fund %+6.2f price %+6.2f cost %5.2f xfer %4.2f %%/yr | on %.2f liq %d "
                  "| rnd %.2f | yrs %s" % (
                      name, e, s["n"], s["ann"] * 100, s["vol"] * 100, s["sh"], s["t"], ex2["ann"] * 100, ex2["t"],
                      ex3["ann"] * 100, c15["ann"] * 100, lt["ann"] * 100, res["fl"].mean() * 36500,
                      res["pl"].mean() * 36500, res["cs"].mean() * 36500, res["tr"].mean() * 36500, res["on_share"],
                      res["liq"], rnd, " ".join("%d:%+.2f" % (k, v * 100) for k, v in ys.items())), flush=True)

# max-over-cells null on IS: joint stationary block bootstrap of demeaned series (aligned on the common window)
names = sorted({k[0] for k in series})
L = min(len(series[(n, "IS")]) for n in names)
X = np.array([series[(n, "IS")][-L:] for n in names])
X0 = X - X.mean(1, keepdims=True)
tact = np.array([d3.nw_t(x) for x in X])
mx = []
for _ in range(1000):
    idx = []
    while len(idx) < L:
        s = rng.integers(0, L)
        ln = rng.geometric(1 / 20)
        idx.extend([(s + k) % L for k in range(ln)])
    idx = np.array(idx[:L])
    mx.append(max(d3.nw_t(x[idx]) for x in X0))
mx = np.array(mx)
print("max-over-cells IS null (common window %d days): 95th pct of max t = %.2f" % (L, np.percentile(mx, 95)))
for n, t in zip(names, tact):
    print("  %s IS t (common window) %+.2f  p_max %.3f" % (n, t, (mx >= t).mean()))
