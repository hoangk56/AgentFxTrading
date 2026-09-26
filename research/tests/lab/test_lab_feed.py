from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_ticks  # noqa: E402
from research.lab.feed import cross_ticks, load_chunk, mirror  # noqa: E402
from research.ticks import Ticks, day_ms, load_ticks  # noqa: E402


def _t(ts, bid, ask):
    return Ticks(np.asarray(ts, np.int64), np.asarray(bid, float), np.asarray(ask, float))


def test_cross_ticks_mul_and_div_as_of_join():
    a = _t([0, 10, 20], [1.10, 1.11, 1.12], [1.1001, 1.1101, 1.1201])
    b = _t([5, 15], [150.0, 151.0], [150.02, 151.02])
    x = cross_ticks(a, b, "mul")
    assert list(x.ts) == [5, 10, 15, 20]                      # before 5 leg B is unknown
    assert x.bid[0] == pytest.approx(1.10 * 150.0) and x.ask[0] == pytest.approx(1.1001 * 150.02)
    assert x.bid[3] == pytest.approx(1.12 * 151.0)
    d = cross_ticks(a, b, "div")
    assert d.bid[0] == pytest.approx(1.10 / 150.02) and d.ask[0] == pytest.approx(1.1001 / 150.0)


def test_cross_spread_factor_scales_around_the_mid():
    a = _t([0], [1.10], [1.1002])
    b = _t([0], [1.0], [1.0])
    x = cross_ticks(a, b, "mul", spread_factor=0.5)
    assert (x.bid[0] + x.ask[0]) / 2 == pytest.approx(1.1001)
    assert x.ask[0] - x.bid[0] == pytest.approx(0.0001)


def test_mirror_twice_is_the_identity_and_keeps_ask_above_bid():
    t = _t([0, 1], [1.1, 1.2], [1.1002, 1.2003])
    once = mirror(t, 1.21)
    assert np.all(once.ask > once.bid)
    back = mirror(once, 1.21)
    np.testing.assert_allclose(back.bid, t.bid)
    np.testing.assert_allclose(back.ask, t.ask)


@needs_ticks
def test_load_chunk_has_warm_up_and_tail_around_the_year():
    ch = load_chunk("BTCUSD", "real", 2025, warmup_days=3, tail_days=2)
    assert ch.lo_ms == day_ms(date(2025, 1, 1)) and ch.hi_ms == day_ms(date(2026, 1, 1))
    assert ch.t.ts[0] < ch.lo_ms and ch.t.ts[-1] >= ch.hi_ms
    assert load_chunk("BTCUSD", "real", 2019) is None


@needs_ticks
def test_synthetic_eurjpy_tracks_the_real_one():
    a, b = date(2025, 3, 3), date(2025, 3, 7)
    real = load_ticks("EURJPY", a, b)
    syn = cross_ticks(load_ticks("EURUSD", a, b), load_ticks("USDJPY", a, b), "mul")
    k = np.searchsorted(syn.ts, real.ts, "right") - 1
    ok = k >= 0
    rmid = (real.bid[ok] + real.ask[ok]) / 2
    smid = (syn.bid[k[ok]] + syn.ask[k[ok]]) / 2
    assert np.median(np.abs(rmid - smid) / rmid) < 1e-4
