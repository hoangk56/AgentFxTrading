# Strategy Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build TMS+ORB (T1–T5), Asian Range Judas Sweep (J1–J5) and four literature strategies (N1–N4) from their canonical definitions in the strategy lab, run them once against a pre-registered bar, and report the verdict.

**Architecture:** New strategy modules under `research/lab/strategies/` (`canon.py` shared helpers, `tms_orb2.py`, `judas2.py`, `literature.py`) plug into the existing lab (`engine.Ctx`, `run.py`, `report.py`) through catalog entries. A new `research/lab/verdict.py` applies the six pass conditions. Runs go to new dirs `research/results/lab/v2check` and `research/results/lab/v2`.

**Tech Stack:** Python 3 + numpy in `research/.venv`, pytest, zoneinfo.

**Spec:** `docs/superpowers/specs/2026-09-26-strategy-refresh-design.md`

## Global Constraints

- Python: `research/.venv/bin/python`; tests: `research/.venv/bin/python -m pytest research/tests -q`.
- **No commits, no pushes** (user rule in AGENTS.md and memory): leave every change in the working tree.
- Never write into `research/results/lab/main` (write-protected baseline).
- Parameters are fixed by the spec; after results are seen only bugs may be fixed, each logged in `research/results/prereg_v2.md`.
- Old ports `research/lab/strategies/tmsorb.py` and `judas.py` are not modified.
- Budget: exactly 14 runnable variants: T1-ORB, T2-TMSORB, T3-TMSORB-X, T4-TMS-H4, T5-TMS-H1, J1-ICT, J2-ICT-MO, J3-ICT-2R, J4-ICT-2KZ, J5-SWEEP, N1-FIX, N2-GOTOBI, N3-IMOM, N4-LBO.
- Pass bar constants: holdout 2025–2026, check 2023–2024, ≥ 100 trades, t ≥ 2.5, control ≥ 95 %, breadth ≥ 60 %; no mirror condition for N1/N2, no breadth condition for N2.

---

### Task 1: TMS indicators

**Files:**
- Modify: `research/indicators.py` (append)
- Test: `research/tests/test_indicators_tms.py` (new)

**Interfaces:**
- Produces: `heikin_ashi(o, h, l, c) -> (ha_open, ha_close)`, `tdi(close, rsi_n=13, green_n=2, red_n=7) -> (green, red)`, `stoch(h, l, c, k_n=8, slow_n=3, d_n=3) -> (slow_k, d)` (NaN during warm-up and on zero-range windows).

- [ ] **Step 1: Write the failing tests**

```python
import pytest

np = pytest.importorskip("numpy")

from research.indicators import heikin_ashi, rsi, sma, stoch, tdi  # noqa: E402


def test_heikin_ashi_open_is_the_mean_of_the_previous_ha_bar():
    o, h = np.array([10.0, 11.0, 12.0]), np.array([12.0, 13.0, 14.0])
    l, c = np.array([9.0, 10.0, 11.0]), np.array([11.0, 12.0, 13.0])
    ho, hc = heikin_ashi(o, h, l, c)
    assert hc.tolist() == [10.5, 11.5, 12.5]
    assert ho.tolist() == [10.5, 10.5, 11.0]


def test_tdi_is_sma2_and_sma7_of_rsi13():
    c = 100 + np.cumsum(np.sin(np.arange(60.0)))
    green, red = tdi(c)
    x = rsi(c, 13)
    assert np.allclose(green[1:], sma(x, 2)[1:]) and np.allclose(red[6:], sma(x, 7)[6:])
    assert np.isnan(red[5])


def test_stoch_slow_k_and_d_in_a_steady_uptrend():
    c = np.arange(1.0, 21.0)
    k, d = stoch(c + 1, c - 1, c)
    assert np.isnan(k[8]) and k[9] == pytest.approx(800 / 9)
    assert np.isnan(d[10]) and d[11] == pytest.approx(800 / 9)


def test_stoch_is_nan_on_a_flat_window():
    c = np.full(15, 5.0)
    k, d = stoch(c, c, c)
    assert np.isnan(k).all() and np.isnan(d).all()
```

- [ ] **Step 2: Run to verify they fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_indicators_tms.py -q`
Expected: ImportError (`heikin_ashi` not defined).

- [ ] **Step 3: Implement (append to `research/indicators.py`)**

```python
def heikin_ashi(o: np.ndarray, h: np.ndarray, l: np.ndarray, c: np.ndarray):
    """(ha_open, ha_close): ha_close = (O+H+L+C)/4, ha_open = mean of the previous HA open and close, seeded with
    (O0+C0)/2."""
    hc = (o + h + l + c) / 4.0
    ho = np.empty(len(o))
    if len(o):
        ho[0] = (o[0] + c[0]) / 2.0
        for i in range(1, len(o)):
            ho[i] = (ho[i - 1] + hc[i - 1]) / 2.0
    return ho, hc


def tdi(close: np.ndarray, rsi_n: int = 13, green_n: int = 2, red_n: int = 7):
    """Traders Dynamic Index lines TMS trades on: green = SMA(green_n) of RSI(rsi_n), red = SMA(red_n) of it."""
    r = rsi(close, rsi_n)
    return sma(r, green_n), sma(r, red_n)


def _rolling_mean(x: np.ndarray, n: int) -> np.ndarray:
    """Mean of each n-window; a NaN only spoils the windows that contain it (unlike sma's running sum)."""
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(x, n).mean(axis=1)
    return out


def stoch(h: np.ndarray, l: np.ndarray, c: np.ndarray, k_n: int = 8, slow_n: int = 3, d_n: int = 3):
    """(slow %K, %D): raw %K = 100 (C - LL) / (HH - LL) over k_n bars, slow %K = its SMA(slow_n), %D = SMA(d_n) of
    that. NaN during warm-up and where the k_n-bar range is zero."""
    raw = np.full(len(c), np.nan)
    if len(c) >= k_n:
        hh = sliding_window_view(h, k_n).max(axis=1)
        ll = sliding_window_view(l, k_n).min(axis=1)
        rng = hh - ll
        with np.errstate(divide="ignore", invalid="ignore"):
            raw[k_n - 1:] = np.where(rng > 0, 100.0 * (c[k_n - 1:] - ll) / rng, np.nan)
    k = _rolling_mean(raw, slow_n)
    return k, _rolling_mean(k, d_n)
```

- [ ] **Step 4: Run to verify they pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_indicators_tms.py research/tests/test_indicators.py -q`
Expected: all pass.

- [ ] **Step 5: No commit** (user rule). Leave in the working tree.

---

### Task 2: Shared canonical helpers (`canon.py`)

**Files:**
- Create: `research/lab/strategies/canon.py`
- Test: `research/tests/lab/test_lab_refresh_canon.py`

