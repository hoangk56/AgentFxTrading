# FlowRSI Entry Screening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a numpy tick simulator of FlowRsiBot in `research/`, prove it reproduces cTrader, and screen 10 candidate entry signals × 2 exits over 15 pairs × 2025/2026 against a pre-registered pass bar.

**Architecture:** The cTrader CLI tick cache is copied from the VPS into `research/data/`. Pure-numpy modules decode ticks, build bid bars, compute indicators, and replay FlowRsiBot's order placement, sizing guardrails and exits tick by tick. A calibration gate compares the replay of the current signal with cTrader jobs #43–#56 and #93 before any screening result is trusted. `screen.py` runs every config and writes a pass/fail report. This plan ends at the verdict. Coding the winner into `FlowRsiBot.cs` (spec part 3) gets its own plan, and only if a config passes.

**Tech Stack:** Python 3.14 (local Mac), numpy, pytest, bash + ssh to the VPS, cTrader CLI backtests through the app's `/api/backtests`.

**Spec:** `docs/superpowers/specs/2026-09-25-flowrsi-entry-redesign-design.md`

## Global Constraints

- Every simulation and backtest starts at **$2000** per pair. The only exception is calibration job #93 (XAUUSD, $10k, `MaxRiskPerTradeMoney=1000`), replayed exactly as it ran.
- Periods: P1 = 2025-01-01..2025-12-31, P2 = 2026-01-01..2026-05-31, P3 = 2026-06-01..2026-09-24 (UTC).
- Pass bar: in each of P1/P2/P3 pooled mean R > 0 and t ≥ 2; pair mean R over P1–P3 > 0 on ≥ 9/15 pairs (no positions = not positive); positions ÷ (15 × months) ≥ 2; pooled mean R above C2's seed mean in every period.
- R per position = net $ ÷ (0.5 % × equity at entry).
- `EnableMacroTmsFilter=false` in every simulated config.
- XAUUSD `MinSlFloorPips=500` in every screening config except C0; C0 keeps the preset 1500.
- No edits to `app/`, `cBot/`, `templates/`, `static/`. Only `.gitignore` changes outside `research/`.
- numpy lives in `research/requirements.txt` and `research/.venv`; the app's `requirements.txt` is not touched.
- Never commit or push unless the user asks; stage only files from this plan (other sessions share the checkout). Never run `scripts/deploy_feature.sh`.
- VPS: `forge@204.168.144.232`. The tick cache is root-owned, so use `sudo -n tar`, and never glob in a remote shell (it expands as forge).
- Run tests from the repo root with `research/.venv/bin/python -m pytest research/tests -q`.

## File Structure

```
.gitignore                     + research/results/
research/
  __init__.py                  empty (lets `python -m research.x` work)
  requirements.txt             numpy, pytest
  pull_cache.sh                VPS tick cache -> research/data/<SYMBOL>/{t1,m15}
  fill_2025.py                 queues the 8 cache-fill backtests (run on the VPS through ssh)
  ticks.py                     .zticks decode, forward-fill, Ticks, day_ms()
  bars.py                      bid OHLC bars from ticks + bar-close event tick; .zbars decode
  indicators.py                ema, rsi (cTrader), sma, atr_sma, bollinger, adx, prior_max/min
  specs.py                     SymbolSpec table, CBOT_DEFAULTS, flowrsi_params, normalize_units, size_units
  sim.py                       make_levels, place_order, exits X1/X2, run_account, Trade
  signals.py                   legacy (C0/C1), E1–E5, random_like (C2), HTF trend, build()
  calibrate.py                 gate against cTrader jobs #43–#56, #93
  screen.py                    runs all configs, summarize/verdict, writes research/results/
  tests/
    conftest.py                repo root on sys.path
    test_ticks.py  test_bars.py  test_indicators.py  test_specs.py
    test_sim.py  test_signals.py  test_calibrate.py  test_screen.py
  data/                        git-ignored (global `data/` rule)
  results/                     git-ignored (added here)
  .venv/                       git-ignored (global `.venv/` rule)
```

Every test module starts with `np = pytest.importorskip("numpy")`, so the repo-level `pytest` run from AGENTS.md skips it on the VPS, where numpy is missing.

---

### Task 1: Scaffold `research/` and decode the tick cache

**Files:**
- Create: `research/__init__.py`, `research/requirements.txt`, `research/ticks.py`, `research/tests/conftest.py`, `research/tests/test_ticks.py`
- Modify: `.gitignore` (append one block)

**Interfaces:**
- Produces: `Ticks(ts: int64[], bid: float64[], ask: float64[])` with `__len__`; `decode_day(path) -> int64[n,3]`; `load_ticks(symbol, start: date, end: date, data_dir=DATA_DIR) -> Ticks`; `day_ms(d: date) -> int`; constants `PRICE_SCALE = 1e5`, `DATA_DIR = research/data`.

- [ ] **Step 1: Create the scaffold**

`research/__init__.py`: empty file.

`research/requirements.txt`:
```
numpy>=2.1
pytest>=8
```

Append to `.gitignore`:
```
# Research outputs (research/data and research/.venv are already covered by data/ and .venv/)
research/results/
```

`research/tests/conftest.py`:
```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
```

Create the venv:
```bash
python3 -m venv research/.venv
```
```bash
research/.venv/bin/pip install -q -r research/requirements.txt
```

- [ ] **Step 2: Write the failing tests**

`research/tests/test_ticks.py`:
```python
import gzip
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from research.ticks import DATA_DIR, day_ms, load_ticks  # noqa: E402


def _write(root, symbol, day, rows):
    d = root / symbol / "t1"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{day:%Y%m%d}.zticks").write_bytes(gzip.compress(np.asarray(rows, dtype="<i8").tobytes()))


def test_forward_fills_unchanged_sides_across_days(tmp_path):
    _write(tmp_path, "EURUSD", date(2026, 1, 1), [[1000, 117000, 117010], [2000, 0, 117020]])
    _write(tmp_path, "EURUSD", date(2026, 1, 2), [[86_401_000, 117005, 0]])
    t = load_ticks("EURUSD", date(2026, 1, 1), date(2026, 1, 2), data_dir=tmp_path)
    assert t.ts.tolist() == [1000, 2000, 86_401_000]
    assert np.allclose(t.bid, [1.17, 1.17, 1.17005])
    assert np.allclose(t.ask, [1.1701, 1.1702, 1.1702])


def test_drops_ticks_until_both_sides_are_known(tmp_path):
    _write(tmp_path, "EURUSD", date(2026, 1, 1), [[1000, 117000, 0], [2000, 0, 117010]])
    t = load_ticks("EURUSD", date(2026, 1, 1), date(2026, 1, 1), data_dir=tmp_path)
    assert t.ts.tolist() == [2000]
    assert len(t) == 1


def test_missing_days_give_empty_ticks(tmp_path):
    t = load_ticks("EURUSD", date(2026, 1, 1), date(2026, 1, 3), data_dir=tmp_path)
    assert len(t) == 0


def test_day_ms_is_utc_midnight():
    assert day_ms(date(2026, 1, 1)) == 1767225600000


REAL = DATA_DIR / "EURUSD" / "t1" / "20260105.zticks"


@pytest.mark.skipif(not REAL.exists(), reason="run research/pull_cache.sh first (Task 8)")
def test_real_day_is_sorted_with_ask_above_bid():
    t = load_ticks("EURUSD", date(2026, 1, 5), date(2026, 1, 5))
    assert len(t) > 10_000
    assert np.all(np.diff(t.ts) >= 0)
    assert np.mean(t.ask >= t.bid) > 0.999
    assert 1.0 < t.bid.mean() < 1.4
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_ticks.py -q`
Expected: collection error `ModuleNotFoundError: No module named 'research.ticks'`.

- [ ] **Step 4: Implement `research/ticks.py`**

```python
"""Decode the cTrader CLI backtest tick cache (.zticks) into bid/ask arrays."""
import gzip
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

PRICE_SCALE = 1e5
DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass
class Ticks:
    ts: np.ndarray   # int64, ms UTC
    bid: np.ndarray  # float64
    ask: np.ndarray  # float64

    def __len__(self) -> int:
        return len(self.ts)


def day_ms(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)


def decode_day(path: Path) -> np.ndarray:
    """(n, 3) int64 rows of one .zticks file: ts ms UTC, bid x1e5, ask x1e5; 0 = side unchanged."""
    raw = gzip.decompress(Path(path).read_bytes())
    return np.frombuffer(raw, dtype="<i8").reshape(-1, 3)


def _ffill(col: np.ndarray) -> np.ndarray:
    """Each 0 becomes the last non-zero value before it; leading zeros stay 0."""
    idx = np.where(col != 0, np.arange(col.size), 0)
    np.maximum.accumulate(idx, out=idx)
    return col[idx]


def load_ticks(symbol: str, start: date, end: date, data_dir: Path = DATA_DIR) -> Ticks:
    """Ticks of the UTC days start..end (both included). Ticks before both sides are known are dropped."""
    days = []
    d = start
    while d <= end:
        path = data_dir / symbol / "t1" / f"{d:%Y%m%d}.zticks"
        if path.exists():
            days.append(decode_day(path))
        d += timedelta(days=1)
    if not days:
        return Ticks(np.empty(0, np.int64), np.empty(0), np.empty(0))
    rows = np.concatenate(days)
    bid, ask = _ffill(rows[:, 1]), _ffill(rows[:, 2])
    keep = (bid != 0) & (ask != 0)
    return Ticks(rows[keep, 0].copy(), bid[keep] / PRICE_SCALE, ask[keep] / PRICE_SCALE)
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_ticks.py -q`
Expected: `4 passed, 1 skipped`. The real-data test is skipped until Task 8.

- [ ] **Step 6: Checkpoint (no commit unless the user asks)**

Files for a later `git add`: `.gitignore research/__init__.py research/requirements.txt research/ticks.py research/tests/conftest.py research/tests/test_ticks.py`

---

### Task 2: Bid bars and the bar-close event tick

**Files:**
- Create: `research/bars.py`, `research/tests/test_bars.py`

**Interfaces:**
- Consumes: `Ticks`, `load_ticks`, `DATA_DIR`, `PRICE_SCALE` (Task 1).
- Produces: `Bars(open_time, o, h, l, c, first_tick, event_tick, minutes)` with `__len__` and `close_time` (int64 ms). `event_tick[i]` = index of the first tick after bar i, where `OnBarClosed` runs; `len(ticks)` for the last bar. `build_bars(t: Ticks, minutes: int) -> Bars`; `decode_zbars(path) -> int64[n,6]`.

- [ ] **Step 1: Write the failing tests**

`research/tests/test_bars.py`:
```python
from datetime import date, timedelta

import pytest

np = pytest.importorskip("numpy")

from research.bars import build_bars, decode_zbars  # noqa: E402
from research.ticks import DATA_DIR, PRICE_SCALE, Ticks, load_ticks  # noqa: E402


def test_bars_bucket_bid_prices_and_mark_the_close_event_tick():
    ts = np.array([0, 60_000, 899_999, 900_000, 1_000_000, 2_700_000], np.int64)
    bid = np.array([1.0, 1.2, 0.9, 1.1, 1.3, 1.05])
    b = build_bars(Ticks(ts, bid, bid + 0.0001), 15)
    assert b.open_time.tolist() == [0, 900_000, 2_700_000]
    assert b.o.tolist() == [1.0, 1.1, 1.05]
    assert b.h.tolist() == [1.2, 1.3, 1.05]
    assert b.l.tolist() == [0.9, 1.1, 1.05]
    assert b.c.tolist() == [0.9, 1.3, 1.05]
    assert b.first_tick.tolist() == [0, 3, 5]
    assert b.event_tick.tolist() == [3, 5, 6]
    assert b.close_time.tolist() == [900_000, 1_800_000, 3_600_000]


def test_h1_bars_align_to_the_utc_hour():
    ts = np.array([0, 3_599_999, 3_600_000], np.int64)
    bid = np.array([1.0, 2.0, 3.0])
    b = build_bars(Ticks(ts, bid, bid), 60)
    assert b.open_time.tolist() == [0, 3_600_000]
    assert b.c.tolist() == [2.0, 3.0]


def _zbar_months():
    for m15 in sorted(DATA_DIR.glob("*/m15")):
        for path in sorted(m15.glob("2026*.zbars")):
            yield m15.parent.name, path


@pytest.mark.skipif(next(_zbar_months(), None) is None, reason="run research/pull_cache.sh first (Task 8)")
def test_m15_bars_match_ctrader_zbars():
    """If no bar times are in common, print zb[:3, 0] against b.open_time[:3]: the .zbars stamp may be
    seconds or the close time. Convert the stamp; do not loosen the price tolerance."""
    checked = 0
    for symbol, path in _zbar_months():
        zb = decode_zbars(path)
        if len(zb) == 0:
            continue
        zb = zb[np.unique(zb[:, 0], return_index=True)[1]]
        year, month = int(path.stem[:4]), int(path.stem[4:])
        start = date(year, month, 1)
        end = min(date(year + month // 12, month % 12 + 1, 1) - timedelta(days=1), date(2026, 9, 24))
        t = load_ticks(symbol, start, end)
        if len(t) == 0:
            continue
        b = build_bars(t, 15)
        common, zi, bi = np.intersect1d(zb[:, 0], b.open_time, return_indices=True)
        assert len(common) >= 0.95 * len(zb), f"{symbol} {path.stem}: {len(common)}/{len(zb)} bar times in common"
        for col, built in ((1, b.o), (2, b.h), (3, b.l), (4, b.c)):
            assert np.allclose(zb[zi, col] / PRICE_SCALE, built[bi], atol=0.5 / PRICE_SCALE), f"{symbol} {path.stem} col {col}"
        checked += 1
        if checked == 3:
            break
    assert checked > 0
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_bars.py -q`
Expected: `ModuleNotFoundError: No module named 'research.bars'`.

