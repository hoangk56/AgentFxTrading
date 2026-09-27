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


def test_weekend_closed_mask_follows_new_york_time_across_dst():
    from research.swing.weekend_test import weekend_closed_mask

    def ms(*a):
        return int(datetime.datetime(*a, tzinfo=datetime.timezone.utc).timestamp() * 1000)

    ts = np.array([
        ms(2025, 7, 11, 20, 59), ms(2025, 7, 11, 21, 0),    # Friday, EDT: 16:59 open, 17:00 closed
        ms(2025, 7, 13, 21, 4), ms(2025, 7, 13, 21, 5),     # Sunday, EDT: 17:04 closed, 17:05 open
        ms(2025, 1, 10, 21, 59), ms(2025, 1, 10, 22, 0),    # Friday, EST
        ms(2025, 1, 12, 22, 4), ms(2025, 1, 12, 22, 5),     # Sunday, EST
        ms(2025, 7, 12, 12, 0), ms(2025, 7, 9, 12, 0),      # Saturday closed, Wednesday open
    ], dtype=np.int64)
    assert weekend_closed_mask(ts).tolist() == [False, True, True, False, False, True, True, False, True, False]


def test_weekdays_from_month_end_counts_back_from_the_last_weekday():
    from research.swing.swing_rules import weekdays_from_month_end
    k = weekdays_from_month_end(datetime.date(2026, 1, 1), datetime.date(2026, 9, 30))
    assert k[datetime.date(2026, 9, 30)] == 1              # Wednesday, the month's last day
    assert k[datetime.date(2026, 9, 28)] == 3
    assert k[datetime.date(2026, 9, 25)] == 4              # the weekend in between is skipped
    assert k[datetime.date(2026, 1, 30)] == 1              # Sat 31st: Friday 30th is the last weekday
    assert k[datetime.date(2026, 1, 28)] == 3
    assert datetime.date(2026, 1, 31) not in k


@needs_m1
def test_month_end_usd_buys_usd_from_10_to_13_utc_on_the_third_last_weekday():
    from research.swing import swing as S
    from research.swing import swing_rules as SR
    tr = S.run_bot(SR.month_end_usd, ["USDJPY", "EURUSD"], (5, 0), cap=3, per_symbol=1)
    assert tr
    k = SR.weekdays_from_month_end(datetime.date(2016, 1, 1), datetime.date(2026, 9, 30))
    for t in tr:
        t_in = datetime.datetime.fromtimestamp(t.t_in / 1000, datetime.timezone.utc)
        assert t_in.strftime("%H:%M") == "10:00" and k[t_in.date()] == 3
        assert t.t_out - t.t_in <= 3 * 3_600_000 + 60_000
        assert t.side == (1 if t.symbol == "USDJPY" else -1)
        assert t.scale == 1.0


def test_account_compounds_off_equity_at_entry():
    from research.swing.account import compound, stats
    h = 3_600_000
    # sequential: +1R then -1R at 10 % risk -> 1.1, then 1.1 - 0.11 = 0.99
    seq = compound([(0, h, 1.0, 1.0), (2 * h, 3 * h, -1.0, 1.0)], 0.10)
    assert [round(e, 6) for _, e in seq] == [1.1, 0.99]
    # overlapping: both sized off the starting equity, since neither has closed when the other opens
    ovl = compound([(0, 2 * h, 1.0, 1.0), (h, 3 * h, 1.0, 2.0)], 0.10)
    assert [round(e, 6) for _, e in ovl] == [1.1, 1.3]
    s = stats(compound([(0, h, 1.0, 1.0), (2 * h, 3 * h, -2.0, 1.0)], 0.10))
    assert abs(s["max_dd"] - 0.2) < 1e-9 and abs(s["final"] - 0.88) < 1e-9
