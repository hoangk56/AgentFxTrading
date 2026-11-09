"""Independent re-implementation of kienphan/AgentFxTrading cBot/OrbRE2Bot.cs (upstream 94901a1) on the IC tick cache.

Follows the gate order of TryEnterOnTick exactly: level-based trigger on the bid, whipsaw memory recorded only once
the range is final and the entry delay has passed, trend = bid vs EMA of closed D1 bars, one trade per session,
SL = max(k x ATR(D-1), MinSl), TP = R x SL measured from the fill, flatten at EOD.

Usage: orb_re2_sim.py OUT.json [tick|m1] SYMBOL ...
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

REPO = Path.home() / "00.code_base/105.AgentFxTrading"
sys.path.insert(0, str(REPO))
from research.m1 import load as load_m1  # noqa: E402
from research.m1bars import resample  # noqa: E402
from research.ticks import DATA_DIR, decode_day, _ffill, PRICE_SCALE  # noqa: E402
from research.specs import SPECS  # noqa: E402

MIN = 60_000
H = 3_600_000


@dataclass(frozen=True)
class Cfg:
    name: str
    open_h: int = 13
    open_m: int = 0
    dst: str = "US"            # US / Europe / None
    or_min: int = 15
    eod_h: int = 21
    eod_m: int = 0
    chart_min: int = 15        # the range is final only when the first bar past the window has closed
    delay: int = 0             # EntryDelayMinutes
    max_entry: int = 180
    min_or_pips: float = 20.0
    buffer_pips: float = 0.5
    trend: bool = True
    whipsaw: bool = True
    record_from_or_end: bool = False  # fix under test: whipsaw memory also sees the blind minutes
    atr_mult: float = 0.5
    min_sl_pips: float = 10.0
    tp_r: float = 2.0
    max_spread_pips: float = 50.0
    max_overshoot_r: float = 0.0      # fix under test: refuse a fill further than this from the trigger (0 = off)
    flip: bool = False                # placebo: same entry tick, opposite direction


def nth_sunday(y, m, n):
    d = date(y, m, 1)
    return d + timedelta(days=(6 - d.weekday()) % 7 + (n - 1) * 7)


def last_sunday(y, m):
    d = (date(y, m, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() + 1) % 7)


def is_dst(rule, d):
    if rule == "US":
        return nth_sunday(d.year, 3, 2) <= d < nth_sunday(d.year, 11, 1)
    if rule == "Europe":
        return last_sunday(d.year, 3) <= d < last_sunday(d.year, 10)
    return False


def adj(rule, d, winter_h):
    if rule == "None" or winter_h == 0:
        return winter_h
    return (winter_h - 1) % 24 if is_dst(rule, d) else winter_h


def ms(d):
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)


def daily_context(symbol):
    """For each UTC date: (EMA10, ATR14) from D1 bars closed before that date's forming bar (22:00 UTC roll)."""
    m = load_m1(symbol)
    d1 = resample(m, 1440, 120)
    keep = (d1.last - d1.first + 1) >= 120       # drop the Friday / holiday stubs of a few minutes
    t, hi, lo, c = d1.t[keep], d1.h[keep], d1.l[keep], d1.c[keep]
    a = 2.0 / 11.0
    ema = np.full(len(c), np.nan)
    if len(c) >= 10:
        ema[9] = c[:10].mean()
        for i in range(10, len(c)):
            ema[i] = (c[i] - ema[i - 1]) * a + ema[i - 1]
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.c_[hi - lo, np.abs(hi - pc), np.abs(lo - pc)], axis=1)
    atr = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        atr[i] = tr[i - 13:i + 1].mean()
    close_t = t + 1440 * MIN
    return close_t, ema, atr


def ticks_of_day(symbol, d):
    path = DATA_DIR / symbol / "t1" / f"{d:%Y%m%d}.zticks"
    if not path.exists():
        return None
    r = decode_day(path)
    b, a = _ffill(r[:, 1]), _ffill(r[:, 2])
    k = (b != 0) & (a != 0)
    return r[k, 0], b[k] / PRICE_SCALE, a[k] / PRICE_SCALE


