import datetime
import sqlite3

from fastapi.testclient import TestClient

from app.dashboard_alerts import build_alerts
from app.server import app
from tests._paths import dashboard_page

client = TestClient(app)
NOW = datetime.datetime(2026, 10, 28, 21, 0, 0)


def _event(minutes_ago, success=True, bot="cbot-demo-eurusd", reason="stale feed", message="ok"):
    stamp = (NOW - datetime.timedelta(minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M:%S")
    return {"timestamp": stamp, "bot_name": bot, "reason": reason, "success": success, "message": message}


def _alerts(positions=(), events=(), telemetry=None, weekend=False):
    status = {"recent_events": list(events), "bar_telemetry": telemetry or {}}
    return build_alerts(list(positions), status, weekend, NOW)


def test_quiet_desk_has_no_alerts():
    assert _alerts(positions=[{"bot_id": "b", "symbol": "EURUSD", "price_age_seconds": 5.0}],
                   telemetry={"b": {"bar_age": 60, "allowance": 2400}}) == []


def test_open_position_without_a_price_is_critical():
    alerts = _alerts(positions=[{"bot_id": "b", "symbol": "EURUSD", "price_age_seconds": 900.0}])
    assert [(a["level"], a["kind"], a["bot"]) for a in alerts] == [("crit", "stale_price", "b")]
    assert "15 min" in alerts[0]["message"]


def test_position_with_no_price_info_is_not_flagged():
    # Older bots never report a price; that is not an outage.
    assert _alerts(positions=[{"bot_id": "b", "symbol": "EURUSD", "price_age_seconds": None}]) == []


def test_stalled_feed_is_a_warning_past_its_own_allowance():
    alerts = _alerts(telemetry={"slow": {"bar_age": 5000, "allowance": 4000}, "ok": {"bar_age": 3000, "allowance": 4000}})
    assert [(a["level"], a["bot"]) for a in alerts] == [("warn", "slow")]


def test_recent_restart_is_a_warning_and_a_failed_one_is_critical_and_listed_first():
    alerts = _alerts(events=[_event(5, bot="a"), _event(10, success=False, bot="b", message="docker down"),
                             _event(2, bot="a"), _event(180, bot="old")])
    assert [(a["level"], a["kind"], a["bot"]) for a in alerts] == [("crit", "restart_failed", "b"), ("warn", "restarted", "a")]
    assert "docker down" in alerts[0]["message"]


def test_weekend_silences_everything_except_a_failed_restart():
    alerts = _alerts(positions=[{"bot_id": "b", "symbol": "EURUSD", "price_age_seconds": 9000.0}],
                     events=[_event(5, bot="a"), _event(5, success=False, bot="c")],
                     telemetry={"s": {"bar_age": 99999, "allowance": 10}}, weekend=True)
    assert [(a["kind"], a["bot"]) for a in alerts] == [("restart_failed", "c")]


def test_bad_event_timestamp_is_ignored():
    assert _alerts(events=[{"timestamp": "yesterday", "bot_name": "a", "success": False}]) == []


def test_alerts_endpoint_returns_a_list():
    resp = client.get("/api/dashboard/alerts?account_id=all")
    assert resp.status_code == 200 and isinstance(resp.json()["alerts"], list)


def test_summary_floating_pnl_is_equity_minus_balance(tmp_path, monkeypatch):
    import app.dashboard as dashboard_module
    db = tmp_path / "p.db"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE accounts (account_id TEXT, account_type TEXT, label TEXT, is_configured INTEGER, "
                 "last_balance REAL, last_equity REAL)")
    conn.execute("CREATE TABLE positions (id INTEGER PRIMARY KEY, status TEXT, pnl REAL, account_id TEXT, bot_id TEXT, "
                 "exit_time TEXT, entry_time TEXT)")
    conn.execute("INSERT INTO accounts VALUES ('a1', 'demo', 'Demo', 1, 1000.0, 987.5)")
    conn.commit()
    conn.close()
    monkeypatch.setattr(dashboard_module, "get_db", lambda: sqlite3.connect(str(db)))
    assert dashboard_module.get_portfolio_summary("a1")["floating_pnl"] == -12.5
    assert dashboard_module.get_portfolio_summary("missing")["floating_pnl"] is None


def test_overview_has_the_alert_strip_the_floating_tile_and_the_script():
    html = client.get("/demo/dashboard").text
    assert 'id="health-alerts"' in html and 'id="floating-pnl"' in html
    assert '/static/js/overview_alerts.js' in html
    assert "getElementById('floating-pnl')" in dashboard_page(client)


def test_a_bot_nobody_stopped_is_critical_even_on_the_weekend():
    for weekend in (False, True):
        alerts = build_alerts([], {"recent_events": [], "bar_telemetry": {}}, weekend, NOW,
                              [{"bot_id": "cbot-live-gold", "status": "exited"}])
        assert [(a["level"], a["kind"], a["bot"]) for a in alerts] == [("crit", "bot_stopped", "cbot-live-gold")]
        assert "exited" in alerts[0]["message"]


def test_bot_mode_reads_the_live_token_not_a_substring():
    from app.dashboard_alerts import bot_mode
    assert bot_mode("cbot-live-live-eurusd-ecb-f3") == "live"
    assert bot_mode("cbot-demo-demo-eurusd-ecb-e1") == "demo"
    assert bot_mode("cbot-demo-alive-eurusd") == "demo"   # "alive" is not the live account


def test_filter_by_mode_keeps_docker_alerts_for_both_pages():
    from app.dashboard_alerts import filter_by_mode
    alerts = [{"kind": "bot_stopped", "bot": "cbot-live-live-x"}, {"kind": "bot_stopped", "bot": "cbot-demo-demo-y"},
              {"kind": "docker_down", "bot": "docker"}]
    assert [a["bot"] for a in filter_by_mode(alerts, "live")] == ["cbot-live-live-x", "docker"]
    assert [a["bot"] for a in filter_by_mode(alerts, "demo")] == ["cbot-demo-demo-y", "docker"]


def test_docker_missing_and_docker_error_are_critical():
    alerts = build_alerts([], {"recent_events": [], "bar_telemetry": {}}, False, NOW,
                          [{"bot_id": "cbot-live-live-x", "status": "error"}], docker_missing=True)
    assert [(a["kind"], a["bot"]) for a in alerts] == [("docker_down", "docker"), ("bot_stopped", "cbot-live-live-x")]
    assert "Docker error" in alerts[1]["message"]
