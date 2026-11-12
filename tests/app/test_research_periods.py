"""Periods of the research screen (app/research_periods.py) and how the API attaches them (app/research_api.py)."""
import datetime as dt

import pytest

import app.research_api as api
from app import research_periods as rp
from app.a2_live_status import evaluate as a2_evaluate
from app.basis_b_status import evaluate as basis_evaluate

D = dt.date


@pytest.mark.parametrize("day, months, want", [
    (D(2026, 3, 31), 1, D(2026, 2, 28)),          # month end into a shorter month
    (D(2024, 3, 31), 1, D(2024, 2, 29)),          # leap year
    (D(2024, 2, 29), 12, D(2023, 2, 28)),         # leap day a year back
    (D(2026, 1, 15), 1, D(2025, 12, 15)),         # across the year
    (D(2026, 11, 13), 12, D(2025, 11, 13)),
])
def test_minus_months(day, months, want):
    assert rp.minus_months(day, months) == want


def test_windows_follow_the_calendar_and_touch_end_to_end():
    w = rp.windows(D(2026, 11, 13))
    assert w["week"] == ((D(2026, 11, 7), D(2026, 11, 13)), (D(2026, 10, 31), D(2026, 11, 6)))
    assert w["month"] == ((D(2026, 10, 14), D(2026, 11, 13)), (D(2026, 9, 14), D(2026, 10, 13)))
    assert w["year"] == ((D(2025, 11, 14), D(2026, 11, 13)), (D(2024, 11, 14), D(2025, 11, 13)))
    march = rp.windows(D(2026, 3, 31))["month"]
    # the previous month runs one month back from 28/02 by the same rule (106 does the same)
    assert march == ((D(2026, 3, 1), D(2026, 3, 31)), (D(2026, 1, 29), D(2026, 2, 28)))


def test_cell_counts_trades_inside_and_days_since_the_run_started():
    trades = [(D(2026, 11, 1), 2.0), (D(2026, 11, 7), 4.0), (D(2026, 11, 13), -1.0), (D(2026, 11, 14), 99.0)]
    c = rp.cell(trades, D(2026, 11, 7), D(2026, 11, 13), since=D(2026, 11, 10))
    assert c == {"from": "2026-11-07", "to": "2026-11-13", "days": 7, "covered": 4, "n": 2, "mean": 1.5,
                 "t": c["t"], "total": 3.0}
    assert c["t"] == pytest.approx(0.6)
    before = rp.cell(trades, D(2026, 10, 1), D(2026, 10, 31), since=D(2026, 11, 10))
    assert before["covered"] == 0 and before["n"] == 0 and before["mean"] is None and before["t"] is None
    one = rp.cell(trades, D(2026, 11, 1), D(2026, 11, 1), since=None)
    assert one["covered"] == 1 and one["n"] == 1 and one["t"] is None       # t needs two trades


def test_periods_shape():
    out = rp.periods([(D(2026, 11, 12), 1.0)], D(2026, 11, 13), D(2026, 10, 16), "bp")
    assert out["unit"] == "bp" and out["end"] == "2026-11-13" and out["since"] == "2026-10-16"
    assert set(out) == {"unit", "end", "since", "week", "month", "year"}
    assert out["week"]["current"]["n"] == 1 and out["week"]["previous"]["n"] == 0
    assert out["year"]["previous"]["covered"] == 0


def test_dated_reads_iso_strings_and_drops_bad_rows():
    rows = [("2026-11-03 07:00:00", 1), ("2026-11-03T07:00:00Z", "2.5"), (dt.datetime(2026, 11, 4, 1), 3),
            (None, 1), ("garbage", 1), ("2026-11-05", None), ("2026-11-05", float("nan")), ("2026-11-05", "x")]
    assert rp.dated(rows) == [(D(2026, 11, 3), 1.0), (D(2026, 11, 3), 2.5), (D(2026, 11, 4), 3.0)]


def _entry(tier="demo", tracker=None, history=()):
    return {"id": "X", "tier": tier, "tracker": tracker, "plain": {"history": list(history)}}


def _rules(dated, available=True):
    return {"key": "ecb_e1", "kind": "rules", "available": available, "data": {"n": len(dated), "dated": dated}}


