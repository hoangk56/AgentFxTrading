from fastapi.testclient import TestClient

from app.server import app as fastapi_app

client = TestClient(fastapi_app)


def test_tick():
    payload = {
        "bot_id": "cbot-usdjpy-fix-gotobi",
        "account_number": "123456",
        "symbol": "USDJPY",
        "bid": 148.501,
        "ask": 148.504,
        "equity": 10250.0,
        "balance": 10000.0
    }
    res = client.post("/api/tick", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_portfolio_reports():
    open_payload = {
        "bot_id": "cbot-usdjpy-fix-gotobi",
        "action": "open",
        "symbol": "USDJPY",
        "side": "BUY",
        "volume": 0.05,
        "entry_price": 148.500,
        "sl_pips": 30.0,
        "account_number": "123456",
        "account_balance": 10000.0,
        "account_equity": 10000.0
    }
    res_open = client.post("/portfolio/report", json=open_payload)
    assert res_open.status_code == 200
    assert res_open.json()["status"] == "success"

    close_payload = {
        "bot_id": "cbot-usdjpy-fix-gotobi",
        "action": "close",
        "symbol": "USDJPY",
        "exit_price": 148.700,
        "pnl": 200.0,
        "account_number": "123456",
        "account_balance": 10200.0,
        "account_equity": 10200.0
    }
    res_close = client.post("/portfolio/report", json=close_payload)
    assert res_close.status_code == 200
    assert res_close.json()["status"] == "success"


def test_removed_ai_routes_are_gone():
    """The AI layer (/trade, news, risk limits, cross-locks) was removed with the TMS/Judas/FlowRSI bots."""
    assert client.post("/trade", json={}).status_code in (404, 405)
    for path in ("/api/risk-limits", "/api/news/calendar", "/api/tms/cross-locks",
                 "/api/dashboard/latest-decisions", "/portfolio/open-positions"):
        assert client.get(path).status_code == 404, path


def test_logging_isolation_flag():
    from app.server import is_running_under_test
    assert is_running_under_test() is True
