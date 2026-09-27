"""One-position tick engine for the strategy lab (docs/superpowers/specs/2026-09-25-strategy-lab-design.md).

A Ctx runs one strategy on one chunk. Buys fill at the ask and close at the bid, sells the other way round.
A stop or target is hit by the first tick whose closing-side price reaches it and fills at that tick's price,
so a gap fills at the gapped price. Each closing deal is converted to USD at its day's rate
(research/lab/costs.py) and pays commission and the swaps of the rollovers it was held over. Positions never
overlap: an entry needs a tick after the previous exit, also across chunks (busy_ms)."""
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import numpy as np

from research.bars import Bars, build_bars
from research.lab import costs
from research.lab.feed import Chunk
from research.ticks import _first_hit
from research.ticks import Ticks

NAN = float("nan")
HOUR_MS, DAY_MS = 3_600_000, 86_400_000
NY = ZoneInfo("America/New_York")
D1_ENTRY_DELAY_MS = 2 * HOUR_MS        # D1 entries wait out the 17:00 New York rollover spread


def ny_offset_ms(ts: np.ndarray) -> np.ndarray:
    """New York's UTC offset in ms (negative) at each timestamp, resolved per UTC hour."""
    h = np.asarray(ts, np.int64) // HOUR_MS
    h0 = int(h.min())
    offs = np.array([datetime.fromtimestamp(x * 3600, NY).utcoffset().total_seconds() * 1000
                     for x in range(h0, int(h.max()) + 1)], np.int64)
    return offs[h - h0]


def build_d1_ny(t: Ticks) -> Bars:
    """Bid D1 bars of the FX day, 17:00 New York to 17:00 New York: no Sunday or Friday stubs."""
    if len(t) == 0:
        return build_bars(t, 1440)
    off = ny_offset_ms(t.ts)
    bucket = (t.ts + off + 7 * HOUR_MS) // DAY_MS
    starts = np.flatnonzero(np.r_[True, bucket[1:] != bucket[:-1]])
    ends = np.r_[starts[1:], len(t)]
    return Bars(bucket[starts] * DAY_MS - 7 * HOUR_MS - off[starts], t.bid[starts],
                np.maximum.reduceat(t.bid, starts), np.minimum.reduceat(t.bid, starts), t.bid[ends - 1],
                starts, ends, 1440)


@dataclass
class Trade:
    strategy: str
    symbol: str
    variant: str
    side: int
    t_in: int
    t_out: int
    entry: float
    exit: float           # volume-weighted exit price
    units: float
    sl0: float
    tp0: float
    gross: float
    comm: float
    swap: float
    risk_usd: float       # |entry - sl0| x units in USD at entry; NaN without a stop
    why: str

    @property
    def net(self) -> float:
        return self.gross - self.comm + self.swap

    @property
    def r(self) -> float:
        return self.net / self.risk_usd if self.risk_usd > 0 else NAN


@dataclass
class Pos:
    side: int
    e: int                # entry tick
    entry: float
    units: float          # still open
    sl: float
    tp: float
    sl0: float
    tp0: float
    deals: List[Tuple[int, float, float, str]] = field(default_factory=list)   # (tick, price, units, why)


@dataclass
class Intent:
    at_ms: int            # enter at the first tick at or after this time
    side: int
    sl_dist: float = NAN  # stop / target as a distance from the fill ...
    tp_dist: float = NAN
    exit_ms: int = 0      # time exit at the first tick at or after this time; 0 = none
    sl_px: float = NAN    # ... or as a price, which wins when set
    tp_px: float = NAN


