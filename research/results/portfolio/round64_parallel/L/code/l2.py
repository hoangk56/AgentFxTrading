"""Stream L (declared in ../HYPOTHESES_L.md): Coinbase <COIN>-USD listing of a coin that already has a Binance perp:
short alt perp / long BTC perp from L + 1 h (1m close), hold 24 / 72 h. The trade, fill and funding logic is K2's,
imported unchanged from ../../K/code (k2.trade, k2.btc_px, fills.price_at, kdata.funding / btc_1m / cl_t). Only the
caches written by this stream live under research/data/coinbase/binance/.
Usage: python -I l2.py events | fetch | run | random"""
import csv, json, os, pickle, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
KCODE = os.path.join(HERE, "..", "..", "K", "code")
sys.path.insert(0, HERE)
sys.path.insert(1, KCODE)
import k2, fills, kdata  # K's modules, unchanged
import importlib.util as _ilu
# k2 puts K/code first on sys.path, so a plain `import net` would load K's fetcher (logs to research/data/upbit):
# load this stream's net.py by path instead (round 64 L: 281 fapi requests were logged in upbit/requests.log before this fix)
_sp = _ilu.spec_from_file_location("lnet", os.path.join(HERE, "net.py"))
lnet = _ilu.module_from_spec(_sp)
from kdata import H, M, DAY, G0, CUT, ERAS, cl_t, year_of

CB = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/coinbase"
BD = os.path.join(CB, "binance")
A1 = os.path.join(BD, "alt_1m")
FD = os.path.join(BD, "funding")
P1 = os.path.join(BD, "perp_1h")
OUT = os.path.join(HERE, "..")
for d in (A1, FD, P1):
    os.makedirs(d, exist_ok=True)


def iso(ms):
    return time.strftime('%Y-%m-%d %H:%M', time.gmtime(ms / 1000))


def listings():
    with open(os.path.join(CB, "listings.csv")) as f:
        return list(csv.DictReader(f))


def load_events(min_age=7 * DAY, guard=True):
    """One event per coin: first <COIN>-USD hour L, perp >= min_age old at L, L in [G0, CUT - 4 d)."""
    ev = []
    seen = set()
    excl = json.load(open(os.path.join(CB, "exclusions.json"))) if os.path.exists(os.path.join(CB, "exclusions.json")) else {}
    for r in listings():
        if r["pre"] != "0" or not r["L"]:
            continue
        L, pf = int(r["L"]), int(r["perp_first"])
        if L < G0 or L >= CUT - 4 * DAY or L - pf < min_age or r["sym"] in seen:
            continue
        if guard and r["coin"] in excl:
            continue
        seen.add(r["sym"])
        ev.append(dict(coin=r["coin"], sym=r["sym"], L=L, pf=pf, product=r["product"], status=r["status"],
                       c_L1=float(r["c_L1"]) if r["c_L1"] else np.nan))
    return sorted(ev, key=lambda e: e["L"])


def cache(sym):
    """K's 1m cache (read-only) merged with this stream's."""
    c = dict(fills.load(sym))
    p = os.path.join(A1, sym + ".csv")
    if os.path.exists(p):
        with open(p) as f:
            for t, v in csv.reader(f):
                c.setdefault(int(t), float(v))
    return c


def fetch_1m(need, limit=99):
    """Same as K's fills.fetch, written to this stream's cache."""
    net = lnet; _sp.loader.exec_module(lnet) if not hasattr(lnet, 'get') else None
    for sym in sorted(need):
        have = cache(sym)
        miss = sorted(t for t in need[sym] if t not in have and t < CUT)
        rows, k = [], 0
        while k < len(miss):
            st = miss[k]
            js = net.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1m&startTime={st}&limit={limit}")
            got = {int(x[0]): float(x[4]) for x in (js or []) if int(x[0]) < CUT}
            if not got:
                got = {st: float("nan")}
            rows += [(t, c) for t, c in got.items() if t not in have]
            have.update(got)
            end = st + limit * M
            while k < len(miss) and miss[k] < end:
                k += 1
        if rows:
            with open(os.path.join(A1, sym + ".csv"), "a", newline="") as f:
                csv.writer(f).writerows(rows)
        print("1m", sym, len(miss), "needed,", len(rows), "bars added", flush=True)


