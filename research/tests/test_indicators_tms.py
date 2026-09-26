import pytest

np = pytest.importorskip("numpy")

from research.indicators import heikin_ashi, rsi, sma, stoch, tdi  # noqa: E402


def test_heikin_ashi_open_is_the_mean_of_the_previous_ha_bar():
    o, h = np.array([10.0, 11.0, 12.0]), np.array([12.0, 13.0, 14.0])
    l, c = np.array([9.0, 10.0, 11.0]), np.array([11.0, 12.0, 13.0])
    ho, hc = heikin_ashi(o, h, l, c)
    assert hc.tolist() == [10.5, 11.5, 12.5]
    assert ho.tolist() == [10.5, 10.5, 11.0]


def test_tdi_is_sma2_and_sma7_of_rsi13():
    c = 100 + np.cumsum(np.sin(np.arange(60.0)))
    green, red = tdi(c)
    x = rsi(c, 13)
    assert np.allclose(green[1:], sma(x, 2)[1:]) and np.allclose(red[6:], sma(x, 7)[6:])
    assert np.isnan(red[5])


def test_stoch_slow_k_and_d_in_a_steady_uptrend():
    c = np.arange(1.0, 21.0)
    k, d = stoch(c + 1, c - 1, c)
    assert np.isnan(k[8]) and k[9] == pytest.approx(800 / 9)
    assert np.isnan(d[10]) and d[11] == pytest.approx(800 / 9)


def test_stoch_is_nan_on_a_flat_window():
    c = np.full(15, 5.0)
    k, d = stoch(c, c, c)
    assert np.isnan(k).all() and np.isnan(d).all()
