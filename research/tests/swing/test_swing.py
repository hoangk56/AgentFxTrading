"""research/swing/swing.py invariants: the three hard constraints (hold <= 5 days, <= 3 open positions per bot,
lots off a default risk, never equity) and the gotobi calendar."""
import datetime

import numpy as np
import pytest

from research.ticks import DATA_DIR

needs_m1 = pytest.mark.skipif(not (DATA_DIR / "m1" / "USDJPY.npz").exists(), reason="no M1 cache")


def _trade(sym, t_in, t_out, strength=1.0):
    from research.swing.swing import Trade
    return Trade(sym, 1, t_in, t_in, t_out, 1.0, 1.0, 0.1, 0.0, "time", strength)


def test_admit_caps_open_positions_per_bot_and_per_symbol():
    from research.swing.swing import admit
    h = 3_600_000
    tr = [_trade("A", 0, 10 * h), _trade("A", 1 * h, 10 * h), _trade("B", 2 * h, 10 * h),
          _trade("C", 3 * h, 10 * h), _trade("C", 11 * h, 12 * h)]
    taken = admit(tr, cap=3, per_symbol=3)
    assert [t.symbol for t in taken] == ["A", "A", "B", "C"]
    assert [t.symbol for t in admit(tr, cap=3, per_symbol=1)] == ["A", "B", "C", "C"]


def test_gotobi_nominal_moves_weekend_days_to_the_friday_before():
    from research.swing.swing_rules import gotobi_nominal
    lab = gotobi_nominal(datetime.date(2026, 1, 1), datetime.date(2026, 1, 31))
    assert lab[datetime.date(2026, 1, 5)] == "5"          # Monday
    assert lab[datetime.date(2026, 1, 9)] == "10"         # Sat 10th -> Fri 9th
    assert lab[datetime.date(2026, 1, 23)] == "25"        # Sun 25th -> Fri 23rd
    assert lab[datetime.date(2026, 1, 30)] == "last"      # Sat 31st -> Fri 30th


@needs_m1
def test_gotobi_basket_respects_the_hard_constraints():
    from research.swing import swing as S
    from research.swing import swing_rules as SR
    tr = S.run_bot(SR.gotobi, ["USDJPY", "EURJPY"], (5, 0), cap=3)
    assert tr
    assert max(t.t_out - t.t_in for t in tr) <= S.HOLD_MS
    ev = sorted([(t.t_in, 1) for t in tr] + [(t.t_out, -1) for t in tr], key=lambda e: (e[0], e[1]))
    assert max(np.cumsum([d for _, d in ev])) <= 3
    assert all(S.SCALE_MIN <= t.scale <= S.SCALE_MAX for t in tr)
    t = tr[0]
    assert datetime.datetime.fromtimestamp(t.t_in / 1000, datetime.timezone.utc).strftime("%H:%M") in ("18:00", "00:55")


@needs_m1
def test_crypto_donchian_respects_the_hold_limit():
    from research.swing import swing as S
    from research.swing.swing_rules import donchian
    tr = S.run_bots(donchian, ["BTCUSD"], S.H4, n=55, exit_n=20, shorts=True)
    assert tr and max(t.t_out - t.t_in for t in tr) <= S.HOLD_MS
