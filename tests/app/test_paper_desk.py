"""Paper desk: the insert-only call log and the scoring against baselines."""
import datetime

import pytest

from app import paper_desk as pd

UTC = datetime.timezone.utc
BEFORE = datetime.datetime(2026, 11, 2, 6, 59, tzinfo=UTC)
AT_ENTRY = datetime.datetime(2026, 11, 2, 7, 0, tzinfo=UTC)


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "pd.db")
    pd.init_schema(path)
    return path


def test_record_and_load(db):
    pd.record_call("2026-11-02", "EURUSD", "macro", -1, 0.6, "why", {"atr": 1.2}, "m", now=BEFORE, db_target=db)
    rows = pd.load_calls(db)
    assert rows == [{"call_date": "2026-11-02", "symbol": "EURUSD", "analyst": "macro", "direction": -1,
                     "confidence": 0.6}]


def test_refused_at_or_after_entry_time(db):
    with pytest.raises(pd.CallRefused, match="after the 07:00 UTC entry"):
        pd.record_call("2026-11-02", "EURUSD", "macro", 1, now=AT_ENTRY, db_target=db)
    assert pd.load_calls(db) == []


def test_refuses_repeat_unknown_symbol_and_bad_direction(db):
    pd.record_call("2026-11-02", "EURUSD", "macro", 1, now=BEFORE, db_target=db)
    with pytest.raises(pd.CallRefused, match="already recorded"):
        pd.record_call("2026-11-02", "EURUSD", "macro", -1, now=BEFORE, db_target=db)
    with pytest.raises(pd.CallRefused, match="unknown symbol"):
        pd.record_call("2026-11-02", "DOGEUSD", "macro", 1, now=BEFORE, db_target=db)
    with pytest.raises(pd.CallRefused, match="direction"):
        pd.record_call("2026-11-02", "EURUSD", "tech", 2, now=BEFORE, db_target=db)
    assert len(pd.load_calls(db)) == 1


def test_module_has_no_update_or_delete():
    src = open(pd.__file__, encoding="utf-8").read().upper()
    assert "UPDATE PAPER_CALLS" not in src and "DELETE FROM" not in src and "INSERT OR REPLACE" not in src


def test_net_bp():
    assert pd.net_bp(1, 100.0, 100.5, 1.0) == pytest.approx(49.0)
    assert pd.net_bp(-1, 100.0, 100.5, 1.0) == pytest.approx(-51.0)
    assert pd.net_bp(0, 100.0, 100.5, 1.0) == 0.0


def _calls(analyst, directions):
    return [{"call_date": f"2026-11-{i + 2:02d}", "symbol": "EURUSD", "analyst": analyst, "direction": d,
             "confidence": None} for i, d in enumerate(directions)]


def test_score_hit_rate_baselines_and_skipped_unpriced():
    # entry 100, exit 101 (+100 bp) on days 1-2, 99 (-100 bp) on day 3; day 4 has no prices yet
    prices = {("2026-11-02", "EURUSD"): (99.0, 100.0, 101.0), ("2026-11-03", "EURUSD"): (100.0, 100.0, 101.0),
              ("2026-11-04", "EURUSD"): (100.0, 100.0, 99.0)}
    calls = _calls("macro", [1, 1, -1, 1]) + _calls("flat", [0, 0, 0, 0])
    out = pd.score(calls, prices, {"EURUSD": 1.0})
    m = out["analysts"]["macro"]
    assert m["n"] == 3 and m["hit"] == 1.0 and m["mean"] == pytest.approx(99.0)
    assert out["analysts"]["flat"]["n"] == 0 and out["analysts"]["flat"]["mean"] is None
    assert out["baselines"]["always_long"]["n"] == 3
    assert out["baselines"]["always_long"]["mean"] == pytest.approx((99 + 99 - 101) / 3)
    assert out["baselines"]["prev_day_momentum"]["n"] == 1        # day 1 trades long (99 -> 100); days 2 and 3 have prev == entry: no trade
    assert m["verdict"] == "TOO_FEW"


def test_verdict_needs_n_t_and_beating_baselines():
    good = {"n": 700, "t": 3.0, "beats_baselines": True}
    assert pd.verdict(good, False) == "PASS"
    assert pd.verdict({**good, "n": 599}, False) == "TOO_FEW"
    assert pd.verdict({**good, "t": 2.4}, False) == "FAIL"
    assert pd.verdict({**good, "beats_baselines": False}, False) == "FAIL"
    assert pd.verdict(good, True) == "BASELINE"
