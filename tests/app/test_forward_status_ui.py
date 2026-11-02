"""The forward trackers (app/forward_status.py) as /api/research serves them, and the node helpers the dashboard
renderer tests share (HOSTILE, NODE, _function).

The trackers are drawn in the Research view since 2026-11-01 (tests/app/test_research_ui.py); their own endpoint
/api/forward/status was dropped on 2026-11-02, nothing but hand checks called it."""
import shutil

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


def test_a_pooled_t_that_cannot_be_computed_goes_out_as_null():
    from app.research_api import _json_safe
    assert _json_safe({"c": [{"pooled_t": float("nan"), "n": 3}]}) == {"c": [{"pooled_t": None, "n": 3}]}


def test_the_test_database_gives_the_three_candidates():
    from app.forward_status import forward_status
    from app.portfolio import get_portfolio_manager
    rows = forward_status(get_portfolio_manager().db_path)
    assert [c["key"] for c in rows] == ["ecb_f3", "ecb_e1", "gold_levels"]
    assert all(c["verdict"] in ("NO_DATA", "CONTINUE", "STOP", "PROMOTE_CHECK") for c in rows)
