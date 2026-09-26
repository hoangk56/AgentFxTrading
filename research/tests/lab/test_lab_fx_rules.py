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
