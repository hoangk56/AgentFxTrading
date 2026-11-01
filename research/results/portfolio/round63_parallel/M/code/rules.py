"""Round 63 stream M rules: round 24 HYPOTHESES_C readings (+ Amendment 0 of HYPOTHESES_M: data-driven signals end
one minute before the entry quote). Each rule returns candidates:
  dict(id, sym, ms_in, ms_out, side_fn(ms_in, idx) -> side, ctrl, [pool/clock for day controls], [carry])."""
import datetime as dt
import os

import holidays
import numpy as np

import eng
from eng import loc_ms, bdays, xmas, price

D0, D1 = dt.date(2016, 1, 1), dt.date(2024, 12, 31)
YRS = range(2015, 2026)
XECB = holidays.financial_holidays("XECB", years=YRS)
XSHG = holidays.financial_holidays("XSHG", years=YRS)
XNYS = holidays.financial_holidays("XNYS", years=YRS)
ENG = holidays.UK(subdiv="ENG", years=YRS)
USF = holidays.US(years=YRS)
EARLY = {dt.date.fromisoformat(x) for x in [
    "2016-11-25", "2017-11-24", "2018-11-23", "2019-11-29", "2020-11-27", "2021-11-26", "2022-11-25",
    "2023-11-24", "2024-11-29", "2017-07-03", "2018-07-03", "2019-07-03", "2023-07-03", "2024-07-03"]} | {dt.date(y, 12, 24) for y in YRS}
MIN = 60000


def fixed(s):
    return lambda ms, idx: np.full(len(ms), float(s))


R24READ = os.environ.get("M_R24READ") == "1"   # information run: round 24's zero-latency signal reading


def rel(sym, s_min, e_min, mult):
    """side = mult * sign(p(t - e) / p(t - s) - 1), t = entry."""
    if R24READ:
        e_min = 0
    def f(ms, idx):
        a = price(sym, ms - s_min * MIN); b = price(sym, ms - e_min * MIN)
        return mult * np.sign(b / a - 1)
    return f


def vs_ref(sym, ref_ms, e_min, mult):
    """side = mult * sign(p(t - e) / p(ref_i) - 1); ref fixed per candidate."""
    if R24READ:
        e_min = 0
    ref_ms = np.asarray(ref_ms, dtype=np.int64)

    def f(ms, idx):
        a = price(sym, ref_ms[idx]); b = price(sym, ms - e_min * MIN)
        return mult * np.sign(b / a - 1)
    return f


def mk(id_, sym, ms_in, ms_out, side_fn, ctrl="time", **kw):
    d = dict(id=id_, sym=sym, ms_in=np.asarray(ms_in, dtype=np.int64), ms_out=np.asarray(ms_out, dtype=np.int64),
             side_fn=side_fn, ctrl=ctrl)
    d.update(kw)
    return d


def wk(filter_=lambda d: True):
    return [d for d in bdays(D0, D1) if filter_(d)]


def clock_rule(id_, sym, days, a, b, tz, side, ctrl="time"):
    ms_in = [loc_ms(d, *a, tz) for d in days]; ms_out = [loc_ms(d, *b, tz) for d in days]
    return mk(id_, sym, ms_in, ms_out, fixed(side), ctrl)


# ---------------------------------------------------------------- FX (ECN)
def F2():
    return clock_rule("F2", "EURUSD", wk(lambda d: not xmas(d)), (4, 0), (8, 0), "NY", -1)


def F4():
    return clock_rule("F4", "EURUSD", wk(lambda d: not xmas(d) and d not in XECB), (12, 45), (13, 0), "LON", -1)


def F7():
    return clock_rule("F7", "USDCHF", wk(lambda d: not xmas(d)), (10, 0), (12, 0), "UTC", +1)


