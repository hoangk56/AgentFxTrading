"""Stream BD: random benchmark for the 24 h cells (random (a) of analyze.py cannot fit a 24 h hold inside two days).
Same coin, random 5m-bar opens within [N - 30 d, N + 30 d] (end capped at 2024-12-31 23:55), excluding
[N - 2 d, N + 2 d]; short at the bar open, cover at the open 24 h later, taker fees both sides, no funding (the event
side is compared ex-funding, as in analyze.py). Bars: data.binance.vision futures/um monthly 5m klines (bu), Bybit
v5 public kline (by). Also post-hoc: the 24 h exit with entry at N + 5 min / N + 60 min from the same bars.
Run: python -I random24.py"""
import csv, io, json, os, sys, zipfile, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import net
from analyze import clt, FEE

OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/BD"
KD = os.path.join(net.D, "k5m"); os.makedirs(KD, exist_ok=True)
END = 1735689600
DAY = 86400


def months(a, b):
    d = dt.date.fromtimestamp(a); out = []
    d = dt.date(d.year, d.month, 1)
    while d <= dt.date.fromtimestamp(min(b, END - 1)):
        out.append(f"{d.year}-{d.month:02d}"); d = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return out


def bars(v, sym, a, b):
    """-> dict open_time_s -> open price, for [a, b)"""
    fn = os.path.join(KD, f"{v}_{sym}_{a}.json")
    if os.path.exists(fn):
        return {int(k): x for k, x in json.load(open(fn)).items()}
    o = {}
    if v == "bu":
        for m in months(a, b):
            if m > "2024-12":
                continue
            u = f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/5m/{sym}-5m-{m}.zip"
            body, s = net.get(u)
            if not body:
                continue
            with zipfile.ZipFile(io.BytesIO(body)) as z:
                txt = z.read(z.namelist()[0]).decode()
            for ln in txt.splitlines():
                f = ln.split(",")
                if not f[0].isdigit():
                    continue
                t = int(f[0]) // 1000
                if a <= t < b:
                    o[t] = float(f[1])
    else:
        st = a
        while st < min(b, END):
            en = min(st + 1000 * 300, b, END) - 1
            body, s = net.get(f"https://api.bybit.com/v5/market/kline?category=linear&symbol={sym}&interval=5&start={st * 1000}&end={en * 1000}&limit=1000")
            L = ((json.loads(body) if body else {}).get("result") or {}).get("list") or []
            for x in L:
                t = int(x[0]) // 1000
                if a <= t < b:
                    o[t] = float(x[1])
            st = en + 1
    json.dump(o, open(fn, "w"))
    return o


def main():
    T = list(csv.DictReader(open(os.path.join(OUT, "trades.csv"))))
    rng = np.random.default_rng(7424)
    NS = 2000
    fo = open(os.path.join(OUT, "random24.txt"), "w")
    P = lambda *a: (print(*a), print(*a, file=fo))
    P("# Random benchmark for 24 h cells (5m bars, same coin, +-30 d excl. +-2 d) and post-hoc later entries; bp")
    for cls in ("S", "MT"):
        rows = [r for r in T if r["cls"] == cls and r["era"] == "VAL" and r["24h_net"] != ""]
        G = np.full((NS, len(rows)), np.nan); ev = []; late5, late60 = [], []
        for j, r in enumerate(rows):
            N = int(dt.datetime.strptime(r["utc"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp())
            a, b = N - 30 * DAY, min(N + 30 * DAY, END)
            B = bars(r["venue"], r["sym"], a, b)
            ev.append(float(r["24h_net"]) - float(r["24h_fund"] or 0))
            ts = np.array(sorted(B)); px = np.array([B[t] for t in ts])
            ok = [i for i, t in enumerate(ts) if abs(t - N) > 2 * DAY and (t + DAY) in B]
            fee = 2 * FEE[r["venue"]]
            if len(ok) >= 30:
                u = rng.choice(ok, NS)
                G[:, j] = [1e4 * (1 - B[ts[i] + DAY] / px[i] - fee) for i in u]
            for lag, acc in ((300, late5), (3600, late60)):
                t0 = N + lag; t0 = t0 - t0 % 300 + 300  # next 5m open after N + lag
                if t0 in B and (t0 + DAY) in B:
                    acc.append(1e4 * (1 - B[t0 + DAY] / B[t0] - fee))
            P(f"  {cls} {r['utc']} {r['coin']:6s} {r['venue']} bars {len(B):5d} random ok {len(ok):5d} event ex-fund {ev[-1]:7.0f}")
        ev = np.array(ev); okc = np.isfinite(G).all(0)
        if okc.sum():
            pct = 100 * np.mean(G[:, okc].mean(1) < ev[okc].mean())
            days = [r["utc"][:10] for r, o in zip(rows, okc) if o]
            tr = np.array([clt(G[s, okc], days)[1] for s in range(NS)])
            m, t, n = clt(ev[okc], days)
            P(f"{cls}-24h VAL: coins with random {okc.sum()}/{len(rows)}; event mean ex-funding {ev[okc].mean():.0f} (t {t:.2f}); random mean {np.nanmean(G[:, okc]):.0f}; "
              f"event beats {pct:.1f} % of random sets; 95th pct of random t {np.percentile(tr, 95):.2f}, event t beats {100*np.mean(tr < t):.1f} %")
        P(f"{cls}-24h post-hoc entry N + 5 min (next 5m open): mean {np.mean(late5):.0f} n {len(late5)}; N + 60 min: mean {np.mean(late60):.0f} n {len(late60)} (fees only, no funding)")
    fo.close()


if __name__ == "__main__":
    main()
