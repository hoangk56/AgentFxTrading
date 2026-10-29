"""Backtest page: the dashboard wiring and the renderers in static/js/backtest.js.

Strings the renderers draw come from a bot's run_command (names, symbols), the cBot metadata (group
and parameter labels), the user (notes, parameter values) and a container's log (errors). They are all
drawn with innerHTML, so each one must pass through the dashboard's escapeHtml."""
import json
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS, REPO_ROOT, dashboard_page

client = TestClient(app)
JS = REPO_ROOT / "static" / "js" / "backtest.js"
DASHBOARD = REPO_ROOT / "templates" / "dashboard.html"
NODE = shutil.which("node")
HOSTILE = "evil<img src=x onerror=alert(1)>\"'"


def _function(src: str, name: str) -> str:
    """Source of `function name(...) {...}`, matched on braces (same as tests/test_dashboard_xss.py)."""
    start = src.index(f"function {name}(")
    depth = 0
    for i in range(src.index("{", start), len(src)):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        if depth == 0:
            return src[start:i + 1]
    raise AssertionError(f"unbalanced braces in {name}")


def test_dashboard_has_the_backtest_nav_view_and_script():
    html = client.get("/demo/dashboard").text
    assert 'data-target="view-backtest"' in html and 'id="view-backtest"' in html
    assert '<script src="/static/js/backtest.js' in html and " defer></script>" in html
    for element_id in ("bt-form-panel", "bt-bot", "bt-start", "bt-end", "bt-data-mode", "bt-spread-wrap",
                       "bt-spread", "bt-balance", "bt-note", "bt-params", "bt-locked", "bt-run-btn", "bt-form-msg",
                       "bt-form-toggle", "bt-form-body", "bt-form-summary", "bt-compare-btn", "bt-jobs-tbody",
                       "bt-pager", "bt-modal", "bt-modal-title", "bt-modal-body", "bt-modal-prev", "bt-modal-next",
                       "bt-modal-close", "bt-runs-info", "bt-parallel"):
        assert f'id="{element_id}"' in html, element_id


def test_switch_view_opens_the_backtest_page():
    html = dashboard_page(client)
    assert "targetId === 'view-backtest'" in html and "btOnShow();" in html


def test_backtest_js_is_served_and_uses_the_api():
    resp = client.get("/static/js/backtest.js")
    assert resp.status_code == 200 and "function btOnShow" in resp.text
    for route in ("/api/backtests/sources", "/params", "/api/backtests", "/cancel", "/report.json"):
        assert route in resp.text, route


def test_the_form_offers_only_the_bots_data_modes():
    src = JS.read_text(encoding="utf-8")
    apply = _function(src, "btApplyDataModes")
    assert "source.data_modes" in apply and "option.disabled = !modes.includes(option.value)" in apply
    assert "if (!modes.includes(select.value)) select.value = modes[0];" in apply
    assert _function(src, "btLoadParams").index("btApplyDataModes();") < _function(src, "btLoadParams").index("await")


def test_best_value_rules():
    src = JS.read_text(encoding="utf-8")
    assert "['max_equity_dd_pct', 'Sụt giảm tối đa %', 'min', 'pct']" in src
    assert "['avg_loss', 'Lỗ TB (lần chốt)', 'zero', 'money']" in src
    assert "['position_win_rate', 'Tỷ lệ thắng % (lệnh)', 'max', 'num']" in src
    assert "['avg_position_loss', 'Lỗ TB (lệnh)', 'zero', 'money']" in src
    assert "['full_loss_pct', 'Lỗ nguyên lệnh %', 'min', 'num']" in src


def test_the_avg_win_loss_pair_may_wrap_in_its_card():
    # Two amounts do not fit one ninth of the KPI row; .kpi-value would clip the loss.
    css = (REPO_ROOT / "static" / "css" / "dashboard.css").read_text(encoding="utf-8")
    assert ".kpi-value.bt-kpi-wrap{white-space:normal}" in css


