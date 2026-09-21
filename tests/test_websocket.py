import sys
from pathlib import Path
import asyncio
import json
import pytest
from fastapi.testclient import TestClient

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.server import app, ws_manager
from app.dashboard import broadcast_update, broadcast_tick, broadcast_event


def test_websocket_connection_and_ping():
    client = TestClient(app)
    with client.websocket_connect("/ws/dashboard") as ws:
        # Send ping
        ws.send_text(json.dumps({"type": "ping", "account_id": "all"}))
        data = ws.receive_json()
        assert data["type"] == "update"
        assert "summary" in data
        assert "positions" in data
        assert data["account_id"] == "all"


def test_websocket_subscription_and_logging_broadcast():
    client = TestClient(app)
    with client.websocket_connect("/ws/dashboard") as ws:
        # Subscribe
        ws.send_text(json.dumps({"type": "subscribe", "account_id": "demo", "mode": "demo"}))
        data = ws.receive_json()
        assert data["type"] == "update"
        
        # Test direct log broadcast
        test_log_line = "12:00:00 [INFO] AgentFxTrading: [AI Decision] BUY EURUSD"
        ws_manager.broadcast_log_threadsafe(test_log_line)
        # Verify broadcast receives if event loop was set or via async broadcast
        asyncio.run(ws_manager.broadcast_log(test_log_line))
        received = ws.receive_json()
        assert received["type"] == "log"
        assert received["line"] == test_log_line


def test_websocket_tick_and_event_broadcast():
    client = TestClient(app)
    with client.websocket_connect("/ws/dashboard") as ws:
        # Initial ping/update
        ws.send_text(json.dumps({"type": "ping", "account_id": "all"}))
        _ = ws.receive_json()

        # Broadcast tick
        asyncio.run(broadcast_tick(symbol="XAUUSD", bid=2650.50, ask=2650.80, account_id="demo"))
        tick_msg = ws.receive_json()
        assert tick_msg["type"] == "tick"
        assert tick_msg["symbol"] == "XAUUSD"
        assert tick_msg["bid"] == 2650.50
        assert tick_msg["ask"] == 2650.80

        # Broadcast event
        asyncio.run(broadcast_event(event_type="GUARDRAIL", message="High impact news pause active", bot_id="judas_xau", account_id="demo"))
        event_msg = ws.receive_json()
        assert event_msg["type"] == "event"
        assert event_msg["event_type"] == "GUARDRAIL"
        assert "High impact news" in event_msg["message"]

def test_cbot_websocket_stream():
    client = TestClient(app)
    with client.websocket_connect("/ws/cbot") as ws:
        # Test ping
        ws.send_text(json.dumps({"type": "ping"}))
        res = ws.receive_json()
        assert res["type"] == "pong"

        # Test tick stream
        ws.send_text(json.dumps({
            "type": "tick",
            "bot_id": "cbot-xauusd-test",
            "symbol": "XAUUSD",
            "bid": 2910.0,
            "ask": 2910.3,
            "account_id": "demo"
        }))
        ack = ws.receive_json()
        assert ack["type"] == "ack"
        assert ack["status"] == "ok"


