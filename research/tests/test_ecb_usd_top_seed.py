import datetime as dt

import numpy as np

from research.tools import ecb_usd_top_seed as seed

MIN = 60_000


def _utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def test_selector_minutes_follow_london_and_new_york_daylight_saving():
    # 2026-03-09..13: New York on EDT (from 8 March), London still on GMT (until 29 March)
    mins = [_utc(x) for x in seed.selector_minutes(dt.date(2026, 3, 9), dt.date(2026, 3, 9))]
    assert mins == ["2026-03-09 07:00", "2026-03-09 22:00"]
    mins = [_utc(x) for x in seed.selector_minutes(dt.date(2026, 7, 1), dt.date(2026, 7, 1))]
    assert mins == ["2026-07-01 06:00", "2026-07-01 22:00"]
    mins = [_utc(x) for x in seed.selector_minutes(dt.date(2026, 1, 5), dt.date(2026, 1, 5))]
    assert mins == ["2026-01-05 07:00", "2026-01-05 23:00"]
    # weekends have no selector minute
    assert seed.selector_minutes(dt.date(2026, 10, 17), dt.date(2026, 10, 18)) == []


def test_quote_is_the_last_bar_up_to_ten_bars_before_the_one_ending_at_x():
    x = 1_000 * MIN
    ts = np.array([x - 11 * MIN, x - 3 * MIN, x], dtype=np.int64)
    bid, ask = np.array([1.0, 2.0, 3.0]), np.array([1.1, 2.1, 3.1])
    assert seed.quote_at(ts, bid, ask, x) == (2.0, 2.1)                 # the bar starting at x is after x
    assert seed.quote_at(ts[:1], bid[:1], ask[:1], x) == (1.0, 1.1)     # 10 bars before the bar labelled x - 1 min
    assert seed.quote_at(ts[:1], bid[:1], ask[:1], x + MIN) is None     # 11 bars before: stale
    assert seed.quote_at(ts[:1], bid[:1], ask[:1], x - 11 * MIN) is None
