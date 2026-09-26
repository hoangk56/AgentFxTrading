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
