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
    src = (ROOT / "app" / "trade_gates.py").read_text()
    for pair in ("100.0, 10000.0", "15.0, 200.0", "10000.0, 400000.0", "800.0, 35000.0", "120.0, 800.0",
                 "50.0, 4000.0", "12.0, 100.0"):
        assert f"min_asian_pips, max_asian_pips = {pair}" in src
