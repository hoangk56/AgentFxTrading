"""Paper desk status: coverage from the call log, the score file, the alerts, and the cost pairs."""
import datetime as dt

import pytest

from app import paper_desk as pd
from app import paper_desk_status as st
from app.paper_desk_runner import COST_BP

UTC = dt.timezone.utc


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setenv("PAPER_DESK_DATA", str(tmp_path / "data"))
    path = str(tmp_path / "pd.db")
    pd.init_schema(path)
    return path


def _call(db, day, symbol, analyst, direction, rationale="r"):
    pd.record_call(day, symbol, analyst, direction, 0.5, rationale, {}, "m",
                   now=dt.datetime.fromisoformat(day).replace(hour=3, tzinfo=UTC), db_target=db)


def test_coverage_counts_sides_errors_and_missing_weekdays(db):
    _call(db, "2026-10-26", "EURUSD", "trend@m", 1)
    _call(db, "2026-10-26", "EURUSD", "risk@m", 0)
    _call(db, "2026-10-26", "USDJPY", "trend@m", -1, "ERROR: timeout")
    _call(db, "2026-10-28", "EURUSD", "trend@m", 0)          # Tuesday 10-27 has no calls
    cov = st.coverage(db, now=dt.datetime(2026, 10, 28, 8, tzinfo=UTC))
    a = {x["analyst"]: x for x in cov["analysts"]}
    assert a["trend@m"]["calls"] == 3 and a["trend@m"]["traded"] == 2 and a["trend@m"]["errors"] == 1
    assert a["trend@m"]["long"] == 1 and a["trend@m"]["short"] == 1
    assert a["risk@m"]["directional_rate"] == 0
    assert cov["days_missing"] == ["2026-10-27"] and cov["days_with_calls"] == 2
    assert cov["recent_days"][0]["symbols"] == 2


def test_today_is_not_missing_before_the_alert_hour(db):
    _call(db, "2026-10-26", "EURUSD", "trend@m", 1)
    cov = st.coverage(db, now=dt.datetime(2026, 10, 27, 4, tzinfo=UTC))
    assert cov["days_missing"] == []
    cov = st.coverage(db, now=dt.datetime(2026, 10, 27, 5, tzinfo=UTC))
    assert cov["days_missing"] == ["2026-10-27"]


def test_empty_table_has_no_missing_days(db):
    cov = st.coverage(db, now=dt.datetime(2026, 10, 28, 8, tzinfo=UTC))
    assert cov["analysts"] == [] and cov["days_missing"] == []


def test_score_file_round_trip(db):
    assert st.load_score() is None
    st.save_score({"analysts": {}, "baselines": {}}, now=dt.datetime(2026, 10, 29, 4, tzinfo=UTC))
    assert st.load_score()["scored_at"] == "2026-10-29T04:00:00+00:00"


def test_alerts_for_a_missed_day_and_failed_calls(db):
    _call(db, "2026-10-26", "EURUSD", "trend@m", 1)
    _call(db, "2026-10-27", "EURUSD", "trend@m", 0, "ERROR: x")
    sent = []
    alerts = st.PaperDeskAlerts(lambda text, key=None: sent.append((text, key)))
    out = alerts.check(db, now=dt.datetime(2026, 10, 28, 6, tzinfo=UTC))
    assert len(out) == 2 and sent[0][1] == ("paper_desk", "2026-10-28", "missing")
    assert sent[1][1] == ("paper_desk", "2026-10-27", "errors")
    assert alerts.check(db, now=dt.datetime(2026, 10, 28, 3, tzinfo=UTC))[:1] != out[:1]   # before 05:00: no miss


def test_cost_pairs_apply_by_direction():
    assert pd.cost_for((1.58, 0.64), 1) == 1.58 and pd.cost_for((1.58, 0.64), -1) == 0.64
    assert pd.cost_for(2.0, -1) == 2.0
    assert pd.net_bp(-1, 100.0, 99.0, (5.0, 1.0)) == pytest.approx(100.0 - 1.0)
    assert pd.net_bp(0, 100.0, 99.0, (5.0, 1.0)) == 0.0
    assert set(COST_BP) == set(pd.SYMBOLS)


def test_api_on_the_test_database():
    from fastapi.testclient import TestClient
    from app.server import app
    body = TestClient(app).get("/api/paper-desk/status").json()
    assert set(body) == {"coverage", "score"} and body["coverage"]["symbols"] == list(pd.SYMBOLS)
