"""Forward view: the API, the dashboard wiring and the renderer in static/js/forward_status.js.

Labels and notes are drawn with innerHTML, so every string must pass through the dashboard's escapeHtml."""
import json
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS, REPO_ROOT, dashboard_page

client = TestClient(app)
JS = REPO_ROOT / "static" / "js" / "forward_status.js"
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


def test_dashboard_has_the_forward_nav_view_and_script():
    html = client.get("/demo/dashboard").text
    assert 'data-target="view-forward"' in html and 'id="view-forward"' in html and 'id="fs-body"' in html
    assert 'href="#forward"' in html and '<script src="/static/js/forward_status.js' in html
    assert "targetId === 'view-forward'" in dashboard_page(client) and "fsOnShow();" in dashboard_page(client)


def test_api_lists_every_candidate_with_a_verdict(monkeypatch):
    import app.forward_status_api as api
    monkeypatch.setattr(api, "forward_status", lambda db: [
        {"key": "x", "verdict": "CONTINUE", "pooled_t": float("nan"), "reasons": [], "manual": []}])
    body = client.get("/api/forward/status").json()           # NaN must not break the JSON
    assert body["candidates"][0]["pooled_t"] is None


def test_api_on_the_test_database_returns_the_three_candidates():
    body = client.get("/api/forward/status").json()
    assert [c["key"] for c in body["candidates"]] == ["ecb_f3", "ecb_e1", "gold_levels"]
    assert all(c["verdict"] in ("NO_DATA", "CONTINUE", "STOP", "PROMOTE_CHECK") for c in body["candidates"])


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_forward_renderer_escapes_external_strings():
    dash = DASHBOARD_JS.read_text(encoding="utf-8")
    src = JS.read_text(encoding="utf-8")
    helpers = _function(dash, "escapeHtml")
    renderers = "\n".join(_function(src, n) for n in ("fsNum", "fsListHtml", "fsRowHtml", "fsCalendarHtml", "fsTableHtml"))
    data = {"candidates": [
        {"label": HOSTILE, "tier": HOSTILE, "prereg": HOSTILE, "verdict": "STOP", "n": 60, "mean": -3.2, "cum": -192.0,
         "pooled_t": -1.4, "hold_n": 117, "reasons": [HOSTILE], "manual": [HOSTILE]},
        {"label": "ok", "tier": "DEMO", "prereg": "p", "verdict": "NO_DATA", "n": 0, "mean": None, "cum": 0.0,
         "pooled_t": None, "hold_n": 228, "reasons": [], "manual": []}]}
    script = f"{helpers}\n{renderers}\nconst d = {json.dumps(data)};\n" \
             "console.log(JSON.stringify({t: fsTableHtml(d), e: fsTableHtml({candidates: []})}));"
    run = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    out = json.loads(run.stdout)
    assert "<img" not in out["t"].lower() and "evil&lt;img" in out["t"]
    assert "fs-verdict--STOP" in out["t"] and "fs-verdict--NO_DATA" in out["t"]
    assert "-3.20" in out["t"] and "Why stopped" in out["t"] and "–" in out["t"]
    assert "No candidates" in out["e"]
