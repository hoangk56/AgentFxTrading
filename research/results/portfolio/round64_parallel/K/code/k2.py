"""K2 (declared in ../HYPOTHESES_K.md): Upbit KRW listing of a coin that already has a Binance perp (>= 7 days):
short alt perp / long BTC perp from L + 1 h (1m close), hold 24 / 72 h.
Usage: python -I k2.py events | fetch | run"""
import csv, json, os, sys, time, calendar
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kdata import UP, R, MAP, H, M, DAY, G0, CUT, ERAS, b1h, funding, btc_1m, cl_t, year_of, upbit
import fills

COST = 0.0042  # 4 taker fills x 5 bp + 2 x 10 bp alt half-spread + 2 x 1 bp BTC
OUT = os.path.dirname(os.path.abspath(__file__)) + "/.."
EV = os.path.join(UP, "k2_events.csv")


def perp_first(sym):
    with open(os.path.join(R, "binance", "perp_1d", sym + ".csv")) as f:
        f.readline()
        return int(f.readline().split(",")[0])


def status():
    st = {}
    for line in open(os.path.join(UP, "pull_m240.out")):
        p = line.split()
        if len(p) == 4:
            st[p[0]] = p[3]
    return st


def events():
    """Find L from the 240-min first candle, then one 60-min request to get the first KRW hour."""
    import net
    st = status()
    rows = []
    for coin, sym in sorted(MAP.items()):
        if coin in ("BTC", "USDC") or st.get(coin) != "history_start":
            continue
        u = upbit(coin)
        if u is None or not len(u):
            continue
        F = int(u[0, 0])
        pf = perp_first(sym)
        if F < pf + 7 * DAY:
            continue
        to = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime((F + 4 * H) / 1000))
        js = net.get(f"https://api.upbit.com/v1/candles/minutes/60?market=KRW-{coin}&to={to}&count=20")
        hrs = sorted(calendar.timegm(time.strptime(x["candle_date_time_utc"], "%Y-%m-%dT%H:%M:%S")) * 1000 for x in (js or []))
        hrs = [h for h in hrs if h >= F]
        if not hrs:
            continue
        rows.append((coin, sym, hrs[0], F, pf))
    with open(EV, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["coin", "sym", "L", "F240", "perp_first"]); w.writerows(rows)
    print(len(rows), "events")
    for r in rows:
        print(r[0], time.strftime('%Y-%m-%d %H:%M', time.gmtime(r[2] / 1000)))


def load_events():
    with open(EV) as f:
        rd = csv.DictReader(f)
        return [dict(coin=x["coin"], sym=x["sym"], L=int(x["L"]), pf=int(x["perp_first"])) for x in rd if int(x["L"]) < CUT - 4 * DAY]


ENTRY = {"e1h": H, "e1h5": H + 5 * M, "e2h": 2 * H}


def need_map(ev, extra=()):
    need = {}
    for e in ev:
        for off in ENTRY.values():
            for hold in (0, 24 * H, 72 * H):
                t = e["L"] + off + hold
                need.setdefault(e["sym"], set()).add(t)
        need.setdefault(e["sym"], set()).add(e["L"] - 24 * H)
    for sym, t in extra:
        need.setdefault(sym, set()).add(t)
    return need


def btc_px(btc, t):
    i = (t - G0) // M
    for d in range(5):
        if 0 <= i + d < len(btc) and np.isfinite(btc[i + d]):
            return btc[i + d]
    return np.nan


def fsum(F, a, b):
    if not len(F):
        return 0.0
    w = (F[:, 0] > a + 30000) & (F[:, 0] <= b + 30000)
    return float(F[w, 1].sum())


def trade(sym, te, hold, cache, btc, FU, cost=COST):
    sc = 1000.0 if sym.startswith("1000") else 1.0
    ae, ax = fills.price_at(cache, te) / sc, fills.price_at(cache, te + hold) / sc
    be, bx = btc_px(btc, te), btc_px(btc, te + hold)
    if not all(np.isfinite([ae, ax, be, bx])):
        return None
    price = -((ax / ae - 1) - (bx / be - 1))
    fund = fsum(FU[sym], te + M, te + hold + M) - fsum(FU["BTCUSDT"], te + M, te + hold + M)
    return price, fund, price + fund - cost


def h1_alt(sym):
    b = b1h(sym)
    return {int(t): c for t, c in zip(b[:, 0], b[:, 4])} if b is not None else {}


