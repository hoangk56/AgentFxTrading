"""Stream BD, registered new-era test of cell S-24h (BD/PREREG_BD_S24h.md). One code path, two windows:

  --dry-val [--fresh DIR]   VAL 2022-01-01..2024-12-31: must reproduce STREAM_BD's S-24h VAL numbers exactly
                            (cells.json, cells_edited.json, random24.txt). --fresh DIR rebuilds every price / bar / BTC
                            file from the network into the empty folder DIR (end-to-end check of the fetch path);
                            without it the VAL caches in research/data/binance_delist_tg are read.
                            Writes BD/dryval_results.txt. Never touches 2025-26 posts or prices.
  --open-hold-once          HOLD 2025-01-01..2026-10-29 (post time < 2026-10-30 00:00 UTC; prices up to 2026-10-30
                            23:59:59 so the 24 h exit of the last day fits). Refuses to run if BD/HOLD_OPENED exists;
                            creates it first. Writes BD/hold_results.txt and BD/trades_hold.csv.

Rule (unchanged from the VAL run): class-S title of @binance_announcements (events.classify, edited posts dropped),
coins by events.coins, stablecoins excluded; instrument Binance USDT-M <C>USDT, else 1000<C>USDT, else Bybit linear
<C>USDT (pull.exists on the notice day); SHORT at the worst price (lo) of the 1 s bucket of the first trade >= N + 5 s,
cover at the worst price (hi) of the first trade >= N + 24 h (analyze.fill / analyze.trade); taker 5 bp (Binance) /
5.5 bp (Bybit) a side; real funding (analyze.funding); a coin with no trade in the 60 s before N's reference second
(last(N - 60) NaN) is dropped as in analyze.main.

What is copied here instead of imported (each only to move a hard-coded 2024-12-31 limit to the window's end):
analyze.arr -> arr_w, analyze.btc -> btc_w, random24.bars -> bars_w (+ daily 5m kline files when a monthly file is
not published yet; months taken in UTC, random24 used local dates, which gives the same months for these events),
net.guard -> guard_w, instruments.main -> pick (same order). The dry-val run proves the copies give the same numbers.
HOLD days whose files are not published yet (BTCUSDT reference file missing on data.binance.vision or
public.bybit.com for the notice day or the next day) are skipped and listed, never filled from elsewhere.
Run: research/.venv/bin/python -I hold_s24h.py --dry-val | --open-hold-once"""
import argparse, csv, io, json, os, sys, zipfile, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import net, pull, events, analyze
from analyze import fill, last, clt, FEE

OUT = os.path.dirname(HERE)
FLAG = os.path.join(OUT, "HOLD_OPENED")
DAY = 86400
D_ENTRY, D_LATE, HOLD_S = analyze.D_ENTRY, analyze.D_LATE, analyze.EXITS["24h"]

WIN = {
    "VAL": dict(ev_start=1640995200, ev_end=1735689600, last_day="2024-12-31", price_end=1735689600),
    "HOLD": dict(ev_start=1735689600, ev_end=1793318400, last_day="2026-10-30", price_end=1793404800),
}
# STREAM_BD's VAL numbers (cells.json / cells_edited.json / random24.txt), the dry-val target
EXPECT = dict(
    primary=json.load(open(os.path.join(OUT, "cells.json")))["S|24h|VAL"],
    edited=json.load(open(os.path.join(OUT, "cells_edited.json")))["S|24h|VAL"],
    random="S-24h VAL: coins with random 14/14; event mean ex-funding 1516 (t 3.99); random mean -23; event beats 100.0 % "
           "of random sets; 95th pct of random t 1.84, event t beats 99.8 %",
    late="S-24h post-hoc entry N + 5 min (next 5m open): mean 1277 n 14; N + 60 min: mean 738 n 14 (fees only, no funding)",
)
W = None; CACHE = None  # set in main


def utc(T):
    return dt.datetime.fromtimestamp(T, dt.timezone.utc)


