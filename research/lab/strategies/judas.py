"""AsianRangeJudasSweepBot (cBot/AsianRangeJudasSweepBot.cs) in the lab, with the AI replaced by "approve every
candidate".

Live bots run UseAiGateMode=true: on M15 bar closes a Judas sweep (a bar that spikes beyond the Asian range by
the sweep buffer inside the London / New York killzone and closes back inside with a rejection wick) opens a
3-bar window in which the AI is asked; the server (evaluate_judas_sweep_gate) and the cBot (ExecuteDecision)
then apply the guards modelled here: Asian range inside the preset and the server's per-class band, one trade
per side per Asian session, a side locked after a decisive close beyond the range, the entry no further than
25 % of the range from the swept level, and the SL floor max(AiSlMinFloorPips, 0.8 x ATR14). The AI's own SL/TP
choice is replaced by its fallbacks, the preset stoplossPip / takeprofitPip. Exits: SL/TP, break-even at
breakEvenRrTrigger x R (buffer = max(breakEvenExtraPips, commission in pips + 0.5)), and the structural guard
(a decisive close beyond the range closes the position on that side). Not modelled: AI ADJUST / CLOSE_ALL,
the news filter, anti-FOMO staging (an approval arrives on the signal tick, at the bar open), the negative-swap
term of the break-even buffer. Options the presets leave off (trailing, DCA, indicator close, RSI filter) raise."""
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from research.indicators import ema, true_range
from research.lab import costs
from research.lab.cbot import cbot_params
from research.lab.engine import Ctx, Pos
from research.ticks import _first_hit

SIGNAL_WINDOW_BARS = 3            # CrossSignalWindowBars
UNMODELLED = {"enableTrailingStop": False, "enableTrailingStopFromBreakEven": False, "dcaEnable": False,
              "enableIndicatorCloseInAiMode": False, "enableRsiFilter": False}


def _nth_sunday(y: int, m: int, n: int) -> datetime:
    first = datetime(y, m, 1, tzinfo=timezone.utc)
    return first + timedelta(days=(6 - first.weekday()) % 7 + 7 * (n - 1))


def _last_sunday(y: int, m: int) -> datetime:
    last = datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=timezone.utc) - timedelta(days=1)
    return last - timedelta(days=(last.weekday() + 1) % 7)


def europe_dst(dt: datetime) -> bool:
    return _last_sunday(dt.year, 3) + timedelta(hours=1) <= dt < _last_sunday(dt.year, 10) + timedelta(hours=1)


def us_dst(dt: datetime) -> bool:
    return _nth_sunday(dt.year, 3, 2) + timedelta(hours=7) <= dt < _nth_sunday(dt.year, 11, 1) + timedelta(hours=6)


def in_killzone(dt: datetime, p: dict) -> bool:
    """IsGoldenKillzone: London [start, end) or New York start:30 .. end; the hours are summer UTC hours
    moved one hour later in winter."""
    ls, le, ns, ne = p["londonStartHour"], p["londonEndHour"], p["nyStartHour"], p["nyEndHour"]
    rule = p["dstRule"]
    if rule != "None":
        if not (us_dst(dt) if rule == "US" else europe_dst(dt)):
            ls, le = (ls + 1) % 24, (le + 1) % 24
        if not (europe_dst(dt) if rule == "Europe" else us_dst(dt)):
            ns, ne = (ns + 1) % 24, (ne + 1) % 24
    h, m = dt.hour, dt.minute
    return ls <= h < le or (h == ns and m >= 30) or ns < h < ne