def F8():
    days = wk(lambda d: not xmas(d))
    sig = np.log(price("USDCHF", [loc_ms(d, 10 if R24READ else 9, 0 if R24READ else 59, "UTC") for d in days]) /
                 price("USDCHF", [loc_ms(d, 6, 0, "UTC") for d in days]))
    keep = []
    for i, d in enumerate(days):
        h = sig[max(0, i - 250):i]; h = h[~np.isnan(h)]
        if len(h) >= 60 and not np.isnan(sig[i]) and sig[i] >= np.percentile(h, 67):
            keep.append(d)
    r = clock_rule("F8", "USDCHF", keep, (10, 0), (12, 0), "UTC", +1, ctrl="fwd")
    return r


def F9():
    return clock_rule("F9", "USDCHF", wk(lambda d: not xmas(d)), (8, 0), (8, 30), "NY", -1)


def F10():
    return clock_rule("F10", "USDJPY", wk(lambda d: not xmas(d)), (11, 0), (13, 0), "LON", +1)


def F11():
    return clock_rule("F11", "EURJPY", wk(lambda d: not xmas(d)), (11, 0), (13, 0), "LON", -1)


def _noroll(r):
    bad = eng.in_roll(r["ms_in"], r["ms_out"])
    r["ms_in"] = r["ms_in"][~bad]; r["ms_out"] = r["ms_out"][~bad]
    return r


def F12():
    return _noroll(clock_rule("F12", "GBPJPY", wk(lambda d: not xmas(d)), (17, 30), (21, 30), "LON", +1))


def F13():
    return _noroll(clock_rule("F13", "GBPJPY", wk(lambda d: not xmas(d)), (2, 45), (6, 45), "SYD", +1))


def F14():
    return clock_rule("F14", "EURJPY", wk(lambda d: not xmas(d)), (16, 0), (20, 0), "LON", +1)


