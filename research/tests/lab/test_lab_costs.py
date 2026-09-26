from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import needs_m1  # noqa: E402
from research.lab import costs  # noqa: E402
from research.lab.universe import instrument  # noqa: E402
from research.specs import SPECS  # noqa: E402
from research.ticks import day_ms  # noqa: E402

DAY = costs.DAY_MS


def test_usd_quote_needs_no_conversion():
    assert costs.usd_per_quote("USD", 0) == 1.0


def test_conversion_uses_the_previous_days_close(monkeypatch):
    days, px = np.array([100, 101, 102]), np.array([150.0, 160.0, 170.0])
    monkeypatch.setattr(costs, "daily_closes", lambda pair: (days, px))
    ms = 102 * DAY + 5
    assert costs.usd_per_quote("JPY", ms) == pytest.approx(1 / 160.0)      # USDJPY: 1 / price
    assert costs.usd_per_quote("EUR", ms) == pytest.approx(160.0)          # EURUSD: price
    assert costs.usd_per_quote("JPY", 50 * DAY) == pytest.approx(1 / 150.0)  # before the cache: first close


@needs_m1
def test_conversion_matches_the_2026_report_constants():
    for sym, ccy in (("USDJPY", "JPY"), ("USDCAD", "CAD"), ("DE40", "EUR"), ("UK100", "GBP")):
        assert costs.usd_per_quote(ccy, day_ms(date(2026, 3, 16))) == pytest.approx(SPECS[sym].usd_per_quote, rel=0.08)


def test_commission_and_swap():
    inst = instrument("XAUUSD")
    assert costs.commission(inst, 2) == pytest.approx(2 * 0.2579)
    t_in = day_ms(date(2025, 3, 11)) + 12 * 3_600_000       # Tue 12:00 UTC
    t_out = t_in + 2 * DAY                                  # Thu 12:00 UTC: Tue + Wed (triple) rollovers
    assert costs.swap(inst, 1, 2, t_in, t_out) == pytest.approx(inst.swap_long * 2 * 4)
    assert costs.swap(inst, -1, 2, t_in, t_out) == pytest.approx(inst.swap_short * 2 * 4)