class M1Days:
    """M1 bars as four pseudo ticks per minute (O, then low/high by the bar's colour, then C); ask = bid + mean spread."""

    def __init__(self, symbol):
        self.m = load_m1(symbol)

    def day(self, d):
        m, s = self.m, ms(d)
        i, j = np.searchsorted(m["ts"], [s, s + 24 * H])
        if i == j:
            return None
        o, h, l, c, sp, t = m["o"][i:j], m["h"][i:j], m["l"][i:j], m["c"][i:j], m["smean"][i:j], m["ts"][i:j]
        up = c >= o
        p2, p3 = np.where(up, l, h), np.where(up, h, l)
        bid = np.c_[o, p2, p3, c].ravel()
        ts = np.c_[t, t + 15_000, t + 30_000, t + 59_000].ravel()
        return ts, bid, bid + np.repeat(sp, 4)


def simulate(cfg, d, ts, bid, ask, ema, atr, spec):
    """One session. Returns a trade dict or None."""
    pip = spec.pip
    open_t = ms(d) + adj(cfg.dst, d, cfg.open_h) * H + cfg.open_m * MIN
    or_end = open_t + cfg.or_min * MIN
    eod = ms(d) + adj(cfg.dst, d, cfg.eod_h) * H + cfg.eod_m * MIN

    i0, i1 = np.searchsorted(ts, [open_t, or_end])
    if i1 <= i0:
        return None
    or_hi, or_lo = bid[i0:i1].max(), bid[i0:i1].min()
    if (or_hi - or_lo) / pip < cfg.min_or_pips:
        return None
    if not np.isfinite(atr) or atr <= 0 or (cfg.trend and not np.isfinite(ema)):
        return None

    start = or_end + max(cfg.chart_min * MIN, cfg.delay * MIN)
    stop = min(eod, open_t + cfg.max_entry * MIN)
    w0, w1 = np.searchsorted(ts, [or_end if cfg.record_from_or_end else start, stop])
    if w1 <= w0:
        return None

    b, a, t = bid[w0:w1], ask[w0:w1], ts[w0:w1]
    lt = or_hi + cfg.buffer_pips * pip
    st = or_lo - cfg.buffer_pips * pip
    live = t >= start
    spr_ok = (a - b) / pip <= cfg.max_spread_pips
    brk_l, brk_s = b >= lt, b <= st
    up = b > ema if cfg.trend else np.ones(len(b), bool)
    dn = b < ema if cfg.trend else np.ones(len(b), bool)
    ok_l = brk_l & up & spr_ok & live
    ok_s = brk_s & dn & spr_ok & live

    n = len(b)
    if cfg.whipsaw:
        fl = int(np.argmax(brk_l)) if brk_l.any() else n
        fs = int(np.argmax(brk_s)) if brk_s.any() else n
        if fl == n and fs == n:
            return None
        # After the first reverse break both sides are dead: the later side sees the earlier one, and the earlier
        # side is refused from then on.
        if fl < fs:
            idx = np.flatnonzero(ok_l[fl:fs])
            j, side = (fl + int(idx[0]), 1) if idx.size else (n, 0)
        else:
            idx = np.flatnonzero(ok_s[fs:fl])
            j, side = (fs + int(idx[0]), -1) if idx.size else (n, 0)
        if j == n:
            return None
    else:
        jl = int(np.argmax(ok_l)) if ok_l.any() else n
        js = int(np.argmax(ok_s)) if ok_s.any() else n
        j = min(jl, js)
        if j == n:
            return None
        side = 1 if jl <= js else -1

    sl = max(atr * cfg.atr_mult, cfg.min_sl_pips * pip)
    trigger = lt if side > 0 else st
    overshoot = (b[j] - trigger) * side / sl
    if cfg.max_overshoot_r > 0 and overshoot > cfg.max_overshoot_r:
        return None

    k = w0 + j
    tside = -side if cfg.flip else side
    entry = ask[k] if tside > 0 else bid[k]
    sl_px, tp_px = entry - tside * sl, entry + tside * sl * cfg.tp_r
    e = int(np.searchsorted(ts, eod))
    if tside > 0:
        px = bid[k + 1:e]
        hit = np.flatnonzero((px <= sl_px) | (px >= tp_px))
    else:
        px = ask[k + 1:e]
        hit = np.flatnonzero((px >= sl_px) | (px <= tp_px))
    if hit.size:
        q = k + 1 + int(hit[0])
        x = bid[q] if tside > 0 else ask[q]
        why = "sl" if (x - entry) * tside < 0 else "tp"
    else:
        q = min(e, len(ts) - 1)
        x = bid[q] if tside > 0 else ask[q]
        why = "eod"
    comm = spec.comm_per_unit / spec.usd_per_quote
    pnl = (x - entry) * tside - comm
    return dict(date=d.isoformat(), side=tside, entry_t=int(ts[k]), mins_after_or=(int(ts[k]) - or_end) / MIN,
                sl=float(sl), r=float(pnl / sl), pnl_px=float(pnl), why=why, overshoot=float(overshoot),
                spread=float(ask[k] - bid[k]), atr=float(atr))