def _last_wkday(y, m):
    d = (dt.date(y, m, 28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def F15():
    ev = [_last_wkday(y, m) for y in range(2016, 2025) for m in (3, 6, 9)]
    r = clock_rule("F15", "EURJPY", ev, (5, 0), (7, 0), "LON", -1, ctrl="day")
    r["clock"] = ((5, 0), (7, 0), "LON"); r["events"] = set(ev)
    r["pool"] = wk(lambda d: not xmas(d) and d not in set(ev))
    return r


def F16():
    ev = [d for d in (_last_wkday(y, m) for y in range(2016, 2025) for m in range(1, 13)) if not xmas(d)]
    r = clock_rule("F16", "GBPUSD", ev, (15, 0), (16, 0), "LON", +1, ctrl="day")
    r["clock"] = ((15, 0), (16, 0), "LON"); r["events"] = set(ev)
    r["pool"] = wk(lambda d: not xmas(d) and d not in set(ev))
    return r


def F23():
    return clock_rule("F23", "USDCNH", wk(lambda d: not xmas(d)), (1, 30), (8, 30), "UTC", +1)


def F24():
    return clock_rule("F24", "USDJPY", wk(lambda d: not xmas(d)), (7, 45), (8, 0), "UTC", +1)


# ---------------------------------------------------------------- gold (GC)
def _xshg_days():
    return wk(lambda d: d not in XSHG and d >= dt.date(2016, 4, 19))


def M2():
    days = _xshg_days()
    prev = [None] + days[:-1]
    sig = np.array([np.nan if p is None else float(np.log(price("XAUUSD", [loc_ms(d, 2, 0, "UTC")])[0] /
                                                           price("XAUUSD", [loc_ms(p, 7, 0, "UTC")])[0]))
                    for d, p in zip(days, prev)])
    keep = []
    for i, d in enumerate(days):
        h = sig[max(0, i - 250):i]; h = h[~np.isnan(h)]
        if len(h) >= 60 and not np.isnan(sig[i]) and sig[i] <= np.percentile(h, 20):
            keep.append(d)
    return clock_rule("M2", "XAUUSD", keep, (2, 15), (2, 23), "UTC", +1, ctrl="fwd")


def M4():
    days = _xshg_days()
    return mk("M4", "XAUUSD", [loc_ms(d, 7, 0, "UTC") for d in days], [loc_ms(d, 7, 30, "UTC") for d in days],
              rel("XAUUSD", 30, 1, -1))


def _nyse(full=True, x2=False):
    return wk(lambda d: d not in XNYS and (not full or d not in EARLY) and (not x2 or not xmas(d, 2)))


def M7():
    days = _nyse(full=False)
    ref = [loc_ms(p, 13, 30, "NY") for p in [None] + days[:-1] if p is not None]
    days = days[1:]
    return mk("M7", "XAUUSD", [loc_ms(d, 13, 25, "NY") for d in days], [loc_ms(d, 13, 30, "NY") for d in days],
              vs_ref("XAUUSD", ref, 1, +1))


def M11():
    days = wk(lambda d: d not in XNYS and not xmas(d, 2))
    return mk("M11", "XAUUSD", [loc_ms(d, 8, 20, "NY") for d in days], [loc_ms(d, 8, 30, "NY") for d in days],
              rel("XAUUSD", 10, 1, -1))


def M12():
    allb = bdays(dt.date(2015, 12, 1), dt.date(2025, 1, 31))
    ev = set()
    for h in sorted(ENG):
        if h.weekday() >= 5 or not (D0 <= h <= D1):
            continue
        d = h - dt.timedelta(days=1)
        while d.weekday() >= 5 or d in ENG:
            d -= dt.timedelta(days=1)
        if not xmas(d) and not xmas(h) and D0 <= d:
            ev.add(d)
    ev = sorted(ev)
    r = clock_rule("M12", "XAUUSD", ev, (2, 0), (6, 0), "UTC", +1, ctrl="day")
    r["clock"] = ((2, 0), (6, 0), "UTC"); r["events"] = set(ev)
    r["pool"] = wk(lambda d: not xmas(d) and d not in set(ev))
    return r


# ---------------------------------------------------------------- indices (futures)
def I1():
    days = _nyse(x2=True)
    return mk("I1", "USTEC", [loc_ms(d, 15, 52, "NY") for d in days], [loc_ms(d, 16, 0, "NY") for d in days],
              rel("USTEC", 2, 1, +1))


def I3():
    days = _nyse(x2=True)
    return mk("I3", "US30", [loc_ms(d, 16, 4, "NY") for d in days], [loc_ms(d, 16, 14, "NY") for d in days],
              rel("US30", 10, 1, -1))


def I4():
    days = _nyse(x2=True)
    return mk("I4", "US500", [loc_ms(d, 9, 41, "NY") for d in days], [loc_ms(d, 9, 51, "NY") for d in days],
              rel("US500", 10, 1, -1))


def I5():
    days = wk(lambda d: d not in ENG and not xmas(d, 2))
    return mk("I5", "UK100", [loc_ms(d, 16, 34, "LON") for d in days], [loc_ms(d, 16, 39, "LON") for d in days],
              rel("UK100", 10, 1, -1))


def I6():
    nsw = holidays.AU(subdiv="NSW", years=YRS)
    days = wk(lambda d: d not in nsw and not xmas(d, 2))
    return mk("I6", "AUS200", [loc_ms(d, 16, 13, "SYD") for d in days], [loc_ms(d, 16, 30, "SYD") for d in days],
              rel("AUS200", 13, 1, -1))


def I8():
    days = wk(lambda d: not xmas(d, 2))
    prev = [d - dt.timedelta(days=3 if d.weekday() == 0 else 1) for d in days]
    return mk("I8", "HK50", [loc_ms(d, 9, 30, "HK") for d in days], [loc_ms(d, 9, 31, "HK") for d in days],
              vs_ref("HK50", [loc_ms(p, 16, 0, "HK") for p in prev], 1, -1))


def I10():
    days = wk(lambda d: not (d.month == 12 and d.day in (24, 31)))
    prev = [d - dt.timedelta(days=3 if d.weekday() == 0 else 1) for d in days]
    return mk("I10", "DE40", [loc_ms(d, 17, 25, "CET") for d in days], [loc_ms(d, 17, 35, "CET") for d in days],
              vs_ref("DE40", [loc_ms(p, 17, 35, "CET") for p in prev], 1, +1))


def I13():
    days = _nyse()
    nxt = {}
    alld = [d for d in bdays(D0, dt.date(2025, 1, 10)) if d not in XNYS]
    for a, b in zip(alld[:-1], alld[1:]):
        nxt[a] = b
    days = [d for d in days if d in nxt and nxt[d] <= D1]
    ms_in = [loc_ms(d, 16, 0, "NY") for d in days]; ms_out = [loc_ms(nxt[d], 9, 30, "NY") for d in days]
    # futures carry (r - q) dt, r = Fed funds (DFF, last value on or before the entry date), q = 1.5 %
    import csv
    rows = list(csv.reader(open("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/rates/DFF.csv")))
    dff = {}
    for r_ in rows[1:]:
        try:
            dff[dt.date.fromisoformat(r_[0])] = float(r_[1])
        except ValueError:
            pass
    ks = sorted(dff)
    import bisect
    carry = []
    for d, a, b in zip(days, ms_in, ms_out):
        j = bisect.bisect_right(ks, d) - 1
        r = dff[ks[j]] if j >= 0 else 0.0
        carry.append((r - 1.5) / 100 * (b - a) / (365.25 * 86400000) * 1e4)
    return mk("I13", "US500", ms_in, ms_out, fixed(+1), carry=np.array(carry))


# ---------------------------------------------------------------- oil, BTC
def _us_oil_days():
    return [d for d in bdays(dt.date(2018, 1, 1), D1) if d not in USF]


def E1x():
    days = _us_oil_days()
    prev = [d - dt.timedelta(days=3 if d.weekday() == 0 else 1) for d in days]
    return mk("E1x", "XTIUSD", [loc_ms(d, 14, 15, "NY") for d in days], [loc_ms(d, 14, 30, "NY") for d in days],
              vs_ref("XTIUSD", [loc_ms(p, 14, 30, "NY") for p in prev], 1, +1))


def E2x():
    days = _us_oil_days()
    return mk("E2x", "XTIUSD", [loc_ms(d, 14, 30, "NY") for d in days], [loc_ms(d, 14, 31, "NY") for d in days],
              rel("XTIUSD", 10, 1, -1))


def C1():
    days = [D0 + dt.timedelta(days=i) for i in range((D1 - D0).days + 1)]
    return mk("C1", "BTCUSD", [loc_ms(d, 23, 30, "UTC") for d in days],
              [loc_ms(d, 23, 30, "UTC") + 30 * MIN for d in days],
              vs_ref("BTCUSD", [loc_ms(d, 0, 0, "UTC") for d in days], 1, +1))


SINGLE = [F2, F4, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16, F23, F24, M2, M4, M7, M11, M12,
          I1, I3, I4, I5, I6, I8, I10, I13, E1x, E2x, C1]
CONTAM = {"F2", "F4", "M7", "I1"}
SEL = {"F2": "PRE", "F4": "PRE", "F7": "PRE", "F8": "decl", "F9": "PRE", "F10": "PRE", "F11": "PRE", "F12": "PRE",
       "F13": "PRE", "F14": "PRE", "F15": "PRE", "F16": "PRE", "F23": "lit", "F24": "decl*", "M2": "decl",
       "M4": "decl", "M7": "lit", "M11": "decl", "M12": "PRE", "I1": "decl", "I3": "decl", "I4": "decl",
       "I5": "decl", "I6": "decl", "I8": "decl", "I10": "decl", "I13": "lit", "E1x": "lit", "E2x": "decl",
       "C1": "lit", "N1a": "lit", "N1b": "lit", "N1c": "lit"}
