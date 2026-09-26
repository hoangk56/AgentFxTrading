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
    then `after` = [(minute from 07:00 UTC, bid), ...] with the bid held until the next change."""
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
