"""Research view: dashboard wiring and the renderers in static/js/research.js (strings pass through escapeHtml)."""
import json
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.server import app
from tests._paths import DASHBOARD_JS, REPO_ROOT, dashboard_page
from tests.app.test_forward_status_ui import HOSTILE, NODE, _function

client = TestClient(app)
JS = REPO_ROOT / "static" / "js" / "research.js"
PURE = ("rsNum", "rsTierOf", "rsTierLabel", "rsFold", "rsMatches", "rsFilter", "rsCounts", "rsParseHash", "rsHashFor",
        "rsSelection", "rsVerdictLabel", "rsVerdictHtml", "rsListItemsHtml", "rsCode", "rsChipsHtml",
        "rsItemStateHtml", "rsListHtml", "rsResearchHtml", "rsStatsHtml", "rsTone", "rsRulesWords", "rsCalendarHtml",
        "rsRulesTrackerHtml", "rsFillable", "rsBasisHtml", "rsTrackerHtml", "rsDetailHtml",
        "rsTriedHtml", "rsStatusOf")


def test_dashboard_has_the_research_nav_view_and_script():
    html = client.get("/").text
    assert 'data-target="view-research"' in html and 'id="view-research"' in html and 'id="rs-grid"' in html
    assert 'href="#research"' in html and '<script src="/static/js/research.js' in html
    assert ">Nghiên cứu</span>" in html and "view-forward" not in html
    page = dashboard_page(client)
    assert "targetId === 'view-research'" in page and "rsOnShow();" in page


def _run(body: str) -> dict:
    dash = DASHBOARD_JS.read_text(encoding="utf-8")
    src = JS.read_text(encoding="utf-8")
    consts = src[src.index("const RS_TIERS"):src.index("function rsNum(")]
    script = "\n".join([_function(dash, "escapeHtml"), consts] + [_function(src, n) for n in PURE] + [body])
    run = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


