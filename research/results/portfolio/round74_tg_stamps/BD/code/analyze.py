"""Stream BD analysis (rules declared in BD/HYPOTHESES_BD.md): short the delisted coin's perp at the worst price of
the 1 s bucket of the first trade at or after N + 5 s, buy back the same way at N + 5 min / 60 min / 24 h.
Classes S (spot delisting) and F (perp delisting) graded; MT VAL-only info. Burst timing, random benchmarks (a) same
coin random seconds, (b) non-delisting Binance post times in the loaded two days. Spot path info for class S.
Reads research/data/binance_delist_tg/sec only (plus funding / BTC 1m via net, all <= 2024-12-31).
Run: python -I analyze.py [edited]   (edited -> keep edited posts too)"""
import csv, json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net, pull

OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/BD"
FEE = {"bu": 0.0005, "by": 0.00055}
EXITS = {"5m": 300, "60m": 3600, "24h": 86400}
D_ENTRY, D_LATE = 5, 10
OFFS = [-600, -60, -10, -5, -2, 0, 2, 5, 10, 30, 60, 300, 3600]
IS_END, VAL_END = 1640995200, 1735689600
_A = {}


def arr(v, sym, d0):
    """two-day per-second arrays (day d0 and d0 + 1, the second NaN if missing or >= 2025)."""
    k = (v, sym, d0)
    if k in _A:
        return _A[k]
    d1 = str(dt.date.fromisoformat(d0) + dt.timedelta(days=1))
    out = {}
    for j, d in enumerate((d0, d1)):
        p = pull.path(v, sym, d)
        if d <= "2024-12-31" and os.path.exists(p):
            z = np.load(p); x = {f: z[f] for f in ("last", "lo", "hi", "n")}
        else:
            x = dict(last=np.full(86400, np.nan), lo=np.full(86400, np.nan), hi=np.full(86400, np.nan), n=np.zeros(86400, np.int32))
        for f in x:
            out.setdefault(f, []).append(x[f])
    S = {f: np.concatenate(out[f]) for f in out}
    # carry day-0 last into day 1 until its first trade
    S["base"] = int(np.datetime64(d0, "s").astype(np.int64))
    _A[k] = S
    return S


def fill(S, T, side):
    """first second >= T with a trade; side -1 = we sell (lo), +1 = we buy (hi). -> (price, second index) or None."""
    i = T - S["base"]
    if i < 0 or i >= len(S["n"]):
        return None
    j = np.argmax(S["n"][i:i + 600] > 0)
    if S["n"][i + j] == 0:
        return None  # no trade in 10 min
    return (S["lo"] if side < 0 else S["hi"])[i + j], i + j


def last(S, T):
    i = T - S["base"]
    return S["last"][i] if 0 <= i < len(S["last"]) else np.nan


_FU = {}


def funding(v, sym, a, b):
    """sum of funding rates with stamps in (a, b] (seconds); short receives +rate."""
    k = (v, sym, a)
    if k in _FU:
        return _FU[k]
    a_ms, b_ms = a * 1000, min(b * 1000, net.END_MS - 1)
    if v == "bu":
        u = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={a_ms}&endTime={b_ms}&limit=1000"
        body, s = net.get(u); js = json.loads(body) if body else []
        rates = [float(x["fundingRate"]) for x in js if a_ms < int(x["fundingTime"]) <= b_ms]
    else:
        u = f"https://api.bybit.com/v5/market/funding/history?category=linear&symbol={sym}&startTime={a_ms}&endTime={b_ms}&limit=200"
        body, s = net.get(u); js = json.loads(body) if body else {}
        L = (js.get("result") or {}).get("list") or []
        rates = [float(x["fundingRate"]) for x in L if a_ms < int(x["fundingRateTimestamp"]) <= b_ms]
    _FU[k] = float(sum(rates))
    return _FU[k]


_BTC = {}