def random_k2(ev, draws=500, seed=11):
    """Gross short-alt / long-BTC P&L on 1h closes (fill = close of the 1h bar starting at L + 1 h, i.e. at L + 2 h):
    actual events vs (a) other universe alts at the same time, (b) same coin at random hours 30-180 d after L."""
    rng = np.random.default_rng(seed)
    hb = h1_alt("BTCUSDT")
    H1 = {s: h1_alt(s) for s in sorted(set(MAP.values()) - {"USDCUSDT", "BTCUSDT"})}
    pf = {s: perp_first(s) for s in H1}
    sc = lambda s: 1000.0 if s.startswith("1000") else 1.0
    def g(s, t0, hold):
        a0, a1, b0, b1 = H1[s].get(t0), H1[s].get(t0 + hold), hb.get(t0), hb.get(t0 + hold)
        if None in (a0, a1, b0, b1):
            return np.nan
        return -((a1 / a0 - 1) - (b1 / b0 - 1))
    out = {}
    for hold in (24, 72):
        act, ra, rb = [], [], []
        for e in ev:
            t0 = e["L"] + H  # 1h bar starting at L + 1 h; its close = price at L + 2 h
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
            out[(hold, era)] = dict(n=int(w.sum()), gross_h1=m * 1e4, pct_other_alts=float((A < m).mean() * 100),
                                    med_other=float(np.median(A) * 1e4), pct_same_coin=float((B < m).mean() * 100),
                                    med_same=float(np.median(B) * 1e4))
            print("random", hold, era, out[(hold, era)], flush=True)
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "events":
        events(); sys.exit()
    ev = load_events()
    if mode == "fetch":
        fills.fetch(need_map(ev)); sys.exit()
    if mode == "random":
        random_k2(ev); sys.exit()
    btc = btc_1m()
    syms = sorted({e["sym"] for e in ev})
    FU = {s: funding(s) for s in syms}; FU["BTCUSDT"] = funding("BTCUSDT")
    caches = {s: fills.load(s) for s in syms}
    res = {}
    T = {}
    for ename, off in ENTRY.items():
        for hold in (24, 72):
            for cm in (1.0, 1.5):
                rows = []
                for e in ev:
                    te = e["L"] + off
                    r = trade(e["sym"], te, hold * H, caches[e["sym"]], btc, FU, COST * cm)
                    if r is None:
                        continue
                    # pre-entry run-up: alt vs BTC from L - 24 h to entry
                    a0 = fills.price_at(caches[e["sym"]], e["L"] - 24 * H); a1 = fills.price_at(caches[e["sym"]], te)
                    b0 = btc_px(btc, e["L"] - 24 * H); b1 = btc_px(btc, te)
                    run = (a1 / a0 - 1) - (b1 / b0 - 1) if all(np.isfinite([a0, a1, b0, b1])) else np.nan
                    rows.append((te, *r, run, e["L"] - e["pf"]))
                T[(ename, hold, cm)] = np.array(rows)
    import pickle
    pickle.dump(dict(T=T, ev=ev), open(os.path.join(OUT, "k2_trades.pkl"), "wb"))
    for (ename, hold, cm), a in T.items():
        for era in ("IS", "VAL"):
            lo, hi = ERAS[era]
            x = a[(a[:, 0] >= lo) & (a[:, 0] < hi)]
            if len(x) < 3:
                print(ename, hold, cm, era, "n", len(x)); continue
            day = (x[:, 0] // DAY).astype(np.int64)
            yrs = year_of(x[:, 0])
            by = {int(y): (int((yrs == y).sum()), round(float(x[yrs == y, 3].mean() * 1e4))) for y in np.unique(yrs)}
            print(f"{ename} H{hold} c{cm} {era} n {len(x)} gross {x[:,1].mean()*1e4:.0f} fund {x[:,2].mean()*1e4:.0f} "
                  f"net {x[:,3].mean()*1e4:.0f} t {cl_t(x[:,3], day):.2f} median {np.median(x[:,3])*1e4:.0f} sd {x[:,3].std(ddof=1)*1e4:.0f} "
                  f"SR {x[:,3].mean()/x[:,3].std(ddof=1):.3f} win {(x[:,3]>0).mean():.2f} worst {x[:,3].min()*1e4:.0f} best {x[:,3].max()*1e4:.0f} "
                  f"runup {np.nanmean(x[:,4])*1e4:.0f} years {by}", flush=True)

