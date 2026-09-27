"""Externally sourced strings are HTML-escaped by the dashboard's JS renderers.

bot_id, symbol, side, the account label, prices and times all come from a cBot's own POST payload
and are stored as sent (`sanitize_bot_id` only strips quotes, and SQLite keeps a string in a REAL
column), and the Docker panel's names and commands from bot configs. The JS renderers draw all of
these with innerHTML, so each value has to pass through `escapeHtml`:
a bot_id like `evil<img src=x onerror=alert(1)>` otherwise runs script in every dashboard
session. The Jinja-rendered first paint is autoescaped and is not covered here.
"""
import html
import json
import re
import shutil
import subprocess

import pytest

from tests._paths import DASHBOARD_JS
NODE = shutil.which("node")

HOSTILE = "evil<img src=x onerror=alert(1)>\"'"


def _script() -> str:
    return DASHBOARD_JS.read_text(encoding="utf-8")


def _function(src: str, name: str) -> str:
    """Source of `[async] function name(...) {...}`, matched on braces."""
    start = src.index(f"function {name}(")
    if src[:start].endswith("async "):
        start -= len("async ")
    depth = 0
    for i in range(src.index("{", start), len(src)):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        if depth == 0:
            return src[start:i + 1]
    raise AssertionError(f"unbalanced braces in {name}")


def test_bot_badge_escapes_the_bot_id():
    body = _function(_script(), "botBadge")
    assert "${b}" not in body
    assert "escapeHtml(b)" in body


RENDERERS = [
    "escapeHtml", "formatMoney", "pnlClass", "accountBadge", "sideChip", "pnlCellHtml",
    "sltpLineHtml", "sltpCellHtml", "tradeTimesHtml", "closeReasonHtml", "botBadge", "closeButtonHtml",
    "updateDashboard", "updateTradeHistory",
    "lbHas", "lbVnToday", "lbAddDays", "lbIsoDay", "lbRangeFor", "lbShortDay", "lbRangeText", "lbPeriodLabel",
    "applyLbControls", "lbRankCell", "lbBotCells", "lbWinRateCell", "lbProfitFactorCell", "lbTradesCell",
    "lbScoreCell", "lbReturnDdCell", "lbEmptyRow", "renderLeaderboard",
    "renderBots",
]

# A minimal DOM: every id resolves to a plain object whose innerHTML the test reads back.
HARNESS = """
const els = {};
const classList = {toggle() {}, add() {}, remove() {}, contains: () => false};
const document = {
    getElementById: id => (els[id] = els[id] || {innerHTML: '', textContent: '', className: '', style: {}, classList}),
    querySelectorAll: () => [],
};
const lucide = {createIcons() {}};
const window = {lucide};
let currentMode = 'demo';
let selectedAccountId = 'demo', historyPage = 1;
function fetchTradeHistory() {}
const closingPositions = new Set();
const LB_WEIGHT_HINTS = {usd: '', lot: ''}, LB_ROLLING = {all: 'All time'}, LB_CALENDAR = {};
let lbTab = 'usd', lbPeriod = 'all', lbDateFrom = '', lbDateTo = '', lbData = null;
%(functions)s
const H = %(hostile)s;
const out = {};
(async () => {

updateDashboard({open_positions: 1, daily_pnl: 0, total_pnl: 0, win_rate: 0, trades_today: 0, loss_streak: 0},
    [{id: 7, ctrader_id: 11, bot_id: H, symbol: H, side: H, account_type: 'demo', account_label: H, volume: H,
      entry_price: H, current_price: H, sl_price: H, tp_price: H, sl_pnl: 1, tp_pnl: 2, entry_time: H}]);
out.positions = els['positions-table'].innerHTML;

updateTradeHistory({page: 1, total_pages: 1, items: [
    {bot_id: H, symbol: H, side: H, account_type: 'demo', account_label: H, volume: H, entry_price: H,
     exit_price: H, sl_price: H, tp_price: H, pnl: 1, close_reason: H, entry_time: H, exit_time: H, duration: H}]});
out.history = els['history-table'].innerHTML;

const lbBot = {rank: 4, bot_id: H, bot_name: H, symbol_display: H, tier_badge: 'TIER_C',
    tier_label: 'Tier C', tier_color: '#fff', win_rate: 50, total_wins: 1, total_losses: 1, total_trades: 2,
    profit_factor: 1, total_pnl_usd: 1, closed_pnl_usd: 1, floating_pnl_usd: 0, composite_score: 40,
    payoff_ratio: 1.5, return_dd: 2, net_units: 3, max_dd_units: 1.5, basis: 'risk'};
renderLeaderboard({rankings: [lbBot], lot_neutral: {top_performer: null, rankings: [lbBot]}});
out.leaderboard = els['leaderboard-table-body'].innerHTML;
out.leaderboard_lot = els['leaderboard-lot-table-body'].innerHTML;

// A running, not-polling bot and a stuck, paused one, so both status branches and every button are drawn.
renderBots([
    {name: H, bot_id: H, account_type: 'demo', status: 'running', polling: false, last_poll_age_s: 30,
     open_positions: 1, description: H, run_command: H, container_id: 'abcdef1234567890'},
    {name: H, account_type: 'demo', status: H, stuck: true, paused: true, health_reason: H, description: H, run_command: H},
], true);
out.bots = els['bots-tbody'].innerHTML;

console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    src = _script()
    js = HARNESS % {
        "functions": "\n".join(_function(src, name) for name in RENDERERS),
        "hostile": json.dumps(HOSTILE),
    }
    path = tmp_path_factory.mktemp("xss") / "harness.js"
    path.write_text(js, encoding="utf-8")
    run = subprocess.run([NODE, str(path)], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.parametrize("table", [
    "positions", "history", "leaderboard", "leaderboard_lot", "bots",
])
def test_js_renderers_escape_external_strings(rendered, table):
    out = rendered[table].lower()
    assert "&lt;img" in out, "the hostile value should reach the table, escaped"
    assert "<img" not in out


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.parametrize("table, kinds", [
    ("bots", {"name", "desc", "cmd"}),
    ("positions", {"bot", "symbol", "side", "volume"}),
])
def test_buttons_hand_their_handlers_the_original_values(rendered, table, kinds):
    # The bot action buttons, the Edit form and the position Close confirm read these back
    # through dataset, which decodes the entities: escaping must not change what they see.
    attrs = re.findall(r'data-(%s)="([^"]*)"' % "|".join(kinds), rendered[table])
    assert {kind for kind, _ in attrs} == kinds
    assert all(html.unescape(value) == HOSTILE for _, value in attrs)