- [ ] **Step 3: Implement `research/bars.py`**

```python
"""Bid OHLC bars built from ticks the way cTrader builds them, plus the tick that closes each bar."""
import gzip
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from research.ticks import Ticks

MINUTE_MS = 60_000


@dataclass
class Bars:
    open_time: np.ndarray   # int64 ms, bucket start (UTC-aligned)
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    first_tick: np.ndarray  # index of the bar's first tick
    event_tick: np.ndarray  # first tick after the bar: OnBarClosed runs and orders fill there; len(ticks) if none
    minutes: int

    def __len__(self) -> int:
        return len(self.open_time)

    @property
    def close_time(self) -> np.ndarray:
        return self.open_time + self.minutes * MINUTE_MS


def build_bars(t: Ticks, minutes: int) -> Bars:
    span = minutes * MINUTE_MS
    bucket = t.ts // span
    starts = np.flatnonzero(np.r_[True, bucket[1:] != bucket[:-1]])
    ends = np.r_[starts[1:], len(t)]
    return Bars(
        open_time=bucket[starts] * span,
        o=t.bid[starts],
        h=np.maximum.reduceat(t.bid, starts),
        l=np.minimum.reduceat(t.bid, starts),
        c=t.bid[ends - 1],
        first_tick=starts,
        event_tick=ends,
        minutes=minutes,
    )


def decode_zbars(path: Path) -> np.ndarray:
    """(n, 6) int64 rows of a cTrader .zbars file: ts, open, high, low, close (x1e5), tick count."""
    raw = gzip.decompress(Path(path).read_bytes())
    return np.frombuffer(raw, dtype="<i8").reshape(-1, 6)
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_bars.py -q`
Expected: `2 passed, 1 skipped`.

- [ ] **Step 5: Checkpoint (no commit unless the user asks)**

Files: `research/bars.py research/tests/test_bars.py`

---

### Task 3: Indicators matching the cBot

**Files:**
- Create: `research/indicators.py`, `research/tests/test_indicators.py`

**Interfaces:**
- Produces (all take/return float64 arrays of equal length; NaN where undefined):
  `ema(x, n)` (cTrader EMA: k = 2/(n+1), seeded with x[0]);
  `rsi(close, n)` (cTrader RSI: EMA of period 2n−1 of gains/losses = Wilder);
  `sma(x, n)`; `true_range(h, l, c)`; `atr_sma(h, l, c, n)` (cBot uses `MovingAverageType.Simple`, FlowRsiBot.cs:532);
  `bollinger(c, n=20, k=2.0) -> (lower, mid, upper)`; `adx(h, l, c, n=14)`;
  `prior_max(x, n)` / `prior_min(x, n)` = max/min of the n values **before** i (bar i excluded).

- [ ] **Step 1: Write the failing tests**

`research/tests/test_indicators.py`:
```python
import pytest

np = pytest.importorskip("numpy")

from research.indicators import adx, atr_sma, bollinger, ema, prior_max, prior_min, rsi  # noqa: E402


def test_ema_seeds_with_the_first_value():
    assert np.allclose(ema(np.array([1.0, 2.0, 3.0]), 3), [1.0, 1.5, 2.25])


def test_rsi_is_wilder_smoothing():
    out = rsi(np.array([10.0, 11.0, 10.0]), 2)
    assert out[0] == 100.0 and out[1] == 100.0
    assert out[2] == pytest.approx(100 - 100 / 1.5)


def test_rsi_extremes():
    assert rsi(np.arange(50, dtype=float), 14)[-1] == 100.0
    assert rsi(np.arange(50, 0, -1, dtype=float), 14)[-1] == pytest.approx(0.0)


def test_atr_is_a_simple_average_of_true_range():
    h, l, c = np.array([2.0, 3.0, 4.0]), np.array([1.0, 1.0, 2.0]), np.array([1.5, 2.5, 3.0])
    out = atr_sma(h, l, c, 2)
    assert np.isnan(out[0])
    assert out[1:].tolist() == [1.5, 2.0]


def test_prior_window_excludes_the_current_bar():
    x = np.array([1.0, 5.0, 2.0, 3.0])
    assert np.isnan(prior_max(x, 2)[:2]).all()
    assert prior_max(x, 2)[2:].tolist() == [5.0, 5.0]
    assert prior_min(x, 2)[2:].tolist() == [1.0, 2.0]


def test_bollinger_uses_population_std():
    c = np.array([1.0, 2.0, 3.0])
    lower, mid, upper = bollinger(c, 3, 2.0)
    assert mid[2] == 2.0
    assert upper[2] == pytest.approx(2.0 + 2 * np.std([1.0, 2.0, 3.0]))
    assert lower[2] == pytest.approx(2.0 - 2 * np.std([1.0, 2.0, 3.0]))


def test_adx_high_in_a_trend_low_in_a_range():
    i = np.arange(200, dtype=float)
    assert adx(i + 1.0, i, i + 0.5, 14)[-1] > 25
    c = np.where(np.arange(200) % 2 == 0, 1.0, 1.001)
    assert adx(c + 0.0005, c - 0.0005, c, 14)[-1] < 20
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_indicators.py -q`
Expected: `ModuleNotFoundError: No module named 'research.indicators'`.

- [ ] **Step 3: Implement `research/indicators.py`**

```python
"""Indicators computed the way the cTrader built-ins used by FlowRsiBot compute them."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def ema(x: np.ndarray, n: int) -> np.ndarray:
    """cTrader ExponentialMovingAverage: k = 2 / (n + 1), seeded with the first value."""
    k = 2.0 / (n + 1)
    out = np.empty(len(x))
    acc = 0.0
    for i, v in enumerate(x):
        acc = v if i == 0 else v * k + acc * (1.0 - k)
        out[i] = acc
    return out


def rsi(close: np.ndarray, n: int) -> np.ndarray:
    """cTrader RelativeStrengthIndex: EMA(2n - 1) of gains and losses, i.e. Wilder smoothing."""
    d = np.diff(close, prepend=close[0])
    gain = ema(np.maximum(d, 0.0), 2 * n - 1)
    loss = ema(np.maximum(-d, 0.0), 2 * n - 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 100.0 - 100.0 / (1.0 + gain / loss)
    out[loss == 0] = 100.0
    return out


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.r_[0.0, x])
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def true_range(h: np.ndarray, l: np.ndarray, c: np.ndarray) -> np.ndarray:
    prev = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev), np.abs(l - prev)))
    tr[0] = h[0] - l[0]
    return tr


def atr_sma(h: np.ndarray, l: np.ndarray, c: np.ndarray, n: int) -> np.ndarray:
    """AverageTrueRange(n, MovingAverageType.Simple), FlowRsiBot.cs:532."""
    return sma(true_range(h, l, c), n)


def bollinger(c: np.ndarray, n: int = 20, k: float = 2.0):
    mid = sma(c, n)
    sd = np.full(len(c), np.nan)
    if len(c) >= n:
        sd[n - 1:] = sliding_window_view(c, n).std(axis=1)
    return mid - k * sd, mid, mid + k * sd


def _wilder(x: np.ndarray, n: int) -> np.ndarray:
    return ema(x, 2 * n - 1)


def adx(h: np.ndarray, l: np.ndarray, c: np.ndarray, n: int = 14) -> np.ndarray:
    up = np.diff(h, prepend=h[0])
    down = -np.diff(l, prepend=l[0])
    plus = np.where((up > down) & (up > 0), up, 0.0)
    minus = np.where((down > up) & (down > 0), down, 0.0)
    tr = _wilder(true_range(h, l, c), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi = 100.0 * _wilder(plus, n) / tr
        mdi = 100.0 * _wilder(minus, n) / tr
        dx = 100.0 * np.abs(pdi - mdi) / (pdi + mdi)
    return _wilder(np.nan_to_num(dx), n)


def prior_max(x: np.ndarray, n: int) -> np.ndarray:
    """out[i] = max(x[i-n .. i-1]); NaN for i < n."""
    out = np.full(len(x), np.nan)
    if len(x) > n:
        out[n:] = sliding_window_view(x, n).max(axis=1)[:-1]
    return out


def prior_min(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) > n:
        out[n:] = sliding_window_view(x, n).min(axis=1)[:-1]
    return out
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_indicators.py -q`
Expected: `7 passed`.

- [ ] **Step 5: Checkpoint (no commit unless the user asks)**

Files: `research/indicators.py research/tests/test_indicators.py`

---

### Task 4: Symbol specs, FlowRSI parameters and position sizing

**Files:**
- Create: `research/specs.py`, `research/tests/test_specs.py`

**Interfaces:**
- Consumes: `app.cbot_presets.PRESETS` (repo root on `sys.path`).
- Produces: `SymbolSpec(symbol, pip, tick_size, min_units, step_units, comm_per_unit, usd_per_quote)` with `pip_value` property (USD per pip per unit); `SPECS: dict[str, SymbolSpec]` (15 pairs); `CBOT_DEFAULTS: dict`; `flowrsi_params(symbol, **overrides) -> dict`; `normalize_units(units, spec) -> float`; `size_units(equity, sl_pips, spec, p) -> float` (0.0 = refused).

The numbers below come from reports #27–#42: pip = |close − entry| ÷ pips; min/step = observed deal volumes; `comm_per_unit` = Σ|commissions| ÷ Σvolume (round trip); `usd_per_quote` = gross ÷ (pips × pip × volume), which cTrader held constant for the whole run. ETHUSD's smallest observed deal was 0.04, so its minimum is taken as the 0.01 step. Index tick sizes are approximate; they only feed `minStopBuffer = max(3 × spread, 10 × tick)`, where the spread term dominates.

- [ ] **Step 1: Write the failing tests**

`research/tests/test_specs.py`:
```python
import re
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from research.specs import CBOT_DEFAULTS, SPECS, flowrsi_params, normalize_units, size_units  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def _cbot_defaults():
    src = (ROOT / "cBot" / "FlowRsiBot.cs").read_text()
    pairs = re.findall(r"\[Parameter\([^\n]*?DefaultValue = ([^,)\n]+)[^\n]*\n\s*public \w+ (\w+)", src)
    return {name: value.strip() for value, name in pairs}


def test_cbot_defaults_match_the_cs_source():
    parsed = _cbot_defaults()
    for key, value in CBOT_DEFAULTS.items():
        assert key in parsed, key
        if isinstance(value, bool):
            assert parsed[key] == ("true" if value else "false"), key
        else:
            assert float(parsed[key]) == float(value), key


def test_all_fifteen_pairs_have_specs():
    assert len(SPECS) == 15
    assert SPECS["USDJPY"].pip_value == pytest.approx(0.01 * 0.0062963)


def test_flowrsi_params_layer_defaults_preset_and_overrides():
    p = flowrsi_params("XAUUSD")
    assert p["MinSlFloorPips"] == 1500.0 and p["TrailingStopDistancePips"] == 800.0
    assert p["PartialCloseRatio"] == 0.5
    assert flowrsi_params("XAUUSD", MinSlFloorPips=500.0)["MinSlFloorPips"] == 500.0
    assert flowrsi_params("EURUSD")["MinSlFloorPips"] == 15.0


def test_normalize_rounds_to_the_nearest_step():
    eur = SPECS["EURUSD"]
    assert normalize_units(6666.7, eur) == 7000
    assert normalize_units(6400, eur) == 6000
    assert normalize_units(0.123, SPECS["BTCUSD"]) == pytest.approx(0.12)


def test_size_units_matches_the_cbot_risk_engine():
    p = flowrsi_params("EURUSD")
    assert size_units(2000.0, 15.0, SPECS["EURUSD"], p) == 7000      # $10 / 15 pips -> 6667 -> 7000


def test_xau_min_lot_guardrail_at_2000():
    p, xau = flowrsi_params("XAUUSD"), SPECS["XAUUSD"]
    assert size_units(2000.0, 1500.0, xau, p) == 1                  # $15 == 1.5 x $10: allowed
    assert size_units(2000.0, 1600.0, xau, p) == 0.0                # $16 > $15: refused
    assert size_units(1990.0, 1500.0, xau, p) == 0.0                # 1.5 x $9.95 < $15: refused
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_specs.py -q`
Expected: `ModuleNotFoundError: No module named 'research.specs'`.

- [ ] **Step 3: Implement `research/specs.py`**