**Interfaces:**
- Consumes: `heikin_ashi`, `tdi`, `stoch` (Task 1); `Ctx`, `Trade`, `NAN` from `research/lab/engine.py`; `_first_hit` from `research/sim.py`.
- Produces:
  - constants `NY, LONDON, TOKYO, BERLIN, MINUTE_MS, ORB_SESSIONS, ORB_GROUP, OR_MINUTES=15, ORB_WINDOW_MINUTES=180, MIN_RANGE_SPREADS=3.0`
  - `local_ms(d: date, t: time, tz: str) -> int`, `chunk_days(ctx, before=2) -> Iterator[date]`
  - `@dataclass Tms(close_time, green, red, ha_dir, stoch_dir)` with `Tms.of(bars)`, `.state() -> int array`, `.last_closed(ms) -> int`, `.first_against(after_ms, side) -> int` (close_time or 0)
  - `fractal_lows(l) -> bool array`, `fractal_highs(h) -> bool array`, `last_fvg(h, l, first, last, side) -> int` (a or -1)
  - `first_outside(price, start, end, lo, hi) -> int`, `first_inside(price, start, end, lo, hi) -> int`
  - `trade(ctx, e, side, exit_ms, sl=NAN, tp=NAN, sl_dist=NAN, why_time="time") -> Optional[Trade]`
  - `range_breakout(ctx, a_ms, b_ms, w_end_ms, exit_ms, stop="other", side_ok=None, exit_for=None) -> Optional[Trade]`

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date, time

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.strategies.canon import (LONDON, NY, ORB_GROUP, TOKYO, Tms, first_inside, first_outside,  # noqa: E402
                                           fractal_highs, fractal_lows, last_fvg, local_ms, range_breakout, trade)
from research.lab.universe import ALL  # noqa: E402
from research.ticks import day_ms  # noqa: E402

HOUR, MIN = 3_600_000, 60_000
DAY = date(2025, 7, 1)                   # a Tuesday, British summer time
T0 = day_ms(DAY)


def minute_ticks(start_min, prices):
    """One bid tick per minute from T0 + start_min minutes."""
    ts = [T0 + (start_min + k) * MIN for k in range(len(prices))]
    return make_chunk(ts, prices, spread=0.0002)


def test_local_times_follow_daylight_saving():
    assert local_ms(DAY, time(8), LONDON) == T0 + 7 * HOUR
    assert local_ms(date(2025, 1, 15), time(8), LONDON) == day_ms(date(2025, 1, 15)) + 8 * HOUR
    assert local_ms(DAY, time(9), TOKYO) == T0
    assert local_ms(date(2025, 3, 12), time(2), NY) == day_ms(date(2025, 3, 12)) + 6 * HOUR


def test_every_lab_symbol_has_an_orb_session():
    assert set(ORB_GROUP) == set(ALL)


def test_tick_breakout_helpers():
    p = np.array([1.0, 1.5, 2.5, 1.2, 0.5, 1.0])
    assert first_outside(p, 0, 6, 1.0, 2.0) == 2 and first_outside(p, 3, 6, 1.0, 2.0) == 4
    assert first_outside(p, 0, 2, 1.0, 2.0) == 2
    assert first_inside(p, 2, 6, 1.0, 2.0) == 3 and first_inside(p, 4, 5, 1.0, 2.0) == 5


def test_fractals_and_fair_value_gaps():
    l = np.array([5.0, 4.0, 3.0, 4.0, 5.0, 2.0, 6.0])
    assert np.flatnonzero(fractal_lows(l)).tolist() == [2, 5]
    assert np.flatnonzero(fractal_highs(-l)).tolist() == [2, 5]
    h, lo = np.array([10.0, 9.0, 8.0, 7.0, 6.5]), np.array([9.0, 8.0, 7.5, 6.0, 5.0])
    assert last_fvg(h, lo, 0, 4, -1) == 2 and last_fvg(h, lo, 0, 3, -1) == 1
    assert last_fvg(h, lo, 0, 4, 1) == -1


def test_tms_state_last_closed_and_first_against():
    tms = Tms(close_time=np.array([10, 20, 30, 40]), green=np.array([60.0, 60.0, 40.0, 45.0]),
              red=np.array([55.0, 55.0, 45.0, 50.0]), ha_dir=np.array([1, -1, -1, -1]), stoch_dir=np.zeros(4))
    assert tms.state().tolist() == [1, 0, -1, -1]
    assert tms.last_closed(29) == 1 and tms.last_closed(30) == 2 and tms.last_closed(5) == -1
    assert tms.first_against(10, 1) == 30 and tms.first_against(30, -1) == 0


def test_trade_stops_out_and_never_opens_at_or_after_its_exit():
    ch = minute_ticks(0, [1.1000] * 5 + [1.0985] + [1.1000] * 5)
    ctx = Ctx(ch, "T")
    tr = trade(ctx, 1, 1, T0 + 10 * MIN, sl=1.0990)
    assert tr.why == "sl" and tr.t_out == T0 + 5 * MIN
    assert trade(ctx, 8, 1, T0 + 8 * MIN, sl=1.0990) is None
    tr = trade(ctx, 7, -1, T0 + 9 * MIN, sl_dist=0.0050)
    assert tr.why == "time" and tr.t_out == T0 + 9 * MIN and tr.sl0 == pytest.approx(1.1000 + 0.0050)


def _orb_path(after):
    """Ticks 06:00-17:00 UTC: flat before 07:00 UTC (08:00 London), a 1.1000-1.1010 opening range for 15 minutes,
    then `after` = [(minute from 07:15 UTC, bid), ...] with the bid held until the next change."""
    prices = [1.1005] * 60 + [1.1000, 1.1010] * 7 + [1.1005]
    level, changes = 1.1005, dict(after)
    for m in range(15, 600):
        level = changes.get(m, level)
        prices.append(level)
    return minute_ticks(6 * 60, prices)


def test_range_breakout_takes_the_first_break_with_the_stop_at_the_other_side():
    ctx = Ctx(_orb_path([(15, 1.1015)]), "T1")
    o = T0 + 7 * HOUR
    tr = range_breakout(ctx, o, o + 15 * MIN, o + 195 * MIN, T0 + 15 * HOUR + 30 * MIN)
    assert tr.side == 1 and tr.t_in == T0 + 7 * HOUR + 15 * MIN
    assert tr.entry == pytest.approx(1.1017) and tr.sl0 == pytest.approx(1.1000)
    assert tr.why == "time" and tr.t_out == T0 + 15 * HOUR + 30 * MIN


def test_range_breakout_rearms_a_skipped_side_and_uses_the_earlier_exit():
    ctx = Ctx(_orb_path([(15, 1.0990), (25, 1.1005), (35, 1.1015)]), "T2")
    o = T0 + 7 * HOUR
    tr = range_breakout(ctx, o, o + 15 * MIN, o + 195 * MIN, T0 + 15 * HOUR, side_ok=lambda side, k: side > 0,
                        exit_for=lambda side, ms: T0 + 12 * HOUR)
    assert tr.side == 1 and tr.t_in == T0 + 7 * HOUR + 35 * MIN
    assert tr.why == "tms" and tr.t_out == T0 + 12 * HOUR


