import pytest

np = pytest.importorskip("numpy")

from lab_helpers import make_chunk  # noqa: E402
from research.lab.control import random_control  # noqa: E402
from research.lab.engine import NAN, Trade  # noqa: E402

T0 = 1_741_600_800_000                        # 2025-03-10 10:00 UTC


def _chunk():
    rng = np.random.default_rng(0)
    n = 2 * 24 * 60                           # two days of minute ticks
    return make_chunk(T0 + np.arange(n) * 60_000, 1.10 + np.cumsum(rng.normal(0, 1e-4, n)))


def _real(n):
    return [Trade("x", "EURUSD", "real", 1, T0, T0 + 3_600_000, 1.1, 1.1, 10_000, 1.098, NAN, 0, 0, 0, 20.0, "time")
            for _ in range(n)]


def test_control_replays_the_trade_shapes_with_random_sides():
    c = random_control(_chunk(), _real(20), seed=1)
    assert len(c) == 20
    assert all(abs(tr.entry - tr.sl0) == pytest.approx(0.002) for tr in c)
    assert all(tr.t_out - tr.t_in <= 3_600_000 + 60_000 for tr in c)
    assert {tr.side for tr in c} == {-1, 1}
    assert all(b.t_in > a.t_out for a, b in zip(c, c[1:]))


def test_control_is_deterministic_per_seed_and_empty_without_trades():
    ch = _chunk()
    a = [(t.t_in, t.side) for t in random_control(ch, _real(5), seed=2)]
    b = [(t.t_in, t.side) for t in random_control(ch, _real(5), seed=2)]
    assert a == b
    assert random_control(ch, [], seed=2) == []