```python
"""Per-pair contract data, cost constants and FlowRSI parameters for the simulator."""
from dataclasses import dataclass

import numpy as np

from app.cbot_presets import PRESETS


@dataclass(frozen=True)
class SymbolSpec:
    symbol: str
    pip: float
    tick_size: float
    min_units: float
    step_units: float
    comm_per_unit: float   # USD per unit, round trip
    usd_per_quote: float   # cTrader's quote -> USD factor in the 2026 reports

    @property
    def pip_value(self) -> float:
        """Symbol.PipValue: USD per pip for one unit."""
        return self.pip * self.usd_per_quote


_JPY = dict(pip=0.01, tick_size=0.001, min_units=1000, step_units=1000, usd_per_quote=0.0062963)
_FX = dict(pip=0.0001, tick_size=0.00001, min_units=1000, step_units=1000)
_INDEX = dict(pip=0.1, tick_size=0.1, min_units=0.1, step_units=0.1, comm_per_unit=0.0)

SPECS = {s.symbol: s for s in [
    SymbolSpec("AUDJPY", comm_per_unit=4.167e-5, **_JPY),
    SymbolSpec("EURJPY", comm_per_unit=6.850e-5, **_JPY),
    SymbolSpec("GBPJPY", comm_per_unit=8.000e-5, **_JPY),
    SymbolSpec("USDJPY", comm_per_unit=6.000e-5, **_JPY),
    SymbolSpec("AUDUSD", comm_per_unit=4.159e-5, usd_per_quote=1.0, **_FX),
    SymbolSpec("EURUSD", comm_per_unit=6.733e-5, usd_per_quote=1.0, **_FX),
    SymbolSpec("GBPUSD", comm_per_unit=8.000e-5, usd_per_quote=1.0, **_FX),
    SymbolSpec("USDCAD", comm_per_unit=6.000e-5, usd_per_quote=0.707707, **_FX),
    SymbolSpec("XAUUSD", pip=0.01, tick_size=0.01, min_units=1, step_units=1, comm_per_unit=0.2579, usd_per_quote=1.0),
    SymbolSpec("BTCUSD", pip=0.01, tick_size=0.01, min_units=0.01, step_units=0.01, comm_per_unit=0.0, usd_per_quote=1.0),
    SymbolSpec("ETHUSD", pip=0.01, tick_size=0.01, min_units=0.01, step_units=0.01, comm_per_unit=0.0, usd_per_quote=1.0),
    SymbolSpec("DE40", usd_per_quote=1.13765, **_INDEX),
    SymbolSpec("UK100", usd_per_quote=1.3218, **_INDEX),
    SymbolSpec("US30", usd_per_quote=1.0, **_INDEX),
    SymbolSpec("USTEC", usd_per_quote=1.0, **_INDEX),
]}

# [Parameter] DefaultValue in cBot/FlowRsiBot.cs; test_specs checks every entry against the source.
CBOT_DEFAULTS = {
    "FastRsiPeriod": 7, "SlowRsiPeriod": 14, "RsiCrossLookbackBars": 3,
    "RsiBullishCrossMin": 25.0, "RsiBullishCrossMax": 50.0, "RsiBearishCrossMin": 50.0, "RsiBearishCrossMax": 75.0,
    "EnableSmcFilter": True, "SwingLookback": 5, "EnableFvgDetection": True, "FvgMinPips": 2.0,
    "EquilibriumThreshold": 0.5, "EnableLiquiditySweepFilter": True, "EnableMacroTmsFilter": True,
    "RiskPercentage": 0.5, "MaxRiskPerTradeMoney": 50.0, "MaxMinLotRiskMultiple": 1.5,
    "AtrPeriod": 14, "AtrSlMultiplier": 1.5, "TargetRiskReward": 1.5, "MinSlFloorPips": 15.0, "MaxSpreadPips": 30.0,
    "EnableBreakEven": True, "BreakEvenTriggerRr": 1.0, "MinBreakEvenPips": 10.0, "BreakEvenExtraPips": 0.5,
    "EnableTrailingStop": True, "TrailingStopTriggerRr": 1.2, "TrailingStopDistancePips": 25.0,
    "EnablePartialClose": True, "PartialCloseRatio": 0.5, "RemoveTpOnTrailing": True,
}


def flowrsi_params(symbol: str, **overrides) -> dict:
    """cBot defaults, then the live preset for the symbol, then the overrides."""
    params = dict(CBOT_DEFAULTS)
    params.update(PRESETS[("flowrsi", symbol)]["params"])
    params.update(overrides)
    return params


def normalize_units(units: float, spec: SymbolSpec) -> float:
    """Symbol.NormalizeVolumeInUnits with its default RoundingMode.ToNearest."""
    return round(float(np.floor(units / spec.step_units + 0.5)) * spec.step_units, 8)


def size_units(equity: float, sl_pips: float, spec: SymbolSpec, p: dict) -> float:
    """CalculateDynamicVolumeInUnits (FlowRsiBot.cs:1812); 0.0 when a guardrail refuses the entry."""
    risk = min(equity * p["RiskPercentage"] / 100.0, p["MaxRiskPerTradeMoney"])
    units = max(normalize_units(risk / (sl_pips * spec.pip_value), spec), spec.min_units)
    final = units * sl_pips * spec.pip_value
    if final > p["MaxRiskPerTradeMoney"]:
        return 0.0
    if p["MaxMinLotRiskMultiple"] > 0 and risk > 0 and final > risk * p["MaxMinLotRiskMultiple"]:
        return 0.0
    return units
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_specs.py -q`
Expected: `6 passed`. If `test_xau_min_lot_guardrail_at_2000` fails on the first assertion only, float rounding put 1 × 1500 × 0.01 above 15.0. Keep the cBot's strict `>` and change that assertion to use 1499.0 pips. Do not add an epsilon to `size_units`.

- [ ] **Step 5: Checkpoint (no commit unless the user asks)**

Files: `research/specs.py research/tests/test_specs.py`

---

### Task 5: Order placement, exit X1 and the account loop

**Files:**
- Create: `research/sim.py`, `research/tests/test_sim.py`

**Interfaces:**
- Consumes: `Ticks` (T1), `Bars` (T2), `atr_sma`, `prior_max`, `prior_min` (T3), `SymbolSpec`, `size_units`, `normalize_units`, `flowrsi_params`, `SPECS` (T4).
- Produces:
  - `Trade(side, entry_tick, entry_ts, entry, units, sl_pips, risk_usd, exit_tick=-1, net=0.0, deals=0)` with property `r`.
  - `make_levels(bars, spec, p, sl_mode: "swing"|"atr") -> levels(i, side, bid, ask) -> (sl, tp)`.
  - `place_order(side, tech_sl, tech_tp, bid, ask, equity, spec, p) -> (units, sl, tp) | None`.
  - `run_account(t, bars, sig, levels, spec, p, exit_mode: "X1"|"X2", balance, start_ms=None) -> (list[Trade], refused: int)`.
  - Private helpers used by Task 6: `_first_hit(price, start, lo, hi) -> int`, `_close(tr, j, price, units, spec)`.

- [ ] **Step 1: Write the failing tests**

`research/tests/test_sim.py`:
```python
import pytest

np = pytest.importorskip("numpy")

from research.bars import Bars  # noqa: E402
from research.sim import Trade, make_levels, place_order, run_account  # noqa: E402
from research.specs import SPECS, flowrsi_params  # noqa: E402
from research.ticks import Ticks  # noqa: E402

EUR = SPECS["EURUSD"]
X1 = dict(EnableMacroTmsFilter=False, EnableBreakEven=False, EnableTrailingStop=False, EnablePartialClose=False)


def mk_bars(h, l, c, event_tick=None):
    n = len(c)
    ev = np.arange(n) + 1 if event_tick is None else np.asarray(event_tick)
    return Bars(np.arange(n, dtype=np.int64) * 900_000, np.asarray(c, float), np.asarray(h, float),
                np.asarray(l, float), np.asarray(c, float), np.arange(n), ev, 15)


def test_levels_swing_and_atr_modes():
    bars = mk_bars([1.101] * 20, [1.099] * 20, [1.1] * 20)
    p = flowrsi_params("EURUSD", EnableMacroTmsFilter=False)
    sl, tp = make_levels(bars, EUR, p, "swing")(19, 1, 1.1, 1.1001)
    assert sl == pytest.approx(1.098) and tp == pytest.approx(1.1031)
    sl, tp = make_levels(bars, EUR, p, "atr")(19, 1, 1.1, 1.1001)
    assert sl == pytest.approx(1.097) and tp == pytest.approx(1.1046)
    sl, tp = make_levels(bars, EUR, p, "swing")(19, -1, 1.1, 1.1001)
    assert sl == pytest.approx(1.1021) and tp == pytest.approx(1.097)


def test_place_order_applies_the_floor_and_resizes_on_the_ask_distance():
    p = flowrsi_params("EURUSD")
    units, sl, tp = place_order(1, 1.09950, 1.10080, 1.10000, 1.10002, 2000.0, EUR, p)
    assert sl == pytest.approx(1.09850)
    assert tp == pytest.approx(1.10227)
    assert units == 7000


def test_place_order_refuses_a_stop_on_the_wrong_side():
    p = flowrsi_params("EURUSD", MinSlFloorPips=5.0)
    assert place_order(1, 1.10100, 1.10500, 1.10000, 1.10002, 2000.0, EUR, p) is None


def test_run_account_x1_one_position_at_a_time_and_spread_gate():
    bid = np.array([1.1, 1.1, 1.1005, 1.1010, 1.1020, 1.1035, 1.1, 1.1, 1.1, 1.1])
    ask = bid + 0.0001
    ask[6] = bid[6] + 0.0040                        # 40 pips > MaxSpreadPips 30
    t = Ticks(np.arange(10, dtype=np.int64) * 60_000, bid, ask)
    bars = mk_bars([1.1] * 3, [1.1] * 3, [1.1] * 3, event_tick=[1, 3, 6])
    p = flowrsi_params("EURUSD", **X1)
    levels = lambda i, side, b, a: (b - 0.0020, a + 0.0030)  # noqa: E731
    trades, refused = run_account(t, bars, np.array([1, 1, 1], np.int8), levels, EUR, p, "X1", 2000.0)
    assert refused == 0 and len(trades) == 1
    tr = trades[0]
    assert (tr.entry_tick, tr.exit_tick, tr.units, tr.deals) == (1, 5, 5000, 1)
    assert tr.entry == pytest.approx(1.1001)
    assert tr.net == pytest.approx((1.1035 - 1.1001) * 5000 - 5000 * EUR.comm_per_unit)
    assert tr.risk_usd == pytest.approx(10.0)


def test_x1_sell_takes_profit_at_the_tick_price():
    bid = np.array([1.1, 1.1, 1.1014, 1.0968])
    ask = np.array([1.10001, 1.1001, 1.1015, 1.0969])
    t = Ticks(np.arange(4, dtype=np.int64), bid, ask)
    bars = mk_bars([1.1], [1.1], [1.1], event_tick=[0])
    p = flowrsi_params("EURUSD", **X1)
    levels = lambda i, side, b, a: (1.10200, 1.09700)  # noqa: E731
    trades, _ = run_account(t, bars, np.array([-1], np.int8), levels, EUR, p, "X1", 2000.0)
    tr = trades[0]
    assert tr.entry == 1.1 and tr.exit_tick == 3
    assert tr.net == pytest.approx((1.1 - 1.0969) * tr.units - tr.units * EUR.comm_per_unit)


def test_signals_before_start_ms_are_warm_up_only():
    bid = np.full(5, 1.1)
    t = Ticks(np.array([0, 1, 2, 3, 4], np.int64) * 60_000, bid, bid + 0.0001)
    bars = mk_bars([1.1] * 2, [1.1] * 2, [1.1] * 2, event_tick=[1, 3])
    p = flowrsi_params("EURUSD", **X1)
    levels = lambda i, side, b, a: (b - 0.0020, a + 0.0030)  # noqa: E731
    trades, _ = run_account(t, bars, np.array([1, 1], np.int8), levels, EUR, p, "X1", 2000.0, start_ms=120_000)
    assert [tr.entry_tick for tr in trades] == [3]
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_sim.py -q`
Expected: `ModuleNotFoundError: No module named 'research.sim'`.

- [ ] **Step 3: Implement `research/sim.py` (X2 is added in Task 6)**