def test_range_breakout_midpoint_stop_and_narrow_range_skip():
    o = T0 + 7 * HOUR
    ctx = Ctx(_orb_path([(15, 1.0990)]), "N4")
    tr = range_breakout(ctx, o, o + 15 * MIN, o + 195 * MIN, T0 + 15 * HOUR, stop="mid")
    assert tr.side == -1 and tr.sl0 == pytest.approx(1.1005)
    narrow = [1.1005] * 60 + [1.1003, 1.1006] * 8 + [1.1010] * 100
    assert range_breakout(Ctx(minute_ticks(6 * 60, narrow), "T1"), o, o + 15 * MIN, o + 60 * MIN, o + 90 * MIN) is None
```

- [ ] **Step 2: Run to verify they fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_canon.py -q`
Expected: ModuleNotFoundError `research.lab.strategies.canon`.

- [ ] **Step 3: Implement `research/lab/strategies/canon.py`**

```python
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
```

- [ ] **Step 4: Run to verify they pass**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_canon.py -q`
Expected: all pass.

- [ ] **Step 5: No commit.**

---

### Task 3: TMS + ORB family (T1–T5)

**Files:**
- Create: `research/lab/strategies/tms_orb2.py`
- Test: `research/tests/lab/test_lab_refresh_tms_orb.py`

**Interfaces:**
- Consumes: `canon.Tms`, `canon.range_breakout`, `canon.trade`, session table constants; `rules.session_days(ctx, tz, t_open, t_close) -> [(date, open_ms, close_ms)]`.
- Produces: `orb(ctx, tms=False, tms_exit=False)` (T1/T2/T3), `tms_signals(green, red, ha_dir, stoch_dir) -> [(decision_bar, side)]`, `tms_system(ctx, tf=240)` (T4 tf=240, T5 tf=60).

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.strategies.tms_orb2 import orb, tms_signals  # noqa: E402
from research.ticks import day_ms  # noqa: E402

HOUR, MIN = 3_600_000, 60_000
T0 = day_ms(date(2025, 7, 1))


def test_tms_signals_take_candle_1_or_2_only():
    green = np.array([40, 45, 55, 56, 57, 58, 50, 45, 44, 43.0])
    red = np.array([50, 50, 50, 50, 50, 50, 52, 52, 52, 52.0])
    ha = np.array([1, 1, -1, 1, 1, 1, 1, 1, -1, -1])
    st = np.ones(10, int)
    assert tms_signals(green, red, ha, st) == [(3, 1)]
    st[3] = -1
    assert tms_signals(green, red, ha, st) == []


def test_orb_trades_the_london_opening_range_breakout_to_the_session_end():
    prices = [1.1005] * 60 + [1.1000, 1.1010] * 7 + [1.1005] * 15 + [1.1015] * 600
    ts = [T0 + (6 * 60 + k) * MIN for k in range(len(prices))]
    ctx = Ctx(make_chunk(ts, prices, spread=0.0002, symbol="EURUSD"), "T1-ORB")
    orb(ctx)
    (tr,) = ctx.trades
    assert tr.side == 1 and tr.t_in == T0 + 7 * HOUR + 30 * MIN and tr.sl0 == pytest.approx(1.1000)
    assert tr.why == "time" and tr.t_out == T0 + 15 * HOUR + 30 * MIN
```

- [ ] **Step 2: Run to verify they fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_tms_orb.py -q`
Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement `research/lab/strategies/tms_orb2.py`**

```python
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
```

- [ ] **Step 4: Run to verify they pass**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_tms_orb.py -q`
Expected: all pass.

- [ ] **Step 5: No commit.**

---

### Task 4: Asian Range Judas Sweep family (J1–J5)

**Files:**
- Create: `research/lab/strategies/judas2.py`
- Test: `research/tests/lab/test_lab_refresh_judas.py`

**Interfaces:**
- Consumes: `canon.local_ms`, `canon.chunk_days`, `canon.fractal_lows/highs`, `canon.last_fvg`, `canon.trade`, `canon.NY`; `_first_hit`.
- Produces: `judas_ict(ctx, killzones=("london",), midnight_filter=False, tp_mode="range")` (J1–J4), `judas_sweep_close(ctx)` (J5), `asian_days(ctx, b5) -> List[Day]`.

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import bar_ticks, make_chunk  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.strategies.judas2 import judas_ict, judas_sweep_close  # noqa: E402
from research.ticks import day_ms  # noqa: E402

MIN = 60_000
T0 = day_ms(date(2025, 7, 2))     # 20:00 New York on Tue 1 July (EDT) = 00:00 UTC Wed 2 July
FLAT = (1.1025, 1.1030, 1.1020, 1.1025)


def _judas_day():
    """M5 bars from 20:00 NY: Asian range 1.0960-1.1050, a fractal low 1.1015 at bar 70 (01:50 NY), a sweep to
    1.1060 at bar 73 (02:05 NY), a bearish FVG (bar 74 low 1.1030 > bar 76 high 1.1020), MSS close 1.1010 at bar
    76, a retrace to 1.1021 at bar 77, then a fall through the Asian low."""
    bars = [(1.1025, 1.1050, 1.0960, 1.1025)] + [FLAT] * 69 + [(1.1025, 1.1030, 1.1015, 1.1025), FLAT]
    bars += [(1.1025, 1.1040, 1.1022, 1.1038), (1.1038, 1.1060, 1.1036, 1.1045), (1.1045, 1.1046, 1.1030, 1.1032),
             (1.1032, 1.1033, 1.1016, 1.1018), (1.1018, 1.1020, 1.1008, 1.1010), (1.1010, 1.1021, 1.1009, 1.1015),
             (1.1015, 1.1016, 1.0990, 1.0992), (1.0992, 1.0993, 1.0955, 1.0958)] + [(1.0958, 1.0960, 1.0950, 1.0955)] * 10
    ts, px = bar_ticks(T0, 5, bars)
    return make_chunk(ts, px, spread=0.0002, symbol="EURUSD")


def test_j1_sells_the_fvg_retrace_after_the_sweep_and_structure_shift():
    ctx = Ctx(_judas_day(), "J1-ICT")
    judas_ict(ctx)
    (tr,) = ctx.trades
    assert tr.side == -1 and tr.t_in == T0 + (77 * 5 + 2) * MIN and tr.entry == pytest.approx(1.1021)
    assert tr.sl0 == pytest.approx(1.1062) and tr.tp0 == pytest.approx(1.0960) and tr.why == "tp"


def test_j2_midnight_filter_blocks_a_sell_below_the_midnight_open():
    ctx = Ctx(_judas_day(), "J2-ICT-MO")
    judas_ict(ctx, midnight_filter=True)
    assert ctx.trades == []


