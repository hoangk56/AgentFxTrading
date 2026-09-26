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
    prices = [1.1005] * 60 + [1.1000, 1.1010] * 7 + [1.1005] * 16 + [1.1015] * 600
    ts = [T0 + (6 * 60 + k) * MIN for k in range(len(prices))]
    ctx = Ctx(make_chunk(ts, prices, spread=0.0002, symbol="EURUSD"), "T1-ORB")
    orb(ctx)
    (tr,) = ctx.trades
    assert tr.side == 1 and tr.t_in == T0 + 7 * HOUR + 30 * MIN and tr.sl0 == pytest.approx(1.1000)
    assert tr.why == "time" and tr.t_out == T0 + 15 * HOUR + 30 * MIN