class Ctx:
    def __init__(self, ch: Chunk, strategy: str, busy_ms: int = 0):
        self.ch, self.t, self.inst, self.strategy = ch, ch.t, ch.inst, strategy
        self.units = ch.inst.units
        self.busy_ms = busy_ms
        self.busy_tick = -1
        self.trades: List[Trade] = []
        self._bars: Dict[int, Bars] = {}

    def bars(self, minutes: int) -> Bars:
        if minutes not in self._bars:
            self._bars[minutes] = build_d1_ny(self.t) if minutes == 1440 else build_bars(self.t, minutes)
        return self._bars[minutes]

    def tick_at(self, ms: int) -> int:
        return int(np.searchsorted(self.t.ts, ms, side="left"))

    def can_enter(self, e: int) -> bool:
        if e <= self.busy_tick or e >= len(self.t):
            return False
        ts = int(self.t.ts[e])
        return self.ch.lo_ms <= ts < self.ch.hi_ms and ts > self.busy_ms

    def open(self, e: int, side: int, sl: float = NAN, tp: float = NAN) -> Pos:
        entry = float(self.t.ask[e] if side > 0 else self.t.bid[e])
        return Pos(side, e, entry, self.units, sl, tp, sl, tp)

    def close(self, pos: Pos, j: int, why: str, units: Optional[float] = None) -> None:
        u = pos.units if units is None else units
        pos.deals.append((j, float(self.t.bid[j] if pos.side > 0 else self.t.ask[j]), u, why))
        pos.units -= u

    def finish(self, pos: Pos) -> Trade:
        """Book a position whose deals close all of it."""
        t, inst = self.t, self.inst
        t_in = int(t.ts[pos.e])
        gross = comm = sw = 0.0
        for j, px, u, _ in pos.deals:
            t_j = int(t.ts[j])
            gross += (px - pos.entry) * pos.side * u * costs.usd_per_quote(inst.quote_ccy, t_j)
            comm += costs.commission(inst, u)
            sw += costs.swap(inst, pos.side, u, t_in, t_j)
        units = sum(d[2] for d in pos.deals)
        last = max(d[0] for d in pos.deals)
        risk = (abs(pos.entry - pos.sl0) * units * costs.usd_per_quote(inst.quote_ccy, t_in)
                if math.isfinite(pos.sl0) else NAN)
        tr = Trade(self.strategy, self.ch.symbol, self.ch.variant, pos.side, t_in, int(t.ts[last]), pos.entry,
                   sum(d[1] * d[2] for d in pos.deals) / units, units, pos.sl0, pos.tp0, gross, comm, sw, risk,
                   pos.deals[-1][3])
        self.trades.append(tr)
        self.busy_tick, self.busy_ms = last, int(t.ts[last])
        return tr

    def first_exit(self, pos: Pos, start: int, end: int) -> Tuple[int, str]:
        """First tick in [start, end] that hits the stop or the target; (end, "") when none does."""
        lo = pos.sl if pos.side > 0 else pos.tp
        hi = pos.tp if pos.side > 0 else pos.sl
        lo = lo if math.isfinite(lo) else -np.inf
        hi = hi if math.isfinite(hi) else np.inf
        price = self.t.bid if pos.side > 0 else self.t.ask
        j = _first_hit(price[:end + 1], start, lo, hi)
        if j > end:
            return end, ""
        stopped = math.isfinite(pos.sl) and (float(price[j]) - pos.sl) * pos.side <= 0
        return j, "sl" if stopped else "tp"


def run_intents(ctx: Ctx, intents: List[Intent]) -> List[Trade]:
    """Vector strategies: enter each intent in time order unless a position is open, then exit at the stop,
    the target or the time exit, whichever comes first ("tail" when the chunk ends first)."""
    n = len(ctx.t)
    for it in sorted(intents, key=lambda x: x.at_ms):
        e = ctx.tick_at(it.at_ms)
        if not ctx.can_enter(e):
            continue
        pos = ctx.open(e, it.side)
        pos.sl = pos.sl0 = it.sl_px if math.isfinite(it.sl_px) else pos.entry - it.side * it.sl_dist
        pos.tp = pos.tp0 = it.tp_px if math.isfinite(it.tp_px) else pos.entry + it.side * it.tp_dist
        if math.isfinite(pos.sl) and (pos.entry - pos.sl) * it.side <= 0:
            continue                                  # the stop is already through the fill
        timed = it.exit_ms and ctx.tick_at(it.exit_ms) < n
        end = ctx.tick_at(it.exit_ms) if timed else n - 1
        j, why = ctx.first_exit(pos, e + 1, end)
        ctx.close(pos, j, why or ("time" if timed else "tail"))
        ctx.finish(pos)
    return ctx.trades
