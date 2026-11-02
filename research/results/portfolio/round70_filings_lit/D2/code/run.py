"""Grade the 6 declared D2 cells on IS / VAL (python -I run.py). Output: ../out/report.txt (+ stdout)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import d2

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
os.makedirs(OUT, exist_ok=True)
lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    lines.append(s)


A = {}
for a in ("BTC", "ETH"):
    X = d2.load(a)
    D = d2.daily(X)
    A[a] = D
    say(a, "missing marks (2nd half) FD/FB/S:", D["miss_FD"], D["miss_FB"], D["miss_S"])
days = A["BTC"]["days"]
assert (days == A["ETH"]["days"]).all() and days[-1] == d2.CUT
cash = d2.fed_funds(days)
yrs = d2.years(days)


def era_idx(e):
    a, b = d2.ERAS[e]
    return int(np.searchsorted(days, a)), int(np.searchsorted(days, b))


# ---------- descriptive: funding levels by year (annualised, % / yr) ----------
say("\n== Funding by year (annualised %/yr): Binance stamps sum, Deribit interest_1h sum, gap; share Binance stamps"
    " == 0.0001, share Deribit hours == 0")
for a in ("BTC", "ETH"):
    D = A[a]
    X = d2.load(a)
    for y in range(2020, 2025):
        m = (yrs == y)
        hb = X["rB"]; hy = d2.years(d2.T0 + np.arange(X["nh"]) * d2.H) == y
        st = hb[hy]; st = st[st != 0]
        i1 = X["i1"][hy]; i1 = i1[~np.isnan(i1)]
        say(f"  {a} {y}: Binance {100*365*D['fb'][m].mean():6.2f}  Deribit {100*365*D['fd'][m].mean():6.2f}  gap "
            f"{100*365*D['gap_pure'][m].mean():6.2f}  | B@0.01% {100*np.mean(np.abs(st-0.0001)<1e-9):5.1f}%  D==0 "
            f"{100*np.mean(i1==0):5.1f}%")


def run_cell(asset, rule, e, cost_mult=1.0, late=0, L=2.0, shift=None):
    d0, d1 = era_idx(e)
    out = []
    for a in (("BTC", "ETH") if asset == "BOTH" else (asset,)):
        D = A[a]
        if rule == "ON":
            on = np.ones(len(days), bool)
        else:
            s = D["s7"].copy()
            on = np.nan_to_num(s, nan=-1) > 0
        if late:
            on = np.concatenate([[False] * late, on[:-late]])
        if shift is not None:
            seg = on[d0:d1].copy()
            on = on.copy(); on[d0:d1] = np.roll(seg, shift)
        res = d2.simulate(D, d0, d1, on, L=L, cost_mult=cost_mult)
        res["on"] = on[d0:d1]
        out.append(res)
    if len(out) == 1:
        return out[0]
    w = 0.5
    comb = {k: w * out[0][k] + w * out[1][k] for k in ("r", "fundB", "fundD", "cost", "price")}
    comb["on"] = out[0]["on"].astype(float) * w + out[1]["on"].astype(float) * w
    comb["nrebal"] = out[0]["nrebal"] + out[1]["nrebal"]; comb["ntransfer"] = out[0]["ntransfer"] + out[1]["ntransfer"]
    comb["liq"] = out[0]["liq"] + out[1]["liq"]
    return comb


cells = [(a, r) for a in ("BTC", "ETH", "BOTH") for r in ("ON", "F7")]
res = {}
say("\n== Cells (net %/yr on N, NW t lag 10, annual Sharpe; excess over DFF on capital C = N at L 2)")
for e in ("IS", "VAL"):
    d0, d1 = era_idx(e)
    cs = cash[d0:d1]; yy = yrs[d0:d1]
    for c in cells:
        R = run_cell(*c, e)
        st = d2.stats(R["r"])
        ex = d2.stats(R["r"] - cs * 1.0)
        ex3 = d2.stats(R["r"] - cs * 2.0 / 3.0)
        exdep = d2.stats(R["r"] - cs * 1.0 * R["on"])
        c15 = d2.stats(run_cell(*c, e, cost_mult=1.5)["r"])
        lt = d2.stats(run_cell(*c, e, late=1)["r"])
        by = {int(y): round(float(100 * R["r"][yy == y].sum()), 2) for y in np.unique(yy)}
        dec = {k: round(float(100 * 365 * R[k].mean()), 2) for k in ("fundB", "fundD", "price", "cost")}
        pure = A["BTC"]["gap_pure"][d0:d1] if c[0] == "BTC" else (A["ETH"]["gap_pure"][d0:d1] if c[0] == "ETH" else
               0.5 * (A["BTC"]["gap_pure"][d0:d1] + A["ETH"]["gap_pure"][d0:d1]))
        onf = R["on"].mean()
        pure_on = 100 * 365 * np.mean(pure * R["on"])
        res[(c, e)] = dict(st=st, ex=ex, r=R["r"])
        say(f"{e} {c[0]:4s} {c[1]}: net {100*st['ann']:6.2f}  vol {100*st['vol']:5.2f}  t {st['t']:5.2f}  SR {st['sr']:5.2f}"
            f"  maxdd {100*st['maxdd']:6.2f} | excess(C=N) {100*ex['ann']:6.2f} t {ex['t']:5.2f} | excess(C=2/3N) "
            f"{100*ex3['ann']:6.2f} t {ex3['t']:5.2f} | excess dep-only {100*exdep['ann']:6.2f} t {exdep['t']:5.2f}"
            f" | x1.5 {100*c15['ann']:6.2f} late {100*lt['ann']:6.2f} | on {100*onf:4.0f}%  rebal {R['nrebal']} "
            f"transfers {R['ntransfer']} liq-days {len(R['liq'])}")
        say(f"      years {by}  decomposition %/yr: Binance funding received {dec["fundB"]}  Deribit funding paid {dec["fundD"]}"
            f"  price {dec['price']}  costs {dec["cost"]}  | pure gap fB-fD while on {pure_on:.2f}")
        if c[0] != "BOTH":
            U = d2.simulate_usd(A[c[0]], d0, d1, (np.ones(len(days), bool) if c[1] == "ON" else
                                np.nan_to_num(A[c[0]]["s7"], nan=-1) > 0))
            su = d2.stats(U["r"])
            say(f"      pure pair (USD-stable Deribit collateral, descriptive): net {100*su['ann']:6.2f} t {su['t']:5.2f}"
                f" SR {su['sr']:5.2f} | Binance funding {100*365*U['fundB'].mean():6.2f} Deribit funding paid "
                f"{100*365*U['fundD'].mean():6.2f} price {100*365*U['price'].mean():6.2f} | excess(C=N) "
                f"{100*d2.stats(U['r'] - cs)['ann']:6.2f} t {d2.stats(U['r'] - cs)['t']:5.2f}")
        if R["liq"]:
            say("      liquidation-check days (date, Binance loss/N, Deribit loss/N):",
                [(str(np.datetime64(t, 'ms'))[:10], b, dd) for t, b, dd in R["liq"][:6]])

# ---------- random benchmark for F7: circular shifts of the on mask ----------
say("\n== Random benchmark F7: circular shifts of the on/off mask (500 draws, offsets 30..n-30)")
rng = np.random.default_rng(70)
for e in ("IS", "VAL"):
    d0, d1 = era_idx(e)
    n = d1 - d0
    for a in ("BTC", "ETH", "BOTH"):
        obs = res[((a, "F7"), e)]["st"]["sr"]
        sims = []
        for _ in range(500):
            sh = int(rng.integers(30, n - 30))
            sims.append(d2.stats(run_cell(a, "F7", e, shift=sh)["r"])["sr"])
        sims = np.array(sims)
        say(f"  {e} {a} F7: SR {obs:5.2f}  random median {np.median(sims):5.2f}  beaten {100*np.mean(sims < obs):5.1f}%")
    for a in ("BTC", "ETH", "BOTH"):
        st = res[((a, "ON"), e)]["st"]
        say(f"  {e} {a} ON: random side = minus the book; beaten iff net > 0: {'yes' if st['ann'] > 0 else 'no'}")

# ---------- max-over-cells null (IS t), joint stationary bootstrap ----------
say("\n== Max-over-cells null on IS t (joint stationary bootstrap of demeaned series, mean block 20, 1,000 draws)")
for e in ("IS", "VAL"):
    Rm = np.array([res[(c, e)]["r"] for c in cells])
    n = Rm.shape[1]
    obs = max(res[(c, e)]["st"]["t"] for c in cells)
    Z = Rm - Rm.mean(axis=1, keepdims=True)
    mx = []
    for _ in range(1000):
        ix = np.empty(n, int); i = int(rng.integers(n))
        for k in range(n):
            if k == 0 or rng.random() < 1 / 20:
                i = int(rng.integers(n))
            else:
                i = (i + 1) % n
            ix[k] = i
        mx.append(max(d2.stats(z[ix])["t"] for z in Z))
    mx = np.array(mx)
    say(f"  {e}: best cell t {obs:.2f}; null max t 95th pct {np.percentile(mx, 95):.2f}; p {np.mean(mx >= obs):.3f}")

# ---------- power at VAL size for HOLD (667 days) ----------
say("\n== HOLD power at VAL size (VAL annual Sharpe x sqrt(667/365)), raw and excess over cash (C = N)")
for c in cells:
    st = res[(c, "VAL")]["st"]; ex = res[(c, "VAL")]["ex"]
    say(f"  {c[0]:4s} {c[1]}: raw {st['sr']*np.sqrt(667/365):5.2f}  excess {ex['sr']*np.sqrt(667/365):5.2f}")

open(os.path.join(OUT, "report.txt"), "w").write("\n".join(lines) + "\n")
