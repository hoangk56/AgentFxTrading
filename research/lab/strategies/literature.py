"""Literature candidates of the 2026-09-26 refresh (docs/superpowers/specs/2026-09-26-strategy-refresh-design.md):
N1 the FX fixing reversal (Krohn, Mueller & Whelan 2024), N2 the gotobi Tokyo-fix pattern (Bessho, Sugimoto &
Suzuki 2023), N3 market intraday momentum (Gao, Han, Li & Zhou 2018), N4 the London breakout of the Asian range."""
import math
from datetime import date, time, timedelta
from typing import List

import numpy as np

from research.indicators import atr_sma
from research.lab.engine import NAN, Ctx
from research.lab.strategies.canon import LONDON, MINUTE_MS, TOKYO, chunk_days, local_ms, range_breakout, trade
from research.lab.strategies.rules import SESSIONS, _bid_before, session_days

USD_BUY_SIDE = {"USDJPY": 1, "USDCAD": 1, "EURUSD": -1, "GBPUSD": -1, "AUDUSD": -1}   # the side that buys USD


def _atr_before(b, a, ms: int) -> float:
    k = int(np.searchsorted(b.close_time, ms, side="right")) - 1
    return float(a[k]) if k >= 20 and math.isfinite(a[k]) else NAN


def _timed_pair(ctx: Ctx, b, a, legs, k_atr: float) -> None:
    """legs = [(at_ms, side, exit_ms)], each entered at the first tick at or after at_ms with an SL of k_atr x ATR20."""
    for at, side, ex in legs:
        atr = _atr_before(b, a, at)
        if math.isfinite(atr):
            trade(ctx, ctx.tick_at(at), side, ex, sl_dist=k_atr * atr)


def fix_reversal(ctx: Ctx) -> None:
    """N1: long USD 14:00 -> 16:00 London, short USD 16:00 -> 18:00 London on weekdays; SL 3 x ATR20(H1)."""
    b = ctx.bars(60)
    a = atr_sma(b.h, b.l, b.c, 20)
    up = USD_BUY_SIDE[ctx.ch.symbol]
    for d in chunk_days(ctx):
        if d.weekday() < 5:
            p0, fx, p1 = (local_ms(d, time(h), LONDON) for h in (14, 16, 18))
            _timed_pair(ctx, b, a, [(p0, up, fx), (fx, -up, p1)], 3.0)


def gotobi_days(first: date, last: date) -> List[date]:
    """The 5th, 10th, 15th, 20th, 25th and the last day of each month in [first, last]; one on a weekend moves to
    the Friday before (Japanese holidays are not modelled)."""
    out, y, m = set(), first.year, first.month
    while (y, m) <= (last.year, last.month):
        nxt = date(y + (m == 12), m % 12 + 1, 1)
        for d in [date(y, m, k) for k in (5, 10, 15, 20, 25)] + [nxt - timedelta(days=1)]:
            while d.weekday() >= 5:
                d -= timedelta(days=1)
            if first <= d <= last:
                out.add(d)
        y, m = nxt.year, nxt.month
    return sorted(out)


def gotobi(ctx: Ctx) -> None:
    """N2 (USDJPY): on gotobi days long 03:00 -> 09:55 Tokyo, then short 09:55 -> 11:55 Tokyo; SL 3 x ATR20(H1)."""
    b = ctx.bars(60)
    a = atr_sma(b.h, b.l, b.c, 20)
    days = list(chunk_days(ctx))
    for d in gotobi_days(days[0], days[-1]):
        s, fx, e = (local_ms(d, x, TOKYO) for x in (time(3, 0), time(9, 55), time(11, 55)))
        _timed_pair(ctx, b, a, [(s, 1, fx), (fx, -1, e)], 3.0)


def intraday_momentum(ctx: Ctx) -> None:
    """N3 (index CFDs): r1 = bid at open + 30 min / bid at the previous session close - 1; trade sign(r1) over the
    last 30 minutes of the session; SL 2 x ATR20(30-min bars)."""
    b = ctx.bars(30)
    a = atr_sma(b.h, b.l, b.c, 20)
    days = session_days(ctx, *SESSIONS[ctx.ch.symbol])
    for (_, _, prev_close), (_, o, c) in zip(days, days[1:]):
        prev, now = _bid_before(ctx, prev_close), _bid_before(ctx, o + 30 * MINUTE_MS)
        if not (math.isfinite(prev) and math.isfinite(now) and prev > 0) or now == prev:
            continue
        at = c - 30 * MINUTE_MS
        atr = _atr_before(b, a, at)
        if math.isfinite(atr):
            trade(ctx, ctx.tick_at(at), 1 if now > prev else -1, c, sl_dist=2.0 * atr)


def london_breakout(ctx: Ctx) -> None:
    """N4: range = bid high/low 00:00-07:00 London; the first breakout 07:00-10:00 London is followed; SL at the
    range midpoint; exit 16:00 London; skipped when the range is under 3 median spreads."""
    for d in chunk_days(ctx):
        if d.weekday() < 5:
            a, r, w, x = (local_ms(d, time(h), LONDON) for h in (0, 7, 10, 16))
            range_breakout(ctx, a, r, w, x, stop="mid")
