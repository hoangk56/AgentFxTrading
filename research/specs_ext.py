"""Approximate cost specs for the 11 symbols added to the 26-symbol universe (2026-09-27 portfolio-cap swing
research) that research/specs.py does not calibrate from a live cTrader report.

research/specs.SPECS's 15 entries come from measured cTrader reports; that calibration does not exist for
these 11, so their `comm_per_unit` follows the broker's disclosed schedule instead (2 x $30 per $1M notional
per side for FX and metals, none for indices and energies -- research/lab/universe.COMMISSION_PER_SIDE and
docs/superpowers/specs/2026-09-26-h1-history-data-design.md), and `usd_per_quote` is a single constant (the
2025-09..2026-09 median of the conversion pair), not the day-by-day conversion research/lab/costs.py uses for
the main lab. Swaps are not modelled (SWAPS omits these symbols; research.specs.swap_usd returns 0 for a
symbol it does not know) -- a real but second-order gap given the <=5-day hold this lab enforces (at most a
handful of rollovers per trade). None of this is Symbol.Commission truth; it is a research-only approximation
so the 2016-2026 swing lab can include these symbols at all.
"""
from research.specs import SymbolSpec

_SIDE = 30e-6  # USD per USD notional, one side (research/lab/universe.COMMISSION_PER_SIDE)

EXT_SPECS = {s.symbol: s for s in [
    # FX
    SymbolSpec("NZDUSD", pip=0.0001, tick_size=0.00001, min_units=1000, step_units=1000,
               comm_per_unit=2 * _SIDE * 0.58, usd_per_quote=1.0),
    SymbolSpec("USDCHF", pip=0.0001, tick_size=0.00001, min_units=1000, step_units=1000,
               comm_per_unit=2 * _SIDE * 1.0, usd_per_quote=1.0 / 0.8131),
    # metals (same convention as XAUUSD: 1 unit = 1 oz, quote USD)
    SymbolSpec("XAGUSD", pip=0.001, tick_size=0.001, min_units=1, step_units=1,
               comm_per_unit=2 * _SIDE * 65.3, usd_per_quote=1.0),
    SymbolSpec("XPTUSD", pip=0.01, tick_size=0.01, min_units=1, step_units=1,
               comm_per_unit=2 * _SIDE * 1791.9, usd_per_quote=1.0),
    # energies: spread-only, no commission (design doc)
    SymbolSpec("XTIUSD", pip=0.01, tick_size=0.01, min_units=1, step_units=1, comm_per_unit=0.0, usd_per_quote=1.0),
    SymbolSpec("XBRUSD", pip=0.01, tick_size=0.01, min_units=1, step_units=1, comm_per_unit=0.0, usd_per_quote=1.0),
    SymbolSpec("XNGUSD", pip=0.001, tick_size=0.001, min_units=1, step_units=1, comm_per_unit=0.0, usd_per_quote=1.0),
    # indices: spread-only, no commission; usd_per_quote is irrelevant when comm_per_unit == 0.0
    SymbolSpec("US500", pip=0.1, tick_size=0.1, min_units=0.1, step_units=0.1, comm_per_unit=0.0, usd_per_quote=1.0),
    SymbolSpec("JP225", pip=1.0, tick_size=1.0, min_units=0.1, step_units=0.1, comm_per_unit=0.0,
               usd_per_quote=1.0 / 155.14),
    SymbolSpec("AUS200", pip=0.1, tick_size=0.1, min_units=0.1, step_units=0.1, comm_per_unit=0.0,
               usd_per_quote=0.71639),
    SymbolSpec("HK50", pip=1.0, tick_size=1.0, min_units=0.1, step_units=0.1, comm_per_unit=0.0,
               usd_per_quote=1.0 / 7.80),  # HKD/USD peg, stable since 1983
]}
