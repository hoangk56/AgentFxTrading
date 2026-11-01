"""Paper desk view: dashboard wiring and the renderer in static/js/paper_desk.js (strings pass through escapeHtml)."""
import json
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS, REPO_ROOT, dashboard_page
from tests.app.test_forward_status_ui import HOSTILE, NODE, _function

client = TestClient(app)
JS = REPO_ROOT / "static" / "js" / "paper_desk.js"


def test_dashboard_has_the_paper_desk_nav_view_and_script():
    html = client.get("/demo/dashboard").text
    assert 'data-target="view-paper-desk"' in html and 'id="view-paper-desk"' in html and 'id="pd-body"' in html
    assert 'href="#paper-desk"' in html and '<script src="/static/js/paper_desk.js' in html
    assert "targetId === 'view-paper-desk'" in dashboard_page(client) and "pdOnShow();" in dashboard_page(client)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_paper_desk_renderer_escapes_external_strings():
    dash = DASHBOARD_JS.read_text(encoding="utf-8")
    src = JS.read_text(encoding="utf-8")
    helpers = _function(dash, "escapeHtml")
    names = src[src.index("const PD_NAMES"):src.index("};", src.index("const PD_NAMES")) + 2]
    renderers = names + "\n" + "\n".join(_function(src, n) for n in ("pdNum", "pdPct", "pdNameHtml", "pdCoverageHtml", "pdWhen", "pdVerdictLabel",
                                                         "pdScoreHtml", "pdProgress", "pdStatusOf", "pdSummaryHtml", "pdHtml"))
    cov = {"analysts": [{"analyst": HOSTILE, "calls": 10, "traded": 4, "long": 3, "short": 1, "errors": 2,
                         "directional_rate": 0.4}],
           "recent_days": [{"date": HOSTILE, "symbols": 6, "calls": 24, "traded": 5, "errors": 0}],
           "days_with_calls": 1, "days_missing": [HOSTILE], "symbols": ["A"] * 6, "min_traded_for_verdict": 600}
    stat = {"n": 12, "hit": 0.5, "mean": -1.5, "t": None, "verdict": "TOO_FEW"}
    score = {"scored_at": HOSTILE, "scored_cells": 3, "cells": 6,
             "analysts": {HOSTILE: stat}, "baselines": {"always_long": dict(stat, verdict="BASELINE")}}
    script = f"{helpers}\n{renderers}\nconst d = {json.dumps({'coverage': cov, 'score': score})};\n" \
             "console.log(JSON.stringify({t: pdHtml(d), e: pdHtml({coverage: {analysts: []}, score: null})," \
             " s: pdStatusOf(d), es: pdStatusOf({coverage: {analysts: []}})}));"
    run = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    out = json.loads(run.stdout)
    assert "<img" not in out["t"].lower() and "evil&lt;img" in out["t"]
    assert "-1.50" in out["t"] and ">Chưa đủ</span>" in out["t"] and "Ngày làm việc không có lượt dự đoán" in out["t"]
    # the answer first: how far from a verdict, and the score before the coverage tables
    assert out["s"] == ["warn", "Chưa đủ để kết luận: 4 / 600 lượt có chọn hướng · với nhịp hiện tại cần thêm khoảng "
                        "30 tuần làm việc · thiếu 1 ngày làm việc"]
    assert out["t"].index("pd-stats") < out["t"].index(">Điểm<") < out["t"].index(">Từng AI<")
    assert out["es"] == ["", "Chưa có lượt dự đoán nào"]
    assert "Mốc: luôn mua" in out["t"] and "always_long" in out["t"]   # plain name first, the raw id below
    assert "Chưa có lượt dự đoán nào" in out["e"] and "Chưa có điểm" in out["e"]
