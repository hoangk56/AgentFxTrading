"""Request error log (app/request_errors.py): a request that ends in an exception or an HTTP error reaches the agent
log (file, dashboard, Telegram) instead of only uvicorn's lines in journald."""
import logging

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app import auth
from app.logging_setup import Throttle
from app.request_errors import RequestErrorLogMiddleware
from app.server import app as real_app

LOGGER = "AgentFxTrading.Requests"


def _client():
    app = FastAPI()
    app.add_middleware(RequestErrorLogMiddleware, throttle=Throttle(60))

    @app.get("/ok")
    def ok():
        return {"status": "ok"}

    @app.get("/boom")
    def boom():
        raise ValueError("bad value")

    @app.get("/missing")
    def missing():
        raise HTTPException(404, "no report for this backtest")

    @app.get("/down")
    def down():
        raise HTTPException(503, "Docker is not available on this server")

    @app.get("/long")
    def long():
        raise HTTPException(400, "x" * 1000)

    @app.post("/report")
    def report(request: dict):
        return {"status": "ok"}

    return TestClient(app, raise_server_exceptions=False)


def _records(caplog):
    return [(r.levelno, r.getMessage()) for r in caplog.records if r.name == LOGGER]


def test_an_unhandled_exception_is_logged_with_its_traceback_and_still_answers_500(caplog):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        res = _client().get("/boom")
    assert res.status_code == 500
    assert _records(caplog) == [(logging.ERROR, "Unhandled error on GET /boom")]
    [record] = [r for r in caplog.records if r.name == LOGGER]
    assert record.exc_info[0] is ValueError


def test_a_5xx_answer_is_an_error_with_its_body(caplog):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert _client().get("/down").status_code == 503
    assert _records(caplog) == [
        (logging.ERROR, 'HTTP 503 on GET /down: {"detail":"Docker is not available on this server"}')]


def test_a_4xx_answer_is_a_warning_with_its_body(caplog):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert _client().get("/missing").status_code == 404
    assert _records(caplog) == [
        (logging.WARNING, 'HTTP 404 on GET /missing: {"detail":"no report for this backtest"}')]


def test_a_body_that_is_not_a_json_object_is_logged_as_a_422(caplog):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert _client().post("/report", json=[1, 2]).status_code == 422
    [(level, message)] = _records(caplog)
    assert level == logging.WARNING and message.startswith("HTTP 422 on POST /report: ")
    assert "dict_type" in message


def test_a_long_body_is_cut(caplog):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        _client().get("/long")
    [(_, message)] = _records(caplog)
    assert message.endswith("…") and len(message) < 400


def test_successful_requests_are_not_logged(caplog):
    client = _client()
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert client.get("/ok").status_code == 200
        assert client.post("/report", json={"a": 1}).status_code == 200
    assert _records(caplog) == []


def test_the_same_error_on_the_same_route_is_logged_once_a_minute(caplog):
    client = _client()
    with caplog.at_level(logging.INFO, logger=LOGGER):
        for _ in range(5):
            client.get("/missing")
        client.get("/down")
    assert [m.split(":")[0] for _, m in _records(caplog)] == ["HTTP 404 on GET /missing", "HTTP 503 on GET /down"]


@pytest.fixture
def login_on(monkeypatch, tmp_path):
    monkeypatch.setenv("DASHBOARD_USERNAME", "admin")
    monkeypatch.setenv("DASHBOARD_PASSWORD", "s3cret pass")
    monkeypatch.setattr(auth, "SECRET_FILE", tmp_path / "session_secret")
    monkeypatch.setattr(auth, "_secret", None)


def test_the_server_logs_a_cbot_request_it_rejects(caplog):
    local = TestClient(real_app, client=("127.0.0.1", 40000))
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert local.post("/api/tick", json=["not", "an", "object"]).status_code == 422
    assert any(m.startswith("HTTP 422 on POST /api/tick: ") for _, m in _records(caplog))


def test_the_server_does_not_log_visitors_turned_away_by_the_login(login_on, caplog):
    visitor = TestClient(real_app, follow_redirects=False, headers={"X-Real-IP": "203.0.113.9"})
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert visitor.get("/wp-login.php").status_code == 303
        assert visitor.post("/api/tick", json={}).status_code == 401
    assert _records(caplog) == []