```python
"""One pair's signals through FlowRsiBot's order placement and exits, tick by tick."""
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import numpy as np

from research.bars import Bars
from research.indicators import atr_sma, prior_max, prior_min
from research.specs import SymbolSpec, normalize_units, size_units
from research.ticks import Ticks

Levels = Callable[[int, int, float, float], Tuple[float, float]]


@dataclass
class Trade:
    side: int            # +1 buy, -1 sell
    entry_tick: int
    entry_ts: int
    entry: float
    units: float
    sl_pips: float       # initial stop distance from the fill price (_initialSlDistances)
    risk_usd: float      # RiskPercentage of equity at entry: the R unit
    exit_tick: int = -1
    net: float = 0.0
    deals: int = 0

    @property
    def r(self) -> float:
        return self.net / self.risk_usd


def make_levels(bars: Bars, spec: SymbolSpec, p: dict, sl_mode: str) -> Levels:
    """EvaluateStrategySignals step 6 (FlowRsiBot.cs:833-906): technical SL/TP at the bar-close tick.
    sl_mode "swing" = Technical_Swing (the presets), "atr" = ATR_Multiplier (exit X1)."""
    atr = atr_sma(bars.h, bars.l, bars.c, int(p["AtrPeriod"]))
    lookback = int(p["SwingLookback"]) * 3
    hi, lo = prior_max(bars.h, lookback), prior_min(bars.l, lookback)
    pip = spec.pip
    floor = p["MinSlFloorPips"] if p["MinSlFloorPips"] > 0 else 15.0
    mult, rr = p["AtrSlMultiplier"], p["TargetRiskReward"]

    def levels(i: int, side: int, bid: float, ask: float) -> Tuple[float, float]:
        a = atr[i]
        min_sl = max(floor, a / pip)
        if side > 0:
            swing = lo[i] - 0.5 * a if 0 < lo[i] < bid else bid - mult * a
            sl = bid - mult * a if sl_mode == "atr" else swing
            if (bid - sl) / pip < min_sl:
                sl = bid - min_sl * pip
            return sl, ask + (bid - sl) * rr
        swing = hi[i] + 0.5 * a if hi[i] > ask else ask + mult * a
        sl = ask + mult * a if sl_mode == "atr" else swing
        if (sl - ask) / pip < min_sl:
            sl = ask + min_sl * pip
        return sl, bid - (sl - ask) * rr

    return levels


def place_order(side: int, tech_sl: float, tech_tp: float, bid: float, ask: float, equity: float,
                spec: SymbolSpec, p: dict) -> Optional[Tuple[float, float, float]]:
    """ExecuteTechnicalOrder (FlowRsiBot.cs:1718-1788): (units, sl, tp), or None when refused."""
    pip = spec.pip
    price = ask if side > 0 else bid
    sl, tp = tech_sl, tech_tp
    sl_pips = abs(price - sl) / pip
    floor = p["MinSlFloorPips"] if p["MinSlFloorPips"] > 0 else 15.0
    if sl_pips < floor:
        sl_pips = floor
        sl = bid - floor * pip if side > 0 else ask + floor * pip
        min_tp = floor * p["TargetRiskReward"] * pip
        if side > 0 and tp - ask < min_tp:
            tp = ask + min_tp
        elif side < 0 and bid - tp < min_tp:
            tp = bid - min_tp
    units = size_units(equity, sl_pips, spec, p)
    if (side > 0 and sl >= bid) or (side < 0 and sl <= ask):
        return None
    buffer = max((ask - bid) * 3, spec.tick_size * 10)
    if side > 0 and sl >= bid - buffer:
        sl = bid - buffer - 2 * pip
    elif side < 0 and sl <= ask + buffer:
        sl = ask + buffer + 2 * pip
    clamped = abs(price - sl) / pip
    if abs(clamped - sl_pips) > 0.01:
        units = size_units(equity, clamped, spec, p)
    if units <= 0:
        return None
    return units, sl, tp


def _first_hit(price: np.ndarray, start: int, lo: float, hi: float) -> int:
    """First index >= start with price <= lo or price >= hi; len(price) if none."""
    n, size = len(price), 4096
    while start < n:
        seg = price[start:start + size]
        hit = np.flatnonzero((seg <= lo) | (seg >= hi))
        if hit.size:
            return start + int(hit[0])
        start += size
        size *= 2
    return n


def _close(tr: Trade, j: int, price: float, units: float, spec: SymbolSpec) -> None:
    tr.net += (price - tr.entry) * tr.side * units * spec.usd_per_quote - spec.comm_per_unit * units
    tr.deals += 1
    tr.exit_tick = j


def _run_fixed(t: Ticks, tr: Trade, sl: float, tp: float, spec: SymbolSpec) -> None:
    """Exit X1: only the broker's SL/TP; a hit fills at that tick's closing-side price."""
    if tr.side > 0:
        j = _first_hit(t.bid, tr.entry_tick + 1, sl, tp)
    else:
        j = _first_hit(t.ask, tr.entry_tick + 1, tp, sl)
    j = min(j, len(t) - 1)
    _close(tr, j, t.bid[j] if tr.side > 0 else t.ask[j], tr.units, spec)


def run_account(t: Ticks, bars: Bars, sig: np.ndarray, levels: Levels, spec: SymbolSpec, p: dict,
                exit_mode: str, balance: float, start_ms: Optional[int] = None) -> Tuple[List[Trade], int]:
    """sig[i] in {-1, 0, 1} for closed bar i. One position at a time (MaxPositions=1); a signal whose
    close tick falls inside an open position is dropped, as OnBarClosed does with hasOpenPos."""
    trades: List[Trade] = []
    refused = 0
    equity = balance
    busy_until = -1
    for i in np.flatnonzero(sig):
        e = int(bars.event_tick[i])
        if e >= len(t) or e < busy_until:
            continue
        if start_ms is not None and t.ts[e] < start_ms:
            continue
        b, a = float(t.bid[e]), float(t.ask[e])
        if (a - b) / spec.pip > p["MaxSpreadPips"]:
            continue
        side = int(sig[i])
        tech_sl, tech_tp = levels(int(i), side, b, a)
        order = place_order(side, tech_sl, tech_tp, b, a, equity, spec, p)
        if order is None:
            refused += 1
            continue
        units, sl, tp = order
        entry = a if side > 0 else b
        tr = Trade(side, e, int(t.ts[e]), entry, units, abs(entry - sl) / spec.pip,
                   equity * p["RiskPercentage"] / 100.0)
        if exit_mode == "X1":
            _run_fixed(t, tr, sl, tp, spec)
        else:
            _run_flowrsi(t, tr, sl, tp, spec, p)
        equity += tr.net
        busy_until = tr.exit_tick
        trades.append(tr)
    return trades, refused


def _run_flowrsi(t: Ticks, tr: Trade, sl: float, tp: Optional[float], spec: SymbolSpec, p: dict) -> None:
    raise NotImplementedError("exit X2 is Task 6")
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_sim.py -q`
Expected: `6 passed`.

- [ ] **Step 5: Checkpoint (no commit unless the user asks)**

Files: `research/sim.py research/tests/test_sim.py`

---

### Task 6: Exit X2, the FlowRSI position manager

**Files:**
- Modify: `research/sim.py` (replace the `_run_flowrsi` stub; add `_modify_sl`, `_modify_trail`)
- Modify: `research/tests/test_sim.py` (append tests)

**Interfaces:**
- Consumes: `_first_hit`, `_close`, `Trade`, `normalize_units` (Tasks 4–5).
- Produces: `_run_flowrsi(t, tr, sl, tp, spec, p)`, used by `run_account(..., "X2", ...)`.

The replica follows FlowRsiBot.cs:1846–2003 and `SafeModifyPosition` (2075–2179) line by line. On each tick the broker's SL/TP is checked first, then `ManageExits` runs. Rules to keep exactly:
- BE fires when rr ≥ `BreakEvenTriggerRr` and pnl ≥ `MinBreakEvenPips`. The new stop is the zero-loss price: entry ± (round-trip commission in pips + `BreakEvenExtraPips`).
- The partial close happens only right after a *successful* BE modify, and only if both halves stay ≥ min volume.
- The trailing trigger is `TrailingStopTriggerRr`, clamped to 0.8 × the TP's R while a TP exists. It is re-evaluated every tick, so it reverts to 1.2 once the TP is removed.
- Trailing distance = max(`TrailingStopDistancePips`, initial SL × (0.6 if rr ≥ 2.5 else 1)). The step is 10 % of that distance, with a minimum of 1 pip.
- A trailing candidate never goes below the zero-loss price.
- The TP is removed on the first trailing modify after a partial.
- `SafeModifyPosition` rules: the stop only ever ratchets in the profit direction; a stop within `max(3 × spread, 10 × tick)` of price keeps the old stop; a change of 0.5 pip or less is ignored.
- A trailing modify that leaves the stop at or beyond zero-loss net also marks break-even as done, which rules out a later partial.

- [ ] **Step 1: Write the failing tests (append to `research/tests/test_sim.py`)**

```python
from research.sim import _run_flowrsi  # noqa: E402


def _x2_ticks(bids):
    bid = np.array(bids)
    return Ticks(np.arange(len(bid), dtype=np.int64), bid, bid + 0.00001)


def test_x2_break_even_partial_tp_removal_and_trailing():
    t = _x2_ticks([1.09999, 1.10100, 1.10205, 1.10250, 1.10600, 1.10340])
    tr = Trade(1, 0, 0, 1.10000, 10000, 20.0, 10.0)
    _run_flowrsi(t, tr, 1.09800, 1.10300, EUR, flowrsi_params("EURUSD", EnableMacroTmsFilter=False))
    fee = 5000 * EUR.comm_per_unit
    # tick 2: +20.5 pips = 1R -> BE to entry + 1.17 pips and half closed at 1.10205
    # tick 3: 1.25R -> trailing arms, candidate clamps to zero-loss, TP removed (partial done)
    # tick 4: 3R -> stop trails to 1.10600 - 25 pips = 1.10350; tick 5 hits it at 1.10340
    assert tr.deals == 2 and tr.exit_tick == 5
    assert tr.net == pytest.approx((0.00205 * 5000 - fee) + (0.00340 * 5000 - fee))


def test_x2_min_lot_position_cannot_partial_and_keeps_its_tp():
    t = _x2_ticks([1.09999, 1.10205, 1.10250, 1.10310])
    tr = Trade(1, 0, 0, 1.10000, 1000, 20.0, 10.0)
    _run_flowrsi(t, tr, 1.09800, 1.10300, EUR, flowrsi_params("EURUSD", EnableMacroTmsFilter=False))
    assert tr.deals == 1 and tr.exit_tick == 3                  # TP 1.10300 hit at 1.10310
    assert tr.net == pytest.approx(0.00310 * 1000 - 1000 * EUR.comm_per_unit)


def test_x2_stop_out_before_any_trigger_is_a_full_loss():
    t = _x2_ticks([1.09999, 1.10050, 1.09790])
    tr = Trade(1, 0, 0, 1.10000, 10000, 20.0, 10.0)
    _run_flowrsi(t, tr, 1.09800, 1.10300, EUR, flowrsi_params("EURUSD", EnableMacroTmsFilter=False))
    assert tr.deals == 1 and tr.exit_tick == 2
    assert tr.net == pytest.approx(-0.00210 * 10000 - 10000 * EUR.comm_per_unit)


def test_x2_sell_break_even_moves_the_stop_below_entry():
    ask = np.array([1.10000, 1.09795, 1.10000])
    t = Ticks(np.arange(3, dtype=np.int64), ask - 0.00001, ask)
    tr = Trade(-1, 0, 0, 1.10000, 10000, 20.0, 10.0)
    _run_flowrsi(t, tr, 1.10200, 1.09700, EUR, flowrsi_params("EURUSD", EnableMacroTmsFilter=False))
    fee_pips = EUR.comm_per_unit / EUR.pip_value
    zero_loss = 1.10000 - (fee_pips + 0.5) * 0.0001
    fee = 5000 * EUR.comm_per_unit
    # tick 1: 20.5 pips -> BE + half closed at 1.09795; tick 2: ask 1.10000 >= zero-loss stop
    assert tr.deals == 2 and tr.exit_tick == 2
    assert tr.net == pytest.approx((0.00205 * 5000 - fee) + ((1.10000 - 1.10000) * -1 * 5000 - fee))
    assert zero_loss < 1.10000
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_sim.py -q`
Expected: the 4 new tests fail with `NotImplementedError: exit X2 is Task 6`.

- [ ] **Step 3: Replace the stub in `research/sim.py`**

