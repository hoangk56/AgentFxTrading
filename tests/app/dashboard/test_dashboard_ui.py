import time
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import dashboard_page

client = TestClient(app)

def test_ui_endpoints():
    # Test Sessions API
    resp_sess = client.get("/api/dashboard/sessions")
    assert resp_sess.status_code == 200
    data_sess = resp_sess.json()
    assert "sessions" in data_sess
    assert "sydney" in data_sess["sessions"]
    assert "killzone" not in data_sess
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
    assert 'id="profit-factor"' in html_real
    # The AI views went with the TMS / Judas / FlowRSI bots
    for gone in ("view-decisions", "view-news", "view-risk", "kz-banner", "news-assessment-modal"):
        assert gone not in html_demo, gone


def test_bot_badges_name_the_two_strategies():
    page = dashboard_page(client)
    for badge in ("bot-badge--gotobi", "bot-badge--donchian", "'Gotobi'", "'Donchian'"):
        assert badge in page, badge
    for gone in ("bot-badge--flowrsi", "bot-badge--judas", "bot-badge--tms", "TMS+ORB", "FlowRSI"):
        assert gone not in page, gone


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
    # The report's other fields survive: the dashboard still needs entry/SL/TP
    assert entry["entry_price"] == 10727.6
    assert entry["side"] == "BUY"
    # The bare bot_id key is written too, which is how a position row without an account resolves
    assert pm._bot_positions_cache["bot-a"]["unrealized_pnl"] == 1.24

    # A tick can create the entry (e.g. right after a restart)
    pm.update_position_metrics("bot-b", -0.5, -25.0, account_id="live-1")
    assert pm._bot_positions_cache["live-1:bot-b"]["unrealized_pnl_pips"] == -25.0

    # Keys registered earlier are refreshed even without an account_id on the tick,
    # so the key the dashboard resolves first cannot stay behind a stale value
    pm2 = PortfolioManager.__new__(PortfolioManager)
    pm2._bot_positions_cache = {"live-9:bot-c": {"entry_price": 1.1, "unrealized_pnl": 0.0}}
    pm2.update_position_metrics("bot-c", 2.5, 10.0)
    assert pm2._bot_positions_cache["live-9:bot-c"]["unrealized_pnl"] == 2.5
    assert pm2._bot_positions_cache["live-9:bot-c"]["entry_price"] == 1.1


def test_setup_instances_panel_is_in_docker_view():
    html = dashboard_page(client)
    docker_idx = html.find('id="view-docker"')
    logs_idx = html.find('id="view-logs"')
    panel_idx = html.find('id="setup-panel"')
    button_idx = html.find('id="setup-instances-btn"')
    assert docker_idx != -1 and panel_idx != -1 and button_idx != -1
    assert docker_idx < button_idx < panel_idx < logs_idx        # inside the Docker view, next to Add Bot
    assert "Setup Instances" in html
    for element_id in ("setup-account", "setup-new-account", "setup-acc-password", "setup-grid",
                       "setup-save-only", "setup-create-btn", "setup-results"):
        assert f'id="{element_id}"' in html, element_id
    assert 'id="setup-acc-password" type="password"' in html
    for endpoint in ("/api/setup/presets", "/api/setup/instances", "/api/setup/installed", "/api/ctrader-accounts"):
        assert endpoint in html, endpoint


def test_setup_grid_marks_cells_already_installed_for_an_account():
    html = dashboard_page(client)
    # Each preset cell carries a note slot; the installed list fills it with the account label(s)
    # without re-rendering the grid (which would drop the user's ticks).
    assert 'class="setup-cell-note"' in html
    assert "function refreshSetupInstalled" in html
    # refreshed when the panel opens and again after "Create instances"
    assert html.count("await refreshSetupInstalled()") >= 2


def test_bot_action_buttons_show_pending_state_and_polls_do_not_overlap():
    html = dashboard_page(client)
    # A docker stop/restart takes 7-10 s: the clicked row must say so instead of looking dead.
    for label in ("Starting…", "Stopping…", "Restarting…", "Deleting…"):
        assert label in html, label
    # A 10 s poll must never re-render over a pending row, nor stack up while a slow poll runs.
    assert "if (botsFetchInFlight || botActionInFlight) return;" in html


def test_active_positions_rows_have_a_close_button():
    html = dashboard_page(client)
    assert "action-close-pos" in html
    assert "fetch(`/api/positions/${d.id}/close`" in html
    assert "fetch(`/api/bot-commands/${id}`)" in html
    assert 'colspan="11" class="empty-state">No active positions' in html
    assert 'colspan="10" class="empty-state">No active positions' not in html
    # delegated once on the tbody, so rows re-rendered by updateDashboard() keep working
    assert "document.getElementById('positions-table').addEventListener('click'" in html
    assert "did not pick up the command within 15 s" in html


def test_a_failed_close_re_enables_the_button_on_screen():
    """The table can be re-rendered while a close waits, drawing a new "Closing…" button:
    a failure must reset the button in the table now, not only the detached one clicked."""
    html = dashboard_page(client)
    failure = html[html.index("async function closePosition(btn)"):]
    failure = failure[failure.index("} catch (err) {"):failure.index("} finally {")]
    assert "document.querySelectorAll(`#positions-table .action-close-pos[data-id=\"${d.id}\"]`)" in failure
    assert failure.index("closingPositions.delete(String(d.id));") < failure.index("querySelectorAll")


def test_bots_tab_has_pause_resume_and_close_and_stop():
    html = dashboard_page(client)
    for snippet in ("action-pause", "action-resume", "action-close-stop", "Close &amp; Stop",
                    "Pausing…", "Resuming…", "Closing & stopping…", "/close-and-stop", ">PAUSED</span>"):
        assert snippet in html, snippet


def test_bots_tab_flags_running_containers_that_do_not_poll():
    html = dashboard_page(client)
    assert "(isRunning && !b.polling)" in html
    assert ">NOT POLLING</span>" in html
    assert "${statusHtml}${pausedHtml}${notPollingHtml}" in html