def test_j3_targets_two_r():
    ctx = Ctx(_judas_day(), "J3-ICT-2R")
    judas_ict(ctx, tp_mode="2r")
    (tr,) = ctx.trades
    assert tr.tp0 == pytest.approx(1.1020 - 2 * 0.0042)


def test_j5_fades_the_m15_sweep_and_close_at_the_next_tick():
    ctx = Ctx(_judas_day(), "J5-SWEEP")
    judas_sweep_close(ctx)
    (tr,) = ctx.trades
    assert tr.side == -1 and tr.t_in == T0 + 75 * 5 * MIN and tr.entry == pytest.approx(1.1032)
    assert tr.sl0 == pytest.approx(1.1062) and tr.why == "tp"
```

- [ ] **Step 2: Run to verify they fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_judas.py -q`
Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement `research/lab/strategies/judas2.py`**

```python
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
from research.sim import _first_hit

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
```

- [ ] **Step 4: Run to verify they pass**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_judas.py -q`
Expected: all pass.

- [ ] **Step 5: No commit.**

---

### Task 5: Literature family (N1–N4)

**Files:**
- Create: `research/lab/strategies/literature.py`
- Test: `research/tests/lab/test_lab_refresh_literature.py`

**Interfaces:**
- Consumes: `canon.local_ms`, `canon.chunk_days`, `canon.trade`, `canon.range_breakout`, `canon.LONDON/TOKYO`, `canon.MINUTE_MS`; `rules.SESSIONS`, `rules.session_days`, `rules._bid_before`; `indicators.atr_sma`.
- Produces: `fix_reversal(ctx)` (N1), `gotobi_days(first, last) -> List[date]`, `gotobi(ctx)` (N2), `intraday_momentum(ctx)` (N3), `london_breakout(ctx)` (N4); `USD_BUY_SIDE`.

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.strategies.literature import (fix_reversal, gotobi, gotobi_days, intraday_momentum,  # noqa: E402
                                                london_breakout)
from research.ticks import day_ms  # noqa: E402

HOUR, MIN = 3_600_000, 60_000


def wiggle(start_ms, minutes, base, step, symbol, spread, jump_at=None, jump=0.0):
    """One tick a minute alternating base +/- step; from jump_at (ms) on the base moves by `jump`."""
    ts = np.array([start_ms + k * MIN for k in range(minutes)], np.int64)
    px = base + step * np.where(np.arange(minutes) % 2 == 0, 1.0, -1.0)
    if jump_at is not None:
        px = px + np.where(ts >= jump_at, jump, 0.0)
    return make_chunk(ts, px, spread=spread, symbol=symbol, lo=day_ms(date(2025, 7, 1)))


def test_gotobi_days_roll_weekends_to_the_friday_before():
    assert gotobi_days(date(2025, 5, 1), date(2025, 5, 31)) == [date(2025, 5, d) for d in (5, 9, 15, 20, 23, 30)]


def test_n1_buys_usd_into_the_london_fix_and_sells_it_after():
    ch = wiggle(day_ms(date(2025, 6, 28)), 4 * 1440, 1.1500, 0.0003, "EURUSD", 0.0001)
    ctx = Ctx(ch, "N1-FIX")
    fix_reversal(ctx)
    day = [tr for tr in ctx.trades if tr.t_in >= day_ms(date(2025, 7, 1))][:2]
    t0 = day_ms(date(2025, 7, 1))
    assert [(tr.side, tr.t_in, tr.t_out) for tr in day] == [(-1, t0 + 13 * HOUR, t0 + 15 * HOUR),
                                                             (1, t0 + 15 * HOUR + MIN, t0 + 17 * HOUR)]


def test_n2_trades_usdjpy_around_the_tokyo_fix_on_gotobi_days():
    ch = wiggle(day_ms(date(2025, 7, 7)), 3 * 1440 + 300, 150.00, 0.03, "USDJPY", 0.01)
    ctx = Ctx(ch, "N2-GOTOBI")
    gotobi(ctx)
    t9, t10 = day_ms(date(2025, 7, 9)), day_ms(date(2025, 7, 10))
    assert [(tr.side, tr.t_in, tr.t_out) for tr in ctx.trades] == [
        (1, t9 + 18 * HOUR, t10 + 55 * MIN), (-1, t10 + 56 * MIN, t10 + 2 * HOUR + 55 * MIN)]


def test_n3_follows_the_first_half_hour_into_the_last_half_hour():
    jump = day_ms(date(2025, 7, 2)) + 13 * HOUR + 30 * MIN
    ch = wiggle(day_ms(date(2025, 6, 30)), 3 * 1440, 44000.0, 5.0, "US30", 2.0, jump_at=jump, jump=100.0)
    ctx = Ctx(ch, "N3-IMOM")
    intraday_momentum(ctx)
    t2 = day_ms(date(2025, 7, 2))
    (tr,) = [x for x in ctx.trades if x.t_in >= t2]
    assert tr.side == 1 and tr.t_in == t2 + 19 * HOUR + 30 * MIN and tr.t_out == t2 + 20 * HOUR and tr.why == "time"


def test_n4_follows_the_london_break_of_the_asian_range():
    t1 = day_ms(date(2025, 7, 1))
    prices = [1.1000, 1.1020] * 210 + [1.1030] * 600       # 23:00 UTC -> 06:00 UTC range, then a break
    ts = [t1 - HOUR + k * MIN for k in range(len(prices))]
    ctx = Ctx(make_chunk(ts, prices, spread=0.0002, symbol="EURUSD"), "N4-LBO")
    london_breakout(ctx)
    (tr,) = ctx.trades
    assert tr.side == 1 and tr.t_in == t1 + 6 * HOUR and tr.sl0 == pytest.approx(1.1010)
    assert tr.t_out == t1 + 15 * HOUR and tr.why == "time"
```

Notes for the implementer: N1 on 2025-07-01 (BST) — 14:00/16:00/18:00 London = 13:00/15:00/17:00 UTC; the post-fix
entry moves one tick past the pre-fix exit (15:01). N2 on Thu 2025-07-10 (gotobi 10th): 03:00 / 09:55 / 11:55 Tokyo =
18:00 UTC on the 9th / 00:55 / 02:55 UTC. N3: New York 10:00 on 2 July = 14:00 UTC; the jump at 13:30 UTC makes
r1 > 0; the trade runs 19:30 → 20:00 UTC.

- [ ] **Step 2: Run to verify they fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_literature.py -q`
Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement `research/lab/strategies/literature.py`**

```python
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
```

- [ ] **Step 4: Run to verify they pass**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_literature.py -q`
Expected: all pass.

- [ ] **Step 5: No commit.**

---

### Task 6: Catalog entries and whole-lab checks

**Files:**
- Modify: `research/lab/catalog.py` (imports; new `REFRESH` and `DROPPED` lists; `CATALOG` order)
- Test: `research/tests/lab/test_lab_refresh_catalog.py` (new)

