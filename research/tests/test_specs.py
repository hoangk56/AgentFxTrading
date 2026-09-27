import pytest

np = pytest.importorskip("numpy")

from research.specs import SPECS  # noqa: E402


def test_all_fifteen_pairs_have_specs():
    assert len(SPECS) == 15
    assert SPECS["USDJPY"].pip_value == pytest.approx(0.01 * 0.0062963)


from research.specs import SWAPS, rollovers, swap_usd  # noqa: E402

NY_MS = {  # 2026-01-06 is a Tuesday; New York is UTC-5 in January
    "tue_16": 1767733200000,   # Tue 2026-01-06 16:00 NY
    "thu_18": 1767913200000,   # Thu 2026-01-08 18:00 NY
    "fri_16": 1767992400000,   # Fri 2026-01-09 16:00 NY
    "mon_16": 1768251600000,   # Mon 2026-01-12 16:00 NY
}


def test_rollovers_count_the_triple_day_three_times():
    assert rollovers(NY_MS["tue_16"], NY_MS["thu_18"], triple_weekday=2) == 1 + 3 + 1   # Tue, Wed x3, Thu
    assert rollovers(NY_MS["tue_16"], NY_MS["tue_16"] + 3_600_000, triple_weekday=2) == 1
    assert rollovers(NY_MS["tue_16"], NY_MS["tue_16"] + 1_800_000, triple_weekday=2) == 0


def test_weekend_has_no_rollover_but_friday_can_be_triple():
    assert rollovers(NY_MS["fri_16"], NY_MS["mon_16"], triple_weekday=4) == 3
    assert rollovers(NY_MS["fri_16"], NY_MS["mon_16"], triple_weekday=2) == 1


def test_swap_usd_uses_the_side_rate():
    long_rate, short_rate, triple = SWAPS["AUDJPY"]
    assert swap_usd("AUDJPY", 1, 10000, NY_MS["tue_16"], NY_MS["thu_18"]) == pytest.approx(5 * long_rate * 10000)
    assert swap_usd("AUDJPY", -1, 10000, NY_MS["tue_16"], NY_MS["thu_18"]) == pytest.approx(5 * short_rate * 10000)
    assert triple == 2
