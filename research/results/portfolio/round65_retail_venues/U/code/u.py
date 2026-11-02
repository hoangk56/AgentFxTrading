"""Stream U main run (declared in ../HYPOTHESES_U.md): 12 cells, 1m fills, costs 42 bp + funding, benchmarks.
Usage: python -B u.py [draws]"""
import csv, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from udata import *
from fetch import load, price_at

COST = 0.0042
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CELLS = [(k, ru, hold) for k in (2, 4, 8) for ru in (0, 1) for hold in (24, 72)]
ENTRY = {"e1h": H, "e1h5": H + 5 * M, "e2h": 2 * H}
ND = int(sys.argv[1]) if len(sys.argv) > 1 else 500


def name(c):
    return f"k{c[0]}-{'RU' if c[1] else 'ALL'}-H{c[2]}"


def btc_px(btc, t):
    i = (t - G0) // M
    for d in range(5):
        if 0 <= i + d < len(btc) and np.isfinite(btc[i + d]):
            return btc[i + d]
    return np.nan


def fsum(F, a, b):
    if not len(F):
        return np.nan
    w = (F[:, 0] > a + 30000) & (F[:, 0] <= b + 30000)
    return float(F[w, 1].sum())


def era_of(t):
    for e, (lo, hi) in ERAS.items():
        if lo <= t < hi:
            return e
    return None


