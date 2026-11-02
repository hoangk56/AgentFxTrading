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
        "rsTriedHtml", "rsStatusOf", "rsFlagOf", "rsTechHtml", "rsLiveRHtml", "rsPlainName", "rsUnitInfo", "rsVi",
        "rsSure", "rsSureHtml", "rsRunLabel", "rsRealRun", "rsBarValues", "rsTrend", "rsTrendSentence", "rsTrendHtml",
        "rsMiniBarsHtml", "rsPeriodChartHtml", "rsSureLineHtml", "rsJourneyHtml", "rsRealVerdict", "rsTrackerCount")


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
    consts = src[src.index("const RS_TIERS"):src.index("function rsNum(")]   # RS_TIERS, RS_UNITS, RS_PERIODS…
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
    assert out["status"] == ["crit", "1 tiền thật · 1 demo · 1 chờ anh quyết · 1 chạm luật dừng"]
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
    assert out["counts"] == {"all": 4, "live": 1, "demo": 1, "cho-kiem": 1, "da-loai": 1}    # unknown tier -> Chờ anh quyết
    assert out["hash"] == {"tier": "demo", "q": "vàng", "id": "G1"}
    assert out["bad"] == {"tier": None, "q": "", "id": None}
    assert out["back"].startswith("#research?") and "tier=demo" in out["back"] and "id=G1" in out["back"]
    assert out["bare"] == "#research"
    assert out["first"] == "F3" and out["picked"] == "X" and out["hidden"] == "F3"


def _plain(unit="bp", is_=None, hold=None, hold_t=None, **kw):
    periods = {}
    if is_ is not None:
        periods["is"] = {"years": "2016–2021", "n": 100, "mean": is_, "t": 3.0}
    if hold is not None:
        periods["hold"] = {"years": "2025–2026", "n": 80, "mean": hold, "t": hold_t}
    return {"name": "Tên dễ hiểu", "what": "Làm việc này.", "why": "Vì thế này.", "unit": unit, "periods": periods,
            "history": [], "note": None, **kw}


def _rules_tracker(n, mean, t, verdict="CONTINUE"):
    return {"key": "ecb_f3", "kind": "rules", "available": True,
            "data": {"verdict": verdict, "n": n, "mean": mean, "cum": n * (mean or 0), "pooled_t": 2.0, "forward_t": t,
                     "hold_n": 117, "reasons": [], "manual": []},
            "rules": {"stop_t_after": 60, "stop_t": -1.0, "stop_cum_after": None, "floor_after": None,
                      "promote_after": 100, "promote_t": 2.5}}