def funding(sym, lo=None, hi=None):
    """kdata.funding if it covers [lo, hi], else this stream's REST copy."""
    F = kdata.funding(sym)
    if lo is None or (len(F) and F[0, 0] <= lo and F[-1, 0] >= hi):
        return F
    p = os.path.join(FD, sym + ".csv")
    if os.path.exists(p):
        G = kdata._read(p, 2)
        if len(G):
            return np.vstack([F, G]) if len(F) else G
    return F


def fetch_funding(ev):
    net = lnet; _sp.loader.exec_module(lnet) if not hasattr(lnet, 'get') else None
    for e in ev:
        lo, hi = e["L"], e["L"] + 2 * H + 72 * H
        F = kdata.funding(e["sym"])
        if len(F) and F[0, 0] <= lo and F[-1, 0] >= hi:
            continue
        p = os.path.join(FD, e["sym"] + ".csv")
        if os.path.exists(p):
            continue
        st, end, rows = lo - 2 * DAY, min(lo + 6 * DAY, CUT - 1000), []
        js = net.get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={e['sym']}&startTime={st}&endTime={end}&limit=1000")
        rows = [(x["fundingTime"], x["fundingRate"]) for x in (js or []) if x["fundingTime"] < CUT]
        with open(p, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["t", "rate"]); w.writerows(rows)
        print("funding", e["sym"], len(rows), flush=True)


def h1(sym):
    """1h closes: kdata.b1h (local files) else this stream's REST copy."""
    b = kdata.b1h(sym)
    d = {int(t): c for t, c in zip(b[:, 0], b[:, 4])} if b is not None else {}
    p = os.path.join(P1, sym + ".csv")
    if os.path.exists(p):
        a = kdata._read(p, 5)
        for t, c in zip(a[:, 0], a[:, 4]):
            d.setdefault(int(t), c)
    return d


