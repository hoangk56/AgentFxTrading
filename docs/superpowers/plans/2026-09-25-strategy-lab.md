# Strategy Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A reusable strategy catalog plus a tick-level lab that runs every catalogued strategy on 22 symbols
over 2023-01 → 2026-09 with fixed lots for a $10k account, no loss limits and one position per
(strategy × symbol), with mirrored / week-shuffled / random-control stress tests.

**Architecture:** `research/lab/` on top of the existing research code (tick cache decoder, cTrader-style bar
builder, FlowRSI replica, cost specs). A chunk = one symbol-year of ticks (real, synthetic cross, mirrored or
week-shuffled) with warm-up and tail; a `Ctx` runs one strategy on one chunk through a one-position engine
that books fills, exits and USD costs. Strategies are plain functions `fn(ctx, **params)`; `catalog.py`
registers them with rules, origin, status and findings and renders `research/STRATEGIES.md`. `run.py`
fans (symbol, variant) jobs out to processes; `report.py` turns trades into per-cell tables and flags.

**Tech Stack:** Python 3.14 in `research/.venv` (numpy 2.5, pytest 9). No new dependencies (no pandas).

**Spec:** `docs/superpowers/specs/2026-09-25-strategy-lab-design.md`

## Global Constraints

- Tests: `research/.venv/bin/python -m pytest research/tests -q` from the repo root
  (`/Users/hoangbk/00.code_base/105.AgentFxTrading`). Every task ends with the whole research suite green.
- **Never commit or push.** `research/` is untracked on main and `docs/` is git-ignored; the user commits on
  request only (AGENTS.md, memory "No auto-commit"). The "Commit" step of each task is replaced by "leave the
  files in the working tree".
- No production changes: no cBot edits, no app/ edits, no DB writes, no service or container restarts. The
  only VPS action is Task 1 (queue cache-fill backtests through the Backtest API), approved by the user.
- Account rules for every run: start $10,000; fixed units per symbol (FX 10,000 incl. synthetic crosses,
  XAUUSD 2, BTCUSD 0.1, ETHUSD 4, US30 0.2, USTEC 0.4, DE40 0.4, UK100 0.8); no loss-count, daily or total
  loss limit, no guardrails, no equity-based sizing; one position per (strategy, symbol).
- Years: 2023, 2024, 2025 and 2026-01-01..2026-09-24. Warm-up 190 days, tail 45 days per chunk.
- Symbols: 15 real (AUDJPY AUDUSD BTCUSD DE40 ETHUSD EURJPY EURUSD GBPJPY GBPUSD UK100 US30 USDCAD USDJPY
  USTEC XAUUSD) + 7 synthetic crosses (EURGBP EURAUD GBPAUD EURCAD GBPCAD AUDCAD CADJPY).
- Changes to existing research files are additive (optional arguments / new fields) so the existing tests and
  the pushed branch `origin/feat/flowrsi-entry-screening` stay compatible.
- Match the style of `research/`: module docstrings that explain the model, few comments, numpy.
- Test files live in `research/tests/lab/` and are named `test_lab_*.py` (pytest's prepend import mode
  needs unique basenames); shared helpers in `research/tests/lab/lab_helpers.py`.

## File Structure

```
research/fill_2023_2024_rest.py        Task 1  queue the VPS cache-fill backtests (10 symbols x 2 years)
research/sim.py                        Task 11 + fixed_units, fills, sl0/tp0 (additive)
research/lab/__init__.py               Task 2
research/lab/universe.py               Task 2  symbols, fixed units, contract data, synthetic crosses
research/lab/cbot.py                   Task 2  cBot [Parameter] defaults + live presets
research/lab/costs.py                  Task 3  quote->USD by day, commission, swap
research/lab/feed.py                   Task 4/5 chunks: real, synthetic cross, mirror, week shuffle
research/lab/check_crosses.py          Task 4  synthetic-vs-real cross check -> SYNTH_SPREAD_FACTOR
research/lab/engine.py                 Task 6  Trade/Pos/Intent/Ctx, run_intents, NY D1 bars
research/lab/control.py                Task 7  random-entry control
research/lab/strategies/__init__.py    Task 8
research/lab/strategies/rules.py       Task 8/9/10 researched rules
research/lab/strategies/flowrsi.py     Task 11 FlowRSI replica adapter
research/lab/strategies/judas.py       Task 12 Judas port
research/lab/strategies/tmsorb.py      Task 13/14 TMS+ORB port
research/lab/catalog.py                Task 15 registry + STRATEGIES.md renderer
research/lab/run.py                    Task 16 runner
research/lab/report.py                 Task 17 cells.csv, matrix.csv, report.md
research/STRATEGIES.md                 Task 15/18 generated catalog
research/tests/lab/lab_helpers.py      Task 2  synthetic ticks/chunks for tests
research/tests/lab/test_lab_*.py       one per task
research/results/lab/<run>/            Task 18 outputs (git-ignored)
```

---

### Task 1: Fill the 2023–2024 tick cache for the ten 2025+ symbols

Long-running (hours on the VPS); start it first and keep implementing while it runs.

**Files:**
- Create: `research/fill_2023_2024_rest.py`

**Interfaces:**
- Consumes: the Backtest API on the VPS (`POST http://127.0.0.1:8000/api/backtests`, same body as `research/fill_2023_2024.py`), `research/pull_years.sh`, `research/scan/m1.py`.
- Produces: `research/data/<SYMBOL>/t1/2023*.zticks, 2024*.zticks` and rebuilt `research/data/m1/<SYMBOL>.npz` for AUDJPY AUDUSD ETHUSD EURJPY EURUSD GBPJPY GBPUSD UK100 USDCAD USDJPY.

- [ ] **Step 1: Write the queue script**

```python
"""Queue the cTrader backtests that fill the 2023-2024 tick cache for the ten symbols that only had 2025+
(strategy lab, docs/superpowers/specs/2026-09-25-strategy-lab-design.md). Live FlowRSI presets, $2000, ticks;
the reports themselves are not used. The API caps a run at 365 days, so 2024 ends on 12-30 (12-29..31 are
cached). Cross pairs go last: their conversion-symbol ticks load lazily inside the first order, so a cold run
can abort once by timeout; the Backtest page reruns it and the failed run still fills the cache.
Run on the VPS:  ssh forge@204.168.144.232 'python3 -' < research/fill_2023_2024_rest.py"""
import json
import urllib.request

API = "http://127.0.0.1:8000/api/backtests"
PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD", "ETHUSD", "UK100", "EURJPY", "GBPJPY", "AUDJPY"]
YEARS = [("2023-01-01", "2023-12-31"), ("2024-01-01", "2024-12-30")]

for symbol in PAIRS:
    for start, end in YEARS:
        body = {"bot_name": f"cbot-demo-demo-{symbol.lower()}-all-flowrsi", "start": start, "end": end,
                "data_mode": "ticks", "balance": 2000.0, "note": f"lab cache fill {start[:4]}", "overrides": {}}
        req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            print(resp.status, resp.read().decode(), symbol, start[:4])
```

- [ ] **Step 2: Check the ten FlowRSI bots exist on the VPS**

Run: `ssh forge@204.168.144.232 "curl -s http://127.0.0.1:8000/api/bots" | grep -o 'cbot-demo-demo-[a-z0-9]*-all-flowrsi' | sort -u`
Expected: the ten names for eurusd gbpusd audusd usdjpy usdcad ethusd uk100 eurjpy gbpjpy audjpy (among the 15).
If a name is missing, stop and ask the user which bot to use for that symbol.

- [ ] **Step 3: Queue the 20 jobs**

Run: `ssh forge@204.168.144.232 'python3 -' < research/fill_2023_2024_rest.py`
Expected: 20 lines starting with `200` or `201` and a job id.

- [ ] **Step 4: Wait for the jobs (in the background)**

Poll every ~20 minutes: `ssh forge@204.168.144.232 "curl -s 'http://127.0.0.1:8000/api/backtests'" | python3 -c "import json,sys; d=json.load(sys.stdin); d=d.get('jobs', d) if isinstance(d, dict) else d; [print(j.get('id'), j.get('status'), j.get('note'), j.get('symbol')) for j in d if 'lab cache fill' in str(j.get('note'))]"`
Expected: all 20 `done` (or `failed` after the automatic rerun). A job that failed twice: queue it once more by hand with the same body; a failed run still fills most of the cache, so continue if the coverage check in Step 6 passes.

- [ ] **Step 5: Pull the new years and rebuild the M1 cache**

Run: `research/pull_years.sh "2023 2024" EURUSD GBPUSD AUDUSD USDJPY USDCAD ETHUSD UK100 EURJPY GBPJPY AUDJPY`
Then: `research/.venv/bin/python -m research.scan.m1 AUDJPY AUDUSD ETHUSD EURJPY EURUSD GBPJPY GBPUSD UK100 USDCAD USDJPY`
Expected: each symbol prints ~1360 tick days (2023-01-0x .. 2026-09-24) and the M1 builder prints its minute count.

- [ ] **Step 6: Coverage check**

Run: `cd research/data && for s in AUDJPY AUDUSD ETHUSD EURJPY EURUSD GBPJPY GBPUSD UK100 USDCAD USDJPY; do echo "$s $(ls $s/t1 | head -1) $(ls $s/t1 | grep -c '^2023') $(ls $s/t1 | grep -c '^2024')"; done`
Expected: first file `2023010x.zticks`; ≥ 250 days in 2023 and in 2024 for FX and UK100 (ETHUSD trades weekends: ≥ 350).
Record any gaps in the Task 18 report.

- [ ] **Step 7: Leave the files in the working tree (no commit)**

---

### Task 2: Universe and cBot parameters

**Files:**
- Create: `research/lab/__init__.py`, `research/lab/universe.py`, `research/lab/cbot.py`
- Create: `research/tests/lab/lab_helpers.py`
- Test: `research/tests/lab/test_lab_universe.py`

**Interfaces:**
- Consumes: `research.specs.SPECS, SWAPS, SymbolSpec`; `app.cbot_presets.PRESETS`; `cBot/*.cs`.
- Produces:
  - `universe.REAL, FX_REAL, INDICES, SYNTHETIC: Dict[str, Tuple[str, str, str]], CHECK_CROSSES, FX, ALL, FIXED_UNITS, QUOTE_CCY, CONVERSION, PRESET_TEMPLATE, REF_PRICE, SYNTH_SPREAD_FACTOR`
  - `universe.Instrument(symbol, pip, tick_size, units, comm_per_unit, quote_ccy, swap_long, swap_short, triple_weekday, cross=None)` with `.synthetic`, `.mirrored() -> Instrument`, `.spec() -> SymbolSpec`
  - `universe.instrument(symbol: str) -> Instrument`
  - `cbot.cbot_defaults(strategy: str) -> Dict[str, Any]` (strategy in `"flowrsi" | "judas" | "tms_orb"`), `cbot.preset(strategy, symbol) -> dict`, `cbot.cbot_params(strategy, symbol, **overrides) -> Dict[str, Any]`
  - test helpers `lab_helpers.make_chunk(ts, bid, spread=0.0002, symbol="EURUSD", lo=None, hi=None, variant="real", year=2025, **inst_over) -> Chunk` and `lab_helpers.bar_ticks(t0_ms, minutes, ohlc) -> (ts, bid)`, `needs_ticks`, `needs_m1` (defined after Task 4 creates `Chunk`; this task adds only `needs_ticks`/`needs_m1`, Task 4 adds the two builders)

- [ ] **Step 1: Write the failing tests**

`research/tests/lab/test_lab_universe.py`:

```python
import pytest

np = pytest.importorskip("numpy")

from research.lab.cbot import cbot_defaults, cbot_params  # noqa: E402
from research.lab.universe import ALL, FIXED_UNITS, SYNTHETIC, instrument  # noqa: E402
from research.specs import SWAPS  # noqa: E402


def test_every_symbol_has_an_instrument_with_fixed_units():
    assert len(ALL) == 22 and len(SYNTHETIC) == 7
    for s in ALL:
        assert instrument(s).units == FIXED_UNITS[s] > 0


def test_fixed_units_follow_the_spec_table():
    assert FIXED_UNITS["EURUSD"] == FIXED_UNITS["EURGBP"] == FIXED_UNITS["CADJPY"] == 10_000
    assert (FIXED_UNITS["XAUUSD"], FIXED_UNITS["BTCUSD"], FIXED_UNITS["ETHUSD"]) == (2, 0.1, 4)
    assert (FIXED_UNITS["US30"], FIXED_UNITS["USTEC"], FIXED_UNITS["DE40"], FIXED_UNITS["UK100"]) == (0.2, 0.4, 0.4, 0.8)


def test_synthetic_cross_contract_data():
    eg = instrument("EURGBP")
    assert eg.synthetic and eg.cross == ("EURUSD", "GBPUSD", "div") and eg.quote_ccy == "GBP"
    assert eg.pip == 0.0001 and eg.comm_per_unit == pytest.approx(6.96e-5)
    cj = instrument("CADJPY")
    assert cj.pip == 0.01 and cj.tick_size == 0.001 and cj.quote_ccy == "JPY"
    assert not instrument("EURUSD").synthetic


def test_synthetic_swaps_are_the_legs_weighted_by_exposure():
    ec = instrument("EURCAD")          # long EURCAD = long 1 EURUSD + long 1.16 USDCAD
    assert ec.swap_long == pytest.approx(SWAPS["EURUSD"][0] + 1.16 * SWAPS["USDCAD"][0])
    assert ec.swap_short == pytest.approx(SWAPS["EURUSD"][1] + 1.16 * SWAPS["USDCAD"][1])
    eg = instrument("EURGBP")          # long EURGBP = long 1 EURUSD + short 0.865 GBPUSD
    assert eg.swap_long == pytest.approx(SWAPS["EURUSD"][0] + 0.865 * SWAPS["GBPUSD"][1])


def test_mirrored_instrument_exchanges_the_swap_sides():
    x = instrument("XAUUSD")
    m = x.mirrored()
    assert (m.swap_long, m.swap_short) == (x.swap_short, x.swap_long)


def test_spec_for_the_flowrsi_simulator():
    assert instrument("EURUSD").spec().usd_per_quote == 1.0
    s = instrument("CADJPY").spec()
    assert s.min_units == 1000 and s.usd_per_quote == pytest.approx(1 / 154.8)


def test_cbot_defaults_parse_all_three_bots():
    j = cbot_defaults("judas")
    assert (j["asianStartHour"], j["asianEndHour"], j["dstRule"]) == (0, 6, "Auto")
    assert j["requireRejectionWick"] is True and j["minRejectionWickRatio"] == 0.35
    assert j["breakEvenMode"] == "Risk_Reward_Ratio"
    t = cbot_defaults("tms_orb")
    assert t["TmsTimeFrame"] == "Hour" and t["SessionDstRule"] == "US" and t["MaxBarsAfterBreakout"] == 8
    assert cbot_defaults("flowrsi")["AtrPeriod"] == 14


def test_cbot_params_layer_defaults_preset_template_and_overrides():
    p = cbot_params("judas", "EURGBP")                 # synthetic cross -> EURUSD preset
    assert (p["stoplossPip"], p["takeprofitPip"], p["asianEndHour"]) == (15.0, 35.0, 6)
    assert cbot_params("tms_orb", "USTEC")["OrbStartMinute"] == 30
    assert cbot_params("judas", "XAUUSD", stoplossPip=1.0)["stoplossPip"] == 1.0
```

`research/tests/lab/lab_helpers.py` (first part; Task 4 appends the chunk builders):

```python
"""Shared helpers for the lab tests."""
import pytest

from research.ticks import DATA_DIR

needs_ticks = pytest.mark.skipif(not (DATA_DIR / "BTCUSD" / "t1").exists(), reason="no tick cache")
needs_m1 = pytest.mark.skipif(not (DATA_DIR / "m1" / "EURUSD.npz").exists(), reason="no M1 cache")
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_universe.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'research.lab'`.

- [ ] **Step 3: Implement**

`research/lab/__init__.py`:

```python
"""Strategy lab: every catalogued strategy on every symbol, tick level, fixed lots, one position per cell."""
```

`research/lab/universe.py`:

```python
"""The lab's symbols: fixed units, contract data, quote currencies and the synthetic crosses.

Real symbols take pip, tick size, commission and swaps from research/specs.py (fitted on the 2026 cTrader
reports). A synthetic cross is built from two USD legs (research/lab/feed.py); its commission is the broker's
$30 per million per side on the base currency, its swaps are the legs' swaps weighted by the legs' exposure
at 2025-26 median prices (approximate, like every swap before 2026)."""
from dataclasses import dataclass, replace
from typing import Dict, Optional, Tuple

from research.specs import SPECS, SWAPS, SymbolSpec

REAL = ("AUDJPY", "AUDUSD", "BTCUSD", "DE40", "ETHUSD", "EURJPY", "EURUSD", "GBPJPY", "GBPUSD",
        "UK100", "US30", "USDCAD", "USDJPY", "USTEC", "XAUUSD")
FX_REAL = ("AUDJPY", "AUDUSD", "EURJPY", "EURUSD", "GBPJPY", "GBPUSD", "USDCAD", "USDJPY")
INDICES = ("DE40", "UK100", "US30", "USTEC")
# (leg A, leg B, op): "mul" -> A x B, "div" -> A / B
SYNTHETIC: Dict[str, Tuple[str, str, str]] = {
    "EURGBP": ("EURUSD", "GBPUSD", "div"),
    "EURAUD": ("EURUSD", "AUDUSD", "div"),
    "GBPAUD": ("GBPUSD", "AUDUSD", "div"),
    "EURCAD": ("EURUSD", "USDCAD", "mul"),
    "GBPCAD": ("GBPUSD", "USDCAD", "mul"),
    "AUDCAD": ("AUDUSD", "USDCAD", "mul"),
    "CADJPY": ("USDJPY", "USDCAD", "div"),
}
# Real crosses rebuilt from their legs to check the method (research/lab/check_crosses.py).
CHECK_CROSSES = {"EURJPY": ("EURUSD", "USDJPY", "mul"), "GBPJPY": ("GBPUSD", "USDJPY", "mul"),
                 "AUDJPY": ("AUDUSD", "USDJPY", "mul")}
FX = FX_REAL + tuple(SYNTHETIC)
ALL = REAL + tuple(SYNTHETIC)

FIXED_UNITS = {**{s: 10_000.0 for s in FX}, "XAUUSD": 2.0, "BTCUSD": 0.1, "ETHUSD": 4.0,
               "US30": 0.2, "USTEC": 0.4, "DE40": 0.4, "UK100": 0.8}
QUOTE_CCY = {"AUDJPY": "JPY", "EURJPY": "JPY", "GBPJPY": "JPY", "USDJPY": "JPY", "CADJPY": "JPY",
             "USDCAD": "CAD", "EURCAD": "CAD", "GBPCAD": "CAD", "AUDCAD": "CAD",
             "EURGBP": "GBP", "UK100": "GBP", "EURAUD": "AUD", "GBPAUD": "AUD", "DE40": "EUR"}
# quote currency -> (conversion pair, True when that pair is quoted in USD per unit of the currency)
CONVERSION = {"JPY": ("USDJPY", False), "CAD": ("USDCAD", False), "EUR": ("EURUSD", True),
              "GBP": ("GBPUSD", True), "AUD": ("AUDUSD", True)}
# Live-preset donor for the symbols the bots do not trade.
PRESET_TEMPLATE = {"EURGBP": "EURUSD", "EURAUD": "EURUSD", "GBPAUD": "GBPUSD", "EURCAD": "EURUSD",
                   "GBPCAD": "GBPUSD", "AUDCAD": "AUDUSD", "CADJPY": "AUDJPY"}
# 2025-26 medians, used where a constant is enough (commission, swap weights, the FlowRSI SymbolSpec).
REF_PRICE = {"EURUSD": 1.16, "GBPUSD": 1.34, "AUDUSD": 0.66, "USDCAD": 1.39, "USDJPY": 154.8,
             "EURGBP": 0.865, "EURAUD": 1.76, "GBPAUD": 2.03, "EURCAD": 1.61, "GBPCAD": 1.86,
             "AUDCAD": 0.915, "CADJPY": 111.6}
COMMISSION_PER_SIDE = 30e-6          # USD per USD of base notional
# Real / synthetic spread ratio measured on EURJPY, GBPJPY, AUDJPY (research/lab/check_crosses.py).
SYNTH_SPREAD_FACTOR = 1.0


@dataclass(frozen=True)
class Instrument:
    symbol: str
    pip: float
    tick_size: float
    units: float              # the lab's fixed volume in cTrader units
    comm_per_unit: float      # USD per unit, round trip
    quote_ccy: str
    swap_long: float          # USD per unit per rollover
    swap_short: float
    triple_weekday: int
    cross: Optional[Tuple[str, str, str]] = None

    @property
    def synthetic(self) -> bool:
        return self.cross is not None

    def mirrored(self) -> "Instrument":
        """Prices mirrored: a long position now earns what a short one did."""
        return replace(self, swap_long=self.swap_short, swap_short=self.swap_long)

    def spec(self) -> SymbolSpec:
        """research.specs.SymbolSpec for the FlowRSI simulator (constant USD per quote)."""
        if self.symbol in SPECS:
            return SPECS[self.symbol]
        pair, direct = CONVERSION[self.quote_ccy]
        usd_per_quote = REF_PRICE[pair] if direct else 1.0 / REF_PRICE[pair]
        return SymbolSpec(self.symbol, self.pip, self.tick_size, 1000, 1000, self.comm_per_unit, usd_per_quote)


def _base_usd(symbol: str) -> float:
    return {"EUR": REF_PRICE["EURUSD"], "GBP": REF_PRICE["GBPUSD"], "AUD": REF_PRICE["AUDUSD"],
            "CAD": 1.0 / REF_PRICE["USDCAD"]}[symbol[:3]]


def _synthetic_swaps(symbol: str) -> Tuple[float, float]:
    """(long, short) USD per unit. One unit long of the cross = w_a units of leg A and w_b of leg B (sign = side)."""
    a, b, op = SYNTHETIC[symbol]
    if op == "mul":                   # EURCAD = EURUSD x USDCAD: long 1 EURUSD and EURUSD-worth of USDCAD
        w_a, w_b = 1.0, REF_PRICE[a]
    elif symbol == "CADJPY":          # USDJPY / USDCAD: long and short 1/USDCAD of each leg
        w_a, w_b = 1.0 / REF_PRICE["USDCAD"], -1.0 / REF_PRICE["USDCAD"]
    else:                             # EURGBP = EURUSD / GBPUSD: long 1 EURUSD, short EURGBP-worth of GBPUSD
        w_a, w_b = 1.0, -REF_PRICE[symbol]

    def leg(sym: str, w: float, long_cross: bool) -> float:
        long_rate, short_rate, _ = SWAPS[sym]
        return abs(w) * (long_rate if (w > 0) == long_cross else short_rate)

    return leg(a, w_a, True) + leg(b, w_b, True), leg(a, w_a, False) + leg(b, w_b, False)


def instrument(symbol: str) -> Instrument:
    if symbol in SPECS:
        s = SPECS[symbol]
        long_rate, short_rate, triple = SWAPS[symbol]
        return Instrument(symbol, s.pip, s.tick_size, FIXED_UNITS[symbol], s.comm_per_unit,
                          QUOTE_CCY.get(symbol, "USD"), long_rate, short_rate, triple)
    if symbol in SYNTHETIC:
        jpy = symbol.endswith("JPY")
        long_rate, short_rate = _synthetic_swaps(symbol)
        return Instrument(symbol, 0.01 if jpy else 0.0001, 0.001 if jpy else 0.00001, FIXED_UNITS[symbol],
                          2 * COMMISSION_PER_SIDE * _base_usd(symbol), QUOTE_CCY[symbol], long_rate, short_rate, 2,
                          SYNTHETIC[symbol])
    raise KeyError(symbol)
```

`research/lab/cbot.py`:

```python
"""The live cBots' parameters: the [Parameter] defaults parsed from cBot/*.cs, then the live preset
(app/cbot_presets.py; synthetic crosses borrow a template symbol's), then overrides."""
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from app.cbot_presets import PRESETS
from research.lab.universe import PRESET_TEMPLATE

ROOT = Path(__file__).resolve().parents[2]
BOTS = {"flowrsi": "FlowRsiBot", "judas": "AsianRangeJudasSweepBot", "tms_orb": "AiAgentBot"}
_PARAM = re.compile(r"\[Parameter\([^\n]*?DefaultValue = ([^,)\n]+)[^\n]*\n\s*public ([\w.]+) (\w+)")


def _value(raw: str, typ: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"'):
        return raw.strip('"')
    if raw in ("true", "false"):
        return raw == "true"
    if typ == "int":
        return int(raw)
    if typ in ("double", "float"):
        return float(raw)
    return raw.split(".")[-1]          # enum member: DstRule.US -> "US"


@lru_cache(maxsize=None)
def cbot_defaults(strategy: str) -> Dict[str, Any]:
    src = (ROOT / "cBot" / f"{BOTS[strategy]}.cs").read_text()
    return {name: _value(raw, typ) for raw, typ, name in _PARAM.findall(src)}


def preset(strategy: str, symbol: str) -> dict:
    return PRESETS[(strategy, PRESET_TEMPLATE.get(symbol, symbol))]


def cbot_params(strategy: str, symbol: str, **overrides) -> Dict[str, Any]:
    p = dict(cbot_defaults(strategy))
    p.update(preset(strategy, symbol)["params"])
    p.update(overrides)
    return p
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_universe.py -q`
Expected: 8 passed.

- [ ] **Step 5: Run the whole research suite**

Run: `research/.venv/bin/python -m pytest research/tests -q`
Expected: all passed.

- [ ] **Step 6: Leave the files in the working tree (no commit)**

---

### Task 3: Costs — quote→USD by day, commission, swaps

**Files:**
- Create: `research/lab/costs.py`
- Test: `research/tests/lab/test_lab_costs.py`

**Interfaces:**
- Consumes: `research.scan.m1.load(symbol) -> dict` (keys ts, o, h, l, c, ca, ...), `research.specs.rollovers(entry_ms, exit_ms, triple_weekday) -> int`, `universe.CONVERSION, Instrument`.
- Produces: `costs.DAY_MS`, `costs.daily_closes(pair) -> (days: ndarray, mid: ndarray)`, `costs.usd_per_quote(ccy: str, ts_ms: int) -> float`, `costs.commission(inst, units) -> float`, `costs.swap(inst, side, units, t_in, t_out) -> float`.

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_m1  # noqa: E402
from research.lab import costs  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.specs import SPECS  # noqa: E402
from research.ticks import day_ms  # noqa: E402

DAY = costs.DAY_MS


def test_usd_quote_needs_no_conversion():
    assert costs.usd_per_quote("USD", 0) == 1.0


def test_conversion_uses_the_previous_days_close(monkeypatch):
    days, px = np.array([100, 101, 102]), np.array([150.0, 160.0, 170.0])
    monkeypatch.setattr(costs, "daily_closes", lambda pair: (days, px))
    ms = 102 * DAY + 5
    assert costs.usd_per_quote("JPY", ms) == pytest.approx(1 / 160.0)      # USDJPY: 1 / price
    assert costs.usd_per_quote("EUR", ms) == pytest.approx(160.0)          # EURUSD: price
    assert costs.usd_per_quote("JPY", 50 * DAY) == pytest.approx(1 / 150.0)  # before the cache: first close


@needs_m1
def test_conversion_matches_the_2026_report_constants():
    for sym, ccy in (("USDJPY", "JPY"), ("USDCAD", "CAD"), ("DE40", "EUR"), ("UK100", "GBP")):
        assert costs.usd_per_quote(ccy, day_ms(date(2026, 3, 16))) == pytest.approx(SPECS[sym].usd_per_quote, rel=0.08)


