"""Overview "Sắp tới": the next scheduled entries of the installed Gotobi and ECB bots (app/overview_api.py)."""
from datetime import date, datetime, timezone

from fastapi.testclient import TestClient

from app.overview_api import upcoming_events
from app.server import app
from tests._paths import dashboard_page

client = TestClient(app)

GOTOBI = [{"strategy": "gotobi", "symbol": s} for s in ("USDJPY", "EURJPY")]
E1 = [{"strategy": "ecb_e1", "symbol": "EURUSD"}]
F3 = [{"strategy": "ecb_f3", "symbol": "EURUSD"}]


def _utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


def test_gotobi_long_the_evening_before_then_the_short_at_the_fix():
    # Thu 2026-10-29 12:00 UTC: next trading gotobi day is Fri 30/10 (31/10 is a Saturday, moved to the 30th)
    events = upcoming_events(_utc(2026, 10, 29, 12), GOTOBI, set(), limit=2)
    assert [(e["at"], e["side"]) for e in events] == [
        ("2026-10-29T18:00:00+00:00", "BUY"), ("2026-10-30T00:55:00+00:00", "SELL")]
    assert events[0]["symbols"] == ["EURJPY", "USDJPY"] and events[0]["jitter_min"] == 60
    assert events[1]["jitter_min"] == 0


def test_a_jittered_long_stays_listed_until_its_latest_time():
    events = upcoming_events(_utc(2026, 10, 29, 18, 30), GOTOBI, set(), limit=1)
    assert events[0]["side"] == "BUY"
    events = upcoming_events(_utc(2026, 10, 29, 19, 1), GOTOBI, set(), limit=1)
    assert events[0]["side"] == "SELL"


def test_skip_dates_drop_the_gotobi_day():
    events = upcoming_events(_utc(2026, 10, 29, 12), GOTOBI, {date(2026, 10, 30)}, limit=1)
    assert events[0]["at"].startswith("2026-11-04T18:00")   # 5/11 is next


def test_ecb_entry_is_11_london_in_both_seasons_and_f3_is_conditional():
    summer = upcoming_events(_utc(2026, 10, 23, 6), E1, set(), limit=1)[0]    # BST until 25/10
    winter = upcoming_events(_utc(2026, 10, 29, 6), E1, set(), limit=1)[0]
    assert summer["at"] == "2026-10-23T10:00:00+00:00" and not summer["conditional"]
    assert winter["at"] == "2026-10-29T11:00:00+00:00"
    f3 = upcoming_events(_utc(2026, 11, 1, 12), F3, set(), limit=1)[0]          # Sunday -> F3 skips Monday
    assert f3["at"].startswith("2026-11-03T11:00") and f3["conditional"] and f3["rule"] == "F3"


def test_no_installed_bot_means_nothing_coming_up():
    assert upcoming_events(_utc(2026, 10, 29, 12), [], set()) == []
    assert upcoming_events(_utc(2026, 10, 29, 12), [{"strategy": "gold50", "symbol": "XAUUSD"}], set()) == []


def test_endpoint_and_overview_wire_up():
    body = client.get("/api/overview/upcoming?account_id=demo").json()
    assert isinstance(body["events"], list) and "now" in body
    html = dashboard_page(client)
    assert 'id="ov-upcoming"' in html and "/static/js/overview_upcoming.js" in html