def test_job_list_heads_position_columns():
    html = client.get("/demo/dashboard").text
    assert "<th>% thắng (lệnh)</th>" in html and "<th>Số lệnh</th>" in html


HARNESS = r"""
%(escape)s
%(js)s
const H = %(hostile)s;
const out = {};
out.sources = btSourceOptionsHtml([{name: H, supported: false, reason: H}, {name: H, supported: true, reason: ''}]);
const view = {timeframes: ['Hour', H], groups: [{name: H, params: [
    {key: H, label: H, type: 'String', bot_value: H, default: H},
    {key: 'StopMode', label: H, type: 'Enum', bot_value: H, enum_values: [H, 'Atr']},
    {key: 'AtrPeriod', label: 'Fast', type: 'Integer', bot_value: H, min: H, max: 50},
    {key: 'TrendTimeFrame', label: 'TF', type: 'TimeFrame', bot_value: 'Hour'},
    {key: 'ShowLogs', label: 'Logs', type: 'Boolean', bot_value: 'true'}]}]};
const overrides = {AtrPeriod: H};
overrides[H] = H;
out.params = btParamGroupsHtml(view, overrides, new Set([H]));
out.locked = btLockedHtml({[H]: H});
const job = {id: 3, bot_name: H, symbol: H, period: H, start_date: H, end_date: H, data_mode: H, note: H,
    status: 'done', overrides: {[H]: {from: H, to: H}}, algo_build_time: H,
    summary: {net_profit: H, profit_factor: 1.2, win_rate: 50, max_equity_dd_pct: 4, total_trades: 10,
              starting_capital: 10000},
    report: {trades: [{entry_time: H, close_time: H, direction: H, lots: H, entry_price: H, close_price: H,
                       pips: H, net: H, commissions: 0, swaps: 0}],
             parameters: {[H]: H, BotId: 'bt-3'}, equity: [], pnl_by_hour: [], pnl_by_weekday: []}};
out.rows = btJobRowsHtml([job, {...job, id: 4, status: 'failed', error: H},
                          {...job, id: 5, status: 'running', phase: H, progress: 42}], new Set([3]));
out.detail = btDetailHtml(job);
out.title = btDetailTitleHtml(job);
out.pages = [btPageList(1, 1), btPageList(1, 3), btPageList(6, 12), btPageList(12, 12)];
out.pager = [btPagerHtml(2, 20, 57), btPagerHtml(1, 20, 0), btPagerHtml(1, 50, 45)];
out.failed = btDetailHtml({...job, status: 'failed', error: H});
const other = {...job, id: 6, start_date: '2026-01-01',
               report: {...job.report, parameters: {[H]: 'other', BotId: 'bt-6'}}};
out.compare = btCompareHtml([job, other]);
out.diff = btParamDiff([job, other]);
out.warnings = btCompareWarnings([job, other]);
const stats = {net_profit: -3151.04, roi_pct: -31.5, profit_factor: 0.55, max_equity_dd_pct: 32.4,
               commissions: -342.62, swaps: -94.04, win_rate: 56.2, total_trades: 379, avg_win: 18.2,
               avg_loss: -42.33, positions: 270, position_win_rate: 42.22, avg_position_win: 33.84,
               avg_position_loss: -44.93, full_loss_pct: 57.78};
out.kpi = btKpiCardsHtml(stats);
out.kpiOld = btKpiCardsHtml({...stats, positions: undefined, position_win_rate: undefined,
                             avg_position_win: undefined, avg_position_loss: undefined, full_loss_pct: undefined});
out.rowNew = btJobRowsHtml([{...job, summary: stats}], new Set());
out.rowOld = btJobRowsHtml([{...job, summary: {win_rate: 56.2, total_trades: 379}}], new Set());
out.best = [btBestIndex([1, 3, 2], 'max'), btBestIndex([1, 3, 2], 'min'), btBestIndex([-5, -1, 2], 'zero'),
            btBestIndex([2, 2], 'max'), btBestIndex([1, 2], null)];
out.runsInfo = [btRunsInfoText({running: 1, queued: 2, total: 9}, 3),
                btRunsInfoText({}, undefined)];
out.parallel = btParallelOptionsHtml(3, 4);
console.log(JSON.stringify(out));
"""


