"""Shared pieces of the canonical strategies of the 2026-09-26 refresh
(docs/superpowers/specs/2026-09-26-strategy-refresh-design.md): local clock times, the TMS+ORB session table, the
TMS lines, M5 swing points and fair value gaps, tick breakouts, and one position with a stop, a target and a time
exit."""
import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Callable, Iterator, Optional
from zoneinfo import ZoneInfo

import numpy as np

from research.indicators import heikin_ashi, stoch, tdi
from research.lab.engine import NAN, Ctx, Trade
from research.sim import _first_hit

NY, LONDON, TOKYO, BERLIN = "America/New_York", "Europe/London", "Asia/Tokyo", "Europe/Berlin"
MINUTE_MS = 60_000
# group: (time zone, opening-range start, session end), local times
ORB_SESSIONS = {"tokyo": (TOKYO, time(9, 0), time(15, 0)),
                "london": (LONDON, time(8, 0), time(16, 30)),
                "frankfurt": (BERLIN, time(9, 0), time(17, 30)),
                "newyork_fx": (NY, time(8, 0), time(16, 0)),
                "newyork_cash": (NY, time(9, 30), time(16, 0))}
ORB_GROUP = {**dict.fromkeys(("USDJPY", "AUDJPY", "AUDUSD", "CADJPY", "AUDCAD"), "tokyo"),
             **dict.fromkeys(("EURUSD", "GBPUSD", "EURJPY", "GBPJPY", "EURGBP", "EURAUD", "GBPAUD", "EURCAD",
                              "GBPCAD", "UK100"), "london"),
             "DE40": "frankfurt", "USDCAD": "newyork_fx", "XAUUSD": "newyork_fx",
             **dict.fromkeys(("US30", "USTEC", "BTCUSD", "ETHUSD"), "newyork_cash")}
OR_MINUTES, ORB_WINDOW_MINUTES, MIN_RANGE_SPREADS = 15, 180, 3.0


def local_ms(d: date, t: time, tz: str) -> int:
    return int(datetime.combine(d, t, ZoneInfo(tz)).timestamp() * 1000)


def chunk_days(ctx: Ctx, before: int = 2) -> Iterator[date]:
    """UTC calendar dates from `before` days ahead of the chunk's entry window to the day after it ends."""
    d = datetime.fromtimestamp(ctx.ch.lo_ms / 1000, timezone.utc).date() - timedelta(days=before)
    last = datetime.fromtimestamp(ctx.ch.hi_ms / 1000, timezone.utc).date() + timedelta(days=1)
    while d <= last:
        yield d
        d += timedelta(days=1)


@dataclass
class Tms:
    """TMS (Trading Made Simple) lines on one timeframe: TDI green/red, Heiken Ashi colour, Stoch direction."""
    close_time: np.ndarray
    green: np.ndarray
    red: np.ndarray
    ha_dir: np.ndarray      # +1 bullish HA bar, -1 bearish, 0 doji
    stoch_dir: np.ndarray   # +1 slow %K above %D, -1 below, 0 equal or not warm

    @classmethod
    def of(cls, b) -> "Tms":
        green, red = tdi(b.c)
        ho, hc = heikin_ashi(b.o, b.h, b.l, b.c)
        k, d = stoch(b.h, b.l, b.c)
        with np.errstate(invalid="ignore"):
            sd = np.nan_to_num(np.sign(k - d))
        return cls(b.close_time, green, red, np.sign(hc - ho).astype(int), sd.astype(int))

    def state(self) -> np.ndarray:
        """Per bar: +1 bull (green > red, green > 50, HA bullish), -1 bear (mirrored), 0 otherwise."""
        g, r = self.green, self.red
        with np.errstate(invalid="ignore"):
            bull = (g > r) & (g > 50) & (self.ha_dir > 0)
            bear = (g < r) & (g < 50) & (self.ha_dir < 0)
        return bull.astype(int) - bear.astype(int)

    def last_closed(self, ms: int) -> int:
        """Index of the last bar closed at ms; -1 if none."""
        return int(np.searchsorted(self.close_time, ms, side="right")) - 1

    def first_against(self, after_ms: int, side: int) -> int:
        """close_time of the first bar closing after after_ms with green crossed against `side` (a long: green <
        red); 0 if none."""
        i = int(np.searchsorted(self.close_time, after_ms, side="right"))
        with np.errstate(invalid="ignore"):
            hit = np.flatnonzero((self.green[i:] - self.red[i:]) * side < 0)
        return int(self.close_time[i + hit[0]]) if hit.size else 0


def fractal_lows(l: np.ndarray) -> np.ndarray:
    """True at k when l[k] is below both neighbours (known once bar k+1 has closed)."""
    out = np.zeros(len(l), bool)
    if len(l) >= 3:
        out[1:-1] = (l[1:-1] < l[:-2]) & (l[1:-1] < l[2:])
    return out