**Interfaces:**
- Consumes: `tms_orb2.orb`, `tms_orb2.tms_system`, `judas2.judas_ict`, `judas2.judas_sweep_close`, `literature.*`.
- Produces: catalog ids `T1-ORB … N4-LBO` (status `candidate`), `PREFOMC`, `WKGAP`, `CARRY` (status `rejected`, not runnable); `REFRESH_IDS` tuple exported from `catalog.py`.

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_ticks  # noqa: E402
from research.lab.catalog import CATALOG, REFRESH_IDS, by_id  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk, real_ticks  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.ticks import Ticks, day_ms  # noqa: E402


def test_refresh_entries_are_the_fourteen_pre_registered_candidates():
    assert REFRESH_IDS == ("T1-ORB", "T2-TMSORB", "T3-TMSORB-X", "T4-TMS-H4", "T5-TMS-H1", "J1-ICT", "J2-ICT-MO",
                           "J3-ICT-2R", "J4-ICT-2KZ", "J5-SWEEP", "N1-FIX", "N2-GOTOBI", "N3-IMOM", "N4-LBO")
    cat = by_id()
    assert all(cat[i].status == "candidate" and cat[i].runnable for i in REFRESH_IDS)
    assert not ({"BTCUSD", "ETHUSD"} & set(cat["J1-ICT"].symbols))
    assert cat["N2-GOTOBI"].symbols == ("USDJPY",) and "mirror" not in cat["N1-FIX"].variants
    assert {"PREFOMC", "WKGAP", "CARRY"} <= {s.id for s in CATALOG if s.status == "rejected" and not s.runnable}


@needs_ticks
@pytest.mark.parametrize("sid,sym", [("T2-TMSORB", "EURUSD"), ("T3-TMSORB-X", "USDJPY"), ("T5-TMS-H1", "EURUSD"),
                                     ("J1-ICT", "EURUSD"), ("J5-SWEEP", "GBPUSD"), ("N3-IMOM", "US30"),
                                     ("N4-LBO", "EURUSD")])
def test_no_lookahead_cutting_the_ticks_keeps_every_earlier_entry(sid, sym):
    t = real_ticks(sym, date(2025, 1, 6), date(2025, 3, 28))
    cut = day_ms(date(2025, 3, 7))
    lo, hi = day_ms(date(2025, 2, 3)), day_ms(date(2025, 3, 28))
    keep = t.ts < cut
    full = Chunk(sym, "real", 2025, t, lo, hi, instrument(sym))
    part = Chunk(sym, "real", 2025, Ticks(t.ts[keep], t.bid[keep], t.ask[keep]), lo, hi, instrument(sym))
    runs = []
    for ch in (full, part):
        ctx = Ctx(ch, sid)
        by_id()[sid].run(ctx)
        runs.append([(tr.t_in, tr.side, round(tr.sl0, 6), round(tr.tp0, 6)) for tr in ctx.trades if tr.t_in < cut])
    assert runs[0] == runs[1] and len(runs[0]) > 0
```

- [ ] **Step 2: Run to verify they fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_refresh_catalog.py -q`
Expected: ImportError (`REFRESH_IDS`).

- [ ] **Step 3: Implement in `research/lab/catalog.py`**

Add to the imports:

```python
from research.lab.strategies import judas2, literature, rules, tms_orb2
```

(replacing `from research.lab.strategies import rules`). After the `TMSORB = StrategyInfo(...)` block add:

