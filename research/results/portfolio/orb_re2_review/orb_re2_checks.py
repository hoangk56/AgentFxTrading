"""Sanity traces, D1-roll sensitivity, always-in benchmark, USTEC delay0 split, 23-session odds."""
import json
import sys
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, ".")
import orb_re2_sim as S  # noqa: E402


def stat(r):
    r = np.asarray(r)
    if len(r) < 2:
        return f"n {len(r)}"
    g, l = r[r > 0].sum(), -r[r < 0].sum()
    return (f"n {len(r)} win {100 * (r > 0).mean():.1f}% avg {r.mean():+.3f} t "
            f"{r.mean() / r.std(ddof=1) * np.sqrt(len(r)):+.2f} PF {g / l:.2f} tot {r.sum():+.1f}")


def utc(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def daily_ctx_offset(symbol, offset):
    """Same as S.daily_context with another D1 roll, to measure how much the assumed roll matters."""
    orig = S.resample
    S.resample = lambda m, minutes, _o: orig(m, minutes, offset)
    try:
        return S.daily_context(symbol)
    finally:
        S.resample = orig


def trace(symbol, cfg, days):
    close_t, ema, atr = S.daily_context(symbol)
    spec = S.SPECS[symbol]
    for d in days:
        ts, bid, ask = S.ticks_of_day(symbol, d)
        pos = int(np.searchsorted(close_t, S.ms(d) - 2 * S.H, side="right")) - 1
        tr = S.simulate(cfg, d, ts, bid, ask, ema[pos], atr[pos], spec)
        open_t = S.ms(d) + S.adj(cfg.dst, d, cfg.open_h) * S.H + cfg.open_m * S.MIN
        or_end = open_t + cfg.or_min * S.MIN
        i, j = np.searchsorted(ts, [open_t, or_end])
        hi, lo = bid[i:j].max(), bid[i:j].min()
        start = or_end + max(cfg.chart_min, cfg.delay) * S.MIN
        s = int(np.searchsorted(ts, start))
        print(f"\n{symbol} {d} open {utc(open_t)} OR [{lo:.2f},{hi:.2f}] live from {utc(start)} first bid {bid[s]:.2f} "
              f"EMA {ema[pos]:.2f} ATR {atr[pos]:.2f} D1 closed {utc(int(close_t[pos]))}")
        if not tr:
            print("  no trade")
            continue
        k = int(np.searchsorted(ts, tr["entry_t"]))
        sign = tr["side"]
        entry = ask[k] if sign > 0 else bid[k]
        sl_px = entry - sign * tr["sl"]
        tp_px = entry + sign * tr["sl"] * cfg.tp_r
        print(f"  {'LONG' if sign > 0 else 'SHORT'} {utc(tr['entry_t'])} bid {bid[k]:.2f} ask {ask[k]:.2f} SL {sl_px:.2f} "
              f"TP {tp_px:.2f} -> {tr['why']} R {tr['r']:+.3f} overshoot {tr['overshoot']:.3f}")
        # independent brute-force scan of the exit on raw ticks
        for q in range(k + 1, len(ts)):
            if ts[q] >= S.ms(d) + S.adj(cfg.dst, d, cfg.eod_h) * S.H + cfg.eod_m * S.MIN:
                x, why = (bid[q] if sign > 0 else ask[q]), "eod"
                break
            px = bid[q] if sign > 0 else ask[q]
            if (px - sl_px) * sign <= 0:
                x, why = px, "sl"
                break
            if (px - tp_px) * sign >= 0:
                x, why = px, "tp"
                break
        comm = spec.comm_per_unit / spec.usd_per_quote
        print(f"  brute force exit {why} at {utc(int(ts[q]))} px {x:.2f} R {((x - entry) * sign - comm) / tr['sl']:+.3f}")


def run_days(symbol, cfgs, ctx=None, sides=None):
    close_t, ema, atr = ctx or S.daily_context(symbol)
    spec = S.SPECS[symbol]
    out = {c.name: [] for c in cfgs}
    d = date(2016, 3, 1)
    while d <= date(2026, 9, 24):
        if d.weekday() < 5:
            data = S.ticks_of_day(symbol, d)
            if data is not None and len(data[0]):
                ts, bid, ask = data
                pos = int(np.searchsorted(close_t, S.ms(d) - 2 * S.H, side="right")) - 1
                if pos >= 0:
                    for c in cfgs:
                        tr = S.simulate(c, d, ts, bid, ask, ema[pos], atr[pos], spec)
                        if tr:
                            out[c.name].append(tr)
        d += timedelta(days=1)
    return out


def always_in(symbol, cfg):
    """Benchmark: no range at all. Enter at the first tick of the bot's live window with the D1 trend (or long only),
    same stop, target and EOD. If the bot does not beat this, the break adds nothing beyond drift / trend."""
    close_t, ema, atr = S.daily_context(symbol)
    spec = S.SPECS[symbol]
    out = {"always_long": [], "always_with_trend": []}
    d = date(2016, 3, 1)
    comm = spec.comm_per_unit / spec.usd_per_quote
    while d <= date(2026, 9, 24):
        if d.weekday() < 5:
            data = S.ticks_of_day(symbol, d)
            if data is not None and len(data[0]):
                ts, bid, ask = data
                pos = int(np.searchsorted(close_t, S.ms(d) - 2 * S.H, side="right")) - 1
                if pos >= 0 and np.isfinite(atr[pos]) and np.isfinite(ema[pos]):
                    open_t = S.ms(d) + S.adj(cfg.dst, d, cfg.open_h) * S.H + cfg.open_m * S.MIN
                    start = open_t + cfg.or_min * S.MIN + max(cfg.chart_min, cfg.delay) * S.MIN
                    eod = S.ms(d) + S.adj(cfg.dst, d, cfg.eod_h) * S.H + cfg.eod_m * S.MIN
                    k, e = np.searchsorted(ts, [start, eod])
                    if k < e:
                        sl = max(atr[pos] * cfg.atr_mult, cfg.min_sl_pips * spec.pip)
                        for name, side in (("always_long", 1), ("always_with_trend", 1 if bid[k] > ema[pos] else -1)):
                            entry = ask[k] if side > 0 else bid[k]
                            px = (bid if side > 0 else ask)[k + 1:e]
                            a, b = entry - side * sl, entry + side * sl * cfg.tp_r
                            hit = np.flatnonzero(((px - a) * side <= 0) | ((px - b) * side >= 0))
                            q = k + 1 + int(hit[0]) if hit.size else min(e, len(ts) - 1)
                            x = (bid if side > 0 else ask)[q]
                            out[name].append(((x - entry) * side - comm) / sl)
        d += timedelta(days=1)
    return out


def rolling_odds(trades, targets):
    r_by = {x["date"]: x["r"] for x in trades}
    a, b = date.fromisoformat(trades[0]["date"]), date.fromisoformat(trades[-1]["date"])
    cal = [a + timedelta(days=i) for i in range((b - a).days + 1)]
    v = np.array([r_by.get(d.isoformat(), 0.0) for d in cal if d.weekday() < 5])
    tot = np.convolve(v, np.ones(23), "valid")
    return {t: round(float((tot >= t).mean() * 100), 1) for t in targets}


if __name__ == "__main__":
    base = {g.name: g for g in S.grid("XAUUSD")}["base"]
    trace("XAUUSD", base, [date(2026, 9, 15), date(2026, 9, 16), date(2024, 5, 8)])
    ust = {g.name: g for g in S.grid("USTEC")}["base"]
    trace("USTEC", replace(ust, delay=0), [date(2026, 9, 15), date(2025, 3, 11)])

    print("\n=== D1 roll sensitivity (base, tick): 22:00 UTC vs 00:00 UTC vs 21:00 UTC")
    for sym in ("XAUUSD", "US30", "USTEC"):
        b = {g.name: g for g in S.grid(sym)}["base"]
        print(sym, "22:00", stat([x["r"] for x in run_days(sym, [b])["base"]]))
        for lab, off in (("00:00", 0), ("21:00", 180)):
            print(sym, lab, stat([x["r"] for x in run_days(sym, [b], ctx=daily_ctx_offset(sym, off))["base"]]))

    print("\n=== Benchmarks without any range (tick)")
    for sym in ("XAUUSD", "US30", "USTEC"):
        for dl in (0, 30):
            b = {g.name: g for g in S.grid(sym)}["base"]
            b = replace(b, delay=dl)
            res = always_in(sym, b)
            print(sym, f"delay{dl}", {k: stat(v) for k, v in res.items()})

    print("\n=== USTEC delay0 split")
    u0 = replace(ust, name="d0", delay=0)
    uf = replace(ust, name="d0flip", delay=0, flip=True)
    res = run_days("USTEC", [u0, uf])
    t = res["d0"]
    r = [x["r"] for x in t]
    print("all", stat(r), "| flip", stat([x["r"] for x in res["d0flip"]]))
    for s in (1, -1):
        print("side", s, stat([x["r"] for x in t if x["side"] == s]))
    for y in range(2016, 2027):
        print(y, stat([x["r"] for x in t if x["date"][:4] == str(y)]))
    for lo, hi in (("2016", "2020"), ("2021", "2024"), ("2025", "2027")):
        print(lo, hi, stat([x["r"] for x in t if lo <= x["date"][:4] < hi]))

    print("\n=== Odds of a 23-session total at or above X R under the base config (tick)")
    data = json.loads(open("tick.json").read())
    for sym in ("XAUUSD", "US30", "USTEC"):
        print(sym, rolling_odds(data[f"{sym}|tick"]["trades"]["base"], [2, 3, 4, 5, 6, 8]))
    x = data["XAUUSD|tick"]["trades"]["base"]
    print("XAU stop in $/0.1 lot: last 20 trades mean", round(np.mean([t["sl"] for t in x[-20:]]) * 10), "2025+ mean",
          round(np.mean([t["sl"] for t in x if t["date"] >= "2025"]) * 10))