def fractal_highs(h: np.ndarray) -> np.ndarray:
    out = np.zeros(len(h), bool)
    if len(h) >= 3:
        out[1:-1] = (h[1:-1] > h[:-2]) & (h[1:-1] > h[2:])
    return out


def last_fvg(h: np.ndarray, l: np.ndarray, first: int, last: int, side: int) -> int:
    """First bar a of the last fair value gap (a, a+1, a+2) whose third bar lies in [first, last]: bearish (side -1)
    when l[a] > h[a+2], bullish (+1) when h[a] < l[a+2]. -1 if none."""
    for c3 in range(last, max(first, 2) - 1, -1):
        a = c3 - 2
        if (side < 0 and l[a] > h[c3]) or (side > 0 and h[a] < l[c3]):
            return a
    return -1


def first_outside(price: np.ndarray, start: int, end: int, lo: float, hi: float) -> int:
    """First index in [start, end) with price < lo or price > hi; end if none."""
    return min(_first_hit(price[:end], start, np.nextafter(lo, -np.inf), np.nextafter(hi, np.inf)), end)


def first_inside(price: np.ndarray, start: int, end: int, lo: float, hi: float) -> int:
    """First index in [start, end) with lo <= price <= hi; end if none."""
    size = 4096
    while start < end:
        seg = price[start:min(start + size, end)]
        hit = np.flatnonzero((seg >= lo) & (seg <= hi))
        if hit.size:
            return start + int(hit[0])
        start += size
        size *= 2
    return end


def trade(ctx: Ctx, e: int, side: int, exit_ms: int, sl: float = NAN, tp: float = NAN, sl_dist: float = NAN,
          why_time: str = "time") -> Optional[Trade]:
    """Open at tick e (moved just past the last exit when needed), close at the stop, the target or the first tick
    at or after exit_ms ("tail" when the chunk ends first). None when it cannot enter, when the fill is at or after
    exit_ms, or when the stop or the target is already through the fill."""
    if e <= ctx.busy_tick:
        e = ctx.busy_tick + 1
    if not ctx.can_enter(e) or int(ctx.t.ts[e]) >= exit_ms:
        return None
    pos = ctx.open(e, side)
    if not math.isfinite(sl) and math.isfinite(sl_dist):
        sl = pos.entry - side * sl_dist
    if (math.isfinite(sl) and (pos.entry - sl) * side <= 0) or (math.isfinite(tp) and (tp - pos.entry) * side <= 0):
        return None
    pos.sl = pos.sl0 = sl
    pos.tp = pos.tp0 = tp
    n = len(ctx.t)
    x = ctx.tick_at(exit_ms)
    timed = x < n
    j, why = ctx.first_exit(pos, e + 1, max(x if timed else n - 1, e))
    ctx.close(pos, j, why or (why_time if timed else "tail"))
    return ctx.finish(pos)


def range_breakout(ctx: Ctx, a_ms: int, b_ms: int, w_end_ms: int, exit_ms: int, stop: str = "other",
                   side_ok: Optional[Callable[[int, int], bool]] = None,
                   exit_for: Optional[Callable[[int, int], int]] = None) -> Optional[Trade]:
    """Range = bid high/low of the ticks in [a_ms, b_ms). From b_ms until w_end_ms, the first tick with bid above
    the high (long) or below the low (short) is a breakout event. side_ok(side, tick) False skips an event; that
    side re-arms once bid is back inside the range. Without side_ok the first event is the only one. Stop at the
    other side ("other") or the midpoint ("mid"); exit at exit_ms, or at exit_for(side, entry ms) when that is
    earlier (why "tms"). Skipped when the range is below MIN_RANGE_SPREADS median spreads."""
    t = ctx.t
    e0, e1 = ctx.tick_at(a_ms), ctx.tick_at(b_ms)
    if e1 - e0 < 2:
        return None
    hi, lo = float(t.bid[e0:e1].max()), float(t.bid[e0:e1].min())
    if hi <= lo or hi - lo < MIN_RANGE_SPREADS * float(np.median(t.ask[e0:e1] - t.bid[e0:e1])):
        return None
    w1 = ctx.tick_at(w_end_ms)
    j = e1
    while j < w1:
        k = first_outside(t.bid, j, w1, lo, hi)
        if k >= w1:
            return None
        side = 1 if t.bid[k] > hi else -1
        if side_ok is None or side_ok(side, k):
            sl = (lo if side > 0 else hi) if stop == "other" else (hi + lo) / 2.0
            ex, why = exit_ms, "time"
            if exit_for is not None:
                x = exit_for(side, int(t.ts[k]))
                if x and x < exit_ms:
                    ex, why = x, "tms"
            return trade(ctx, k, side, ex, sl=sl, why_time=why)
        j = first_inside(t.bid, k, w1, lo, hi)
    return None
