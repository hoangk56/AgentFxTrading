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
