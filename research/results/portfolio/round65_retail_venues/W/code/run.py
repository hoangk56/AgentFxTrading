"""Stream W cells (VAL only; IS has 0 events). Fills via k2rule (fapi 1m), random benchmark on local 1h closes."""
import os, sys, csv, json, glob, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import k2rule as K
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
W = os.path.join(os.path.dirname(__file__), "..")
CUT = 1735689600000; H = 3600000; M = 60000; DAY = 86400000
ERAS = {"IS": (1577836800000, 1640995200000), "VAL": (1640995200000, CUT)}
_PX = {}
_px0 = K.px


def pxc(sym, t):
    k = (sym, t)
    if k not in _PX:
        _PX[k] = _px0(sym, t)
    return _PX[k]


K.px = pxc
ev = [r for r in csv.DictReader(open(os.path.join(W, "events_kept.csv")))]
for r in ev:
    r["t"] = int(r["t"]); r["tdl"] = int(r["tdl"]) if r["tdl"] else None
    r["L"] = r["t"] // M * M


def cells():
    out = {}
    for c in ("W", "D", "U"):
        for h in (24, 72):
            out[f"{c}{h}"] = [(r, h * H) for r in ev if r["cls"] == c]
    out["Ddl"] = [(r, r["tdl"] - (r["L"] + H)) for r in ev if r["cls"] == "D" and r["tdl"]]
    return out


def one(r, hold, off=H, cost=K.COST):
    te = r["L"] + off; tx = te + hold
    if tx + 2 * M >= CUT:
        return None
    return K.trade(r["perp"], r["L"], hold=hold, cost=cost, off=off)


# ---- local 1h closes for random draws
def b1h(sym):
    best = None
    for p in [os.path.join(R, "binance_1h_full", "1h", sym + ".csv"), os.path.join(R, "binance_basis", "perp_1h", sym + ".csv"),
              os.path.join(R, "upbit", "binance", "perp_1h", sym + ".csv")] + glob.glob(os.path.join(R, "binance", "perp_1h", sym + "_*.csv")):
        if os.path.exists(p):
            with open(p) as f:
                rd = csv.reader(f); next(rd)
                a = np.array([(float(x[0]), float(x[4])) for x in rd if x], float)
            a = a[a[:, 0] < CUT] if len(a) else a
            if len(a) and (best is None or a[0, 0] < best[0, 0] or len(a) > len(best)):
                best = a
    return best


CACHE = os.path.join(R, "upbit_notices", "perp1h_close.npz")


