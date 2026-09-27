"""Asian Range Judas Sweep rebuilt from ICT's definition (docs/superpowers/specs/2026-09-26-strategy-refresh-design.md),
independent of cBot/AsianRangeJudasSweepBot.cs. Asian range = 20:00-00:00 New York; in a killzone price runs one
side of it, shifts structure on M5 with a fair value gap, and the trade is a limit at the gap back towards the other
side (J1-J4). J5 fades an M15 sweep-and-close without the structure shift."""
from dataclasses import dataclass
from datetime import date, time, timedelta
from typing import Callable, List, Optional

import numpy as np

from research.lab.engine import Ctx
from research.lab.strategies.canon import (NY, chunk_days, fractal_highs, fractal_lows, last_fvg, local_ms,
                                           trade)
from research.ticks import _first_hit

ASIA = (time(20, 0), time(0, 0))          # the previous New York evening -> New York midnight
KILLZONES = {"london": (time(2, 0), time(5, 0)), "nyam": (time(7, 0), time(10, 0))}
EXIT_AT = time(12, 0)
MIN_ASIA_BARS = 36                         # of 48 M5 bars


@dataclass
class Day:
    d: date
    ah: float
    al: float
    midnight: float
    i0: int          # first Asian M5 bar
    exit_ms: int


@dataclass
class Order:
    side: int
    limit: float
    sl: float
    tp: float
    placed: int      # first tick the limit order is live


def asian_days(ctx: Ctx, b5) -> List[Day]:
    """Weekdays (New York) whose Asian window has at least MIN_ASIA_BARS M5 bars and a bar at or after midnight."""
    out = []
    for d in chunk_days(ctx):
        if d.weekday() >= 5:
            continue
        a, m = local_ms(d - timedelta(days=1), ASIA[0], NY), local_ms(d, ASIA[1], NY)
        i0, i1 = (int(x) for x in np.searchsorted(b5.open_time, [a, m]))
        if i1 - i0 < MIN_ASIA_BARS or i1 >= len(b5):
            continue
        out.append(Day(d, float(b5.h[i0:i1].max()), float(b5.l[i0:i1].min()), float(b5.o[i1]), i0,
                       local_ms(d, EXIT_AT, NY)))
    return out


def _ref_swing(fl, fh, i0: int, ext_bar: int, side: int) -> int:
    """Latest fractal (low for a sell setup, high for a buy) at k in [i0, ext_bar - 1]; -1 if none."""
    ks = np.flatnonzero((fl if side < 0 else fh)[i0:ext_bar]) + i0
    return int(ks[-1]) if ks.size else -1


def find_order(b, fl, fh, day: Day, k0: int, k1: int, spread_at: Callable[[int], float], tp_mode: str,
               midnight_filter: bool) -> Optional[Order]:
    """The first valid limit order of one killzone (M5 bars [k0, k1)). Side -1 = the high was swept (sell setup),
    +1 = the low was swept (buy setup)."""
    state = {-1: None, 1: None}                        # side -> [extreme, extreme bar, armed]
    for i in range(k0, k1):
        for side in (-1, 1):
            ext_now = float(b.h[i] if side < 0 else b.l[i])
            beyond = ext_now > day.ah if side < 0 else ext_now < day.al
            st = state[side]
            if beyond and (st is None or (ext_now - st[0]) * -side > 0):
                state[side] = [ext_now, i, True]       # new or extended sweep: steps 2-4 start again
                continue
            if st is None or not st[2]:
                continue
            ref = _ref_swing(fl, fh, day.i0, st[1], side)
            if ref < 0:
                st[2] = False
                continue
            if not (b.c[i] < b.l[ref] if side < 0 else b.c[i] > b.h[ref]):
                continue
            st[2] = False                               # one structure shift per sweep extreme
            a = last_fvg(b.h, b.l, st[1], i, side)
            if a < 0:
                continue
            e = int(b.event_tick[i])
            limit = float(b.h[a + 2] if side < 0 else b.l[a + 2])
            sl = st[0] + spread_at(e) if side < 0 else st[0]
            risk = (sl - limit) * -side
            if risk <= 0:
                continue
            if tp_mode == "range":
                tp = day.al if side < 0 else day.ah
                if (limit - tp) * -side < risk:
                    continue
            else:
                tp = limit + side * 2.0 * risk
            if midnight_filter and (limit - day.midnight) * -side <= 0:
                continue
            return Order(side, limit, sl, tp, e)
    return None


def fill_tick(t, order: Order, end: int) -> int:
    """First tick in [order.placed, end) at which a sell limit's bid >= limit (a buy limit's ask <= limit)."""
    if order.side < 0:
        return min(_first_hit(t.bid[:end], order.placed, -np.inf, order.limit), end)
    return min(_first_hit(t.ask[:end], order.placed, order.limit, np.inf), end)


def judas_ict(ctx: Ctx, killzones=("london",), midnight_filter: bool = False, tp_mode: str = "range") -> None:
    """J1 (defaults), J2 (midnight_filter), J3 (tp_mode "2r"), J4 (killzones london + nyam). One filled trade per day;
    exit at the stop, the target or 12:00 New York."""
    t, b = ctx.t, ctx.bars(5)
    fl, fh = fractal_lows(b.l), fractal_highs(b.h)

    def spread_at(e: int) -> float:
        return float(t.ask[e] - t.bid[e]) if e < len(t) else 0.0

    for day in asian_days(ctx, b):
        for kz in killzones:
            s, f = (local_ms(day.d, x, NY) for x in KILLZONES[kz])
            k0, k1 = (int(x) for x in np.searchsorted(b.open_time, [s, f]))
            order = find_order(b, fl, fh, day, k0, k1, spread_at, tp_mode, midnight_filter)
            if order is None:
                continue
            end = ctx.tick_at(f)
            j = fill_tick(t, order, end)
            if j < end and trade(ctx, j, order.side, day.exit_ms, sl=order.sl, tp=order.tp) is not None:
                break


def judas_sweep_close(ctx: Ctx) -> None:
    """J5: an M15 bar inside the London killzone that trades beyond the Asian range and closes back inside is faded
    at the next tick; SL beyond the killzone's extreme so far (+ spread for a sell), TP the other side of the range,
    skipped when the target is nearer than the stop; exit 12:00 New York; one trade per day."""
    t, b5, b = ctx.t, ctx.bars(5), ctx.bars(15)
    for day in asian_days(ctx, b5):
        s, f = (local_ms(day.d, x, NY) for x in KILLZONES["london"])
        k0, k1 = (int(x) for x in np.searchsorted(b.open_time, [s, f]))
        for i in range(k0, k1):
            e = int(b.event_tick[i])
            if e >= len(t):
                break
            if b.h[i] > day.ah and b.c[i] < day.ah:
                side, sl, tp, entry = -1, float(b.h[k0:i + 1].max()) + float(t.ask[e] - t.bid[e]), day.al, t.bid[e]
            elif b.l[i] < day.al and b.c[i] > day.al:
                side, sl, tp, entry = 1, float(b.l[k0:i + 1].min()), day.ah, t.ask[e]
            else:
                continue
            if abs(tp - entry) < abs(sl - entry):
                continue
            if trade(ctx, e, side, day.exit_ms, sl=sl, tp=tp) is not None:
                break