def test_commission_and_swap():
    inst = instrument("XAUUSD")
    assert costs.commission(inst, 2) == pytest.approx(2 * 0.2579)
    t_in = day_ms(date(2025, 3, 11)) + 12 * 3_600_000       # Tue 12:00 UTC
    t_out = t_in + 2 * DAY                                  # Thu 12:00 UTC: Tue + Wed (triple) rollovers
    assert costs.swap(inst, 1, 2, t_in, t_out) == pytest.approx(inst.swap_long * 2 * 4)
    assert costs.swap(inst, -1, 2, t_in, t_out) == pytest.approx(inst.swap_short * 2 * 4)
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_costs.py -q`
Expected: FAIL, `No module named 'research.lab.costs'`.

- [ ] **Step 3: Implement `research/lab/costs.py`**

```python
"""Money in the lab: quote -> USD at the market's rate of the day, commission and swaps for fixed units.

The FlowRSI simulator used cTrader's 2026 USD-per-quote constants; over 2023-2026 USDJPY moved 130 -> 160, so
the lab converts each deal at the previous UTC day's close of the conversion pair (M1 cache). Swaps keep the
rates fitted on 2026 (research/specs.py), so earlier years' swaps are approximate and reported separately."""
from functools import lru_cache
from typing import Tuple

import numpy as np

from research.lab.universe import CONVERSION, Instrument
from research.scan.m1 import load
from research.specs import rollovers

DAY_MS = 86_400_000


@lru_cache(maxsize=None)
def daily_closes(pair: str) -> Tuple[np.ndarray, np.ndarray]:
    """(UTC day number, mid of the day's last M1 bar)."""
    m = load(pair)
    day = m["ts"] // DAY_MS
    last = np.r_[np.flatnonzero(day[1:] != day[:-1]), len(day) - 1]
    return day[last], (m["c"][last] + m["ca"][last]) / 2.0