```python
REFRESH_ORIGIN = "strategy refresh 2026-09-26 (docs/superpowers/specs/2026-09-26-strategy-refresh-design.md)"
REFRESH_PENDING = ("Pre-registered 2026-09-26 (research/results/prereg_v2.md); result pending in lab run v2.",)
NO_CRYPTO = tuple(s for s in ALL if s not in ("BTCUSD", "ETHUSD"))
NO_MIRROR = ("real", "shuffle")
ORB_RULES = ("Opening range = bid high/low of the first 15 minutes of the session (local: Tokyo 09:00, London 08:00, "
             "Frankfurt 09:00, New York FX 08:00, New York cash 09:30; BTC/ETH on the cash open). For 3 hours after "
             "it the first tick beyond the range is a breakout; SL at the other side; no target; exit at the session "
             "end (Tokyo 15:00, London 16:30, Frankfurt 17:30, New York 16:00); one trade per session; skipped when "
             "the range is under 3 median spreads.")
TMS_STATE = (" Only breakouts in the direction of the H1 TMS state (last closed H1 bar: bull = TDI green (SMA2 of "
             "RSI13) > red (SMA7), green > 50, Heiken Ashi bullish; bear mirrored); a skipped side re-arms once bid "
             "is back inside the range.")
TMS_RULES = ("TMS (Trading Made Simple): TDI green (SMA2 of RSI13) crosses red (SMA7); enter at the close of candle 1, "
             "else candle 2, if green is still across, the Heiken Ashi bar has the trade's colour and Stoch(8,3,3) %K "
             "is on the trade's side of %D; never candle 3+. SL beyond the last 5 bars' low / high (+ spread for "
             "sells); exit at the bar close where green crosses back; no target.")
JUDAS_RULES = ("ICT: Asian range = M5 high/low 20:00-00:00 New York. In the London killzone (02:00-05:00 New York) a "
               "run beyond one side (sweep extreme H*), then an M5 close through the latest fractal swing before H* "
               "(market structure shift) with a fair value gap between the H* bar and the shift bar; limit at the "
               "gap's near edge until the killzone ends; SL beyond H* (+ spread for sells); TP the other side of the "
               "Asian range, placed only if TP >= SL distance; exit 12:00 New York; one filled trade per day; "
               "BTC/ETH excluded.")
REFRESH = [
    StrategyInfo("T1-ORB", "Opening range breakout (Crabel)", "candidate", REFRESH_ORIGIN, "ORB breakout",
                 "15-min range, ticks", ORB_RULES, REFRESH_PENDING, tms_orb2.orb),
    StrategyInfo("T2-TMSORB", "TMS + ORB", "candidate", REFRESH_ORIGIN, "ORB breakout + TMS bias",
                 "15-min range, H1 bias", ORB_RULES + TMS_STATE, REFRESH_PENDING, tms_orb2.orb, dict(tms=True)),
    StrategyInfo("T3-TMSORB-X", "TMS + ORB, TMS exit", "candidate", REFRESH_ORIGIN, "ORB breakout + TMS bias",
                 "15-min range, H1 bias",
                 ORB_RULES + TMS_STATE + " Also exits at the first H1 close with green crossed against the trade.",
                 REFRESH_PENDING, tms_orb2.orb, dict(tms=True, tms_exit=True)),
    StrategyInfo("T4-TMS-H4", "TMS system on H4", "candidate", REFRESH_ORIGIN, "TDI cross + Heiken Ashi", "H4",
                 TMS_RULES, REFRESH_PENDING, tms_orb2.tms_system, dict(tf=240)),
    StrategyInfo("T5-TMS-H1", "TMS system on H1", "candidate", REFRESH_ORIGIN, "TDI cross + Heiken Ashi", "H1",
                 TMS_RULES, REFRESH_PENDING, tms_orb2.tms_system, dict(tf=60)),
    StrategyInfo("J1-ICT", "Judas sweep, ICT model", "candidate", REFRESH_ORIGIN, "liquidity sweep", "M5",
                 JUDAS_RULES, REFRESH_PENDING, judas2.judas_ict, symbols=NO_CRYPTO),
    StrategyInfo("J2-ICT-MO", "Judas sweep, ICT + midnight open", "candidate", REFRESH_ORIGIN, "liquidity sweep",
                 "M5", JUDAS_RULES + " Sells only above the New York midnight open, buys only below it.",
                 REFRESH_PENDING, judas2.judas_ict, dict(midnight_filter=True), symbols=NO_CRYPTO),
    StrategyInfo("J3-ICT-2R", "Judas sweep, ICT, TP 2R", "candidate", REFRESH_ORIGIN, "liquidity sweep", "M5",
                 JUDAS_RULES + " TP = 2 x the stop distance instead of the range side (no TP check).",
                 REFRESH_PENDING, judas2.judas_ict, dict(tp_mode="2r"), symbols=NO_CRYPTO),
    StrategyInfo("J4-ICT-2KZ", "Judas sweep, ICT, London + NY AM", "candidate", REFRESH_ORIGIN, "liquidity sweep",
                 "M5", JUDAS_RULES + " Also the New York AM killzone 07:00-10:00, same range, still one trade a day.",
                 REFRESH_PENDING, judas2.judas_ict, dict(killzones=("london", "nyam")), symbols=NO_CRYPTO),
    StrategyInfo("J5-SWEEP", "Judas sweep-and-close (no MSS/FVG)", "candidate", REFRESH_ORIGIN, "liquidity sweep",
                 "M15",
                 "Asian range 20:00-00:00 New York. An M15 bar in the London killzone that trades beyond the range and "
                 "closes back inside is faded at the next tick; SL beyond the killzone's extreme so far (+ spread for "
                 "sells); TP the other side of the range, skipped when nearer than the stop; exit 12:00 New York; one "
                 "trade per day. Ablation of J1's structure-shift step.",
                 REFRESH_PENDING, judas2.judas_sweep_close, symbols=NO_CRYPTO),
    StrategyInfo("N1-FIX", "FX fixing reversal (London fix)", "candidate",
                 REFRESH_ORIGIN + "; Krohn, Mueller & Whelan (J. Finance 2024)", "flow", "clock",
                 "Weekdays: long USD 14:00 -> 16:00 London, short USD 16:00 -> 18:00 London; SL 3 x ATR20(H1).",
                 REFRESH_PENDING, literature.fix_reversal, symbols=MEF_PAIRS, variants=NO_MIRROR),
    StrategyInfo("N2-GOTOBI", "Gotobi Tokyo-fix USDJPY", "candidate",
                 REFRESH_ORIGIN + "; Bessho, Sugimoto & Suzuki (2023)", "flow", "clock",
                 "On the 5th/10th/15th/20th/25th/last day (weekend -> Friday before): long USDJPY 03:00 -> 09:55 Tokyo, "
                 "short 09:55 -> 11:55 Tokyo; SL 3 x ATR20(H1).",
                 REFRESH_PENDING, literature.gotobi, symbols=("USDJPY",), variants=NO_MIRROR),
    StrategyInfo("N3-IMOM", "Market intraday momentum", "candidate",
                 REFRESH_ORIGIN + "; Gao, Han, Li & Zhou (JFE 2018)", "intraday momentum", "30 min",
                 "Sign of the return from the previous session close to open + 30 minutes, traded over the session's "
                 "last 30 minutes (US30/USTEC New York 9:30-16:00, DE40 Berlin 9:00-17:30, UK100 London 8:00-16:30); "
                 "SL 2 x ATR20(30-min bars).",
                 REFRESH_PENDING, literature.intraday_momentum, symbols=INDICES),
    StrategyInfo("N4-LBO", "London breakout of the Asian range", "candidate", REFRESH_ORIGIN, "breakout",
                 "ticks",
                 "Range = bid high/low 00:00-07:00 London; the first breakout 07:00-10:00 London is followed; SL at the "
                 "range midpoint; no target; exit 16:00 London; one trade per day; skipped under 3 median spreads.",
                 REFRESH_PENDING, literature.london_breakout, symbols=FX + ("XAUUSD",)),
]
REFRESH_IDS = tuple(s.id for s in REFRESH)
DROPPED = [
    StrategyInfo("PREFOMC", "Pre-FOMC announcement drift", "rejected",
                 "literature (Lucca & Moench 2015), refresh 2026-09-26", "calendar", "event",
                 "Long US equity indices over the 24 hours before scheduled FOMC announcements.",
                 ("Not run: the drift disappeared after 2015 (Kurov, Wolfe & Gilbert).",)),
    StrategyInfo("WKGAP", "FX weekend-gap fade", "rejected", "trading lore, refresh 2026-09-26", "gap fade", "weekly",
                 "Fade the Sunday-open gap of FX pairs towards Friday's close.",
                 ("Not run: gaps above 20 pips are rare and the Sunday-open spread is wide.",)),
    StrategyInfo("CARRY", "FX carry", "rejected", "literature (Lustig & Verdelhan), refresh 2026-09-26", "carry",
                 "weekly", "Long the highest-swap pairs, short the lowest, rebalanced weekly.",
                 ("Not run: the lab's swaps are the 2026 rates held constant, so 2023-25 carry cannot be measured.",)),
]
```

Change the last line to:

```python
CATALOG: List[StrategyInfo] = [*_flowrsi_entries(), JUDAS, TMSORB, *REFRESH, *RESEARCH, *_bank_entries(), *INFO,
                               *DROPPED]
```

- [ ] **Step 4: Run the new tests and the whole suite**

Run: `research/.venv/bin/python -m pytest research/tests -q`
Expected: all pass, including `test_every_runnable_strategy_runs_on_a_short_slice` (runs the 14 new entries on Feb–Mar 2025) and the 7 no-lookahead cases.

- [ ] **Step 5: No commit.**

---

### Task 7: Verdict script

**Files:**
- Create: `research/lab/verdict.py`
- Test: `research/tests/lab/test_lab_verdict.py`

**Interfaces:**
- Consumes: `RUN_DIR/trades.csv.gz` (columns of `run.TRADE_FIELDS`), `RUN_DIR/control.csv` (`strategy,symbol,year,seed,n,net,sum_r,n_r`); `catalog.REFRESH_IDS`.
- Produces: `evaluate(rows, control_by_seed, sid) -> dict` with keys `id, n, mean_r, t, net_2025, net_2026, mean_r_check, control_pct, mirror_net, breadth, symbols, checks (dict name->bool), passed`; `load(run_dir, ids) -> (rows_by_id, control_by_id)`; `render(results) -> str`; CLI `python -m research.lab.verdict RUN_DIR [ID ...]` writing `RUN_DIR/verdict.md`.