def _render() -> dict:
    inline = DASHBOARD_JS.read_text(encoding="utf-8")
    src = HARNESS % {"escape": _function(inline, "escapeHtml"), "js": JS.read_text(encoding="utf-8"),
                     "hostile": json.dumps(HOSTILE)}
    result = subprocess.run([NODE, "-e", src], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_backtest_renderers_escape_external_strings():
    out = _render()
    for name in ("sources", "params", "locked", "rows", "detail", "title", "failed", "compare"):
        assert "<img" not in out[name], name
        assert "evil&lt;img" in out[name], name
    assert out["diff"] == [HOSTILE]                               # BotId is ignored
    assert out["warnings"] == ["khoảng ngày khác nhau"]
    assert out["best"] == [1, 0, 1, -1, -1]
    assert out["runsInfo"] == ["1/3 đang chạy · 2 đang chờ", "0 đang chạy · 0 đang chờ"]
    assert out["parallel"] == ('<option value="1">1</option><option value="2">2</option>'
                               '<option value="3" selected>3</option><option value="4">4</option>')


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_position_stats_lead_and_deal_stats_stay_labelled():
    out = _render()
    kpi = out["kpi"]
    assert "Tỷ lệ thắng · lệnh" in kpi and "42.2%" in kpi and "56.2% theo lần chốt" in kpi
    assert ">270<" in kpi and "379 lần chốt" in kpi
    assert "bt-kpi-wrap\">+$33.84 / −$44.93" in kpi and "mỗi lần chốt +$18.20 / −$42.33" in kpi
    assert "Lỗ nguyên lệnh" in kpi and "57.8%" in kpi
    assert "—%" not in out["kpiOld"] and "56.2% theo lần chốt" in out["kpiOld"]
    assert "42.22<div" in out["rowNew"] and "56.20 lần chốt" in out["rowNew"]
    assert "270<div" in out["rowNew"] and "379 lần chốt" in out["rowNew"]
    assert "—<div" in out["rowOld"] and "56.20 lần chốt" in out["rowOld"]   # saved before position stats


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_pager_keeps_the_ends_and_the_neighbours():
    out = _render()
    assert out["pages"] == [[1], [1, 2, 3], [1, None, 5, 6, 7, None, 12], [1, None, 11, 12]]
    middle, empty, single = out["pager"]
    assert "21–40 / 57" in middle and 'data-page="2" aria-current="page" disabled' in middle
    assert 'data-page="1" aria-label="Trang trước"' in middle and 'data-page="3" aria-label="Trang sau"' in middle
    assert '<option value="20" selected>' in middle
    assert "0–0 / 0" in empty and "bt-pager-btns" not in empty      # one page: no buttons
    assert "1–45 / 45" in single and "bt-pager-btns" not in single and "<option value=\"50\" selected>" in single


def test_run_detail_and_compare_open_in_a_modal_and_the_form_folds():
    src = JS.read_text(encoding="utf-8")
    assert "btOpenModal(btDetailTitleHtml(job), btDetailHtml(job)" in src and "btOpenModal(title, btCompareHtml(jobs))" in src
    assert "`/api/backtests?page=${bt.page}&per_page=${bt.perPage}`" in src
    assert "btStore('bt-form-collapsed'" in src
    css = (REPO_ROOT / "static" / "css" / "dashboard.css").read_text(encoding="utf-8")
    assert "#bt-form-panel.bt-collapsed #bt-form-body{display:none}" in css and ".bt-modal-backdrop[hidden]{display:none}" in css
