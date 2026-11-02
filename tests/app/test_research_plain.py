"""research/plain.yaml (app/research_plain.py): the plain-language layer of the research screen, merged by id."""
import pytest
from fastapi.testclient import TestClient

import app.research_api as api
from app.research_plain import KINDS, PLAIN_PATH, UNITS, load_plain
from app.server import app
from tests._paths import FIXTURES_DIR

client = TestClient(app)
FIXTURE = FIXTURES_DIR / "research" / "plain.yaml"


def _write(tmp_path, text, name="plain.yaml"):
    path = tmp_path / name
    path.write_bytes(text.encode("utf-8") if isinstance(text, str) else text)
    return path


def test_missing_file_gives_nothing_and_no_warning(tmp_path):
    assert load_plain(tmp_path / "nope.yaml") == ({}, [])


@pytest.mark.parametrize("text", ["a: [unclosed", "- just\n- a list\n", b"\xff\xfe"])
def test_broken_file_warns(tmp_path, text):
    plain, warnings = load_plain(_write(tmp_path, text))
    assert plain == {} and warnings


def test_fixture_is_cleaned_and_history_sorted():
    plain, warnings = load_plain(FIXTURE, known_ids=["F3"])
    assert warnings == []
    f3 = plain["F3"]
    assert f3["name"] == "ECB F3 dễ hiểu" and f3["unit"] == "bp" and f3["note"] == "Ghi chú."
    assert f3["periods"] == {"is": {"years": "2016–2021", "n": 381, "mean": 2.39, "t": 3.29},
                             "hold": {"years": "2025–2026", "n": 117, "mean": 2.0, "t": 2.16}}
    assert [h["date"] for h in f3["history"]] == ["2026-10-15", "2026-10-16"]
    assert [h["kind"] for h in f3["history"]] == ["find", "live"]


def test_bad_fields_are_dropped_with_a_warning(tmp_path):
    path = _write(tmp_path, """
X:
  name: ok
  unit: usd
  periods:
    is: {years: "a", n: -3, mean: "abc", t: true}
    val: {years: "b", n: 4, mean: 1.5, t: 2}
    nope: {mean: 1}
  history:
    - {date: "31/10", kind: find, text: "bad date"}
    - {date: 2026-10-01, kind: boom, text: "bad kind"}
    - {date: 2026-10-02, kind: demo, text: "kept"}
    - "not a dict"
GHOST: {name: "not in the registry"}
LIST: [1, 2]
""")
    plain, warnings = load_plain(path, known_ids=["X", "LIST"])
    x = plain["X"]
    assert x["unit"] is None
    assert x["periods"] == {"is": {"years": "a", "n": None, "mean": None, "t": None},
                            "val": {"years": "b", "n": 4, "mean": 1.5, "t": 2.0}}
    assert x["history"] == [{"date": "2026-10-02", "kind": "demo", "text": "kept"}]
    assert "GHOST" not in plain and "LIST" not in plain
    text = " ".join(warnings)
    for needle in ("X", "usd", "31/10", "boom", "GHOST", "LIST", "nope"):
        assert needle in text, needle


@pytest.mark.parametrize("bad", ["history: 5", "history: true", "periods: {is: {mean: .nan, t: .inf}}",
                                 "periods: [1, 2]", "name: [a, b]"])
def test_a_malformed_entry_never_breaks_the_page(tmp_path, bad):
    path = _write(tmp_path, "X:\n  " + bad + "\n")
    plain, warnings = load_plain(path)
    x = plain.get("X")
    assert x is None or (x["history"] == [] and all(
        v is None or v == v and abs(v) != float("inf") for p in x["periods"].values() for v in (p["mean"], p["t"])))
    assert "history: 5" not in bad or warnings


def test_api_survives_a_nan_in_the_plain_file(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "REGISTRY_PATH", FIXTURES_DIR / "research" / "registry.yaml")
    monkeypatch.setattr(api, "PLAIN_PATH", _write(tmp_path, "F3:\n  unit: bp\n  periods: {is: {mean: .nan}}\n"))
    monkeypatch.setattr(api, "_rule_trackers", lambda keys: {})
    monkeypatch.setattr(api, "basis_b_tracker", lambda: {"key": "basis_b", "kind": "basis_b", "available": False})
    res = client.get("/api/research")
    assert res.status_code == 200 and res.json()["algorithms"][0]["plain"]["periods"]["is"]["mean"] is None


def test_entry_without_optional_fields():
    plain, _ = load_plain(FIXTURE)
    assert set(plain["F3"]) == {"name", "what", "why", "unit", "periods", "history", "note"}


def test_committed_plain_file_matches_the_committed_registry():
    algorithms, _, _ = api.load_registry()
    plain, warnings = load_plain(PLAIN_PATH, known_ids=[a["id"] for a in algorithms])
    assert warnings == []
    # Every entry belongs to a registry row; a registry row without an entry falls back to the registry's own text
    # (the research sessions add rows before anyone writes their plain words).
    assert set(plain) <= {a["id"] for a in algorithms}
    assert all(p["unit"] in UNITS for p in plain.values() if p["periods"])
    assert all(h["kind"] in KINDS for p in plain.values() for h in p["history"])


def test_api_attaches_plain_or_null(monkeypatch):
    monkeypatch.setattr(api, "REGISTRY_PATH", FIXTURES_DIR / "research" / "registry.yaml")
    monkeypatch.setattr(api, "PLAIN_PATH", FIXTURE)
    monkeypatch.setattr(api, "_rule_trackers", lambda keys: {})
    monkeypatch.setattr(api, "basis_b_tracker", lambda: {"key": "basis_b", "kind": "basis_b", "available": False})
    data = client.get("/api/research").json()
    rows = {a["id"]: a for a in data["algorithms"]}
    assert rows["F3"]["plain"]["unit"] == "bp" and rows["G1"]["plain"] is None
    assert "Bản dễ hiểu" not in (data["warning"] or "")          # the fixture registry has warnings of its own