```python
def _modify_sl(side: int, sl: float, target: float, bid: float, ask: float, buffer: float, thr: float):
    """SafeModifyPosition for the BreakEven move: the new stop, or None if nothing would change."""
    final = target
    if (side > 0 and final < sl) or (side < 0 and final > sl):
        final = sl
    if (side > 0 and final >= bid - buffer) or (side < 0 and final <= ask + buffer):
        final = sl
    return final if abs(final - sl) > thr else None


def _modify_trail(side: int, sl: float, tp: Optional[float], cand: float, remove_tp: bool,
                  bid: float, ask: float, buffer: float, thr: float):
    """SafeModifyPosition for the trailing stop: (sl, tp, changed)."""
    final_sl = cand
    if (side > 0 and cand < sl) or (side < 0 and cand > sl):
        final_sl = sl
    if (side > 0 and final_sl >= bid - buffer) or (side < 0 and final_sl <= ask + buffer):
        final_sl = sl
    final_tp = None if remove_tp else tp
    if abs(final_sl - sl) <= thr and (final_tp is None) == (tp is None):
        return sl, tp, False
    return final_sl, final_tp, True


def _run_flowrsi(t: Ticks, tr: Trade, sl: float, tp: Optional[float], spec: SymbolSpec, p: dict) -> None:
    """Exit X2: broker SL/TP, then ManageExits (FlowRsiBot.cs:1846-2003) on every tick."""
    pip, side, entry = spec.pip, tr.side, tr.entry
    units, init_sl = tr.units, tr.sl_pips
    fee_pips = spec.comm_per_unit / spec.pip_value            # |Commissions| x 2 per unit, in pips
    zero_loss = entry + side * (fee_pips + max(0.0, p["BreakEvenExtraPips"])) * pip
    thr = 0.5 * pip
    be_on, trail_on = p["EnableBreakEven"], p["EnableTrailingStop"]
    min_be = p["MinBreakEvenPips"] if p["MinBreakEvenPips"] > 0 else 10.0
    be_done = partial_done = False
    bid, ask, n = t.bid, t.ask, len(t)

    def trail_trigger(cur_tp):
        trig = p["TrailingStopTriggerRr"]
        if cur_tp is not None:
            tp_rr = abs(cur_tp - entry) / pip / init_sl
            if tp_rr > 0 and trig >= tp_rr:
                trig = tp_rr * 0.8
        return trig

    # Until BE or trailing can first trigger, only the broker's SL/TP can act: jump there.
    first = min(max(p["BreakEvenTriggerRr"] * init_sl, min_be) if be_on else np.inf,
                trail_trigger(tp) * init_sl if trail_on else np.inf)
    if side > 0:
        j = _first_hit(bid, tr.entry_tick + 1, sl, min(tp, entry + first * pip))
    else:
        j = _first_hit(ask, tr.entry_tick + 1, max(tp, entry - first * pip), sl)

    while j < n:
        b, a = float(bid[j]), float(ask[j])
        px = b if side > 0 else a
        if (side > 0 and (px <= sl or (tp is not None and px >= tp))) or \
           (side < 0 and (px >= sl or (tp is not None and px <= tp))):
            _close(tr, j, px, units, spec)
            return
        pnl = (b - entry) / pip if side > 0 else (entry - a) / pip
        rr = pnl / init_sl
        buffer = max((a - b) * 3, spec.tick_size * 10)

        if be_on and not be_done and rr >= p["BreakEvenTriggerRr"] and pnl >= min_be \
                and (zero_loss > sl if side > 0 else zero_loss < sl):
            new_sl = _modify_sl(side, sl, zero_loss, b, a, buffer, thr)
            if new_sl is not None:
                sl, be_done = new_sl, True
                ratio = p["PartialCloseRatio"]
                if p["EnablePartialClose"] and 0 < ratio < 1 and not partial_done:
                    vol = normalize_units(units * ratio, spec)
                    if vol >= spec.min_units and units - vol >= spec.min_units:
                        _close(tr, j, px, vol, spec)
                        units -= vol
                        partial_done = True

        if trail_on and rr >= trail_trigger(tp):
            dist = max(p["TrailingStopDistancePips"], init_sl * (0.6 if rr >= 2.5 else 1.0))
            step = max(1.0, dist * 0.1) * pip
            remove_tp = p["RemoveTpOnTrailing"] and partial_done
            if side > 0:
                cand = max(b - dist * pip, zero_loss)
                go = (cand >= sl + step or (remove_tp and tp is not None)) and cand < b
            else:
                cand = min(a + dist * pip, zero_loss)
                go = (cand <= sl - step or (remove_tp and tp is not None)) and cand > a
            if go:
                sl, tp, changed = _modify_trail(side, sl, tp, cand, remove_tp, b, a, buffer, thr)
                if changed and side * (sl - entry) / pip >= fee_pips:
                    be_done = True
        j += 1

    j = n - 1
    _close(tr, j, float(bid[j]) if side > 0 else float(ask[j]), units, spec)
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_sim.py -q`
Expected: `10 passed`. If `test_x2_sell_break_even_moves_the_stop_below_entry` fails with `exit_tick == 3`/`n-1`, ask 1.10000 did not cross the zero-loss stop because the stop is *below* entry for a sell and ask 1.10000 ≥ stop must hold. Check the sign in `zero_loss`, not the test.

- [ ] **Step 5: Checkpoint (no commit unless the user asks)**

Files: `research/sim.py research/tests/test_sim.py`

---

### Task 7: The current FlowRSI signal (C0/C1) and the market bundle

**Files:**
- Create: `research/signals.py`, `research/tests/test_signals.py`

**Interfaces:**
- Consumes: `Bars` (T2), `rsi`, `prior_max`, `prior_min` (T3), `SymbolSpec` (T4).
- Produces: `Market(m15: Bars, h1: Bars, h4: Bars)`; `WARMUP_BARS = 20`; `rsi_cross_signals(f, s, p) -> (bull, bear)`; `smc_flags(bars, p, pip) -> dict[str, bool[]]` with keys `disc prem fvg_b fvg_s sw_l sw_h`; `legacy(m, spec, p) -> int8[]` (raises `ValueError` if `EnableMacroTmsFilter` is on).

Replicates FlowRsiBot.cs:708–798:
- RSI cross within the last `RsiCrossLookbackBars` bars, in the zone, and confirmed on the current bar.
- Swing high/low = max/min of the 15 bars before the current one.
- Discount/premium at the 0.5 equilibrium.
- 3-bar FVG.
- A sweep in the lookback window against the current bar's swing.
- The SMC filter is an OR of those three.
- A buy wins over a sell on the same bar.

- [ ] **Step 1: Write the failing tests**

`research/tests/test_signals.py`:
```python
import pytest

np = pytest.importorskip("numpy")

from research.bars import Bars  # noqa: E402
from research.signals import rsi_cross_signals, smc_flags  # noqa: E402

P = {"RsiCrossLookbackBars": 3, "RsiBullishCrossMin": 25.0, "RsiBullishCrossMax": 50.0,
     "RsiBearishCrossMin": 50.0, "RsiBearishCrossMax": 75.0, "SwingLookback": 1, "EquilibriumThreshold": 0.5,
     "EnableFvgDetection": True, "FvgMinPips": 2.0, "EnableLiquiditySweepFilter": True}


def mk_bars(h, l, c):
    n = len(c)
    return Bars(np.arange(n, dtype=np.int64) * 900_000, np.asarray(c, float), np.asarray(h, float),
                np.asarray(l, float), np.asarray(c, float), np.arange(n), np.arange(n) + 1, 15)


def test_rsi_cross_stays_valid_for_the_lookback_while_confirmed():
    f = np.array([40.0, 30.0, 45.0, 46.0, 47.0, 48.0])
    s = np.array([42.0, 40.0, 41.0, 42.0, 43.0, 44.0])
    bull, bear = rsi_cross_signals(f, s, P)
    assert bull.tolist() == [False, False, True, True, True, False]
    assert not bear.any()


def test_rsi_cross_outside_the_zone_is_ignored():
    f = np.array([20.0, 15.0, 22.0])
    s = np.array([21.0, 18.0, 20.0])                      # slow RSI 20 < 25 at the cross
    bull, _ = rsi_cross_signals(f, s, P)
    assert not bull.any()


def test_smc_discount_and_sell_side_sweep():
    b = mk_bars(h=[1.02, 1.03, 1.04, 1.05, 1.04, 1.03],
                l=[1.00, 1.00, 1.01, 1.02, 1.01, 0.995],
                c=[1.01, 1.02, 1.03, 1.04, 1.02, 1.015])
    f = smc_flags(b, P, 0.0001)
    assert f["disc"][5] and not f["prem"][5]
    assert f["sw_l"][5] and not f["sw_h"][5]
    assert not f["fvg_b"][5] and not f["fvg_s"][5]


def test_smc_bullish_fvg():
    b = mk_bars(h=[1.0000, 1.0010, 1.0040], l=[0.9990, 1.0000, 1.0003], c=[0.9995, 1.0008, 1.0035])
    assert smc_flags(b, P, 0.0001)["fvg_b"][2]
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_signals.py -q`
Expected: `ModuleNotFoundError: No module named 'research.signals'`.

- [ ] **Step 3: Implement `research/signals.py`**

```python
"""Entry signals on closed M15 bars: +1 buy, -1 sell, 0 none; index i = the bar that just closed."""
from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from research.bars import Bars
from research.indicators import prior_max, prior_min, rsi
from research.specs import SymbolSpec

WARMUP_BARS = 20   # EvaluateStrategySignals returns while index < 20


@dataclass
class Market:
    m15: Bars
    h1: Bars
    h4: Bars


def _any_last(x: np.ndarray, lookback: int) -> np.ndarray:
    """out[i] = any(x[i-lookback+1 .. i])."""
    cs = np.cumsum(x.astype(np.int64))
    prev = np.r_[np.zeros(lookback, np.int64), cs[:-lookback]]
    return (cs - prev) > 0


def rsi_cross_signals(f: np.ndarray, s: np.ndarray, p: dict) -> Tuple[np.ndarray, np.ndarray]:
    """FlowRsiBot.cs:717-746: a fast/slow cross inside the zone within the lookback, confirmed now."""
    n = len(f)
    up, down = np.zeros(n, bool), np.zeros(n, bool)
    up[1:] = (f[:-1] <= s[:-1]) & (f[1:] > s[1:])
    down[1:] = (f[:-1] >= s[:-1]) & (f[1:] < s[1:])
    bull_x = up & (s >= p["RsiBullishCrossMin"]) & (s <= p["RsiBullishCrossMax"])
    bear_x = down & (s >= p["RsiBearishCrossMin"]) & (s <= p["RsiBearishCrossMax"])
    lookback = max(1, int(p["RsiCrossLookbackBars"]))
    return _any_last(bull_x, lookback) & (f > s), _any_last(bear_x, lookback) & (f < s)


def smc_flags(b: Bars, p: dict, pip: float) -> Dict[str, np.ndarray]:
    """FlowRsiBot.cs:750-788: premium/discount, 3-bar FVG and liquidity sweeps."""
    n = len(b)
    window = int(p["SwingLookback"]) * 3
    hi, lo = prior_max(b.h, window), prior_min(b.l, window)
    rng, eq = hi - lo, p["EquilibriumThreshold"]
    with np.errstate(invalid="ignore"):
        disc = (rng > 0) & (b.c <= lo + rng * eq)
        prem = (rng > 0) & (b.c >= lo + rng * (1.0 - eq))
    fvg_b, fvg_s = np.zeros(n, bool), np.zeros(n, bool)
    if p["EnableFvgDetection"]:
        gap = p["FvgMinPips"] * pip
        fvg_b[2:] = (b.l[2:] - b.h[:-2] >= gap) & (b.c[2:] >= b.h[:-2])
        fvg_s[2:] = (b.l[:-2] - b.h[2:] >= gap) & (b.c[2:] <= b.l[:-2])
    sw_l, sw_h = np.zeros(n, bool), np.zeros(n, bool)
    if p["EnableLiquiditySweepFilter"]:
        lookback = max(1, int(p["RsiCrossLookbackBars"]))
        for i in range(window, n):
            k0 = max(1, i - lookback + 1)
            sw_l[i] = bool(np.any((b.l[k0:i + 1] < lo[i]) & (b.c[k0:i + 1] > lo[i])))
            sw_h[i] = bool(np.any((b.h[k0:i + 1] > hi[i]) & (b.c[k0:i + 1] < hi[i])))
    return {"disc": disc, "prem": prem, "fvg_b": fvg_b, "fvg_s": fvg_s, "sw_l": sw_l, "sw_h": sw_h}


def legacy(m: Market, spec: SymbolSpec, p: dict) -> np.ndarray:
    """The live FlowRSI entry (steps 1-5) with the Macro TMS filter off."""
    if p.get("EnableMacroTmsFilter", True):
        raise ValueError("legacy() replicates FlowRSI with EnableMacroTmsFilter=false only")
    b = m.m15
    bull, bear = rsi_cross_signals(rsi(b.c, int(p["FastRsiPeriod"])), rsi(b.c, int(p["SlowRsiPeriod"])), p)
    buy, sell = bull.copy(), bear.copy()
    if p["EnableSmcFilter"]:
        f = smc_flags(b, p, spec.pip)
        buy &= f["disc"] | f["fvg_b"] | f["sw_l"]
        sell &= f["prem"] | f["fvg_s"] | f["sw_h"]
    sig = np.where(buy, 1, np.where(sell, -1, 0)).astype(np.int8)
    sig[:WARMUP_BARS] = 0
    return sig
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_signals.py -q`
Expected: `4 passed`.

- [ ] **Step 5: Checkpoint (no commit unless the user asks)**

Files: `research/signals.py research/tests/test_signals.py`

---

### Task 8: Data: fill the 2025 cache, pull ticks and reports

**Files:**
- Create: `research/fill_2025.py`, `research/pull_cache.sh`

**Interfaces:**
- Produces on disk: `research/data/<SYMBOL>/t1/*.zticks` (2024-12-29..2026-09-24 for all 15), `research/data/<SYMBOL>/m15/*.zbars`, `research/data/reports/{43..56,93}.json`.

Start Step 1 as soon as this plan is approved, because the VPS needs ~40–60 min. Tasks 1–7 can go on meanwhile.

- [ ] **Step 1: Queue the 8 cache-fill backtests on the VPS**

`research/fill_2025.py`:
```python
"""Queue the cTrader backtests that fill the 2025 tick cache for the 8 pairs that lack it.
Live presets, $2000, ticks. Run on the VPS:  ssh forge@204.168.144.232 'python3 -' < research/fill_2025.py"""
import json
import urllib.request

API = "http://127.0.0.1:8000/api/backtests"
PAIRS = ["BTCUSD", "DE40", "ETHUSD", "UK100", "US30", "USDCAD", "USTEC", "XAUUSD"]

for symbol in PAIRS:
    body = {"bot_name": f"cbot-demo-demo-{symbol.lower()}-all-flowrsi", "start": "2025-01-01",
            "end": "2025-12-31", "data_mode": "ticks", "balance": 2000.0,
            "note": "cache fill 2025", "overrides": {}}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        print(resp.status, resp.read().decode(), symbol)
```

Run:
```bash
ssh forge@204.168.144.232 'python3 -' < research/fill_2025.py
```
Expected: 8 lines `201 {"id":…,"status":"queued",…}`.

