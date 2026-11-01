"""Stream W backtest: Kalshi daily-high brackets vs observed max-so-far (ISD) and climatology.
Rules (a), (b), (c) as declared in HYPOTHESES_W.md. Every Kalshi row has close_time < 2025-01-01 (cut at pull).
Usage: python -I backtest.py [--draws N]"""
import os, sys, re, json, glob, math, datetime as dt, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M

DATA = M.DATA
CITY_OF = {"HIGHNY": "NY", "KXHIGHNY": "NY", "HIGHCHI": "CHI", "KXHIGHCHI": "CHI",
           "HIGHAUS": "AUS", "KXHIGHAUS": "AUS", "HIGHMIA": "MIA", "KXHIGHMIA": "MIA"}
C = 10  # contracts per order
CUT = int(dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp())


def fee(p, mult=1.0):
    """Kalshi taker fee per contract ($): ceil to the cent of 0.07*C*P*(1-P), divided by C."""
    return math.ceil(round(0.07 * C * p * (1 - p) * 100, 6)) / 100 / C * mult


def f(x):
    try:
        return None if x in (None, "") else float(x)
    except ValueError:  # free-text settlement notes (e.g. CLI not finalized); truth comes from `result`
        return None


def bracket(m):
    st = m["strike_type"]
    if st == "less":
        return -999, int(round(float(m["cap_strike"]))) - 1
    if st == "greater":
        return int(round(float(m["floor_strike"]))) + 1, 999
    if st == "between":
        return int(round(float(m["floor_strike"]))), int(round(float(m["cap_strike"])))
    # 2021-22 markets have no strike_type: parse the YES subtitle ("97° or higher", "93° or lower", "80° to 81°")
    t = (m.get("yes_sub_title") or "").replace("°", "")
    r = re.match(r"^\s*(-?\d+)\s+or (higher|above|more)\s*$", t)
    if r:
        return int(r.group(1)), 999
    r = re.match(r"^\s*(-?\d+)\s+or (lower|below|less)\s*$", t)
    if r:
        return -999, int(r.group(1))
    r = re.match(r"^\s*(-?\d+)\s*to\s*(-?\d+)\s*$", t)
    if r:
        return int(r.group(1)), int(r.group(2))
    return None


def load_events():
    evs = []
    for p in sorted(glob.glob(f"{DATA}/events/*/*.json")):
        e = json.load(open(p))
        series = e["event_ticker"].split("-")[0]
        city = CITY_OF[series]
        day = e["date"]
        br = []
        for m in e["markets"]:
            b = bracket(m)
            if b is None or m.get("result") not in ("yes", "no"):
                continue
            q = {}
            for row in m["candles"]:
                t = int(row[0])
                if t >= CUT:
                    continue
                q[t] = (f(row[1]), f(row[2]))
            br.append({"ticker": m["ticker"], "lo": b[0], "hi": b[1], "yes": m["result"] == "yes",
                       "ev": f(m.get("expiration_value")), "q": q, "qt": np.array(sorted(q), np.int64),
                       "close": int(dt.datetime.fromisoformat(m["close_time"].replace("Z", "+00:00")).timestamp())})
        if br:
            evs.append({"city": city, "day": day, "br": br, "series": series})
    return evs




def quote(b, t):
    """(bid, ask) as of time t: close of the latest hourly candle ending <= t (an hour without a candle had no
    quote change). bid None if yes_bid = 0 (no bid), ask None if yes_ask = 1 (no ask). None if no candle yet or
    after the market's close."""
    if t > b["close"] or len(b["qt"]) == 0:
        return None
    i = np.searchsorted(b["qt"], t, side="right") - 1
    if i < 0:
        return None
    bid, ask = b["q"][int(b["qt"][i])]
    bid = bid if bid is not None and bid > 0 else None
    ask = ask if ask is not None and ask < 1 else None
    if bid is not None and ask is not None and ask <= bid:
        return None
    if bid is None and ask is None:
        return None
    return bid, ask


def price_of(b, side, t):
    """Taker price for buying `side` at t, or None if that side has no quote."""
    q = quote(b, t)
    if q is None:
        return None
    if side == "yes":
        return q[1]
    return None if q[0] is None else 1 - q[0]


