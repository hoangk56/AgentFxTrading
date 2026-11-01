"""Overview after redesign D (2026-11-01): Real and Demo on one page, Cần làm for both modes, in-page confirmation.

The pure renderers of static/js/overview_alerts.js, overview_demo.js and confirm_dialog.js run in node with hostile
strings; the page and the server are checked through the test client.
"""
import json
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS, REPO_ROOT
from tests.app.test_forward_status_ui import HOSTILE, NODE, _function

client = TestClient(app)
JS = REPO_ROOT / "static" / "js"


def _run(functions: str, body: str):
    run = subprocess.run([NODE, "-e", f"{functions}\n{body}"], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


def _alert_functions():
    dash = DASHBOARD_JS.read_text(encoding="utf-8")
    alerts = (JS / "overview_alerts.js").read_text(encoding="utf-8")
    confirm = (JS / "confirm_dialog.js").read_text(encoding="utf-8")
    return "\n".join([_function(dash, "escapeHtml")]
                     + [_function(alerts, n) for n in ("ovAlertActions", "ovModeChip", "ovSortAlerts", "ovTodoHtml",
                                                         "ovStatus", "ovLogsUrl")]
                     + [_function(confirm, "confirmWordFor")])


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_todo_rows_escape_bot_strings_put_real_first_and_carry_their_buttons():
    alerts = [
        {"level": "warn", "kind": "restarted", "bot": "cbot-demo-demo-xauusd-levels-gold50", "mode": "demo",
         "container": "cbot-demo-demo-xauusd-levels-gold50", "message": HOSTILE},
        {"level": "crit", "kind": "stale_price", "bot": HOSTILE, "mode": "live", "container": HOSTILE, "message": "x"},
        {"level": "crit", "kind": "docker_down", "bot": "docker", "mode": "all", "message": "no docker"},
    ]
    out = _run(_alert_functions(), f"const a = {json.dumps(alerts)};"
               "console.log(JSON.stringify({h: ovTodoHtml(a), order: ovSortAlerts(a).map(x => x.mode),"
               " s: ovStatus(a), quiet: ovStatus([]), demoOnly: ovStatus([a[0]])}));")
    html = out["h"]
    assert "<img" not in html.lower() and "evil&lt;img" in html
    assert out["order"] == ["live", "all", "demo"]
    assert html.index("mode-chip--live") < html.index("mode-chip--demo")
    assert 'data-action="restart"' in html and 'data-action="logs"' in html
    assert out["s"] == {"cls": "crit", "text": "2 việc tiền thật cần xử lý ngay · Demo có 1 cảnh báo"}
    assert out["quiet"] == {"cls": "ok", "text": "Tiền thật: mọi bot chạy bình thường"}
    assert out["demoOnly"]["cls"] == "warn" and out["demoOnly"]["text"].startswith("Tiền thật: mọi bot")


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_each_alert_kind_gets_the_button_that_fixes_it():
    out = _run(_alert_functions(), "console.log(JSON.stringify(['bot_stopped','restart_failed','stale_price',"
               "'feed_stalled','restarted','docker_down'].map(k => ovAlertActions({kind: k}).map(x => x[0]))));")
    assert out == [["start", "logs"], ["restart", "logs"], ["restart", "logs"], ["logs"], ["logs"], []]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_logs_link_opens_the_bots_own_mode_and_the_confirm_word_is_its_pair():
    out = _run(_alert_functions(), "console.log(JSON.stringify({"
               "same: ovLogsUrl('live', 'cbot-live-live-gbpjpy-fix-gotobi'),"
               "other: ovLogsUrl('demo', 'cbot-demo-demo-eurusd-ecb-e1'),"
               "w1: confirmWordFor('cbot-live-live-gbpjpy-fix-gotobi'),"
               "w2: confirmWordFor('cbot-live-live-us500-x-y', ''), w3: confirmWordFor('odd-name'),"
               "w4: confirmWordFor('anything', 'xauusd'), w5: confirmWordFor('cbot-demo-usdjpy-fix-gotobi'),"
               "w6: confirmWordFor('cbot-demo-demo-xauusd-levels-gold50')}));")
    assert out["same"] == "#logs?q=cbot-live-live-gbpjpy-fix-gotobi"
    assert out["other"] == "#logs?q=cbot-demo-demo-eurusd-ecb-e1"   # one page for both modes since step 4
    assert (out["w1"], out["w2"], out["w3"], out["w4"]) == ("GBPJPY", "US500", "odd-name", "XAUUSD")
    assert (out["w5"], out["w6"]) == ("USDJPY", "XAUUSD")   # the docs' shorter names and the gold bot


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_demo_row_figures():
    dash = DASHBOARD_JS.read_text(encoding="utf-8")
    demo = (JS / "overview_demo.js").read_text(encoding="utf-8")
    fns = "\n".join([_function(dash, n) for n in ("escapeHtml", "formatMoney", "pnlClass", "signedMoney")]
                    + [_function(demo, "ovDemoFigsHtml")])
    out = _run(fns, "console.log(JSON.stringify({h: ovDemoFigsHtml({daily_pnl: -42.1, month_pnl: 88.3,"
               " account_equity: 99837.7}, 1), e: ovDemoFigsHtml(null, 0)}));")
    assert "-$42.10" in out["h"] and "+$88.30" in out["h"] and "$99,837.70" in out["h"] and "<b>1</b> lệnh" in out["h"]
    assert out["e"] == "Chưa tải được số liệu demo"


def test_overview_has_no_mode_switch_in_the_topbar_and_both_blocks():
    html = client.get("/demo/dashboard").text
    topbar = html[html.index('<header class="topbar">'):html.index("</header>")]
    assert "trade-mode-switch" not in html and "account-selector" not in html and 'id="todo-pill"' in topbar
    # Step 4: no page-wide scope at all; Lịch, Xếp hạng chi tiết and Nhật ký carry their own switch
    assert 'id="scope-bar"' not in html and "data-scoped" not in html and "🔴" not in html
    for seg in ('id="gc-mode"', 'id="lb-mode"', 'id="log-mode"'):
        assert seg in html, seg
    for part in ('<h1>Tổng quan</h1>', 'id="ov-todo"', 'class="ov-real"', 'id="ov-demo"',
                 'data-upcoming-account="live"', 'data-upcoming-account="demo"', 'id="confirm-dialog"',
                 "/static/js/overview_demo.js", "/static/js/confirm_dialog.js"):
        assert part in html, part


def test_overview_first_paint_is_the_live_accounts_on_either_url(monkeypatch):
    import app.dashboard as dashboard
    seen = []
    real = dashboard.get_portfolio_summary
    monkeypatch.setattr(dashboard, "get_portfolio_summary", lambda acc="all": seen.append(acc) or real(acc))
    for url in ("/demo/dashboard", "/real/dashboard"):
        assert client.get(url).status_code == 200
    assert seen == ["live", "live"]


def test_overview_script_reads_the_live_scope_not_the_scope_bar():
    js = DASHBOARD_JS.read_text(encoding="utf-8")
    refresh = js[js.index("async function refreshDashboardData()"):js.index("bindModeSeg('lb-mode'")]
    assert "selectedAccountId" not in refresh and "OV_ACCOUNT" in refresh
    assert "ws.send(JSON.stringify({type:'subscribe',account_id:OV_ACCOUNT,mode:'real'}))" in js
    assert "bindModeSeg('lb-mode'" in js and "bindModeSeg('log-mode'" in js
    close = js[js.index("async function closePosition(btn)"):js.index("closingPositions.add(String(d.id));")]
    assert "askConfirm(" in close and "confirm(`" not in close
