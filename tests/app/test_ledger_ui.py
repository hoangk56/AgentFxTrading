"""Ledger view: the dashboard wiring and the renderers in static/js/ledger.js.

Labels, account ids and notes are user or bot input and are drawn with innerHTML, so every one must pass through
the dashboard's escapeHtml."""
import json
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS, REPO_ROOT, dashboard_page

client = TestClient(app)
JS = REPO_ROOT / "static" / "js" / "ledger.js"
NODE = shutil.which("node")
HOSTILE = "evil<img src=x onerror=alert(1)>\"'"


def _function(src: str, name: str) -> str:
    start = src.index(f"function {name}(")
    depth = 0
    for i in range(src.index("{", start), len(src)):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        if depth == 0:
            return src[start:i + 1]
    raise AssertionError(f"unbalanced braces in {name}")


def test_dashboard_has_the_ledger_nav_view_and_script():
    html = client.get("/demo/dashboard").text
    assert 'data-target="view-ledger"' in html and 'id="view-ledger"' in html and 'id="lg-body"' in html
    assert '<script src="/static/js/ledger.js' in html
    page = dashboard_page(client)
    assert "targetId === 'view-ledger'" in page and "ledgerOnShow();" in page
    assert "ledgerRefreshIfShown()" in page       # the account selector refreshes it


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_ledger_renderers_escape_external_strings():
    dash = DASHBOARD_JS.read_text(encoding="utf-8")
    src = JS.read_text(encoding="utf-8")
    helpers = "\n".join(_function(dash, n) for n in ("escapeHtml", "formatMoney", "accountBadge"))
    renderers = "\n".join(_function(src, n) for n in ("lgMoney", "lgStatHtml", "lgAccountHtml", "lgPageHtml"))
    script = f"""{helpers}
{renderers}
const H = {json.dumps(HOSTILE)};
const full = {{account_id: H, label: H, account_type: 'demo',
    deposits: 500, withdrawals: 0, closed_pnl: -2.5, closed_trades: 3, expected_balance: 497.5,
    broker_balance: 1502.5, broker_balance_at_vn: H, discrepancy: 1005, balanced: false,
    unexplained: [{{log_id: H, recorded_at_vn: H, balance_before: 0, balance: 1040, delta: 1000, nearby_closes: [],
                    opening: true, earlier_closes: 2, earlier_pnl: 40}},
                  {{log_id: H, recorded_at_vn: H, balance_before: 1497.5, balance: 1502.5, delta: 5, nearby_closes: [H],
                    opening: false}}],
    movements: [{{id: H, occurred_at_vn: H, amount: 500, note: H, balance_log_id: 3}}]}};
const empty = {{account_id: H, label: H, account_type: 'live', deposits: 0, withdrawals: 0, closed_pnl: 0,
    closed_trades: 0, expected_balance: 0, broker_balance: null, discrepancy: null, movements: [], unexplained: []}};
console.log(JSON.stringify({{full: lgPageHtml({{accounts: [full], tolerance: 0.05}}),
                             empty: lgPageHtml({{accounts: [empty]}}), none: lgPageHtml({{accounts: []}})}}));
"""
    run = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    out = json.loads(run.stdout)
    for name in ("full", "empty"):
        assert "<img" not in out[name].lower(), name
        assert "evil&lt;img" in out[name], name
    assert "Ghi là khoản nạp" in out["full"] and "+$5.00" in out["full"] and "kpi-value--warn" in out["full"]
    assert "Số dư ghi nhận đầu tiên: $1,040.00" in out["full"] and "2 lệnh đóng trước đó: +$40.00" in out["full"]
    assert 'data-opening="1"' in out["full"] and "Opening balance" not in out["full"]
    assert "Chưa nhận được số dư" in out["empty"] and "Cài bot từ mẫu" in out["none"]
