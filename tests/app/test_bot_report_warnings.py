"""A value a bot sends that the server cannot read is dropped as before, but no longer silently: it is logged as a
warning, once a minute per bot and field. Same for a report action the server does not know and a dashboard
broadcast that fails."""
import logging

import pytest
from fastapi.testclient import TestClient

import app.portfolio as portfolio_mod
from app import portfolio_api
from app.portfolio import PortfolioManager
from app.server import app

client = TestClient(app)
LOGGER = "AgentFxTrading"


def _warnings(caplog):
    return [r.getMessage() for r in caplog.records if r.name == LOGGER and r.levelno == logging.WARNING]


@pytest.fixture
def pm(tmp_path, monkeypatch):
    manager = PortfolioManager(db_path=str(tmp_path / "warnings.db"))
    monkeypatch.setattr(portfolio_mod, "portfolio_manager", manager)
    return manager


def _tick(bot_id, **fields):
    return client.post("/api/tick", json={"bot_id": bot_id, "account_number": "555", "symbol": "EURUSD",
                                          "bid": 1.1, "ask": 1.1002, **fields})


def test_an_unreadable_tick_pnl_is_logged(caplog):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert _tick("cbot-warn-pnl", pnl="abc", pips=3).json()["status"] == "ok"
    assert _warnings(caplog) == ["Bot cbot-warn-pnl sent an unreadable pnl: 'abc'; ignored"]


def test_an_unreadable_position_entry_is_logged(caplog):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        _tick("cbot-warn-pos", positions=[{"net_profit": "n/a", "pips": 1}])
    assert _warnings(caplog) == ["Bot cbot-warn-pos sent an unreadable positions[0].net_profit: 'n/a'; ignored"]


def test_the_same_unreadable_field_is_logged_once_a_minute(caplog):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        for _ in range(5):
            _tick("cbot-warn-repeat", pnl="abc")
    assert len(_warnings(caplog)) == 1


def test_missing_null_and_zero_values_are_not_warnings(caplog, pm):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        _tick("cbot-warn-none", pnl=None, pips="")
        client.post("/portfolio/report", json={
            "bot_id": "cbot-warn-none", "action": "open", "symbol": "EURUSD", "side": "Buy", "volume": 0.1,
            "entry_price": 1.1, "sl_price": 0, "tp_price": None, "account_number": "555", "ctrader_id": ""})
    assert _warnings(caplog) == []


def test_unreadable_report_fields_are_logged_and_the_trade_still_books(caplog, pm):
    base = {"bot_id": "cbot-warn-close", "symbol": "EURUSD", "account_number": "555"}
    with caplog.at_level(logging.INFO, logger=LOGGER):
        opened = client.post("/portfolio/report", json={**base, "action": "open", "side": "Buy", "volume": 0.1,
                                                         "entry_price": 1.1, "ctrader_id": "7x"})
        closed = client.post("/portfolio/report", json={**base, "action": "close", "exit_price": 1.1, "pnl": 0.0,
                                                         "volume": "0,1", "sl_pips": "abc"})
    assert opened.json()["status"] == "success" and closed.json()["status"] == "success"
    assert _warnings(caplog) == ["Bot cbot-warn-close sent an unreadable ctrader_id: '7x'; ignored",
                                 "Bot cbot-warn-close sent an unreadable volume: '0,1'; ignored",
                                 "Bot cbot-warn-close sent an unreadable sl_pips: 'abc'; ignored"]


def test_an_unknown_report_action_is_an_error_and_a_warning(caplog, pm):
    with caplog.at_level(logging.INFO, logger=LOGGER):
        res = client.post("/portfolio/report", json={
            "bot_id": "cbot-warn-action", "action": "modify", "symbol": "EURUSD", "account_number": "555"})
    assert res.json() == {"status": "error", "message": "Unknown action: modify"}
    assert _warnings(caplog) == ["Bot cbot-warn-action sent an unknown report action: 'modify'; ignored"]


def test_a_failed_dashboard_broadcast_is_logged(caplog, monkeypatch):
    async def broken(**kw):
        raise RuntimeError("socket gone")

    monkeypatch.setattr(portfolio_api, "broadcast_tick", broken)
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert _tick("cbot-warn-bcast").json()["status"] == "ok"
    assert _warnings(caplog) == ["Dashboard tick broadcast failed: RuntimeError: socket gone"]
