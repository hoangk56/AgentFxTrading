"""Calendar (app/gotobi_calendar.py, /api/gotobi/calendar): the gotobi days, the Gotobi trades and the ECB window
trades by day.

A position belongs to the gotobi day the bot opened it for (GotobiBot.InferLeg): a buy in the evening long window is
the long of the next day, a sell just after the 00:55 UTC fix the short of that day. On a day that is not a trading
day (not gotobi, or in the presets' SkipDates) the bot trades only decoys. An EcbWindowBot trade belongs to its UTC
entry day, in its own bucket.
"""
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from app import gotobi_calendar as gc
from app.accounts import AccountRegistry
from app.db import get_db_connection
from app.portfolio import PortfolioManager
from app.server import app

client = TestClient(app)


@pytest.mark.parametrize("day, expected", [
    (date(2026, 10, 5), True),     # Monday the 5th
    (date(2026, 10, 9), True),     # Saturday the 10th moves to Friday the 9th
    (date(2026, 10, 10), False),
    (date(2026, 10, 12), False),
    (date(2026, 10, 30), True),    # Saturday the 31st (last day) moves to Friday the 30th
    (date(2026, 11, 30), True),    # last day of a 30-day month
    (date(2026, 2, 27), True),     # Saturday the 28th (last day) moves to Friday the 27th
    (date(2026, 1, 23), True),     # Sunday the 25th moves to Friday the 23rd
    (date(2026, 1, 26), False),
])
def test_is_gotobi_matches_the_bot(day, expected):
    assert gc.is_gotobi(day) is expected


def test_leg_of_follows_the_bots_entry_windows():
    assert gc.leg_of("Buy", datetime(2026, 10, 8, 18, 20)) == ("long", date(2026, 10, 9))
    assert gc.leg_of("BUY", datetime(2026, 10, 8, 17, 0)) == ("long", date(2026, 10, 9))    # earliest jittered entry
    assert gc.leg_of("Buy", datetime(2026, 10, 8, 23, 5)) == ("long", date(2026, 10, 9))    # latest + slack
    assert gc.leg_of("Sell", datetime(2026, 10, 9, 0, 55, 30)) == ("short", date(2026, 10, 9))
    assert gc.leg_of("Sell", datetime(2026, 10, 9, 1, 3)) == ("short", date(2026, 10, 9))
    assert gc.leg_of("Sell", datetime(2026, 10, 9, 12, 0)) is None
    assert gc.leg_of("Buy", datetime(2026, 10, 9, 1, 0)) is None
    assert gc.leg_of("Buy", datetime(2026, 10, 9, 18, 0)) is None     # Friday evening: Saturday is never traded


def test_ecb_rule_comes_from_the_bot_id():
    assert gc.ecb_rule("cbot-live-live-eurusd-ecb-f3") == "F3"
    assert gc.ecb_rule("cbot-demo-demo-eurusd-ecb-e1") == "E1"
    assert gc.ecb_rule("cbot-demo-usdjpy-fix-gotobi") is None and gc.ecb_rule(None) is None


def test_ecb_days_and_plan_follow_the_bot():
    assert gc.is_ecb_day(date(2026, 10, 19), "E1") and not gc.is_ecb_day(date(2026, 10, 19), "F3")   # Monday
    assert gc.is_ecb_day(date(2026, 10, 20), "F3")
    assert not gc.is_ecb_day(date(2026, 10, 17), "E1")                                               # Saturday
    assert not gc.is_ecb_day(date(2026, 12, 24), "E1") and not gc.is_ecb_day(date(2027, 1, 1), "E1")
    assert gc.is_ecb_day(date(2026, 12, 23), "E1") and gc.is_ecb_day(date(2027, 1, 4), "E1")
    today, bots = date(2026, 10, 19), {"E1": date(2026, 10, 16), "F3": date(2026, 10, 16)}
    assert gc.ecb_plan(date(2026, 10, 15), today, bots, set()) == []                                 # before the bots
    assert gc.ecb_plan(date(2026, 10, 16), today, bots, set()) == [{"rule": "E1", "status": "no-trade"}]
    assert gc.ecb_plan(date(2026, 10, 19), today, bots, set()) == [{"rule": "E1", "status": "scheduled"}]
    assert gc.ecb_plan(date(2026, 10, 20), today, bots, set()) == [
        {"rule": "E1", "status": "scheduled"}, {"rule": "F3", "status": "possible"}]
    assert gc.ecb_plan(date(2026, 10, 20), today, bots, {"E1"}) == [{"rule": "F3", "status": "possible"}]
    assert gc.ecb_plan(date(2026, 10, 20), today, {}, set()) == []