def btc(T):
    """BTCUSDT spot 1m close of the minute containing T (hedge sensitivity), cached per UTC day."""
    d = dt.datetime.fromtimestamp(T, dt.timezone.utc).strftime("%Y-%m-%d")
    if d > "2024-12-31":
        return np.nan
    if d not in _BTC:
        fn = os.path.join(net.D, "btc1m", d + ".json"); os.makedirs(os.path.dirname(fn), exist_ok=True)
        if not os.path.exists(fn):
            s0 = int(np.datetime64(d, "s").astype(np.int64)) * 1000; rows = []
            end = min(s0 + 86400000 - 1, net.END_MS - 1)
            for st in (s0, s0 + 1000 * 60000):
                body, _ = net.get(f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={st}&endTime={end}&limit=1000")
                rows += json.loads(body or b"[]")
            json.dump({str(int(r[0]) // 1000): float(r[4]) for r in rows}, open(fn, "w"))
        _BTC[d] = {int(k): v for k, v in json.load(open(fn)).items()}
    return _BTC[d].get(T - T % 60, np.nan)


def clt(x, day):
    x = np.asarray(x, float); n = len(x)
    if n < 2:
        return (x.mean() if n else np.nan), np.nan, n
    m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    se = np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n
    return m, (m / se if se > 0 else np.nan), n


def trade(r, S, d, hold, costmul=1.0, hedge=False):
    N = int(r["time"])
    e = fill(S, N + d, -1)
    if e is None:
        return None
    pe, ie = e
    x = fill(S, N + hold, +1)
    if x is None or x[1] < ie:
        return None
    px, ix = x
    if not (np.isfinite(pe) and np.isfinite(px)):
        return None
    gross = 1 - px / pe
    te, tx = S["base"] + ie, S["base"] + ix
    f = funding(r["venue"], r["sym"], te, tx) if hold >= 28800 else 0.0
    cost = 2 * FEE[r["venue"]]
    h = 0.0
    if hedge:
        b0, b1 = btc(te), btc(tx)
        h = b1 / b0 - 1 - 2 * 0.0005
    return dict(gross=gross, fund=f, cost=cost, net=gross + f - costmul * cost + h, lag=te - N)


def era(N):
    return "IS" if 1577836800 <= N < IS_END else ("VAL" if IS_END <= N < VAL_END else "pre")


def main(keep_edited=False):
    R = list(csv.DictReader(open(os.path.join(OUT, "trades_in.csv"))))
    R = [r for r in R if int(r["time"]) < VAL_END]
    if not keep_edited:
        R = [r for r in R if r["edited"] == "0"]
    tag = "_edited" if keep_edited else ""
    fo = open(os.path.join(OUT, f"results{tag}.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=fo))
    P(f"# Stream BD results{' (edited posts kept)' if keep_edited else ' (edited posts dropped)'}; bp unless noted")
    rows = []
    for r in R:
        if not r["venue"]:
            continue
        S = arr(r["venue"], r["sym"], r["d0"])
        N = int(r["time"])
        if not np.isfinite(last(S, N - 60)):
            continue
        ref = last(S, N - 60)
        row = dict(r, era=era(N), year=r["utc"][:4], day=r["utc"][:10])
        row["path"] = {o: float(np.log(last(S, N + o) / ref)) for o in OFFS}
        # onset: first second with lo <= ref * 0.98 in [N - 600, N + 600]
        i0 = N - 600 - S["base"]; lo = S["lo"][i0:i0 + 1200]
        hit = np.where(lo <= ref * 0.98)[0]
        row["onset"] = int(hit[0]) - 600 if len(hit) else None
        row["n_pre"] = int(S["n"][N - 60 - S["base"]:N - S["base"]].sum())
        for xn, hold in EXITS.items():
            row[xn] = trade(row, S, D_ENTRY, hold)
            row[xn + "_x15"] = trade(row, S, D_ENTRY, hold, 1.5)
            row[xn + "_late"] = trade(row, S, D_LATE, hold)
            row[xn + "_hedge"] = trade(row, S, D_ENTRY, hold, hedge=True)
        rows.append(row)
    no_perp = [r for r in R if not r["venue"]]
    P("\n## Coverage (coins with a short instrument / without), by class and era")
    for c in ("S", "F", "MT"):
        for e in ("pre", "IS", "VAL"):
            a = sum(1 for r in rows if r["cls"] == c and r["era"] == e)
            b = sum(1 for r in no_perp if r["cls"] == c and era(int(r["time"])) == e)
            if a or b:
                P(f"  {c:3s} {e:4s} with instrument {a:4d}  without {b:4d}  (bu {sum(1 for r in rows if r['cls']==c and r['era']==e and r['venue']=='bu')}, by {sum(1 for r in rows if r['cls']==c and r['era']==e and r['venue']=='by')})")

    P("\n## Per event: onset of -2 % (s vs N), path r (bp vs N - 60 s)")
    P("utc                 cls coin       venue onset  " + " ".join(f"{o:>6d}" for o in OFFS))
    for r in rows:
        P(f"{r['utc']} {r['cls']:3s} {r['coin']:10s} {r['venue']:3s} {('--' if r['onset'] is None else r['onset']):>6} "
          + " ".join(f"{1e4*r['path'][o]:6.0f}" for o in OFFS))

    P("\n## Path by class / era: median (mean) r(t), bp; share of the r(300 s) move done by N + 5 s")
    for c in ("S", "F", "MT"):
        for e in ("IS", "VAL"):
            S_ = [r for r in rows if r["cls"] == c and r["era"] == e]
            if not S_:
                continue
            P(f"  {c} {e} n {len(S_)}: " + "  ".join(f"{o}:{1e4*np.median([r['path'][o] for r in S_]):.0f}({1e4*np.mean([r['path'][o] for r in S_]):.0f})" for o in OFFS))
            neg = [r for r in S_ if r["path"][300] < -0.002]
            if neg:
                sh = [r["path"][5] / r["path"][300] for r in neg]
                P(f"     burst share r(5s)/r(300s) over {len(neg)} events with r(300s) < -20 bp: median {np.median(sh):.2f}, "
                  f"r(0)/r(300s) median {np.median([r['path'][0] / r['path'][300] for r in neg]):.2f}; onset<=0 s: "
                  f"{sum(1 for r in neg if r['onset'] is not None and r['onset'] <= 0)}/{len(neg)}")

    P("\n## Cells (net bp per trade, short at N + 5 s; taker fees + worst-of-1 s fills; funding on 24 h; t clustered by day)")
    P("cell      era  n(days)  gross  fund    net      t  median   SR   win  x1.5   late(+10s) hedged  years")
    cells = {}
    for c in ("S", "F", "MT"):
        for xn in EXITS:
            for e in ("IS", "VAL"):
                S_ = [r for r in rows if r["cls"] == c and r["era"] == e and r[xn] is not None]
                if not S_:
                    continue
                net_ = np.array([r[xn]["net"] for r in S_]); days = [r["day"] for r in S_]
                m, t, n = clt(net_, days); sr = net_.mean() / net_.std(ddof=1) if n > 1 else np.nan
                g = lambda k: 1e4 * np.mean([r[k]["net"] for r in S_ if r[k] is not None]) if any(r[k] is not None for r in S_) else np.nan
                yrs = {}
                for r in S_:
                    yrs.setdefault(r["year"], []).append(r[xn]["net"])
                ys = " ".join(f"{y}:{1e4*np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
                q = dict(n=n, days=len(set(days)), gross=1e4 * np.mean([r[xn]["gross"] for r in S_]),
                         fund=1e4 * np.mean([r[xn]["fund"] for r in S_]), net=1e4 * m, t=t, med=1e4 * np.median(net_), sr=sr,
                         win=np.mean(net_ > 0), x15=g(xn + "_x15"), late=g(xn + "_late"), hedge=g(xn + "_hedge"), years=ys,
                         yrs_pos=f"{sum(np.mean(v) > 0 for v in yrs.values())}/{len(yrs)}")
                cells[(c, xn, e)] = q
                P(f"{c}-{xn:4s} {e:4s} {n:3d}({q['days']:3d}) {q['gross']:6.0f} {q['fund']:5.0f} {q['net']:6.0f} {t:6.2f} {q['med']:6.0f} {sr:5.2f} {q['win']:4.2f} "
                  f"{q['x15']:6.0f} {q['late']:6.0f} {q['hedge']:6.0f}  {ys}")

    # random (a): same coin, same two days, random seconds outside the event zone; same fill / cost model
    rng = np.random.default_rng(74)
    NS = 500
    P(f"\n## Random (a): same coin / same two days, random entry seconds outside [N - 15 min, N + hold + 15 min], {NS} sets")
    G = {}
    for xn, hold in EXITS.items():
        M = np.full((NS, len(rows)), np.nan)
        for j, r in enumerate(rows):
            S = arr(r["venue"], r["sym"], r["d0"]); N = int(r["time"]) - S["base"]
            Ltot = len(S["n"])
            ok = np.arange(0, Ltot - hold - 600)
            ok = ok[((ok + hold + 900 < N - 900) | (ok > N + hold + 900)) & np.isfinite(S["last"][ok]) & np.isfinite(S["last"][np.minimum(ok + hold, Ltot - 1)])]
            if len(ok) < 50:
                continue
            u = rng.choice(ok, NS)
            for s, uu in enumerate(u):
                e_ = fill(S, S["base"] + int(uu), -1); x_ = fill(S, S["base"] + int(uu) + hold, +1)
                if e_ and x_ and np.isfinite(e_[0]) and np.isfinite(x_[0]):
                    M[s, j] = 1 - x_[0] / e_[0] - 2 * FEE[r["venue"]]
        G[xn] = M
    for e in ("IS", "VAL"):
        maxt = np.full(NS, -np.inf)
        for c in ("S", "F"):
            for xn in EXITS:
                idx = [j for j, r in enumerate(rows) if r["cls"] == c and r["era"] == e and r[xn] is not None and np.isfinite(G[xn][:, j]).all()]
                if len(idx) < 2:
                    continue
                ev = np.mean([rows[j][xn]["net"] - rows[j][xn]["fund"] for j in idx])
                Mx = G[xn][:, idx]; pct = 100 * np.mean(Mx.mean(1) < ev)
                cells[(c, xn, e)]["rand_a"] = pct
                days = [rows[j]["day"] for j in idx]
                ts = np.array([clt(Mx[s], days)[1] for s in range(NS)])
                maxt = np.maximum(maxt, np.nan_to_num(ts, nan=-np.inf))
                P(f"  {c}-{xn:4s} {e:4s} n {len(idx)} event net ex-funding {1e4*ev:6.0f}  random mean {1e4*np.nanmean(Mx):6.0f}  beats {pct:5.1f} %")
        if np.isfinite(maxt).any():
            P(f"  {e}: 95th pct of max-over-cells random t = {np.percentile(maxt[np.isfinite(maxt)], 95):.2f}")

    # random (b): non-delisting Binance post times inside the loaded two days, same coin, same hold
    P("\n## Random (b): same coin at other (non-delisting) @binance_announcements post times in the same two days")
    allp = list(csv.DictReader(open(os.path.join(OUT, "events_binance_announcements.csv"))))
    other = np.array([int(p["time"]) for p in allp if p["cls"] == "" and int(p["time"]) < VAL_END])
    for c in ("S", "F"):
        for xn, hold in EXITS.items():
            for e in ("IS", "VAL"):
                S_ = [r for r in rows if r["cls"] == c and r["era"] == e and r[xn] is not None]
                ev, rb = [], []
                for r in S_:
                    S = arr(r["venue"], r["sym"], r["d0"]); N = int(r["time"])
                    cand = other[(other >= S["base"]) & (other + hold + 60 < S["base"] + len(S["n"])) & (np.abs(other - N) > 900 + hold)]
                    vals = []
                    for T in cand:
                        e_ = fill(S, int(T) + D_ENTRY, -1); x_ = fill(S, int(T) + hold, +1)
                        if e_ and x_ and np.isfinite(e_[0]) and np.isfinite(x_[0]):
                            vals.append(1 - x_[0] / e_[0] - 2 * FEE[r["venue"]])
                    if vals:
                        ev.append(r[xn]["net"] - r[xn]["fund"]); rb.append(np.mean(vals))
                if ev:
                    P(f"  {c}-{xn:4s} {e:4s} n {len(ev)}: event {1e4*np.mean(ev):6.0f}  random-post mean {1e4*np.mean(rb):6.0f}  event > random-post in {np.mean(np.array(ev) > np.array(rb)):.2f} of coins")

    # information only: Binance spot path of class-S coins (spot cannot be shorted; measures reaction / burst timing)
    P("\n## Info: Binance spot path of class-S coins (not tradeable short), r(t) vs N - 60 s, bp; median (mean)")
    SP = []
    for r in R:
        if r["cls"] != "S" or not r["spot"]:
            continue
        S = arr("bs", r["spot"], r["d0"]); N = int(r["time"]); ref = last(S, N - 60)
        if not np.isfinite(ref):
            continue
        pth = {o: float(np.log(last(S, N + o) / ref)) for o in OFFS + [86400]}
        # first second with a trade at or after N, and its low (the first sell-side print)
        SP.append(dict(era=era(N) if N >= 1577836800 else "pre", year=r["utc"][:4], day=r["utc"][:10], path=pth, coin=r["coin"]))
    for e in ("pre", "IS", "VAL"):
        S_ = [x for x in SP if x["era"] == e]
        if not S_:
            continue
        P(f"  spot {e} n {len(S_)} ({len(set(x['day'] for x in S_))} days): " + "  ".join(
            f"{o}:{1e4*np.nanmedian([x['path'][o] for x in S_]):.0f}({1e4*np.nanmean([x['path'][o] for x in S_]):.0f})" for o in OFFS + [86400]))
        neg = [x for x in S_ if x["path"][300] < -0.002]
        if neg:
            P(f"     share of r(300 s) done by N + 5 s: median {np.nanmedian([x['path'][5] / x['path'][300] for x in neg]):.2f}; by N: "
              f"{np.nanmedian([x['path'][0] / x['path'][300] for x in neg]):.2f}; by N - 10 s: {np.nanmedian([x['path'][-10] / x['path'][300] for x in neg]):.2f} (n {len(neg)} of {len(S_)} with r(300 s) < -20 bp)")
        for k in (300, 3600, 86400):
            v = np.array([x["path"][k] - x["path"][5] for x in S_]); ok = np.isfinite(v)
            m, t, n = clt(v[ok], [x["day"] for x, o in zip(S_, ok) if o])
            P(f"     r({k} s) - r(5 s) (gross move after a +5 s entry): mean {1e4*m:.0f} t {t:.2f} n {n}")
    with open(os.path.join(OUT, f"spot_paths{tag}.csv"), "w") as f:
        w = csv.writer(f); w.writerow(["day", "coin", "era"] + [f"r{o}" for o in OFFS + [86400]])
        for x in SP:
            w.writerow([x["day"], x["coin"], x["era"]] + [round(1e4 * x["path"][o], 1) for o in OFFS + [86400]])

    json.dump({"|".join(k): v for k, v in cells.items()}, open(os.path.join(OUT, f"cells{tag}.json"), "w"), indent=1, default=float)
    with open(os.path.join(OUT, f"trades{tag}.csv"), "w") as f:
        w = csv.writer(f)
        w.writerow(["utc", "cls", "coin", "venue", "sym", "edited", "era", "onset"] + [f"r{o}" for o in OFFS]
                   + [f"{xn}_{k}" for xn in EXITS for k in ("gross", "fund", "net")])
        for r in rows:
            w.writerow([r["utc"], r["cls"], r["coin"], r["venue"], r["sym"], r["edited"], r["era"], r["onset"]]
                       + [round(1e4 * r["path"][o], 1) for o in OFFS]
                       + [("" if r[xn] is None else round(1e4 * r[xn][k], 1)) for xn in EXITS for k in ("gross", "fund", "net")])
    fo.close()


if __name__ == "__main__":
    main(len(sys.argv) > 1 and sys.argv[1] == "edited")