def trade_pnl(b, side, t, mode="base"):
    """P&L per contract ($) and price paid; side 'yes'/'no'; mode base / x15 / maker."""
    q = quote(b, t)
    if q is None:
        return None
    bid, ask = q
    if mode == "maker":
        if bid is None or ask is None:
            return None
        mid = (bid + ask) / 2
        price = mid if side == "yes" else 1 - mid
        cost = 0.0
    else:
        price = price_of(b, side, t)
        if price is None:
            return None
        cost = fee(price, 1.5 if mode == "x15" else 1.0)
        if mode == "x15":
            price += 0.5 * (ask - bid) if (bid is not None and ask is not None) else 0.01
    win = b["yes"] if side == "yes" else (not b["yes"])
    return (1.0 if win else 0.0) - price - cost, price


class Obs:
    def __init__(self):
        self.d = {c: M.load(c) for c in M.CITIES}

    def t0(self, city, day):
        return M.day_start_utc(day, self.d[city][3])

    def state(self, city, day, T):
        ts, tf, sod, off = self.d[city]
        return M.state(ts, tf, self.t0(city, day), T)


# ---------------- rules ----------------
def rule_a(evs, obs, tab, T, theta, late=0, mode="base", rnd=None):
    out = []
    for e in evs:
        s = obs.state(e["city"], e["day"], T)
        if s is None:
            continue
        Mx, cur = s
        t = obs.t0(e["city"], e["day"]) + T * 3600
        key = (e["city"], M.season(int(e["day"][5:7])), T, M.dropb(Mx - cur))
        best = None
        for b in e["br"]:
            p = M.prob(tab, key, b["lo"], b["hi"], Mx)
            if p is None:
                continue
            for side, pw in (("yes", p), ("no", 1 - p)):
                pr = price_of(b, side, t)
                if pr is None:
                    continue
                edge = pw - pr - fee(pr)
                if best is None or edge > best[0]:
                    best = (edge, b, side)
        if best is None or best[0] < theta:
            continue
        b, side = best[1], best[2]
        if rnd is not None:
            cand = [x for x in e["br"] if price_of(x, side, t) is not None]
            b = cand[rnd.integers(len(cand))]
        r = trade_pnl(b, side, t + late * 3600, mode)
        if r is not None:
            out.append((e["city"], e["day"], r[0], r[1]))
    return out


def rule_b(evs, obs, x, margin, late=0, mode="base", rnd=None, detail=None):
    out = []
    for e in evs:
        t0 = obs.t0(e["city"], e["day"])
        pnl, paid, done = 0.0, 0.0, set()
        n = 0
        for T in range(10, 24):
            s = obs.state(e["city"], e["day"], T)
            if s is None:
                continue
            Mx = s[0] - margin
            t = t0 + T * 3600
            for b in e["br"]:
                if b["ticker"] in done:
                    continue
                q = quote(b, t)
                if q is None:
                    continue
                bid, ask = q
                dead = b["hi"] < Mx
                won = b["hi"] == 999 and b["lo"] <= Mx
                side = None
                if dead and bid is not None and bid >= x:
                    side = "no"
                elif won and ask is not None and ask <= 1 - x:
                    side = "yes"
                if side is None:
                    continue
                done.add(b["ticker"])
                tb = b
                if rnd is not None:
                    cand = [y for y in e["br"] if price_of(y, side, t) is not None
                            and not (y["hi"] < Mx) and not (y["hi"] == 999 and y["lo"] <= Mx)]
                    if not cand:
                        continue
                    tb = cand[rnd.integers(len(cand))]
                r = trade_pnl(tb, side, t + late * 3600, mode)
                if r is not None:
                    pnl += r[0]; paid += r[1]; n += 1
                    if detail is not None:
                        detail.append((e["city"], e["day"], T, b["ticker"], side, r[1], r[0], b["yes"]))
        if n:
            out.append((e["city"], e["day"], pnl, paid))
    return out


def rule_c(evs, obs, lo, hi, late=0, mode="base", rnd=None):
    out = []
    for e in evs:
        t = obs.t0(e["city"], e["day"])  # quotes as of 00:00 LST of the contract day (T-1 evening)
        res = []
        valid = [b for b in e["br"] if quote(b, t) is not None and None not in quote(b, t)]
        for b in valid:
            bid, ask = quote(b, t)
            mid = (bid + ask) / 2
            if not (lo <= mid <= hi):
                continue
            tb = valid[rnd.integers(len(valid))] if rnd is not None else b
            r = trade_pnl(tb, "no", t + late * 3600, mode)
            if r is not None:
                res.append(r)
        if res:
            out.append((e["city"], e["day"], float(np.mean([r[0] for r in res])), float(np.mean([r[1] for r in res]))))
    return out