def test_trading_day_excludes_skip_dates():
    assert gc.is_trading_day(date(2026, 10, 9), set())
    assert not gc.is_trading_day(date(2026, 12, 25), {date(2026, 12, 25)})
    assert gc.parse_skip_dates("2026-12-25, 2027-05-05,bad") == {date(2026, 12, 25), date(2027, 5, 5)}


# ---------- /api/gotobi/calendar ----------

@pytest.fixture
def db(tmp_path, monkeypatch):
    path = str(tmp_path / "gotobi.db")
    pm = PortfolioManager(db_path=path)
    registry = AccountRegistry(path)
    import app.portfolio as portfolio_mod
    import app.accounts as accounts_mod
    monkeypatch.setattr(portfolio_mod, "portfolio_manager", pm)
    monkeypatch.setattr(accounts_mod, "_account_registry", registry)
    monkeypatch.setattr(gc, "today_utc", lambda: date(2026, 10, 12))
    conn = get_db_connection(path)
    for acc_id, acc_type in (("demo-1", "demo"), ("live-1", "live")):
        conn.execute("INSERT INTO accounts (account_id, account_number, account_type, label) VALUES (?, ?, ?, ?)",
                     (acc_id, acc_id, acc_type, acc_id))
    conn.commit()
    yield conn
    conn.close()


def _pos(conn, pos_id, bot, side, entry, exit_, pnl, account="demo-1", status="closed"):
    conn.execute("INSERT INTO positions (id, bot_id, symbol, side, volume, entry_price, entry_time, exit_time, pnl, "
                 "status, account_id) VALUES (?, ?, 'USDJPY', ?, 0.1, 150, ?, ?, ?, ?, ?)",
                 (pos_id, bot, side, entry, exit_, pnl, status, account))
    conn.commit()


BOT = "cbot-demo-usdjpy-fix-gotobi"


def _seed(conn):
    _pos(conn, 1, BOT, "Buy", "2026-10-08 18:12:00", "2026-10-09 00:55:01", 12.0)        # long of Fri 9th
    _pos(conn, 2, BOT, "Sell", "2026-10-09 00:55:02", "2026-10-09 02:55:00", -3.5)       # short of Fri 9th
    _pos(conn, 3, BOT, "Buy", "2026-10-06 18:40:00", "2026-10-07 00:55:00", -0.4)        # decoy long of Wed 7th
    _pos(conn, 4, "cbot-demo-usdjpy-london-flowrsi", "Buy", "2026-10-09 08:00:00", None, 50.0)   # not Gotobi
    _pos(conn, 5, BOT, "Buy", "2026-11-04 18:00:00", None, None, status="open")          # long of Thu Nov 5th
    _pos(conn, 8, BOT, "Buy", "2026-10-30 18:30:00", "2026-10-30 22:00:00", -1.0)        # Fri evening: no leg
    _pos(conn, 6, BOT, "Buy", "2026-09-30 18:00:00", "2026-10-01 00:55:00", 4.0)         # long of Oct 1st (decoy)
    _pos(conn, 7, "cbot-live-usdjpy-fix-gotobi", "Sell", "2026-10-09 00:56:00", "2026-10-09 02:55:00", 8.0,
         account="live-1")


def _days(data):
    return {d["date"]: d for d in data["days"]}


