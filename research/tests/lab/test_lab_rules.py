from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import bar_ticks, make_chunk, needs_ticks  # noqa: E402
from research.lab.engine import Ctx  # noqa: E402
from research.lab.feed import Chunk  # noqa: E402
from research.lab.strategies import rules  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.ticks import day_ms, load_ticks  # noqa: E402

T0 = day_ms(date(2025, 3, 10))
QUIET, SHOCK = (1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1045, 1.0995, 1.1040)
AFTER = (1.1040, 1.1045, 1.1035, 1.1040)


def _shock_chunk():
    ts, px = bar_ticks(T0, 15, [QUIET] * 30 + [SHOCK] + [AFTER] * 20)
    return make_chunk(ts, px, spread=0.0002)


def test_parse_bank_names():
    assert rules.parse_bank("zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0") == dict(
        kind="zmove", mode=1, tf="D1", L=3, Z=3.0, H=3, SLK=1.0, TPK=1.0)
    assert rules.parse_bank("donchR_H4_N55_H24_SL2.5_TPNone") == dict(
        kind="donch", mode=-1, tf="H4", N=55, H=24, SLK=2.5, TPK=None)
    assert rules.parse_bank("rsiF_H1_P14_lo20_H12_SL2.0_TPNone") == dict(
        kind="rsi", mode=1, tf="H1", P=14, lo=20.0, H=12, SLK=2.0, TPK=None)


def test_bank_configs_cover_every_kind_direction_and_timeframe_once():
    keys = {(k["kind"], k["mode"], k["tf"]) for k in map(rules.parse_bank, rules.BANK_CONFIGS)}
    assert len(rules.BANK_CONFIGS) == len(keys) == 24


def test_shock_follow_buys_the_next_tick_with_atr_stop_and_target():
    ctx = Ctx(_shock_chunk(), "BTC-S1")
    rules.shock_follow(ctx)
    (tr,) = ctx.trades
    atr = (19 * 0.0010 + 0.0050) / 20
    assert tr.side == 1 and tr.t_in == T0 + 31 * 900_000
    assert tr.entry - tr.sl0 == pytest.approx(2 * atr) and tr.tp0 - tr.entry == pytest.approx(2 * atr)
    assert tr.why == "time" and tr.t_out == T0 + 43 * 900_000


def test_bank_donchian_follow_enters_on_the_first_close_beyond_the_range():
    ctx = Ctx(_shock_chunk(), "BANK")
    rules.bank_rule(ctx, kind="donch", mode=1, tf="M15", N=20, H=6, SLK=1.5)
    assert [(tr.side, tr.t_in) for tr in ctx.trades] == [(1, T0 + 31 * 900_000)]
    assert np.isnan(ctx.trades[0].tp0)


@needs_ticks
def test_btc_s1_matches_ticksim_with_fixed_units():
    from research.scan.ticksim import run as tick_run
    ref, _, _ = tick_run("BTCUSD", date(2025, 3, 1), date(2025, 4, 30), fixed_units=0.1)
    t = load_ticks("BTCUSD", date(2025, 2, 26), date(2025, 4, 30))
    ch = Chunk("BTCUSD", "real", 2025, t, day_ms(date(2025, 3, 1)), day_ms(date(2025, 5, 1)), instrument("BTCUSD"))
    ctx = Ctx(ch, "BTC-S1")
    rules.shock_follow(ctx)
    assert len(ref) > 10
    assert [(p.t_in, p.side) for p in ref] == [(tr.t_in, tr.side) for tr in ctx.trades]
    assert [p.net for p in ref] == pytest.approx([tr.net for tr in ctx.trades], abs=1e-6)
