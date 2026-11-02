"""Stream M runner (declared in ../HYPOTHESES_M.md). K2's rule frozen via k2rule.trade (copied, log folder changed).
Modes: python -I run.py trades | random | report
  trades : price every M event, K2's 40 events and the 4 survivorship extras (H72 main + H24, x1.5, +5 min, L + 2 h),
           pre-entry pump and the name-collision guard; writes research/data/upbit_nonkrw/trades.json
  random : gross on local 1h closes vs (a) other perps same hour, (b) same coin 30-180 d later (500 draws)
  report : tables (era, year, sensitivity, survivorship) -> stdout"""
import csv, json, os, sys, time, calendar
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k2rule
import events as EV

R = k2rule.R
D = k2rule.D
H, M, DAY = k2rule.H, k2rule.M, k2rule.DAY
CUT = 1735689600000
IS_END = 1640995200000
HERE = os.path.dirname(os.path.abspath(__file__))
K2EV = os.path.join(HERE, "..", "..", "..", "round64_parallel", "K", "k2_events.csv")

# Cache identical fapi URLs (k2rule.get is unchanged; repeated px calls for the same bar re-use the response).
_CF = os.path.join(D, "fapi_cache.json")
_C = json.load(open(_CF)) if os.path.exists(_CF) else {}
_get0 = k2rule.get


def _cached(url):
    if url not in _C:
        js = _get0(url)
        if js is None:
            return None
        _C[url] = js
    return _C[url]


k2rule.get = _cached


def iso(t):
    return time.strftime('%Y-%m-%d %H:%M', time.gmtime(t / 1000))