def test_calendar_month_buckets_real_and_decoy_trades(db):
    _seed(db)
    data = client.get("/api/gotobi/calendar?month=2026-10&account_id=demo").json()
    days = _days(data)
    assert data["month"] == "2026-10" and data["today"] == "2026-10-12"
    assert all(datetime.fromisoformat(d).weekday() < 5 for d in days)   # weekdays only
    assert len(days) == 22

    fri = days["2026-10-09"]
    assert fri["gotobi"] and fri["status"] == "traded"
    assert (fri["real"]["n"], fri["real"]["pnl"]) == (2, 8.5)
    assert [(t["id"], t["leg"], t["decoy"]) for t in fri["trades"]] == [(1, "long", False), (2, "short", False)]
    assert fri["trades"][0]["entry_time_vn"] == "01:12:00 09/10/2026"

    wed = days["2026-10-07"]
    assert not wed["gotobi"] and wed["status"] == "plain"
    assert (wed["decoy"]["n"], wed["decoy"]["pnl"], wed["real"]["n"]) == (1, -0.4, 0)
    assert days["2026-10-01"]["decoy"]["n"] == 1                      # entered the evening of Sep 30th

    assert days["2026-10-05"]["status"] == "no-trade"                 # past gotobi day, no position
    assert days["2026-10-15"]["status"] == "scheduled"
    fri30 = days["2026-10-30"]                                        # the bot never trades a weekend day
    assert [(t["id"], t["leg"]) for t in fri30["trades"]] == [(8, None)] and fri30["other"]["n"] == 1
    assert fri30["real"]["n"] == 0 and fri30["status"] == "scheduled"
    assert (data["totals"]["real_pnl"], data["totals"]["real_trades"], data["totals"]["decoy_pnl"]) == (8.5, 2, 3.6)
    assert data["totals"]["gotobi_days"] == 6


def test_calendar_ecb_trades_have_their_own_bucket(db):
    _seed(db)
    # 11:00 London = 10:00 UTC in summer: an F3 short on the gotobi Friday 9th, an E1 short on plain Tuesday 6th
    _pos(db, 20, "cbot-live-live-eurusd-ecb-f3", "Sell", "2026-10-09 10:00:00", "2026-10-09 12:00:00", 1.2,
         account="live-1")
    _pos(db, 21, "cbot-demo-demo-eurusd-ecb-e1", "Sell", "2026-10-06 10:00:01", "2026-10-06 12:00:00", -3.0)
    _pos(db, 22, "cbot-demo-demo-eurusd-ecb-e1", "Sell", "2026-10-12 10:00:00", None, None, status="open")
    data = client.get("/api/gotobi/calendar?month=2026-10&account_id=all").json()
    days = _days(data)
    fri = days["2026-10-09"]
    assert fri["ecb"] == {"n": 1, "pnl": 1.2, "open": 0}
    assert fri["real"]["n"] == 3 and fri["status"] == "traded"          # the Gotobi legs are unchanged
    f3 = next(t for t in fri["trades"] if t["id"] == 20)
    assert (f3["strategy"], f3["rule"], f3["leg"], f3["decoy"]) == ("ecb", "F3", None, False)
    tue = days["2026-10-06"]
    assert tue["ecb"] == {"n": 1, "pnl": -3.0, "open": 0} and tue["status"] == "plain"
    assert tue["decoy"]["n"] == 0 and tue["other"]["n"] == 0
    assert days["2026-10-12"]["ecb"] == {"n": 1, "pnl": 0.0, "open": 1}
    assert (data["totals"]["ecb_trades"], data["totals"]["ecb_pnl"]) == (3, -1.8)
    assert data["totals"]["real_trades"] == 3                          # ECB trades never count as Gotobi legs
    assert all(t["strategy"] == "gotobi" for t in days["2026-10-07"]["trades"])
    live = _days(client.get("/api/gotobi/calendar?month=2026-10&account_id=live").json())
    assert live["2026-10-09"]["ecb"]["n"] == 1 and live["2026-10-06"]["ecb"]["n"] == 0


