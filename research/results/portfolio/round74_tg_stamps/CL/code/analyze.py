"""Stream CL analysis (rules declared in CL/HYPOTHESES_CL.md, 14:47 UTC): path around the Telegram stamp T, "already
moved" share, the 6 graded cells ({BH, CBA, CBL} x exit T + 5 min / T + 60 min, entry T + 5 s) plus RH / OTH
descriptive rows, robustness, random benchmark and the max-over-cells null. Helpers follow round 65 A2/code/analyze.py.
Reads research/data/tg_cl/npz and the local BTC caches only (plus local funding files, fapi fundingRate if missing)."""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net
from pull import btc_local, days_of, load_events

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
NPZ = os.path.join(net.D, "npz")
OUTD = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/CL"
H = 3600000
COST = 0.0020 + 0.0002   # 4 taker fills x 5 bp + 1 bp per BTC fill
EXITS = {"5m": 300000, "60m": 3600000}
GRADED = ["BH", "CBA", "CBL"]
DESC = ["RH", "OTH"]
OFFS = [-600, -300, -60, -10, -5, 0, 1, 2, 5, 10, 30, 60, 300, 900, 3600]
NHOLD = {"BH": 64, "CBA": 15, "CBL": 18}
_C = {}


def npz(sym, day):
    k = (sym, day)
    if k not in _C:
        p = os.path.join(NPZ, f"{sym}_{day}.npz")
        if not os.path.exists(p) and sym == "BTCUSDT":
            p = btc_local(day)
        if p is None or not os.path.exists(p):
            _C[k] = None
        else:
            z = np.load(p); _C[k] = {x: z[x] for x in z.files}
    return _C[k]


def alt_trades(sym, T):
    parts = [npz(sym, d) for d in days_of(T)]
    if any(x is None for x in parts):
        return None
    t = np.concatenate([x["t"] for x in parts]); p = np.concatenate([x["p"] for x in parts])
    o = np.argsort(t, kind="stable")
    return dict(t=t[o], p=p[o])


