from collections import Counter
from datetime import date, datetime, timezone

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk, needs_ticks  # noqa: E402
from research.lab.cbot import cbot_params  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk  # noqa: E402
from research.lab.strategies import tmsorb as tm  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.ticks import day_ms, load_ticks  # noqa: E402

T0 = day_ms(date(2025, 7, 1)) + 9 * 3_600_000


def _hold(bid, sl, tp=1.1100, eod_ms=None, atr=10.0):
    ts = T0 + np.arange(len(bid)) * 1000
    ctx = Ctx(make_chunk(ts, bid, spread=0.0002), "TMSORB")
    pos = ctx.open(0, 1)                                         # ask 1.1000 when bid[0] = 1.0998
    pos.sl = pos.sl0 = sl
    pos.tp = pos.tp0 = tp
    hd = tm.Hold(pos, 1, atr, eod_ms or int(ts[-1]) + 10**9, (pos.entry - sl) / 0.0001)
    return ctx, hd


def test_break_even_moves_the_stop_and_closes_half():
    ctx, hd = _hold([1.0998, 1.1005, 1.1013, 1.1008, 1.1000], sl=1.0980)
    p = cbot_params("tms_orb", "EURUSD")                         # BE at 1.2 ATR = 12 pips, offset 1 pip
    assert tm.run_ticks(ctx, hd, 5, p) == "sl"
    assert [(j, round(px, 4), u, why) for j, px, u, why in hd.pos.deals] == [(2, 1.1013, 5000.0, "partial"),
                                                                            (4, 1.1000, 5000.0, "sl")]
    assert ctx.trades[0].units == 10_000


def test_giveback_lock_closes_after_45_percent_of_the_peak():
    ctx, hd = _hold([1.0998, 1.1012, 1.1030, 1.1020, 1.1015, 1.1010], sl=1.0970)
    p = cbot_params("tms_orb", "EURUSD", TrailTriggerAtr=0.0, Tier2TriggerAtr=0.0, MaxGivebackAtr=0.0)
    assert tm.run_ticks(ctx, hd, 6, p) == "giveback"
    assert hd.pos.deals[-1][0] == 4                              # pnl 15 after a 30-pip peak: 15 >= 13.5


def test_session_end_flattens():
    ctx, hd = _hold([1.0998, 1.1001, 1.1002, 1.1001, 1.1002], sl=1.0980, eod_ms=T0 + 3000)
    assert tm.run_ticks(ctx, hd, 5, cbot_params("tms_orb", "EURUSD")) == "eod"
    assert hd.pos.deals[-1][0] == 3


def test_run_ticks_stops_at_end_without_closing():
    ctx, hd = _hold([1.0998, 1.1001, 1.1002, 1.1001, 1.1002], sl=1.0980)
    assert tm.run_ticks(ctx, hd, 3, cbot_params("tms_orb", "EURUSD")) is None
    assert hd.cur == 3 and not ctx.trades


@needs_ticks
def test_tms_orb_smoke_on_usdjpy_june_2025():
    t = load_ticks("USDJPY", date(2025, 5, 12), date(2025, 6, 30))
    ch = Chunk("USDJPY", "real", 2025, t, day_ms(date(2025, 6, 2)), day_ms(date(2025, 6, 28)), instrument("USDJPY"))
    ctx = Ctx(ch, "TMSORB")
    tm.tms_orb(ctx)
    allowed = {"sl", "tp", "giveback", "giveback_atr", "eod", "ai_close", "bias_flip", "tail"}
    print(len(ctx.trades), Counter(tr.why for tr in ctx.trades))
    for tr in ctx.trades:
        hour = datetime.fromtimestamp(tr.t_in / 1000, timezone.utc).hour
        assert 0 <= hour < 9 and tr.why in allowed and np.isfinite(tr.sl0)
        assert tr.t_out <= day_ms(date(2025, 6, 30)) + 86_400_000