# ---------------- stats ----------------
def summarize(tr, era=None):
    if era:
        tr = [x for x in tr if era[0] <= x[1] <= era[1]]
    if not tr:
        return {"n": 0}
    pnl = np.array([x[2] for x in tr]); paid = np.array([x[3] for x in tr])
    days = np.array([x[1] for x in tr])
    ud = np.unique(days)
    cl = np.array([pnl[days == d].sum() for d in ud])
    G = len(ud)
    se = math.sqrt(G / max(G - 1, 1) * ((cl - cl.sum() / len(pnl) * np.array([(days == d).sum() for d in ud])) ** 2).sum()) / len(pnl)
    m = pnl.mean()
    sd_cd = pnl.std(ddof=1) if len(pnl) > 1 else float("nan")
    return {"n": len(pnl), "dates": G, "mean_c": round(100 * m, 3), "t_date": round(m / se, 2) if se > 0 else None,
            "t_cityday": round(m / (sd_cd / math.sqrt(len(pnl))), 2) if len(pnl) > 1 and sd_cd > 0 else None,
            "per$_pct": round(100 * pnl.sum() / paid.sum(), 3), "sharpe_trade": round(m / sd_cd, 4) if sd_cd > 0 else None}


def by_year(tr):
    ys = sorted({x[1][:4] for x in tr})
    return {y: summarize(tr, (f"{y}-01-01", f"{y}-12-31")) for y in ys}


IS = ("2000-01-01", "2023-12-31")
VAL = ("2024-01-01", "2024-12-31")
M_TAB = [None]

if __name__ == "__main__":
    draws = int(sys.argv[sys.argv.index("--draws") + 1]) if "--draws" in sys.argv else 200
    evs = load_events()
    obs = Obs()
    tab, stats = M.fit()
    M_TAB[0] = tab
    margin = int(json.load(open(os.path.join(os.path.dirname(__file__), "..", "margin.json")))["margin"])
    print("events", len(evs), "by city", {c: sum(e["city"] == c for e in evs) for c in M.CITIES}, "margin", margin)
    cells = {}
    for T in (15, 17):
        for th in (0.05, 0.10):
            cells[f"a_T{T}_th{th}"] = lambda late=0, mode="base", rnd=None, T=T, th=th: rule_a(evs, obs, tab, T, th, late, mode, rnd)
    for x in (0.03, 0.05):
        cells[f"b_x{x}"] = lambda late=0, mode="base", rnd=None, x=x: rule_b(evs, obs, x, margin, late, mode, rnd)
    cells["c1_3-10c"] = lambda late=0, mode="base", rnd=None: rule_c(evs, obs, 0.03, 0.10, late, mode, rnd)
    cells["c2_10-20c_info"] = lambda late=0, mode="base", rnd=None: rule_c(evs, obs, 0.10, 0.20, late, mode, rnd)
    res = {}
    rng = np.random.default_rng(63)
    for name, fn in cells.items():
        base = fn()
        r = {"IS": summarize(base, IS), "VAL": summarize(base, VAL), "years": by_year(base)}
        for mode in ("x15", "maker"):
            tr = fn(mode=mode)
            r[mode] = {"IS": summarize(tr, IS), "VAL": summarize(tr, VAL)}
        tr = fn(late=1)
        r["late1"] = {"IS": summarize(tr, IS), "VAL": summarize(tr, VAL)}
        # random benchmark (same timing, same side, random bracket)
        rm = {"IS": [], "VAL": []}
        for _ in range(draws):
            tr = fn(rnd=rng)
            for era, rr in (("IS", IS), ("VAL", VAL)):
                s = summarize(tr, rr)
                rm[era].append(s.get("mean_c", np.nan) if s["n"] else np.nan)
        for era in ("IS", "VAL"):
            arr = np.array(rm[era], float)
            mc = r[era].get("mean_c")
            r[era]["rand_pct"] = None if mc is None or np.all(np.isnan(arr)) else round(100 * np.nanmean(arr < mc), 1)
            r[era]["rand_mean_c"] = None if np.all(np.isnan(arr)) else round(float(np.nanmean(arr)), 3)
        res[name] = r
        print(name, json.dumps({k: r[k] for k in ("IS", "VAL")}), flush=True)
    out = os.path.join(os.path.dirname(__file__), "..", "results_W.json")
    json.dump({"model_stats": stats, "cells": res, "draws": draws}, open(out, "w"), indent=1)
