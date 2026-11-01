"""/api/forward/status, and the node helpers the dashboard renderer tests share (HOSTILE, NODE, _function).

The trackers are drawn in the Research view since 2026-11-01: tests/app/test_research_ui.py covers that screen."""
import shutil

from fastapi.testclient import TestClient

from app.server import app

client = TestClient(app)
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