def guard_w(url):
    import re
    for d in re.findall(r"(20\d\d-\d\d-\d\d)", url):
        assert d <= W["last_day"], url
    for m in re.findall(r"-(20\d\d-\d\d)\.zip", url):
        assert m <= W["last_day"][:7], url
    for v in re.findall(r"(?:endTime|end|startTime|start)=(\d{13})", url):
        assert int(v) < W["price_end"] * 1000, url


_A = {}


def arr_w(v, sym, d0):
    """analyze.arr with the window's last price day instead of 2024-12-31."""
    k = (v, sym, d0)
    if k in _A:
        return _A[k]
    d1 = str(dt.date.fromisoformat(d0) + dt.timedelta(days=1))
    out = {}
    for d in (d0, d1):
        p = pull.path(v, sym, d)
        if d <= W["last_day"] and os.path.exists(p):
            z = np.load(p); x = {f: z[f] for f in ("last", "lo", "hi", "n")}
        else:
            x = dict(last=np.full(86400, np.nan), lo=np.full(86400, np.nan), hi=np.full(86400, np.nan), n=np.zeros(86400, np.int32))
        for f in x:
            out.setdefault(f, []).append(x[f])
    S = {f: np.concatenate(out[f]) for f in out}
    S["base"] = int(np.datetime64(d0, "s").astype(np.int64))
    _A[k] = S
    return S


_BTC = {}