- [ ] **Step 1: Write the failing tests**

```python
import csv
import gzip

import pytest

np = pytest.importorskip("numpy")

from research.lab.verdict import evaluate, load, render  # noqa: E402


def _rows(sid, n, r, year, sym="EURUSD", variant="real"):
    return [dict(strategy=sid, symbol=sym, variant=variant, year=str(year), r=str(r), net=str(10.0 * r))
            for _ in range(n)]


def _good(sid):
    rows = []
    for y in (2023, 2024, 2025, 2026):
        rows += _rows(sid, 60, 1.0, y) + _rows(sid, 40, -1.0, y)
    return rows + _rows(sid, 10, 1.0, 2025, variant="mirror")


def test_a_strategy_meeting_every_condition_passes():
    v = evaluate(_good("T1-ORB"), {s: -100.0 for s in range(20)}, "T1-ORB")
    assert v["passed"], v["checks"]
    assert v["n"] == 200 and v["mean_r"] == pytest.approx(0.2) and v["breadth"] == 1.0


def test_each_condition_can_fail_on_its_own():
    ctrl = {s: -100.0 for s in range(20)}
    no_mirror = [r for r in _good("T1-ORB") if r["variant"] == "real"]
    assert not evaluate(no_mirror, ctrl, "T1-ORB")["checks"]["mirror net > 0"]
    assert evaluate([dict(r, strategy="N1-FIX") for r in no_mirror], ctrl, "N1-FIX")["passed"]
    assert not evaluate(_good("T1-ORB"), {s: 1e6 for s in range(20)}, "T1-ORB")["passed"]
    bad_2026 = [r for r in _good("T1-ORB") if not (r["year"] == "2026" and float(r["r"]) > 0)]
    assert not evaluate(bad_2026, ctrl, "T1-ORB")["checks"]["2025 > 0 and 2026 > 0"]
    losers = _good("T1-ORB") + _rows("T1-ORB", 5, -1.0, 2025, sym="GBPUSD") + _rows("T1-ORB", 5, -1.0, 2025, sym="USDJPY")
    assert not evaluate(losers, ctrl, "T1-ORB")["checks"]["breadth >= 60 %"]


def test_load_and_render_a_run_dir(tmp_path):
    fields = ["strategy", "symbol", "variant", "year", "side", "t_in", "t_out", "entry", "exit", "units", "sl0", "tp0",
              "gross", "comm", "swap", "net", "risk_usd", "r", "why"]
    with gzip.open(tmp_path / "trades.csv.gz", "wt", newline="") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore", restval="0")
        w.writeheader()
        w.writerows(_good("T1-ORB") + _rows("OTHER", 3, 1.0, 2025))
    (tmp_path / "control.csv").write_text("strategy,symbol,year,seed,n,net,sum_r,n_r\n"
                                          "T1-ORB,EURUSD,2025,0,5,-3,-1,5\nT1-ORB,EURUSD,2026,0,5,-4,-1,5\n"
                                          "T1-ORB,EURUSD,2023,0,5,99,1,5\n")
    rows, ctrl = load(tmp_path, ["T1-ORB"])
    assert len(rows["T1-ORB"]) == 410 and ctrl["T1-ORB"] == {0: -7.0}
    md = render([evaluate(rows["T1-ORB"], ctrl["T1-ORB"], "T1-ORB")])
    assert "| T1-ORB |" in md and "PASS" in md
```

- [ ] **Step 2: Run to verify they fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_verdict.py -q`
Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement `research/lab/verdict.py`**

```python
"""The pre-registered pass bar of docs/superpowers/specs/2026-09-26-strategy-refresh-design.md applied to a lab run.

  python -m research.lab.verdict RUN_DIR [ID ...]   ->   RUN_DIR/verdict.md   (default ids: catalog.REFRESH_IDS)

Per variant, pooled over its symbols: (1) holdout 2025-26 >= 100 trades, mean net R > 0, t >= 2.5; (2) net $ > 0
in 2025 and in 2026; (3) check period 2023-24 mean net R > 0; (4) holdout net above >= 95 % of the random-entry
control seeds; (5) mirrored holdout net > 0 (not for N1/N2); (6) holdout net > 0 on >= 60 % of the symbols that
traded in the holdout (not for N2)."""
import csv
import gzip
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HOLDOUT, CHECK = (2025, 2026), (2023, 2024)
MIN_TRADES, MIN_T, CONTROL_PCT, BREADTH = 100, 2.5, 95.0, 0.6
NO_MIRROR = {"N1-FIX", "N2-GOTOBI"}
NO_BREADTH = {"N2-GOTOBI"}
NAN = float("nan")


def _mean_t(r):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 2:
        return len(r), (float(r.mean()) if len(r) else NAN), NAN
    sd = float(r.std(ddof=1))
    return len(r), float(r.mean()), float(r.mean() / (sd / math.sqrt(len(r)))) if sd > 0 else NAN


def evaluate(rows, control, sid: str) -> dict:
    """rows: trade dicts of one strategy (all variants); control: {seed: pooled holdout net}."""
    real = [r for r in rows if r["variant"] == "real"]
    hold = [r for r in real if int(r["year"]) in HOLDOUT]
    n, mean_r, t = _mean_t([float(r["r"]) for r in hold])
    _, mean_r_check, _ = _mean_t([float(r["r"]) for r in real if int(r["year"]) in CHECK])
    net = {y: sum(float(r["net"]) for r in real if int(r["year"]) == y) for y in HOLDOUT}
    hold_net = sum(net.values())
    mirror_rows = [r for r in rows if r["variant"] == "mirror" and int(r["year"]) in HOLDOUT]
    mirror = sum(float(r["net"]) for r in mirror_rows) if mirror_rows else NAN
    by_sym = defaultdict(float)
    for r in hold:
        by_sym[r["symbol"]] += float(r["net"])
    breadth = sum(v > 0 for v in by_sym.values()) / len(by_sym) if by_sym else NAN
    seeds = list(control.values())
    control_pct = 100.0 * float(np.mean(np.asarray(seeds) < hold_net)) if seeds else NAN
    checks = {
        "holdout >= 100 trades, mean R > 0, t >= 2.5": n >= MIN_TRADES and mean_r > 0 and t >= MIN_T,
        "2025 > 0 and 2026 > 0": net[2025] > 0 and net[2026] > 0,
        "2023-24 mean R > 0": mean_r_check > 0,
        "beats >= 95 % of control seeds": control_pct >= CONTROL_PCT,
        "mirror net > 0": sid in NO_MIRROR or mirror > 0,
        "breadth >= 60 %": sid in NO_BREADTH or breadth >= BREADTH,
    }
    return dict(id=sid, n=n, mean_r=mean_r, t=t, net_2025=net[2025], net_2026=net[2026], mean_r_check=mean_r_check,
                control_pct=control_pct, mirror_net=mirror, breadth=breadth, symbols=len(by_sym), checks=checks,
                passed=all(checks.values()))