def panel():
    if os.path.exists(CACHE):
        z = np.load(CACHE); return z["T"], list(z["syms"]), z["C"]
    syms = sorted(set(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(R, "binance_basis", "perp_1h", "*.csv")))
                  | set(r["perp"] for r in ev) | {"BTCUSDT"})
    T = np.arange(1577836800000, CUT, H); C = np.full((len(syms), len(T)), np.nan, np.float32)
    for i, s in enumerate(syms):
        a = b1h(s)
        if a is None or not len(a):
            continue
        idx = ((a[:, 0] - T[0]) // H).astype(int); ok = (idx >= 0) & (idx < len(T))
        C[i, idx[ok]] = a[ok, 1]
    np.savez(CACHE, T=T, syms=np.array(syms), C=C)
    return T, syms, C


def g1h(C, T, i, b, te, hold):
    """Gross short alt / long BTC on 1h closes of bars starting at floor_hour(te) and + hold."""
    k0 = int((te // H * H - T[0]) // H); k1 = k0 + int(hold // H)
    if k0 < 0 or k1 >= len(T):
        return np.nan
    a0, a1, b0, b1 = C[i, k0], C[i, k1], C[b, k0], C[b, k1]
    return -((a1 / a0 - 1) - (b1 / b0 - 1))


def main():
    T, syms, C = panel(); si = {s: i for i, s in enumerate(syms)}; b = si["BTCUSDT"]
    rng = np.random.default_rng(65)
    res = {}; lines = []
    for name, lst in cells().items():
        for era, (a0, a1) in ERAS.items():
            sub = [(r, h) for r, h in lst if a0 <= r["t"] < a1]
            rows = []
            for r, h in sub:
                base = one(r, h)
                if base is None:
                    continue
                late = one(r, h, off=H + 5 * M); late2 = one(r, h, off=2 * H)
                te = base[0]
                g = g1h(C, T, si[r["perp"]], b, te, h)
                # random (a): other perps alive at te; (b): same coin at random hours N-180d..N-30d
                k0 = int((te // H * H - T[0]) // H); k1 = k0 + int(h // H)
                alive = [j for j in range(len(syms)) if j not in (b, si[r["perp"]]) and k1 < len(T) and np.isfinite(C[j, k0]) and np.isfinite(C[j, k1])]
                ra = [g1h(C, T, j, b, te, h) for j in alive]
                hrs = (r["t"] - rng.integers(30 * 24, 180 * 24, 400) * H)
                rb = [g1h(C, T, si[r["perp"]], b, x, h) for x in hrs]
                rows.append(dict(coin=r["coin"], perp=r["perp"], t=r["t_utc"], nid=r["nid"], hold_h=h / H, price=base[1], fund=base[2],
                                 net=base[3], net15=base[1] + base[2] - 1.5 * K.COST, late5=late[3] if late else np.nan,
                                 late60=late2[3] if late2 else np.nan, g1h=g, ra=[x for x in ra if np.isfinite(x)], rb=[x for x in rb if np.isfinite(x)],
                                 day=te // DAY, year=r["t_utc"][:4]))
            res[(name, era)] = rows
    return res


def summarize(res):
    rng = np.random.default_rng(66)
    out = []
    for (name, era), rows in res.items():
        if not rows:
            out.append(dict(cell=name, era=era, n=0)); continue
        net = np.array([x["net"] for x in rows]) * 1e4
        m, t, n = K.clt(net, [x["day"] for x in rows]) if len(rows) > 1 else (net[0], np.nan, 1)
        g = np.array([x["g1h"] for x in rows])
        pct = {}
        for key in ("ra", "rb"):
            ok = [i for i, x in enumerate(rows) if len(x[key]) and np.isfinite(g[i])]
            if not ok:
                pct[key] = np.nan; continue
            act = g[ok].mean()
            draws = np.array([np.mean([rng.choice(rows[i][key]) for i in ok]) for _ in range(500)])
            pct[key] = 100 * (draws < act).mean()
        yrs = {}
        for x in rows:
            yrs.setdefault(x["year"], []).append(x["net"] * 1e4)
        out.append(dict(cell=name, era=era, n=n, price=1e4 * np.mean([x["price"] for x in rows]), fund=1e4 * np.mean([x["fund"] for x in rows]),
                        net=m, t=t, median=float(np.median(net)), sd=float(net.std(ddof=1)) if n > 1 else np.nan,
                        sr=m / net.std(ddof=1) if n > 1 else np.nan, net15=1e4 * np.mean([x["net15"] for x in rows]),
                        late5=1e4 * np.nanmean([x["late5"] for x in rows]), late60=1e4 * np.nanmean([x["late60"] for x in rows]),
                        g1h=1e4 * np.nanmean(g), rand_a=pct["ra"], rand_b=pct["rb"],
                        years={y: (len(v), round(float(np.mean(v)))) for y, v in sorted(yrs.items())},
                        trades=[(x["coin"], x["t"], round(x["net"] * 1e4)) for x in rows]))
    return out


if __name__ == "__main__":
    res = main()
    S = summarize(res)
    json.dump(S, open(os.path.join(W, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(W, "trades.csv"), "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["cell", "era", "coin", "perp", "notice_utc", "nid", "hold_h", "price_bp", "fund_bp", "net_bp", "net15_bp", "late5_bp", "late60_bp", "g1h_bp"])
        for (name, era), rows in res.items():
            for x in rows:
                wr.writerow([name, era, x["coin"], x["perp"], x["t"], x["nid"], x["hold_h"]] + [round(1e4 * x[k], 1) for k in ("price", "fund", "net", "net15", "late5", "late60", "g1h")])
    for s in S:
        if s["n"] == 0:
            print(s["cell"], s["era"], "n 0"); continue
        print(f'{s["cell"]:5s} {s["era"]:3s} n {s["n"]:2d} price {s["price"]:+7.0f} fund {s["fund"]:+5.0f} net {s["net"]:+7.0f} t {s["t"]:+.2f} med {s["median"]:+6.0f} '
              f'sd {s["sd"]:5.0f} SR {s["sr"]:+.2f} x1.5 {s["net15"]:+6.0f} +5m {s["late5"]:+6.0f} N+2h {s["late60"]:+6.0f} g1h {s["g1h"]:+6.0f} randA {s["rand_a"]:.0f} randB {s["rand_b"]:.0f} {s["years"]}')
        print("     ", s["trades"])
