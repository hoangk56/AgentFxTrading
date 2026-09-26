import pytest

np = pytest.importorskip("numpy")

from research.lab.cbot import cbot_defaults, cbot_params  # noqa: E402
from research.lab.universe import ALL, FIXED_UNITS, SYNTHETIC, instrument  # noqa: E402
from research.specs import SWAPS  # noqa: E402


def test_every_symbol_has_an_instrument_with_fixed_units():
    assert len(ALL) == 22 and len(SYNTHETIC) == 7
    for s in ALL:
        assert instrument(s).units == FIXED_UNITS[s] > 0


def test_fixed_units_follow_the_spec_table():
    assert FIXED_UNITS["EURUSD"] == FIXED_UNITS["EURGBP"] == FIXED_UNITS["CADJPY"] == 10_000
    assert (FIXED_UNITS["XAUUSD"], FIXED_UNITS["BTCUSD"], FIXED_UNITS["ETHUSD"]) == (2, 0.1, 4)
    assert (FIXED_UNITS["US30"], FIXED_UNITS["USTEC"], FIXED_UNITS["DE40"], FIXED_UNITS["UK100"]) == (0.2, 0.4, 0.4, 0.8)


def test_synthetic_cross_contract_data():
    eg = instrument("EURGBP")
    assert eg.synthetic and eg.cross == ("EURUSD", "GBPUSD", "div") and eg.quote_ccy == "GBP"
    assert eg.pip == 0.0001 and eg.comm_per_unit == pytest.approx(6.96e-5)
    cj = instrument("CADJPY")
    assert cj.pip == 0.01 and cj.tick_size == 0.001 and cj.quote_ccy == "JPY"
    assert not instrument("EURUSD").synthetic


def test_synthetic_swaps_are_the_legs_weighted_by_exposure():
    ec = instrument("EURCAD")          # long EURCAD = long 1 EURUSD + long 1.16 USDCAD
    assert ec.swap_long == pytest.approx(SWAPS["EURUSD"][0] + 1.16 * SWAPS["USDCAD"][0])
    assert ec.swap_short == pytest.approx(SWAPS["EURUSD"][1] + 1.16 * SWAPS["USDCAD"][1])
    eg = instrument("EURGBP")          # long EURGBP = long 1 EURUSD + short 0.865 GBPUSD
    assert eg.swap_long == pytest.approx(SWAPS["EURUSD"][0] + 0.865 * SWAPS["GBPUSD"][1])


def test_mirrored_instrument_exchanges_the_swap_sides():
    x = instrument("XAUUSD")
    m = x.mirrored()
    assert (m.swap_long, m.swap_short) == (x.swap_short, x.swap_long)


def test_spec_for_the_flowrsi_simulator():
    assert instrument("EURUSD").spec().usd_per_quote == 1.0
    s = instrument("CADJPY").spec()
    assert s.min_units == 1000 and s.usd_per_quote == pytest.approx(1 / 154.8)


def test_cbot_defaults_parse_all_three_bots():
    j = cbot_defaults("judas")
    assert (j["asianStartHour"], j["asianEndHour"], j["dstRule"]) == (0, 6, "Auto")
    assert j["requireRejectionWick"] is True and j["minRejectionWickRatio"] == 0.35
    assert j["breakEvenMode"] == "Risk_Reward_Ratio"
    t = cbot_defaults("tms_orb")
    assert t["TmsTimeFrame"] == "Hour" and t["SessionDstRule"] == "US" and t["MaxBarsAfterBreakout"] == 8
    assert cbot_defaults("flowrsi")["AtrPeriod"] == 14


def test_cbot_params_layer_defaults_preset_template_and_overrides():
    p = cbot_params("judas", "EURGBP")                 # synthetic cross -> EURUSD preset
    assert (p["stoplossPip"], p["takeprofitPip"], p["asianEndHour"]) == (15.0, 35.0, 6)
    assert cbot_params("tms_orb", "USTEC")["OrbStartMinute"] == 30
    assert cbot_params("judas", "XAUUSD", stoplossPip=1.0)["stoplossPip"] == 1.0