def btc_at(X):  # 1 s last price of the second containing X
    day = str(np.datetime64(int(X), "ms"))[:10]
    z = npz("BTCUSDT", day)
    if z is None:
        return np.nan
    return float(z["sec_p"][int((X - int(z["d0"])) // 1000)])


def btc_vec(ts):
    out = np.full(len(ts), np.nan)
    days = np.array([str(x)[:10] for x in ts.astype("datetime64[ms]")]) if len(ts) else []
    for day in set(days):
        z = npz("BTCUSDT", day); w = days == day
        if z is not None:
            out[w] = z["sec_p"][((ts[w] - int(z["d0"])) // 1000).astype(int)]
    return out


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
    rs = [(p[bins == k].max() - p[bins == k].min()) / p[bins == k].min() for k in np.unique(bins)]
    return 0.5 * float(np.median(rs))


_FU = {}


def fund(sym, a, b):
    if sym not in _FU:
        p = os.path.join(R, "binance", "funding", sym + ".csv")
        rows = []
        if os.path.exists(p):
            rows = [(float(x["t"]), float(x["rate"])) for x in csv.DictReader(open(p))]
        _FU[sym] = np.array(rows) if rows else np.zeros((0, 2))
    F = _FU[sym]
    if not len(F) or F[:, 0].min() > a or F[:, 0].max() < b - 9 * H:
        assert b + 86400000 < 1735689600000 + 86400000
        r, s = net.opener(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={a - 86400000}&endTime={min(b + 86400000, 1735689599999)}&limit=1000")
        body = r.read() if r else b"[]"
        if r:
            net.log(r.url, s, len(body), "GET"); r.close()
        js = json.loads(body)
        F = np.array([(float(x["fundingTime"]), float(x["fundingRate"])) for x in js]) if js else np.zeros((0, 2))
        _FU[sym] = F
    if not len(F):
        return 0.0
    w = (F[:, 0] > a) & (F[:, 0] <= b)
    return float(F[w, 1].sum())


def clt(x, day):
    x = np.asarray(x, float); n = len(x); m = x.mean(); _, inv = np.unique(day, return_inverse=True)
    g = np.bincount(inv, weights=x - m); G = len(g)
    return m, m / (np.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n), n


def trade(e, A, d, hold_ms, costmul=1.0):
    T = e["T"]
    ae, te = after(A, T + d * 1000)
    if te is None:
        return None
    ax, tx = after(A, T + hold_ms)
    if tx is None or tx - T > hold_ms + 120000:
        return None
    be, bx = btc_at(T + d * 1000), btc_at(T + hold_ms)
    sl = slip(A, te) + slip(A, tx)
    gross = (ax / ae - 1) - (bx / be - 1)
    f = -fund(e["perp"], te, tx) + fund("BTCUSDT", te, tx)
    return dict(gross=gross, fund=f, slip=sl, net=gross + f - costmul * (COST + sl), lag=(te - T) / 1000)


def main():
    E = load_events()
    allr = list(csv.DictReader(open(os.path.join(OUTD, "events_all.csv"))))
    ncoin = {}
    for r in allr:
        ncoin[(r["ch"], r["pid"])] = ncoin.get((r["ch"], r["pid"]), 0) + 1
    out = open(os.path.join(OUTD, "results.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    rows = []; miss = []
    for e in E:
        A = alt_trades(e["perp"], e["T"])
        T = e["T"]
        if A is None or not np.isfinite(btc_at(T - 600000)) or not np.isfinite(btc_at(T + 3600000)):
            miss.append((e["cls"], e["coin"], e["day"])); continue
        ra, rb = at(A, T - 600000), btc_at(T - 600000)
        path = {o: float(np.log(at(A, T + o * 1000) / ra) - np.log(btc_at(T + o * 1000) / rb)) for o in OFFS}
        a0, a1 = np.searchsorted(A["t"], [T - 600000, T + 300000])
        ta, pa = A["t"][a0:a1], A["p"][a0:a1]
        rr = np.log(pa / ra) - np.log(btc_vec(ta) / rb)
        hit = np.where(rr >= 0.02)[0]
        on = (ta[hit[0]] - T) / 1000 if len(hit) else None
        row = dict(e, path=path, onset=on, multi=ncoin.get((e["ch"], str(e["pid"])), 1) > 1)
        for d in (5, 10):
            for xn, hm in EXITS.items():
                row[f"D{d}-{xn}"] = trade(e, A, d, hm)
                row[f"D{d}-{xn}-x15"] = trade(e, A, d, hm, 1.5)
        rows.append(row)
    P("# Stream CL results (bp unless noted). Events graded", len(rows), "missing data", len(miss), miss)

    P("\n## Already moved (ref T - 10 min; onset = first alt trade with alt vs BTC >= +2 %, in [T - 10 min, T + 5 min])")
    P("class era   n  onset found  onset<T  onset<T+5s(moved before entry)  no burst | median r: T-60s  T  T+5s  +60s  +5m  +60m")
    for c in GRADED + DESC:
        for era in ("IS", "VAL"):
            S = [r for r in rows if r["cls"] == c and r["era"] == era]
            if not S:
                continue
            on = [r["onset"] for r in S if r["onset"] is not None]
            med = lambda o: 1e4 * np.median([r["path"][o] for r in S])
            P(f"{c:4s} {era:4s} {len(S):3d}  {len(on):3d}  {sum(x < 0 for x in on):3d}  {sum(x < 5 for x in on):3d} ({100*sum(x < 5 for x in on)/len(S):.0f} % of n)  {len(S)-len(on):3d} | "
              f"{med(-60):6.0f} {med(0):6.0f} {med(5):6.0f} {med(60):6.0f} {med(300):6.0f} {med(3600):6.0f}")
    P("\n## Per event: class era day coin onset(s) r(-60) r(0) r(+5) r(+60) r(+300) r(+3600) net D5-5m D5-60m")
    for r in rows:
        fo = lambda v: "   --  " if v is None else f"{v:7.1f}"
        p = r["path"]; f = lambda k: "  --" if r[k] is None else f"{1e4*r[k]['net']:6.0f}"
        P(f"{r['cls']:4s} {r['era']:4s} {r['day']} {r['coin']:8s} {fo(r['onset'])} "
          + " ".join(f"{1e4*p[o]:6.0f}" for o in (-60, 0, 5, 60, 300, 3600)) + f"  {f('D5-5m')} {f('D5-60m')}")

    P("\n## Cells (entry T + 5 s; net bp per trade; costs 22 bp + alt slippage + funding; t clustered by post day)")
    P("cell       era  n(days)  gross  slip  fund    net      t  median    SR   x1.5  late10s  noEdit  noMulti  years(net)                power")
    cells = {}
    for c in GRADED + DESC:
        for xn in EXITS:
            k = f"{c}-{xn}"
            for era in ("IS", "VAL"):
                S = [r for r in rows if r["cls"] == c and r["era"] == era and r[f"D5-{xn}"] is not None]
                if len(S) < 2:
                    continue
                nt = np.array([r[f"D5-{xn}"]["net"] for r in S]); days = [r["day"] for r in S]
                m, t, n = clt(nt, days); sr = nt.mean() / nt.std(ddof=1)
                x15 = np.mean([r[f"D5-{xn}-x15"]["net"] for r in S])
                lt = [r[f"D10-{xn}"]["net"] for r in S if r[f"D10-{xn}"] is not None]
                ne = [r[f"D5-{xn}"]["net"] for r in S if r["edited"] != "True"]
                nm = [r[f"D5-{xn}"]["net"] for r in S if not r["multi"]]
                yrs = {}
                for r in S:
                    yrs.setdefault(r["year"], []).append(r[f"D5-{xn}"]["net"])
                ys = " ".join(f"{y}:{1e4*np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items()))
                pw = sr * np.sqrt(NHOLD[c]) if (era == "VAL" and c in NHOLD) else np.nan
                q = dict(n=n, days=len(set(days)), net=1e4 * m, t=t, sr=sr, x15=1e4 * x15, late=1e4 * np.mean(lt),
                         noedit=1e4 * np.mean(ne), nomulti=1e4 * np.mean(nm) if nm else np.nan,
                         gross=1e4 * np.mean([r[f"D5-{xn}"]["gross"] for r in S]),
                         slip=1e4 * np.mean([r[f"D5-{xn}"]["slip"] for r in S]),
                         fund=1e4 * np.mean([r[f"D5-{xn}"]["fund"] for r in S]), median=1e4 * np.median(nt),
                         years=ys, yrs_pos=f"{sum(np.mean(v) > 0 for v in yrs.values())}/{len(yrs)}", power=pw)
                cells[(k, era)] = q
                P(f"{k:10s} {era:4s} {n:3d}({q['days']:2d}) {q['gross']:6.0f} {q['slip']:5.0f} {q['fund']:5.0f} {q['net']:6.0f} {t:6.2f} {q['median']:6.0f} {sr:6.2f} {q['x15']:6.0f} {q['late']:7.0f} {q['noedit']:7.0f} {q['nomulti']:7.0f}  {ys:26s} {pw:5.2f}")

    rng = np.random.default_rng(74)
    NS = 1000
    P(f"\n## Random benchmark ({NS} draw sets, same coin / day, gross; percentile of the event gross mean; max-over-6-cells net-t null)")
    G = {}
    for c in GRADED:
        for xn, hm in EXITS.items():
            k = f"{c}-{xn}"
            idx = [j for j, r in enumerate(rows) if r["cls"] == c and r[f"D5-{xn}"] is not None]
            M = np.full((NS, len(idx)), np.nan)
            for jj, j in enumerate(idx):
                r = rows[j]; day = str(np.datetime64(int(r["T"]), "ms"))[:10]
                A = npz(r["perp"], day); B = npz("BTCUSDT", day); d0 = int(A["d0"]); hold = (hm - 5000) // 1000
                z0 = (r["T"] - 900000 - d0) // 1000; z1 = (r["T"] + 3900000 + H - d0) // 1000
                ok = np.array([u for u in range(0, 86400 - hold) if u + hold < z0 or u > z1])
                ok = ok[np.isfinite(A["sec_p"][ok]) & np.isfinite(B["sec_p"][ok]) & np.isfinite(A["sec_p"][ok + hold])]
                u = rng.choice(ok, NS)
                M[:, jj] = (A["sec_p"][u + hold] / A["sec_p"][u] - 1) - (B["sec_p"][u + hold] / B["sec_p"][u] - 1)
            G[k] = (idx, M)
    for era in ("IS", "VAL"):
        maxt = np.full(NS, -np.inf)
        for k, (idx, M) in G.items():
            sel = [jj for jj, j in enumerate(idx) if rows[j]["era"] == era]
            if not sel:
                continue
            xn = k.split("-")[1]
            ev = np.mean([rows[idx[jj]][f"D5-{xn}"]["gross"] for jj in sel])
            pct = 100 * np.mean(M[:, sel].mean(1) < ev)
            cells[(k, era)]["rand_pct"] = pct
            cost = np.array([COST + rows[idx[jj]][f"D5-{xn}"]["slip"] for jj in sel])
            days = [rows[idx[jj]]["day"] for jj in sel]
            ts = np.array([clt(M[s, sel] - cost, days)[1] for s in range(NS)])
            maxt = np.maximum(maxt, ts)
            P(f"  {k:8s} {era:4s} event gross {1e4*ev:7.0f}  random mean {1e4*M[:, sel].mean():6.0f}  beats {pct:5.1f} %")
        P(f"  {era}: 95th pct of max-over-6-cells net t under the random null = {np.percentile(maxt, 95):.2f}")
    json.dump({f"{c}|{e}": v for (c, e), v in cells.items()}, open(os.path.join(OUTD, "cells.json"), "w"), indent=1, default=float)
    with open(os.path.join(OUTD, "trades.csv"), "w") as f:
        w = csv.writer(f)
        w.writerow(["cls", "era", "day", "coin", "perp", "T", "ch", "pid", "edited", "multi", "onset_s"] + [f"r{o}" for o in OFFS]
                   + [f"D{d}-{xn}_{q}" for d in (5, 10) for xn in EXITS for q in ("gross", "slip", "fund", "net")])
        for r in rows:
            w.writerow([r["cls"], r["era"], r["day"], r["coin"], r["perp"], r["T"], r["ch"], r["pid"], r["edited"], r["multi"], r["onset"]]
                       + [round(1e4 * r["path"][o], 1) for o in OFFS]
                       + [("" if r[f"D{d}-{xn}"] is None else round(1e4 * r[f"D{d}-{xn}"][q], 1)) for d in (5, 10) for xn in EXITS for q in ("gross", "slip", "fund", "net")])
    out.close()


if __name__ == "__main__":
    main()
