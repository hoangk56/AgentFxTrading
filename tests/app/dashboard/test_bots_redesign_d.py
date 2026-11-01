"""Bot screen after redesign D step 2 (2026-11-01): Real first, Demo folded, sizing as fields, one main button by state.

The pure helpers in static/js/dashboard.js run in node; the page is checked through the test client.
"""
import json
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS
from tests.app.test_forward_status_ui import HOSTILE, NODE, _function

client = TestClient(app)
GOTOBI = ('docker run -d --name cbot-live-live-usdjpy-fix-gotobi ghcr.io/spotware/ctrader-console:latest run x.algo '
          '--symbol=USDJPY --BotId="cbot-live-live-usdjpy-fix-gotobi" --RiskPerTradeMoney=2000.0 --MaxLotsPerTrade=25 '
          '--SkipDates="2026-12-25,2026-12-31" --EmergencyStopMin=1.0')
ECB = 'docker run x --symbol=EURUSD --UsdTopOnly=true --Lots=0.01 --EmergencyStopPips=40'


def _fns(*names):
    src = DASHBOARD_JS.read_text(encoding="utf-8")
    return "\n".join(_function(src, n) for n in ("escapeHtml", "formatMoney", "signedMoney", "strategyName") + names)


def _run(names, body):
    run = subprocess.run([NODE, "-e", f"{_fns(*names)}\n{body}"], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_sizing_flags_are_read_and_rewritten_in_place():
    out = _run(("botParam", "setBotParam", "botSizingHtml"), f"const g = {json.dumps(GOTOBI)}, e = {json.dumps(ECB)};"
               "console.log(JSON.stringify({risk: botParam(g, 'RiskPerTradeMoney'), max: botParam(g, 'MaxLotsPerTrade'),"
               " sym: botParam(g, 'symbol'), skip: botParam(g, 'SkipDates'), none: botParam(e, 'RiskPerTradeMoney'),"
               " set: setBotParam(g, 'RiskPerTradeMoney', '1500'), add: setBotParam(e, 'MaxLotsPerTrade', '3'),"
               " sg: botSizingHtml(g), se: botSizingHtml(e), sn: botSizingHtml('docker run x')}));")
    assert (out["risk"], out["max"], out["sym"], out["none"]) == ("2000.0", "25", "USDJPY", None)
    assert out["skip"] == "2026-12-25,2026-12-31"
    assert "--RiskPerTradeMoney=1500 --MaxLotsPerTrade=25" in out["set"] and out["set"].count("RiskPerTradeMoney") == 1
    assert '--SkipDates="2026-12-25,2026-12-31"' in out["set"]   # the other flags are untouched
    assert out["add"].endswith(" --MaxLotsPerTrade=3")
    assert out["sg"].startswith("$2,000") and "tối đa 25 lot" in out["sg"] and out["se"] == "0.01 lot" and "—" in out["sn"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_each_state_gets_its_main_button_and_words():
    names = ("botParam", "botSizingHtml", "botState", "botReasonShort", "botNeedsAction", "botResultCells", "botRowHtml")
    bots = {
        "stuck": {"name": "a", "status": "running", "stuck": True, "polling": True},
        "deaf": {"name": "b", "status": "running", "polling": False},
        "off": {"name": "c", "status": "exited"},
        "offOnPurpose": {"name": "c2", "status": "exited", "stopped_on_purpose": True},
        "paused": {"name": "d", "status": "running", "polling": True, "paused": True},
        "ok": {"name": "cbot-live-live-usdjpy-fix-gotobi", "status": "running", "polling": True, "account_type": "live", "run_command": GOTOBI},
    }
    out = _run(names, f"const B = {json.dumps(bots)}; const o = {{}};"
               "for (const k in B) o[k] = {row: botRowHtml(B[k], k === 'ok' ? {total_pnl_usd: -12.5, total_trades: 4,"
               " profit_factor: 0.8} : null), need: botNeedsAction(B[k]), state: botState(B[k])[1]};"
               "console.log(JSON.stringify(o));")
    first_button = lambda row: row[row.index('<td class="bot-actions">'):].split('class="log-btn ')[1].split('"')[0]
    assert first_button(out["stuck"]["row"]).startswith("action-restart") and out["stuck"]["state"] == "Bị treo"
    assert first_button(out["deaf"]["row"]).startswith("action-restart") and out["deaf"]["state"] == "Không nhận lệnh"
    # nobody pressed Dừng: an outage, counted and in red; pressed on purpose: grey and not counted
    assert first_button(out["off"]["row"]).startswith("action-start") and out["off"]["state"] == "Dừng bất thường"
    assert "chưa ai bấm Dừng" in out["off"]["row"]
    assert out["offOnPurpose"]["state"] == "Đã dừng"
    assert first_button(out["paused"]["row"]) == "action-resume" and out["paused"]["state"] == "Tạm dừng"
    assert first_button(out["ok"]["row"]) == "action-pause" and out["ok"]["state"] == "Đang chạy"
    assert [out[k]["need"] for k in bots] == [True, True, True, False, False, False]
    ok = out["ok"]["row"]
    assert 'data-live="1"' in ok and 'data-symbol="USDJPY"' in ok and "Gotobi USDJPY" in ok
    assert "-$12.50" in ok and "ít lệnh" in ok and "action-delete" in ok and "action-close-stop" in ok   # PF needs 5 trades
    assert 'data-open="0"' in ok


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_sizing_fields_escape_and_only_show_the_flags_the_command_has():
    src = DASHBOARD_JS.read_text(encoding="utf-8")
    const = src[src.index("const BOT_SIZING ="):src.index("\n", src.index("const BOT_SIZING ="))]
    out = _run(("botParam", "botSizingFieldsHtml"), f"{const}\nconsole.log(JSON.stringify({{g: botSizingFieldsHtml("
               f"{json.dumps(GOTOBI)}), h: botSizingFieldsHtml('--Lots=' + {json.dumps(HOSTILE)})}}));")
    assert 'data-param="RiskPerTradeMoney"' in out["g"] and 'data-param="MaxLotsPerTrade"' in out["g"]
    assert 'data-param="Lots"' not in out["g"] and "<img" not in out["h"].lower()


def test_bot_screen_has_both_blocks_no_scope_bar_and_the_ranking_link():
    html = client.get("/real/dashboard").text
    view = html[html.index('id="view-docker"'):html.index("<!-- Ledger View")]
    for part in ("<h1>Bot</h1>", 'id="bots-status"', 'class="ov-real"', 'id="bots-tbody"', 'id="bots-demo"',
                 'id="bots-tbody-demo"', 'id="bots-period"', 'id="bot-sizing"', 'id="bot-cmd-advanced"',
                 'href="#leaderboard"'):
        assert part in view, part
    assert 'id="view-docker" class="view-section">' in html   # not data-scoped any more
    js = DASHBOARD_JS.read_text(encoding="utf-8")
    assert "confirm(`" not in js[js.index("// --- Bot screen"):js.index("// --- Setup Instances")]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_a_risk_change_is_worded_old_to_new_with_its_ratio():
    out = _run(("botParam", "setBotParam", "botSizingChanges"),
               f"const g = {json.dumps(GOTOBI)}; console.log(JSON.stringify({{"
               "a: botSizingChanges(g, setBotParam(g, 'RiskPerTradeMoney', '1500')),"
               "b: botSizingChanges(g, setBotParam(g, 'RiskPerTradeMoney', '20000')), c: botSizingChanges(g, g)}));")
    assert [c["text"] for c in out["a"]] == ["Rủi ro mỗi lệnh $2,000 → $1,500"] and out["a"][0]["ratio"] == 0.75
    assert out["b"][0]["ratio"] == 10 and out["c"] == []


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_the_detailed_ranking_keeps_its_own_mode_and_renumbers():
    data = {"rankings": [{"bot_id": "cbot-live-live-a", "rank": 1}, {"bot_id": "cbot-demo-demo-b", "rank": 2},
                         {"bot_id": "cbot-demo-demo-c", "rank": 3}],
            "lot_neutral": {"rankings": [{"bot_id": "cbot-demo-demo-c", "rank": 1}, {"bot_id": "cbot-live-live-a", "rank": 2}]}}
    out = _run(("lbOwnMode",), f"const d = {json.dumps(data)}; console.log(JSON.stringify({{demo: lbOwnMode(d, 'demo'), live: lbOwnMode(d, 'live')}}));")
    assert [(b["bot_id"], b["rank"]) for b in out["demo"]["rankings"]] == [("cbot-demo-demo-b", 1), ("cbot-demo-demo-c", 2)]
    assert out["demo"]["total_bots"] == 2 and out["demo"]["lot_neutral"]["top_performer"]["bot_id"] == "cbot-demo-demo-c"
    assert [b["bot_id"] for b in out["live"]["rankings"]] == ["cbot-live-live-a"]
