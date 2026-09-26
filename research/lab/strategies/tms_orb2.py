"""TMS + ORB rebuilt from the canonical definitions (docs/superpowers/specs/2026-09-26-strategy-refresh-design.md),
independent of cBot/AiAgentBot.cs: T1 the opening range breakout (Crabel), T2 only breakouts in the direction of the
H1 TMS state, T3 = T2 with the TMS exit, T4 / T5 the TMS (Trading Made Simple) system alone on H4 / H1."""
from typing import List, Tuple

import numpy as np

from research.lab.engine import Ctx
from research.lab.strategies.canon import (MINUTE_MS, OR_MINUTES, ORB_GROUP, ORB_SESSIONS, ORB_WINDOW_MINUTES, Tms,
                                           range_breakout, trade)
from research.lab.strategies.rules import session_days


def orb(ctx: Ctx, tms: bool = False, tms_exit: bool = False) -> None:
    """T1 (tms False), T2 (tms True), T3 (tms and tms_exit True)."""
    tz, t_open, t_end = ORB_SESSIONS[ORB_GROUP[ctx.ch.symbol]]
    lines = Tms.of(ctx.bars(60)) if tms else None
    state = lines.state() if tms else None

    def side_ok(side: int, k: int) -> bool:
        i = lines.last_closed(int(ctx.t.ts[k]))
        return i >= 0 and int(state[i]) == side

    def exit_for(side: int, ms: int) -> int:
        return lines.first_against(ms, side)

    for _, o, c in session_days(ctx, tz, t_open, t_end):
        b = o + OR_MINUTES * MINUTE_MS
        range_breakout(ctx, o, b, min(b + ORB_WINDOW_MINUTES * MINUTE_MS, c), c,
                       side_ok=side_ok if tms else None, exit_for=exit_for if tms_exit else None)


def tms_signals(green, red, ha_dir, stoch_dir) -> List[Tuple[int, int]]:
    """(decision bar, side): green crosses red at bar i; the entry is decided at bar i (candle 1), else bar i+1
    (candle 2), when green is still across, the HA bar has the trade's colour and Stoch points that way."""
    diff = np.asarray(green, float) - np.asarray(red, float)
    with np.errstate(invalid="ignore"):
        up = (diff[1:] > 0) & (diff[:-1] <= 0)
        dn = (diff[1:] < 0) & (diff[:-1] >= 0)
    out = []
    for i in np.flatnonzero(up | dn) + 1:
        side = 1 if diff[i] > 0 else -1
        for dec in (i, i + 1):
            if dec < len(diff) and diff[dec] * side > 0 and ha_dir[dec] == side and stoch_dir[dec] == side:
                out.append((int(dec), side))
                break
    return out


def tms_system(ctx: Ctx, tf: int = 240) -> None:
    """T4 (tf 240) / T5 (tf 60): the TMS system alone. SL beyond the last 5 bars' low / high (+ spread for a sell);
    exit at the first tick after the bar close where green crosses back; no target."""
    b, t = ctx.bars(tf), ctx.t
    lines = Tms.of(b)
    never = int(t.ts[-1]) + 1 if len(t) else 0
    for dec, side in tms_signals(lines.green, lines.red, lines.ha_dir, lines.stoch_dir):
        e = int(b.event_tick[dec])
        if e >= len(t) or e < ctx.busy_tick:
            continue
        lo = max(dec - 4, 0)
        sl = (float(b.l[lo:dec + 1].min()) if side > 0
              else float(b.h[lo:dec + 1].max()) + float(t.ask[e] - t.bid[e]))
        ex = lines.first_against(int(b.close_time[dec]), side)
        trade(ctx, e, side, ex or never, sl=sl, why_time="cross")