def _install_ecb(db, slug, number, acc_type, strategy, created):
    from app.accounts import get_account_registry
    from app.portfolio import get_portfolio_manager
    from app.cbot_presets import container_name
    acc = get_account_registry().get_ctrader_account_by_slug(slug) or get_account_registry().insert_ctrader_account(
        slug, "me@example.com", number, acc_type, slug, "/root/ctrader_data/pwd")
    name = container_name(acc["slug"], strategy, "EURUSD")
    get_portfolio_manager().add_cbot_config(name, "ECB", "docker run ...")
    db.execute("UPDATE cbot_configs SET created_at = ? WHERE name = ?", (created, name))
    db.commit()


def test_calendar_plans_the_installed_ecb_rules_in_scope(db):
    _install_ecb(db, "demo-demo", "demo-1", "demo", "ecb_e1", "2026-10-07 10:00:00")
    _install_ecb(db, "live-live", "live-1", "live", "ecb_f3", "2026-10-07 10:00:00")
    _pos(db, 30, "cbot-demo-demo-eurusd-ecb-e1", "Sell", "2026-10-08 10:00:00", "2026-10-08 12:00:00", 2.0)
    demo = _days(client.get("/api/gotobi/calendar?month=2026-10&account_id=demo").json())
    assert demo["2026-10-06"]["ecb_plan"] == []                                     # before the bot existed
    assert demo["2026-10-07"]["ecb_plan"] == [{"rule": "E1", "status": "no-trade"}]
    assert demo["2026-10-08"]["ecb_plan"] == [] and demo["2026-10-08"]["ecb"]["n"] == 1
    assert demo["2026-10-12"]["ecb_plan"] == [{"rule": "E1", "status": "scheduled"}]   # today, Monday
    live = _days(client.get("/api/gotobi/calendar?month=2026-10&account_id=live").json())
    assert live["2026-10-12"]["ecb_plan"] == []                                     # F3 skips Mondays
    assert live["2026-10-13"]["ecb_plan"] == [{"rule": "F3", "status": "possible"}]
    assert live["2026-10-09"]["ecb_plan"] == []                                     # a past F3 day says nothing
    both = _days(client.get("/api/gotobi/calendar?month=2026-10&account_id=all").json())
    assert both["2026-10-13"]["ecb_plan"] == [{"rule": "E1", "status": "scheduled"}, {"rule": "F3", "status": "possible"}]
    assert both["2026-10-08"]["ecb_plan"] == []                                     # E1 traded; F3 past
    one = _days(client.get("/api/gotobi/calendar?month=2026-10&account_id=live-1").json())
    assert one["2026-10-13"]["ecb_plan"] == [{"rule": "F3", "status": "possible"}]


def test_calendar_account_scope(db):
    _seed(db)
    live = _days(client.get("/api/gotobi/calendar?month=2026-10&account_id=live").json())
    assert live["2026-10-09"]["real"] == {"n": 1, "pnl": 8.0, "open": 0}
    both = _days(client.get("/api/gotobi/calendar?month=2026-10&account_id=all").json())
    assert both["2026-10-09"]["real"]["n"] == 3
    one = _days(client.get("/api/gotobi/calendar?month=2026-10&account_id=live-1").json())
    assert one["2026-10-09"]["real"]["n"] == 1


def test_calendar_open_positions_and_skip_days(db, monkeypatch):
    _seed(db)
    monkeypatch.setattr(gc, "skip_dates", lambda: {date(2026, 11, 5)})
    days = _days(client.get("/api/gotobi/calendar?month=2026-11&account_id=demo").json())
    nov5 = days["2026-11-05"]
    assert nov5["status"] == "skipped" and nov5["skipped"] and nov5["gotobi"]
    assert (nov5["decoy"]["n"], nov5["decoy"]["open"], nov5["decoy"]["pnl"]) == (1, 1, 0.0)


def test_calendar_rejects_a_bad_month(db):
    assert client.get("/api/gotobi/calendar?month=2026-13").status_code == 422
    assert client.get("/api/gotobi/calendar?month=oct").status_code == 422
