"""Stream JP analysis (rules declared in JP/HYPOTHESES_JP.md before any price was loaded). A2's trade / slip / funding /
clustered-t logic copied unchanged from round65_retail_venues/A2/code/analyze.py; the event set, the trading-start exit
L (days later) and the random benchmark (1h bars, same coin, +-180 d) are this stream's declared changes.
Reads research/data/jp_notices/npz, local 1h perp klines (cut ts < 2025-01-01) and local funding files."""
import csv, json, os, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
import net
from events import load_events

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
NPZ = os.path.join(net.D, "npz")
OUTD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = 3600000
DAYMS = 86400000
END = 1735689600000
COST = 0.0020
OFFS = [-60, -30, -10, -5, -2, -1, 0, 1, 2, 3, 5, 10, 20, 30, 60, 120, 300]
CELLS = [("D5-L", 5, "L"), ("D10-L", 10, "L"), ("D2-5m", 2, "5m"), ("D5-5m", 5, "5m"), ("D30-5m", 30, "5m")]
_C = {}


def dstr(ms):
    return str(np.datetime64(int(ms), "ms"))[:10]


def load2(sym, days):  # trades of the N-day and L-day windows, concatenated and time-sorted
    k = (sym, tuple(days))
    if k not in _C:
        parts = [np.load(os.path.join(NPZ, f"{sym}_{d}.npz")) for d in sorted(set(days))]
        t = np.concatenate([z["t"] for z in parts]); p = np.concatenate([z["p"] for z in parts])
        o = np.argsort(t, kind="stable")
        _C[k] = dict(t=t[o], p=p[o])
    return _C[k]


# ---- copied unchanged from A2 analyze.py ----
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
    rs = []
    for k in np.unique(bins):
        q = p[bins == k]; rs.append((q.max() - q.min()) / q.min())
    return 0.5 * float(np.median(rs))


_FU = {}


def fund(sym, a, b):
    assert b < END + DAYMS
    if sym not in _FU:
        p = os.path.join(R, "binance", "funding", sym + ".csv")
        rows = []
        if os.path.exists(p):
            rows = [(float(x["t"]), float(x["rate"])) for x in csv.DictReader(open(p)) if float(x["t"]) < END]
        _FU[sym] = np.array(rows) if rows else np.zeros((0, 2))
    F = _FU[sym]
    if not len(F) or F[:, 0].min() > a or F[:, 0].max() < b - 9 * H:
        e_ = min(b + DAYMS, END - 1)
        s, body = net.get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={a - DAYMS}&endTime={e_}&limit=1000", note="GET funding")
        js = json.loads(body) if s == 200 else []
        F = np.array([(float(x["fundingTime"]), float(x["fundingRate"])) for x in js if x["fundingTime"] < END]) if js else np.zeros((0, 2))
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
# ---- end of the copy ----


_K = {}


def k1h(sym, src="binance_basis/perp_1h"):  # local perp opens, cut ts < 2025-01-01
    if (sym, src) not in _K:
        a = np.loadtxt(os.path.join(R, src, sym + ".csv"), delimiter=",", skiprows=1, usecols=(0, 1))
        a = a[a[:, 0] < END]
        _K[(sym, src)] = (a[:, 0].astype(np.int64), a[:, 1])
    return _K[(sym, src)]


def rand_ok(r, src, step):
    ta_, pa_ = k1h(r["perp"], src); tb_, pb_ = k1h("BTCUSDT", src)
    hold = max(1, int(round((r["L"] - r["N"]) / step)))
    common, ia, ib_ = np.intersect1d(ta_, tb_, return_indices=True)
    pos = {int(t): i for i, t in enumerate(common)}
    ok = []
    for i, t in enumerate(common):
        te = t + hold * step
        if te >= END or abs(t - r["N"]) > 180 * DAYMS:
            continue
        if not (te < r["N"] - 7 * DAYMS or t > r["L"] + 7 * DAYMS):
            continue
        if int(te) in pos:
            ok.append((i, pos[int(te)]))
    return np.array(ok), pa_[ia], pb_[ib_]