def ms(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%S")) * 1000


def load_events():
    m = [dict(set="M", coin=r["coin"], sym=r["sym"], L=int(r["L"]), notice=int(r["notice"]), src=r["src"], market=r["market"],
              nid=int(r["nid"])) for r in csv.DictReader(open(os.path.join(HERE, "..", "events_M.csv")))]
    k = [dict(set="K2", coin=r["coin"], sym=r["sym"], L=int(r["L"]), src="K2 list") for r in csv.DictReader(open(K2EV))
         if int(r["L"]) < CUT - 4 * DAY]
    x = [dict(set="K2X", coin=r["coin"], sym=r["sym"], L=ms(r["L"]), src=r["src"]) for r in EV.KRW_EXTRA]
    return [e for e in m + k + x if e["L"] < EV.TEND]


VARIANTS = {"H72": dict(hold=72 * H), "H24": dict(hold=24 * H), "H72_c15": dict(hold=72 * H, cost=k2rule.COST * 1.5),
            "H72_p5": dict(hold=72 * H, off=H + 5 * M), "H72_L2h": dict(hold=72 * H, off=2 * H)}


def upbit_close(e, te):
    """Upbit close of the new market's 60m bar containing te (for the guard); None when the market is delisted."""
    import fetch
    mk = e.get("market", "KRW")
    cc = EV.RENAMED.get((e["coin"], e.get("nid")), e["coin"])
    if e["set"] != "M":
        return None, mk
    js = fetch.get(f"https://api.upbit.com/v1/candles/minutes/60?market={mk}-{cc}&to={EV.iso(te // H * H + H)}&count=1")
    return (float(js[0]["trade_price"]) if js else None), mk


def trades():
    out = []
    for e in load_events():
        r = dict(e)
        for name, kw in VARIANTS.items():
            t = k2rule.trade(e["sym"], e["L"], **kw)
            r[name] = None if t is None else dict(te=t[0], price=t[1], fund=t[2], net=t[3])
        te = e["L"] + H
        a0, a1 = k2rule.px(e["sym"], e["L"] - 24 * H), k2rule.px(e["sym"], te)
        b0, b1 = k2rule.px("BTCUSDT", e["L"] - 24 * H), k2rule.px("BTCUSDT", te)
        r["pump"] = float((a1 / a0 - 1) - (b1 / b0 - 1)) if np.all(np.isfinite([a0, a1, b0, b1])) else None
        if e["set"] == "M":
            n0 = e["notice"] // M * M - 24 * H
            c0, d0 = k2rule.px(e["sym"], n0), k2rule.px("BTCUSDT", n0)
            r["pump_notice"] = float((a1 / c0 - 1) - (b1 / d0 - 1)) if np.all(np.isfinite([c0, d0, a1, b1])) else None
            # pump between notice and entry only
            c1, d1 = k2rule.px(e["sym"], e["notice"] // M * M + M), k2rule.px("BTCUSDT", e["notice"] // M * M + M)
            r["pump_post_notice"] = float((a1 / c1 - 1) - (b1 / d1 - 1)) if np.all(np.isfinite([c1, d1, a1, b1])) else None
            up, mk = upbit_close(e, te)
            sc = 1000.0 if e["sym"].startswith("1000") else 1.0
            if up is not None and np.isfinite(a1):
                usd = up * b1 if mk == "BTC" else up
                r["guard_ratio"] = float(usd / (a1 / sc))
            else:
                r["guard_ratio"] = None
        out.append(r)
        h = r["H72"]
        print(f"{e['set']:3s} {e['coin']:8s} L {iso(e['L'])} H72 {'-' if h is None else round(h['net'] * 1e4)} "
              f"pump {'-' if r['pump'] is None else round(r['pump'] * 1e4)} guard {r.get('guard_ratio')}", flush=True)
        json.dump(_C, open(_CF, "w"))
    json.dump(out, open(os.path.join(D, "trades.json"), "w"), indent=0)


# ---------------- random benchmark (gross on local 1h closes, as K2's random_k2) ----------------
def h1(sym):
    best = None
    cands = [os.path.join(R, "binance_1h_full", "1h", sym + ".csv"), os.path.join(R, "binance_basis", "perp_1h", sym + ".csv")]
    import glob
    cands += glob.glob(os.path.join(R, "binance", "perp_1h", sym + "_*.csv"))
    for p in cands:
        if not os.path.exists(p):
            continue
        with open(p) as f:
            hd = f.readline().strip().split(",")
            ic = hd.index("c")
            a = np.array([(float(x[0]), float(x[ic])) for x in (l.split(",") for l in f) if x and x[0]], dtype=float)
        if len(a):
            a = a[a[:, 0] < CUT]
        if len(a):  # merge the local windows; earlier files keep their value on overlap
            best = a if best is None else np.vstack([best, a[~np.isin(a[:, 0], best[:, 0])]])
    return None if best is None else best[np.argsort(best[:, 0])]


def panel():
    p = os.path.join(D, "perp1h_close.npz")
    if os.path.exists(p):
        z = np.load(p, allow_pickle=True)
        return z["d"].item()
    import glob
    syms = set()
    for d in ("binance_1h_full/1h", "binance_basis/perp_1h"):
        syms |= {os.path.basename(x)[:-4] for x in glob.glob(os.path.join(R, d, "*USDT.csv"))}
    syms |= {os.path.basename(x).split("_")[0] for x in glob.glob(os.path.join(R, "binance", "perp_1h", "*USDT_*.csv"))}
    out = {}
    for s in sorted(syms):
        a = h1(s)
        if a is not None and len(a) > 24 * 5:
            out[s] = a
    np.savez(p, d=np.array(out, dtype=object))
    return out


def supplement(tr):
    """fapi 1h closes for each event symbol from L - 2 d to L + 185 d (end <= 2024-12-31 23:59:59), filling gaps in the
    local windows (via k2rule.get: logged, cached). Returns {sym: {t: close}}."""
    p = os.path.join(D, "event_1h.json")
    out = {k: {int(t): c for t, c in v.items()} for k, v in json.load(open(p)).items()} if os.path.exists(p) else {}
    for e in tr:
        s = e["sym"]
        a, b = e["L"] - 2 * DAY, min(e["L"] + 185 * DAY, CUT - 1)
        if s in out and any(a <= t <= a + DAY for t in out[s]) and any(b - 3 * DAY <= t <= b for t in out[s]):
            continue
        d = out.setdefault(s, {})
        t = a
        while t < b:
            js = k2rule.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&startTime={t}&endTime={b}&limit=1500") or []
            for x in js:
                if int(x[0]) < CUT:
                    d[int(x[0])] = float(x[4])
            if len(js) < 1500:
                break
            t = int(js[-1][0]) + H
    json.dump({k: {str(t): c for t, c in v.items()} for k, v in out.items()}, open(p, "w"))
    return out


def random_bench(draws=500, seed=11):
    rng = np.random.default_rng(seed)
    P = panel()
    idx = {s: {int(t): c for t, c in a} for s, a in P.items()}
    first = {s: int(a[0, 0]) for s, a in P.items()}
    tr0 = json.load(open(os.path.join(D, "trades.json")))
    for sym, d in supplement(tr0).items():
        A = idx.setdefault(sym, {})
        for t, c in d.items():
            A.setdefault(t, c)
        first.setdefault(sym, min(d) if d else CUT)
    hb = idx["BTCUSDT"]
    excl = {"BTCUSDT", "USDCUSDT", "ETHUSDT"}

    def g(s, t0, hold):
        A = idx.get(s, {})
        a0, a1, b0, b1 = A.get(t0), A.get(t0 + hold), hb.get(t0), hb.get(t0 + hold)
        if None in (a0, a1, b0, b1):
            return np.nan
        return -((a1 / a0 - 1) - (b1 / b0 - 1))
    tr = json.load(open(os.path.join(D, "trades.json")))
    res = {}
    for st in ("M", "K2", "K2+X"):
        sel = [r for r in tr if (r["set"] == st) or (st == "K2+X" and r["set"] in ("K2", "K2X"))]
        for hold in (24, 72):
            act, ra, rb = [], [], []
            for e in sel:
                t0 = e["L"] + H
                x = g(e["sym"], t0, hold * H)
                if not np.isfinite(x):
                    continue
                others = [s for s in idx if s not in excl and s != e["sym"] and first[s] < t0 - 30 * DAY and t0 in idx[s] and (t0 + hold * H) in idx[s]]
                ra.append([g(s, t0, hold * H) for s in rng.choice(others, draws)] if others else [np.nan] * draws)
                hrs = [t for t in range(e["L"] + 30 * DAY, min(e["L"] + 180 * DAY, CUT - 4 * DAY), H) if t in idx.get(e["sym"], {})]
                rb.append([g(e["sym"], int(t), hold * H) for t in rng.choice(hrs, draws)] if hrs else [np.nan] * draws)
                act.append((t0, x))
            act = np.array(act); ra = np.array(ra); rb = np.array(rb)
            for era, lo, hi in (("IS", 0, IS_END), ("VAL", IS_END, CUT)):
                w = (act[:, 0] >= lo) & (act[:, 0] < hi)
                if w.sum() < 3:
                    continue
                m = act[w, 1].mean()
                A = np.nanmean(ra[w], axis=0); B = np.nanmean(rb[w], axis=0)
                res[f"{st} H{hold} {era}"] = dict(n=int(w.sum()), gross_h1=round(m * 1e4), pct_other=round(float((A < m).mean() * 100), 1),
                                                   med_other=round(float(np.median(A) * 1e4)), pct_same=round(float((B < m).mean() * 100), 1),
                                                   med_same=round(float(np.nanmedian(B) * 1e4)))
                print(f"{st} H{hold} {era}", res[f"{st} H{hold} {era}"], flush=True)
    json.dump(res, open(os.path.join(HERE, "..", "random_M.json"), "w"), indent=1)


# ---------------- report ----------------
def year(t):
    return time.gmtime(t / 1000).tm_year


def stats(rows, key="H72"):
    x = [(r[key]["te"], r[key]["price"], r[key]["fund"], r[key]["net"]) for r in rows if r.get(key)]
    if len(x) < 2:
        return None
    a = np.array(x)
    m, t, n = k2rule.clt(a[:, 3], (a[:, 0] // DAY).astype(np.int64))
    sd = a[:, 3].std(ddof=1)
    yrs = {}
    for te, net in zip(a[:, 0], a[:, 3]):
        yrs.setdefault(year(te), []).append(net)
    srt = np.sort(a[:, 3])
    return dict(n=n, gross=a[:, 1].mean() * 1e4, fund=a[:, 2].mean() * 1e4, net=m * 1e4, t=t, med=np.median(a[:, 3]) * 1e4,
                sd=sd * 1e4, sr=m / sd if sd > 0 else np.nan, worst=srt[0] * 1e4, best=srt[-1] * 1e4,
                drop_best=srt[:-1].mean() * 1e4, win=(a[:, 3] > 0).mean(), days=len(np.unique(a[:, 0] // DAY)),
                years={y: (len(v), round(np.mean(v) * 1e4)) for y, v in sorted(yrs.items())})


def fmt(s):
    if s is None:
        return "n < 2"
    return (f"n {s['n']} (days {s['days']}) gross {s['gross']:+.0f} fund {s['fund']:+.0f} net {s['net']:+.0f} t {s['t']:.2f} "
            f"med {s['med']:+.0f} sd {s['sd']:.0f} SR {s['sr']:.3f} win {s['win']:.2f} worst {s['worst']:+.0f} best {s['best']:+.0f} "
            f"drop-best {s['drop_best']:+.0f} years {s['years']}")


def era(rows, e):
    return [r for r in rows if (r["L"] < IS_END) == (e == "IS")]


def report():
    tr = json.load(open(os.path.join(D, "trades.json")))
    M_ = [r for r in tr if r["set"] == "M"]
    bad = [r for r in M_ if r.get("guard_ratio") is not None and not (1 / 1.5 <= r["guard_ratio"] <= 1.5)]
    print("guard failures:", [(r["coin"], round(r["guard_ratio"], 3)) for r in bad])
    print("guard ratios:", {r["coin"]: (None if r.get("guard_ratio") is None else round(r["guard_ratio"], 3)) for r in M_})
    M_ = [r for r in M_ if r not in bad]
    print("\n== M events (non-KRW additions), K2 rule ==")
    bp = lambda v: "-" if v is None else f"{v * 1e4:+6.0f}"
    for r in M_:
        print(f"  {r['coin']:8s} {iso(r['L'])} {r['market']:4s} H72 {bp(r['H72'] and r['H72']['net'])} H24 {bp(r['H24'] and r['H24']['net'])} "
              f"pump(L-24h->entry) {bp(r['pump'])} pump(N-24h->entry) {bp(r.get('pump_notice'))} notice->entry {bp(r.get('pump_post_notice'))}  [{r['src']}]")
    for key in VARIANTS:
        for e in ("IS", "VAL"):
            print(f"M {key:8s} {e:3s}", fmt(stats(era(M_, e), key)))
    for e in ("IS", "VAL"):
        p = [r["pump"] for r in era(M_, e) if r["pump"] is not None]
        pn = [r["pump_notice"] for r in era(M_, e) if r.get("pump_notice") is not None]
        pp = [r["pump_post_notice"] for r in era(M_, e) if r.get("pump_post_notice") is not None]
        print(f"M pump {e}: L-24h->entry mean {np.mean(p)*1e4:+.0f} median {np.median(p)*1e4:+.0f} (n {len(p)}); "
              f"N-24h->entry mean {np.mean(pn)*1e4:+.0f} median {np.median(pn)*1e4:+.0f}; notice->entry mean {np.mean(pp)*1e4:+.0f} median {np.median(pp)*1e4:+.0f}")
    nf = [r for r in M_ if not r["src"].startswith("fallback")]
    for e in ("IS", "VAL"):
        print(f"M H72 no-fallback {e}", fmt(stats(era(nf, e))))
    print("\n== K2 recomputed with this k2rule copy, and the survivorship extras ==")
    K = [r for r in tr if r["set"] == "K2"]; X = [r for r in tr if r["set"] == "K2X"]
    for r in X:
        print(f"  extra {r['coin']:6s} {iso(r['L'])} H72 {'-' if not r['H72'] else round(r['H72']['net'] * 1e4)} "
              f"H24 {'-' if not r['H24'] else round(r['H24']['net'] * 1e4)} pump {'-' if r['pump'] is None else round(r['pump'] * 1e4)} [{r['src']}]")
    for key in ("H72", "H24", "H72_c15", "H72_p5", "H72_L2h"):
        for e in ("IS", "VAL"):
            print(f"K2   {key:8s} {e:3s}", fmt(stats(era(K, e), key)))
            print(f"K2+X {key:8s} {e:3s}", fmt(stats(era(K + X, e), key)))
    for e in ("IS", "VAL"):
        p = [r["pump"] for r in era(K, e) if r["pump"] is not None]
        print(f"K2 pump {e}: mean {np.mean(p)*1e4:+.0f} median {np.median(p)*1e4:+.0f}")
    print("\n== pooled M + K2 + X (information only) ==")
    for e in ("IS", "VAL"):
        print(f"pool H72 {e}", fmt(stats(era(M_ + K + X, e))))


if __name__ == "__main__":
    {"trades": trades, "random": random_bench, "report": report}[sys.argv[1]]()