def server_range_ok(symbol: str, pips: float) -> bool:
    """evaluate_judas_sweep_gate's Asian-range band per asset class (app/trade_gates.py)."""
    s = symbol.upper()
    if "XAU" in s or "GOLD" in s:
        lo, hi = 100.0, 10000.0
    elif "JPY" in s:
        lo, hi = 15.0, 200.0
    elif "BTC" in s:
        lo, hi = 10000.0, 400000.0
    elif "ETH" in s:
        lo, hi = 800.0, 35000.0
    elif "UK100" in s:
        lo, hi = 120.0, 800.0
    elif any(x in s for x in ("US30", "USTEC", "DE40")):
        lo, hi = 50.0, 4000.0
    else:
        lo, hi = 12.0, 100.0
    return lo <= pips <= hi


@dataclass
class _State:
    day: Optional[date] = None
    hi: float = 0.0
    lo: float = 0.0
    buy_taken: bool = False
    sell_taken: bool = False
    low_broken: bool = False
    high_broken: bool = False
    allowed: int = 0
    since: int = 99
    be_done: bool = False

    def range_pips(self, pip: float) -> float:
        return (self.hi - self.lo) / pip if self.hi > 0 else 0.0


def _track_asian(st: _State, b, i: int, p: dict) -> None:
    dt = datetime.fromtimestamp(b.open_time[i] / 1000, timezone.utc)
    if p["asianStartHour"] <= dt.hour < p["asianEndHour"]:
        if st.day != dt.date():
            st.day, st.hi, st.lo = dt.date(), float(b.h[i]), float(b.l[i])
            st.buy_taken = st.sell_taken = st.low_broken = st.high_broken = False
        else:
            st.hi, st.lo = max(st.hi, float(b.h[i])), min(st.lo, float(b.l[i]))


def _sweep(b, i: int, st: _State, p: dict, buf: float, pip: float) -> int:
    """CheckJudasSweep on closed bar i: -1 sell sweep above the high, +1 buy sweep below the low, 0 none."""
    if st.hi <= 0 or st.lo <= 0:
        return 0
    rng = st.range_pips(pip)
    if rng < p["minAsianRangePips"] or rng > p["maxAsianRangePips"]:
        return 0
    o, h, l, c = b.o[i], b.h[i], b.l[i], b.c[i]
    total = h - l
    need = p["requireRejectionWick"]
    if h >= st.hi + buf and c <= st.hi:
        return -1 if not need or (total > 0 and (h - max(o, c)) / total >= p["minRejectionWickRatio"]) else 0
    if l <= st.lo - buf and c >= st.lo:
        return 1 if not need or (total > 0 and (min(o, c) - l) / total >= p["minRejectionWickRatio"]) else 0
    return 0


def _exit(ctx: Ctx, pos: Pos, j: int, why: str) -> None:
    ctx.close(pos, j, why)
    ctx.finish(pos)


def _enter(ctx: Ctx, st: _State, e: int, atr_i: float, p: dict, pip: float) -> Optional[Pos]:
    side, t = st.allowed, ctx.t
    if (st.buy_taken if side > 0 else st.sell_taken) or (st.low_broken if side > 0 else st.high_broken):
        return None
    rng = st.hi - st.lo
    dist = (t.ask[e] - st.lo) if side > 0 else (st.hi - t.bid[e])
    if rng > 0 and p["maxEntryExtensionRangePct"] > 0 and dist > rng * p["maxEntryExtensionRangePct"] / 100.0:
        return None
    atr_pips = round(atr_i / pip) if math.isfinite(atr_i) else 0
    floor = max(p["AiSlMinFloorPips"], round(atr_pips * 0.8) if atr_pips > 0 else 0)
    sl_pips = max(p["stoplossPip"], floor)
    pos = ctx.open(e, side)
    pos.sl = pos.sl0 = pos.entry - side * sl_pips * pip
    pos.tp = pos.tp0 = pos.entry + side * p["takeprofitPip"] * pip
    if side > 0:
        st.buy_taken = True
    else:
        st.sell_taken = True
    st.be_done = False
    return pos


