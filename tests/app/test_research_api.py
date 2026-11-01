"""Research view API (app/research_api.py): registry parsing, a missing or broken file, the forward trackers merged into
their entries, and the basis B tracker when app/basis_b_status.py is missing, raises or answers."""
import sys
import types

import pytest
from fastapi.testclient import TestClient

import app.research_api as api
from app.server import app
from tests._paths import FIXTURES_DIR

client = TestClient(app)
FIXTURE = FIXTURES_DIR / "research" / "registry.yaml"

BASIS_STATUS = {
    "available": True, "last_run": "2026-11-01T08:00:00+00:00", "has_secret": False,
    "signals": 5, "fillable": 2, "not_fillable": 1, "unknown_borrow": 2,
    "open": [{"coin": "ABC", "entry_time": "2026-11-01T06:00:00Z", "d_bp": -55.0, "hours_open": 2.0}],
    "closed": [{"coin": "XYZ", "entry_time": "2026-10-31T01:00:00Z", "exit_time": "2026-10-31T05:00:00Z",
                "hold_h": 4.0, "net_bp_registered": 12.5, "net_bp_book": 10.0, "fund_bp": 1.5, "fillable": None,
                "borrow_rate_y": None, "inventory_usd": None}],
    "cum_net_bp": 12.5, "mean_net_bp": 12.5, "pooled_t": float("nan"), "verdict": "CONTINUE",
    "verdict_reason": "cần thêm lệnh",
    "rules": {"stop_after": 40, "stop_not_fillable_share": 0.3, "promote_t": 2.5, "hold": {"n": 100, "mean_bp": 9.0, "t": 14.0}},
}


@pytest.fixture
def registry(monkeypatch):
    monkeypatch.setattr(api, "REGISTRY_PATH", FIXTURE)


@pytest.fixture
def fake_basis(monkeypatch):
    def install(status):
        mod = types.ModuleType("app.basis_b_status")
        mod.status = status
        monkeypatch.setitem(sys.modules, "app.basis_b_status", mod)
    return install


@pytest.fixture
def no_basis(monkeypatch):
    monkeypatch.setitem(sys.modules, "app.basis_b_status", None)     # import raises ImportError


def test_load_registry_parses_rows_and_warns_about_bad_ones():
    algorithms, tried, warnings = api.load_registry(FIXTURE)
    assert [a["id"] for a in algorithms] == ["F3", "G1", "BB", "P1", "D1", "W1"]
    f3 = algorithms[0]
    assert f3["round"] == "24" and f3["tier"] == "live" and f3["forward"] == "ecb_f3"
    assert f3["research"] == {"is": "IS line", "val": "VAL line", "hold": "HOLD line"}
    assert algorithms[1]["research"] == {"hold": "HOLD only"} and algorithms[3]["forward"] is None
    assert tried[0] == {"round": "31", "name": "Storms", "reason": "No edge after costs",
                        "report": "research/results/r31/REPORT.md"}
    assert tried[1]["report"] is None
    text = " ".join(warnings)
    assert "thiếu id" in text and "id trùng" in text and "maybe" in text


def test_missing_registry_gives_an_empty_page_with_a_warning(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "REGISTRY_PATH", tmp_path / "registry.yaml")
    body = client.get("/api/research").json()
    assert body["algorithms"] == [] and body["tried"] == [] and "Chưa có sổ nghiên cứu" in body["warning"]
    assert body["generated_at"] and body["gold_calendar"] is None


@pytest.mark.parametrize("text", ["algorithms: [unclosed", "- just\n- a list\n", "\xff\xfe"])
def test_broken_registry_does_not_break_the_page(tmp_path, monkeypatch, text):
    path = tmp_path / "registry.yaml"
    path.write_bytes(text.encode("latin-1"))
    monkeypatch.setattr(api, "REGISTRY_PATH", path)
    res = client.get("/api/research")
    assert res.status_code == 200
    body = res.json()
    assert body["algorithms"] == [] and body["warning"]


def test_empty_registry_file_is_fine(tmp_path, monkeypatch):
    path = tmp_path / "registry.yaml"
    path.write_text("", encoding="utf-8")
    monkeypatch.setattr(api, "REGISTRY_PATH", path)
    body = client.get("/api/research").json()
    assert body["algorithms"] == [] and body["warning"] is None


def test_api_merges_rule_trackers_and_basis_b(registry, fake_basis):
    fake_basis(lambda: BASIS_STATUS)
    body = client.get("/api/research").json()
    by_id = {a["id"]: a for a in body["algorithms"]}

    f3 = by_id["F3"]["tracker"]
    assert f3["kind"] == "rules" and f3["available"] and f3["data"]["key"] == "ecb_f3"
    assert f3["data"]["verdict"] in ("NO_DATA", "CONTINUE", "STOP", "PROMOTE_CHECK")
    assert f3["rules"] == {"stop_t_after": 60, "stop_t": -1.0, "stop_cum_after": None, "floor_after": None,
                           "promote_after": 100, "promote_t": 2.5, "hold": {"n": 117, "mean_bp": 2.0}}
    gold = by_id["G1"]["tracker"]
    assert gold["rules"]["stop_t_after"] is None and gold["rules"]["stop_cum_after"] == 60
    assert body["gold_calendar"] is None or "valid_through" in body["gold_calendar"]

    bb = by_id["BB"]["tracker"]
    assert bb["kind"] == "basis_b" and bb["available"] and bb["data"]["has_secret"] is False
    assert bb["data"]["pooled_t"] is None                                # NaN goes out as null
    assert bb["data"]["closed"][0]["coin"] == "XYZ"

    assert by_id["P1"]["tracker"] is None and by_id["D1"]["tracker"] is None
    assert by_id["W1"]["tracker"]["available"] is False and "no_such_tracker" in by_id["W1"]["tracker"]["message"]
    assert [t["name"] for t in body["tried"]] == ["Storms", "Rolls"]


def test_only_the_wanted_rule_trackers_are_computed(registry, no_basis, monkeypatch):
    seen = []
    monkeypatch.setattr(api, "forward_status", lambda db, keys: seen.append(list(keys)) or [])
    api.research_payload()
    assert seen == [["ecb_f3", "gold_levels"]]


def test_basis_b_missing_module_shows_no_data(registry, no_basis):
    bb = {a["id"]: a for a in client.get("/api/research").json()["algorithms"]}["BB"]["tracker"]
    assert bb == {"key": "basis_b", "kind": "basis_b", "available": False, "message": "chưa có dữ liệu"}


def test_basis_b_that_raises_shows_no_data(registry, fake_basis):
    def boom():
        raise RuntimeError("binance down")
    fake_basis(boom)
    bb = {a["id"]: a for a in client.get("/api/research").json()["algorithms"]}["BB"]["tracker"]
    assert bb["available"] is False and bb["message"] == "chưa có dữ liệu"


def test_basis_b_not_available_keeps_its_data(registry, fake_basis):
    fake_basis(lambda: {**BASIS_STATUS, "available": False, "verdict": "NO_DATA"})
    bb = {a["id"]: a for a in client.get("/api/research").json()["algorithms"]}["BB"]["tracker"]
    assert bb["available"] is False and bb["data"]["has_secret"] is False


def test_a_failing_forward_status_does_not_break_the_page(registry, no_basis, monkeypatch):
    def boom(db, keys):
        raise RuntimeError("db gone")
    monkeypatch.setattr(api, "forward_status", boom)
    body = client.get("/api/research").json()
    f3 = {a["id"]: a for a in body["algorithms"]}["F3"]["tracker"]
    assert f3["available"] is False and len(body["algorithms"]) == 6