def _entry(**kw):
    base = {"id": HOSTILE, "name": HOSTILE, "description": HOSTILE, "market": HOSTILE, "round": HOSTILE,
            "tier": "live", "tier_reason": HOSTILE, "research": {"is": HOSTILE, "hold": HOSTILE}, "forward": None,
            "bot": HOSTILE, "prereg": HOSTILE, "report": HOSTILE, "tracker": None}
    return {**base, **kw}


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_research_renderers_escape_external_strings():
    rules = {"key": "gold_levels", "kind": "rules", "available": True,
             "data": {"verdict": "STOP", "n": 60, "mean": -3.2, "cum": -192.0, "pooled_t": -1.4, "hold_n": 228,
                      "reasons": [HOSTILE], "manual": [HOSTILE]},
             "rules": {"stop_t_after": None, "stop_t": -1.0, "stop_cum_after": 60, "floor_after": 120,
                       "promote_after": 100, "promote_t": 2.5}}
    basis = {"key": "basis_b", "kind": "basis_b", "available": True,
             "data": {"has_secret": False, "verdict": "CONTINUE", "verdict_reason": HOSTILE, "signals": 3,
                      "fillable": 1, "not_fillable": 1, "unknown_borrow": 1, "cum_net_bp": 4.0, "mean_net_bp": 2.0,
                      "pooled_t": None, "last_run": HOSTILE, "last_error": HOSTILE,
                      "open": [{"coin": HOSTILE, "entry_time": HOSTILE, "d_bp": -50, "hours_open": 1.5}],
                      "closed": [{"coin": HOSTILE, "entry_time": HOSTILE, "exit_time": HOSTILE, "hold_h": 4,
                                  "net_bp_registered": 5.5, "net_bp_book": -1, "fund_bp": 0.5, "fillable": False,
                                  "borrow_rate_y": 0.12, "inventory_usd": 1500}],
                      "rules": {"stop_after": 40, "stop_not_fillable_share": 0.3, "promote_t": 2.5,
                                "hold": {"n": 100, "mean_bp": 9, "t": 14}}}}
    data = {"gold_calendar": {"valid_through": HOSTILE, "days_left": 5},
            "algorithms": [_entry(forward="gold_levels", tracker=rules),
                           _entry(id="b", tier="demo", forward="basis_b", tracker=basis),
                           _entry(id="p", tier="cho-kiem"), _entry(id="d", tier="da-loai")],
            "tried": [{"round": HOSTILE, "name": HOSTILE, "reason": HOSTILE, "report": HOSTILE}]}
    out = _run(f"const d = {json.dumps(data)};\n"
               "const st = {tier: null, q: '', id: null};\n"
               "const sel = rsSelection(d.algorithms, st);\n"
               "console.log(JSON.stringify({"
               "rules: rsDetailHtml(d.algorithms[0], d), basis: rsDetailHtml(d.algorithms[1], d),"
               "list: rsListHtml(sel.ordered, sel.selected, st, {}),"
               "chips: rsChipsHtml(rsCounts(d.algorithms), st),"
               "status: rsStatusOf(d), triedOpen: rsTriedHtml(d.tried, true),"
               "triedShut: rsTriedHtml(d.tried, false), none: rsDetailHtml(null, d),"
               "basisOff: rsBasisHtml({available: false, data: {has_secret: false, verdict: 'NO_DATA'}}),"
               "noTracker: rsTrackerHtml(d.algorithms[2], d)}));")
    for key, html in out.items():
        assert "<img" not in str(html).lower(), key
    assert "evil&lt;img" in out["rules"] and "evil&lt;img" in out["basis"] and "evil&lt;img" in out["triedOpen"]
    assert "fs-verdict--STOP" in out["rules"] and ">Dừng</span>" in out["rules"] and "-3.20" in out["rules"]
    assert "Dừng nếu sau 60 lệnh, tổng ròng &lt; 0." in out["rules"] and "&amp;lt;" not in out["rules"]
    assert "Đủ điều kiện xét khi có ít nhất 100 lệnh và t gộp ≥ 2.5." in out["rules"] and "Lịch mốc giá vàng" in out["rules"]
    assert "Chưa có API secret: chưa đo được lượng coin vay được và lãi vay" in out["basis"]
    assert "12.00 %" in out["basis"] and ">Không</span>" in out["basis"] and "Đang mở (1)" in out["basis"]
    assert "Dừng nếu sau 40 tín hiệu, tổng ròng &lt; 0, hoặc hơn 30 % tín hiệu" in out["basis"]
    assert "thu gọn sẵn" in out["list"] and 'data-rs-group="da-loai" aria-expanded="false"' in out["list"]
    assert 'data-rs-id="d"' not in out["list"] and "is-selected" in out["list"]
    assert "Tất cả <b>4</b>" in out["chips"] and "Demo <b>1</b>" in out["chips"]
    # the title line counts the tiers and names the tracker that hit its stop rule
    assert out["status"] == ["crit", "1 đang live · 1 chạy demo · 1 chờ kiểm · 1 chạm luật dừng"]
    assert 'aria-expanded="true"' in out["triedOpen"] and "<table" not in out["triedShut"] and "1 hướng" in out["triedShut"]
    assert "Không có thuật toán nào khớp bộ lọc" in out["none"]
    assert "Chưa có dữ liệu" in out["basisOff"] and "API secret" not in out["basisOff"]
    assert "Không có bot kiểm chứng" in out["noTracker"] and "Lỗi lần chạy đó" in out["basis"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_research_filter_search_hash_and_selection():
    entries = [{"id": "F3", "name": "ECB F3", "tier": "live"}, {"id": "G1", "name": "Vàng mốc $50", "tier": "demo"},
               {"id": "X", "name": "Dừng sớm", "tier": "da-loai"}, {"id": "U", "name": "u", "tier": "odd"}]
    out = _run(f"const e = {json.dumps(entries)};\n"
               "console.log(JSON.stringify({"
               "vang: rsFilter(e, {q: 'vang'}).map(x => x.id), dung: rsFilter(e, {q: 'DUNG'}).map(x => x.id),"
               "demo: rsFilter(e, {tier: 'demo', q: ''}).map(x => x.id), counts: rsCounts(e),"
               "hash: rsParseHash('#research?tier=demo&q=v%C3%A0ng&id=G1'), bad: rsParseHash('#forward?tier=nope'),"
               "back: rsHashFor({tier: 'demo', q: 'vàng', id: 'G1'}), bare: rsHashFor({tier: null, q: ' ', id: null}),"
               "first: rsSelection(e, {tier: null, q: '', id: null}).selected.id,"
               "picked: rsSelection(e, {tier: null, q: '', id: 'X'}).selected.id,"
               "hidden: rsSelection(e, {tier: 'live', q: '', id: 'G1'}).selected.id}));")
    assert out["vang"] == ["G1"] and out["dung"] == ["X"] and out["demo"] == ["G1"]
    assert out["counts"] == {"all": 4, "live": 1, "demo": 1, "cho-kiem": 1, "da-loai": 1}    # unknown tier -> Chờ kiểm
    assert out["hash"] == {"tier": "demo", "q": "vàng", "id": "G1"}
    assert out["bad"] == {"tier": None, "q": "", "id": None}
    assert out["back"].startswith("#research?") and "tier=demo" in out["back"] and "id=G1" in out["back"]
    assert out["bare"] == "#research"
    assert out["first"] == "F3" and out["picked"] == "X" and out["hidden"] == "F3"