def usd_per_quote(ccy: str, ts_ms: int) -> float:
    """USD value of one unit of the quote currency at ts_ms (previous day's close; the first close before the
    cache starts)."""
    if ccy == "USD":
        return 1.0
    pair, direct = CONVERSION[ccy]
    days, px = daily_closes(pair)
    k = max(int(np.searchsorted(days, ts_ms // DAY_MS, side="left")) - 1, 0)
    return float(px[k]) if direct else 1.0 / float(px[k])


def commission(inst: Instrument, units: float) -> float:
    return inst.comm_per_unit * units


def swap(inst: Instrument, side: int, units: float, t_in: int, t_out: int) -> float:
    rate = inst.swap_long if side > 0 else inst.swap_short
    return rate * units * rollovers(t_in, t_out, inst.triple_weekday)
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_costs.py -q`
Expected: 4 passed (the M1 test skips without the cache).

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

Run: `research/.venv/bin/python -m pytest research/tests -q`

---

### Task 4: Feed — chunks, synthetic crosses, mirror

**Files:**
- Create: `research/lab/feed.py`, `research/lab/check_crosses.py`
- Modify: `research/tests/lab/lab_helpers.py` (append builders), `research/lab/universe.py` (`SYNTH_SPREAD_FACTOR` from the check)
- Test: `research/tests/lab/test_lab_feed.py`

**Interfaces:**
- Consumes: `research.ticks.Ticks, load_ticks, day_ms`, `research.scan.m1.load`, `universe.instrument, SYNTH_SPREAD_FACTOR`.
- Produces: `feed.DATA_END, YEARS, WARMUP_DAYS, TAIL_DAYS, DAY_MS, WEEK_MS, SAT0_MS`, `feed.year_span(year) -> (date, date)`, `feed.Chunk(symbol, variant, year, t, lo_ms, hi_ms, inst)`, `feed.cross_ticks(ta, tb, op, spread_factor=1.0) -> Ticks`, `feed.real_ticks(symbol, a, b) -> Ticks`, `feed.mirror_k(symbol) -> float`, `feed.mirror(t, k) -> Ticks`, `feed.load_chunk(symbol, variant, year, warmup_days=WARMUP_DAYS, tail_days=TAIL_DAYS) -> Optional[Chunk]` (variants `real`, `mirror`; Task 5 adds `shuffle:<seed>`).

- [ ] **Step 1: Append the chunk builders to `lab_helpers.py`**

```python
from dataclasses import replace  # noqa: E402

import numpy as np  # noqa: E402

from research.lab.feed import Chunk  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.ticks import Ticks  # noqa: E402


def make_chunk(ts, bid, spread=0.0002, symbol="EURUSD", lo=None, hi=None, variant="real", year=2025, **inst_over):
    t = Ticks(np.asarray(ts, np.int64), np.asarray(bid, float), np.asarray(bid, float) + spread)
    inst = instrument(symbol)
    if inst_over:
        inst = replace(inst, **inst_over)
    return Chunk(symbol, variant, year, t, int(t.ts[0]) if lo is None else lo,
                 int(t.ts[-1]) + 1 if hi is None else hi, inst)


def bar_ticks(t0_ms, minutes, ohlc):
    """Four bid ticks per bar: open, then low/high (high first on a down bar), then the close one minute before
    the bar ends. Returns (ts, bid)."""
    ts, px = [], []
    for k, (o, h, l, c) in enumerate(ohlc):
        base = t0_ms + k * minutes * 60_000
        first, second = (l, h) if c >= o else (h, l)
        ts += [base, base + 60_000, base + 120_000, base + (minutes - 1) * 60_000]
        px += [o, first, second, c]
    return np.array(ts, np.int64), np.array(px, float)
```

- [ ] **Step 2: Write the failing tests** (`research/tests/lab/test_lab_feed.py`)

```python
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_ticks  # noqa: E402
from research.lab.feed import cross_ticks, load_chunk, mirror  # noqa: E402
from research.ticks import Ticks, day_ms, load_ticks  # noqa: E402


def _t(ts, bid, ask):
    return Ticks(np.asarray(ts, np.int64), np.asarray(bid, float), np.asarray(ask, float))


def test_cross_ticks_mul_and_div_as_of_join():
    a = _t([0, 10, 20], [1.10, 1.11, 1.12], [1.1001, 1.1101, 1.1201])
    b = _t([5, 15], [150.0, 151.0], [150.02, 151.02])
    x = cross_ticks(a, b, "mul")
    assert list(x.ts) == [5, 10, 15, 20]                      # before 5 leg B is unknown
    assert x.bid[0] == pytest.approx(1.10 * 150.0) and x.ask[0] == pytest.approx(1.1001 * 150.02)
    assert x.bid[3] == pytest.approx(1.12 * 151.0)
    d = cross_ticks(a, b, "div")
    assert d.bid[0] == pytest.approx(1.10 / 150.02) and d.ask[0] == pytest.approx(1.1001 / 150.0)


def test_cross_spread_factor_scales_around_the_mid():
    a = _t([0], [1.10], [1.1002])
    b = _t([0], [1.0], [1.0])
    x = cross_ticks(a, b, "mul", spread_factor=0.5)
    assert (x.bid[0] + x.ask[0]) / 2 == pytest.approx(1.1001)
    assert x.ask[0] - x.bid[0] == pytest.approx(0.0001)


def test_mirror_twice_is_the_identity_and_keeps_ask_above_bid():
    t = _t([0, 1], [1.1, 1.2], [1.1002, 1.2003])
    once = mirror(t, 1.21)
    assert np.all(once.ask > once.bid)
    back = mirror(once, 1.21)
    np.testing.assert_allclose(back.bid, t.bid)
    np.testing.assert_allclose(back.ask, t.ask)


@needs_ticks
def test_load_chunk_has_warm_up_and_tail_around_the_year():
    ch = load_chunk("BTCUSD", "real", 2025, warmup_days=3, tail_days=2)
    assert ch.lo_ms == day_ms(date(2025, 1, 1)) and ch.hi_ms == day_ms(date(2026, 1, 1))
    assert ch.t.ts[0] < ch.lo_ms and ch.t.ts[-1] >= ch.hi_ms
    assert load_chunk("BTCUSD", "real", 2019) is None


@needs_ticks
def test_synthetic_eurjpy_tracks_the_real_one():
    a, b = date(2025, 3, 3), date(2025, 3, 7)
    real = load_ticks("EURJPY", a, b)
    syn = cross_ticks(load_ticks("EURUSD", a, b), load_ticks("USDJPY", a, b), "mul")
    k = np.searchsorted(syn.ts, real.ts, "right") - 1
    ok = k >= 0
    rmid = (real.bid[ok] + real.ask[ok]) / 2
    smid = (syn.bid[k[ok]] + syn.ask[k[ok]]) / 2
    assert np.median(np.abs(rmid - smid) / rmid) < 1e-4
```

- [ ] **Step 3: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_feed.py -q`
Expected: FAIL, `No module named 'research.lab.feed'`.

- [ ] **Step 4: Implement `research/lab/feed.py`**

```python
"""Tick chunks for the lab: real ticks, synthetic crosses from USD legs, mirrored prices and (Task 5)
week-shuffled histories. A chunk is one calendar year plus a warm-up before it and a tail after it; entries
are allowed only inside the year, the tail only finishes positions opened in it."""
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache
from typing import Optional

import numpy as np

from research.lab.universe import SYNTH_SPREAD_FACTOR, Instrument, instrument
from research.scan.m1 import load as load_m1
from research.ticks import Ticks, day_ms, load_ticks

DATA_START, DATA_END = date(2023, 1, 1), date(2026, 9, 24)
YEARS = (2023, 2024, 2025, 2026)
WARMUP_DAYS, TAIL_DAYS = 190, 45
DAY_MS, WEEK_MS = 86_400_000, 7 * 86_400_000
SAT0_MS = 2 * DAY_MS                   # 1970-01-03 00:00 UTC is a Saturday: lab weeks run Sat -> Sat


def year_span(year: int):
    return date(year, 1, 1), min(date(year, 12, 31), DATA_END)


@dataclass
class Chunk:
    symbol: str
    variant: str
    year: int
    t: Ticks
    lo_ms: int          # entries allowed from ...
    hi_ms: int          # ... until (exclusive)
    inst: Instrument


def _empty() -> Ticks:
    return Ticks(np.empty(0, np.int64), np.empty(0), np.empty(0))


def cross_ticks(ta: Ticks, tb: Ticks, op: str, spread_factor: float = 1.0) -> Ticks:
    """As-of join of two legs on the union of their tick times. mul: bid = bidA x bidB, ask = askA x askB;
    div: bid = bidA / askB, ask = askA / bidB. spread_factor scales the half-spread around the mid."""
    if len(ta) == 0 or len(tb) == 0:
        return _empty()
    ts = np.union1d(ta.ts, tb.ts)
    ia = np.searchsorted(ta.ts, ts, side="right") - 1
    ib = np.searchsorted(tb.ts, ts, side="right") - 1
    ok = (ia >= 0) & (ib >= 0)
    ts, ia, ib = ts[ok], ia[ok], ib[ok]
    if op == "mul":
        bid, ask = ta.bid[ia] * tb.bid[ib], ta.ask[ia] * tb.ask[ib]
    else:
        bid, ask = ta.bid[ia] / tb.ask[ib], ta.ask[ia] / tb.bid[ib]
    if spread_factor != 1.0:
        mid, half = (bid + ask) / 2.0, (ask - bid) / 2.0 * spread_factor
        bid, ask = mid - half, mid + half
    return Ticks(ts, bid, ask)


def real_ticks(symbol: str, a: date, b: date) -> Ticks:
    inst = instrument(symbol)
    if not inst.synthetic:
        return load_ticks(symbol, a, b)
    leg_a, leg_b, op = inst.cross
    return cross_ticks(load_ticks(leg_a, a, b), load_ticks(leg_b, a, b), op, SYNTH_SPREAD_FACTOR)


@lru_cache(maxsize=None)
def mirror_k(symbol: str) -> float:
    """K of p' = K / p: the square of the symbol's first M1 close, so the mirror starts at the real level."""
    return float(load_m1(symbol)["c"][0]) ** 2


def mirror(t: Ticks, k: float) -> Ticks:
    """Prices reflected in log space: up-moves become down-moves; the new bid is K / ask."""
    return Ticks(t.ts, k / t.ask, k / t.bid)


def load_chunk(symbol: str, variant: str, year: int, warmup_days: int = WARMUP_DAYS,
               tail_days: int = TAIL_DAYS) -> Optional[Chunk]:
    """None when the symbol has no tick inside the year."""
    a0, b0 = year_span(year)
    a, b = a0 - timedelta(days=warmup_days), min(b0 + timedelta(days=tail_days), DATA_END)
    inst = instrument(symbol)
    if variant == "real":
        t = real_ticks(symbol, a, b)
    elif variant == "mirror":
        t, inst = mirror(real_ticks(symbol, a, b), mirror_k(symbol)), inst.mirrored()
    else:
        raise ValueError(f"unknown variant {variant}")
    lo, hi = day_ms(a0), day_ms(b0) + DAY_MS
    if len(t) == 0 or not np.any((t.ts >= lo) & (t.ts < hi)):
        return None
    return Chunk(symbol, variant, year, t, lo, hi, inst)
```

- [ ] **Step 5: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_feed.py -q`
Expected: 5 passed.

- [ ] **Step 6: Write and run the cross check, then set the spread factor**

`research/lab/check_crosses.py`:

```python
"""Rebuild EURJPY, GBPJPY, AUDJPY from their USD legs and compare with the real ticks, one week per month of
2025-2026: median mid difference (bp) and median spread, real vs synthetic. The median ratio real/synthetic
becomes universe.SYNTH_SPREAD_FACTOR.   python -m research.lab.check_crosses"""
from datetime import date, timedelta

import numpy as np

from research.lab.feed import cross_ticks
from research.lab.universe import CHECK_CROSSES
from research.ticks import load_ticks

WEEKS = [date(2025, m, 3) for m in range(1, 13)] + [date(2026, m, 2) for m in range(1, 10)]


def main() -> None:
    ratios = []
    for sym, (a, b, op) in CHECK_CROSSES.items():
        diffs, spreads_real, spreads_syn = [], [], []
        for d in WEEKS:
            e = d + timedelta(days=4)
            real = load_ticks(sym, d, e)
            syn = cross_ticks(load_ticks(a, d, e), load_ticks(b, d, e), op)
            if len(real) == 0 or len(syn) == 0:
                continue
            k = np.searchsorted(syn.ts, real.ts, "right") - 1
            ok = k >= 0
            rm = (real.bid[ok] + real.ask[ok]) / 2
            sm = (syn.bid[k[ok]] + syn.ask[k[ok]]) / 2
            diffs.append(float(np.median(np.abs(rm - sm) / rm)) * 1e4)
            spreads_real.append(float(np.median(real.ask - real.bid)))
            spreads_syn.append(float(np.median(syn.ask - syn.bid)))
        ratio = float(np.median(np.array(spreads_real) / np.array(spreads_syn)))
        ratios.append(ratio)
        print(f"{sym}: mid diff {np.median(diffs):.2f} bp | spread real {np.median(spreads_real):.4f} "
              f"synthetic {np.median(spreads_syn):.4f} | ratio {ratio:.2f}")
    print(f"SYNTH_SPREAD_FACTOR = {np.median(ratios):.2f}")


if __name__ == "__main__":
    main()
```

Run: `research/.venv/bin/python -m research.lab.check_crosses`
Expected: mid diff < 1 bp for all three and a final `SYNTH_SPREAD_FACTOR = x.xx` line.
Edit `research/lab/universe.py`: set `SYNTH_SPREAD_FACTOR` to the printed value, and add the three result
lines to its comment (e.g. `# 2026-09-2x: EURJPY 0.62, GBPJPY 0.58, AUDJPY 0.65 -> median 0.62`).
If the mid difference is ≥ 1 bp, stop and report: the synthetic crosses would not be trustworthy.

- [ ] **Step 7: Whole research suite green; leave the files in the working tree (no commit)**

---
### Task 5: Feed — week shuffle

**Files:**
- Modify: `research/lab/feed.py` (add `week_of`, `WeekShuffle`, `shuffler`, the `shuffle:<seed>` branch of `load_chunk`)
- Test: `research/tests/lab/test_lab_shuffle.py`

**Interfaces:**
- Consumes: `feed.load_m1`, `feed.load_ticks` (module attributes, monkeypatched in tests).
- Produces: `feed.week_of(ms) -> int | ndarray`, `feed.WeekShuffle(symbol, seed)` with `.weeks`, `.src`, `.scale`, `.ticks(a: date, b: date) -> Ticks`; `feed.shuffler(symbol, seed) -> WeekShuffle` (cached); `load_chunk(symbol, "shuffle:<seed>", year)`.

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date, timedelta

import pytest

np = pytest.importorskip("numpy")

from research.lab import feed  # noqa: E402
from research.ticks import Ticks, day_ms  # noqa: E402

W0 = 2900                                   # a lab week number (Saturday 1970-01-03 + 2900 weeks)
PRICES = {W0: (100.0, 104.0, 110.0), W0 + 1: (110.0, 105.0, 99.0), W0 + 2: (100.0, 111.0, 120.0)}


def _week_ticks(w, prices):
    sat = feed.SAT0_MS + w * feed.WEEK_MS
    ts = [sat + 2 * feed.DAY_MS, sat + 4 * feed.DAY_MS, sat + 6 * feed.DAY_MS - 3_600_000]   # Mon, Wed, Fri 23:00
    return ts, list(prices)


@pytest.fixture
def fake(monkeypatch):
    ts, px = [], []
    for w, p in PRICES.items():
        a, b = _week_ticks(w, p)
        ts += a
        px += b
    ts, px = np.array(ts, np.int64), np.array(px, float)
    monkeypatch.setattr(feed, "load_m1", lambda s: {"ts": ts, "o": px, "c": px})

    def load_ticks(symbol, a, b):
        keep = (ts >= day_ms(a)) & (ts < day_ms(b) + feed.DAY_MS)
        return Ticks(ts[keep], px[keep], px[keep] + 0.01)

    monkeypatch.setattr(feed, "load_ticks", load_ticks)
    feed.shuffler.cache_clear()
    return ts, px


def _weeks_of(t):
    w = feed.week_of(t.ts)
    return [(t.bid[w == k][0], t.bid[w == k][-1]) for k in np.unique(w)]


def test_shuffle_keeps_weekly_returns_and_clock_positions(fake):
    ts, px = fake
    sh = feed.WeekShuffle("X", seed=3)
    a = date(1970, 1, 3) + timedelta(weeks=W0)
    t = sh.ticks(a, a + timedelta(days=20))
    got = sorted(round(last / first, 9) for first, last in _weeks_of(t))
    want = sorted(round(p[2] / p[0], 9) for p in PRICES.values())
    assert got == want
    assert sorted((t.ts - feed.SAT0_MS) % feed.WEEK_MS) == sorted((ts - feed.SAT0_MS) % feed.WEEK_MS)
    assert np.all(np.diff(t.ts) > 0)
    assert np.allclose(t.ask - t.bid, 0.01 * sh.scale[np.repeat(np.arange(3), 3)])


def test_each_week_opens_at_the_previous_close_times_its_own_gap(fake):
    sh = feed.WeekShuffle("X", seed=3)
    a = date(1970, 1, 3) + timedelta(weeks=W0)
    weeks = _weeks_of(sh.ticks(a, a + timedelta(days=20)))
    first = np.array([p[0] for p in PRICES.values()])
    last = np.array([p[2] for p in PRICES.values()])
    gap = np.r_[1.0, first[1:] / last[:-1]]
    assert weeks[0][0] == pytest.approx(100.0)
    for k in (1, 2):
        assert weeks[k][0] == pytest.approx(weeks[k - 1][1] * gap[sh.src[k]])


def test_load_chunk_accepts_the_shuffle_variant(fake, monkeypatch):
    btc = feed.instrument("BTCUSD")
    monkeypatch.setattr(feed, "instrument", lambda s: btc)
    a = date(1970, 1, 3) + timedelta(weeks=W0)
    monkeypatch.setattr(feed, "year_span", lambda y: (a, a + timedelta(days=20)))
    ch = feed.load_chunk("X", "shuffle:3", 2025, warmup_days=0, tail_days=0)
    assert ch is not None and ch.variant == "shuffle:3" and len(ch.t) == 9
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_shuffle.py -q`
Expected: FAIL, `module 'research.lab.feed' has no attribute 'WeekShuffle'`.

- [ ] **Step 3: Implement** — add to `research/lab/feed.py` after `mirror`:

```python
def week_of(ms):
    return (np.asarray(ms) - SAT0_MS) // WEEK_MS


class WeekShuffle:
    """The symbol's weeks (Sat 00:00 UTC -> Sat) permuted with a seed. Target slot k (the k-th week with data)
    receives source week src[k], shifted by whole weeks into the slot (weekday and hour kept) and scaled so
    that it opens at the previous slot's close times the source week's own weekend gap."""

    def __init__(self, symbol: str, seed: int):
        m = load_m1(symbol)
        w = week_of(m["ts"])
        starts = np.flatnonzero(np.r_[True, w[1:] != w[:-1]])
        ends = np.r_[starts[1:], len(w)] - 1
        first, last = m["o"][starts], m["c"][ends]
        gap = np.r_[1.0, first[1:] / last[:-1]]
        self.symbol = symbol
        self.weeks = w[starts]
        self.src = np.random.default_rng(seed).permutation(len(self.weeks))
        self.scale = np.empty(len(self.src))
        self.scale[0] = first[0] / first[self.src[0]]
        for k in range(1, len(self.src)):
            opening = self.scale[k - 1] * last[self.src[k - 1]] * gap[self.src[k]]
            self.scale[k] = opening / first[self.src[k]]

    def ticks(self, a: date, b: date) -> Ticks:
        lo, hi = day_ms(a), day_ms(b) + DAY_MS
        parts = []
        for k in np.flatnonzero((self.weeks >= week_of(lo)) & (self.weeks <= week_of(hi - 1))):
            s = int(self.weeks[self.src[k]])
            s0 = date(1970, 1, 3) + timedelta(weeks=s)
            t = load_ticks(self.symbol, s0, s0 + timedelta(days=6))
            if len(t):
                parts.append((t.ts + (int(self.weeks[k]) - s) * WEEK_MS, t.bid * self.scale[k], t.ask * self.scale[k]))
        if not parts:
            return _empty()
        ts = np.concatenate([p[0] for p in parts])
        keep = (ts >= lo) & (ts < hi)
        return Ticks(ts[keep], np.concatenate([p[1] for p in parts])[keep], np.concatenate([p[2] for p in parts])[keep])


@lru_cache(maxsize=32)
def shuffler(symbol: str, seed: int) -> WeekShuffle:
    return WeekShuffle(symbol, seed)
```

and in `load_chunk`, before the `else: raise`:

```python
    elif variant.startswith("shuffle:"):
        t = shuffler(symbol, int(variant.split(":", 1)[1])).ticks(a, b)
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_shuffle.py research/tests/lab/test_lab_feed.py -q`
Expected: all passed.

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 6: Engine

**Files:**
- Create: `research/lab/engine.py`
- Test: `research/tests/lab/test_lab_engine.py`

**Interfaces:**
- Consumes: `research.bars.Bars, build_bars`, `research.sim._first_hit(price, start, lo, hi) -> int`, `costs.*`, `feed.Chunk`.
- Produces:
  - `engine.NAN, HOUR_MS, DAY_MS, D1_ENTRY_DELAY_MS (= 2 h)`, `engine.ny_offset_ms(ts) -> ndarray`, `engine.build_d1_ny(t) -> Bars`
  - `engine.Trade(strategy, symbol, variant, side, t_in, t_out, entry, exit, units, sl0, tp0, gross, comm, swap, risk_usd, why)` with `.net`, `.r`
  - `engine.Pos(side, e, entry, units, sl, tp, sl0, tp0, deals=[])` — deals are `(tick, price, units, why)`
  - `engine.Intent(at_ms, side, sl_dist=NAN, tp_dist=NAN, exit_ms=0, sl_px=NAN, tp_px=NAN)`
  - `engine.Ctx(ch, strategy, busy_ms=0)` with `.t .inst .units .ch .trades .busy_ms .busy_tick`, `.bars(minutes) -> Bars` (1440 = New York-close D1), `.tick_at(ms) -> int`, `.can_enter(e) -> bool`, `.open(e, side, sl=NAN, tp=NAN) -> Pos`, `.close(pos, j, why, units=None)`, `.finish(pos) -> Trade`, `.first_exit(pos, start, end) -> (tick, why)` (why `""` when nothing hit up to `end`)
  - `engine.run_intents(ctx, intents) -> List[Trade]`

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date, datetime, timezone

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk  # noqa: E402
from research.lab import engine  # noqa: E402
from research.lab.engine import Ctx, Intent, build_d1_ny, run_intents  # noqa: E402
from research.ticks import Ticks, day_ms  # noqa: E402

T0 = day_ms(date(2025, 3, 11)) + 12 * 3_600_000      # Tue 12:00 UTC
S = 1000


def ch_of(bid, **kw):
    return make_chunk(T0 + np.arange(len(bid)) * S, bid, **kw)


def test_buy_fills_at_the_ask_and_is_stopped_on_the_bid_at_the_gapped_price():
    ctx = Ctx(ch_of([1.1000, 1.1000, 1.0990, 1.0980]), "t")
    run_intents(ctx, [Intent(T0, 1, sl_dist=0.0015)])
    (tr,) = ctx.trades
    assert tr.entry == pytest.approx(1.1002) and tr.sl0 == pytest.approx(1.0987)
    assert tr.exit == pytest.approx(1.0980) and tr.why == "sl"
    assert tr.gross == pytest.approx((1.0980 - 1.1002) * 10_000)
    assert tr.comm == pytest.approx(6.733e-5 * 10_000)
    assert tr.risk_usd == pytest.approx(0.0015 * 10_000) and tr.r == pytest.approx(tr.net / 15.0)


def test_sell_target_is_hit_on_the_ask():
    ctx = Ctx(ch_of([1.1000, 1.0995, 1.0985, 1.0970]), "t")
    run_intents(ctx, [Intent(T0, -1, sl_dist=0.0020, tp_dist=0.0020)])
    (tr,) = ctx.trades
    assert tr.entry == pytest.approx(1.1000) and tr.why == "tp"
    assert tr.exit == pytest.approx(1.0972)                    # first ask <= 1.0980 is 1.0970 + 0.0002


def test_time_exit_and_tail():
    ctx = Ctx(ch_of([1.1000] * 6), "t")
    run_intents(ctx, [Intent(T0, 1, sl_dist=0.01, exit_ms=T0 + 3 * S)])
    assert ctx.trades[0].why == "time" and ctx.trades[0].t_out == T0 + 3 * S
    ctx = Ctx(ch_of([1.1000] * 6), "t")
    run_intents(ctx, [Intent(T0, 1, sl_dist=0.01)])
    assert ctx.trades[0].why == "tail" and ctx.trades[0].t_out == T0 + 5 * S


def test_one_position_at_a_time_and_entries_only_inside_the_year():
    bid = [1.1000] * 20
    ch = ch_of(bid, lo=T0 + 2 * S, hi=T0 + 15 * S)
    ctx = Ctx(ch, "t")
    run_intents(ctx, [Intent(T0, 1, exit_ms=T0 + 4 * S),              # before lo: skipped
                      Intent(T0 + 3 * S, 1, exit_ms=T0 + 8 * S),      # taken
                      Intent(T0 + 5 * S, -1, exit_ms=T0 + 9 * S),     # inside the first: skipped
                      Intent(T0 + 8 * S, -1, exit_ms=T0 + 10 * S),    # on the exit tick: skipped
                      Intent(T0 + 9 * S, -1, exit_ms=T0 + 12 * S),    # taken
                      Intent(T0 + 16 * S, 1, exit_ms=T0 + 18 * S)])   # after hi: skipped
    assert [(tr.t_in - T0) // S for tr in ctx.trades] == [3, 9]
    assert ctx.busy_ms == T0 + 12 * S


def test_busy_ms_from_the_previous_chunk_blocks_entries():
    ctx = Ctx(ch_of([1.1] * 10), "t", busy_ms=T0 + 4 * S)
    run_intents(ctx, [Intent(T0 + 2 * S, 1, exit_ms=T0 + 6 * S), Intent(T0 + 5 * S, 1, exit_ms=T0 + 7 * S)])
    assert [(tr.t_in - T0) // S for tr in ctx.trades] == [5]


def test_swap_is_booked_over_rollovers():
    ts = np.array([T0, T0 + 2 * engine.DAY_MS], np.int64)            # Tue 12:00 -> Thu 12:00 UTC
    ctx = Ctx(make_chunk(ts, [2900.0, 2910.0], spread=0.2, symbol="XAUUSD"), "t")
    run_intents(ctx, [Intent(T0, 1, exit_ms=int(ts[1]))])
    (tr,) = ctx.trades
    assert tr.swap == pytest.approx(ctx.inst.swap_long * 2 * 4)
    assert tr.gross == pytest.approx((2910.0 - 2900.2) * 2)


def test_partial_deals_give_a_volume_weighted_exit():
    ctx = Ctx(ch_of([1.1000, 1.1010, 1.1020]), "t")
    pos = ctx.open(0, 1, sl=1.09)
    ctx.close(pos, 1, "partial", 5000)
    ctx.close(pos, 2, "tp")
    tr = ctx.finish(pos)
    assert tr.units == 10_000 and tr.exit == pytest.approx(1.1015) and tr.why == "tp"
    assert tr.gross == pytest.approx((1.1010 - 1.1002) * 5000 + (1.1020 - 1.1002) * 5000)


def test_d1_bars_close_at_17_new_york_without_a_sunday_stub():
    def ms(y, m, d, h):
        return int(datetime(y, m, d, h, tzinfo=timezone.utc).timestamp() * 1000)
    # EDT (UTC-4): the FX day runs 21:00 UTC -> 21:00 UTC
    ts = np.array([ms(2025, 7, 11, 20), ms(2025, 7, 13, 21), ms(2025, 7, 14, 10), ms(2025, 7, 14, 21)], np.int64)
    t = Ticks(ts, np.array([1.0, 2.0, 3.0, 4.0]), np.array([1.0, 2.0, 3.0, 4.0]))
    b = build_d1_ny(t)
    assert list(b.open_time) == [ms(2025, 7, 10, 21), ms(2025, 7, 13, 21), ms(2025, 7, 14, 21)]
    assert list(b.c) == [1.0, 3.0, 4.0] and b.minutes == 1440
    assert b.close_time[1] == ms(2025, 7, 14, 21)
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_engine.py -q`
Expected: FAIL, `No module named 'research.lab.engine'`.

- [ ] **Step 3: Implement `research/lab/engine.py`**

```python
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
from research.sim import _first_hit
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
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_engine.py -q`
Expected: 8 passed.

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 7: Random-entry control

**Files:**
- Create: `research/lab/control.py`
- Test: `research/tests/lab/test_lab_control.py`

**Interfaces:**
- Consumes: `engine.Ctx, Intent, Trade, run_intents`, `feed.Chunk`.
- Produces: `control.random_control(ch: Chunk, real: List[Trade], seed: int) -> List[Trade]` (strategy name `control:<seed>`).

- [ ] **Step 1: Write the failing tests**

```python
import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk  # noqa: E402
from research.lab.control import random_control  # noqa: E402
from research.lab.engine import NAN, Trade  # noqa: E402

T0 = 1_741_600_800_000                        # 2025-03-10 10:00 UTC


def _chunk():
    rng = np.random.default_rng(0)
    n = 2 * 24 * 60                           # two days of minute ticks
    return make_chunk(T0 + np.arange(n) * 60_000, 1.10 + np.cumsum(rng.normal(0, 1e-4, n)))


def _real(n):
    return [Trade("x", "EURUSD", "real", 1, T0, T0 + 3_600_000, 1.1, 1.1, 10_000, 1.098, NAN, 0, 0, 0, 20.0, "time")
            for _ in range(n)]


def test_control_replays_the_trade_shapes_with_random_sides():
    c = random_control(_chunk(), _real(20), seed=1)
    assert len(c) == 20
    assert all(abs(tr.entry - tr.sl0) == pytest.approx(0.002) for tr in c)
    assert all(tr.t_out - tr.t_in <= 3_600_000 + 60_000 for tr in c)
    assert {tr.side for tr in c} == {-1, 1}
    assert all(b.t_in > a.t_out for a, b in zip(c, c[1:]))


def test_control_is_deterministic_per_seed_and_empty_without_trades():
    ch = _chunk()
    a = [(t.t_in, t.side) for t in random_control(ch, _real(5), seed=2)]
    b = [(t.t_in, t.side) for t in random_control(ch, _real(5), seed=2)]
    assert a == b
    assert random_control(ch, [], seed=2) == []
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_control.py -q`
Expected: FAIL, `No module named 'research.lab.control'`.

- [ ] **Step 3: Implement `research/lab/control.py`**

```python
"""Random-entry control for one (strategy, symbol, chunk): the real trades' shapes (stop distance, target
distance, holding time as a time cap) replayed in order at random M15 bar closes with random sides, one
position at a time. Its P&L is what the costs and the exit shape earn without the entry signal."""
from typing import List

import numpy as np

from research.lab.engine import Ctx, Intent, Trade, run_intents
from research.lab.feed import Chunk


def random_control(ch: Chunk, real: List[Trade], seed: int) -> List[Trade]:
    if not real:
        return []
    ctx = Ctx(ch, f"control:{seed}")
    closes = ctx.bars(15).close_time
    closes = closes[(closes >= ch.lo_ms) & (closes < ch.hi_ms)]
    if len(closes) == 0:
        return []
    rng = np.random.default_rng(seed)
    times = np.sort(rng.choice(closes, size=min(len(closes), 3 * len(real)), replace=False))
    shapes = [(abs(tr.entry - tr.sl0), abs(tr.tp0 - tr.entry), max(tr.t_out - tr.t_in, 60_000)) for tr in real]
    k = 0
    for at in times:
        if k == len(shapes):
            break
        sl_d, tp_d, hold = shapes[k]
        side = 1 if rng.random() < 0.5 else -1
        before = len(ctx.trades)
        run_intents(ctx, [Intent(int(at), side, sl_d, tp_d, int(at) + int(hold))])
        k += len(ctx.trades) > before
    return ctx.trades
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_control.py -q`
Expected: 2 passed.

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---
### Task 8: Researched rules A — BTC-S1, XAU-T1 and the rule bank

**Files:**
- Create: `research/lab/strategies/__init__.py` (empty docstring), `research/lab/strategies/rules.py`
- Test: `research/tests/lab/test_lab_rules.py`

**Interfaces:**
- Consumes: `engine.Ctx, Intent, run_intents, NAN, D1_ENTRY_DELAY_MS`, `research.indicators.atr_sma, prior_max, prior_min, rsi`.
- Produces: `rules.TF_MIN`, `rules.shock_follow(ctx, tf=15, Z=2.5, H=12, SLK=2.0, TPK=2.0)`, `rules.bank_rule(ctx, kind, mode, tf, H, SLK, TPK=None, L=1, Z=1.0, N=20, P=14, lo=30.0, warm=25)`, `rules.parse_bank(name) -> dict`, `rules.BANK_CONFIGS: Tuple[str, ...]` (24 names). All strategy functions return None and append to `ctx.trades`.

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import bar_ticks, make_chunk, needs_ticks  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk  # noqa: E402
from research.lab.strategies import rules  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.ticks import day_ms, load_ticks  # noqa: E402

T0 = day_ms(date(2025, 3, 10))
QUIET, SHOCK = (1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1045, 1.0995, 1.1040)
AFTER = (1.1040, 1.1045, 1.1035, 1.1040)


def _shock_chunk():
    ts, px = bar_ticks(T0, 15, [QUIET] * 30 + [SHOCK] + [AFTER] * 20)
    return make_chunk(ts, px, spread=0.0002)


def test_parse_bank_names():
    assert rules.parse_bank("zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0") == dict(
        kind="zmove", mode=1, tf="D1", L=3, Z=3.0, H=3, SLK=1.0, TPK=1.0)
    assert rules.parse_bank("donchR_H4_N55_H24_SL2.5_TPNone") == dict(
        kind="donch", mode=-1, tf="H4", N=55, H=24, SLK=2.5, TPK=None)
    assert rules.parse_bank("rsiF_H1_P14_lo20_H12_SL2.0_TPNone") == dict(
        kind="rsi", mode=1, tf="H1", P=14, lo=20.0, H=12, SLK=2.0, TPK=None)


def test_bank_configs_cover_every_kind_direction_and_timeframe_once():
    keys = {(k["kind"], k["mode"], k["tf"]) for k in map(rules.parse_bank, rules.BANK_CONFIGS)}
    assert len(rules.BANK_CONFIGS) == len(keys) == 24


def test_shock_follow_buys_the_next_tick_with_atr_stop_and_target():
    ctx = Ctx(_shock_chunk(), "BTC-S1")
    rules.shock_follow(ctx)
    (tr,) = ctx.trades
    atr = (19 * 0.0010 + 0.0050) / 20
    assert tr.side == 1 and tr.t_in == T0 + 31 * 900_000
    assert tr.entry - tr.sl0 == pytest.approx(2 * atr) and tr.tp0 - tr.entry == pytest.approx(2 * atr)
    assert tr.why == "time" and tr.t_out == T0 + 43 * 900_000


def test_bank_donchian_follow_enters_on_the_first_close_beyond_the_range():
    ctx = Ctx(_shock_chunk(), "BANK")
    rules.bank_rule(ctx, kind="donch", mode=1, tf="M15", N=20, H=6, SLK=1.5)
    assert [(tr.side, tr.t_in) for tr in ctx.trades] == [(1, T0 + 31 * 900_000)]
    assert np.isnan(ctx.trades[0].tp0)


@needs_ticks
def test_btc_s1_matches_ticksim_with_fixed_units():
    from research.scan.ticksim import run as tick_run
    ref, _, _ = tick_run("BTCUSD", date(2025, 3, 1), date(2025, 4, 30), fixed_units=0.1)
    t = load_ticks("BTCUSD", date(2025, 2, 26), date(2025, 4, 30))
    ch = Chunk("BTCUSD", "real", 2025, t, day_ms(date(2025, 3, 1)), day_ms(date(2025, 5, 1)), instrument("BTCUSD"))
    ctx = Ctx(ch, "BTC-S1")
    rules.shock_follow(ctx)
    assert len(ref) > 10
    assert [(p.t_in, p.side) for p in ref] == [(tr.t_in, tr.side) for tr in ctx.trades]
    assert [p.net for p in ref] == pytest.approx([tr.net for tr in ctx.trades], abs=1e-6)
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_rules.py -q`
Expected: FAIL, `No module named 'research.lab.strategies'`.

- [ ] **Step 3: Implement**

`research/lab/strategies/__init__.py`:

```python
"""Lab strategies: functions fn(ctx, **params) that trade one chunk and append to ctx.trades."""
```

`research/lab/strategies/rules.py` (the import block already lists what Tasks 9 and 10 add):

```python
"""The researched rules (research/results/strategy_search.md, strategy_prereg.md) as lab strategies.

Each function trades one chunk through run_intents. Stops and targets are distances from the fill unless a
rule names a price (range ends, previous close). D1 bars close at 17:00 New York and D1 entries and time
exits wait 2 h (engine.D1_ENTRY_DELAY_MS). Rules that need other symbols' history (X1, FXM1, MEF) read the
real M1 cache and are catalogued as real-data only."""
import math
import re
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache, reduce
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from research.indicators import atr_sma, ema, prior_max, prior_min, rsi
from research.lab.engine import D1_ENTRY_DELAY_MS, DAY_MS, NAN, Ctx, Intent, run_intents
from research.lab.universe import FX_REAL
from research.scan.data import atr as scan_atr, resample
from research.scan.engine import Order, simulate
from research.scan.m1 import load as load_m1
from research.sim import _first_hit

TF_MIN = {"M15": 15, "H1": 60, "H4": 240, "D1": 1440}


def _delay(b) -> int:
    return D1_ENTRY_DELAY_MS if b.minutes == 1440 else 0


def _intents(b, a, sig, H, SLK, TPK, warm) -> List[Intent]:
    n, d = len(b), _delay(b)
    out = []
    for i in np.flatnonzero(sig):
        if i < warm or not math.isfinite(a[i]) or a[i] <= 0:
            continue
        out.append(Intent(int(b.close_time[i]) + d, int(sig[i]), SLK * a[i], TPK * a[i] if TPK else NAN,
                          int(b.close_time[min(i + H, n - 1)]) + d))
    return out


def shock_follow(ctx: Ctx, tf: int = 15, Z: float = 2.5, H: int = 12, SLK: float = 2.0, TPK: float = 2.0) -> None:
    """BTC-S1: a bar whose close moved more than Z x ATR20 (SMA of TR) -> follow at the next tick; SL/TP x ATR
    from the fill; time exit at the first tick after bar i + H closes."""
    b = ctx.bars(tf)
    a = atr_sma(b.h, b.l, b.c, 20)
    with np.errstate(invalid="ignore", divide="ignore"):
        mv = np.r_[0.0, np.diff(b.c)] / a
    sig = np.where(mv > Z, 1, np.where(mv < -Z, -1, 0))
    run_intents(ctx, _intents(b, a, sig, H, SLK, TPK, 25))


def bank_rule(ctx: Ctx, kind: str, mode: int, tf: str, H: int, SLK: float, TPK=None, L: int = 1,
              Z: float = 1.0, N: int = 20, P: int = 14, lo: float = 30.0, warm: int = 25) -> None:
    """research/scan/bank.py's families: zmove (C - C[L] beyond Z x ATR20), donch (first close beyond the prior
    N-bar high/low), rsi (RSI(P) beyond 100 - lo / lo). mode +1 follows the move, -1 fades it."""
    b = ctx.bars(TF_MIN[tf])
    a = atr_sma(b.h, b.l, b.c, 20)
    n = len(b)
    with np.errstate(invalid="ignore", divide="ignore"):
        if kind == "zmove":
            z = np.zeros(n)
            z[L:] = (b.c[L:] - b.c[:-L]) / a[L:]
            raw = np.where(z > Z, 1, np.where(z < -Z, -1, 0))
        elif kind == "donch":
            up, dn = b.c > prior_max(b.h, N), b.c < prior_min(b.l, N)
            raw = np.where(up & ~np.r_[False, up[:-1]], 1, np.where(dn & ~np.r_[False, dn[:-1]], -1, 0))
        elif kind == "rsi":
            r = rsi(b.c, P)
            raw = np.where(r > 100 - lo, 1, np.where(r < lo, -1, 0))
        else:
            raise ValueError(kind)
    run_intents(ctx, _intents(b, a, raw * mode, H, SLK, TPK, warm))


_BANK = re.compile(r"(zmove|donch|rsi)([FR])_(M15|H1|H4|D1)_(.*)_H(\d+)_SL([\d.]+)_TP(None|[\d.]+)$")


def parse_bank(name: str) -> dict:
    """'zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0' -> bank_rule keyword arguments."""
    kind, fr, tf, mid, H, SL, TP = _BANK.match(name).groups()
    kw = dict(kind=kind, mode=1 if fr == "F" else -1, tf=tf, H=int(H), SLK=float(SL),
              TPK=None if TP == "None" else float(TP))
    for part in mid.split("_"):
        key = re.match(r"[A-Za-z]+", part).group()
        val = part[len(key):]
        kw[key] = float(val) if "." in val else int(val)
    if "lo" in kw:
        kw["lo"] = float(kw["lo"])
    return kw


# The 552-config bank's best cell per (kind, direction, timeframe) by pooled 2025 mean R with n >= 30
# (research/results/bank_stats.csv, P1), frozen 2026-09-25 for the lab. The 2025 means are in the catalog.
BANK_CONFIGS = (
    "donchF_D1_N55_H6_SL1.0_TP1.5", "donchF_H1_N10_H24_SL2.5_TPNone", "donchF_H4_N55_H6_SL1.0_TP1.5",
    "donchF_M15_N55_H24_SL2.5_TPNone", "donchR_D1_N10_H6_SL1.5_TPNone", "donchR_H1_N20_H6_SL1.5_TPNone",
    "donchR_H4_N55_H24_SL2.5_TPNone", "donchR_M15_N55_H24_SL2.5_TPNone", "rsiF_D1_P14_lo30_H6_SL1.0_TP1.0",
    "rsiF_H1_P14_lo20_H12_SL2.0_TPNone", "rsiF_H4_P2_lo10_H12_SL2.0_TPNone", "rsiF_M15_P14_lo20_H12_SL2.0_TPNone",
    "rsiR_D1_P2_lo5_H3_SL1.5_TPNone", "rsiR_H1_P2_lo5_H3_SL1.5_TPNone", "rsiR_H4_P14_lo20_H12_SL2.0_TPNone",
    "rsiR_M15_P2_lo5_H12_SL2.0_TPNone", "zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0", "zmoveF_H1_L3_Z3.0_H3_SL1.0_TP1.0",
    "zmoveF_H4_L1_Z3.0_H12_SL2.0_TPNone", "zmoveF_M15_L1_Z3.0_H12_SL2.0_TPNone", "zmoveR_D1_L3_Z3.0_H12_SL2.0_TPNone",
    "zmoveR_H1_L1_Z3.0_H12_SL2.0_TPNone", "zmoveR_H4_L3_Z3.0_H12_SL2.0_TPNone", "zmoveR_M15_L1_Z1.0_H12_SL2.0_TPNone",
)
# 2025 pooled mean R of each, same order (for the catalog's findings).
BANK_2025_R = (-0.051, -0.012, -0.018, -0.063, +0.099, -0.023, +0.113, -0.049, -0.047, +0.026, -0.014, -0.013,
               +0.063, -0.043, +0.124, -0.067, +0.107, +0.023, +0.246, -0.047, +0.137, -0.025, +0.092, -0.063)
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_rules.py -q`
Expected: 5 passed (the ticksim parity test needs the tick cache; it must pass, not skip, on this Mac).

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 9: Researched rules B — index sessions (TOM, K2 ORB, VB1, LC1, GF1, OD1)

**Files:**
- Modify: `research/lab/strategies/rules.py` (append)
- Test: `research/tests/lab/test_lab_sessions.py`

**Interfaces:**
- Produces: `rules.SESSIONS`, `rules.session_days(ctx, tz_name, t_open, t_close) -> [(date, open_ms, close_ms)]`, `rules.turn_of_month(ctx, sl_pct=0.03)`, `rules.opening_range(ctx, minutes=60)`, `rules.vol_breakout(ctx, k=0.35, lookback=5)`, `rules.last30_fade(ctx)`, `rules.gap_fade(ctx, k=0.1, lookback=5)`, `rules.overnight_drift(ctx)`.

- [ ] **Step 1: Write the failing tests** (`research/tests/lab/test_lab_sessions.py`)

```python
import math
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.strategies import rules  # noqa: E402

NY = ZoneInfo("America/New_York")


def _ms(d, hh, mm=0, tz=timezone.utc):
    return int(datetime.combine(d, time(hh, mm), tz).timestamp() * 1000)


def _minutes(days, price):
    ts = np.concatenate([_ms(d, 0) + np.arange(1440, dtype=np.int64) * 60_000 for d in days])
    return ts, np.array([price(int(x)) for x in ts])


def _wave(t, amp=50.0, period_min=60):
    return 40000.0 + amp * math.sin(2 * math.pi * (t // 60_000) / period_min)


def _weekdays(start, n):
    return [d for d in (start + timedelta(days=k) for k in range(n)) if d.weekday() < 5]


def test_turn_of_month_trades_the_last_and_the_first_three_days():
    days = _weekdays(date(2025, 1, 20), 19)                     # Jan 20 .. Feb 7
    ts, px = _minutes(days, lambda t: 40000.0)
    ch = make_chunk(ts, px, spread=1.0, symbol="US30", lo=_ms(date(2025, 1, 27), 0))
    ctx = Ctx(ch, "TOM")
    rules.turn_of_month(ctx)
    got = [datetime.fromtimestamp(tr.t_in / 1000, NY) for tr in ctx.trades]
    assert [g.date() for g in got] == [date(2025, 1, 31), date(2025, 2, 3), date(2025, 2, 4), date(2025, 2, 5)]
    assert all((g.hour, g.minute) == (9, 30) for g in got) and all(tr.why == "time" for tr in ctx.trades)
    assert ctx.trades[0].sl0 == pytest.approx(40000 * 0.97)


def test_opening_range_follows_the_first_hour_with_the_stop_at_the_far_end():
    d = date(2025, 1, 15)
    o = _ms(d, 9, 30, NY)
    ts, px = _minutes([d], lambda t: 40000.0 + 100.0 * min(max((t - o) / 3_600_000, 0.0), 1.0))
    ctx = Ctx(make_chunk(ts, px, spread=1.0, symbol="US30"), "K2")
    rules.opening_range(ctx)
    (tr,) = ctx.trades
    assert tr.side == 1 and tr.sl0 == pytest.approx(40000.0) and tr.t_in == o + 3_600_000 and tr.why == "time"


def test_vol_breakout_buys_the_first_touch_above_the_open():
    days = _weekdays(date(2025, 1, 6), 8)                       # Jan 6-10, 13
    last = days[-1]

    def price(t):
        if datetime.fromtimestamp(t / 1000, timezone.utc).date() < last:
            return _wave(t)
        return 40000.0 if t < _ms(last, 10, 0, NY) else 40060.0

    ts, px = _minutes(days, price)
    ctx = Ctx(make_chunk(ts, px, spread=1.0, symbol="US30", lo=_ms(last, 0)), "VB1")
    rules.vol_breakout(ctx)
    (tr,) = ctx.trades
    assert tr.side == 1 and tr.sl0 == pytest.approx(40000.0) and tr.t_in == _ms(last, 10, 0, NY)


def test_last30_fades_the_mid_session_move():
    d = date(2025, 1, 15)
    a, b = _ms(d, 10, 0, NY), _ms(d, 15, 30, NY)
    ts, px = _minutes([d], lambda t: 40000.0 + 100.0 * min(max((t - a) / (b - a), 0.0), 1.0))
    ctx = Ctx(make_chunk(ts, px, spread=1.0, symbol="US30"), "LC1")
    rules.last30_fade(ctx)
    (tr,) = ctx.trades
    assert tr.side == -1 and tr.t_in == b and tr.why == "time" and tr.sl0 > tr.entry


def test_gap_fade_targets_the_previous_close():
    days = _weekdays(date(2025, 1, 6), 10)                      # 8 sessions, the last one gaps up
    last = days[-1]

    def price(t):
        d = datetime.fromtimestamp(t / 1000, timezone.utc).date()
        if d == last:
            return 40050.0 if t < _ms(last, 10, 0, NY) else 39990.0
        return 40000.0 if t >= _ms(d, 15, 0, NY) else _wave(t)

    ts, px = _minutes(days, price)
    ctx = Ctx(make_chunk(ts, px, spread=1.0, symbol="US30", lo=_ms(last, 0)), "GF1")
    rules.gap_fade(ctx)
    (tr,) = ctx.trades
    assert tr.side == -1 and tr.tp0 == pytest.approx(40000.0) and tr.sl0 == pytest.approx(40100.0)
    assert tr.why == "tp"


def test_overnight_drift_is_long_from_two_to_three_new_york():
    days = [date(2025, 1, 13), date(2025, 1, 14), date(2025, 1, 15)]
    ts, px = _minutes(days, lambda t: _wave(t, amp=20.0, period_min=90))
    ctx = Ctx(make_chunk(ts, px, spread=1.0, symbol="US30", lo=_ms(days[-1], 0)), "OD1")
    rules.overnight_drift(ctx)
    (tr,) = ctx.trades
    assert tr.side == 1 and tr.t_in == _ms(days[-1], 2, 0, NY) and tr.t_out == _ms(days[-1], 3, 0, NY)
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_sessions.py -q`
Expected: FAIL, `module ... has no attribute 'turn_of_month'`.

- [ ] **Step 3: Implement** — append to `research/lab/strategies/rules.py`:

```python
# ---------------------------------------------------------------- index cash sessions
SESSIONS = {"US30": ("America/New_York", time(9, 30), time(16, 0)),
            "USTEC": ("America/New_York", time(9, 30), time(16, 0)),
            "DE40": ("Europe/Berlin", time(9, 0), time(17, 30)),
            "UK100": ("Europe/London", time(8, 0), time(16, 30))}
OPEN_TOLERANCE_MS = 5 * 60_000


def session_days(ctx: Ctx, tz_name: str, t_open: time, t_close: time):
    """[(date, open_ms, close_ms)] for the weekdays from two weeks before the chunk's year (look-backs) whose
    open has a tick within 5 minutes; a holiday has none."""
    tz, t = ZoneInfo(tz_name), ctx.t
    d = datetime.fromtimestamp(ctx.ch.lo_ms / 1000, timezone.utc).date() - timedelta(days=14)
    last = datetime.fromtimestamp(ctx.ch.hi_ms / 1000, timezone.utc).date()
    out = []
    while d <= last:
        if d.weekday() < 5:
            o = int(datetime.combine(d, t_open, tz).timestamp() * 1000)
            e = ctx.tick_at(o)
            if e < len(t) and t.ts[e] < o + OPEN_TOLERANCE_MS:
                out.append((d, o, int(datetime.combine(d, t_close, tz).timestamp() * 1000)))
        d += timedelta(days=1)
    return out


def _index_days(ctx: Ctx):
    return session_days(ctx, *SESSIONS[ctx.ch.symbol])


def _bid_at(ctx: Ctx, ms: int) -> float:
    e = ctx.tick_at(ms)
    return float(ctx.t.bid[e]) if e < len(ctx.t) else NAN


def _bid_before(ctx: Ctx, ms: int) -> float:
    e = ctx.tick_at(ms) - 1
    return float(ctx.t.bid[e]) if e >= 0 else NAN


def _hl(ctx: Ctx, a_ms: int, b_ms: int):
    m = ctx.bars(1)
    i0, i1 = np.searchsorted(m.open_time, [a_ms, b_ms], side="left")
    if i1 <= i0:
        return NAN, NAN
    return float(m.h[i0:i1].max()), float(m.l[i0:i1].min())


def _tom_days(days):
    """The last trading day of each month (once the next month has started) and its first three."""
    by_month = {}
    for d in sorted(days):
        by_month.setdefault((d.year, d.month), []).append(d)
    months = sorted(by_month)
    out = set()
    for k, key in enumerate(months):
        out.update(by_month[key][:3])
        if k + 1 < len(months):
            out.add(by_month[key][-1])
    return out


def turn_of_month(ctx: Ctx, sl_pct: float = 0.03) -> None:
    """TOM: long over the cash session on the last and the first three trading days of each month; SL 3 %."""
    days = _index_days(ctx)
    tom = _tom_days([d for d, _, _ in days])
    run_intents(ctx, [Intent(o, 1, sl_px=_bid_at(ctx, o) * (1 - sl_pct), exit_ms=c)
                      for d, o, c in days if d in tom])


def opening_range(ctx: Ctx, minutes: int = 60) -> None:
    """K2: direction of the first `minutes` of the cash session, entered at its end, stop at the other end of
    the range, exit at the session close."""
    its = []
    for _, o, c in _index_days(ctx):
        end = o + minutes * 60_000
        hi, lo = _hl(ctx, o, end)
        first, last = _bid_at(ctx, o), _bid_before(ctx, end)
        if not math.isfinite(hi) or not math.isfinite(last) or last == first:
            continue
        side = 1 if last > first else -1
        its.append(Intent(end, side, sl_px=lo if side > 0 else hi, exit_ms=c))
    run_intents(ctx, its)


def vol_breakout(ctx: Ctx, k: float = 0.35, lookback: int = 5) -> None:
    """VB1: stop entries at the open +/- k x the mean range of the last sessions; the first side touched
    trades, SL at the open, exit at the session close."""
    t, ranges, its = ctx.t, [], []
    for _, o, c in _index_days(ctx):
        hi, lo = _hl(ctx, o, c)
        if len(ranges) >= lookback:
            rng = float(np.mean(ranges[-lookback:]))
            e0, e1 = ctx.tick_at(o), ctx.tick_at(c)
            op = float(t.bid[e0])
            jb = _first_hit(t.ask[:e1], e0, -np.inf, op + k * rng)
            js = _first_hit(t.bid[:e1], e0, op - k * rng, np.inf)
            if min(jb, js) < e1:
                its.append(Intent(int(t.ts[min(jb, js)]), 1 if jb <= js else -1, sl_px=op, exit_ms=c))
        if math.isfinite(hi):
            ranges.append(hi - lo)
    run_intents(ctx, its)


def last30_fade(ctx: Ctx) -> None:
    """LC1 (US30, USTEC): fade C(15:30) - C(10:00) New York from 15:30 to the 16:00 close; SL 2 x ATR20(30 min)."""
    b = ctx.bars(30)
    a = atr_sma(b.h, b.l, b.c, 20)
    its = []
    for _, o, c in session_days(ctx, "America/New_York", time(9, 30), time(16, 0)):
        t10, t1530 = o + 30 * 60_000, c - 30 * 60_000
        mid = _bid_before(ctx, t1530) - _bid_before(ctx, t10)
        k = int(np.searchsorted(b.close_time, t1530, side="right")) - 1
        if math.isfinite(mid) and mid != 0 and k >= 20 and math.isfinite(a[k]):
            its.append(Intent(t1530, -1 if mid > 0 else 1, 2.0 * a[k], exit_ms=c))
    run_intents(ctx, its)


def gap_fade(ctx: Ctx, k: float = 0.1, lookback: int = 5) -> None:
    """GF1 (US30, USTEC): an opening gap larger than k x the mean session range is faded at 9:31, TP at the
    previous close, SL the gap's size beyond the open, exit at the close."""
    ranges, prev_c, its = [], None, []
    for _, o, c in session_days(ctx, "America/New_York", time(9, 30), time(16, 0)):
        hi, lo = _hl(ctx, o, c)
        if prev_c is not None and len(ranges) >= lookback:
            op, pc = _bid_at(ctx, o), _bid_before(ctx, prev_c)
            gap = op - pc
            if math.isfinite(gap) and abs(gap) > k * float(np.mean(ranges[-lookback:])):
                side = -1 if gap > 0 else 1
                its.append(Intent(o + 60_000, side, sl_px=op - side * abs(gap), tp_px=pc, exit_ms=c))
        if math.isfinite(hi):
            ranges.append(hi - lo)
        prev_c = c
    run_intents(ctx, its)


def overnight_drift(ctx: Ctx) -> None:
    """OD1 (US30, USTEC): long 02:00 -> 03:00 New York on weekdays; SL 2 x ATR20(H1)."""
    b = ctx.bars(60)
    a = atr_sma(b.h, b.l, b.c, 20)
    its = []
    for _, o, c in session_days(ctx, "America/New_York", time(2, 0), time(3, 0)):
        k = int(np.searchsorted(b.close_time, o, side="right")) - 1
        if k >= 20 and math.isfinite(a[k]):
            its.append(Intent(o, 1, 2.0 * a[k], exit_ms=c))
    run_intents(ctx, its)
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_sessions.py -q`
Expected: 6 passed.

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 10: Researched rules C — FX D1/H4 (K1, FXM1, X1), MEF, WF1

**Files:**
- Modify: `research/lab/strategies/rules.py` (append)
- Test: `research/tests/lab/test_lab_fx_rules.py`

**Interfaces:**
- Consumes: `research.scan.m1.load`, `research.scan.data.resample, atr`, `research.scan.engine.Order, simulate`.
- Produces: `rules.weekly_fade(ctx, L=5, Z=1.5, H=5, SLK=3.0)`, `rules.regime_fade(ctx, window_days=120)`, `rules.cross_sectional_reversal(ctx)`, `rules.month_end_fix(ctx)`, `rules.walk_forward_ridge(ctx, tf=15, train_months=6, lam=0.1, q=0.9, SLK=2.0)`, helpers `rules._m1(symbol)` (cached M1 load), `rules._m1_close_before(symbol, ms)`, `rules._fx_fade_log() -> ndarray (n, 2)`, `rules._x1_schedule() -> {pair: [(at_ms, side, exit_ms)]}`, `rules.MEF_SIDE`.

- [ ] **Step 1: Write the failing tests** (`research/tests/lab/test_lab_fx_rules.py`)

```python
import math
from datetime import date, datetime, time, timedelta, timezone

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk, needs_m1, needs_ticks  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import load_chunk  # noqa: E402
from research.lab.strategies import rules  # noqa: E402


def _ms(d, hh, mm=0):
    return int(datetime.combine(d, time(hh, mm), timezone.utc).timestamp() * 1000)


def _hourly(days, price):
    ts, px = [], []
    for n, d in enumerate(days):
        for h in range(24):
            if d.weekday() == 4 and h >= 21:
                break                                   # the FX week ends Friday 21:00 UTC
            ts.append(_ms(d, h))
            px.append(price(n, h))
    return np.array(ts, np.int64), np.array(px)


def _weekdays(start, n):
    return [d for d in (start + timedelta(days=k) for k in range(n)) if d.weekday() < 5]


def test_weekly_fade_sells_a_rally_two_hours_after_the_new_york_close():
    days = _weekdays(date(2025, 1, 6), 70)
    ts, px = _hourly(days, lambda n, h: 1.10 + max(0, n - 39) * 0.002 + 0.002 * math.sin(2 * math.pi * h / 24))
    ctx = Ctx(make_chunk(ts, px), "K1")
    rules.weekly_fade(ctx)
    tr = ctx.trades[0]
    assert tr.side == -1 and tr.sl0 > tr.entry
    b = ctx.bars(1440)
    assert int(tr.t_in - 2 * 3_600_000) in set(int(x) for x in b.close_time)


def test_month_end_fix_sells_usd_when_us_stocks_beat_germany(monkeypatch):
    cut = _ms(date(2025, 1, 31), 0)
    prices = {"US30": (40000.0, 41000.0), "DE40": (20000.0, 20100.0), "EURUSD": (1.0, 1.0)}
    monkeypatch.setattr(rules, "_m1_close_before", lambda s, ms: prices[s][1] if ms > cut else prices[s][0])
    days = _weekdays(date(2025, 1, 1), 31)
    ts, px = _hourly(days, lambda n, h: 1.10 + (0.0005 if h % 2 else -0.0005))    # ATR(H1) 0.001, never stopped
    ctx = Ctx(make_chunk(ts, px), "MEF")
    rules.month_end_fix(ctx)
    (tr,) = ctx.trades
    assert tr.side == 1 and tr.t_in == _ms(date(2025, 1, 31), 10) and tr.t_out == _ms(date(2025, 1, 31), 16)


@needs_m1
def test_x1_schedule_trades_three_pairs_per_rebalance_for_thirty_h4_bars():
    sched = rules._x1_schedule()
    by_time = {}
    for pair, rows in sched.items():
        for at, side, ex in rows:
            by_time.setdefault(at, []).append(pair)
            assert side in (-1, 1)
    assert len(by_time) > 50 and all(len(v) == 3 for v in by_time.values())
    at, _, ex = sched["EURUSD"][0]
    assert ex - at <= 30 * 4 * 3_600_000 + 4 * 86_400_000       # 30 H4 bars (weekends widen the gap)


@needs_m1
def test_fx_fade_log_has_closed_base_trades():
    log = rules._fx_fade_log()
    assert log.shape[1] == 2 and len(log) > 100 and np.all(np.diff(log[:, 0]) >= 0)


@needs_ticks
def test_walk_forward_ridge_trades_only_inside_the_year():
    ch = load_chunk("EURUSD", "real", 2025)
    ctx = Ctx(ch, "WF1")
    rules.walk_forward_ridge(ctx)
    assert ctx.trades and all(ch.lo_ms <= tr.t_in < ch.hi_ms for tr in ctx.trades)
    assert all(math.isfinite(tr.sl0) for tr in ctx.trades)
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_fx_rules.py -q`
Expected: FAIL, `module ... has no attribute 'weekly_fade'`.

- [ ] **Step 3: Implement** — append to `research/lab/strategies/rules.py`:

```python
# ---------------------------------------------------------------- FX D1 / H4 and cross-symbol rules
_m1 = lru_cache(maxsize=None)(load_m1)


def _d1_z(b, L):
    a = atr_sma(b.h, b.l, b.c, 20)
    z = np.full(len(b), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        z[L:] = (b.c[L:] - b.c[:-L]) / a[L:]
    return a, z


def weekly_fade(ctx: Ctx, L: int = 5, Z: float = 1.5, H: int = 5, SLK: float = 3.0) -> None:
    """K1 / K1b: a 5-day move beyond Z x ATR20(D1) is faded 2 h after the New York close; SL SLK x ATR from
    the signal close, no target, time exit H D1 bars later."""
    b = ctx.bars(1440)
    a, z = _d1_z(b, L)
    n, d, its = len(b), _delay(b), []
    for i in range(25, n):
        if math.isfinite(z[i]) and abs(z[i]) > Z and math.isfinite(a[i]):
            side = -1 if z[i] > 0 else 1
            its.append(Intent(int(b.close_time[i]) + d, side, sl_px=b.c[i] - side * SLK * a[i],
                              exit_ms=int(b.close_time[min(i + H, n - 1)]) + d))
    run_intents(ctx, its)


@lru_cache(maxsize=1)
def _fx_fade_log() -> np.ndarray:
    """(exit ms, R) of K1's base fade trades on the 8 real FX pairs, M1 engine, D1 cut at 00:00 UTC (FXM1's
    regime input, as pre-registered)."""
    rows = []
    for s in FX_REAL:
        m = _m1(s)
        b = resample(m, 1440)
        a = scan_atr(b, 20)
        n = len(b)
        z = np.full(n, np.nan)
        with np.errstate(invalid="ignore", divide="ignore"):
            z[5:] = (b.c[5:] - b.c[:-5]) / a[5:]
        orders = []
        for i in range(25, n - 1):
            if math.isfinite(z[i]) and abs(z[i]) > 1.5 and math.isfinite(a[i]):
                side = -1 if z[i] > 0 else 1
                orders.append(Order(int(b.last[i]) + 1, side, b.c[i] - side * 3.0 * a[i], int(b.last[min(i + 5, n - 1)])))
        rows += [(f.t_out, f.r) for f in simulate(m, s, orders)]
    return np.array(sorted(rows), float).reshape(-1, 2)


def regime_fade(ctx: Ctx, window_days: int = 120) -> None:
    """FXM1: K1's fade, traded in the direction the base fade earned over the last 120 days on the 8 pairs
    (sum of R > 0 -> fade, < 0 -> follow)."""
    log = _fx_fade_log()
    b = ctx.bars(1440)
    a, z = _d1_z(b, 5)
    n, d, its = len(b), _delay(b), []
    for i in range(25, n):
        if not (math.isfinite(z[i]) and abs(z[i]) > 1.5 and math.isfinite(a[i])):
            continue
        T = int(b.close_time[i])
        sel = (log[:, 0] < T) & (log[:, 0] >= T - window_days * DAY_MS)
        regime = np.sign(log[sel, 1].sum())
        if regime == 0:
            continue
        side = int((-1 if z[i] > 0 else 1) * regime)
        its.append(Intent(T + d, side, sl_px=b.c[i] - side * 3.0 * a[i], exit_ms=int(b.close_time[min(i + 5, n - 1)]) + d))
    run_intents(ctx, its)


@lru_cache(maxsize=1)
def _x1_schedule(L: int = 30, hold: int = 30, top: int = 3):
    """X1: currency strengths = least-squares fit of the 8 pairs' 30-bar H4 log returns (6 currencies, sum 0);
    pair score = (strength base - strength quote) / (ATR20 / price). Every 30 H4 bars the 3 largest |score|
    are traded against the score for 30 bars, no stop."""
    ccys = ("AUD", "CAD", "EUR", "GBP", "JPY", "USD")
    bars = {s: resample(_m1(s), 240) for s in FX_REAL}
    common = reduce(np.intersect1d, [b.t for b in bars.values()])
    idx = {s: np.searchsorted(bars[s].t, common) for s in FX_REAL}
    logc = np.column_stack([np.log(bars[s].c[idx[s]]) for s in FX_REAL])
    atr_rel = np.column_stack([scan_atr(bars[s], 20)[idx[s]] / bars[s].c[idx[s]] for s in FX_REAL])
    A = np.zeros((len(FX_REAL), len(ccys)))
    for p, s in enumerate(FX_REAL):
        A[p, ccys.index(s[:3])], A[p, ccys.index(s[3:])] = 1.0, -1.0
    M = np.vstack([A, np.ones(len(ccys))])
    close = common + 240 * 60_000
    sched = {s: [] for s in FX_REAL}
    for k in range(L + 20, len(common) - 1, hold):
        r, ar = logc[k] - logc[k - L], atr_rel[k]
        if not (np.all(np.isfinite(r)) and np.all(np.isfinite(ar)) and np.all(ar > 0)):
            continue
        score = (A @ np.linalg.lstsq(M, np.r_[r, 0.0], rcond=None)[0]) / ar
        for p in np.argsort(-np.abs(score))[:top]:
            sched[FX_REAL[p]].append((int(close[k]), -int(np.sign(score[p])),
                                      int(close[min(k + hold, len(common) - 1)])))
    return sched


def cross_sectional_reversal(ctx: Ctx) -> None:
    run_intents(ctx, [Intent(at, side, exit_ms=ex) for at, side, ex in _x1_schedule().get(ctx.ch.symbol, []) if side])


MEF_SIDE = {"EURUSD": 1, "GBPUSD": 1, "AUDUSD": 1, "USDCAD": -1, "USDJPY": -1}   # the side that sells USD
LONDON = ZoneInfo("Europe/London")


def _m1_close_before(symbol: str, ms: int) -> float:
    m = _m1(symbol)
    k = int(np.searchsorted(m["ts"], ms, side="left")) - 1
    return float(m["c"][k]) if k >= 0 else NAN


def month_end_fix(ctx: Ctx) -> None:
    """MEF: on the last business day of the month, 10:00 -> 16:00 London, sell USD if US30 beat DE40 (in USD)
    over the month to date, else buy it; SL 2 x ATR20(H1)."""
    b = ctx.bars(60)
    a = atr_sma(b.h, b.l, b.c, 20)
    side0 = MEF_SIDE[ctx.ch.symbol]
    d0 = datetime.fromtimestamp(ctx.ch.lo_ms / 1000, timezone.utc).date() - timedelta(days=40)
    d1 = datetime.fromtimestamp(ctx.ch.hi_ms / 1000, timezone.utc).date()
    y, m, its = d0.year, d0.month, []
    while (y, m) <= (d1.year, d1.month):
        nxt = date(y + (m == 12), m % 12 + 1, 1)
        d = nxt - timedelta(days=1)
        while d.weekday() >= 5:
            d -= timedelta(days=1)
        at = int(datetime.combine(d, time(10, 0), LONDON).timestamp() * 1000)
        ex = int(datetime.combine(d, time(16, 0), LONDON).timestamp() * 1000)
        start = int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000)
        us = _m1_close_before("US30", at) / _m1_close_before("US30", start) - 1
        de = (_m1_close_before("DE40", at) * _m1_close_before("EURUSD", at)
              / (_m1_close_before("DE40", start) * _m1_close_before("EURUSD", start)) - 1)
        k = int(np.searchsorted(b.close_time, at, side="right")) - 1
        if math.isfinite(us) and math.isfinite(de) and us != de and k >= 20 and math.isfinite(a[k]):
            its.append(Intent(at, side0 if us > de else -side0, 2.0 * a[k], exit_ms=ex))
        y, m = nxt.year, nxt.month
    run_intents(ctx, its)


WF_HORIZON = 4


def _wf_features(b):
    """research/scan/wf.py's 14 causal features at each bar close and the target (C[i+4] - C[i]) / ATR20."""
    c = b.c
    a20, a5 = atr_sma(b.h, b.l, c, 20), atr_sma(b.h, b.l, c, 5)
    n_ticks = (b.event_tick - b.first_tick).astype(float)
    F = {}
    for k in (1, 4, 16, 64):
        r = np.full(len(c), np.nan)
        r[k:] = (c[k:] - c[:-k]) / a20[k:]
        F[f"r{k}"] = r
    hh, ll = np.full(len(c), np.nan), np.full(len(c), np.nan)
    if len(c) >= 20:
        hh[19:], ll[19:] = sliding_window_view(b.h, 20).max(axis=1), sliding_window_view(b.l, 20).min(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        F["rangepos"] = (c - ll) / (hh - ll) - 0.5
        F["volratio"] = a5 / a20 - 1
        F["body"] = (c - b.o) / (b.h - b.l)
        F["ema"] = (c - ema(c, 50)) / a20
        F["rsi"] = rsi(c, 14) / 50 - 1
        act = n_ticks / np.convolve(np.r_[np.full(95, n_ticks[:96].mean()), n_ticks], np.ones(96) / 96, "valid") - 1
    F["act"] = act
    F["r1xact"] = F["r1"] * act
    F["shock"] = np.sign(F["r1"]) * (np.abs(F["r1"]) > 2)
    hour = (b.open_time // 3_600_000) % 24
    F["sinh"], F["cosh"] = np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)
    y = np.full(len(c), np.nan)
    y[:-WF_HORIZON] = (c[WF_HORIZON:] - c[:-WF_HORIZON]) / a20[:-WF_HORIZON]
    return np.column_stack(list(F.values())), y, a20


def _month(ms) -> np.ndarray:
    return np.asarray(ms, np.int64).astype("datetime64[ms]").astype("datetime64[M]").astype(np.int64)


def walk_forward_ridge(ctx: Ctx, tf: int = 15, train_months: int = 6, lam: float = 0.1, q: float = 0.9,
                       SLK: float = 2.0) -> None:
    """WF1: ridge on the standardized features, refit every month on the 6 months before it; trade |pred|
    above the training months' q-quantile in the direction of the prediction, SL 2 x ATR20, exit after 4 bars."""
    b = ctx.bars(tf)
    X, y, a = _wf_features(b)
    mon = _month(b.open_time)
    finite = np.all(np.isfinite(X), axis=1)
    pred, thr = np.full(len(y), np.nan), np.full(len(y), np.nan)
    for M in range(int(_month(ctx.ch.lo_ms)), int(_month(ctx.ch.hi_ms - 1)) + 1):
        tr = (mon >= M - train_months) & (mon < M)
        idx = np.flatnonzero(tr)
        if idx.size:
            tr[idx[-WF_HORIZON:]] = False              # their labels reach into month M
        ok = tr & finite & np.isfinite(y)
        if ok.sum() < 500:
            continue
        mu, sd = X[ok].mean(0), X[ok].std(0) + 1e-12
        Z = (X[ok] - mu) / sd
        yt = np.clip(y[ok], -5, 5)
        w = np.linalg.solve(Z.T @ Z + lam * ok.sum() * np.eye(Z.shape[1]), Z.T @ (yt - yt.mean()))
        te = (mon == M) & finite
        pred[te] = ((X[te] - mu) / sd) @ w + yt.mean()
        thr[te] = np.quantile(np.abs(Z @ w + yt.mean()), q)
    with np.errstate(invalid="ignore"):
        sig = np.where(np.abs(pred) > thr, np.sign(pred), 0).astype(int)
    n = len(b)
    run_intents(ctx, [Intent(int(b.close_time[i]), int(sig[i]), SLK * a[i], NAN,
                             int(b.close_time[min(i + WF_HORIZON, n - 1)]))
                      for i in np.flatnonzero(sig) if math.isfinite(a[i]) and a[i] > 0])
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_fx_rules.py -q`
Expected: 5 passed (the M1 / tick tests must pass, not skip, on this Mac).

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---
### Task 11: FlowRSI adapter (fixed units in the calibrated replica)

**Files:**
- Modify: `research/sim.py` (additive: `Trade.fills/sl0/tp0`, `place_order(..., fixed_units=None)`, `_close` records fills, `run_account(..., fixed_units=None)`)
- Create: `research/lab/strategies/flowrsi.py`
- Test: `research/tests/lab/test_lab_flowrsi.py`

**Interfaces:**
- Consumes: `research.signals.Market, build`, `research.sim.make_levels, run_account`, `research.screen.params_for(symbol, name, exit_mode)`, `universe.PRESET_TEMPLATE`, `Instrument.spec()`.
- Produces: `flowrsi.flowrsi(ctx, name="C0", exit_mode="X2")`; `sim.Trade.fills: list[(tick, price, units)]`, `sim.Trade.sl0`, `sim.Trade.tp0`.

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_ticks  # noqa: E402
from research.bars import build_bars  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk  # noqa: E402
from research.lab.strategies.flowrsi import flowrsi  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.screen import params_for  # noqa: E402
from research.signals import Market, build  # noqa: E402
from research.sim import make_levels, place_order, run_account  # noqa: E402
from research.specs import SPECS, flowrsi_params  # noqa: E402
from research.ticks import day_ms, load_ticks  # noqa: E402


def test_place_order_with_fixed_units_skips_the_risk_sizing():
    p = flowrsi_params("XAUUSD")
    spec = SPECS["XAUUSD"]
    assert place_order(1, 2900.0, 2930.0, 2915.0, 2915.2, 100.0, spec, p) is None      # min-lot guard at $100
    units, sl, tp = place_order(1, 2900.0, 2930.0, 2915.0, 2915.2, 100.0, spec, p, fixed_units=2.0)
    assert units == 2.0 and sl == pytest.approx(2900.0) and tp == pytest.approx(2930.0)


@needs_ticks
def test_flowrsi_adapter_matches_the_replica_with_fixed_units():
    t = load_ticks("EURUSD", date(2025, 3, 1), date(2025, 4, 15))
    ch = Chunk("EURUSD", "real", 2025, t, day_ms(date(2025, 3, 10)), day_ms(date(2025, 4, 10)), instrument("EURUSD"))
    ctx = Ctx(ch, "FLOWRSI")
    flowrsi(ctx, "C0", "X2")
    spec, p = SPECS["EURUSD"], params_for("EURUSD", "C0", "X2")
    m = Market(build_bars(t, 15), build_bars(t, 60), build_bars(t, 240))
    sig = build("C0", m, spec, p).copy()
    sig[m.m15.close_time >= ch.hi_ms] = 0
    ref, _ = run_account(t, m.m15, sig, make_levels(m.m15, spec, p, "swing"), spec, p, "X2", 10_000.0,
                         start_ms=ch.lo_ms, fixed_units=10_000.0)
    assert len(ref) > 5
    assert [(r.entry_ts, r.side) for r in ref] == [(tr.t_in, tr.side) for tr in ctx.trades]
    assert [r.net for r in ref] == pytest.approx([tr.net for tr in ctx.trades], abs=1e-6)
    assert all(tr.units == 10_000 and np.isfinite(tr.sl0) for tr in ctx.trades)
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_flowrsi.py -q`
Expected: FAIL (`No module named 'research.lab.strategies.flowrsi'`; `place_order() got an unexpected keyword argument 'fixed_units'`).

- [ ] **Step 3: Edit `research/sim.py`** (additive)

- `from dataclasses import dataclass` → `from dataclasses import dataclass, field`
- in `class Trade`, after `deals: int = 0` add:

```python
    fills: list = field(default_factory=list)   # (tick, price, units) of each closing deal
    sl0: float = float("nan")                   # stop and target as placed
    tp0: float = float("nan")
```

- `place_order` signature gains `fixed_units: Optional[float] = None` (last parameter, docstring: "fixed_units replaces the risk sizing and its guards (strategy lab)"); replace `units = size_units(equity, sl_pips, spec, p)` by `units = fixed_units if fixed_units else size_units(equity, sl_pips, spec, p)` and `if abs(clamped - sl_pips) > 0.01:` by `if abs(clamped - sl_pips) > 0.01 and not fixed_units:`.
- in `_close`, after `tr.deals += 1` add `tr.fills.append((j, price, units))`.
- `run_account` signature gains `fixed_units: Optional[float] = None` (last parameter); the call becomes `order = place_order(side, tech_sl, tech_tp, b, a, equity, spec, p, fixed_units)`; after `tr = Trade(...)` add `tr.sl0, tr.tp0 = sl, tp`.

- [ ] **Step 4: Create `research/lab/strategies/flowrsi.py`**

```python
"""FlowRSI in the lab: the calibrated replica (research/signals.py + research/sim.py; Macro TMS off, which the
replica does not model) with the lab's fixed units instead of the risk sizing, and the P&L rebuilt from the
replica's fills with the lab's costs. name = C0 (live presets), C1 (SL floor 25/30) or an entry-screening
candidate E1a..E5b; exit_mode X2 = FlowRSI's break-even/partial/trailing, X1 = fixed ATR stop and 1.5R target."""
from research.lab.engine import Ctx, Pos
from research.lab.universe import PRESET_TEMPLATE
from research.screen import params_for
from research.signals import Market, build
from research.sim import make_levels, run_account


def flowrsi(ctx: Ctx, name: str = "C0", exit_mode: str = "X2") -> None:
    spec = ctx.inst.spec()
    p = params_for(PRESET_TEMPLATE.get(ctx.ch.symbol, ctx.ch.symbol), name, exit_mode)
    m = Market(ctx.bars(15), ctx.bars(60), ctx.bars(240))
    sig = build(name, m, spec, p).copy()
    sig[m.m15.close_time >= ctx.ch.hi_ms] = 0
    levels = make_levels(m.m15, spec, p, "atr" if exit_mode == "X1" else "swing")
    trades, _ = run_account(ctx.t, m.m15, sig, levels, spec, p, exit_mode, 10_000.0,
                            start_ms=max(ctx.ch.lo_ms, ctx.busy_ms + 1), fixed_units=ctx.units)
    for tr in trades:
        pos = Pos(tr.side, tr.entry_tick, tr.entry, 0.0, tr.sl0, tr.tp0, tr.sl0, tr.tp0)
        pos.deals = [(j, px, u, "exit") for j, px, u in tr.fills]
        ctx.finish(pos)
```

- [ ] **Step 5: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_flowrsi.py research/tests/test_sim.py research/tests/test_screen.py -q`
Expected: all passed (the existing sim/screen tests prove the edit is additive).

- [ ] **Step 6: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 12: Judas port

**Files:**
- Create: `research/lab/strategies/judas.py`
- Test: `research/tests/lab/test_lab_judas.py`

**Interfaces:**
- Consumes: `cbot.cbot_params("judas", symbol, **overrides)`, `engine.Ctx, Pos`, `costs.usd_per_quote`, `research.indicators.ema, true_range`, `research.sim._first_hit`.
- Produces: `judas.judas(ctx, **overrides)`, `judas.europe_dst(dt) -> bool`, `judas.us_dst(dt) -> bool`, `judas.in_killzone(dt, p) -> bool`, `judas.server_range_ok(symbol, pips) -> bool`, `judas.SIGNAL_WINDOW_BARS`. Trade exit reasons: `sl`, `tp`, `structure`, `tail`.

- [ ] **Step 1: Write the failing tests**

```python
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import bar_ticks, make_chunk  # noqa: E402
from research.lab.cbot import cbot_params  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.strategies.judas import in_killzone, judas, server_range_ok  # noqa: E402
from research.ticks import day_ms  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
T0 = day_ms(date(2025, 7, 1))                            # summer: London killzone 07-10 UTC
ASIAN = [(1.1010, 1.1020, 1.1000, 1.1010)] * 24          # 00:00-06:00: range 1.1000-1.1020 (20 pips)
PRE = [(1.1010, 1.1012, 1.1008, 1.1010)] * 4             # 06:00-07:00
SWEEP = (1.1006, 1.1007, 1.0990, 1.1004)                 # 07:00 bar: wick below the low, close back inside
QUIET = [(1.1006, 1.1008, 1.1004, 1.1006)] * 10


def _run(bars, **over):
    ts, px = bar_ticks(T0, 15, bars)
    ctx = Ctx(make_chunk(ts, px, spread=0.0001), "JUDAS")
    judas(ctx, **over)
    return ctx


def test_sweep_buy_moves_to_break_even_and_is_stopped_there():
    ctx = _run(ASIAN + PRE + [SWEEP, (1.1003, 1.1030, 1.1002, 1.1028), (1.1028, 1.1029, 1.1005, 1.1006)] + QUIET)
    (tr,) = ctx.trades
    assert tr.side == 1 and tr.t_in == T0 + 29 * 900_000 and tr.entry == pytest.approx(1.1004)
    assert tr.sl0 == pytest.approx(1.0989) and tr.tp0 == pytest.approx(1.1039)
    assert tr.why == "sl" and tr.exit == pytest.approx(1.1005)       # stop moved to entry + 2 pips (1.1006)


def test_decisive_close_below_the_range_closes_the_buy_and_locks_the_side():
    breakdown = (1.1003, 1.1004, 1.0994, 1.0995)                     # closes below low - buffer
    ctx = _run(ASIAN + PRE + [SWEEP, breakdown, SWEEP] + QUIET, stoplossPip=40.0)
    (tr,) = ctx.trades
    assert tr.why == "structure" and tr.t_out == T0 + 30 * 900_000


def test_killzones_follow_daylight_saving():
    p = cbot_params("judas", "EURUSD")
    at = lambda *a: datetime(*a, tzinfo=timezone.utc)                # noqa: E731
    assert in_killzone(at(2025, 7, 1, 7, 30), p) and not in_killzone(at(2025, 7, 1, 6, 30), p)
    assert in_killzone(at(2025, 7, 1, 12, 30), p) and not in_killzone(at(2025, 7, 1, 12, 15), p)
    assert not in_killzone(at(2025, 7, 1, 16, 0), p)
    assert not in_killzone(at(2025, 1, 15, 7, 30), p) and in_killzone(at(2025, 1, 15, 8, 30), p)
    assert not in_killzone(at(2025, 1, 15, 13, 15), p) and in_killzone(at(2025, 1, 15, 13, 30), p)


def test_server_asian_range_bands():
    assert not server_range_ok("XAUUSD", 50) and server_range_ok("XAUUSD", 150)
    assert not server_range_ok("USDJPY", 14) and server_range_ok("EURUSD", 20)
    assert not server_range_ok("US30", 5000)
    src = (ROOT / "app" / "server.py").read_text()
    for pair in ("100.0, 10000.0", "15.0, 200.0", "10000.0, 400000.0", "800.0, 35000.0", "120.0, 800.0",
                 "50.0, 4000.0", "12.0, 100.0"):
        assert f"min_asian_pips, max_asian_pips = {pair}" in src
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_judas.py -q`
Expected: FAIL, `No module named 'research.lab.strategies.judas'`.

- [ ] **Step 3: Implement `research/lab/strategies/judas.py`**

```python
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
from research.sim import _first_hit

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
    """evaluate_judas_sweep_gate's Asian-range band per asset class (app/server.py)."""
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
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_judas.py -q`
Expected: 4 passed.

- [ ] **Step 5: Smoke on real data**

Run: `research/.venv/bin/python -c "
from research.lab.engine import Ctx; from research.lab.feed import load_chunk; from research.lab.strategies.judas import judas
from collections import Counter
for s in ('EURUSD','XAUUSD','US30'):
    ctx = Ctx(load_chunk(s, 'real', 2025), 'JUDAS'); judas(ctx)
    print(s, len(ctx.trades), Counter(t.why for t in ctx.trades), round(sum(t.net for t in ctx.trades), 2))"`
Expected: a few dozen to a few hundred trades per symbol, reasons among sl/tp/structure, no exception.
If a symbol has 0 trades, check its Asian-range band against the preset (e.g. XAU's 200–8000 pips) and report it.

- [ ] **Step 6: Whole research suite green; leave the files in the working tree (no commit)**

---
### Task 13: TMS+ORB port, part 1 — indicators, macro bias, ORB, session, regime, gate, levels

**Files:**
- Create: `research/lab/strategies/tmsorb.py` (the pure pieces; Task 14 appends the position loop and `tms_orb`)
- Test: `research/tests/lab/test_lab_tms_parts.py`

**Interfaces:**
- Consumes: `judas.europe_dst, us_dst`, `cbot.cbot_params, preset`, `research.indicators.atr_sma, ema`.
- Produces (all in `tmsorb`): constants `PERIOD_MIN, BREAKOUT_DISTANCE_LIMITS, MAX_BARS_SINCE_BREAKOUT_MODEL2, CHOPPY_OVERRIDE_*, TMS_CLOSE_MIN_*, US_INDEX_SYMBOLS, GIVEBACK_ARM_ATR, GIVEBACK_ARM_RISK, GIVEBACK_ARM_PEAK_ATR, TIER2_TP_FRACTION, POST_TP_MIN_EXIT_ATR`;
  `resolve_breakout_limits(symbol, atr_pips) -> (direct, absolute)`; `heikin_ashi(o, h, l, c) -> (ho, hh, hl, hc)`; `tdi(hc, rsi_p, red_p) -> (green, red)`; `stoch(hc, hh, hl, k_p, d_p, slow) -> (k, d)`; `chart_tms(bars, p) -> dict[str, ndarray]` with keys `g slope above below turned_green turned_red stoch_bull stoch_bear ang_l ang_s long_entry short_entry exit_long exit_short bounce_bull bounce_bear`; `hysteresis(cand, confirmed, last_flip_ms, closed_ms, sep_ok, p) -> (bias, confirmed, last_flip_ms)`; `MacroTms(h1_bars, p)` with arrays `bias exit_long exit_short bounce_bull bounce_bear` indexed by H1 bar; `adjusted_hour(dt, base, rule) -> int`; `orb_states(bars, p, pip) -> dict(hi, lo, complete, dir, bar)`; `OrbView(complete, direction, dist, decisive, since, in_window)`; `orb_data(orb, i, mid, p, pip) -> OrbView`; `session_info(ms, p) -> (phase, active)`; `session_end_ms(ms, p) -> int`; `market_regime(bars, i, now_ms, or_hi, or_lo, p) -> (regime, flips)`; `PostTp` (`active side extreme`, `.on_close(ctx, pos, p, atr)`, `.release(bias, bid, ask, atr, pip, orb, i, ch, macro, mh, p)`); `cycle_gate(sym, now_ms, phase, active, session_name, bias, gate, od, ch, i, atr_pips, regime, flips) -> int`; `entry_levels(side, bid, ask, atr, or_hi, or_lo, p, pip) -> (sl_pips, tp_pips)`; `close_valid(side, entry, sl, bid, ask, macro_exit) -> bool`.

- [ ] **Step 1: Write the failing tests** (`research/tests/lab/test_lab_tms_parts.py`)

```python
import ast
import math
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import bar_ticks  # noqa: E402
from research.bars import build_bars  # noqa: E402
from research.lab.cbot import cbot_params  # noqa: E402
from research.lab.strategies import tmsorb as tm  # noqa: E402
from research.ticks import Ticks, day_ms  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
NAN = math.nan


def _tdi_loop(hc, P, R):                              # AiAgentBot.UpdateTdi, transcribed
    n = len(hc)
    g, red = [NAN] * n, [NAN] * n
    gs = ls = ag = al = 0.0
    for i in range(1, n):
        d = hc[i] - hc[i - 1]
        gain, loss = max(d, 0.0), max(-d, 0.0)
        if i <= P:
            gs, ls = gs + gain, ls + loss
            if i == P:
                ag, al = gs / P, ls / P
                g[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
        else:
            ag, al = (ag * (P - 1) + gain) / P, (al * (P - 1) + loss) / P
            g[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
        if not math.isnan(g[i]) and i >= P + R - 1:
            red[i] = sum(g[i - R + 1:i + 1]) / R
    return np.array(g), np.array(red)


def _stoch_loop(hc, hh, hl, K, D, S):                 # AiAgentBot.UpdateStoch, transcribed
    n = len(hc)
    raw, k, d = [0.0] * n, [NAN] * n, [NAN] * n
    for i in range(n):
        lo, hi = min(hl[max(0, i - K + 1):i + 1]), max(hh[max(0, i - K + 1):i + 1])
        raw[i] = 100 * (hc[i] - lo) / (hi - lo) if hi > lo else 50.0
        if i >= S - 1:
            k[i] = sum(raw[i - S + 1:i + 1]) / S
        if i >= S + D - 2:
            d[i] = sum(k[i - D + 1:i + 1]) / D
    return np.array(k), np.array(d)


def test_tdi_and_stoch_match_the_cbot_loops():
    rng = np.random.default_rng(0)
    c = 1.1 + np.cumsum(rng.normal(0, 1e-4, 300))
    o = np.r_[c[0], c[:-1]]
    h, l = np.maximum(o, c) + 5e-5, np.minimum(o, c) - 5e-5
    ho, hh, hl, hc = tm.heikin_ashi(o, h, l, c)
    assert ho[1] == pytest.approx((ho[0] + hc[0]) / 2) and hc[5] == pytest.approx((o[5] + h[5] + l[5] + c[5]) / 4)
    g, r = tm.tdi(hc, 6, 6)
    g2, r2 = _tdi_loop(hc, 6, 6)
    np.testing.assert_allclose(g, g2, equal_nan=True)
    np.testing.assert_allclose(r, r2, equal_nan=True)
    k, d = tm.stoch(hc, hh, hl, 6, 6, 4)
    k2, d2 = _stoch_loop(hc, hh, hl, 6, 6, 4)
    np.testing.assert_allclose(k, k2, equal_nan=True)
    np.testing.assert_allclose(d, d2, equal_nan=True)


def test_macro_bias_hysteresis():
    p = {"MinBarsBetweenFlips": 2}
    H = 3_600_000
    assert tm.hysteresis(1, None, None, 0, False, p) == (1, 1, 0)             # first confirmed cross
    assert tm.hysteresis(-1, 1, 0, 1 * H, True, p) == (1, 1, 0)               # lockout: flip ignored
    assert tm.hysteresis(-1, 1, 0, 3 * H, False, p) == (1, 1, 0)              # separation too small
    assert tm.hysteresis(-1, 1, 0, 3 * H, True, p) == (-1, -1, 3 * H)         # flip accepted
    assert tm.hysteresis(0, -1, 5, 10, True, p) == (-1, -1, 5)                # no cross: hold the bias


def test_orb_states_and_view_tokyo():
    p = cbot_params("tms_orb", "USDJPY")               # OR 00:00-00:15 UTC, width >= 8 pips, buffer 1.5
    bars = [(150.00, 150.10, 149.98, 150.05), (150.05, 150.09, 150.03, 150.08),
            (150.08, 150.14, 150.07, 150.13), (150.13, 150.21, 150.12, 150.20)]
    ts, px = bar_ticks(day_ms(date(2025, 6, 2)), 15, bars)
    b = build_bars(Ticks(ts, px, px + 0.01), 15)
    orb = tm.orb_states(b, p, 0.01)
    assert not orb["complete"][0] and orb["complete"][1]
    assert orb["dir"][2] == 1 and orb["bar"][3] == 2 and orb["hi"][3] == pytest.approx(150.10)
    v = tm.orb_data(orb, 3, 150.20, p, 0.01)
    assert v.direction == 1 and v.dist == pytest.approx(10.0) and v.decisive and v.since == 1 and v.in_window
    assert tm.orb_data(orb, 3, 150.05, p, 0.01).direction == 0                # back inside: breakout dead


def _utc(*a):
    return int(datetime(*a, tzinfo=timezone.utc).timestamp() * 1000)


def test_session_phases_and_end():
    tokyo, london = cbot_params("tms_orb", "USDJPY"), cbot_params("tms_orb", "EURUSD")
    assert tm.session_info(_utc(2025, 6, 2, 8, 44), tokyo) == ("active", True)
    assert tm.session_info(_utc(2025, 6, 2, 8, 46), tokyo) == ("ending", True)
    assert tm.session_info(_utc(2025, 6, 2, 9, 0), tokyo) == ("closed", False)
    assert tm.session_info(_utc(2025, 7, 1, 7, 0), london) == ("active", True)      # 08:00 London summer = 07 UTC
    assert tm.session_info(_utc(2025, 7, 1, 6, 59), london) == ("pre", False)
    assert tm.session_end_ms(_utc(2025, 7, 1, 10, 0), london) == _utc(2025, 7, 1, 16, 0)


def test_entry_levels_use_the_or_boundary_and_the_tp_ratio():
    p = cbot_params("tms_orb", "EURUSD")
    sl, tp = tm.entry_levels(1, 1.1008, 1.1010, 10.0, 1.1030, 1.0990, p, 0.0001)
    assert sl == pytest.approx(21.0) and tp == pytest.approx(28.0)             # OR low + 1 pip buffer; 21 x 4/3


def _chart(**kw):
    base = dict(g=55.0, slope=1.0, above=True, below=False, turned_green=False, turned_red=False, stoch_bull=True,
                stoch_bear=False, ang_l=True, ang_s=True, long_entry=False, short_entry=False, exit_long=False,
                exit_short=False, bounce_bull=False, bounce_bear=False)
    base.update(kw)
    return {k: np.array([v]) for k, v in base.items()}


def test_cycle_gate():
    now = _utc(2025, 7, 1, 9, 0)
    ok = tm.OrbView(True, 1, 5.0, True, 1, True)
    gate = tm.PostTp()

    def run(sym="EURUSD", bias=1, od=ok, ch=None, regime="mixed", flips=0, at=now, g=gate):
        return tm.cycle_gate(sym, at, "active", True, "london", bias, g, od, ch or _chart(), 0, 10.0, regime, flips)

    assert run() == 1
    assert run(bias=0) == 0
    assert run(od=tm.OrbView(True, -1, 5.0, True, 1, True)) == 0                          # against the bias
    assert run(od=tm.OrbView(True, 1, 40.0, True, 1, True)) == 0                          # > 3.4 ATR absolute cap
    assert run(od=tm.OrbView(True, 1, 1.0, False, 1, True), ch=_chart(above=False)) == 0  # weak, no bounce
    assert run(regime="choppy", flips=6, od=tm.OrbView(True, 1, 5.0, True, 5, True)) == 0
    assert run(sym="US30", at=_utc(2025, 7, 1, 13, 30)) == 0                              # before 9:45 New York
    armed = tm.PostTp(True, 1, 1.1)
    assert run(g=armed) == 0


def test_close_validation():
    assert tm.close_valid(1, 1.1000, 1.0980, 1.0995, 1.0997, macro_exit=True)
    assert not tm.close_valid(1, 1.1000, 1.0980, 1.0995, 1.0997, macro_exit=False)       # 25 % adverse
    assert tm.close_valid(1, 1.1000, 1.0980, 1.0987, 1.0989, macro_exit=False)           # 65 % adverse
    assert tm.close_valid(1, 1.1000, 1.0980, 1.1021, 1.1023, macro_exit=False)           # >= 1R profit


def test_constants_match_the_sources():
    src = (ROOT / "app" / "server.py").read_text()
    block = src[src.index("BREAKOUT_DISTANCE_LIMITS = (") + len("BREAKOUT_DISTANCE_LIMITS = "):]
    assert ast.literal_eval(block[:block.index("\n)\n") + 2]) == tm.BREAKOUT_DISTANCE_LIMITS
    for line in ("MAX_BARS_SINCE_BREAKOUT_MODEL2 = 20", "CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT = 3",
                 "CHOPPY_OVERRIDE_MAX_OR_FLIPS = 7", "CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR = 0.5",
                 "TMS_CLOSE_MIN_ADVERSE_SL_RATIO = 0.60", "TMS_CLOSE_MIN_PROFIT_SL_RATIO = 1.00"):
        assert line in src, line
    assert 'US_INDEX_SYMBOLS = {"US30", "DJ30", "USTEC", "NAS100", "US500", "SPX500"}' in \
        (ROOT / "app" / "portfolio.py").read_text()
    cs = (ROOT / "cBot" / "AiAgentBot.cs").read_text()
    for line in ("GivebackArmAtrFraction = 0.4", "GivebackArmRiskFraction = 0.5", "GivebackArmPeakAtr = 1.5",
                 "Tier2TpFraction = 0.65", "PostTpGateMinExitAtr = 0.5"):
        assert line in cs, line
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_tms_parts.py -q`
Expected: FAIL, `No module named 'research.lab.strategies.tmsorb'`.

- [ ] **Step 3: Implement `research/lab/strategies/tmsorb.py`** (part 1)

```python
"""AiAgentBot (TMS+ORB) in the lab, with the AI replaced by "approve every candidate the server's cycle gate
lets through" and the AI's position management by its prompt rules and the server's close validation.

Sources: cBot/AiAgentBot.cs (Heikin-Ashi TDI and Stochastic, the H1 macro bias with its cross lock and flip
hysteresis, ORB, session, ExecuteDecision's SL/TP, ManageExits, CheckMaxGiveback, CheckSessionEnd, the post-TP
gate, BiasFlipExit) and app/server.py (evaluate_cycle_gate, validate_tms_close_decision, the prompt's rules 1-2:
close on session "ending" or on the chart exit signal). An approved candidate trades in the macro bias
direction. Switched off to honour the lab's account rules: the loss-streak gate, MaxDollarRiskPerTrade and the
min-lot guards (fixed units). Not modelled: the US-index alignment gate (it needs other bots' positions),
AI ADJUST, the LLM's own judgement. The exits use the last closed bar's ATR (the bot reads the forming bar's)."""
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from research.indicators import atr_sma, ema
from research.lab import costs
from research.lab.cbot import cbot_params, preset
from research.lab.engine import NAN, Ctx, Pos
from research.lab.strategies.judas import europe_dst, us_dst
from research.sim import _first_hit
from research.specs import normalize_units

NY = ZoneInfo("America/New_York")
PERIOD_MIN = {"m5": 5, "m15": 15}
# cBot/AiAgentBot.cs private constants
GIVEBACK_ARM_ATR, GIVEBACK_ARM_RISK, GIVEBACK_ARM_PEAK_ATR = 0.4, 0.5, 1.5
TIER2_TP_FRACTION, POST_TP_MIN_EXIT_ATR = 0.65, 0.5
# app/server.py (pinned to the source by the tests)
BREAKOUT_DISTANCE_LIMITS = (
    # (symbol tokens, prompt label, direct ATR x, direct cap, absolute ATR x, absolute cap)
    (("USTEC", "NAS100"), "USTEC/NAS100", 1.3, 700.0, 3.2, 2100.0),
    (("US30", "DJ30"), "US30/DJ30", 1.5, 950.0, 3.4, 2800.0),
    (("US500", "SPX500"), "US500/SPX500", 1.4, 150.0, 3.4, 450.0),
    (("DE40", "GER40"), "DE40/GER40", 1.5, 700.0, 3.4, 1900.0),
    (("UK100", "GB100"), "UK100/GB100", 1.5, 550.0, 3.4, 1600.0),
    (("JP225", "NIKKEI", "JPN225"), "JP225/Nikkei", 1.8, 3000.0, 3.8, 7000.0),
    (("HK50", "HSI"), "HK50/HangSeng", 1.5, 800.0, 3.4, 2200.0),
    (("XAU", "GOLD"), "Gold", 1.8, 1500.0, 3.6, 3500.0),
    (("BTC", "CRYPTO"), "BTC/Crypto", 1.5, 37500.0, 3.5, 130000.0),
    (("ETH", "SOL", "XRP"), "ETH/SOL/XRP", 1.5, 5250.0, 3.5, 35000.0),
    (("JPY",), "JPY Crosses", 1.6, 55.0, 3.6, 120.0),
    (("EURUSD", "GBPUSD", "USDCAD", "AUDUSD", "NZDUSD", "USDCHF"), "Forex Majors", 1.5, 30.0, 3.4, 70.0),
)
MAX_BARS_SINCE_BREAKOUT_MODEL2 = 20
CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT, CHOPPY_OVERRIDE_MAX_OR_FLIPS, CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR = 3, 7, 0.5
TMS_CLOSE_MIN_ADVERSE_SL_RATIO, TMS_CLOSE_MIN_PROFIT_SL_RATIO = 0.60, 1.00
US_INDEX_SYMBOLS = ("US30", "DJ30", "USTEC", "NAS100", "US500", "SPX500")      # app/portfolio.py


def resolve_breakout_limits(symbol: str, atr_pips: Optional[float]) -> Tuple[float, float]:
    sym = symbol.upper()
    row = next((r for r in BREAKOUT_DISTANCE_LIMITS if any(tok in sym for tok in r[0])), BREAKOUT_DISTANCE_LIMITS[-1])
    _, _, direct_atr, direct_cap, abs_atr, abs_cap = row
    if atr_pips and atr_pips > 0:
        return min(atr_pips * direct_atr, direct_cap), min(atr_pips * abs_atr, abs_cap)
    return direct_cap, abs_cap


# ---------------------------------------------------------------- indicators
def heikin_ashi(o, h, l, c):
    hc = (o + h + l + c) / 4.0
    ho = np.empty(len(o))
    ho[0] = (o[0] + c[0]) / 2.0
    for i in range(1, len(o)):
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2.0
    return ho, np.maximum(h, np.maximum(ho, hc)), np.minimum(l, np.minimum(ho, hc)), hc


def _rsi(ag: float, al: float) -> float:
    return 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)


def tdi(hc, rsi_p: int, red_p: int):
    """UpdateTdi: RSI of the HA close (SMA seed, then Wilder), red = SMA(red_p) of it; NaN during warm-up."""
    n = len(hc)
    g = np.full(n, np.nan)
    d = np.diff(hc, prepend=hc[0])
    gain, loss = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    if n > rsi_p:
        ag, al = gain[1:rsi_p + 1].mean(), loss[1:rsi_p + 1].mean()
        g[rsi_p] = _rsi(ag, al)
        for i in range(rsi_p + 1, n):
            ag = (ag * (rsi_p - 1) + gain[i]) / rsi_p
            al = (al * (rsi_p - 1) + loss[i]) / rsi_p
            g[i] = _rsi(ag, al)
    red = np.full(n, np.nan)
    w = rsi_p + red_p - 1
    if n > w:
        red[w:] = sliding_window_view(g, red_p).mean(axis=1)[w - red_p + 1:]
    return g, red


def stoch(hc, hh, hl, k_p: int, d_p: int, slow: int):
    """UpdateStoch on Heikin-Ashi prices: raw %K over k_p bars (a partial window at the start), %K = SMA(slow),
    %D = SMA(d_p) of %K; NaN during warm-up."""
    n = len(hc)
    lo = sliding_window_view(np.r_[np.full(k_p - 1, np.inf), hl], k_p).min(axis=1)
    hi = sliding_window_view(np.r_[np.full(k_p - 1, -np.inf), hh], k_p).max(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = np.where(hi > lo, 100.0 * (hc - lo) / (hi - lo), 50.0)
    k = np.full(n, np.nan)
    if n >= slow:
        k[slow - 1:] = sliding_window_view(raw, slow).mean(axis=1)
    d = np.full(n, np.nan)
    w = slow + d_p - 2
    if n > w:
        d[w:] = sliding_window_view(k[slow - 1:], d_p).mean(axis=1)
    return k, d


def chart_tms(b, p) -> dict:
    """GetTmsSignals on every chart bar (the cross memory runs forward over all bars)."""
    ho, hh, hl, hc = heikin_ashi(b.o, b.h, b.l, b.c)
    g, r = tdi(hc, p["RsiPeriod"], p["RedPeriod"])
    k, d = stoch(hc, hh, hl, p["StochKPeriod"], p["StochDPeriod"], p["StochSlowing"])
    e = ema(b.c, p["EmaPeriod"])
    n = len(b)
    idx = np.arange(n)
    g1, g2, r1 = np.r_[np.nan, g[:-1]], np.r_[np.nan, np.nan, g[:-2]], np.r_[np.nan, r[:-1]]
    green = hc > ho
    green1, green2 = np.r_[False, green[:-1]], np.r_[False, False, green[:-2]]
    valid = np.isfinite(g) & np.isfinite(r) & (idx >= 1)
    with np.errstate(invalid="ignore"):
        above, below = valid & (b.c > e) & (hc > e), valid & (b.c < e) & (hc < e)
        tg = valid & ((green & ~green1) | (green1 & ~green2))
        trd = valid & ((~green & green1) | (~green1 & green2))
        up, dn = valid & (g1 <= r1) & (g > r), valid & (g1 >= r1) & (g < r)
        last = np.maximum.accumulate(np.where(up | dn, idx, -1))
        last_dir = np.where(last >= 0, np.where(up, 1, -1)[np.maximum(last, 0)], 0)
        since = np.where(last >= 0, idx - last, 999)
        mad = p["MinAngleDelta"]
        ang_l = valid & ((g - g2) >= mad if mad > 0 else True)
        ang_s = valid & ((g2 - g) >= mad if mad > 0 else True)
        window = (since >= 1) & (since <= p["MaxBarsAfterCross"])
        sb, sr = valid & (k > d), valid & (k < d)
        x_dn = ((g1 >= r1) & (g < r)) | ((g < r) & (r - g >= 0.5))
        ob = ((g1 >= 68) | (g2 >= 68)) & (g < 60) & (g1 - g >= 3.0) & (~above | trd)
        x_up = ((g1 <= r1) & (g > r)) | ((g > r) & (g - r >= 0.5))
        os_ = ((g1 <= 32) | (g2 <= 32)) & (g > 40) & (g - g1 >= 3.0) & (~below | tg)
        dist, dist1 = np.abs(g - r), np.abs(g1 - r1)
        thr, on = p["BounceDistanceThreshold"], bool(p["BounceTradeEnabled"])
        near = (dist1 <= thr) & (dist > dist1)
        return dict(
            g=np.where(valid, g, 50.0), slope=np.where(valid, g - g1, 0.0), above=above, below=below,
            turned_green=tg, turned_red=trd, stoch_bull=sb, stoch_bear=sr, ang_l=ang_l, ang_s=ang_s,
            long_entry=valid & (last_dir == 1) & window & tg & sb & ang_l & above,
            short_entry=valid & (last_dir == -1) & window & trd & sr & ang_s & below,
            exit_long=valid & (x_dn | ob | ((g < r) & ~above & (trd | ~green))),
            exit_short=valid & (x_up | os_ | ((g > r) & ~below & (tg | green))),
            bounce_bull=valid & on & (g > r) & (g > g1) & near & above & ~trd,
            bounce_bear=valid & on & (g < r) & (g < g1) & near & below & ~tg)


# ---------------------------------------------------------------- macro (H1) bias
def hysteresis(cand, confirmed, last_flip_ms, closed_ms, sep_ok, p):
    """The macro bias flip rule: (bias, confirmed, last_flip_ms). cand 0 = no confirmed cross yet."""
    lock_ok = last_flip_ms is None or (closed_ms - last_flip_ms) / 3_600_000 >= p["MinBarsBetweenFlips"]
    if cand == 0:
        return (confirmed or 0), confirmed, last_flip_ms
    if cand == confirmed:
        return cand, confirmed, last_flip_ms
    if confirmed is None or (sep_ok and lock_ok):
        return cand, cand, closed_ms
    return confirmed, confirmed, last_flip_ms


def _window_rsi(hc, P):
    out = np.full(len(hc), 50.0)
    d = np.diff(hc, prepend=hc[0])
    gain, loss = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    if len(hc) > P:
        ag, al = gain[1:P + 1].sum() / P, loss[1:P + 1].sum() / P
        out[P] = _rsi(ag, al)
        for k in range(P + 1, len(hc)):
            ag, al = (ag * (P - 1) + gain[k]) / P, (al * (P - 1) + loss[k]) / P
            out[k] = _rsi(ag, al)
    return out


def _window_red(rsi, R):
    out = rsi.copy()
    if len(rsi) > R:
        out[R:] = sliding_window_view(rsi, R).mean(axis=1)[1:]
    return out


class MacroTms:
    """GetMacroTmsSignals evaluated at every closed H1 bar h over its 120-bar window (recomputed from the
    window start, as the bot does), with the cross lock and the flip hysteresis carried forward."""

    def __init__(self, hb, p):
        n = len(hb)
        self.bias = np.zeros(n, np.int8)
        self.exit_long, self.exit_short = np.zeros(n, bool), np.zeros(n, bool)
        self.bounce_bull, self.bounce_bear = np.zeros(n, bool), np.zeros(n, bool)
        rp, rd = p["RsiPeriod"], p["RedPeriod"]
        thr, on = p["BounceDistanceThreshold"], bool(p["BounceTradeEnabled"])
        cross, confirmed, last_flip = 0, None, None
        for h in range(n):
            count = h + 2                                    # the forming bar is the window's last element
            if count < rp + rd + 35:
                continue
            s = count - min(count, 120)
            w = slice(s, h + 1)
            ho, hh, hl, hc = heikin_ashi(hb.o[w], hb.h[w], hb.l[w], hb.c[w])
            rsi = _window_rsi(hc, rp)
            red = _window_red(rsi, rd)
            k, d = (np.nan_to_num(x, nan=50.0) for x in stoch(hc, hh, hl, p["StochKPeriod"], p["StochDPeriod"],
                                                             p["StochSlowing"]))
            last = len(hc) - 1
            prev = last - 1
            if prev < 1:
                continue
            g, g1, r, r1 = rsi[last], rsi[prev], red[last], red[prev]
            green, green1 = hc[last] > ho[last], hc[prev] > ho[prev]
            tg, trd = green and not green1, (not green) and green1
            for j in range(last, 0, -1):
                if rsi[j - 1] <= red[j - 1] and rsi[j] > red[j] and hc[j] > ho[j] and k[j] > d[j]:
                    cross = 1
                    break
                if rsi[j - 1] >= red[j - 1] and rsi[j] < red[j] and hc[j] < ho[j] and k[j] < d[j]:
                    cross = -1
                    break
            bias, confirmed, last_flip = hysteresis(cross, confirmed, last_flip, int(hb.open_time[h]),
                                                    abs(g - r) >= p["MinTdiFlipSeparation"], p)
            self.bias[h] = bias
            self.exit_long[h] = (g1 >= r1 and g < r) or (bias == -1 and trd)
            self.exit_short[h] = (g1 <= r1 and g > r) or (bias == 1 and tg)
            near = abs(g1 - r1) <= thr and abs(g - r) > abs(g1 - r1)
            self.bounce_bull[h] = on and g > r and g > g1 and near and not trd
            self.bounce_bear[h] = on and g < r and g < g1 and near and not tg


# ---------------------------------------------------------------- ORB, session, regime
def adjusted_hour(dt: datetime, base: int, rule: str) -> int:
    """GetAdjustedHour: winter UTC hours move one hour earlier in summer."""
    if rule == "None" or base == 0:
        return base
    dst = us_dst(dt) if rule == "US" else (europe_dst(dt) if rule == "Europe" else False)
    return base - 1 if dst else base


def orb_states(b, p, pip: float) -> dict:
    """UpdateOrb after each chart bar: range of the first OrbOpeningRangeMinutes from the session open, complete
    once the window has passed with a wide enough range, breakout direction and bar (reset every UTC day)."""
    n = len(b)
    out = dict(hi=np.full(n, -np.inf), lo=np.full(n, np.inf), complete=np.zeros(n, bool),
               dir=np.zeros(n, np.int8), bar=np.full(n, -1))
    day, hi, lo, done, direction, k = None, -np.inf, np.inf, False, 0, -1
    buf = p["OrbBufferPips"] * pip
    for i in range(n):
        dt = datetime.fromtimestamp(b.open_time[i] / 1000, timezone.utc)
        if dt.date() != day:
            day, hi, lo, done, direction, k = dt.date(), -np.inf, np.inf, False, 0, -1
        start = adjusted_hour(dt, p["OrbStartHour"], p["SessionDstRule"]) * 60 + p["OrbStartMinute"]
        end = start + p["OrbOpeningRangeMinutes"]
        mins = dt.hour * 60 + dt.minute
        if start <= mins < end:
            hi, lo = max(hi, float(b.h[i])), min(lo, float(b.l[i]))
        if mins >= end and not done and hi > -np.inf and (hi - lo) / pip >= p["MinOrWidthPips"]:
            done = True
        if done:
            if b.c[i] > hi + buf and direction != 1:
                direction, k = 1, i
            elif b.c[i] < lo - buf and direction != -1:
                direction, k = -1, i
        out["hi"][i], out["lo"][i], out["complete"][i], out["dir"][i], out["bar"][i] = hi, lo, done, direction, k
    return out


@dataclass
class OrbView:
    complete: bool
    direction: int
    dist: float
    decisive: bool
    since: int
    in_window: bool


def orb_data(orb: dict, i: int, mid: float, p, pip: float) -> OrbView:
    """GetOrbData at the close of bar i with the current mid: a breakout whose price is back inside is dead."""
    hi, lo, d, k = float(orb["hi"][i]), float(orb["lo"][i]), int(orb["dir"][i]), int(orb["bar"][i])
    since = i - k if k >= 0 else 0
    dist = (mid - hi) / pip if d == 1 and hi > -np.inf else ((lo - mid) / pip if d == -1 and lo < np.inf else 0.0)
    direction = d if dist > 0 else 0
    dist = max(dist, 0.0)
    return OrbView(bool(orb["complete"][i]), direction, dist, dist >= p["MinDecisiveBreakoutPips"], since,
                   0 <= since <= p["MaxBarsAfterBreakout"])


def _session_minutes(dt: datetime, p) -> Tuple[int, int]:
    start = adjusted_hour(dt, p["OrbStartHour"], p["SessionDstRule"]) * 60 + p["OrbStartMinute"]
    end = adjusted_hour(dt, p["SessionEndHour"], p["SessionDstRule"]) * 60 + p["SessionEndMinute"]
    return start, (start + 540 if p["SessionEndHour"] == 0 else end)


def session_info(ms: int, p) -> Tuple[str, bool]:
    """GetSessionInfo: (phase, is_trading_time); "ending" = the last 15 minutes."""
    dt = datetime.fromtimestamp(ms / 1000, timezone.utc)
    now = dt.hour * 60 + dt.minute
    start, end = _session_minutes(dt, p)
    over = start > end
    active = (now >= start or now < end) if over else (start <= now < end)
    to_end = ((1440 - now + end) if (over and now >= start) else end - now) if active else 0
    ending = active and to_end <= 15
    if not active and ((end <= now < start) if over else now < start):
        return "pre", False
    if active and not ending:
        return "active", True
    return ("ending", True) if ending else ("closed", False)


def session_end_ms(ms: int, p) -> int:
    """When CheckSessionEnd flattens a position opened at ms (sessions within one UTC day)."""
    dt = datetime.fromtimestamp(ms / 1000, timezone.utc)
    start, end = _session_minutes(dt, p)
    if start > end:
        raise ValueError("overnight sessions are not modelled")
    return int(datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc).timestamp() * 1000) + end * 60_000


def _er(x) -> float:
    path = float(np.abs(np.diff(x)).sum())
    return abs(float(x[-1] - x[0])) / path if path > 1e-7 else 0.0


def market_regime(b, i: int, now_ms: int, or_hi: float, or_lo: float, p) -> Tuple[str, int]:
    """GetMarketRegime: efficiency ratios of the session's closes and the count of failed ORB breakouts."""
    dt = datetime.fromtimestamp(now_ms / 1000, timezone.utc)
    sh = adjusted_hour(dt, p["OrbStartHour"], p["SessionDstRule"])
    start = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc) + timedelta(hours=sh, minutes=p["OrbStartMinute"])
    if dt < start and sh > 12:
        start -= timedelta(days=1)
    closes = b.c[int(np.searchsorted(b.open_time, int(start.timestamp() * 1000), side="left")):i + 1]
    if len(closes) < 6:
        return "forming", 0
    er_s, er_r = _er(closes), _er(closes[-12:])
    flips = 0
    if or_hi > -np.inf and or_lo < np.inf:
        zone = None
        for c in closes:
            z = "A" if c > or_hi else ("B" if c < or_lo else "I")
            flips += zone in ("A", "B") and z == "I"
            zone = z if z != "I" else zone
    if er_s >= 0.35 or (er_r >= 0.45 and flips <= 3):
        return "trending", flips
    return ("choppy" if flips >= 5 else "mixed"), flips


# ---------------------------------------------------------------- post-TP gate, cycle gate, levels
@dataclass
class PostTp:
    active: bool = False
    side: int = 0
    extreme: float = 0.0

    def on_close(self, ctx: Ctx, pos: Pos, p, atr: float) -> None:
        """OnPositionClosed: arm after a profitable exit that captured >= 0.5 ATR."""
        if not p["EnablePostTpGate"]:
            return
        j, px, _, _ = pos.deals[-1]
        exit_pips = (px - pos.entry) * pos.side / ctx.inst.pip
        fee_pips = ctx.inst.comm_per_unit / (ctx.inst.pip * costs.usd_per_quote(ctx.inst.quote_ccy, int(ctx.t.ts[j])))
        if exit_pips > fee_pips and exit_pips >= POST_TP_MIN_EXIT_ATR * atr:
            self.active, self.side = True, pos.side
            self.extreme = float(ctx.t.bid[j] if pos.side > 0 else ctx.t.ask[j])

    def release(self, bias, bid, ask, atr, pip, orb, i, ch, macro, mh, p) -> None:
        """CheckPostTpGateRelease: bias flip, a pullback, an OR touch, or a TDI bounce after a small pullback."""
        if not self.active:
            return
        if self.side == 1 and bid > self.extreme:
            self.extreme = bid
        if self.side == -1 and ask < self.extreme:
            self.extreme = ask
        pull = (self.extreme - bid) / pip if self.side == 1 else (ask - self.extreme) / pip
        m_bull = mh >= 0 and bool(macro.bounce_bull[mh])
        m_bear = mh >= 0 and bool(macro.bounce_bear[mh])
        released = (bias == -self.side or pull >= p["PostTpPullbackAtr"] * atr
                    or (bool(orb["complete"][i]) and ((self.side == 1 and bid <= orb["hi"][i])
                                                      or (self.side == -1 and ask >= orb["lo"][i])))
                    or (pull >= 0.3 * atr and ((self.side == 1 and (bool(ch["bounce_bull"][i]) or m_bull))
                                               or (self.side == -1 and (bool(ch["bounce_bear"][i]) or m_bear)))))
        if released:
            self.active, self.side = False, 0


def cycle_gate(sym, now_ms, phase, active, session_name, bias, gate, od, ch, i, atr_pips, regime, flips) -> int:
    """evaluate_cycle_gate for a flat bot: the side the approve-all AI takes (the macro bias), or 0."""
    if not active or phase in ("pre", "closed"):
        return 0
    s = sym.upper()
    us_idx = any(tok in s for tok in US_INDEX_SYMBOLS)
    gold = "XAU" in s or "GOLD" in s
    name = session_name.lower()
    if "newyork" in name or "ny" in name or us_idx or gold:
        ny = datetime.fromtimestamp(now_ms / 1000, NY)
        m = ny.hour * 60 + ny.minute
        if (us_idx and m < 585) or 550 <= m <= 575:
            return 0
    if bias == 0:
        return 0
    if gate.active and (gate.side == bias or gate.side == 0):
        return 0
    if not od.complete or od.direction == 0:
        return 0
    if bias == 1:
        bounce = (ch["bounce_bull"][i] and ch["above"][i]) or (
            ch["above"][i] and ch["slope"][i] > 0 and ch["g"][i] >= 48.0 and not ch["turned_red"][i]
            and (ch["long_entry"][i] or ch["stoch_bull"][i] or ch["ang_l"][i]))
    else:
        bounce = (ch["bounce_bear"][i] and ch["below"][i]) or (
            ch["below"][i] and ch["slope"][i] < 0 and ch["g"][i] <= 52.0 and not ch["turned_green"][i]
            and (ch["short_entry"][i] or ch["stoch_bear"][i] or ch["ang_s"][i]))
    bounce = bool(bounce)
    atr_ref = round(atr_pips, 1) if atr_pips > 0 else None
    direct, absolute = resolve_breakout_limits(s, atr_ref)
    if od.dist > absolute or (od.dist > direct and not bounce):
        return 0
    if gold and od.dist < 150.0 and not bounce:
        return 0
    if not od.decisive and not bounce:
        return 0
    if not od.in_window and (od.since > MAX_BARS_SINCE_BREAKOUT_MODEL2 or not bounce):
        return 0
    if od.direction != bias:
        return 0
    if regime == "choppy" and flips >= 5:
        fresh = False
        if (od.since <= CHOPPY_OVERRIDE_MAX_BARS_SINCE_BREAKOUT and flips <= CHOPPY_OVERRIDE_MAX_OR_FLIPS
                and (atr_ref is None or od.dist >= CHOPPY_OVERRIDE_MIN_BREAKOUT_ATR * atr_ref)):
            if od.direction == 1:
                fresh = bool(ch["above"][i] and ch["slope"][i] > 0 and not ch["turned_red"][i])
            else:
                fresh = bool(ch["below"][i] and ch["slope"][i] < 0 and not ch["turned_green"][i])
        if not fresh:
            return 0
    return bias


def entry_levels(side, bid, ask, atr, or_hi, or_lo, p, pip) -> Tuple[float, float]:
    """ExecuteDecision's SL/TP in pips (UseAtr), without the dollar-risk guard that shrinks the stop."""
    price = ask if side > 0 else bid
    sl, tp = atr * p["AtrSlMultiplier"], atr * p["AtrTpMultiplier"]
    max_sl = p["MaxSlAtr"] * atr
    sl = max(p["MinSlAtr"] * atr, min(max_sl, sl))
    if p["UseOrBoundarySl"]:
        or_sl = None
        if side > 0 and or_lo < np.inf:
            or_sl = (price - or_lo) / pip + p["OrbBufferPips"]
        elif side < 0 and or_hi > -np.inf:
            or_sl = (or_hi - price) / pip + p["OrbBufferPips"]
        if or_sl is not None and or_sl > 0:
            sl = max(sl, min(max_sl, or_sl))
    sl = min(sl, max_sl)
    if p["MaxAbsoluteSlPips"] > 0:
        sl = min(sl, p["MaxAbsoluteSlPips"])
    ratio = p["AtrTpMultiplier"] / p["AtrSlMultiplier"] if p["AtrTpMultiplier"] > 0 and p["AtrSlMultiplier"] > 0 else 1.5
    return sl, max(p["MinTpAtr"] * atr, max(tp, sl * ratio))


def close_valid(side, entry, sl, bid, ask, macro_exit) -> bool:
    """validate_tms_close_decision: an AI CLOSE_ALL stands on a macro exit signal, >= 60 % of the stop distance
    in drawdown, or >= 1R of profit."""
    if macro_exit:
        return True
    sl_dist = abs(entry - sl)
    if sl_dist <= 0:
        return True
    adverse = (entry - bid) if side > 0 else (ask - entry)
    profit = (bid - entry) if side > 0 else (entry - ask)
    return adverse >= TMS_CLOSE_MIN_ADVERSE_SL_RATIO * sl_dist or profit >= TMS_CLOSE_MIN_PROFIT_SL_RATIO * sl_dist
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_tms_parts.py -q`
Expected: 8 passed.

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 14: TMS+ORB port, part 2 — position management and the bar loop

**Files:**
- Modify: `research/lab/strategies/tmsorb.py` (append)
- Test: `research/tests/lab/test_lab_tms.py`

**Interfaces:**
- Consumes: Task 13's pieces, `engine.Ctx.open/close/finish/tick_at/can_enter`, `research.specs.normalize_units`, `Instrument.spec()`.
- Produces: `tmsorb.Hold(pos, cur, atr, eod_ms, init_risk, mfe=-inf, be_done=False)`, `tmsorb.tier2(profit, atr, total_tp, p)`, `tmsorb.giveback_arm(atr, init_risk, p)`, `tmsorb.run_ticks(ctx, hd, end, p) -> Optional[str]` (exit reason once closed), `tmsorb.tms_orb(ctx, **overrides)`. Exit reasons: `sl tp partial giveback giveback_atr eod ai_close bias_flip tail`.

- [ ] **Step 1: Write the failing tests** (`research/tests/lab/test_lab_tms.py`)

```python
from collections import Counter
from datetime import date, datetime, timezone

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk, needs_ticks  # noqa: E402
from research.lab.cbot import cbot_params  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk  # noqa: E402
from research.lab.strategies import tmsorb as tm  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.ticks import day_ms, load_ticks  # noqa: E402

T0 = day_ms(date(2025, 7, 1)) + 9 * 3_600_000


def _hold(bid, sl, tp=1.1100, eod_ms=None, atr=10.0):
    ts = T0 + np.arange(len(bid)) * 1000
    ctx = Ctx(make_chunk(ts, bid, spread=0.0002), "TMSORB")
    pos = ctx.open(0, 1)                                         # ask 1.1000 when bid[0] = 1.0998
    pos.sl = pos.sl0 = sl
    pos.tp = pos.tp0 = tp
    hd = tm.Hold(pos, 1, atr, eod_ms or int(ts[-1]) + 10**9, (pos.entry - sl) / 0.0001)
    return ctx, hd


def test_break_even_moves_the_stop_and_closes_half():
    ctx, hd = _hold([1.0998, 1.1005, 1.1013, 1.1008, 1.1000], sl=1.0980)
    p = cbot_params("tms_orb", "EURUSD")                         # BE at 1.2 ATR = 12 pips, offset 1 pip
    assert tm.run_ticks(ctx, hd, 5, p) == "sl"
    assert [(j, round(px, 4), u, why) for j, px, u, why in hd.pos.deals] == [(2, 1.1013, 5000.0, "partial"),
                                                                            (4, 1.1000, 5000.0, "sl")]
    assert ctx.trades[0].units == 10_000


def test_giveback_lock_closes_after_45_percent_of_the_peak():
    ctx, hd = _hold([1.0998, 1.1012, 1.1030, 1.1020, 1.1015, 1.1010], sl=1.0970)
    p = cbot_params("tms_orb", "EURUSD", TrailTriggerAtr=0.0, Tier2TriggerAtr=0.0, MaxGivebackAtr=0.0)
    assert tm.run_ticks(ctx, hd, 6, p) == "giveback"
    assert hd.pos.deals[-1][0] == 4                              # pnl 15 after a 30-pip peak: 15 >= 13.5


def test_session_end_flattens():
    ctx, hd = _hold([1.0998, 1.1001, 1.1002, 1.1001, 1.1002], sl=1.0980, eod_ms=T0 + 3000)
    assert tm.run_ticks(ctx, hd, 5, cbot_params("tms_orb", "EURUSD")) == "eod"
    assert hd.pos.deals[-1][0] == 3


def test_run_ticks_stops_at_end_without_closing():
    ctx, hd = _hold([1.0998, 1.1001, 1.1002, 1.1001, 1.1002], sl=1.0980)
    assert tm.run_ticks(ctx, hd, 3, cbot_params("tms_orb", "EURUSD")) is None
    assert hd.cur == 3 and not ctx.trades


@needs_ticks
def test_tms_orb_smoke_on_usdjpy_june_2025():
    t = load_ticks("USDJPY", date(2025, 5, 12), date(2025, 6, 30))
    ch = Chunk("USDJPY", "real", 2025, t, day_ms(date(2025, 6, 2)), day_ms(date(2025, 6, 28)), instrument("USDJPY"))
    ctx = Ctx(ch, "TMSORB")
    tm.tms_orb(ctx)
    allowed = {"sl", "tp", "giveback", "giveback_atr", "eod", "ai_close", "bias_flip", "tail"}
    print(len(ctx.trades), Counter(tr.why for tr in ctx.trades))
    for tr in ctx.trades:
        hour = datetime.fromtimestamp(tr.t_in / 1000, timezone.utc).hour
        assert 0 <= hour < 9 and tr.why in allowed and np.isfinite(tr.sl0)
        assert tr.t_out <= day_ms(date(2025, 6, 30)) + 86_400_000
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_tms.py -q`
Expected: FAIL, `module ... has no attribute 'Hold'`.

- [ ] **Step 3: Implement** — append to `research/lab/strategies/tmsorb.py`:

```python
# ---------------------------------------------------------------- the open position, tick by tick
@dataclass
class Hold:
    pos: Pos
    cur: int              # next tick to process
    atr: float            # ATR (pips) of the last closed chart bar
    eod_ms: int
    init_risk: float      # pips
    mfe: float = -np.inf
    be_done: bool = False


def tier2(profit, atr, total_tp, p) -> bool:
    """IsTier2Reached."""
    return ((p["Tier2TriggerAtr"] > 0 and profit >= p["Tier2TriggerAtr"] * atr)
            or (p["Tier2TriggerPips"] > 0 and profit >= p["Tier2TriggerPips"])
            or (total_tp > 0 and profit >= TIER2_TP_FRACTION * total_tp))


def giveback_arm(atr, init_risk, p) -> float:
    """CheckMaxGiveback's activation threshold (pips of peak profit)."""
    x = GIVEBACK_ARM_ATR * atr
    if p["BreakevenTriggerAtr"] > 0:
        x = max(x, p["BreakevenTriggerAtr"] * atr)
    if init_risk > 0:
        x = max(x, init_risk * GIVEBACK_ARM_RISK)
    return max(x, p["GivebackArmMinPips"], GIVEBACK_ARM_PEAK_ATR * atr)


def _close_all(ctx: Ctx, hd: Hold, j: int, why: str) -> str:
    ctx.close(hd.pos, j, why)
    ctx.finish(hd.pos)
    return why


def _tick(ctx: Ctx, hd: Hold, j: int, p, spec, digits: int) -> Optional[str]:
    """One tick: the broker's SL/TP, then OnTick (memory, ManageExits, CheckMaxGiveback, CheckSessionEnd)."""
    t, pos, pip, a = ctx.t, hd.pos, ctx.inst.pip, hd.atr
    side = pos.side
    px = float(t.bid[j] if side > 0 else t.ask[j])
    if (px - pos.sl) * side <= 0:
        return _close_all(ctx, hd, j, "sl")
    if math.isfinite(pos.tp) and (px - pos.tp) * side >= 0:
        return _close_all(ctx, hd, j, "tp")
    pnl = (px - pos.entry) * side / pip
    hd.mfe = max(hd.mfe, pnl)
    total_tp = abs(pos.tp - pos.entry) / pip if math.isfinite(pos.tp) else 0.0
    if p["BreakevenTriggerAtr"] > 0 and pnl >= p["BreakevenTriggerAtr"] * a and not hd.be_done:
        be_sl = pos.entry + side * p["BreakevenOffsetAtr"] * a * pip
        if (be_sl - pos.sl) * side > 0 and (be_sl - px) * side < 0:
            pos.sl, hd.be_done = be_sl, True
            ratio = p["PartialCloseRatio"]
            if 0 < ratio < 1:
                vol = normalize_units(pos.units * ratio, spec)
                if vol >= spec.min_units and pos.units - vol >= spec.min_units:
                    ctx.close(pos, j, "partial", vol)
    if p["TrailTriggerAtr"] > 0 and pnl >= p["TrailTriggerAtr"] * a:
        dist = (min(p["TrailDistanceAtr"], p["Tier2TrailDistanceAtr"]) if tier2(pnl, a, total_tp, p)
                else p["TrailDistanceAtr"]) * a
        cand = round(px - side * dist * pip, digits)
        if (cand - pos.sl) * side >= max(ctx.inst.tick_size, 0.1 * dist * pip) and (cand - px) * side < 0:
            pos.sl = cand
    if hd.mfe >= giveback_arm(a, hd.init_risk, p):
        gb = hd.mfe - pnl
        ratio = max(p["MaxGivebackMfeRatio"], 0.45) if p["MaxGivebackMfeRatio"] > 0 else 0.0
        if tier2(hd.mfe, a, total_tp, p):
            ratio = p["Tier2GivebackMfeRatio"]
        if ratio > 0 and gb >= hd.mfe * ratio:
            return _close_all(ctx, hd, j, "giveback")
        if p["MaxGivebackAtr"] > 0 and gb >= p["MaxGivebackAtr"] * a:
            return _close_all(ctx, hd, j, "giveback_atr")
    if t.ts[j] >= hd.eod_ms:
        return _close_all(ctx, hd, j, "eod")
    return None


def run_ticks(ctx: Ctx, hd: Hold, end: int, p) -> Optional[str]:
    """Ticks [hd.cur, end) of the open position; the exit reason once it is closed. Until break-even, trailing
    or the giveback lock can arm, only the SL, the TP, the arming level and the session end can act, so the
    loop jumps there with a vectorised search."""
    t, pos, pip = ctx.t, hd.pos, ctx.inst.pip
    side, spec = pos.side, ctx.inst.spec()
    digits = max(0, round(-math.log10(ctx.inst.tick_size)))
    price = t.bid if side > 0 else t.ask
    eod_tick = ctx.tick_at(hd.eod_ms)
    end = min(end, len(t))
    while hd.cur < end:
        a = hd.atr
        be = p["BreakevenTriggerAtr"] * a if p["BreakevenTriggerAtr"] > 0 else np.inf
        tr_ = p["TrailTriggerAtr"] * a if p["TrailTriggerAtr"] > 0 else np.inf
        arm = min(be, tr_, giveback_arm(a, hd.init_risk, p))
        if not hd.be_done and hd.mfe < arm:
            lvl = pos.entry + side * arm * pip
            tp = pos.tp if math.isfinite(pos.tp) else side * np.inf
            lo, hi = (pos.sl, min(tp, lvl)) if side > 0 else (max(tp, lvl), pos.sl)
            seg = min(end, eod_tick)
            j = _first_hit(price[:seg], hd.cur, lo, hi)
            if j >= seg:
                hd.cur = seg
                if seg < end:
                    return _close_all(ctx, hd, seg, "eod")
                return None
        else:
            j = hd.cur
        why = _tick(ctx, hd, j, p, spec, digits)
        hd.cur = j + 1
        if why:
            return why
    return None


# ---------------------------------------------------------------- the bar loop
def tms_orb(ctx: Ctx, **overrides) -> None:
    sym, t, pip = ctx.ch.symbol, ctx.t, ctx.inst.pip
    p = cbot_params("tms_orb", sym, **overrides)
    if p["TmsTimeFrame"] != "Hour" or not p["UseAtr"]:
        raise ValueError("the TMS+ORB port models TmsTimeFrame=Hour with ATR stops only")
    b, hb = ctx.bars(PERIOD_MIN[preset("tms_orb", sym)["period"]]), ctx.bars(60)
    ch, macro, orb = chart_tms(b, p), MacroTms(hb, p), orb_states(b, p, pip)
    atr = atr_sma(b.h, b.l, b.c, p["AtrPeriod"])
    gate, hd, prev_atr = PostTp(), None, 10.0
    for i in range(3, len(b)):
        e = int(b.event_tick[i])
        if e >= len(t):
            break
        if hd is not None:
            hd.atr = prev_atr
            if run_ticks(ctx, hd, e, p):
                gate.on_close(ctx, hd.pos, p, prev_atr)
                hd = None
        a_pips = float(atr[i]) / pip if math.isfinite(atr[i]) and atr[i] > 0 else 10.0
        prev_atr = a_pips
        now = int(t.ts[e])
        phase, active = session_info(now, p)
        if hd is None and (not active or phase in ("closed", "ending")):
            continue                                            # the cBot's cost gate: no request sent
        mh = int(np.searchsorted(hb.close_time, now, side="right")) - 1
        bias = int(macro.bias[mh]) if mh >= 0 else 0
        bid, ask = float(t.bid[e]), float(t.ask[e])
        gate.release(bias, bid, ask, a_pips, pip, orb, i, ch, macro, mh, p)
        if hd is not None:
            pos = hd.pos
            want = phase == "ending" or bool((ch["exit_long"] if pos.side > 0 else ch["exit_short"])[i])
            m_exit = mh >= 0 and bool((macro.exit_long if pos.side > 0 else macro.exit_short)[mh])
            if want and close_valid(pos.side, pos.entry, pos.sl, bid, ask, m_exit):
                why = "ai_close"
            elif p["BiasFlipExit"] and bias == -pos.side:
                why = "bias_flip"
            else:
                continue
            _close_all(ctx, hd, e, why)
            gate.on_close(ctx, pos, p, a_pips)
            hd = None
            continue
        od = orb_data(orb, i, (bid + ask) / 2.0, p, pip)
        regime, flips = market_regime(b, i, now, float(orb["hi"][i]), float(orb["lo"][i]), p)
        side = cycle_gate(sym, now, phase, active, str(p["SessionName"]), bias, gate, od, ch, i, a_pips, regime, flips)
        if not side or not ctx.can_enter(e) or (gate.active and gate.side == side):
            continue
        if p["MaxBreakoutDistanceAtr"] > 0 and od.dist > p["MaxBreakoutDistanceAtr"] * a_pips:
            continue
        if int(orb["dir"][i]) == -side:
            continue
        sl_p, tp_p = entry_levels(side, bid, ask, a_pips, float(orb["hi"][i]), float(orb["lo"][i]), p, pip)
        pos = ctx.open(e, side)
        pos.sl = pos.sl0 = pos.entry - side * sl_p * pip
        pos.tp = pos.tp0 = NAN if (p["TrendTpDisabled"] and regime == "trending") else pos.entry + side * tp_p * pip
        hd = Hold(pos, e + 1, a_pips, session_end_ms(now, p), sl_p)
    if hd is not None:
        _close_all(ctx, hd, len(t) - 1, "tail")
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_tms.py -q -s`
Expected: 5 passed; the smoke test prints the trade count and exit reasons (0 trades is possible for a quiet
month, but then run it once on 2025-03..05 and report the counts before moving on).

- [ ] **Step 5: Smoke on the three sessions**

Run: `research/.venv/bin/python -c "
from collections import Counter
from research.lab.engine import Ctx; from research.lab.feed import load_chunk; from research.lab.strategies.tmsorb import tms_orb
for s in ('USDJPY', 'EURUSD', 'US30', 'USTEC', 'XAUUSD'):
    ctx = Ctx(load_chunk(s, 'real', 2025), 'TMSORB'); tms_orb(ctx)
    print(s, len(ctx.trades), Counter(t.why for t in ctx.trades), round(sum(t.net for t in ctx.trades), 2))"`
Expected: no exception; trades on every symbol; exit reasons spread over sl/tp/eod/giveback/ai_close/bias_flip.
Report the counts. If a symbol has 0 trades, find which gate blocks every bar (count the `cycle_gate` zeros by
reason in a scratch copy) and report it before moving on.

- [ ] **Step 6: Whole research suite green; leave the files in the working tree (no commit)**

---
### Task 15: Strategy catalog and STRATEGIES.md

**Files:**
- Create: `research/lab/catalog.py`
- Test: `research/tests/lab/test_lab_catalog.py`

**Interfaces:**
- Consumes: every strategy function above, `rules.BANK_CONFIGS, BANK_2025_R, parse_bank`, `universe.ALL, FX, FX_REAL, INDICES`.
- Produces: `catalog.StrategyInfo(id, name, status, origin, family, timeframe, rules, findings=(), fn=None, params={}, symbols=ALL, variants=("real","mirror","shuffle"), label="")` with `.runnable`, `.run(ctx)`; `catalog.CATALOG: List[StrategyInfo]`; `catalog.by_id() -> Dict[str, StrategyInfo]`; `catalog.runnable_ids() -> List[str]`; `catalog.catalog_hash() -> str`; `catalog.render_markdown(run_dir=None) -> str`; `catalog.main(argv)` writes `research/STRATEGIES.md`. Reads `RUN_DIR/cells.csv` columns `strategy, symbol, net, pos_every_year, all_flags` (Task 17 writes them).

- [ ] **Step 1: Write the failing tests** (`research/tests/lab/test_lab_catalog.py`)

```python
import inspect
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_m1, needs_ticks  # noqa: E402
from research.lab.catalog import ALL_VARIANTS, CATALOG, STATUSES, render_markdown  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk, real_ticks  # noqa: E402
from research.lab.universe import ALL, instrument  # noqa: E402
from research.ticks import day_ms  # noqa: E402


def test_catalog_entries_are_complete():
    ids = [s.id for s in CATALOG]
    assert len(ids) == len(set(ids))
    for s in CATALOG:
        assert s.status in STATUSES and s.rules and s.origin and s.findings, s.id
        assert set(s.symbols) <= set(ALL) and set(s.variants) <= set(ALL_VARIANTS), s.id
        if s.runnable:
            inspect.signature(s.fn).bind(None, **s.params)
    assert {"FLOWRSI", "JUDAS", "TMSORB"} <= {s.id for s in CATALOG if s.status == "live"}
    assert sum(s.id.startswith("BANK-") for s in CATALOG) == 24
    assert sum(s.id.startswith("FLOWRSI-E") for s in CATALOG) == 20
    assert {"BTC-S1", "XAU-T1", "TOM", "K1", "K1b", "K2", "VB1", "LC1", "GF1", "OD1", "MEF", "FXM1", "X1", "WF1",
            "PAIRS"} <= set(ids)


def test_render_markdown_lists_every_strategy_and_the_lab_result(tmp_path):
    (tmp_path / "cells.csv").write_text("strategy,symbol,net,pos_every_year,all_flags\n"
                                        "BTC-S1,BTCUSD,1234.5,True,False\nBTC-S1,ETHUSD,-34.5,False,False\n")
    md = render_markdown(tmp_path)
    for s in CATALOG:
        assert f"## {s.id} — " in md
    assert "net $+1,200 over 2 symbols, 1 positive" in md


@needs_m1
@needs_ticks
def test_every_runnable_strategy_runs_on_a_short_slice():
    chunks = {}

    def chunk(sym):
        if sym not in chunks:
            t = real_ticks(sym, date(2025, 2, 3), date(2025, 3, 21))
            chunks[sym] = Chunk(sym, "real", 2025, t, day_ms(date(2025, 3, 3)), day_ms(date(2025, 3, 15)),
                                instrument(sym))
        return chunks[sym]

    for s in CATALOG:
        if s.runnable:
            ch = chunk("EURUSD" if "EURUSD" in s.symbols else s.symbols[0])
            ctx = Ctx(ch, s.id)
            s.run(ctx)
            assert all(ch.lo_ms <= tr.t_in < ch.hi_ms for tr in ctx.trades), s.id
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_catalog.py -q`
Expected: FAIL, `No module named 'research.lab.catalog'`.

- [ ] **Step 3: Implement `research/lab/catalog.py`**

```python
"""The strategy catalog: every strategy the project runs or has researched - what it does, where it came from,
what was found, and the code the lab runs for it. New research adds an entry here (and a function in
research/lab/strategies/ when it is new code).

  python -m research.lab.catalog [RUN_DIR]   -> research/STRATEGIES.md (with RUN_DIR/cells.csv's results)"""
import csv
import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from research.lab.strategies import rules
from research.lab.strategies.flowrsi import flowrsi
from research.lab.strategies.judas import judas
from research.lab.strategies.tmsorb import tms_orb
from research.lab.universe import ALL, FX, FX_REAL, INDICES

ALL_VARIANTS = ("real", "mirror", "shuffle")
REAL_ONLY = ("real",)
US_INDICES = ("US30", "USTEC")
MEF_PAIRS = ("EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDJPY")
STATUSES = ("live", "candidate", "rejected", "not_applicable")
OUT = Path(__file__).resolve().parents[1] / "STRATEGIES.md"


@dataclass(frozen=True)
class StrategyInfo:
    id: str
    name: str
    status: str                     # live | candidate | rejected | not_applicable
    origin: str
    family: str
    timeframe: str
    rules: str
    findings: Tuple[str, ...] = ()
    fn: Optional[Callable] = None   # fn(ctx, **params); None = catalogued only
    params: Dict = field(default_factory=dict)
    symbols: Tuple[str, ...] = ALL
    variants: Tuple[str, ...] = ALL_VARIANTS
    label: str = ""

    @property
    def runnable(self) -> bool:
        return self.fn is not None

    def run(self, ctx) -> None:
        self.fn(ctx, **self.params)


FLOWRSI_RULES = (
    "M15. Fast RSI(7) crosses the slow RSI(14) inside the zone (buy 25-50, sell 50-75) within 3 bars and is still "
    "crossed; SMC filter: a buy needs discount, a bullish FVG or a liquidity sweep (premium / bearish FVG / sweep "
    "for a sell). SL at the swing +/- 0.5 ATR with a pip floor, TP 1.5R; break-even at 1R with a 50 % partial, "
    "trailing from 1.2R. Macro TMS filter off (the replica does not model it; phase 1 showed it hurts).")
FLOWRSI_FINDINGS = (
    "2026-09-25 cTrader baseline #27-#41 (live presets, $2000, 01/01-24/09/2026): all 14 trading pairs negative, "
    "pooled -0.13R (t -7.3); 45 % of positions reach the partial.",
    "Macro TMS off: better on 11/14 pairs, pooled -0.084R, still negative (phase 1, jobs #42-#96).",
    "Offline fixed-lot sim, 15 pairs 2025-09/2026, no caps: -$67k (C1) / -$86k (C0); every pair negative in $.",
)
E_DESC = {
    "E1a": "the live cross traded in the opposite direction",
    "E1b": "fade only the crosses taken with slow RSI < 30 / > 70",
    "E2a": "RSI(14) pullback through 40/60 in the H1 EMA50 trend",
    "E2b": "RSI(14) pullback through 40/60 in the H4 EMA50 trend",
    "E3a": "RSI(2) < 10 / > 90 in the H1 trend",
    "E3b": "RSI(2) < 10 / > 90, no trend filter",
    "E4a": "close back inside Bollinger(20, 2) with ADX(14) < 20",
    "E4b": "close back inside Bollinger(20, 2), no ADX filter",
    "E5a": "Donchian 20 breakout in the H4 trend",
    "E5b": "Donchian 48 breakout in the H4 trend",
}
EXIT_DESC = {"X1": "fixed stop at the ATR level, TP 1.5R, no break-even or trailing",
             "X2": "FlowRSI's exits (break-even + partial at 1R, trailing)"}
SCREEN_FINDING = ("Entry screening 2026-09-25 (15 pairs, 2025 and 2026 on ticks, $2000, bar t >= 2 in 2025, Jan-May "
                  "and Jun-Sep 2026): negative in every period, none beat the random control; random entries cost "
                  "-0.03R (indices, BTC, XAU) to -0.16R (JPY crosses, ETH) per trade.")
BANK_FINDING = ("552-config bank on 2025-2026 (M1 engine): 0 configs with t >= 2 in 2025, Jan-May and Jun-Sep 2026. "
                "This entry is the family's best pooled 2025 cell, frozen for the lab.")


def _flowrsi_entries() -> List[StrategyInfo]:
    out = [StrategyInfo("FLOWRSI", "FlowRSI (live bot, Macro TMS off)", "live",
                        "cBot/FlowRsiBot.cs + app/cbot_presets.py; replica research/sim.py", "RSI cross + SMC", "M15",
                        FLOWRSI_RULES, FLOWRSI_FINDINGS, flowrsi, dict(name="C0", exit_mode="X2"),
                        label="replica calibrated on cTrader #43-#56, #93 (>= 93 % of entries matched)"),
           StrategyInfo("FLOWRSI-C1", "FlowRSI with the wider SL floor", "rejected", "FlowRSI phase 1, H2 (2026-09-25)",
                        "RSI cross + SMC", "M15", FLOWRSI_RULES + " MinSlFloorPips 25 (FX) / 30 (JPY).",
                        ("Phase 1: -0.134R -> -0.080R on 8 forex pairs, still negative.",), flowrsi,
                        dict(name="C1", exit_mode="X2"), label="replica")]
    for e, desc in E_DESC.items():
        for x in ("X1", "X2"):
            out.append(StrategyInfo(f"FLOWRSI-{e}-{x}", f"FlowRSI entry {e}, exit {x}", "rejected",
                                    "FlowRSI entry screening (2026-09-25, research/signals.py)", "entry screening",
                                    "M15", f"M15 entry: {desc}. Exit: {EXIT_DESC[x]}.", (SCREEN_FINDING,), flowrsi,
                                    dict(name=e, exit_mode=x), label="replica"))
    return out


JUDAS = StrategyInfo(
    "JUDAS", "Asian Range Judas Sweep (live bot)", "live",
    "cBot/AsianRangeJudasSweepBot.cs + app/server.py evaluate_judas_sweep_gate", "liquidity sweep", "M15",
    "Asian range = high/low of the 00:00-06:00 UTC bars. In the London (07-10 UTC summer) or New York (12:30-16 UTC "
    "summer) killzone, a bar that spikes beyond the range by the sweep buffer and closes back inside with a rejection "
    "wick >= 35 % of the bar opens a 3-bar signal window; the trade goes back into the range. Guards: range inside "
    "the preset and the server band, one trade per side per Asian session, the side locked after a decisive close "
    "beyond the range (an open position on that side is closed), entry within 25 % of the range from the swept "
    "level. SL = preset stoplossPip raised to max(AiSlMinFloorPips, 0.8 ATR14), TP = takeprofitPip, break-even at 1.5R.",
    ("Live on the demo account since 2026-09; entries only through the AI gate, so it was never backtested before "
     "the lab.",),
    judas, label="port, uncalibrated: the AI gate approves every candidate; AI SL/TP = the preset fallbacks")

TMSORB = StrategyInfo(
    "TMSORB", "TMS + ORB (live AiAgentBot)", "live",
    "cBot/AiAgentBot.cs + app/server.py evaluate_cycle_gate / validate_tms_close_decision",
    "ORB breakout + TDI bias", "M15 (USTEC M5), H1 bias",
    "Opening range = the first 15 minutes of the session (Tokyo 00:00, London 08:00, New York 13:00, US indices 14:30 "
    "UTC in winter, DST-adjusted). Macro bias = the last confirmed H1 TDI cross (RSI6 of Heikin-Ashi vs its SMA6, with "
    "HA colour and Stoch 6/6/4), with flip hysteresis. The server's cycle gate: in session and outside the NYSE-open "
    "buffer, bias set, post-TP gate clear, a decisive ORB breakout in the bias direction inside the entry window (or a "
    "TDI bounce / EMA-retest model 2), breakout-distance caps, choppy-market gate. Entry in the bias direction; SL 1.5 "
    "ATR clamped to [0.8, 3] ATR and widened to the far side of the range, TP >= SL x 4/3 (none in a trending "
    "session). Exits: break-even + 50 % partial at 1.2 ATR, ATR trailing with a tier 2, MFE giveback lock, session-end "
    "flatten, the AI's exit-signal / session-ending close (server-validated), bias-flip exit.",
    ("Live on the demo account since 2026-09; the AI decides every entry, so it was never backtested before the lab.",),
    tms_orb, label="port, uncalibrated: the AI approves every gate-passing candidate; loss-streak and dollar-risk "
                   "guards off")

RESEARCH = [
    StrategyInfo("BTC-S1", "Shock-bar momentum", "rejected", "strategy search round 1 (2026-09-25), pre-registered",
                 "momentum", "M15",
                 "A bar whose close moved more than 2.5 x ATR20 (SMA of TR) is followed at the next tick; SL and TP 2 x "
                 "ATR from the fill; time exit after 12 bars.",
                 ("Sep-Dec 2024 unseen +0.22R (t 1.8); 2025 +0.10R, 2026 YTD +0.09R (ticks, $2000); 2023 +0.000R -> "
                  "pooled 2023-24 t 1.0: failed the confirmation bar.",
                  "Fixed lot 0.1: $ -103 / +1164 / +2154 / +260 for 2023..2026; beat random entries in 20/20 seeds (2025)."),
                 rules.shock_follow, dict(tf=15, Z=2.5, H=12, SLK=2.0, TPK=2.0)),
    StrategyInfo("XAU-T1", "H4 Donchian 30 trend", "rejected", "strategy search round 1 (2026-09-25), pre-registered",
                 "trend following", "H4",
                 "First H4 close beyond the prior 30-bar high/low -> follow at the next tick; SL 1.5 x ATR20, no target, "
                 "time exit after 12 bars.",
                 ("Jul-Dec 2024 +0.46R; 2023 +0.10R, 2024 +0.09R (t 0.5); shorts negative -> mostly gold beta.",
                  "Fixed lot 0.01: $ +39 / +154 / +283 / +665 for 2023..2026."),
                 rules.bank_rule, dict(kind="donch", mode=1, tf="H4", N=30, H=12, SLK=1.5, warm=31)),
    StrategyInfo("TOM", "Turn of the month", "rejected", "literature, round 2 (2026-09-25)", "calendar", "cash session",
                 "Long over the cash session on the last and the first three trading days of each month; SL 3 %.",
                 ("2025 +0.041R, 2026 +0.088R (t 3.0); 2023 +0.047R but the other days +0.021R; 2024 -0.014R: failed.",),
                 rules.turn_of_month, symbols=INDICES),
    StrategyInfo("K1", "FX weekly fade", "rejected", "round 1, pre-registered (strategy_prereg.md)", "mean reversion",
                 "D1",
                 "z = (C - C[5]) / ATR20(D1); |z| > 1.5 -> trade against z 2 h after the New York close; SL 3 x ATR from "
                 "the signal close, no target, exit after 5 D1 bars.",
                 ("2025 +0.10R (t 2.6, 8/8 pairs) -> 2026 -0.07R (1/8 pairs); 72-cell grid 0 % positive in 2026: "
                  "regime flip.",),
                 rules.weekly_fade, dict(SLK=3.0), symbols=FX),
    StrategyInfo("K1b", "FX weekly fade, SL 2 ATR", "rejected", "K1's sizing variant", "mean reversion", "D1",
                 "K1 with the stop at 2 x ATR.", ("Reported with K1; same verdict.",),
                 rules.weekly_fade, dict(SLK=2.0), symbols=FX),
    StrategyInfo("K2", "Index opening range (60 min)", "rejected", "round 1, pre-registered", "breakout", "cash session",
                 "Direction of the first 60 minutes of the cash session, entered at its end, stop at the other end of "
                 "the range, exit at the close.",
                 ("2025 +0.13R (t 2.3, best of 16 ORB variants) -> 2026 +0.005R: failed.",),
                 rules.opening_range, symbols=INDICES),
    StrategyInfo("VB1", "Index volatility breakout", "rejected", "round 2, pre-registered", "breakout", "cash session",
                 "Stop entries at the open +/- 0.35 x the mean range of the last 5 sessions; the first side touched "
                 "trades; SL at the open; exit at the close.",
                 ("2025 +0.10R (t 2.1), Jan-May 2026 +0.08R, Jun-Sep 2026 -0.14R: failed.",),
                 rules.vol_breakout, symbols=INDICES),
    StrategyInfo("LC1", "US last-30-minute fade", "rejected", "round 2, pre-registered", "intraday reversal", "30 min",
                 "Fade C(15:30) - C(10:00) New York from 15:30 to the 16:00 close; SL 2 x ATR20 (30 min).",
                 ("2025 +0.040R (t 2.2), 2026 +0.022R (t 1.3); Jul-Dec 2024 -0.001R: failed.",),
                 rules.last30_fade, symbols=US_INDICES),
    StrategyInfo("GF1", "US opening-gap fade", "rejected", "round 2, pre-registered", "intraday reversal", "M1",
                 "An opening gap larger than 0.1 x the mean session range is faded at 9:31 New York, TP at the previous "
                 "close, SL the gap's size beyond the open, exit at the close.",
                 ("2026 +0.046R (t 0.8): failed.",), rules.gap_fade, symbols=US_INDICES),
    StrategyInfo("OD1", "Overnight drift", "rejected", "literature (Boyarchenko, Larsen, Whelan 2023), round 2",
                 "calendar", "H1", "Long US30 / USTEC from 02:00 to 03:00 New York on weekdays; SL 2 x ATR20(H1).",
                 ("2025 -0.006R, 2026 +0.029R (t 2.6): sign flip, failed.",), rules.overnight_drift,
                 symbols=US_INDICES),
    StrategyInfo("MEF", "Month-end London fix USD flow", "rejected", "literature (Melvin & Prins 2015), round 2", "flow",
                 "H1",
                 "Last business day of the month, 10:00 -> 16:00 London: sell USD if US30 beat DE40 in USD over the "
                 "month, else buy it; SL 2 x ATR20(H1).",
                 ("20 events in 2025-26, +0.15R (t 1.0): too few to judge.",), rules.month_end_fix,
                 symbols=MEF_PAIRS, variants=REAL_ONLY),
    StrategyInfo("FXM1", "FX fade/follow regime switch", "rejected", "round 2, pre-registered", "meta", "D1",
                 "K1's signal traded in the direction the base fade earned over the last 120 days on the 8 FX pairs.",
                 ("May-Dec 2025 +0.11R (t 2.9), Jan-May 2026 -0.10R (t -2.3), Jun-Sep 2026 0.00R: failed.",),
                 rules.regime_fade, symbols=FX, variants=REAL_ONLY),
    StrategyInfo("X1", "Cross-sectional FX reversal", "rejected", "round 2, pre-registered", "cross-sectional", "H4",
                 "Currency strengths from the 8 pairs' 30-bar H4 returns; every 30 bars the 3 pairs with the largest "
                 "ATR-scaled strength gap are traded against it for 30 bars, no stop.",
                 ("2025 +0.74 ATR/trade (t 2.4) -> 2026 -0.09: failed.",), rules.cross_sectional_reversal,
                 symbols=FX_REAL, variants=REAL_ONLY),
    StrategyInfo("WF1", "Walk-forward ridge model", "rejected", "round 2, pre-registered", "machine learning", "M15",
                 "Ridge on 14 causal features, refit monthly on the prior 6 months; trade the top decile of |prediction| "
                 "in its direction, SL 2 x ATR20, exit after 4 bars.",
                 ("M15 all symbols -0.084R (t -17.5); low-cost group -0.005R; H1 -0.037R: failed.",),
                 rules.walk_forward_ridge),
]


def _bank_rules(kw: dict) -> str:
    way = "follow" if kw["mode"] > 0 else "fade"
    if kw["kind"] == "zmove":
        sig = f"C - C[{kw['L']}] beyond {kw['Z']} x ATR20"
    elif kw["kind"] == "donch":
        sig = f"first close beyond the prior {kw['N']}-bar high/low"
    else:
        sig = f"RSI({kw['P']}) above {100 - kw['lo']:g} / below {kw['lo']:g}"
    tp = f"TP {kw['TPK']} x ATR" if kw["TPK"] else "no target"
    return f"{kw['tf']}: {sig} -> {way}; SL {kw['SLK']} x ATR20 from the fill, {tp}, exit after {kw['H']} bars."


def _bank_entries() -> List[StrategyInfo]:
    out = []
    for name, r25 in zip(rules.BANK_CONFIGS, rules.BANK_2025_R):
        kw = rules.parse_bank(name)
        kind = {"zmove": "z-move", "donch": "Donchian", "rsi": "RSI"}[kw["kind"]]
        way = "follow" if kw["mode"] > 0 else "fade"
        out.append(StrategyInfo(f"BANK-{name}", f"Bank: {kind} {way} {kw['tf']}", "rejected",
                                "rule bank (research/scan/bank.py, 2026-09-25)", f"{kind} {way}", kw["tf"],
                                _bank_rules(kw), (BANK_FINDING, f"Pooled 2025 mean R of this cell: {r25:+.3f}."),
                                rules.bank_rule, kw))
    return out


INFO = [
    StrategyInfo("PAIRS", "Pairs / stat-arb", "not_applicable", "round 2 (2026-09-25)", "statistical arbitrage",
                 "M15/H1",
                 "Rolling-OLS z-score of the log spread of 14 related pairs (US30-USTEC, DE40-UK100, EURUSD-GBPUSD, "
                 "EURJPY-GBPJPY, BTC-ETH, ...); trade both legs.",
                 ("Nothing in 2025, not even before costs.",
                  "Needs two legs open at once: outside the lab's one-position rule.")),
    StrategyInfo("LEADLAG", "Cross-asset lead-lag", "rejected", "round 2 (2026-09-25)", "lead-lag", "M1/M5",
                 "Trade a follower (DE40, UK100, USTEC) on the leader's last M1/M5 move (US indices, DE40, BTC).",
                 ("Correlations of +2..4 % but only 1-2 spreads in size; rules ~0. Not coded in the lab.",)),
    StrategyInfo("HOD", "Hour-of-day drift", "rejected", "round 1 (2026-09-25)", "calendar", "H1",
                 "Trade the average return of each hour of the day.",
                 ("The only persistent pattern is the 17:00 New York rollover spread dip: not tradeable. Not coded.",)),
    StrategyInfo("NOISE", "Noise-area intraday momentum", "rejected", "round 1, literature", "intraday momentum",
                 "30 min", "Trade index breakouts of the average intraday move envelope.", ("2025 t < 1. Not coded.",)),
]

CATALOG: List[StrategyInfo] = [*_flowrsi_entries(), JUDAS, TMSORB, *RESEARCH, *_bank_entries(), *INFO]


def by_id() -> Dict[str, StrategyInfo]:
    return {s.id: s for s in CATALOG}


def runnable_ids() -> List[str]:
    return [s.id for s in CATALOG if s.runnable]


def catalog_hash() -> str:
    text = "|".join(f"{s.id}:{s.fn.__name__ if s.fn else ''}:{sorted(s.params.items())}:{s.symbols}:{s.variants}:"
                    f"{s.rules}" for s in CATALOG)
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def _lab_results(run_dir) -> Dict[str, dict]:
    out = {}
    path = Path(run_dir) / "cells.csv" if run_dir else None
    if not path or not path.exists():
        return out
    with open(path) as fh:
        for row in csv.DictReader(fh):
            s = out.setdefault(row["strategy"], dict(net=0.0, cells=0, pos=0, every=0, flags=0, best=("", -1e18)))
            net = float(row["net"])
            s["net"] += net
            s["cells"] += 1
            s["pos"] += net > 0
            s["every"] += row["pos_every_year"] == "True"
            s["flags"] += row["all_flags"] == "True"
            if net > s["best"][1]:
                s["best"] = (row["symbol"], net)
    return out


def _symbols(s: StrategyInfo) -> str:
    return "all 22" if s.symbols == ALL else ("FX 15" if s.symbols == FX else ", ".join(s.symbols))


def render_markdown(run_dir=None) -> str:
    lab = _lab_results(run_dir)
    src = f" and the lab run `{Path(run_dir).name}`" if run_dir else ""
    lines = ["# Strategy catalog", "",
             f"_Generated by `python -m research.lab.catalog` from `research/lab/catalog.py`{src}. Edit the catalog, "
             "not this file._", "",
             "Lab rules: $10k, fixed lots per symbol, no loss limits, one position per strategy x symbol, tick level, "
             "2023-01 .. 2026-09 (docs/superpowers/specs/2026-09-25-strategy-lab-design.md).", "",
             "| id | name | status | family | TF | symbols | lab net $ | cells + | all flags |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s in CATALOG:
        r = lab.get(s.id)
        cols = f"{r['net']:+,.0f} | {r['pos']}/{r['cells']} | {r['flags']}" if r else " | | "
        lines.append(f"| {s.id} | {s.name} | {s.status} | {s.family} | {s.timeframe} | {_symbols(s)} | {cols} |")
    lines.append("")
    for s in CATALOG:
        lines += [f"## {s.id} — {s.name}", "", f"- Status: **{s.status}**" + (f" ({s.label})" if s.label else ""),
                  f"- Origin: {s.origin}", f"- Family / timeframe: {s.family} / {s.timeframe}", f"- Rules: {s.rules}"]
        if s.params:
            lines.append(f"- Parameters: `{s.params}`")
        lines.append(f"- Lab: `{s.fn.__module__}.{s.fn.__name__}` on {_symbols(s)}, variants {', '.join(s.variants)}"
                     if s.runnable else "- Lab: not run")
        lines += [f"- Finding: {f}" for f in s.findings]
        r = lab.get(s.id)
        if r:
            lines.append(f"- Latest lab run: net ${r['net']:+,.0f} over {r['cells']} symbols, {r['pos']} positive, "
                         f"{r['every']} positive every year, {r['flags']} with all four flags; best {r['best'][0]} "
                         f"${r['best'][1]:+,.0f}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    OUT.write_text(render_markdown(argv[0] if argv else None))
    print(OUT)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_catalog.py -q`
Expected: 3 passed (the slice test runs every runnable entry; a few minutes is fine).

- [ ] **Step 5: Render the catalog without results**

Run: `research/.venv/bin/python -m research.lab.catalog && head -30 research/STRATEGIES.md`
Expected: the summary table with ~68 rows.

- [ ] **Step 6: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 16: Runner

**Files:**
- Create: `research/lab/run.py`
- Test: `research/tests/lab/test_lab_run.py`

**Interfaces:**
- Consumes: `catalog.by_id, runnable_ids, catalog_hash`, `feed.load_chunk, YEARS`, `engine.Ctx`, `control.random_control`, `universe.ALL, REAL, instrument`.
- Produces: `run.TRADE_FIELDS`, `run.CONTROL_FIELDS`, `run.trade_row(tr, year) -> list`, `run._job_strategies(symbol, variant, ids) -> List[str]`, `run.run_job(symbol, variant, ids, years, seeds, run_dir) -> dict`, `run.merge(run_dir)`, `run.positive_cells(run_dir, ids) -> {symbol: [ids]}`, `run.main(argv)`. Files: `RUN_DIR/parts/<SYMBOL>_<variant>.{trades,control,errors,coverage}.csv` (no header), merged `trades.csv.gz`, `control.csv`, `errors.csv`, `coverage.csv` (with headers), `meta.json`.

- [ ] **Step 1: Write the failing tests** (`research/tests/lab/test_lab_run.py`)

```python
import csv
import gzip
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import bar_ticks, make_chunk  # noqa: E402
from research.lab import feed  # noqa: E402
from research.lab.run import TRADE_FIELDS, _job_strategies, merge, run_job  # noqa: E402
from research.ticks import day_ms  # noqa: E402

QUIET, SHOCK = (1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1045, 1.0995, 1.1040)
AFTER = (1.1040, 1.1045, 1.1035, 1.1040)


def test_job_strategies_respect_symbols_and_variants():
    ids = ["TOM", "BTC-S1", "X1"]
    assert _job_strategies("US30", "real", ids) == ["TOM", "BTC-S1"]
    assert _job_strategies("EURUSD", "mirror", ids) == ["BTC-S1"]
    assert _job_strategies("EURGBP", "mirror", ids) == []                       # synthetic: real data only
    assert _job_strategies("EURUSD", "shuffle:3", ["BTC-S1", "X1"]) == ["BTC-S1"]


def test_run_job_writes_parts_and_merge_adds_headers(tmp_path, monkeypatch):
    def fake_chunk(symbol, variant, year, *a, **k):
        if year == 2026:
            return None
        ts, px = bar_ticks(day_ms(date(year, 3, 10)), 15, [QUIET] * 30 + [SHOCK] + [AFTER] * 20)
        return make_chunk(ts, px * 60_000, spread=5.0, symbol="BTCUSD", year=year)

    monkeypatch.setattr(feed, "load_chunk", fake_chunk)
    out = run_job("BTCUSD", "real", ["BTC-S1"], [2025, 2026], 2, str(tmp_path))
    assert out["trades"] == 1 and out["errors"] == 0
    parts = tmp_path / "parts"
    rows = list(csv.reader(open(parts / "BTCUSD_real.trades.csv")))
    assert len(rows) == 1 and rows[0][:4] == ["BTC-S1", "BTCUSD", "real", "2025"]
    assert len(list(csv.reader(open(parts / "BTCUSD_real.control.csv")))) == 2
    assert [r[3] for r in csv.reader(open(parts / "BTCUSD_real.coverage.csv"))] == ["ok", "no data"]
    merge(tmp_path)
    with gzip.open(tmp_path / "trades.csv.gz", "rt") as fh:
        assert next(csv.reader(fh)) == TRADE_FIELDS
    assert (tmp_path / "control.csv").read_text().startswith("strategy,symbol,year,seed")
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_run.py -q`
Expected: FAIL, `No module named 'research.lab.run'`.

- [ ] **Step 3: Implement `research/lab/run.py`**

```python
"""Run the strategy catalog over the lab universe (docs/superpowers/specs/2026-09-25-strategy-lab-design.md).

  python -m research.lab.run [--strategies ID ...] [--symbols SYM ...] [--variants real mirror]
                             [--years 2023 2024 2025 2026] [--seeds 20] [--workers 3] [--run-dir DIR]
  python -m research.lab.run --shuffle 20 --into RUN_DIR      # week-shuffle the cells whose real net > 0

One job = one (symbol, variant). Inside a job the years run in order, so a position can carry across a year end,
and every strategy trades the same loaded chunk. Real-data jobs also run the random-entry control (--seeds).
Each job writes RUN_DIR/parts/<SYMBOL>_<variant>.*.csv; merge() joins them into trades.csv.gz, control.csv,
errors.csv and coverage.csv. meta.json records the arguments, the git HEAD, the lab code hash and the catalog hash."""
import argparse
import csv
import gzip
import hashlib
import json
import math
import subprocess
import time
import traceback
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from research.lab.catalog import by_id, catalog_hash, runnable_ids
from research.lab.feed import YEARS
from research.lab.universe import ALL, REAL, instrument
from research.ticks import DATA_DIR

RESULTS = Path(__file__).resolve().parents[1] / "results" / "lab"
TRADE_FIELDS = ["strategy", "symbol", "variant", "year", "side", "t_in", "t_out", "entry", "exit", "units", "sl0",
                "tp0", "gross", "comm", "swap", "net", "risk_usd", "r", "why"]
CONTROL_FIELDS = ["strategy", "symbol", "year", "seed", "n", "net", "sum_r", "n_r"]
ERROR_FIELDS = ["strategy", "symbol", "variant", "year", "traceback"]
COVERAGE_FIELDS = ["symbol", "variant", "year", "status", "ticks"]


def trade_row(tr, year: int) -> list:
    return [tr.strategy, tr.symbol, tr.variant, year, tr.side, tr.t_in, tr.t_out, f"{tr.entry:.6f}", f"{tr.exit:.6f}",
            f"{tr.units:g}", f"{tr.sl0:.6f}", f"{tr.tp0:.6f}", f"{tr.gross:.4f}", f"{tr.comm:.4f}", f"{tr.swap:.4f}",
            f"{tr.net:.4f}", f"{tr.risk_usd:.4f}", f"{tr.r:.5f}", tr.why]


def _job_strategies(symbol: str, variant: str, ids) -> List[str]:
    base = variant.split(":")[0]
    cat = by_id()
    return [i for i in ids if symbol in cat[i].symbols and base in cat[i].variants and (base == "real" or symbol in REAL)]


def run_job(symbol: str, variant: str, ids: List[str], years: List[int], seeds: int, run_dir: str) -> dict:
    from research.lab.control import random_control
    from research.lab.engine import Ctx
    from research.lab.feed import load_chunk
    cat = by_id()
    parts = Path(run_dir) / "parts"
    parts.mkdir(parents=True, exist_ok=True)
    tag = f"{symbol}_{variant.replace(':', '-')}"
    busy = {i: 0 for i in ids}
    n_trades = n_errors = 0
    t0 = time.time()
    files = {k: open(parts / f"{tag}.{k}.csv", "w", newline="") for k in ("trades", "control", "errors", "coverage")}
    try:
        w = {k: csv.writer(f) for k, f in files.items()}
        for y in years:
            ch = load_chunk(symbol, variant, y)
            if ch is None:
                w["coverage"].writerow([symbol, variant, y, "no data", 0])
                continue
            w["coverage"].writerow([symbol, variant, y, "ok", len(ch.t)])
            for i in ids:
                try:
                    ctx = Ctx(ch, i, busy[i])
                    cat[i].run(ctx)
                    busy[i] = ctx.busy_ms
                    w["trades"].writerows(trade_row(tr, y) for tr in ctx.trades)
                    n_trades += len(ctx.trades)
                    for s in range(seeds if variant == "real" else 0):
                        c = random_control(ch, ctx.trades, s)
                        rs = [x.r for x in c if math.isfinite(x.r)]
                        w["control"].writerow([i, symbol, y, s, len(c), f"{sum(x.net for x in c):.4f}", f"{sum(rs):.5f}",
                                               len(rs)])
                except Exception:
                    n_errors += 1
                    w["errors"].writerow([i, symbol, variant, y, traceback.format_exc()])
            del ch
    finally:
        for f in files.values():
            f.close()
    return dict(symbol=symbol, variant=variant, strategies=len(ids), trades=n_trades, errors=n_errors,
                seconds=round(time.time() - t0))


def merge(run_dir: Path) -> None:
    run_dir = Path(run_dir)
    parts = sorted((run_dir / "parts").glob("*.csv"))
    with gzip.open(run_dir / "trades.csv.gz", "wt", newline="") as out:
        w = csv.writer(out)
        w.writerow(TRADE_FIELDS)
        for p in parts:
            if p.name.endswith(".trades.csv"):
                with open(p, newline="") as fh:
                    w.writerows(csv.reader(fh))
    for kind, fields in (("control", CONTROL_FIELDS), ("errors", ERROR_FIELDS), ("coverage", COVERAGE_FIELDS)):
        with open(run_dir / f"{kind}.csv", "w", newline="") as out:
            w = csv.writer(out)
            w.writerow(fields)
            for p in parts:
                if p.name.endswith(f".{kind}.csv"):
                    with open(p, newline="") as fh:
                        w.writerows(csv.reader(fh))


def positive_cells(run_dir: Path, ids) -> Dict[str, List[str]]:
    """Real-data cells with net > 0 over the whole period, eligible for the week shuffle: symbol -> ids."""
    net = defaultdict(float)
    with gzip.open(Path(run_dir) / "trades.csv.gz", "rt") as fh:
        for row in csv.DictReader(fh):
            if row["variant"] == "real" and row["strategy"] in ids:
                net[(row["strategy"], row["symbol"])] += float(row["net"])
    out = defaultdict(list)
    for (s, sym), v in sorted(net.items()):
        if v > 0 and _job_strategies(sym, "shuffle:0", [s]):
            out[sym].append(s)
    return dict(out)


def _weight(symbol: str) -> int:
    inst = instrument(symbol)
    legs = inst.cross[:2] if inst.synthetic else (symbol,)
    return sum(f.stat().st_size for s in legs for f in (DATA_DIR / s / "t1").glob("*.zticks"))


def _provenance() -> dict:
    root = Path(__file__).resolve().parents[2]
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=root).stdout.strip()
    h = hashlib.sha256()
    for f in sorted(Path(__file__).parent.rglob("*.py")):
        h.update(f.read_bytes())
    return dict(git=head, lab_sha=h.hexdigest()[:12], catalog=catalog_hash())


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategies", nargs="*")
    ap.add_argument("--symbols", nargs="*", default=list(ALL))
    ap.add_argument("--variants", nargs="*", default=["real", "mirror"])
    ap.add_argument("--years", nargs="*", type=int, default=list(YEARS))
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--run-dir")
    ap.add_argument("--shuffle", type=int, default=0)
    ap.add_argument("--into")
    args = ap.parse_args(argv)
    ids = args.strategies or runnable_ids()
    if args.shuffle:
        run_dir = Path(args.into)
        jobs = [(sym, f"shuffle:{k}", sids) for sym, sids in positive_cells(run_dir, ids).items()
                for k in range(args.shuffle)]
    else:
        run_dir = Path(args.run_dir) if args.run_dir else RESULTS / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
        jobs = [(sym, v, _job_strategies(sym, v, ids)) for sym in args.symbols for v in args.variants]
    jobs = sorted((j for j in jobs if j[2]), key=lambda j: -_weight(j[0]))
    run_dir.mkdir(parents=True, exist_ok=True)
    meta_path = run_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"runs": []}
    meta["runs"].append(dict(argv=vars(args), jobs=len(jobs), started=datetime.now(timezone.utc).isoformat(),
                             **_provenance()))
    meta_path.write_text(json.dumps(meta, indent=1))
    print(f"{run_dir}: {len(jobs)} jobs", flush=True)
    with ProcessPoolExecutor(args.workers) as ex:
        futures = [ex.submit(run_job, sym, v, sids, args.years, args.seeds, str(run_dir)) for sym, v, sids in jobs]
        for f in as_completed(futures):
            print(json.dumps(f.result()), flush=True)
    merge(run_dir)
    meta["runs"][-1]["finished"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, indent=1))
    print(run_dir)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_run.py -q`
Expected: 2 passed.

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 17: Report

**Files:**
- Create: `research/lab/report.py`
- Test: `research/tests/lab/test_lab_report.py`

**Interfaces:**
- Consumes: `RUN_DIR/trades.csv.gz` (TRADE_FIELDS), `control.csv`, `errors.csv`, `meta.json`; `feed.YEARS`.
- Produces: `report.stats(rows) -> dict`, `report.build(run_dir) -> List[dict]` (cells, keys `CELL_FIELDS`), `report.write(run_dir, cells)` → `cells.csv`, `matrix.csv`, `report.md`; `report.main(argv)`.

- [ ] **Step 1: Write the failing tests** (`research/tests/lab/test_lab_report.py`)

```python
import csv
import gzip
from datetime import datetime, timezone

import pytest

np = pytest.importorskip("numpy")

from research.lab.report import build, write  # noqa: E402
from research.lab.run import CONTROL_FIELDS, TRADE_FIELDS  # noqa: E402


def _ms(y, m):
    return int(datetime(y, m, 15, tzinfo=timezone.utc).timestamp() * 1000)


def _write_run(tmp):
    rows = []

    def tr(s, sym, v, y, t_out, net):
        rows.append([s, sym, v, y, 1, t_out - 1000, t_out, 1, 1, 1, 1, "nan", net, 0, 0, net, 100, net / 100, "time"])

    tr("A", "EURUSD", "real", 2023, _ms(2023, 3), 100.0)
    tr("A", "EURUSD", "real", 2023, _ms(2023, 4), -30.0)
    tr("A", "EURUSD", "real", 2024, _ms(2024, 5), 50.0)
    tr("A", "EURUSD", "mirror", 2023, _ms(2023, 3), 10.0)
    for k in range(20):
        tr("A", "EURUSD", f"shuffle:{k}", 2023, _ms(2023, 3), float(k) - 10)
    tr("B", "EURUSD", "real", 2023, _ms(2023, 3), -20000.0)
    with gzip.open(tmp / "trades.csv.gz", "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(TRADE_FIELDS)
        w.writerows(rows)
    with open(tmp / "control.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CONTROL_FIELDS)
        w.writerows(["A", "EURUSD", 2023, k, 3, k - 30.0, 0, 0] for k in range(20))
    return tmp


def test_cell_statistics_and_flags(tmp_path):
    cells = {(c["strategy"], c["symbol"]): c for c in build(_write_run(tmp_path))}
    a = cells[("A", "EURUSD")]
    assert a["n"] == 3 and a["net"] == pytest.approx(120.0) and a["max_dd"] == pytest.approx(30.0)
    assert a["worst_month"] == pytest.approx(-30.0) and a["pf"] == pytest.approx(5.0)
    assert a["net_2023"] == pytest.approx(70.0) and a["net_2024"] == pytest.approx(50.0) and a["n_2025"] == 0
    assert a["pos_every_year"] and a["control_pct"] == 100.0 and a["beats_control"]
    assert a["shuffles"] == 20 and a["shuffle_ok"] and a["mirror_ok"] and a["all_flags"]
    b = cells[("B", "EURUSD")]
    assert b["blown"] == "2023-03-15" and not b["pos_every_year"] and not b["beats_control"] and not b["all_flags"]


def test_report_files(tmp_path):
    run = _write_run(tmp_path)
    write(run, build(run))
    assert (run / "cells.csv").exists() and (run / "matrix.csv").exists()
    md = (run / "report.md").read_text()
    assert "| A | EURUSD |" in md and "Cells with all four flags: 1" in md
```

- [ ] **Step 2: Run to see it fail**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_report.py -q`
Expected: FAIL, `No module named 'research.lab.report'`.

- [ ] **Step 3: Implement `research/lab/report.py`**

```python
"""Tables from a lab run.   python -m research.lab.report RUN_DIR   ->   cells.csv, matrix.csv, report.md

A cell is (strategy, symbol) on real data. Per cell: trades, net $, gross, commission, swap, PF, win rate,
mean R and its t, max drawdown, worst month, share of positive months, the date a $10k account would have
reached zero ("blown"), net and trades per year, and the stress tests: mirror net, and the percentile of the real
net among the random-control seeds and among the week-shuffle seeds. Flags: E = positive in every year that had
trades (at least two such years), C = above >= 95 % of the control seeds, S = above >= 95 % of the shuffle seeds
(shuffled cells only), M = mirror net > 0 (mirrored cells only)."""
import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from research.lab.feed import YEARS

START = 10_000.0
NAN = float("nan")
CELL_FIELDS = (["strategy", "symbol", "n", "net", "gross", "comm", "swap", "pf", "win", "mean_r", "t_r", "max_dd",
                "worst_month", "months_pos", "blown"] + [f"net_{y}" for y in YEARS] + [f"n_{y}" for y in YEARS]
               + ["mirror_net", "control_pct", "shuffle_pct", "shuffles", "pos_every_year", "beats_control",
                  "shuffle_ok", "mirror_ok", "all_flags"])
FLAGS = (("E", "pos_every_year"), ("C", "beats_control"), ("S", "shuffle_ok"), ("M", "mirror_ok"))


def _month(ms) -> int:
    d = datetime.fromtimestamp(int(ms) / 1000, timezone.utc)
    return d.year * 100 + d.month


def stats(rows) -> dict:
    if not rows:
        return dict(n=0, net=0.0, gross=0.0, comm=0.0, swap=0.0, pf=NAN, win=NAN, mean_r=NAN, t_r=NAN, max_dd=0.0,
                    worst_month=0.0, months_pos=NAN, blown="")
    rows = sorted(rows, key=lambda r: int(r["t_out"]))
    net = np.array([float(r["net"]) for r in rows])
    rr = np.array([float(r["r"]) for r in rows])
    rr = rr[np.isfinite(rr)]
    cum = np.cumsum(net)
    dd = float(np.max(np.maximum.accumulate(np.r_[0.0, cum]) - np.r_[0.0, cum]))
    months = defaultdict(float)
    for r, v in zip(rows, net):
        months[_month(r["t_out"])] += v
    mv = np.array(list(months.values()))
    below = np.flatnonzero(START + cum <= 0)
    wins, losses = float(net[net > 0].sum()), float(-net[net < 0].sum())
    sd = float(rr.std(ddof=1)) if len(rr) > 1 else 0.0
    return dict(n=len(net), net=float(net.sum()), gross=sum(float(r["gross"]) for r in rows),
                comm=sum(float(r["comm"]) for r in rows), swap=sum(float(r["swap"]) for r in rows),
                pf=wins / losses if losses > 0 else math.inf, win=float((net > 0).mean()),
                mean_r=float(rr.mean()) if len(rr) else NAN,
                t_r=float(rr.mean() / (sd / math.sqrt(len(rr)))) if sd > 0 else NAN, max_dd=dd,
                worst_month=float(mv.min()), months_pos=float((mv > 0).mean()),
                blown=(datetime.fromtimestamp(int(rows[below[0]]["t_out"]) / 1000, timezone.utc).date().isoformat()
                       if below.size else ""))


def _pct_below(x: float, sample) -> float:
    return 100.0 * float(np.mean(np.asarray(sample) < x)) if len(sample) else NAN


def build(run) -> list:
    run = Path(run)
    trades = defaultdict(list)
    with gzip.open(run / "trades.csv.gz", "rt") as fh:
        for row in csv.DictReader(fh):
            trades[(row["strategy"], row["symbol"], row["variant"])].append(row)
    control = defaultdict(lambda: defaultdict(float))
    if (run / "control.csv").exists():
        with open(run / "control.csv") as fh:
            for row in csv.DictReader(fh):
                control[(row["strategy"], row["symbol"])][int(row["seed"])] += float(row["net"])
    shuffles, mirrors = defaultdict(list), {}
    for (s, sym, v), rows in trades.items():
        if v.startswith("shuffle:"):
            shuffles[(s, sym)].append(sum(float(r["net"]) for r in rows))
        elif v == "mirror":
            mirrors[(s, sym)] = sum(float(r["net"]) for r in rows)
    cells = []
    for s, sym in sorted({(s, sym) for (s, sym, v) in trades if v == "real"} | set(control)):
        real = trades.get((s, sym, "real"), [])
        full = stats(real)
        years = {y: stats([r for r in real if int(r["year"]) == y]) for y in YEARS}
        ctrl, shuf = list(control[(s, sym)].values()), shuffles.get((s, sym), [])
        cell = dict(strategy=s, symbol=sym, **full, **{f"net_{y}": years[y]["net"] for y in YEARS},
                    **{f"n_{y}": years[y]["n"] for y in YEARS}, mirror_net=mirrors.get((s, sym), NAN),
                    control_pct=_pct_below(full["net"], ctrl), shuffle_pct=_pct_below(full["net"], shuf),
                    shuffles=len(shuf))
        with_trades = [y for y in YEARS if years[y]["n"] > 0]
        cell["pos_every_year"] = len(with_trades) >= 2 and all(years[y]["net"] > 0 for y in with_trades)
        cell["beats_control"] = bool(ctrl) and cell["control_pct"] >= 95.0
        cell["shuffle_ok"] = bool(shuf) and cell["shuffle_pct"] >= 95.0
        cell["mirror_ok"] = math.isfinite(cell["mirror_net"]) and cell["mirror_net"] > 0
        cell["all_flags"] = all(cell[k] for _, k in FLAGS)
        cells.append(cell)
    return cells


def _fmt(v):
    if isinstance(v, float):
        return "" if math.isnan(v) else f"{v:.4f}"
    return v


def _markdown(run: Path, cells: list) -> str:
    meta = json.loads((run / "meta.json").read_text()) if (run / "meta.json").exists() else {"runs": [{}]}
    errors = sum(1 for _ in csv.reader(open(run / "errors.csv"))) - 1 if (run / "errors.csv").exists() else 0
    ys = " | ".join(str(y) for y in YEARS)
    L = [f"# Strategy lab run {run.name}", "",
         f"$10k account, fixed lots, no loss limits, one position per strategy x symbol, ticks {YEARS[0]}-{YEARS[-1]}. "
         f"Cells: {len(cells)}; strategy errors: {errors}; catalog {meta['runs'][-1].get('catalog', '?')}, "
         f"lab code {meta['runs'][-1].get('lab_sha', '?')}.", "",
         "Flags: E = positive in every year with trades (>= 2 years), C = above >= 95 % of 20 random-entry seeds, "
         "S = above >= 95 % of the week-shuffle seeds, M = mirror net > 0. Long-only rules (TOM, OD1) cannot pass M "
         "by construction.", "",
         "## Strategies (real data, summed over symbols)", "",
         f"| strategy | {ys} | total $ | cells + | E | C | all |", "|---|" + "---|" * (len(YEARS) + 5)]
    by = defaultdict(list)
    for c in cells:
        by[c["strategy"]].append(c)
    for s, cs in sorted(by.items(), key=lambda kv: -sum(c["net"] for c in kv[1])):
        L.append(f"| {s} | " + " | ".join(f"{sum(c[f'net_{y}'] for c in cs):+,.0f}" for y in YEARS)
                 + f" | {sum(c['net'] for c in cs):+,.0f} | {sum(c['net'] > 0 for c in cs)}/{len(cs)} | "
                 f"{sum(c['pos_every_year'] for c in cs)} | {sum(c['beats_control'] for c in cs)} | "
                 f"{sum(c['all_flags'] for c in cs)} |")
    L += ["", "## Top 30 cells by net $", "",
          f"| strategy | symbol | n | net $ | {ys} | PF | mean R | max DD $ | worst month $ | blown | mirror $ | "
          "ctrl pct | shuf pct | flags |", "|---|---|---|---|" + "---|" * (len(YEARS) + 9)]
    for c in sorted(cells, key=lambda c: -c["net"])[:30]:
        flags = "".join(f for f, k in FLAGS if c[k]) or "-"
        L.append(f"| {c['strategy']} | {c['symbol']} | {c['n']} | {c['net']:+,.0f} | "
                 + " | ".join(f"{c[f'net_{y}']:+,.0f}" for y in YEARS)
                 + f" | {c['pf']:.2f} | {c['mean_r']:+.3f} | {c['max_dd']:,.0f} | {c['worst_month']:+,.0f} | "
                 f"{c['blown'] or '-'} | {c['mirror_net']:+,.0f} | {c['control_pct']:.0f} | {c['shuffle_pct']:.0f} | "
                 f"{flags} |")
    passing = [c for c in cells if c["all_flags"]]
    L += ["", f"## Cells with all four flags: {len(passing)}", ""]
    L += [f"- {c['strategy']} on {c['symbol']}: net {c['net']:+,.0f} $, PF {c['pf']:.2f}, max DD {c['max_dd']:,.0f} $"
          for c in passing] or ["- none"]
    L += ["", "Full tables: cells.csv (every cell), matrix.csv (strategy x symbol net $)."]
    return "\n".join(L)


def write(run, cells: list) -> None:
    run = Path(run)
    with open(run / "cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, CELL_FIELDS)
        w.writeheader()
        w.writerows({k: _fmt(c[k]) for k in CELL_FIELDS} for c in cells)
    symbols = sorted({c["symbol"] for c in cells})
    net = {(c["strategy"], c["symbol"]): c["net"] for c in cells}
    with open(run / "matrix.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["strategy"] + symbols + ["total"])
        for s in sorted({c["strategy"] for c in cells}):
            row = [net.get((s, y), NAN) for y in symbols]
            w.writerow([s] + [_fmt(v) for v in row] + [_fmt(float(np.nansum(row)))])
    (run / "report.md").write_text(_markdown(run, cells))


def main(argv=None) -> None:
    run = Path((sys.argv[1:] if argv is None else argv)[0])
    write(run, build(run))
    print(run / "report.md")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests**

Run: `research/.venv/bin/python -m pytest research/tests/lab/test_lab_report.py -q`
Expected: 2 passed.

- [ ] **Step 5: Whole research suite green; leave the files in the working tree (no commit)**

---

### Task 18: Full run, report, catalog and hand-over

Long-running. Run the heavy commands in the background (Bash `run_in_background`) and check back on a long
interval; never poll in a tight loop.

**Files:**
- Output: `research/results/lab/<run>/` (git-ignored), `research/STRATEGIES.md`
- Memory: `/Users/hoangbk/.claude/projects/-Users-hoangbk-00-code-base-105-AgentFxTrading/memory/strategy-lab.md` + a line in `MEMORY.md`

- [ ] **Step 1: Preconditions**

Task 1's coverage check passed (all 15 symbols have 2023-01..2026-09 ticks and a rebuilt M1 cache) and
`research/.venv/bin/python -m pytest research/tests -q` is green. If Task 1 is still running, wait for it.

- [ ] **Step 2: Smoke run and timing**

Run: `research/.venv/bin/python -m research.lab.run --strategies BTC-S1 FLOWRSI JUDAS TMSORB K1 TOM WF1 --symbols EURUSD US30 EURGBP BTCUSD --years 2025 --seeds 2 --workers 3 --run-dir research/results/lab/smoke && research/.venv/bin/python -m research.lab.report research/results/lab/smoke`
Expected: one JSON line per job with `"errors": 0`, then the report path. Read `smoke/errors.csv` (must be
header-only) and `smoke/report.md`. From the job `seconds`, estimate the full run:
full ≈ Σ(job seconds) × (4 years) × (68 runnable strategies / 7) × (22 symbols / 4) × 1.7 (mirror on 15 of 22)
÷ 3 workers, plus the 20 control seeds (already in the smoke's seed=2 cost × 10). Tell the user the estimate
before starting the full run.

- [ ] **Step 3: Full main run (background)**

Run (background): `research/.venv/bin/python -m research.lab.run --workers 3 --run-dir research/results/lab/main > research/results/lab/main.log 2>&1`
Check back every 30–60 minutes (`tail -5 research/results/lab/main.log`). When it ends: `wc -l research/results/lab/main/errors.csv`
must be 1 (header only); otherwise read the tracebacks, fix the strategy, and rerun only the affected symbols with
`--run-dir research/results/lab/main --symbols ... --variants ...` (same (symbol, variant) part files are rewritten
completely, so the rerun must include every strategy of those jobs, i.e. no `--strategies` filter).

- [ ] **Step 4: Report on the main run**

Run: `research/.venv/bin/python -m research.lab.report research/results/lab/main`
Read `report.md`; sanity checks before going on:
- the FLOWRSI cells are negative in $ on most symbols (earlier finding: every pair negative) — if not, stop and
  investigate the adapter;
- BTC-S1 on BTCUSD per year has the sign pattern of the confirmation (≈0 in 2023, positive 2024–2026);
- control nets are mostly negative (cost drag); coverage.csv shows `ok` for every real symbol-year.

- [ ] **Step 5: Week-shuffle phase (background)**

Run (background): `research/.venv/bin/python -m research.lab.run --shuffle 20 --into research/results/lab/main --workers 3 > research/results/lab/shuffle.log 2>&1`
Then: `research/.venv/bin/python -m research.lab.report research/results/lab/main`

- [ ] **Step 6: Render the catalog with the results**

Run: `research/.venv/bin/python -m research.lab.catalog research/results/lab/main`
Expected: `research/STRATEGIES.md` with the lab columns filled.

- [ ] **Step 7: Save the memory note**

Write `strategy-lab.md` (type project): where the catalog and the runner live, how to add a strategy (entry in
`research/lab/catalog.py`, function in `research/lab/strategies/`, then `python -m research.lab.run --strategies
NEW_ID` + report + catalog render), the account rules, the main run's headline (which cells, if any, passed all
four flags; totals by strategy), and that nothing is committed. Add its line to `MEMORY.md`.

- [ ] **Step 8: Hand over to the user (Vietnamese)**

Send `research/results/lab/main/report.md` and `research/STRATEGIES.md` with SendUserFile, and summarise in
chat: totals per strategy, the cells that pass E/C/S/M, what the live bots' ports show, the caveats (ports
uncalibrated; swaps before 2026 approximate; synthetic crosses; D1 timing), and that nothing was committed. Ask
whether to commit `research/lab/` (on a branch; main is push-protected, the user opens PRs).