def test_algorithm_periods_states():
    today = D(2026, 11, 13)
    assert api.algorithm_periods(_entry(), today) == (None, None)
    assert api.algorithm_periods(_entry(tracker={"kind": "unknown", "available": False}), today) == (None, None)
    assert api.algorithm_periods(_entry(tracker=_rules([], available=False)), today)[1] == \
        "Chưa đọc được lệnh của bộ theo dõi."
    assert api.algorithm_periods(_entry(tracker=_rules([])), today) == (None, "Chưa có lệnh nào đóng.")
    entry = _entry(tracker=_rules([("2026-11-12 12:00:00", 1.0), ("2026-11-02 12:00:00", -1.0)]),
                   history=[{"date": "2026-10-06", "kind": "find"}, {"date": "2026-10-16", "kind": "demo"}])
    periods, note = api.algorithm_periods(entry, today)
    assert note is None and periods["since"] == "2026-10-16" and periods["unit"] == "bp"
    assert periods["week"]["current"]["n"] == 1 and periods["month"]["current"]["n"] == 2
    # no journey date: the run starts at its first trade
    periods, _ = api.algorithm_periods(_entry(tracker=_rules([("2026-11-02", 1.0)])), today)
    assert periods["since"] == "2026-11-02"
    # a live algorithm starts at its first live event, in R for the live_r tracker
    live = _entry(tier="live", tracker={"kind": "live_r", "available": True, "data": {"dated": [("2026-11-10", 0.5)]}},
                  history=[{"date": "2026-10-01", "kind": "demo"}, {"date": "2026-10-05", "kind": "live"}])
    periods, _ = api.algorithm_periods(live, today)
    assert periods["since"] == "2026-10-05" and periods["unit"] == "R"


def test_a_broken_tracker_gives_a_note_not_an_error(monkeypatch):
    def boom(*a):
        raise ValueError("bad")
    monkeypatch.setattr(rp, "periods", boom)
    periods, note = api.algorithm_periods(_entry(tracker=_rules([("2026-11-02", 1.0)])), D(2026, 11, 13))
    assert periods is None and note == "Không tính được số theo kỳ: ValueError."


def test_payload_attaches_periods_and_keeps_raw_trades_off_the_wire(tmp_path, monkeypatch):
    reg = tmp_path / "registry.yaml"
    reg.write_text("algorithms:\n  - {id: E, name: E, tier: demo, forward: ecb_e1}\n"
                   "  - {id: P, name: P, tier: cho-kiem, forward: null}\n", encoding="utf-8")
    monkeypatch.setattr(api, "forward_status", lambda db, keys: [
        {"key": "ecb_e1", "verdict": "CONTINUE", "n": 2, "dated": [("2026-11-12 12:00:00", 1.0),
                                                                   ("2026-11-01 12:00:00", 3.0)]}])
    monkeypatch.setattr(api, "_today", lambda: D(2026, 11, 13))
    out = {a["id"]: a for a in api.research_payload(reg, tmp_path / "none.yaml")["algorithms"]}
    e = out["E"]
    assert "dated" not in e["tracker"]["data"] and e["periods_note"] is None
    assert e["periods"]["week"]["current"]["mean"] == 1.0 and e["periods"]["month"]["current"]["n"] == 2
    assert out["P"]["periods"] is None and out["P"]["periods_note"] is None


def test_basis_and_a2_hand_over_their_dated_trades():
    closed = [{"status": "closed", "symbol": "A", "entry_ms": 1, "exit_ms": 1_762_000_000_000, "fillable": 1,
               "net_book": 0.0012, "d_bp": 0},
              {"status": "closed", "symbol": "B", "entry_ms": 1, "exit_ms": 1_761_000_000_000, "fillable": 0,
               "net_book": 0.5, "d_bp": 0},
              {"status": "open", "symbol": "C", "entry_ms": 1, "d_bp": 0}]
    dated = basis_evaluate(closed, now_ms=1_763_000_000_000)["dated"]
    assert [v for _, v in dated] == [0.0, 12.0]                  # oldest exit first; not fillable counts 0
    assert dated[0][0].startswith("2025-") or dated[0][0].startswith("2026-")
    trades = [{"mode": "live", "exit_reason": "time", "exit_utc": "2026-11-10T01:00:00+00:00", "net_bp": "55.5"},
              {"mode": "dry", "exit_reason": "time", "exit_utc": "2026-11-10T01:00:00+00:00", "net_bp": "10"},
              {"mode": "live", "exit_reason": "skipped", "exit_utc": "", "net_bp": ""},
              {"mode": "live", "exit_reason": "", "exit_utc": "", "net_bp": ""}]
    assert a2_evaluate(trades, [])["dated"] == [["2026-11-10T01:00:00+00:00", 55.5]]
