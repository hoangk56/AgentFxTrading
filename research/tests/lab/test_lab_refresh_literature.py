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
    t0 = day_ms(date(2025, 7, 1))
    day = [tr for tr in ctx.trades if tr.t_in >= t0][:2]
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