- [ ] **Step 2: Wait for the jobs, then check the cache**

Poll until none of the 8 jobs is `queued`/`running`. A job can fail once with "aborted by timeout" on a cold cache; the worker reruns it once (PR #56):
```bash
ssh forge@204.168.144.232 'curl -s http://127.0.0.1:8000/api/backtests' | python3 -c "import json,sys; [print(j['id'], j['symbol'], j['status'], j.get('error')) for j in json.load(sys.stdin)['jobs'] if j.get('note') == 'cache fill 2025']"
```
Expected once finished: 8 × `done` (XAUUSD may report 0 positions; it still fills the cache).

Then:
```bash
ssh forge@204.168.144.232 'D=/var/lib/docker/volumes/agentfx-bt-cache/_data/V1/demo_e5322e87; for s in AUDJPY AUDUSD BTCUSD DE40 ETHUSD EURJPY EURUSD GBPJPY GBPUSD UK100 US30 USDCAD USDJPY USTEC XAUUSD; do echo "$s $(sudo -n ls $D/$s/t1 | grep -c ^2025)"; done'
```
Expected: `365` for every pair. For a job that ended `failed`, POST that one pair again with the same body and re-check.

- [ ] **Step 3: Pull the cache to the Mac**

`research/pull_cache.sh`:
```bash
#!/bin/bash
# Copy the cTrader backtest cache (ticks + m15 bars) from the VPS into research/data/<SYMBOL>/.
# Root-owned on the VPS, so tar runs under sudo; paths are spelled out (a remote glob expands as forge).
set -euo pipefail
VPS=forge@204.168.144.232
CACHE=/var/lib/docker/volumes/agentfx-bt-cache/_data/V1/demo_e5322e87
DEST="$(cd "$(dirname "$0")" && pwd)/data"
SYMBOLS=${*:-"AUDJPY AUDUSD BTCUSD DE40 ETHUSD EURJPY EURUSD GBPJPY GBPUSD UK100 US30 USDCAD USDJPY USTEC XAUUSD"}
for s in $SYMBOLS; do
  mkdir -p "$DEST/$s"
  ssh "$VPS" "sudo -n tar cf - -C $CACHE/$s t1 m15" | tar xf - -C "$DEST/$s"
  echo "$s: $(ls "$DEST/$s/t1" | wc -l | tr -d ' ') tick days"
done
```
Run:
```bash
chmod +x research/pull_cache.sh && research/pull_cache.sh
```
Expected: 15 lines. Each pair reports ≥ 632 tick days (365 for 2025 + 267 for 2026, plus a few days before the start). About 4 GB, stays gzip-compressed on disk.

- [ ] **Step 4: Pull the calibration reports**

```bash
mkdir -p research/data/reports && for i in 43 44 45 46 47 48 49 50 51 52 53 54 55 56 93; do ssh forge@204.168.144.232 "cat /home/forge/AgentFxTrading/webui_data/backtests/$i.json" > research/data/reports/$i.json; done && ls -la research/data/reports
```
Expected: 15 files of 2–6 MB each.

- [ ] **Step 5: Run the real-data tests**

Run: `research/.venv/bin/python -m pytest research/tests/test_ticks.py research/tests/test_bars.py -q`
Expected: `8 passed` (nothing skipped). If `test_m15_bars_match_ctrader_zbars` fails, follow its docstring. Tick decoding and bar alignment are prerequisites for the gate in Task 9.

- [ ] **Step 6: Checkpoint (no commit unless the user asks)**

Files: `research/fill_2025.py research/pull_cache.sh` (the data itself is git-ignored).

---

### Task 9: Calibration gate

**Files:**
- Create: `research/calibrate.py`, `research/tests/test_calibrate.py`

**Interfaces:**
- Consumes: `load_ticks`, `day_ms`, `DATA_DIR` (T1), `build_bars` (T2), `SPECS`, `flowrsi_params` (T4), `make_levels`, `run_account`, `Trade` (T5–6), `Market`, `legacy` (T7).
- Produces: `ctrader_positions(report) -> list[(entry_ms, side, units, net, r)]`; `match(ct, sim, tol_ms=900_000) -> list[(ct_row, Trade)]`; CLI `python -m research.calibrate [--show SYMBOL]` that exits 0 on PASS and 1 on FAIL.

Gate (spec): every pair ≥ 90 % of cTrader positions matched (same side, entry within one M15 bar); ≥ 95 % of matched positions with identical volume; pooled mean R within ±0.03R.

- [ ] **Step 1: Write the failing tests**

`research/tests/test_calibrate.py`:
```python
import pytest

np = pytest.importorskip("numpy")

from research.calibrate import ctrader_positions, match  # noqa: E402
from research.sim import Trade  # noqa: E402


def test_ctrader_positions_group_partial_deals():
    report = {"history": {"items": [
        {"entryTime": 1000, "direction": "buy", "entryPrice": 1.1, "closeTime": 5000, "volume": 5000, "net": 10.0, "balance": 2010.0},
        {"entryTime": 1000, "direction": "buy", "entryPrice": 1.1, "closeTime": 9000, "volume": 5000, "net": 5.0, "balance": 2015.0},
        {"entryTime": 20000, "direction": "sell", "entryPrice": 1.2, "closeTime": 30000, "volume": 7000, "net": -10.075, "balance": 2004.925},
    ]}}
    pos = ctrader_positions(report)
    assert [(p[0], p[1], p[2]) for p in pos] == [(1000, 1, 10000), (20000, -1, 7000)]
    assert pos[0][4] == pytest.approx(15.0 / (0.005 * 2000.0))
    assert pos[1][4] == pytest.approx(-10.075 / (0.005 * 2015.0))


def test_match_needs_same_side_within_one_bar():
    ct = [(0, 1, 1000, 5.0, 0.5), (3_600_000, -1, 1000, -10.0, -1.0)]
    sim = [Trade(1, 0, 60_000, 1.1, 1000, 20, 10), Trade(-1, 0, 3_600_000 + 1_000_000, 1.1, 1000, 20, 10)]
    pairs = match(ct, sim)
    assert len(pairs) == 1 and pairs[0][0] == ct[0]
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_calibrate.py -q`
Expected: `ModuleNotFoundError: No module named 'research.calibrate'`.

- [ ] **Step 3: Implement `research/calibrate.py`**

```python
"""Gate: the simulator must replay C0 + X2 the way cTrader ran jobs #43-#56 ($2000) and #93 (XAU, $10k)."""
import argparse
import json
import math
import sys
from datetime import date, datetime, timezone

from research.bars import build_bars
from research.signals import Market, legacy
from research.sim import make_levels, run_account
from research.specs import SPECS, flowrsi_params
from research.ticks import DATA_DIR, day_ms, load_ticks

JOBS = {43: "AUDJPY", 44: "AUDUSD", 45: "BTCUSD", 46: "DE40", 47: "ETHUSD", 48: "EURJPY", 49: "EURUSD",
        50: "GBPJPY", 51: "GBPUSD", 52: "UK100", 53: "US30", 54: "USDCAD", 55: "USDJPY", 56: "USTEC",
        93: "XAUUSD"}
START, END, WARMUP_FROM = date(2026, 1, 1), date(2026, 9, 24), date(2025, 12, 25)
BAR_MS = 15 * 60_000


def ctrader_positions(report: dict):
    """History deals grouped into positions: (entry_ms, side, units, net, r), r = net / 0.5 % of balance before."""
    groups = {}
    for d in sorted(report["history"]["items"], key=lambda d: d["closeTime"]):
        key = (d["entryTime"], d["direction"], d["entryPrice"])
        g = groups.setdefault(key, {"units": 0.0, "net": 0.0, "before": d["balance"] - d["net"]})
        g["units"] += d["volume"]
        g["net"] += d["net"]
    return [(int(k[0]), 1 if k[1] == "buy" else -1, g["units"], g["net"], g["net"] / (0.005 * g["before"]))
            for k, g in sorted(groups.items())]


def match(ct, sim, tol_ms: int = BAR_MS):
    used, pairs = set(), []
    for row in ct:
        best = None
        for k, tr in enumerate(sim):
            if k in used or tr.side != row[1]:
                continue
            dt = abs(tr.entry_ts - row[0])
            if dt <= tol_ms and (best is None or dt < best[0]):
                best = (dt, k)
        if best is not None:
            used.add(best[1])
            pairs.append((row, sim[best[1]]))
    return pairs


def replay(job: int, symbol: str):
    report = json.loads((DATA_DIR / "reports" / f"{job}.json").read_text())
    balance = float(report["main"]["startingCapital"])
    over = {"EnableMacroTmsFilter": False}
    if job == 93:
        over["MaxRiskPerTradeMoney"] = 1000.0
    spec, p = SPECS[symbol], flowrsi_params(symbol, **over)
    t = load_ticks(symbol, WARMUP_FROM, END)
    m = Market(build_bars(t, 15), build_bars(t, 60), build_bars(t, 240))
    trades, refused = run_account(t, m.m15, legacy(m, spec, p), make_levels(m.m15, spec, p, "swing"),
                                  spec, p, "X2", balance, day_ms(START))
    return ctrader_positions(report), trades, refused


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _stamp(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", help="print unmatched cTrader positions of this symbol")
    ap.add_argument("--only", nargs="*", help="symbols to replay (default: all 15)")
    args = ap.parse_args(argv)
    ok, ct_r, sim_r, vol_ok, vol_n = True, [], [], 0, 0
    for job, symbol in JOBS.items():
        if args.only and symbol not in args.only:
            continue
        ct, sim, refused = replay(job, symbol)
        pairs = match(ct, sim)
        rate = len(pairs) / len(ct) if ct else 1.0
        vol_n += len(pairs)
        vol_ok += sum(1 for row, tr in pairs if math.isclose(row[2], tr.units, rel_tol=1e-9, abs_tol=1e-9))
        ct_r += [row[4] for row in ct]
        sim_r += [tr.r for tr in sim]
        ok &= rate >= 0.90
        print(f"#{job} {symbol:7s} cTrader {len(ct):4d}  sim {len(sim):4d}  matched {rate:6.1%}  "
              f"mR {_mean([r[4] for r in ct]):+.3f} vs {_mean([tr.r for tr in sim]):+.3f}  refused {refused}")
        if args.show == symbol:
            matched = {id(row) for row, _ in pairs}
            for row in [r for r in ct if id(r) not in matched][:15]:
                near = min(sim, key=lambda tr: abs(tr.entry_ts - row[0]), default=None)
                print(f"   unmatched {_stamp(row[0])} side {row[1]:+d} units {row[2]:g}   nearest sim "
                      + (f"{_stamp(near.entry_ts)} side {near.side:+d} units {near.units:g}" if near else "-"))
    vol_rate = vol_ok / vol_n if vol_n else 0.0
    diff = _mean(sim_r) - _mean(ct_r)
    ok &= vol_rate >= 0.95 and abs(diff) <= 0.03
    print(f"pooled: volume match {vol_rate:.1%}  mR cTrader {_mean(ct_r):+.3f} sim {_mean(sim_r):+.3f} (diff {diff:+.3f})")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the unit tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_calibrate.py -q`
Expected: `2 passed`.

- [ ] **Step 5: Run the gate**

Run: `research/.venv/bin/python -m research.calibrate`
Expected: 15 lines, a `pooled:` line and `PASS`. Previous replica for comparison: 261/270 AUDJPY entries matched, exit pips p90 diff 0.33.

- [ ] **Step 6: If FAIL, debug one pair at a time until PASS**

Run `research/.venv/bin/python -m research.calibrate --only EURUSD --show EURUSD` and compare the unmatched stamps with the nearest sim entry. Check these known sources of drift, in order, and fix the simulator (never the gate thresholds):
1. **Missing entries across the whole period** usually means the RSI is wrong. Verify the `2n−1` EMA and that `rsi` is computed on bid closes.
2. **Entries one bar late or early:** the bar alignment or `event_tick`. Re-run `test_bars.py`.
3. **Extra sim entries** clustered after big moves: the sweep window, or `prior_max`/`prior_min` including the current bar.
4. **Volume mismatches:** `normalize_units` rounding, `usd_per_quote`, or the resize branch in `place_order`.
5. **mR off with good matching:** the exit. Compare the per-position R of the matched pairs, and check the TP/SL fill price (tick price) and the partial-close condition.

After each fix, add a unit test that pins the corrected behaviour in the matching test module. Then re-run the whole suite: `research/.venv/bin/python -m pytest research/tests -q`.

- [ ] **Step 7: Checkpoint (no commit unless the user asks)**

Files: `research/calibrate.py research/tests/test_calibrate.py` plus any simulator fixes. Record the PASS table in the spec under a new "Calibration result" heading.

---

### Task 10: Candidate signals, trend filters and the random control

**Files:**
- Modify: `research/signals.py` (append), `research/tests/test_signals.py` (append)

**Interfaces:**
- Consumes: `ema`, `rsi`, `bollinger`, `adx`, `prior_max`, `prior_min` (T3), `legacy`, `Market`, `WARMUP_BARS` (T7).
- Produces:
  - `htf_index(m15, htf) -> int[]` (last HTF bar closed by each M15 close, −1 if none);
  - `htf_trend(htf, period=50) -> int8[]`; `trend_on_m15(m15, htf) -> int8[]`;
  - pure signal functions `pullback`, `rsi2_extreme`, `bb_fade`, `donchian_breakout`, `reverse_extreme`, `random_like`;
  - `NAMES` (all config names) and `build(name, m, spec, p, seed=None, cache=None) -> int8[]`.

- [ ] **Step 1: Write the failing tests (append to `research/tests/test_signals.py`)**

```python
from research.signals import (bb_fade, donchian_breakout, htf_index, htf_trend, pullback,  # noqa: E402
                              random_like, reverse_extreme, rsi2_extreme)


def test_htf_index_uses_only_closed_higher_bars():
    m15 = Bars(np.arange(6, dtype=np.int64) * 900_000, *(np.ones(6),) * 4, np.arange(6), np.arange(6) + 1, 15)
    h1 = Bars(np.array([0, 3_600_000], np.int64), *(np.ones(2),) * 4, np.arange(2), np.arange(2) + 1, 60)
    assert htf_index(m15, h1).tolist() == [-1, -1, -1, 0, 0, 0]


def test_htf_trend_needs_price_and_slope_and_warm_up():
    n = 120
    up = Bars(np.arange(n, dtype=np.int64) * 3_600_000, *(np.arange(n, dtype=float),) * 4, np.arange(n), np.arange(n) + 1, 60)
    tr = htf_trend(up, 50)
    assert (tr[:50] == 0).all() and tr[-1] == 1


def test_pullback_reentry_through_40_and_60():
    r = np.array([45.0, 38.0, 41.0, 50.0, 62.0, 58.0])
    trend = np.array([1, 1, 1, 1, -1, -1], np.int8)
    assert pullback(r, trend).tolist() == [0, 0, 1, 0, 0, -1]


def test_rsi2_extreme_with_and_without_trend():
    r2 = np.array([5.0, 50.0, 95.0])
    assert rsi2_extreme(r2, np.array([1, 1, 1], np.int8)).tolist() == [1, 0, 0]
    assert rsi2_extreme(r2, None).tolist() == [1, 0, -1]


def test_bb_fade_and_adx_gate():
    c = np.array([1.0, 0.8, 0.95, 1.2, 1.05])
    lower, upper = np.full(5, 0.9), np.full(5, 1.1)
    assert bb_fade(c, lower, upper).tolist() == [0, 0, 1, 0, -1]
    assert bb_fade(c, lower, upper, np.full(5, 30.0)).tolist() == [0] * 5


def test_donchian_breakout_with_trend():
    c = np.array([1.0, 2.0, 3.0])
    hh, ll = np.array([np.nan, 1.5, 2.5]), np.array([np.nan, 0.5, 0.5])
    assert donchian_breakout(c, hh, ll, np.array([1, 1, -1], np.int8)).tolist() == [0, 1, 0]


def test_reverse_extreme_flips_only_deep_crosses():
    sig = np.array([1, 1, -1, -1], np.int8)
    assert reverse_extreme(sig, np.array([28.0, 35.0, 72.0, 60.0])).tolist() == [-1, 0, 1, 0]


def test_random_like_keeps_the_signal_rate_and_is_seeded():
    sig = np.zeros(10_000, np.int8)
    sig[::10] = 1
    a, b = random_like(sig, 7), random_like(sig, 7)
    assert (a == b).all()
    assert 800 < np.count_nonzero(a) < 1200
    assert set(np.unique(a)) <= {-1, 0, 1}
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_signals.py -q`
Expected: `ImportError: cannot import name 'bb_fade' from 'research.signals'`.

- [ ] **Step 3: Append to `research/signals.py`**

Extend the import line at the top to:
```python
from research.indicators import adx, bollinger, ema, prior_max, prior_min, rsi
```
Then append:
```python
HTF_EMA = 50


def htf_index(m15: Bars, htf: Bars) -> np.ndarray:
    """For each M15 bar, the last higher-timeframe bar already closed at the M15 close (-1 if none)."""
    return np.searchsorted(htf.close_time, m15.close_time, side="right") - 1


def htf_trend(htf: Bars, period: int = HTF_EMA) -> np.ndarray:
    """+1: close above a rising EMA; -1: below a falling one; 0 otherwise or before `period` bars."""
    e = ema(htf.c, period)
    rising = np.r_[False, e[1:] > e[:-1]]
    falling = np.r_[False, e[1:] < e[:-1]]
    out = np.where((htf.c > e) & rising, 1, np.where((htf.c < e) & falling, -1, 0)).astype(np.int8)
    out[:period] = 0
    return out


def trend_on_m15(m15: Bars, htf: Bars) -> np.ndarray:
    k = htf_index(m15, htf)
    trend = htf_trend(htf)
    return np.where(k >= 0, trend[np.maximum(k, 0)], 0).astype(np.int8)


def pullback(r: np.ndarray, trend: np.ndarray, lo: float = 40.0, hi: float = 60.0) -> np.ndarray:
    """E2: with the trend, RSI closes back above `lo` (buy) / below `hi` (sell)."""
    sig = np.zeros(len(r), np.int8)
    buy = (trend[1:] > 0) & (r[:-1] < lo) & (r[1:] >= lo)
    sell = (trend[1:] < 0) & (r[:-1] > hi) & (r[1:] <= hi)
    sig[1:] = np.where(buy, 1, np.where(sell, -1, 0))
    return sig


def rsi2_extreme(r2: np.ndarray, trend=None, lo: float = 10.0, hi: float = 90.0) -> np.ndarray:
    """E3: RSI(2) below `lo` buys, above `hi` sells; optionally only with the trend."""
    buy, sell = r2 < lo, r2 > hi
    if trend is not None:
        buy &= trend > 0
        sell &= trend < 0
    return np.where(buy, 1, np.where(sell, -1, 0)).astype(np.int8)


def bb_fade(c: np.ndarray, lower: np.ndarray, upper: np.ndarray, adx_arr=None, adx_max: float = 20.0) -> np.ndarray:
    """E4: a close outside the band, then a close back inside -> trade back toward the middle."""
    sig = np.zeros(len(c), np.int8)
    with np.errstate(invalid="ignore"):
        buy = (c[:-1] < lower[:-1]) & (c[1:] > lower[1:])
        sell = (c[:-1] > upper[:-1]) & (c[1:] < upper[1:])
        if adx_arr is not None:
            calm = adx_arr[1:] < adx_max
            buy &= calm
            sell &= calm
    sig[1:] = np.where(buy, 1, np.where(sell, -1, 0))
    return sig


def donchian_breakout(c: np.ndarray, hh: np.ndarray, ll: np.ndarray, trend: np.ndarray) -> np.ndarray:
    """E5: close beyond the prior N-bar high/low in the trend's direction."""
    with np.errstate(invalid="ignore"):
        buy = (c > hh) & (trend > 0)
        sell = (c < ll) & (trend < 0)
    return np.where(buy, 1, np.where(sell, -1, 0)).astype(np.int8)


def reverse_extreme(sig: np.ndarray, slow_rsi: np.ndarray, lo: float = 30.0, hi: float = 70.0) -> np.ndarray:
    """E1b: fade only the legacy crosses taken with the slow RSI below `lo` / above `hi`."""
    keep = ((sig > 0) & (slow_rsi < lo)) | ((sig < 0) & (slow_rsi > hi))
    return np.where(keep, -sig, 0).astype(np.int8)


def random_like(sig: np.ndarray, seed: int) -> np.ndarray:
    """C2: random entries at the same rate as `sig`, random direction."""
    rng = np.random.default_rng(seed)
    rate = np.count_nonzero(sig) / max(len(sig), 1)
    fire = rng.random(len(sig)) < rate
    side = rng.choice(np.array([-1, 1], np.int8), len(sig))
    return np.where(fire, side, 0).astype(np.int8)


NAMES = ("C0", "C1", "C2", "E1a", "E1b", "E2a", "E2b", "E3a", "E3b", "E4a", "E4b", "E5a", "E5b")
_LEGACY_KEYS = ("FastRsiPeriod", "SlowRsiPeriod", "RsiCrossLookbackBars", "RsiBullishCrossMin", "RsiBullishCrossMax",
                "RsiBearishCrossMin", "RsiBearishCrossMax", "EnableSmcFilter", "SwingLookback", "EnableFvgDetection",
                "FvgMinPips", "EquilibriumThreshold", "EnableLiquiditySweepFilter")


def build(name: str, m: Market, spec: SymbolSpec, p: dict, seed=None, cache=None) -> np.ndarray:
    """The entry signal of config `name` (spec section 2). `cache` shares the legacy signal across configs."""
    cache = {} if cache is None else cache
    key = tuple(p[k] for k in _LEGACY_KEYS)

    def base():
        if key not in cache:
            cache[key] = legacy(m, spec, p)
        return cache[key]

    b = m.m15
    if name in ("C0", "C1"):
        sig = base()
    elif name == "C2":
        sig = random_like(base(), seed)
    elif name == "E1a":
        sig = -base()
    elif name == "E1b":
        sig = reverse_extreme(base(), rsi(b.c, int(p["SlowRsiPeriod"])))
    elif name in ("E2a", "E2b"):
        sig = pullback(rsi(b.c, 14), trend_on_m15(b, m.h1 if name == "E2a" else m.h4))
    elif name == "E3a":
        sig = rsi2_extreme(rsi(b.c, 2), trend_on_m15(b, m.h1))
    elif name == "E3b":
        sig = rsi2_extreme(rsi(b.c, 2), None)
    elif name in ("E4a", "E4b"):
        lower, _, upper = bollinger(b.c, 20, 2.0)
        sig = bb_fade(b.c, lower, upper, adx(b.h, b.l, b.c, 14) if name == "E4a" else None)
    elif name in ("E5a", "E5b"):
        n = 20 if name == "E5a" else 48
        sig = donchian_breakout(b.c, prior_max(b.h, n), prior_min(b.l, n), trend_on_m15(b, m.h4))
    else:
        raise ValueError(f"unknown config {name}")
    sig = sig.astype(np.int8).copy()
    sig[:WARMUP_BARS] = 0
    return sig
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_signals.py -q`
Expected: `12 passed`.

- [ ] **Step 5: Checkpoint (no commit unless the user asks)**

Files: `research/signals.py research/tests/test_signals.py`

---

### Task 11: Screening runner and the pass/fail verdict

**Files:**
- Create: `research/screen.py`, `research/tests/test_screen.py`

**Interfaces:**
- Consumes: `load_ticks`, `day_ms` (T1), `build_bars` (T2), `SPECS`, `flowrsi_params` (T4), `make_levels`, `run_account` (T5–6), `Market`, `build` (T7/T10).
- Produces:
  - `params_for(symbol, name, exit_mode) -> dict`; `mean_t(rs) -> (n, mean, t)`;
  - `summarize(rows) -> {config: {"P1": (n,m,t), "P2": …, "P3": …, "pairs_positive": int, "positions": int}}`;
  - `c2_means(summary, exit_mode) -> {"P1": float, "P2": float, "P3": float}`; `verdict(stats, c2) -> list[str]` (failed criteria, empty = pass);
  - CLI `python -m research.screen [--pairs …] [--jobs 2]` writing `research/results/screen_trades.csv`, `screen_refusals.csv`, `screen_report.md`.

- [ ] **Step 1: Write the failing tests**

`research/tests/test_screen.py`:
```python
import pytest

np = pytest.importorskip("numpy")

from research.screen import PAIRS, c2_means, params_for, summarize, verdict  # noqa: E402


def _rows(config, pattern_by_period):
    rows = []
    for symbol in PAIRS:
        for period, pattern in pattern_by_period.items():
            for k in range(16):
                rows.append({"config": config, "symbol": symbol, "period": period, "r": pattern[k % 2]})
    return rows


C2 = {"P1": -0.1, "P2": -0.1, "P3": -0.1}


def test_a_consistent_edge_passes():
    s = summarize(_rows("E9/X1", {"P1": (1.0, -0.5), "P2": (1.0, -0.5), "P3": (1.0, -0.5)}))
    assert verdict(s["E9/X1"], C2) == []


def test_one_losing_period_fails():
    s = summarize(_rows("E9/X1", {"P1": (1.0, -0.5), "P2": (1.0, -0.5), "P3": (-1.0, 0.5)}))
    fails = verdict(s["E9/X1"], C2)
    assert any(f.startswith("P3") for f in fails)


def test_too_few_positions_fail():
    rows = [r for r in _rows("E9/X1", {"P1": (1.0, -0.5), "P2": (1.0, -0.5), "P3": (1.0, -0.5)})][::4]
    assert any("positions/pair/month" in f for f in verdict(summarize(rows)["E9/X1"], C2))


def test_c2_mean_is_averaged_over_seeds():
    rows = _rows("C2/X1/s0", {"P1": (0.0, -0.2), "P2": (0.0, -0.2), "P3": (0.0, -0.2)}) + \
           _rows("C2/X1/s1", {"P1": (0.0, 0.0), "P2": (0.0, 0.0), "P3": (0.0, 0.0)})
    assert c2_means(summarize(rows), "X1")["P1"] == pytest.approx(-0.05)


def test_params_for_applies_the_spec_overrides():
    assert params_for("XAUUSD", "C0", "X2")["MinSlFloorPips"] == 1500.0
    assert params_for("XAUUSD", "E2a", "X2")["MinSlFloorPips"] == 500.0
    assert params_for("GBPJPY", "C1", "X2")["MinSlFloorPips"] == 30.0
    assert params_for("EURUSD", "C1", "X2")["MinSlFloorPips"] == 25.0
    x1 = params_for("EURUSD", "E3b", "X1")
    assert not x1["EnableBreakEven"] and not x1["EnableTrailingStop"] and not x1["EnablePartialClose"]
    assert all(not params_for(s, "E1a", "X2")["EnableMacroTmsFilter"] for s in PAIRS)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/test_screen.py -q`
Expected: `ModuleNotFoundError: No module named 'research.screen'`.

- [ ] **Step 3: Implement `research/screen.py`**

```python
"""Screen every entry config over 15 pairs x 2025/2026 on ticks and apply the pre-registered pass bar."""
import argparse
import csv
import math
from concurrent.futures import ProcessPoolExecutor
from datetime import date, timedelta
from pathlib import Path

from research.bars import build_bars
from research.signals import Market, build
from research.sim import make_levels, run_account
from research.specs import SPECS, flowrsi_params
from research.ticks import day_ms, load_ticks

RESULTS = Path(__file__).resolve().parent / "results"
PAIRS = ["AUDJPY", "AUDUSD", "BTCUSD", "DE40", "ETHUSD", "EURJPY", "EURUSD", "GBPJPY", "GBPUSD",
         "UK100", "US30", "USDCAD", "USDJPY", "USTEC", "XAUUSD"]
JPY = {"AUDJPY", "EURJPY", "GBPJPY", "USDJPY"}
FX = {"AUDUSD", "EURUSD", "GBPUSD", "USDCAD"}
YEARS = {2025: (date(2025, 1, 1), date(2025, 12, 31)), 2026: (date(2026, 1, 1), date(2026, 9, 24))}
P3_START_MS = day_ms(date(2026, 6, 1))
PERIODS = ("P1", "P2", "P3")
MONTHS = {"P1": 12.0, "P2": 5.0, "P3": 116 / 30.44}
BALANCE = 2000.0
CONTROLS = ("C0", "C1")
CANDIDATES = ("E1a", "E1b", "E2a", "E2b", "E3a", "E3b", "E4a", "E4b", "E5a", "E5b")
EXITS = ("X1", "X2")
SEEDS = range(20)


def params_for(symbol: str, name: str, exit_mode: str) -> dict:
    over = {"EnableMacroTmsFilter": False}
    if exit_mode == "X1":
        over.update(EnableBreakEven=False, EnableTrailingStop=False, EnablePartialClose=False)
    if name == "C1" and symbol in JPY:
        over["MinSlFloorPips"] = 30.0
    elif name == "C1" and symbol in FX:
        over["MinSlFloorPips"] = 25.0
    if symbol == "XAUUSD" and name != "C0":
        over["MinSlFloorPips"] = 500.0
    return flowrsi_params(symbol, **over)


def _period(entry_ms: int, year: int) -> str:
    if year == 2025:
        return "P1"
    return "P2" if entry_ms < P3_START_MS else "P3"


def run_pair(symbol: str):
    spec = SPECS[symbol]
    trades, refusals = [], []
    for year, (start, end) in YEARS.items():
        t = load_ticks(symbol, start - timedelta(days=7), end)
        if len(t) == 0:
            print(f"WARNING {symbol} {year}: no ticks")
            continue
        m = Market(build_bars(t, 15), build_bars(t, 60), build_bars(t, 240))
        cache = {}
        jobs = [(n, x, None) for n in CONTROLS + CANDIDATES for x in EXITS] + \
               [("C2", x, s) for x in EXITS for s in SEEDS]
        for name, exit_mode, seed in jobs:
            p = params_for(symbol, name, exit_mode)
            sig = build(name, m, spec, p, seed=seed, cache=cache)
            levels = make_levels(m.m15, spec, p, "atr" if exit_mode == "X1" else "swing")
            done, refused = run_account(t, m.m15, sig, levels, spec, p, exit_mode, BALANCE, day_ms(start))
            config = f"{name}/{exit_mode}" + (f"/s{seed}" if seed is not None else "")
            trades += [{"config": config, "symbol": symbol, "period": _period(tr.entry_ts, year),
                        "entry_ts": tr.entry_ts, "side": tr.side, "units": tr.units, "r": tr.r,
                        "net": tr.net, "deals": tr.deals} for tr in done]
            refusals.append({"config": config, "symbol": symbol, "year": year, "refused": refused})
        print(f"{symbol} {year}: done")
    return trades, refusals


def mean_t(rs):
    n = len(rs)
    if n < 2:
        return n, (rs[0] if n else 0.0), 0.0
    m = sum(rs) / n
    sd = math.sqrt(sum((r - m) ** 2 for r in rs) / (n - 1))
    return n, m, (m / (sd / math.sqrt(n)) if sd > 0 else 0.0)


def summarize(rows):
    by_config = {}
    for row in rows:
        by_config.setdefault(row["config"], []).append(row)
    out = {}
    for config, rs in by_config.items():
        s = {P: mean_t([x["r"] for x in rs if x["period"] == P]) for P in PERIODS}
        per_pair = {}
        for x in rs:
            per_pair.setdefault(x["symbol"], []).append(x["r"])
        s["pairs_positive"] = sum(1 for v in per_pair.values() if sum(v) / len(v) > 0)
        s["positions"] = len(rs)
        out[config] = s
    return out


def c2_means(summary, exit_mode: str):
    seeds = [s for k, s in summary.items() if k.startswith(f"C2/{exit_mode}/")]
    return {P: sum(s[P][1] for s in seeds) / len(seeds) for P in PERIODS}


def verdict(s, c2):
    fails = []
    for P in PERIODS:
        _, m, t = s[P]
        if not (m > 0 and t >= 2):
            fails.append(f"{P} mean {m:+.3f} t {t:+.1f}")
        if m <= c2[P]:
            fails.append(f"{P} not above C2 ({c2[P]:+.3f})")
    if s["pairs_positive"] < 9:
        fails.append(f"{s['pairs_positive']}/15 pairs positive")
    rate = s["positions"] / (len(PAIRS) * sum(MONTHS.values()))
    if rate < 2:
        fails.append(f"{rate:.2f} positions/pair/month")
    return fails


def _write_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def report(summary, refusals) -> str:
    lines = ["# FlowRSI entry screening", "",
             "| Config | P1 mR (t) | P2 mR (t) | P3 mR (t) | +pairs | pos/pair/mo | Verdict |",
             "|---|---|---|---|---|---|---|"]
    winners = []
    for exit_mode in EXITS:
        c2 = c2_means(summary, exit_mode)
        lines.append(f"| C2/{exit_mode} (seed mean) | " + " | ".join(f"{c2[P]:+.3f}" for P in PERIODS) + " | | | control |")
        for name in CONTROLS + CANDIDATES:
            config = f"{name}/{exit_mode}"
            s = summary.get(config)
            if s is None:
                continue
            fails = verdict(s, c2)
            rate = s["positions"] / (len(PAIRS) * sum(MONTHS.values()))
            cells = " | ".join(f"{s[P][1]:+.3f} ({s[P][2]:+.1f})" for P in PERIODS)
            status = "control" if name in CONTROLS else ("PASS" if not fails else "fail: " + "; ".join(fails))
            lines.append(f"| {config} | {cells} | {s['pairs_positive']}/15 | {rate:.2f} | {status} |")
            if name not in CONTROLS and not fails:
                winners.append((min(s[P][2] for P in PERIODS), config))
    lines += ["", "## Winner", ""]
    lines.append(f"{max(winners)[1]} (lowest t across P1–P3 = {max(winners)[0]:.2f})" if winners
                 else "None: no candidate passed the pre-registered bar.")
    lines += ["", "## Refused entries (sizing guardrails), XAUUSD", ""]
    for r in refusals:
        if r["symbol"] == "XAUUSD" and "/s" not in r["config"]:
            lines.append(f"- {r['config']} {r['year']}: {r['refused']}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="*", default=PAIRS)
    ap.add_argument("--jobs", type=int, default=2, help="parallel pairs; ~3 GB RAM each for BTCUSD")
    args = ap.parse_args(argv)
    RESULTS.mkdir(exist_ok=True)
    with ProcessPoolExecutor(args.jobs) as ex:
        results = list(ex.map(run_pair, args.pairs))
    trades = [row for tr, _ in results for row in tr]
    refusals = [row for _, rf in results for row in rf]
    _write_csv(RESULTS / "screen_trades.csv", trades)
    _write_csv(RESULTS / "screen_refusals.csv", refusals)
    text = report(summarize(trades), refusals)
    (RESULTS / "screen_report.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/test_screen.py -q`
Expected: `5 passed`.

- [ ] **Step 5: Smoke-run one pair**

Run: `research/.venv/bin/python -m research.screen --pairs EURUSD --jobs 1`
Expected:
- It prints `EURUSD 2025: done`, `EURUSD 2026: done` and a report table.
- `C0/X2` in P2+P3 is close to cTrader #49: 343 positions, mR −0.12 on 2026.
- The run takes a few minutes. If it takes much longer, profile `_run_flowrsi` first.

The verdict column is meaningless with one pair, because the 9/15 and rate criteria assume 15 pairs.

- [ ] **Step 6: Full suite**

Run: `research/.venv/bin/python -m pytest research/tests -q`
Expected: all tests pass, none skipped.

- [ ] **Step 7: Checkpoint (no commit unless the user asks)**

Files: `research/screen.py research/tests/test_screen.py`

---

### Task 12: Run the screening and record the verdict

**Files:**
- Modify: `docs/superpowers/specs/2026-09-25-flowrsi-entry-redesign-design.md` (append results; git-ignored)
- Output: `research/results/screen_report.md`, `screen_trades.csv`, `screen_refusals.csv` (git-ignored)

- [ ] **Step 1: Confirm the gate still passes on the final code**

Run: `research/.venv/bin/python -m research.calibrate`
Expected: `PASS`. If not, go back to Task 9 Step 6. No screening result counts without it.

- [ ] **Step 2: Run the full screen**

Run: `research/.venv/bin/python -m research.screen --jobs 2`
Expected: 30 `done` lines (15 pairs × 2 years), then the report. About 30–60 min on the Mac.

- [ ] **Step 3: Sanity-check the controls before reading any candidate**

In `research/results/screen_report.md`:
- `C0/X2` P2/P3 should sit near the cTrader macro-off result, pooled about −0.08R. XAU contributes 0 positions at the preset 1500 floor.
- `C1/X2` should be at or above `C0/X2` on the 8 forex pairs, since both of its changes helped in phase 1.
- `C2` should be negative in every period.

If a control is far off, stop and investigate. Do not read the candidate rows.

- [ ] **Step 4: Record the verdict in the spec**

Append a "Screening result" section to the spec: the report table, the winner line, and the XAU refusal counts.

- [ ] **Step 5: Hand off to the user**

- **A config passed:** report it with its P1–P3 table. Propose writing the part-3 plan: `EntryMode` in `FlowRsiBot.cs`, the no-regression rerun of #27, 30 confirmation backtests, then presets. That plan is written only after the user agrees.
- **None passed:** report the table and the spec's stop rule: no cBot change. Recommendation: stop the FlowRSI demo bots, or keep them for data collection; the user decides.
- In both cases, list the files created by this plan and ask whether to commit them. Stage only those files.

---

## Self-review notes

- Spec coverage:
  - Data and cache fill: Task 8.
  - Costs and sizing: Tasks 4–5.
  - Entry timing and one position at a time: Task 5.
  - Exit X1: Task 5. Exit X2: Task 6.
  - R metric: Tasks 5 and 11.
  - Calibration gate, including the volume criterion: Task 9.
  - Controls and candidates: Tasks 7 and 10.
  - Periods and pass bar: Task 11.
  - Verdict and stop rules: Task 12.
  - Spec part 3 (cBot, confirmation, deploy) is deliberately deferred to its own plan, per the spec's winner-only rule.
- XAU floor 500 in every config except C0, and $2000 for every pair: `params_for` in Task 11 plus its tests. The #93 exception is in `calibrate.replay`.
- Swaps are ignored, as the spec states.

## Deviations during execution (2026-09-25)

- Task 8: `pull_cache.sh` accepts remote tar exit 1 ("file changed as we read it"): the cache-fill backtests
  write into the cache while it is copied. The 8 filled pairs are pulled again after the fill jobs finish.
- Task 9, first gate run: match ≥ 90 % on every pair and pooled R diff +0.011 passed, but volume on the
  simulated equity path was 91.4 %. Sizing at cTrader's own balance matched 99.7 %: the gap was equity drift
  (a few extra Sunday-open entries, swaps ignored). By user decision:
  - swaps are modelled (`specs.SWAPS`, `rollovers`, `swap_usd`; `sim._close` charges each closing deal), and
  - the volume gate sizes each matched stop at cTrader's balance; the path figure is printed for information.
  Second run: PASS (pooled diff −0.003, volume 99.8 % at cTrader's balance, 95.8 % on the path).
- `ctrader_positions` rows gained a 6th field (balance before); `replay` also returns `spec, p`.
- Task 11 smoke run on EURUSD: 73 s for 2025 + 2026; C0/X2 2026 in line with cTrader #49.