def main():
    E = load_events()
    out = open(os.path.join(OUTD, "results.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    rows = []
    for e in E:
        days = [dstr(e["N"]), dstr(e["L"])]
        A = load2(e["perp"], days); B = load2("BTCUSDT", days); N = e["N"]
        ra, rb = at(A, N - 60000), at(B, N - 60000)
        path = {o: float(np.log(at(A, N + o * 1000) / ra) - np.log(at(B, N + o * 1000) / rb)) for o in OFFS}
        a0, a1 = np.searchsorted(A["t"], [N - 300000, N + 300000])
        ta, pa = A["t"][a0:a1], A["p"][a0:a1]
        ib = np.searchsorted(B["t"], ta, "right") - 1
        r = np.log(pa / ra) - np.log(B["p"][ib] / rb)
        hit = np.where(r >= 0.02)[0]
        on_a = (ta[hit[0]] - N) / 1000 if len(hit) else None
        hit1 = np.where(r >= 0.005)[0]  # declared extra: +0.5 % onset (JP moves expected small)
        on_a5 = (ta[hit1[0]] - N) / 1000 if len(hit1) else None
        s0, s1 = np.searchsorted(A["t"], [N - 600000, N + 300000])
        bins = (A["t"][s0:s1] - (N - 600000)) // 1000
        cnt = np.bincount(bins, minlength=900)[:900]
        base = np.median(cnt[:540]); thr = max(10, 10 * base)
        w = np.where(cnt[300:] >= thr)[0]
        on_b = int(w[0]) - 300 if len(w) else None
        # trade-count ratio: trades in [N, N + 60 s) vs the mean per minute over [N - 10 min, N - 1 min)
        c_post = int(((A["t"] >= N) & (A["t"] < N + 60000)).sum())
        c_pre = ((A["t"] >= N - 600000) & (A["t"] < N - 60000)).sum() / 9.0
        n_pre = int(((A["t"] >= N - 60000) & (A["t"] < N)).sum())
        row = dict(e, path=path, on_a=on_a, on_a5=on_a5, on_b=on_b, base=float(base), n_pre60=n_pre,
                   cnt_ratio=c_post / max(c_pre, 1e-9))
        for c, d, xn in CELLS + [("D10-L", 10, "L"), ("D10-5m", 10, "5m"), ("D60-5m", 60, "5m")]:
            X = N + 300000 if xn == "5m" else e["L"]
            row[c] = trade(e, d, X, A, B)
            row[c + "-x15"] = trade(e, d, X, A, B, 1.5)
        rows.append(row)

    P("# Stream JP results (bp unless noted). Events", len(rows), "IS", sum(r["era"] == "IS" for r in rows))
    P("\n## Per event: onset (s vs N), path r (bp, alt vs BTC since N - 60 s), Upbit overlap, hold to L (h)")
    P("venue    coin   era  day         hold_h  upbit  base/s  on2%   on0.5%  onB  cnt1m/pre  r(-10) r(-1)  r(0)  r(+2)  r(+5)  r(+10) r(+30) r(+60) r(+300)")
    f = lambda v: "  --  " if v is None else f"{v:6.1f}"
    for r in rows:
        p = r["path"]
        P(f"{r['venue']:8s} {r['coin']:6s} {r['era']:4s} {r['day']} {(r['L']-r['N'])/H:7.1f} {r['upbit']:5s} {r['base']:6.1f} {f(r['on_a'])} {f(r['on_a5'])} {f(r['on_b'])} {r['cnt_ratio']:8.1f} "
          + " ".join(f"{1e4*p[o]:6.0f}" for o in (-10, -1, 0, 2, 5, 10, 30, 60, 300)))
    for era in ("IS", "VAL", "ALL"):
        S = [r for r in rows if era == "ALL" or r["era"] == era]
        P(f"\n## Path {era} (n {len(S)}): r(t) vs ref N - 60 s, bp: q25 / median / q75 / mean")
        for o in OFFS:
            v = 1e4 * np.array([r["path"][o] for r in S])
            P(f"  t {o:+5d}s  {np.percentile(v,25):7.0f} {np.median(v):7.0f} {np.percentile(v,75):7.0f} {v.mean():7.0f}")
        for k in ("on_a", "on_a5", "on_b"):
            v = np.array([r[k] for r in S if r[k] is not None])
            if len(v):
                P(f"  {k}: n {len(v)}/{len(S)}  median {np.median(v):.1f} s  min {v.min():.1f}  max {v.max():.1f}  share < 0: {np.mean(v<0):.2f}")
            else:
                P(f"  {k}: n 0/{len(S)}")
        P(f"  trade-count ratio first minute / pre: median {np.median([r['cnt_ratio'] for r in S]):.2f}")

    P("\n## Cells (net bp per trade; 20 bp + slippage + real funding; t clustered by notice day). D5-L is the only rule;")
    P("## the others are descriptive (declared, not selectable).")
    P("cell     era  n(days)  gross   slip  fund    net      t   median   SR    x1.5   late   years(net)            yrs+  power")
    cells = {}
    LATE = {"D5-L": "D10-L", "D10-L": "D10-L", "D2-5m": "D5-5m", "D5-5m": "D10-5m", "D30-5m": "D60-5m"}
    n_val_years = 3.0
    for c, d, xn in CELLS:
        for era in ("IS", "VAL"):
            S = [r for r in rows if r["era"] == era and r[c] is not None]
            if len(S) < 2:
                P(f"{c:8s} {era:4s} n {len(S)}"); continue
            net_ = np.array([r[c]["net"] for r in S]); days = [r["day"] for r in S]
            m, t, n = clt(net_, days); sr = net_.mean() / net_.std(ddof=1)
            x15 = np.mean([r[c + "-x15"]["net"] for r in S]); late = np.mean([r[LATE[c]]["net"] for r in S])
            yrs = {}
            for r in S:
                yrs.setdefault(r["year"], []).append(r[c]["net"])
            ys = " ".join(f"{y}:{1e4*np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
            n_hold = len(S) / n_val_years * 1.83 if era == "VAL" else np.nan
            pw = sr * np.sqrt(n_hold) if era == "VAL" else np.nan
            q = cells[(c, era)] = dict(n=n, days=len(set(days)), net=1e4 * m, t=t, sr=sr, x15=1e4 * x15, late=1e4 * late,
                                       gross=1e4 * np.mean([r[c]["gross"] for r in S]), slip=1e4 * np.mean([r[c]["slip"] for r in S]),
                                       fund=1e4 * np.mean([r[c]["fund"] for r in S]), median=1e4 * np.median(net_), years=ys,
                                       yrs_pos=f"{sum(np.mean(v)>0 for v in yrs.values())}/{len(yrs)}", power=pw, n_hold=n_hold)
            P(f"{c:8s} {era:4s} {n:3d}({q['days']:2d}) {q['gross']:7.0f} {q['slip']:5.0f} {q['fund']:5.0f} {q['net']:7.0f} {t:6.2f} {q['median']:7.0f} {sr:6.2f} {q['x15']:6.0f} {q['late']:6.0f}  {ys:30s} {q['yrs_pos']:4s} {pw:5.2f}")
    # without Upbit-overlap events (same coin listed on Upbit within 7 days of N)
    P("\n## D5-L without Upbit-overlap events")
    for era in ("IS", "VAL"):
        S = [r for r in rows if r["era"] == era and r["D5-L"] is not None and r["upbit"] == "-"]
        if len(S) >= 2:
            m, t, n = clt([r["D5-L"]["net"] for r in S], [r["day"] for r in S])
            P(f"  {era}: n {n}  net {1e4*m:.0f}  t {t:.2f}")

    # random benchmark (declared): same coin, random 1h-open entries within N +- 180 d, whole hold outside
    # [N - 7 d, L + 7 d] and before 2025-01-01; hold = round((L - N) / 1 h) h for L-cells, 0 h (skipped) for 5m cells.
    rng = np.random.default_rng(69)
    NS = 1000
    P(f"\n## Random benchmark D5-L ({NS} draw sets; same coin, 1h opens, N +- 180 d; gross; percentile of the event gross mean)")
    G = np.full((NS, len(rows)), np.nan)
    for j, r in enumerate(rows):
        ok, pa2, pb2 = rand_ok(r, "binance_basis/perp_1h", H)
        r["rand_src"] = "1h"
        if len(ok) < 100:  # deviation (data): sparse local 1h file (KLAY, CYBER) -> daily opens, hold rounded to days
            ok, pa2, pb2 = rand_ok(r, "binance/perp_1d", DAYMS)
            r["rand_src"] = "1d"
        u = ok[rng.integers(0, len(ok), NS)]
        G[:, j] = (pa2[u[:, 1]] / pa2[u[:, 0]] - 1) - (pb2[u[:, 1]] / pb2[u[:, 0]] - 1)
        r["n_rand_ok"] = len(ok)
    for era in ("IS", "VAL"):
        idx = [j for j, r in enumerate(rows) if r["era"] == era and r["D5-L"] is not None]
        if not idx:
            continue
        ev = np.mean([rows[j]["D5-L"]["gross"] for j in idx])
        pct = 100 * np.mean(G[:, idx].mean(1) < ev)
        cells[("D5-L", era)]["rand_pct"] = pct
        days = [rows[j]["day"] for j in idx]
        cost = np.array([COST + rows[j]["D5-L"]["slip"] for j in idx])
        ts = np.array([clt(G[s, idx] - cost, days)[1] for s in range(NS)])
        P(f"  D5-L {era}: event gross {1e4*ev:7.0f}  random mean {1e4*np.nanmean(G[:, idx]):6.0f}  beats {pct:5.1f} %  "
          f"(random net t 95th pct {np.percentile(ts,95):.2f}; min ok entries per event {min(rows[j]['n_rand_ok'] for j in idx)}; "
          f"1d fallback for {[rows[j]['coin'] for j in idx if rows[j]['rand_src'] == '1d']})")
        # without the P10 (Coincheck 2020-21 press, 10:00 JST) stamps
        idx2 = [j for j in idx if rows[j]["stamp"] != "P10"]
        if len(idx2) >= 2:
            m, t, n = clt([rows[j]["D5-L"]["net"] for j in idx2], [rows[j]["day"] for j in idx2])
            ev2 = np.mean([rows[j]["D5-L"]["gross"] for j in idx2])
            P(f"  D5-L {era} without P10 stamps: n {n}  net {1e4*m:.0f}  t {t:.2f}  random beats {100*np.mean(G[:, idx2].mean(1) < ev2):.1f} %")
    json.dump({f"{c}|{e}": v for (c, e), v in cells.items()}, open(os.path.join(OUTD, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(OUTD, "trades.csv"), "w") as fh:
        w = csv.writer(fh)
        w.writerow(["venue", "coin", "era", "day", "N", "L", "upbit", "on_a_s", "on_a5_s", "on_b_s", "cnt_ratio"] + [f"r{o}" for o in OFFS]
                   + [f"{c}_{k}" for c, _, _ in CELLS for k in ("gross", "slip", "fund", "net")])
        for r in rows:
            w.writerow([r["venue"], r["coin"], r["era"], r["day"], r["N"], r["L"], r["upbit"], r["on_a"], r["on_a5"], r["on_b"], round(r["cnt_ratio"], 2)]
                       + [round(1e4 * r["path"][o], 1) for o in OFFS]
                       + [(round(1e4 * r[c][k], 1) if r[c] else "") for c, _, _ in CELLS for k in ("gross", "slip", "fund", "net")])
    out.close()


if __name__ == "__main__":
    main()