def _break_even(ctx: Ctx, pos: Pos, j: int, p: dict, st: _State) -> None:
    t, pip, side = ctx.t, ctx.inst.pip, pos.side
    pip_usd = pip * costs.usd_per_quote(ctx.inst.quote_ccy, int(t.ts[j]))
    buffer = max(p["breakEvenExtraPips"], ctx.inst.comm_per_unit / pip_usd + 0.5) * pip
    new_sl = pos.entry + side * buffer
    if (new_sl - pos.sl) * side <= 0:
        st.be_done = True                                  # the stop is already beyond break-even
        return
    min_stop = max((t.ask[j] - t.bid[j]) * 3, ctx.inst.tick_size * 10)
    if (new_sl < t.bid[j] - min_stop) if side > 0 else (new_sl > t.ask[j] + min_stop):
        pos.sl, st.be_done = new_sl, True


def _hold(ctx: Ctx, pos: Pos, cur: int, end: int, p: dict, st: _State):
    """Ticks [cur, end) of an open position: SL, TP and the break-even move. Returns (pos or None, cursor)."""
    side, pip = pos.side, ctx.inst.pip
    price = ctx.t.bid if side > 0 else ctx.t.ask
    while cur < end:
        be = math.nan
        if p["enableBreakEvenPrice"] and not st.be_done:
            init = abs(pos.entry - pos.sl) / pip or p["stoplossPip"]
            be = pos.entry + side * p["breakEvenRrTrigger"] * init * pip
        if side > 0:
            lo, hi = pos.sl, (min(pos.tp, be) if math.isfinite(be) else pos.tp)
        else:
            lo, hi = (max(pos.tp, be) if math.isfinite(be) else pos.tp), pos.sl
        j = _first_hit(price[:end], cur, lo, hi)
        if j >= end:
            return pos, end
        px = float(price[j])
        if (px - pos.sl) * side <= 0:
            _exit(ctx, pos, j, "sl")
            return None, end
        if (px - pos.tp) * side >= 0:
            _exit(ctx, pos, j, "tp")
            return None, end
        _break_even(ctx, pos, j, p, st)
        cur = j + 1
    return pos, cur


def judas(ctx: Ctx, **overrides) -> None:
    sym, t, pip = ctx.ch.symbol, ctx.t, ctx.inst.pip
    p = cbot_params("judas", sym, **overrides)
    for key, value in UNMODELLED.items():
        if p[key] != value:
            raise ValueError(f"the Judas port does not model {key}={p[key]}")
    b = ctx.bars(15)
    atr = ema(true_range(b.h, b.l, b.c), 14)             # AverageTrueRange(14, Exponential)
    buf = p["sweepBufferPips"] * pip
    st, pos, cur = _State(), None, 0
    for i in range(len(b)):
        e = int(b.event_tick[i])
        if e >= len(t):
            break
        if pos is not None:
            pos, cur = _hold(ctx, pos, cur, e, p, st)
        _track_asian(st, b, i, p)
        if st.hi > 0 and st.lo > 0:
            if not st.low_broken and b.c[i] < st.lo - buf:
                st.low_broken = True
                if pos is not None and pos.side > 0:
                    _exit(ctx, pos, e, "structure")
                    pos = None
            if not st.high_broken and b.c[i] > st.hi + buf:
                st.high_broken = True
                if pos is not None and pos.side < 0:
                    _exit(ctx, pos, e, "structure")
                    pos = None
        now = datetime.fromtimestamp(t.ts[e] / 1000, timezone.utc)      # Server.Time in OnBarClosed
        sig = _sweep(b, i, st, p, buf, pip) if in_killzone(now, p) else 0
        if sig:
            st.allowed, st.since = sig, 0
        elif st.allowed:
            st.since += 1
            if st.since > SIGNAL_WINDOW_BARS:
                st.allowed = 0
        if st.allowed and pos is None and ctx.can_enter(e) and server_range_ok(sym, st.range_pips(pip)):
            pos = _enter(ctx, st, e, float(atr[i]), p, pip)
            cur = e + 1
    if pos is not None:
        _exit(ctx, pos, len(t) - 1, "tail")
