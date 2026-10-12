"""Gotobi view: the dashboard wiring and the renderers in static/js/gotobi_calendar.js.

Bot ids, symbols and account ids come from the bots and are drawn with innerHTML, so every one must pass through
the dashboard's escapeHtml."""
import json
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS, REPO_ROOT, dashboard_page

client = TestClient(app)
JS = REPO_ROOT / "static" / "js" / "gotobi_calendar.js"
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


def test_dashboard_has_the_gotobi_nav_view_and_script():
    html = client.get("/demo/dashboard").text
    assert 'data-target="view-gotobi"' in html and 'id="view-gotobi"' in html and 'id="gc-body"' in html
    assert '<script src="/static/js/gotobi_calendar.js' in html
    page = dashboard_page(client)
    assert "targetId === 'view-gotobi'" in page and "gotobiOnShow();" in page
    assert "gotobiRefreshIfShown()" in page       # the account selector refreshes it


def _day(date, weekday, status, trades=(), real=(0, 0.0, 0), decoy=(0, 0.0, 0), other=(0, 0.0, 0)):
    b = lambda t: {"n": t[0], "pnl": t[1], "open": t[2]}
    return {"date": date, "weekday": weekday, "gotobi": status not in ("plain",), "skipped": status == "skipped",
            "status": status, "real": b(real), "decoy": b(decoy), "other": b(other), "trades": list(trades)}


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_gotobi_renderers_escape_external_strings():
    dash = DASHBOARD_JS.read_text(encoding="utf-8")
    src = JS.read_text(encoding="utf-8")
    helpers = "\n".join(_function(dash, n) for n in ("escapeHtml", "formatMoney"))
    renderers = "\n".join(_function(src, n) for n in ("gcMoney", "gcMonthLabel", "gcCellHtml", "gcMonthHtml",
                                                     "gcDayHtml"))
    trade = {"id": 1, "bot_id": HOSTILE, "account_id": HOSTILE, "symbol": HOSTILE, "side": HOSTILE, "volume": 0.1,
             "leg": "long", "decoy": False, "status": "closed", "pnl": 12.0,
             "entry_time_vn": HOSTILE, "exit_time_vn": HOSTILE}
    data = {"month": "2026-10", "today": "2026-10-12",
            "totals": {"gotobi_days": 6, "traded_days": 1, "real_trades": 2, "real_pnl": 8.5,
                       "decoy_trades": 1, "decoy_pnl": -0.4},
            "days": [_day("2026-10-01", 3, "plain", decoy=(1, -0.4, 0)),
                     _day("2026-10-05", 0, "no-trade"),
                     _day("2026-10-09", 4, "traded", trades=[trade, dict(trade, decoy=True, leg="short")],
                          real=(2, 8.5, 1)),
                     _day("2026-10-15", 3, "scheduled"),
                     _day("2026-10-20", 1, "skipped")]}
    script = f"""{helpers}
{renderers}
const data = {json.dumps(data)};
console.log(JSON.stringify({{month: gcMonthHtml(data, '2026-10-09'), day: gcDayHtml(data.days[2]),
                             empty: gcDayHtml(data.days[1]), label: gcMonthLabel('2026-10')}}));
"""
    run = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    out = json.loads(run.stdout)
    assert "<img" not in out["day"].lower() and "evil&lt;img" in out["day"]
    month = out["month"]
    # Oct 1st 2026 is a Thursday: three blank cells (Mon-Wed) before it
    assert month.count("gc-cell--blank") == 3
    for cls in ("gc-cell--traded", "gc-cell--no-trade", "gc-cell--scheduled", "gc-cell--skipped", "gc-cell--plain",
                "gc-cell--selected"):
        assert cls in month, cls
    assert "+$8.50" in month and "1 open" in month and "decoy" in month and "JP holiday" in month
    assert 'data-date="2026-10-09"' in month
    assert "Decoy" in out["day"] and "Long" in out["day"]
    assert "No Gotobi position" in out["empty"]
    assert out["label"] == "October 2026"