def test_cbot_tick_carries_broker_pnl_to_the_dashboard():
    """A tick with the bot's own P&L sample must reach the dashboard and the position cache.

    This is what keeps prices and P&L live without the server rebuilding the positions payload
    (three account scopes, six DB reads, ~86 ms of CPU) on every single tick.
    """
    from app.portfolio import get_portfolio_manager

    pm = get_portfolio_manager()
    cache = getattr(pm, "_bot_positions_cache", None)
    if cache is not None:
        cache.pop("demo:probe-bot", None)
        cache.pop("probe-bot", None)

    client = TestClient(app)
    with client.websocket_connect("/ws/dashboard") as dash:
        dash.send_text(json.dumps({"type": "ping", "account_id": "all"}))
        assert dash.receive_json()["type"] == "update"

        with client.websocket_connect("/ws/cbot") as bot:
            bot.send_text(json.dumps({
                "type": "tick",
                "bot_id": "probe-bot",
                "symbol": "UK100",
                "bid": 10734.4,
                "ask": 10735.3,
                "account_id": "demo",
                "pnl": 1.24,
                "pips": 68.0,
            }))
            assert bot.receive_json()["type"] == "ack"

            tick = dash.receive_json()
            assert tick["type"] == "tick"
            assert tick["symbol"] == "UK100"
            assert tick["bid"] == 10734.4
            assert tick["pnl"] == 1.24
            assert tick["pips"] == 68.0

    # The server merged the bot's P&L sample into the position cache, keyed account:bot
    cache = getattr(pm, "_bot_positions_cache", {})
    assert cache["demo:probe-bot"]["unrealized_pnl"] == 1.24
    assert cache["demo:probe-bot"]["unrealized_pnl_pips"] == 68.0
    assert isinstance(cache["demo:probe-bot"]["_reported_at"], float)

    cache.pop("demo:probe-bot", None)
    cache.pop("probe-bot", None)

def test_position_close_broadcasts_history_and_event():
    """When a position is closed, broadcast_update must include recent trade history and daily PnL,
    so the dashboard's Recent Trades table immediately displays the closed trade without a page reload.
    """
    client = TestClient(app)
    test_bot = "test-recent-trade-bot"
    test_sym = "EURUSD"
    test_acc = "demo"

    # 1. Register an open position
    open_resp = client.post("/portfolio/report", json={
        "bot_id": test_bot,
        "action": "open",
        "symbol": test_sym,
        "side": "BUY",
        "volume": 0.1,
        "entry_price": 1.0850,
        "sl_pips": 20,
        "tp_pips": 40,
        "account_id": test_acc
    })
    assert open_resp.status_code == 200
    assert open_resp.json()["status"] == "success"

    with client.websocket_connect("/ws/dashboard") as ws:
        # Drain initial ping
        ws.send_text(json.dumps({"type": "ping", "account_id": test_acc}))
        initial = ws.receive_json()
        assert initial["type"] == "update"
        assert "history" in initial
        assert "pnl_history" in initial

        # 2. Close the position
        close_resp = client.post("/portfolio/report", json={
            "bot_id": test_bot,
            "action": "close",
            "symbol": test_sym,
            "exit_price": 1.0875,
            "pnl": 25.0,
            "account_id": test_acc
        })
        assert close_resp.status_code == 200
        assert close_resp.json()["status"] == "success"

        # 3. Read broadcast messages
        messages = []
        for _ in range(10):
            try:
                msg = ws.receive_json()
                messages.append(msg)
                has_trade_update = any(
                    m.get("type") == "update" and any(
                        t.get("bot_id") == test_bot and t.get("symbol") == test_sym for t in m.get("history", [])
                    ) for m in messages
                )
                has_close_event = any(
                    m.get("type") == "event" and m.get("event_type") == "TRADE_CLOSE" for m in messages
                )
                if has_trade_update and has_close_event:
                    break
            except Exception:
                break

        # Verify update with trade in history was received
        matching_updates = [
            m for m in messages
            if m.get("type") == "update" and any(
                t.get("bot_id") == test_bot and t.get("symbol") == test_sym for t in m.get("history", [])
            )
        ]
        assert len(matching_updates) > 0, f"Expected update with closed trade in history, got: {messages}"
        matched_update = matching_updates[0]
        assert "pnl_history" in matched_update
        trade = next(t for t in matched_update["history"] if t.get("bot_id") == test_bot and t.get("symbol") == test_sym)
        assert trade["pnl"] == 25.0
        assert trade["exit_price"] == 1.0875
        assert trade["side"] == "BUY"

        # Verify TRADE_CLOSE event was also broadcast
        events = [m for m in messages if m.get("type") == "event" and m.get("event_type") == "TRADE_CLOSE"]
        assert len(events) > 0
        assert test_sym in events[0]["message"]