def btc_w(T):
    """analyze.btc (BTCUSDT spot 1m close of the minute containing T) with the window's end."""
    d = utc(T).strftime("%Y-%m-%d")
    if d > W["last_day"]:
        return np.nan
    if d not in _BTC:
        fn = os.path.join(CACHE["btc"], d + ".json"); os.makedirs(os.path.dirname(fn), exist_ok=True)
        if not os.path.exists(fn):
            s0 = int(np.datetime64(d, "s").astype(np.int64)) * 1000; rows = []
            end = min(s0 + 86400000 - 1, W["price_end"] * 1000 - 1)
            for st in (s0, s0 + 1000 * 60000):
                body, _ = net.get(f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={st}&endTime={end}&limit=1000")
                rows += json.loads(body or b"[]")
            json.dump({str(int(r[0]) // 1000): float(r[4]) for r in rows}, open(fn, "w"))
        _BTC[d] = {int(k): v for k, v in json.load(open(fn)).items()}
    return _BTC[d].get(T - T % 60, np.nan)


def months_utc(a, b):
    d = utc(a).date().replace(day=1); out = []
    while d <= utc(min(b, W["price_end"]) - 1).date():
        out.append(f"{d.year}-{d.month:02d}"); d = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return out


def _kl_rows(body, a, b, o):
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        txt = z.read(z.namelist()[0]).decode()
    for ln in txt.splitlines():
        f = ln.split(",")
        if not f[0].isdigit():
            continue
        t = int(f[0]) // 1000
        if t > 1e11:  # microsecond stamps in newer files
            t //= 1000
        if a <= t < b:
            o[t] = float(f[1])


def bars_w(v, sym, a, b):
    """random24.bars (5m bar opens in [a, b)) with the window's end; daily files when a month is not published."""
    fn = os.path.join(CACHE["k5m"], f"{v}_{sym}_{a}.json")
    if os.path.exists(fn):
        return {int(k): x for k, x in json.load(open(fn)).items()}
    o = {}; END = W["price_end"]
    if v == "bu":
        for m in months_utc(a, b):
            body, s = net.get(f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/5m/{sym}-5m-{m}.zip")
            if body:
                _kl_rows(body, a, b, o); continue
            d = dt.date.fromisoformat(m + "-01")
            while d.strftime("%Y-%m") == m:
                ds = str(d); d0 = int(np.datetime64(ds, "s").astype(np.int64))
                if d0 + DAY > a and d0 < min(b, END) and ds <= W["last_day"]:
                    body, s = net.get(f"https://data.binance.vision/data/futures/um/daily/klines/{sym}/5m/{sym}-5m-{ds}.zip")
                    if body:
                        _kl_rows(body, a, b, o)
                d += dt.timedelta(days=1)
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


def load_events():
    """class-S posts of @binance_announcements inside the window (cut right after parsing), all coins, edited flag."""
    posts = events.load("binance_announcements")
    rows = []; tmax = 0
    for pid in sorted(posts):
        p = posts[pid]
        tmax = max(tmax, p["time"])
        if not (W["ev_start"] <= p["time"] < W["ev_end"]):
            continue
        t = events.title(p["text"])
        if events.classify(t) != "S":
            continue
        N = int(p["time"])
        rows.append(dict(id=pid, time=N, utc=utc(N).strftime("%Y-%m-%d %H:%M:%S"), edited=str(int(p["edited"])),
                         coins=events.coins(t, p["text"])))
    return rows, tmax


def pick(c, N, d0):
    """instruments.main's order for a class-S coin."""
    if N >= 1567296000:
        for s in (f"{c}USDT", f"1000{c}USDT"):
            if pull.exists("bu", s, d0):
                return ("bu", s)
    if N >= 1577836800 and pull.exists("by", f"{c}USDT", d0):
        return ("by", f"{c}USDT")
    return None


def published(d):
    return pull.exists("bu", "BTCUSDT", d) and pull.exists("by", "BTCUSDT", d)


def build_rows(ev, era, P):
    R = []; skipped = []
    pub = {}
    for e in ev:
        N = e["time"]; d0 = utc(N).strftime("%Y-%m-%d"); d1 = str(dt.date.fromisoformat(d0) + dt.timedelta(days=1))
        if era == "HOLD":
            for d in (d0, d1):
                if d not in pub:
                    pub[d] = published(d)
            if not (pub[d0] and pub[d1]):
                skipped.append(e); continue
        for c in e["coins"]:
            inst = pick(c, N, d0)
            R.append(dict(id=e["id"], time=str(N), utc=e["utc"], edited=e["edited"], cls="S", coin=c,
                          venue=inst[0] if inst else "", sym=inst[1] if inst else "", d0=d0, d1=d1))
    jobs = set()
    for r in R:
        if r["venue"]:
            for d in (r["d0"], r["d1"]):
                if d <= W["last_day"]:
                    jobs.add((r["venue"], r["sym"], d))
    for k, j in enumerate(sorted(jobs, key=lambda x: (x[2], x[0], x[1]))):
        ok = pull.build(*j)
        print(f"  pull {k+1}/{len(jobs)} {j[0]} {j[1]} {'ok' if ok else 'missing'}", flush=True)
    return R, skipped


def grade(R, keep_edited):
    rows = []; drop = dict(no_inst=0, no_ref=0, no_exit=0)
    for r in R:
        if not keep_edited and r["edited"] != "0":
            continue
        if not r["venue"]:
            drop["no_inst"] += 1; continue
        S = arr_w(r["venue"], r["sym"], r["d0"]); N = int(r["time"])
        if not np.isfinite(last(S, N - 60)):
            drop["no_ref"] += 1; continue
        row = dict(r, year=r["utc"][:4], day=r["utc"][:10])
        row["main"] = analyze.trade(row, S, D_ENTRY, HOLD_S)
        row["x15"] = analyze.trade(row, S, D_ENTRY, HOLD_S, 1.5)
        row["late"] = analyze.trade(row, S, D_LATE, HOLD_S)
        row["hedge"] = analyze.trade(row, S, D_ENTRY, HOLD_S, hedge=True)
        if row["main"] is None:
            drop["no_exit"] += 1
        rows.append(row)
    S_ = [r for r in rows if r["main"] is not None]
    q = dict(n=len(S_), drop=drop)
    if not S_:
        return q, rows, S_
    net_ = np.array([r["main"]["net"] for r in S_]); days = [r["day"] for r in S_]
    m, t, n = clt(net_, days)
    g = lambda k: 1e4 * np.mean([r[k]["net"] for r in S_ if r[k] is not None]) if any(r[k] is not None for r in S_) else np.nan
    yrs = {}
    for r in S_:
        yrs.setdefault(r["year"], []).append(r["main"]["net"])
    lodo = []
    for d in sorted(set(days)):
        k = [i for i, x in enumerate(days) if x != d]
        if len(k) >= 2:
            lodo.append(clt(net_[k], [days[i] for i in k])[1])
    q.update(days=len(set(days)), gross=1e4 * np.mean([r["main"]["gross"] for r in S_]),
             fund=1e4 * np.mean([r["main"]["fund"] for r in S_]), net=1e4 * m, t=t, med=1e4 * np.median(net_),
             sr=net_.mean() / net_.std(ddof=1) if n > 1 else np.nan, win=float(np.mean(net_ > 0)),
             x15=g("x15"), late=g("late"), hedge=g("hedge"),
             years=" ".join(f"{y}:{1e4*np.mean(v):+.0f}({len(v)})" for y, v in sorted(yrs.items())),
             yrs_pos=f"{sum(np.mean(v) > 0 for v in yrs.values())}/{len(yrs)}",
             lodo=(min(lodo), max(lodo)) if lodo else (np.nan, np.nan),
             venues=f"bu {sum(r['venue'] == 'bu' for r in S_)}, by {sum(r['venue'] == 'by' for r in S_)}")
    return q, rows, S_


def random24(S_, P):
    """random24.main for class S: same coin, random 5m opens in N +- 30 d excluding +- 2 d, 2,000 sets, seed 7424."""
    rng = np.random.default_rng(7424); NS = 2000; END = W["price_end"]
    G = np.full((NS, len(S_)), np.nan); ev = []; late5, late60 = [], []
    for j, r in enumerate(S_):
        N = int(r["time"]); a, b = N - 30 * DAY, min(N + 30 * DAY, END)
        B = bars_w(r["venue"], r["sym"], a, b)
        ev.append(round(1e4 * r["main"]["net"], 1) - round(1e4 * r["main"]["fund"], 1))  # random24 read trades.csv (0.1 bp)
        ts = np.array(sorted(B)); px = np.array([B[t] for t in ts])
        ok = [i for i, t in enumerate(ts) if abs(t - N) > 2 * DAY and (t + DAY) in B]
        fee = 2 * FEE[r["venue"]]
        if len(ok) >= 30:
            u = rng.choice(ok, NS)
            G[:, j] = [1e4 * (1 - B[ts[i] + DAY] / px[i] - fee) for i in u]
        for lag, acc in ((300, late5), (3600, late60)):
            t0 = N + lag; t0 = t0 - t0 % 300 + 300
            if t0 in B and (t0 + DAY) in B:
                acc.append(1e4 * (1 - B[t0 + DAY] / B[t0] - fee))
    ev = np.array(ev); okc = np.isfinite(G).all(0) if len(S_) else np.array([], bool)
    lines = []
    if okc.sum():
        pct = 100 * np.mean(G[:, okc].mean(1) < ev[okc].mean())
        days = [r["utc"][:10] for r, o in zip(S_, okc) if o]
        tr = np.array([clt(G[s, okc], days)[1] for s in range(NS)])
        m, t, n = clt(ev[okc], days)
        lines.append(f"S-24h {ERA}: coins with random {okc.sum()}/{len(S_)}; event mean ex-funding {ev[okc].mean():.0f} (t {t:.2f}); random mean {np.nanmean(G[:, okc]):.0f}; "
                     f"event beats {pct:.1f} % of random sets; 95th pct of random t {np.percentile(tr, 95):.2f}, event t beats {100*np.mean(tr < t):.1f} %")
    else:
        lines.append(f"S-24h {ERA}: no coin with >= 30 random bars")
    lines.append(f"S-24h post-hoc entry N + 5 min (next 5m open): mean {np.mean(late5) if late5 else np.nan:.0f} n {len(late5)}; N + 60 min: mean {np.mean(late60) if late60 else np.nan:.0f} n {len(late60)} (fees only, no funding)")
    for x in lines:
        P(x)
    return lines


def fmt(q):
    if not q.get("n"):
        return "n 0"
    return (f"n {q['n']} ({q['days']} days; {q['venues']})  gross {q['gross']:.0f}  funding {q['fund']:.0f}  net {q['net']:.0f}  t {q['t']:.2f}  "
            f"median {q['med']:.0f}  SR/trade {q['sr']:.2f}  win {100*q['win']:.0f} %  x1.5 {q['x15']:.0f}  +10 s {q['late']:.0f}  "
            f"BTC-hedged {q['hedge']:.0f}  years {q['years']} ({q['yrs_pos']} positive)  leave-one-day-out t {q['lodo'][0]:.2f}..{q['lodo'][1]:.2f}")


def main():
    global W, CACHE, ERA
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-val", action="store_true")
    g.add_argument("--open-hold-once", action="store_true")
    ap.add_argument("--fresh", metavar="DIR", help="dry-val only: rebuild every data file into this empty folder")
    a = ap.parse_args()
    if a.open_hold_once:
        if a.fresh:
            raise SystemExit("--fresh is for --dry-val only")
        if os.path.exists(FLAG):
            raise SystemExit(f"refused: {FLAG} exists, HOLD was already opened:\n" + open(FLAG).read())
        with open(FLAG, "x") as f:
            f.write(f"HOLD opened {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC by {' '.join(sys.argv)} (pid {os.getpid()})\n")
        ERA = "HOLD"; W = WIN["HOLD"]
        base = os.path.join(net.D, "hold")
        net.guard = guard_w
        net.END_MS = W["price_end"] * 1000  # analyze.funding caps its end at net.END_MS - 1
        out_txt, out_csv = os.path.join(OUT, "hold_results.txt"), os.path.join(OUT, "trades_hold.csv")
    else:
        ERA = "VAL"; W = WIN["VAL"]
        base = os.path.abspath(a.fresh) if a.fresh else None
        if base:
            assert not os.path.exists(base) or not os.listdir(base), "--fresh DIR must be empty"
        orig = net.guard
        net.guard = lambda u: (orig(u), guard_w(u))  # both the VAL run's 2024 guard and the window guard
        out_txt, out_csv = os.path.join(OUT, "dryval_results.txt"), None
    CACHE = dict(sec=os.path.join(base, "sec") if base else pull.SEC, k5m=os.path.join(base, "k5m") if base else os.path.join(net.D, "k5m"),
                 btc=os.path.join(base, "btc1m") if base else os.path.join(net.D, "btc1m"))
    for d in CACHE.values():
        os.makedirs(d, exist_ok=True)
    pull.SEC = CACHE["sec"]  # pull.path / exists / build read this global
    analyze.btc = btc_w      # analyze.trade's hedge leg

    fo = open(out_txt, "w")
    P = lambda *x: (print(*x, flush=True), print(*x, file=fo, flush=True))
    P(f"# BD S-24h {ERA} run {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC; events {utc(W['ev_start']):%Y-%m-%d}.."
      f"{utc(W['ev_end'] - 1):%Y-%m-%d}, prices <= {W['last_day']}; caches {CACHE['sec']}; bp per trade")
    ev, tmax = load_events()
    if ERA == "HOLD":
        P(f"Telegram pages reach post time {utc(tmax):%Y-%m-%d %H:%M} UTC (must be >= window end {utc(W['ev_end']):%Y-%m-%d})")
    P(f"class-S posts in window: {len(ev)} ({sum(e['edited'] == '0' for e in ev)} not edited); coins {sum(len(e['coins']) for e in ev)}")
    R, skipped = build_rows(ev, ERA, P)
    for e in skipped:
        P(f"SKIPPED (files not published yet): {e['utc']} {' '.join(e['coins'])}")
    q, rows, S_ = grade(R, keep_edited=False)
    qe, rows_e, S_e = grade(R, keep_edited=True)
    P(f"\n## S-24h {ERA}, edited posts dropped (primary)")
    P(f"coins: with instrument and graded {q['n']}; no Binance / Bybit perp {q['drop']['no_inst']}; no price in N - 60 s {q['drop']['no_ref']}; "
      f"entry but no 24 h exit {q['drop']['no_exit']}")
    P(fmt(q))
    P(f"\n## Info: edited posts kept\n{fmt(qe)}")
    P(f"\n## Random benchmark (random24.py method) and post-hoc later entries, primary trades")
    rl = random24(S_, P)
    P("\n## Per trade (primary): utc coin venue gross fund net x1.5 +10s hedged")
    for r in S_:
        f_ = lambda k: "" if r[k] is None else f"{1e4 * r[k]['net']:.0f}"
        P(f"  {r['utc']} {r['coin']:7s} {r['venue']} {1e4*r['main']['gross']:7.0f} {1e4*r['main']['fund']:6.0f} {1e4*r['main']['net']:7.0f} "
          f"{f_('x15'):>7s} {f_('late'):>7s} {f_('hedge'):>7s}")

    if ERA == "VAL":
        P("\n## Dry-val check against STREAM_BD (cells.json, cells_edited.json, random24.txt)")
        bad = 0
        for nm, qq in (("primary", q), ("edited", qe)):
            ex = EXPECT[nm]
            for k in ("n", "days", "gross", "fund", "net", "t", "med", "sr", "win", "x15", "late", "hedge", "years", "yrs_pos"):
                a_, b_ = qq[k], ex[k]
                ok = a_ == b_ if isinstance(b_, str) else abs(float(a_) - float(b_)) <= 1e-9 * max(1.0, abs(float(b_)))
                bad += not ok
                P(f"  {nm:7s} {k:7s} {'MATCH' if ok else 'MISMATCH'}  got {a_}  STREAM {b_}")
        for got, ex in ((rl[0], EXPECT["random"]), (rl[1], EXPECT["late"])):
            ok = got == ex; bad += not ok
            P(f"  random  {'MATCH' if ok else 'MISMATCH'}  got: {got}")
        P(f"DRY-VAL {'REPRODUCED EXACTLY' if bad == 0 else f'FAILED ({bad} mismatches)'}")
    else:
        P("\n## Registered pass bar (PREREG_BD_S24h.md)")
        if q["n"] < 8:
            P(f"HOLD n {q['n']} < 8 trades: NOT GRADABLE")
        else:
            c = dict(net=q["net"] > 0, t=q["t"] >= 2.5, x15=q["x15"] > 0, late=q["late"] > 0)
            P(f"net > 0: {c['net']} ({q['net']:.0f}); t >= 2.5: {c['t']} ({q['t']:.2f}); x1.5 > 0: {c['x15']} ({q['x15']:.0f}); "
              f"+10 s > 0: {c['late']} ({q['late']:.0f})")
            P(f"HOLD S-24h: {'LIVE (all four conditions met)' if all(c.values()) else 'FAIL'}")
        with open(out_csv, "w") as f:
            w = csv.writer(f)
            w.writerow(["utc", "id", "coin", "edited", "venue", "sym", "status", "gross", "fund", "net", "net_x15", "net_late10s", "net_hedged"])
            graded = {(r["id"], r["coin"]): r for r in rows_e}
            for r in R:
                x = graded.get((r["id"], r["coin"]))
                st = "no_instrument" if not r["venue"] else ("no_ref_price" if x is None else ("no_exit" if x["main"] is None else "graded"))
                v = lambda k: "" if x is None or x[k] is None else round(1e4 * x[k]["net"], 1)
                w.writerow([r["utc"], r["id"], r["coin"], r["edited"], r["venue"], r["sym"], st,
                            "" if x is None or x["main"] is None else round(1e4 * x["main"]["gross"], 1),
                            "" if x is None or x["main"] is None else round(1e4 * x["main"]["fund"], 1),
                            v("main"), v("x15"), v("late"), v("hedge")])
            for e in skipped:
                for c in e["coins"]:
                    w.writerow([e["utc"], e["id"], c, e["edited"], "", "", "skipped_unpublished"] + [""] * 6)
    fo.close()


if __name__ == "__main__":
    main()