def stats(x, t):
    day = (t // DAY).astype(np.int64)
    sd = x.std(ddof=1) if len(x) > 1 else np.nan
    return dict(n=len(x), net=x.mean() * 1e4, t=cl_t(x, day), med=np.median(x) * 1e4, sd=sd * 1e4, sr=x.mean() / sd,
                days=len(np.unique(day)))


def main():
    coins, hb, T = panel()
    btc = btc_1m()
    FU = {}
    hT = (T - G0) // H
    rng = np.random.default_rng(65)
    # gross on 1h closes: entry = close of the 1h bar starting at T + 1 h, exit = close of the bar starting hold later
    G = {}
    for hold in (24, 72):
        for ci, c in enumerate(coins):
            h0 = hT + 1; h1 = h0 + hold
            okh = h1 < NH
            g = np.full(len(T), np.nan)
            a0 = c["hc"][np.minimum(h0, NH - 1)]; a1 = c["hc"][np.minimum(h1, NH - 1)]
            b0 = hb[np.minimum(h0, NH - 1)]; b1 = hb[np.minimum(h1, NH - 1)]
            g[okh] = -((a1 / a0 - 1) - (b1 / b0 - 1))[okh]
            g[T + 2 * H + hold * H + 10 * M >= CUT] = np.nan
            G[(ci, hold)] = g
    qtr = np.asarray(T, dtype="datetime64[ms]").astype("datetime64[M]").astype(int) // 3
    # generic-pump pools (D < ln 1.5) per era and hold
    POOL = {}
    for hold in (24, 72):
        for era, (lo, hi) in ERAS.items():
            ru, gg = [], []
            for ci, c in enumerate(coins):
                w = c["ok"] & (c["D"] < np.log(1.5)) & np.isfinite(G[(ci, hold)]) & (T >= lo) & (T < hi)
                ru.append(c["RU"][w]); gg.append(G[(ci, hold)][w])
            ru = np.concatenate(ru); gg = np.concatenate(gg); o = np.argsort(ru)
            POOL[(hold, era)] = (ru[o], gg[o])
    res = {}; trades = {}
    lines = []
    def P(s):
        print(s, flush=True); lines.append(s)
    for cell in CELLS:
        k, ru, hold = cell
        ev = events(coins, T, k, ru, hold)
        rows = []
        for ci, j in ev:
            c = coins[ci]; sym = c["sym"]
            if sym not in FU:
                FU[sym] = funding(sym)
            if "BTCUSDT" not in FU:
                FU["BTCUSDT"] = funding("BTCUSDT")
            if sym not in _C:
                _C[sym] = load(sym)
            cache = _C[sym]
            r = {}
            for en, off in ENTRY.items():
                te = int(T[j] + off); tx = te + hold * H
                ae, ax = price_at(cache, te), price_at(cache, tx)
                if sym.startswith("1000") and not sym.startswith("1000000"):
                    ae, ax = ae / 1000, ax / 1000
                be, bx = btc_px(btc, te), btc_px(btc, tx)
                if not all(np.isfinite([ae, ax, be, bx])):
                    r[en] = None; continue
                price = -((ax / ae - 1) - (bx / be - 1))
                fund = fsum(FU[sym], te + M, tx + M) - fsum(FU["BTCUSDT"], te + M, tx + M)
                r[en] = (price, 0.0 if not np.isfinite(fund) else fund, np.isfinite(fund))
            if r["e1h"] is None:
                continue
            gh = G[(ci, hold)][j]
            rows.append(dict(ci=ci, j=j, coin=c["coin"], T=int(T[j]), D=float(c["D"][j]), RU=float(c["RU"][j]),
                             k24=float(c["k24"][j]), r=r, gh=gh))
        trades[cell] = rows
        P(f"\n== {name(cell)}: {len(ev)} events, {len(rows)} priced")
        res[name(cell)] = {}
        for era in ("IS", "VAL"):
            x = [z for z in rows if era_of(z["T"]) == era]
            if len(x) < 3:
                P(f"{era} n {len(x)}"); continue
            t = np.array([z["T"] for z in x], float)
            price = np.array([z["r"]["e1h"][0] for z in x]); fund = np.array([z["r"]["e1h"][1] for z in x])
            net = price + fund - COST
            st = stats(net, t)
            net15 = price + fund - 1.5 * COST
            late = {}
            for en in ("e1h5", "e2h"):
                y = [(z["T"], z["r"][en][0] + z["r"][en][1] - COST) for z in x if z["r"][en] is not None]
                y = np.array(y)
                if len(y) < 3:
                    late[en] = (np.nan, np.nan); continue
                late[en] = (y[:, 1].mean() * 1e4, cl_t(y[:, 1], (y[:, 0] // DAY).astype(np.int64)))
            yrs = year_of(t)
            by = {int(y): (int((yrs == y).sum()), round(float(net[yrs == y].mean() * 1e4))) for y in np.unique(yrs)}
            o = np.argsort(net)
            nobest = net[o[:-1]].mean() * 1e4
            nofund = sum(not z["r"]["e1h"][2] for z in x)
            # benchmarks (gross on 1h closes)
            act = np.array([z["gh"] for z in x]); okb = np.isfinite(act)
            actm = act[okb].mean()
            # (1) random timing: same coin, same quarter
            rt = np.full((okb.sum(), ND), np.nan)
            for ii, z in enumerate([z for z, b in zip(x, okb) if b]):
                ci = z["ci"]; gg = G[(ci, hold)]
                cand = np.flatnonzero(coins[ci]["ok"] & np.isfinite(gg) & (qtr == qtr[z["j"]]))
                if len(cand):
                    rt[ii] = gg[rng.choice(cand, ND)]
            A = np.nanmean(rt, axis=0)
            # (2) generic pump of the same size, no Korean share
            pr, pg = POOL[(hold, era)]
            gc = np.full((okb.sum(), ND), np.nan)
            for ii, z in enumerate([z for z, b in zip(x, okb) if b]):
                p = np.searchsorted(pr, z["RU"]); lo = max(0, p - 25); hi = min(len(pr), lo + 50); lo = max(0, hi - 50)
                gc[ii] = pg[rng.integers(lo, hi, ND)]
            B = np.nanmean(gc, axis=0)
            pa = float((A < actm).mean() * 100); pb = float((B < actm).mean() * 100)
            # coin concentration
            cc = {}
            for z, v in zip(x, net):
                cc.setdefault(z["coin"], []).append(v)
            top = sorted(cc.items(), key=lambda kv: -len(kv[1]))[:4]
            res[name(cell)][era] = dict(st, gross=price.mean() * 1e4, fund=fund.mean() * 1e4, net15=net15.mean() * 1e4,
                                        late5=late["e1h5"], late1h=late["e2h"], years=by, nobest=nobest, worst=net.min() * 1e4,
                                        best=net.max() * 1e4, gross_h1=actm * 1e4, rand_pct=pa, rand_med=float(np.median(A) * 1e4),
                                        pump_pct=pb, pump_med=float(np.median(B) * 1e4), runup=float(np.mean([z["RU"] for z in x]) * 1e4),
                                        nofund=nofund, top=[(a, len(b), round(float(np.mean(b) * 1e4))) for a, b in top])
            q = res[name(cell)][era]
            P(f"{era} n {q['n']} days {q['days']} gross {q['gross']:+.0f} fund {q['fund']:+.0f} net {q['net']:+.0f} t {q['t']:+.2f} "
              f"med {q['med']:+.0f} sd {q['sd']:.0f} SR {q['sr']:+.3f} x1.5 {q['net15']:+.0f} +5m {late['e1h5'][0]:+.0f} ({late['e1h5'][1]:+.2f}) "
              f"T+2h {late['e2h'][0]:+.0f} ({late['e2h'][1]:+.2f}) nobest {nobest:+.0f} worst {q['worst']:.0f} best {q['best']:.0f}")
            P(f"   years {by}  runup {q['runup']:+.0f}  h1 gross {q['gross_h1']:+.0f}  random-timing pct {pa:.1f} (med {q['rand_med']:+.0f})  "
              f"generic-pump pct {pb:.1f} (med {q['pump_med']:+.0f})  no-funding-data {nofund}  top coins {q['top']}")
    json.dump(res, open(os.path.join(OUT, "u_results.json"), "w"), indent=1, default=float)
    # max-over-cells null on IS from random timing (independent draws per cell: an upper bound for correlated cells)
    mx = []
    for d in range(ND if ND < 50 else 200):
        best = 0
        for cell in CELLS:
            x = [z for z in trades[cell] if era_of(z["T"]) == "IS"]
            vals, ts = [], []
            for z in x:
                ci = z["ci"]; gg = G[(ci, cell[2])]
                cand = np.flatnonzero(coins[ci]["ok"] & np.isfinite(gg) & (qtr == qtr[z["j"]]))
                if len(cand):
                    jj = rng.choice(cand); vals.append(gg[jj] - COST); ts.append(T[jj])
            if len(vals) > 3:
                tt = cl_t(np.array(vals), (np.array(ts) // DAY).astype(np.int64))
                best = max(best, tt)
        mx.append(best)
    P(f"\nmax-over-12-cells IS t under random timing (net of cost): median {np.median(mx):.2f}, 95th pct {np.percentile(mx, 95):.2f}")
    import pickle
    pickle.dump(dict(trades={name(c): v for c, v in trades.items()}), open(os.path.join(UV, "u_trades.pkl"), "wb"))
    open(os.path.join(OUT, "u_output.txt"), "w").write("\n".join(lines) + "\n")


_C = {}
if __name__ == "__main__":
    main()