TREND_CASES = [  # (tier, is, hold, hold_t, real run {n, mean, t} or None) -> key, word
    ("da-loai", 2, 2, 3, None, "out", "Đã loại"),
    ("live", 0.043, 0.042, 2.9, None, "flat", "Giữ vững"),
    ("demo", 5.99, 2.87, 1.43, None, "down", "Yếu dần"),
    ("demo", 1.0, 1.3, 2.5, None, "up", "Mạnh lên"),
    ("demo", 1.0, -0.1, -1, None, "down", "Yếu đi"),
    ("demo", 1.0, 0.3, 1, None, "down", "Yếu đi"),
    ("live", 2.0, 2.0, 2, {"n": 40, "mean": -0.5, "t": -1}, "down", "Yếu đi"),
    ("live", 2.0, 2.0, 2, {"n": 40, "mean": 2.5, "t": 2.4}, "up", "Mạnh lên"),
    ("live", 2.0, 2.0, 2, {"n": 40, "mean": 1.2, "t": 1.0}, "flat", "Giữ vững"),
    ("live", 2.0, 2.0, 2, {"n": 40, "mean": 0.5, "t": 0.5}, "down", "Yếu dần"),     # 1,5 se under lúc tìm ra
    ("live", 2.0, 2.0, 2, {"n": 40, "mean": 0.9, "t": 0.3}, "flat", "Giữ vững"),    # too noisy: research decides
    ("live", 0.043, 0.042, 2.9, {"n": 42, "mean": -0.0202, "t": -0.25}, "flat", "Giữ vững"),   # Gotobi on ship day
    ("live", 2.0, 2.0, 2, {"n": 40, "mean": -0.5, "t": None}, "flat", "Giữ vững"),  # no t: research decides
    ("live", 2.0, 2.0, 2, {"n": 10, "mean": -9, "t": -3}, "flat", "Giữ vững"),   # under 30: research decides
    ("demo", -1.0, 2.0, 2, None, "unk", "Chưa rõ"),
    ("demo", -1.0, -2.0, 2, None, "down", "Yếu đi"),
    ("demo", None, 2.0, 2, None, "unk", "Chưa rõ"),
]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_trend_rule_table():
    entries = []
    for tier, is_, hold, hold_t, run, _, _ in TREND_CASES:
        tracker = _rules_tracker(run["n"], run["mean"], run["t"]) if run else None
        entries.append(_entry(tier=tier, plain=_plain("bp", is_, hold, hold_t), tracker=tracker, forward="ecb_f3"))
    out = _run(f"const e = {json.dumps(entries)};\n"
               "console.log(JSON.stringify(e.map(x => { const t = rsTrend(x); return [t.key, t.word]; })));")
    assert out == [[key, word] for *_, key, word in TREND_CASES]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_certainty_words_units_and_numbers():
    out = _run("console.log(JSON.stringify({"
               "sure: [3, 2, 1, -0.99, -1, null].map(t => rsSure(t).word), few: rsSure(null, 3).word,"
               "many: rsSure(2.1, 40).word, r: rsUnitInfo('R').scale, none: rsUnitInfo('usd'),"
               "vi: [rsVi(2.39, true), rsVi(-2.18), rsVi(286.5), rsVi(4.3, true), rsVi(0.04), rsVi(null)]}));")
    assert out["sure"] == ["Rất chắc", "Khá chắc", "Chưa chắc", "Như may rủi", "Lỗ khá rõ", "chưa có số"]
    assert out["few"] == "mới 3 lệnh, chưa đủ" and out["many"] == "Khá chắc"
    assert out["r"] == 100 and out["none"] is None
    assert out["vi"] == ["+2,39", "−2,18", "287", "+4,3", "0,04", "–"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_plain_detail_list_and_journey_escape_and_render():
    plain = _plain("bp", 2.39, 2.0, 2.16, name=HOSTILE, what=HOSTILE, why=HOSTILE, note=HOSTILE,
                   history=[{"date": "2026-10-15", "kind": "find", "text": HOSTILE},
                            {"date": "2026-10-16", "kind": "live", "text": "Tiền thật"}])
    live = _entry(plain=plain, forward="ecb_f3", tracker=_rules_tracker(3, -2.18, None))
    demo = _entry(id="d", tier="demo", plain=plain, forward="ecb_f3", tracker=_rules_tracker(3, 1.0, None))
    stop = _entry(id="s", tier="demo", plain=plain, forward="ecb_f3", tracker=_rules_tracker(60, -3, -1.5, "STOP"))
    out = _run(f"const a = {json.dumps([live, demo, stop])};\n"
               "const st = {tier: null, q: '', id: null}; const sel = rsSelection(a, st);\n"
               "console.log(JSON.stringify({live: rsDetailHtml(a[0], {}), demo: rsDetailHtml(a[1], {}),"
               "stop: rsDetailHtml(a[2], {}), list: rsListHtml(sel.ordered, sel.selected, st, {}),"
               "run: rsRealRun(a[1]), found: rsFilter(a, {q: 'img'}).length}));")
    for key in ("live", "demo", "stop", "list"):
        assert "<img" not in out[key].lower() and "evil&lt;img" in out[key], key
        assert "undefined" not in out[key] and "NaN" not in out[key], key
    live_html = out["live"]
    assert "Làm gì" in live_html and "Vì sao có lãi" in live_html and "Hành trình" in live_html
    assert "Kiểm cuối lãi bằng 84% lúc tìm ra." in live_html and "Chạy thật: 3/100 lệnh, chưa đủ để kết luận." in live_html
    assert "15/10/2026" in live_html and "rs-ev--live" in live_html and '<details class="rs-tech">' in live_html
    assert "rs-chart" in live_html and "−2,18" in live_html and "mới 3 lệnh, chưa đủ" in live_html
    assert "Chạy demo" in out["demo"] and "Chạy thật" not in out["demo"]
    assert out["run"]["label"] == "Chạy demo" and out["run"]["n"] == 3
    assert "Đã chạm luật dừng đăng ký trước." in out["stop"]
    assert out["list"].count("rs-mini") == 3 and "fs-verdict--STOP" in out["list"] and "CONTINUE" not in out["list"]
    assert out["found"] == 3                                         # search reaches the plain name


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_fallback_without_plain_and_unit_mismatch_and_chart_edges():
    bare = _entry(plain=None, description="Mô tả cũ")
    mismatch = _entry(plain=_plain("R", 0.043, 0.042, 2.9), forward="ecb_f3", tracker=_rules_tracker(40, 2, 3))
    edges = _entry(tier="demo", plain=_plain("bp", -2, 3, 1, periods={
        "is": {"years": "a", "n": None, "mean": -2, "t": None}, "val": {"years": "b", "n": 5, "mean": 0, "t": 0},
        "hold": {"years": "c", "n": 9, "mean": 3, "t": 1}}))
    out = _run(f"const a = {json.dumps([bare, mismatch, edges])};\n"
               "console.log(JSON.stringify({bare: rsDetailHtml(a[0], {}), bareRow: rsMiniBarsHtml(a[0]),"
               "bareTrend: rsTrend(a[0]).word, run: rsRealRun(a[1]), mis: rsPeriodChartHtml(a[1]),"
               "edges: rsPeriodChartHtml(a[2]), mini: rsMiniBarsHtml(a[2])}));")
    assert "Mô tả cũ" in out["bare"] and "Sổ chưa có số của từng giai đoạn." in out["bare"]
    assert "Sổ chưa ghi mốc thời gian." in out["bare"] and "undefined" not in out["bare"]
    assert out["bareRow"] == "" and out["bareTrend"] == "Chưa rõ"
    assert out["run"] is None and "chưa có" in out["mis"]
    for svg in (out["edges"], out["mini"], out["mis"]):
        assert "NaN" not in svg and "Infinity" not in svg
    assert out["edges"].count("<line") == 1 and "−2" in out["edges"] and ">0<" in out["edges"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_run_sentence_never_invents_an_empty_run():
    zero = _rules_tracker(0, None, None)
    zero["data"]["verdict"] = "NO_DATA"
    off = {"key": "ecb_f3", "kind": "rules", "available": False, "message": "chưa có dữ liệu"}
    cases = {
        "zero": _entry(tier="demo", plain=_plain("bp", 2, 2, 2), forward="ecb_f3", tracker=zero),
        "off": _entry(tier="demo", plain=_plain("bp", 2, 2, 2), forward="ecb_f3", tracker=off),
        "mismatch": _entry(plain=_plain("R", 0.04, 0.04, 2), forward="ecb_f3", tracker=_rules_tracker(25, 1, 1)),
        "noplain": _entry(tier="demo", plain=None, forward="ecb_f3", tracker=_rules_tracker(25, 1, 1)),
        "noisy": _entry(plain=_plain("R", 0.043, 0.042, 2.9), forward=None, tracker={
            "key": "live_r", "kind": "live_r", "available": True,
            "data": {"n": 42, "mean": -0.0202, "forward_t": -0.25, "skipped": 0, "since": "2026-09-30"}}),
    }
    out = _run(f"const c = {json.dumps(cases)};\n"
               "console.log(JSON.stringify(Object.fromEntries(Object.entries(c).map(([k, e]) => "
               "[k, rsTrend(e).sentence + ' | ' + rsDetailHtml(e, {})]))));")
    assert "Chạy demo: chưa có lệnh nào." in out["zero"]
    assert "chưa đọc được" in out["off"] and "chưa có lệnh nào" not in out["off"]
    for key in ("mismatch", "noplain"):
        assert "chưa có lệnh nào" not in out[key], key
    assert "chưa đủ chắc để đổi kết luận" in out["noisy"].split(" | ")[0]
    assert "chưa trừ phí hoa hồng" in out["noisy"]
