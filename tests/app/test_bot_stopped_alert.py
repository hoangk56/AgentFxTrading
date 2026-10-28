"""Overview alert for a bot that is down: only when the owner did not stop it on purpose."""
import pytest
from fastapi.testclient import TestClient

import app.dashboard as dashboard_module
from app import cbot_watchdog as watchdog_module
from app.portfolio import PortfolioManager
from app.server import app

client = TestClient(app)
RUN = 'dotnet cli run cbot.algo --BotId=cbot-demo-eurusd'


@pytest.fixture
def pm(tmp_path, monkeypatch):
    manager = PortfolioManager(db_path=str(tmp_path / "stopped.db"))
    monkeypatch.setattr(dashboard_module, "get_portfolio_manager", lambda: manager)
    manager.add_cbot_config("bot-a", "A", RUN)
    return manager


def _health(monkeypatch, status):
    monkeypatch.setattr(watchdog_module.cbot_watchdog, "_last_health", {"bot-a": {"status": status}} if status else {})


def _kinds():
    return [(a["kind"], a["bot"]) for a in client.get("/api/dashboard/alerts").json()["alerts"]
            if a["kind"] == "bot_stopped"]


def test_a_dead_container_is_reported_until_the_owner_stops_it(pm, monkeypatch):
    _health(monkeypatch, "exited")
    assert _kinds() == [("bot_stopped", "cbot-demo-eurusd")]
    pm.set_bot_stopped("cbot-demo-eurusd", True)
    assert _kinds() == []


def test_a_running_bot_and_an_unchecked_bot_are_not_reported(pm, monkeypatch):
    _health(monkeypatch, "running")
    assert _kinds() == []
    _health(monkeypatch, None)     # the watchdog has not looked yet, or docker is unavailable
    assert _kinds() == []


def test_stop_start_and_restart_endpoints_remember_the_intent(pm, monkeypatch):
    ok = {"success": True, "message": "ok"}
    for method in ("stop_container", "start_container", "restart_container", "remove_container"):
        monkeypatch.setattr(dashboard_module.docker_manager, method, lambda *a, **k: ok)
    bot_id = "cbot-demo-eurusd"
    client.post("/api/bots/bot-a/stop")
    assert pm.is_bot_stopped_on_purpose(bot_id)
    client.post("/api/bots/bot-a/start")
    assert not pm.is_bot_stopped_on_purpose(bot_id)
    client.post("/api/bots/bot-a/remove")
    assert pm.is_bot_stopped_on_purpose(bot_id)
    client.post("/api/bots/bot-a/restart")
    assert not pm.is_bot_stopped_on_purpose(bot_id)


def test_a_failed_stop_does_not_mark_the_bot_stopped(pm, monkeypatch):
    monkeypatch.setattr(dashboard_module.docker_manager, "stop_container", lambda *a, **k: {"success": False, "message": "x"})
    client.post("/api/bots/bot-a/stop")
    assert not pm.is_bot_stopped_on_purpose("cbot-demo-eurusd")


def test_a_saved_but_never_started_bot_is_not_an_outage(pm, monkeypatch):
    resp = client.post("/api/bots", json={"name": "bot-b", "description": "B", "run_command": RUN.replace("eurusd", "gold")})
    assert resp.json()["success"] is True
    assert pm.is_bot_stopped_on_purpose("cbot-demo-gold")


def test_the_mark_survives_a_restart(tmp_path):
    path = str(tmp_path / "s.db")
    PortfolioManager(db_path=path).set_bot_stopped("cbot-a", True)
    assert PortfolioManager(db_path=path).is_bot_stopped_on_purpose("cbot-a") is True