def load(run_dir, ids):
    run_dir, ids = Path(run_dir), set(ids)
    rows = defaultdict(list)
    with gzip.open(run_dir / "trades.csv.gz", "rt") as fh:
        for r in csv.DictReader(fh):
            if r["strategy"] in ids:
                rows[r["strategy"]].append(r)
    control = defaultdict(lambda: defaultdict(float))
    if (run_dir / "control.csv").exists():
        with open(run_dir / "control.csv") as fh:
            for r in csv.DictReader(fh):
                if r["strategy"] in ids and int(r["year"]) in HOLDOUT:
                    control[r["strategy"]][int(r["seed"])] += float(r["net"])
    return dict(rows), {k: dict(v) for k, v in control.items()}


def _f(x, fmt):
    return "" if isinstance(x, float) and math.isnan(x) else format(x, fmt)


def render(results) -> str:
    names = list(results[0]["checks"]) if results else []
    lines = ["# Verdict — strategy refresh 2026-09-26", "",
             "Pass bar: docs/superpowers/specs/2026-09-26-strategy-refresh-design.md (pre-registered). Holdout = "
             "2025-01 .. 2026-09, check = 2023-24.", "",
             "| id | holdout n | mean R | t | 2025 $ | 2026 $ | 2023-24 mean R | ctrl % | mirror $ | breadth | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in results:
        lines.append(f"| {v['id']} | {v['n']} | {_f(v['mean_r'], '+.3f')} | {_f(v['t'], '+.2f')} | "
                     f"{v['net_2025']:+,.0f} | {v['net_2026']:+,.0f} | {_f(v['mean_r_check'], '+.3f')} | "
                     f"{_f(v['control_pct'], '.0f')} | {_f(v['mirror_net'], '+,.0f')} | "
                     f"{_f(v['breadth'], '.0%')} of {v['symbols']} | {'PASS' if v['passed'] else 'fail'} |")
    lines += ["", "## Conditions", "", "| id | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for v in results:
        lines.append(f"| {v['id']} | " + " | ".join("yes" if v["checks"][k] else "**no**" for k in names) + " |")
    passed = [v["id"] for v in results if v["passed"]]
    lines += ["", f"Passed: {', '.join(passed) if passed else 'none'}."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    run_dir = Path(argv[0])
    if len(argv) > 1:
        ids = argv[1:]
    else:
        from research.lab.catalog import REFRESH_IDS
        ids = list(REFRESH_IDS)
    rows, control = load(run_dir, ids)
    results = [evaluate(rows.get(i, []), control.get(i, {}), i) for i in ids]
    (run_dir / "verdict.md").write_text(render(results))
    print(run_dir / "verdict.md")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify they pass**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_verdict.py -q && research/.venv/bin/python -m pytest research/tests -q`
Expected: all pass.

- [ ] **Step 5: No commit.**

---

### Task 8: Freeze, check run, inspection

**Files:**
- Create: `research/results/prereg_v2.md`
- Output: `research/results/lab/v2check/` (run dir)

- [ ] **Step 1: Write `research/results/prereg_v2.md`** with: date/time (UTC), spec path, the 14 ids, the six pass conditions copied from the spec, and the lab code hash from:

Run: `research/.venv/bin/python -c "from research.lab.run import _provenance; print(_provenance())"`

Add an empty "Bug fixes after the freeze" section.

- [ ] **Step 2: Check run (2023–24, real only, no control seeds)**

Run (background, ~20–40 min):
`research/.venv/bin/python -m research.lab.run --strategies T1-ORB T2-TMSORB T3-TMSORB-X T4-TMS-H4 T5-TMS-H1 J1-ICT J2-ICT-MO J3-ICT-2R J4-ICT-2KZ J5-SWEEP N1-FIX N2-GOTOBI N3-IMOM N4-LBO --variants real --years 2023 2024 --seeds 0 --workers 6 --run-dir research/results/lab/v2check`
Expected: every job prints `"errors": 0`.

- [ ] **Step 3: Inspect trade counts** — per strategy × symbol × year from `v2check/trades.csv.gz`; flag cells with 0 trades where the universe says it should trade, or counts above one per session/day where the rules cap them (T1–T3, N4 ≤ 1/session/day; J ≤ 1/day; N1 ≤ 2/day; N2 ≤ 2/gotobi day; N3 ≤ 1/day). Also `errors.csv` empty.

- [ ] **Step 4: Inspect 3 sample trades per family by hand** — print the bars around each (ORB range + breakout tick; TMS lines at the decision bar; Judas Asian range, H*, swing, MSS bar, FVG, fill; N1/N2/N3 clock times in local time) and check them against the rule text. Only bugs are fixed (then rerun Step 2 into a fresh `v2check2`), each logged in `prereg_v2.md`. Do not look at P&L to decide anything.

---

### Task 9: Full run and verdict

- [ ] **Step 1: Full run** (background, 1–3 h):

`research/.venv/bin/python -m research.lab.run --strategies <the 14 ids> --variants real mirror --seeds 20 --workers 6 --run-dir research/results/lab/v2`
Expected: 0 errors.

- [ ] **Step 2: Week shuffle** (positive cells only):

`research/.venv/bin/python -m research.lab.run --strategies <the 14 ids> --shuffle 20 --into research/results/lab/v2`

- [ ] **Step 3: Tables and verdict**

`research/.venv/bin/python -m research.lab.report research/results/lab/v2`
`research/.venv/bin/python -m research.lab.verdict research/results/lab/v2`

- [ ] **Step 4: Protect the run dir:** `chmod -R a-w research/results/lab/v2`.

---

### Task 10: Record and report

**Files:**
- Modify: `research/lab/catalog.py` (findings + status of the 14 entries), `research/STRATEGIES.md` (re-rendered), `research/README.md` (results index row for v2)
- Memory: `strategy-lab.md` / new memory for the refresh verdict

- [ ] **Step 1:** Replace `REFRESH_PENDING` on each entry with its verdict line (holdout n, mean R, t, 2025/2026 $, failed conditions) and set status `rejected` for failures (`candidate` stays only for a pass).
- [ ] **Step 2:** `research/.venv/bin/python -m research.lab.catalog research/results/lab/main research/results/lab/v2`
- [ ] **Step 3:** `research/.venv/bin/python -m pytest research/tests -q` → all pass.
- [ ] **Step 4:** Report to the user in Vietnamese: verdict table, what failed and why, per-family findings, and (only for a pass) the proposed next step (a separate cBot plan + demo forward test). No commit unless asked.
- [ ] **Step 5:** Update memory (project note with the verdict; pointer in MEMORY.md).