def run_symbol(job):
    symbol, mode, cfgs = job
    spec = SPECS[symbol]
    close_t, ema, atr = daily_context(symbol)
    source = M1Days(symbol) if mode == "m1" else None
    out = {c.name: [] for c in cfgs}
    sessions = {c.name: 0 for c in cfgs}
    d = date(2016, 3, 1)
    while d <= date(2026, 9, 24):
        if d.weekday() < 5:
            data = source.day(d) if source else ticks_of_day(symbol, d)
            if data is not None and len(data[0]):
                ts, bid, ask = data
                # the forming bar at the session roll opened at D-1 22:00, so closed bars end at or before it
                pos = int(np.searchsorted(close_t, ms(d) - 2 * H, side="right")) - 1
                e, a = (ema[pos], atr[pos]) if pos >= 0 else (np.nan, np.nan)
                for c in cfgs:
                    sessions[c.name] += 1
                    tr = simulate(c, d, ts, bid, ask, e, a, spec)
                    if tr:
                        out[c.name].append(tr)
        d += timedelta(days=1)
    return symbol, mode, out, sessions


def grid(symbol):
    base = {
        "XAUUSD": Cfg("base", open_h=13, dst="US", eod_h=21, delay=30),
        "USTEC": Cfg("base", open_h=14, open_m=30, dst="US", eod_h=21, delay=30),
        "US30": Cfg("base", open_h=14, open_m=30, dst="US", eod_h=21, delay=0),
        "DE40": Cfg("base", open_h=8, dst="Europe", eod_h=16, eod_m=30, delay=0),
        "GBPJPY": Cfg("base", open_h=0, dst="None", eod_h=9, delay=0),
    }[symbol]
    v = [base]
    for dl in (0, 30, 45, 60, 90):
        v.append(replace(base, name=f"delay{dl}", delay=dl))
    v.append(replace(base, name="delay_true0", delay=0, chart_min=1))
    v.append(replace(base, name="no_trend", trend=False))
    v.append(replace(base, name="no_whipsaw", whipsaw=False))
    v.append(replace(base, name="no_filters", trend=False, whipsaw=False))
    v.append(replace(base, name="flip", flip=True))
    v.append(replace(base, name="whipsaw_sees_blind", record_from_or_end=True))
    v.append(replace(base, name="cap_overshoot_025", max_overshoot_r=0.25))
    for k in (0.25, 1.0):
        v.append(replace(base, name=f"sl{k}", atr_mult=k))
    for r in (1.0, 3.0):
        v.append(replace(base, name=f"tp{r:g}", tp_r=r))
    if symbol == "XAUUSD":
        for nm, h, m, dst, eod in (("sess_london", 8, 0, "Europe", 16), ("sess_cash", 14, 30, "US", 21)):
            v.append(replace(base, name=nm, open_h=h, open_m=m, dst=dst, eod_h=eod))
    return v


if __name__ == "__main__":
    out_path, mode, *symbols = sys.argv[1:]
    jobs = [(s, mode, grid(s)) for s in symbols]
    res = {}
    with ProcessPoolExecutor(max_workers=min(5, len(jobs))) as ex:
        for symbol, md, trades, sess in ex.map(run_symbol, jobs):
            res[f"{symbol}|{md}"] = {"trades": trades, "sessions": sess,
                                     "cfg": {c.name: asdict(c) for c in grid(symbol)}}
            print(symbol, md, {k: len(v) for k, v in list(trades.items())[:2]}, flush=True)
    Path(out_path).write_text(json.dumps(res))
