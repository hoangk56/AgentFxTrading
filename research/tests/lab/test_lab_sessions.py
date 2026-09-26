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
