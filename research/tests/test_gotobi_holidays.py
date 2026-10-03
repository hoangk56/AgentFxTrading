import datetime

import pytest

from research.tools import gotobi_holidays as gh

HEADER = "symbol,direction,leg,entry_utc,close_utc,entry,close,lots,pips,gross,commissions,swaps,net\n"


def _csv(tmp_path, rows):
    path = tmp_path / "trades.csv"
    path.write_text(HEADER + "".join(
        f"USDJPY,{'buy' if leg == 'L' else 'sell'},GOTOBI-{leg} {day},{day} 00:00:00,{day} 01:00:00,1,1,0.1,0,0,0,0,{net}\n"
        for leg, day, net in rows))
    return path


def test_trades_belong_to_the_gotobi_day_of_their_leg_tag(tmp_path):
    # The long of 2020-01-06 enters at 18:00 UTC on the Friday before the weekend: its tag, not its entry, says
    # which gotobi day it belongs to.
    path = tmp_path / "t.csv"
    path.write_text(HEADER + "USDJPY,buy,GOTOBI-L 2020-01-06,2020-01-03 18:00:00,2020-01-06 00:55:00,1,1,0.1,0,0,0,0,-5\n")
    assert gh.load_trades(path) == [{"day": datetime.date(2020, 1, 6), "leg": "long", "symbol": "USDJPY", "net": -5.0}]


def test_split_separates_holiday_gotobi_days_and_their_legs(tmp_path):
    trades = gh.load_trades(_csv(tmp_path, [
        ("L", "2025-05-05", -20), ("S", "2025-05-05", 5),       # Children's Day
        ("L", "2025-12-31", -10),                               # bank holiday
        ("L", "2025-05-09", 30), ("S", "2025-05-09", 10),       # an ordinary gotobi day
    ]))
    no_fix = {datetime.date(2025, 5, 5): "Children's Day", datetime.date(2025, 12, 31): "Bank holiday"}
    parts = gh.split(trades, no_fix)
    assert [t["net"] for t in parts["holiday gotobi days"]] == [-20, 5, -10]
    assert [t["net"] for t in parts["normal gotobi days"]] == [30, 10]
    assert [t["net"] for t in parts["  holiday, long leg"]] == [-20, -10]
    assert [t["net"] for t in parts["  bank holidays only"]] == [-10]
    assert [t["net"] for t in parts["  public holidays only"]] == [-20, 5]


def test_stats_are_in_units_of_the_default_risk(tmp_path):
    trades = gh.load_trades(_csv(tmp_path, [("L", "2025-05-09", 50), ("S", "2025-05-09", -25), ("L", "2025-05-15", 25)]))
    s = gh.stats(trades, risk=50)
    assert (s["days"], s["trades"], s["net"]) == (2, 3, 50)
    assert s["mean_r"] == pytest.approx(1 / 3) and s["win"] == pytest.approx(2 / 3)


def test_max_drawdown_is_peak_to_trough_of_cumulative_net(tmp_path):
    trades = gh.load_trades(_csv(tmp_path, [("L", "2025-05-09", 10), ("S", "2025-05-09", -30), ("L", "2025-05-15", 5),
                                            ("S", "2025-05-15", -10), ("L", "2025-05-20", 100)]))
    assert gh.max_drawdown(trades) == 35


def test_no_fix_days_are_public_and_bank_holidays():
    pytest.importorskip("holidays")
    days = gh.no_fix_days([2027])
    assert days[datetime.date(2027, 5, 5)] == "Children's Day"
    assert days[datetime.date(2027, 12, 31)] == "Bank holiday"
    assert datetime.date(2027, 5, 6) not in days
    assert [d.isoformat() for d, _ in gh.upcoming(datetime.date(2027, 1, 1), datetime.date(2027, 12, 31))] == [
        "2027-05-05", "2027-09-20", "2027-12-31"]