def fetch_h1(syms):
    net = lnet; _sp.loader.exec_module(lnet) if not hasattr(lnet, 'get') else None
    END = CUT - 1000
    for s in syms:
        if kdata.b1h(s) is not None or os.path.exists(os.path.join(P1, s + ".csv")):
            continue
        rows, st = [], 1567296000000
        while st < END:
            js = net.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&startTime={st}&endTime={END}&limit=1500")
            if not js:
                break
            rows += [(x[0], x[1], x[2], x[3], x[4]) for x in js if x[0] <= END]
            st = js[-1][0] + H
            if len(js) < 1500:
                break
        with open(os.path.join(P1, s + ".csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["t", "o", "h", "l", "c"]); w.writerows(rows)
        print("1h", s, len(rows), flush=True)


def run_set(ev, label, kfund=False):
    btc = kdata.btc_1m()
    T = {}
    FU = {"BTCUSDT": kdata.funding("BTCUSDT")}
    for e in ev:
        FU[e["sym"]] = kdata.funding(e["sym"]) if kfund else funding(e["sym"], e["L"], e["L"] + 2 * H + 72 * H)
    C = {e["sym"]: cache(e["sym"]) for e in ev}
    for ename, off in k2.ENTRY.items():
        for hold in (24, 72):
            for cm in (1.0, 1.5):
                rows = []
                for i, e in enumerate(ev):
                    te = e["L"] + off
                    r = k2.trade(e["sym"], te, hold * H, C[e["sym"]], btc, FU, k2.COST * cm)
                    if r is None:
                        continue
                    a0 = fills.price_at(C[e["sym"]], e["L"] - 24 * H); a1 = fills.price_at(C[e["sym"]], te)
                    b0 = k2.btc_px(btc, e["L"] - 24 * H); b1 = k2.btc_px(btc, te)
                    run = (a1 / a0 - 1) - (b1 / b0 - 1) if all(np.isfinite([a0, a1, b0, b1])) else np.nan
                    rows.append((te, *r, run, e["L"] - e["pf"], i))
                T[(ename, hold, cm)] = np.array(rows).reshape(-1, 7)
    return T


def summ(a, label):
    out = {}
    for era in ("IS", "VAL"):
        lo, hi = ERAS[era]
        x = a[(a[:, 0] >= lo) & (a[:, 0] < hi)]
        if len(x) < 3:
            print(f"{label} {era} n {len(x)}", flush=True); out[era] = dict(n=len(x)); continue
        day = (x[:, 0] // DAY).astype(np.int64)
        yrs = year_of(x[:, 0])
        by = {int(y): (int((yrs == y).sum()), round(float(x[yrs == y, 3].mean() * 1e4))) for y in np.unique(yrs)}
        sr = x[:, 3].mean() / x[:, 3].std(ddof=1)
        d = dict(n=len(x), gross=x[:, 1].mean() * 1e4, fund=x[:, 2].mean() * 1e4, net=x[:, 3].mean() * 1e4,
                 t=cl_t(x[:, 3], day), median=np.median(x[:, 3]) * 1e4, sd=x[:, 3].std(ddof=1) * 1e4, SR=sr,
                 win=(x[:, 3] > 0).mean(), worst=x[:, 3].min() * 1e4, best=x[:, 3].max() * 1e4,
                 runup=np.nanmean(x[:, 4]) * 1e4, years=by, ndays=len(np.unique(day)))
        out[era] = d
        print(f"{label} {era} n {d['n']} days {d['ndays']} gross {d['gross']:.0f} fund {d['fund']:.0f} net {d['net']:.0f} t {d['t']:.2f} "
              f"median {d['median']:.0f} sd {d['sd']:.0f} SR {sr:.3f} win {d['win']:.2f} worst {d['worst']:.0f} best {d['best']:.0f} "
              f"runup {d['runup']:.0f} years {by}", flush=True)
    return out


def random_l(ev, draws=500, seed=11):
    """Copy of k2.random_k2 (same draws, same pricing on 1h closes) with the universe = K's perps + L's symbols."""
    rng = np.random.default_rng(seed)
    hb = h1("BTCUSDT")
    uni = sorted((set(kdata.MAP.values()) | {e["sym"] for e in ev}) - {"USDCUSDT", "BTCUSDT"})
    H1 = {s: h1(s) for s in uni}
    pf = {s: k2.perp_first(s) for s in uni}
    def g(s, t0, hold):
        a0, a1, b0, b1 = H1[s].get(t0), H1[s].get(t0 + hold), hb.get(t0), hb.get(t0 + hold)
        if None in (a0, a1, b0, b1):
            return np.nan
        return -((a1 / a0 - 1) - (b1 / b0 - 1))
    out = {}
    for hold in (24, 72):
        act, ra, rb = [], [], []
        for e in ev:
            t0 = e["L"] + H
            x = g(e["sym"], t0, hold * H)
            if not np.isfinite(x):
                continue
            act.append((t0, x))
            others = [s for s in H1 if s != e["sym"] and pf[s] < t0 - 30 * DAY and t0 in H1[s] and (t0 + hold * H) in H1[s]]
            ra.append([g(s, t0, hold * H) for s in rng.choice(others, draws)] if others else [np.nan] * draws)
            hrs = [t for t in range(e["L"] + 30 * DAY, min(e["L"] + 180 * DAY, CUT - 4 * DAY), H) if t in H1[e["sym"]]]
            rb.append([g(e["sym"], int(t), hold * H) for t in rng.choice(hrs, draws)] if hrs else [np.nan] * draws)
        act = np.array(act); ra = np.array(ra); rb = np.array(rb)
        for era in ("IS", "VAL"):
            lo, hi = ERAS[era]
            w = (act[:, 0] >= lo) & (act[:, 0] < hi)
            if w.sum() < 3:
                continue
            m = act[w, 1].mean()
            A = np.nanmean(ra[w], axis=0); B = np.nanmean(rb[w], axis=0)
            out[f"H{hold} {era}"] = dict(n=int(w.sum()), gross_h1=float(m * 1e4), pct_other_alts=float((A < m).mean() * 100),
                                         med_other=float(np.median(A) * 1e4), pct_same_coin=float((B < m).mean() * 100),
                                         med_same=float(np.median(B) * 1e4))
            print("random", hold, era, out[f"H{hold} {era}"], flush=True)
    return out


def overlap(ev, kev):
    ks = {}
    for e in kev:
        ks.setdefault(e["sym"], []).append(e["L"])
    return [any(abs(e["L"] - L) <= 7 * DAY for L in ks.get(e["sym"], [])) for e in ev]


if __name__ == "__main__":
    mode = sys.argv[1]
    ev7, ev1 = load_events(7 * DAY), load_events(1 * DAY)
    if mode == "events":
        for tag, ev in (("main >=7d", ev7), ("secondary >=1d", ev1)):
            yrs = year_of([e["L"] for e in ev])
            print(tag, len(ev), "events; per year", {int(y): int((yrs == y).sum()) for y in np.unique(yrs)})
        for e in ev1:
            print(e["coin"], e["sym"], e["status"], iso(e["L"]), "perp age d", round((e["L"] - e["pf"]) / DAY, 1))
        sys.exit()
    if mode == "fetch":
        need = k2.need_map(ev1)
        fetch_1m(need)
        fetch_funding(ev1)
        sys.exit()
    if mode == "fetch_h1":
        fetch_h1(sorted({e["sym"] for e in ev1})); sys.exit()
    if mode == "random":
        res = random_l(ev7)
        json.dump(res, open(os.path.join(OUT, "l2_random.json"), "w"), indent=1); sys.exit()
    if mode == "run":
        kev = k2.load_events()
        res = {}
        allT = {}
        for tag, ev in (("main7", ev7), ("sec1", ev1)):
            T = run_set(ev, tag)
            allT[tag] = (T, ev)
            for (ename, hold, cm), a in T.items():
                res[f"{tag} {ename} H{hold} c{cm}"] = summ(a, f"{tag} {ename} H{hold} c{cm}")
        # overlap with K2 and pooled K2 + L (main set, e1h, costs x1)
        T, ev = allT["main7"]
        ov = overlap(ev, kev)
        print("overlap with K2 (same coin within 7 d):", [(e["coin"], iso(e["L"])) for e, o in zip(ev, ov) if o], flush=True)
        evn = [e for e, o in zip(ev, ov) if not o]
        Tn = run_set(evn, "noov")
        KT = run_set(kev, "K2", kfund=True)  # reproduces K's k2 numbers with K's own caches (read-only)
        for hold in (24, 72):
            for cm in (1.0, 1.5):
                res[f"noov e1h H{hold} c{cm}"] = summ(Tn[("e1h", hold, cm)], f"L-no-overlap e1h H{hold} c{cm}")
                res[f"K2 e1h H{hold} c{cm}"] = summ(KT[("e1h", hold, cm)], f"K2-repro e1h H{hold} c{cm}")
                pool = np.vstack([KT[("e1h", hold, cm)], Tn[("e1h", hold, cm)]])
                res[f"pool e1h H{hold} c{cm}"] = summ(pool, f"pooled K2+L e1h H{hold} c{cm}")
            for en in ("e1h5", "e2h"):
                pool = np.vstack([KT[(en, hold, 1.0)], Tn[(en, hold, 1.0)]])
                res[f"pool {en} H{hold} c1.0"] = summ(pool, f"pooled K2+L {en} H{hold} c1.0")
        fl = set(json.load(open(os.path.join(CB, "otherquote_flag.json")))) if os.path.exists(os.path.join(CB, "otherquote_flag.json")) else set()
        Tq = run_set([e for e in ev if e["coin"] not in fl], "noq")
        for hold in (24, 72):
            res[f"main7 no-otherquote e1h H{hold}"] = summ(Tq[("e1h", hold, 1.0)], f"main7 without other-quote-earlier e1h H{hold}")
        pickle.dump(dict(T=allT, Tn=Tn, KT=KT, ov=ov), open(os.path.join(BD, "l2_trades.pkl"), "wb"))
        json.dump(res, open(os.path.join(OUT, "l2_results.json"), "w"), indent=1, default=float)
        # per-event table (main set, e1h, H24 / H72 net)
        with open(os.path.join(OUT, "l2_events.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["coin", "sym", "product", "status", "L_utc", "perp_age_d", "k2_overlap", "net_H24_bp", "net_H72_bp", "runup_bp"])
            a24 = {int(r[6]): r for r in T[("e1h", 24, 1.0)]}; a72 = {int(r[6]): r for r in T[("e1h", 72, 1.0)]}
            for i, (e, o) in enumerate(zip(ev, ov)):
                r24, r72 = a24.get(i), a72.get(i)
                w.writerow([e["coin"], e["sym"], e["product"], e["status"], iso(e["L"]), round((e["L"] - e["pf"]) / DAY, 1), int(o),
                            round(r24[3] * 1e4) if r24 is not None else "", round(r72[3] * 1e4) if r72 is not None else "",
                            round(r72[4] * 1e4) if r72 is not None and np.isfinite(r72[4]) else ""])
