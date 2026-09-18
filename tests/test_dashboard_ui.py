import sys
import time
from pathlib import Path
from fastapi.testclient import TestClient

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.server import app

client = TestClient(app)

def test_ui_endpoints():
    # Test Sessions API
    resp_sess = client.get("/api/dashboard/sessions")
    assert resp_sess.status_code == 200
    data_sess = resp_sess.json()
    assert "sessions" in data_sess
    assert "sydney" in data_sess["sessions"]
    assert "killzone" in data_sess
    assert "forex_status" in data_sess

    # Test Exposure API
    resp_exp = client.get("/api/dashboard/exposure?account_id=all")
    assert resp_exp.status_code == 200
    data_exp = resp_exp.json()
    assert "by_asset_class" in data_exp
    assert "total_volume" in data_exp

    # Test Cumulative PnL API
    resp_cum = client.get("/api/dashboard/cumulative-pnl?days=30&account_id=all")
    assert resp_cum.status_code == 200
    data_cum = resp_cum.json()
    assert isinstance(data_cum, list)

    # Test Latest Decisions API with filtering
    resp_dec = client.get("/api/dashboard/latest-decisions?limit=3")
    assert resp_dec.status_code == 200
    data_dec = resp_dec.json()
    assert isinstance(data_dec, list)

    resp_dec_filtered = client.get("/api/dashboard/latest-decisions?limit=3&symbol=EURUSD")
    assert resp_dec_filtered.status_code == 200
    assert isinstance(resp_dec_filtered.json(), list)
    # Test Summary API
    resp_summary = client.get("/api/dashboard/summary")
    assert resp_summary.status_code == 200
    data_sum = resp_summary.json()
    assert "profit_factor" in data_sum
    assert "win_rate" in data_sum
    assert "total_trades" in data_sum

    # Test Demo and Real Dashboard HTML renders cleanly with new widgets
    resp_demo = client.get("/demo/dashboard")
    assert resp_demo.status_code == 200
    html_demo = resp_demo.text
    assert "market-session-bar" in html_demo
    assert "pnl-chart" in html_demo
    assert "equity-chart" in html_demo
    assert "exposure-chart" in html_demo
    assert 'id="profit-factor"' in html_demo
    resp_real = client.get("/real/dashboard")
    assert resp_real.status_code == 200
    html_real = resp_real.text
    assert "market-session-bar" in html_real
    assert "view-decisions" in html_real
    assert "view-decisions" in html_demo
    assert "ai-feed-list" in html_real
    assert 'id="profit-factor"' in html_real
    assert "view-news" in html_demo
    # Ensure view-news is inside <main class="main-content"> before </main>
    main_close_idx = html_demo.find("</main>")
    news_view_idx = html_demo.find('id="view-news"')
    assert news_view_idx != -1 and news_view_idx < main_close_idx


def test_flowrsi_badge_renders_on_dashboard():
    """FlowRSI bots must render with their dedicated emerald 'FlowRSI' badge rather than falling back to TMS+ORB."""
    resp_demo = client.get("/demo/dashboard")
    assert resp_demo.status_code == 200
    # When a FlowRSI position exists or is rendered in HTML, it must carry bot-badge--flowrsi
    assert "bot-badge--flowrsi" in resp_demo.text
    assert "FlowRSI" in resp_demo.text

def _position():
    return {
        "bot_id": "uk100_m15",
        "symbol": "UK100",
        "side": "BUY",
        "volume": 0.1,
        "entry_price": 10727.6,
        "account_id": "live-6094347",
    }


def test_pnl_is_broker_reported_and_never_reconstructed():
    """Unrealized P&L comes from the broker only.

    The server cannot convert a price move into account currency (UK100 is GBP-denominated,
    cTrader reports pipSize 0.1 while a former per-symbol table used 1.0), so when the bot has
    not reported, the field must read as missing instead of being invented.
    """
    from app.dashboard import _attach_live_metrics

    # Broker report present -> passed through untouched, with its age
    pos = _position()
    _attach_live_metrics(pos, {"unrealized_pnl": -0.12, "unrealized_pnl_pips": -9.0, "_reported_at": time.time() - 30},
                         {"bid": 10726.7, "ask": 10727.7, "ts": time.time() - 30})
    assert pos["unrealized_pnl"] == -0.12
    assert pos["unrealized_pnl_pips"] == -9.0
    assert 25 <= pos["pnl_age_seconds"] <= 40
    assert 25 <= pos["price_age_seconds"] <= 40
    assert pos["current_price"] == 10726.7  # BUY marks to the bid

    # No broker report -> nothing invented, even though price and entry are both known
    pos = _position()
    _attach_live_metrics(pos, None, {"bid": 10726.7, "ask": 10727.7, "ts": time.time()})
    assert pos["unrealized_pnl"] is None
    assert pos["unrealized_pnl_pips"] is None
    assert pos["pnl_age_seconds"] is None

    # No quote yet -> falls back to the entry price and reports no age
    pos = _position()
    _attach_live_metrics(pos, None, None)
    assert pos["current_price"] == 10727.6
    assert pos["price_age_seconds"] is None


def test_tick_metrics_merge_into_the_cached_position_report():
    """A tick refreshes P&L without discarding the rest of the bot's position report."""
    from app.portfolio import PortfolioManager

    pm = PortfolioManager.__new__(PortfolioManager)          # no DB needed for the cache
    pm._bot_positions_cache = {"live-1:bot-a": {"side": "BUY", "entry_price": 10727.6,
                                                "unrealized_pnl": -0.12, "unrealized_pnl_pips": -9.0,
                                                "_reported_at": 1.0}}

    pm.update_position_metrics("bot-a", 1.24, 68.0, account_id="live-1")

    entry = pm._bot_positions_cache["live-1:bot-a"]
    assert entry["unrealized_pnl"] == 1.24
    assert entry["unrealized_pnl_pips"] == 68.0
    assert entry["_reported_at"] > 1.0
    # The snapshot's other fields survive: the dashboard still needs entry/SL/TP
    assert entry["entry_price"] == 10727.6
    assert entry["side"] == "BUY"
    # The bare bot_id key is written too, which is how a position row without an account resolves
    assert pm._bot_positions_cache["bot-a"]["unrealized_pnl"] == 1.24

    # A tick can arrive before the first snapshot (e.g. right after a restart)
    pm.update_position_metrics("bot-b", -0.5, -25.0, account_id="live-1")
    assert pm._bot_positions_cache["live-1:bot-b"]["unrealized_pnl_pips"] == -25.0

    # Keys registered by earlier snapshots are refreshed even without an account_id on the tick,
    # so the key the dashboard resolves first cannot stay behind a stale snapshot value
    pm2 = PortfolioManager.__new__(PortfolioManager)
    pm2._bot_positions_cache = {"live-9:bot-c": {"entry_price": 1.1, "unrealized_pnl": 0.0}}
    pm2.update_position_metrics("bot-c", 2.5, 10.0)
    assert pm2._bot_positions_cache["live-9:bot-c"]["unrealized_pnl"] == 2.5
    assert pm2._bot_positions_cache["live-9:bot-c"]["entry_price"] == 1.1
