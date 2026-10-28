"""Paper desk runner: features, answer validation, a full day with a fake model, and the Dukascopy aggregation."""
import datetime as dt
import json
import lzma
import struct

import math

import pytest

from app import paper_desk, paper_desk_runner as r
from app.dukascopy import Dukascopy

UTC = dt.timezone.utc


def synthetic_hours(first: dt.date, days: int, start=100.0):
    t0 = int(dt.datetime(first.year, first.month, first.day, tzinfo=UTC).timestamp() * 1000)
    out, price = [], start
    for i in range(days * 24):
        price += math.sin(i / 7.0) * 0.1 + 0.01
        out.append((t0 + i * 3600_000, price, price + 0.1, price - 0.1, price + 0.02))
    return out


def test_features_use_only_bars_before_entry():
    hours = synthetic_hours(dt.date(2026, 9, 1), 60)
    f = r.features(hours, "2026-10-05", events=[])
    entry_ms = int(paper_desk.entry_time("2026-10-05").timestamp() * 1000)
    assert "last_close" not in f          # raw price levels are not shown: the scale differs per feed
    assert f["weekday"] == "Monday" and f["usd_high_impact_next_24h"] == []
    assert 0.0 <= f["pos_in_20d_range"] <= 1.0
    # bars at or after the entry change nothing
    tampered = [b if b[0] < entry_ms else (b[0], 1e6, 1e6, 1e6, 1e6) for b in hours]
    assert r.features(tampered, "2026-10-05", events=[]) == f


def test_features_none_when_the_newest_bar_is_stale():
    hours = synthetic_hours(dt.date(2026, 9, 1), 60)
    entry_ms = int(paper_desk.entry_time("2026-10-05").timestamp() * 1000)
    stale = [b for b in hours if b[0] < entry_ms - 6 * 3600_000]       # nothing in the last 6 hours before entry
    assert r.features(stale, "2026-10-05", events=[]) is None
    assert r.features(hours, "2026-10-05", events=[]) is not None


def test_a_404_is_an_empty_day_not_a_retry_loop():
    d = Dukascopy("/nonexistent")
    d._request = lambda path: (404, b"x")                              # type: ignore[assignment]
    assert d._download("EURUSD", dt.date(2026, 10, 28)) == b""


def test_features_none_without_enough_history():
    assert r.features(synthetic_hours(dt.date(2026, 10, 1), 5), "2026-10-05", events=[]) is None


def test_parse_answer_validates():
    assert r.parse_answer('{"direction": -1, "confidence": 0.7, "rationale": "x"}')["direction"] == -1
    for bad in ('{"direction": 2}', '{"direction": true}', "not json", '{"confidence": 0.5}',
                '{"direction": 1, "confidence": 3}'):
        with pytest.raises(ValueError):
            r.parse_answer(bad)


def test_ask_turns_failures_into_recorded_zero():
    def boom(system, user):
        raise RuntimeError("HTTP 500")
    a = r.ask(boom, "trend", "", "EURUSD", {})
    assert a["direction"] == 0 and a["rationale"].startswith("ERROR:") and a["error"]
    assert r.ask(lambda s, u: "garbage", "trend", "", "EURUSD", {})["direction"] == 0


class FakeDuka:
    def range(self, symbol, first, last):
        return synthetic_hours(first, (last - first).days + 1)


def test_run_day_records_every_analyst_and_symbol(tmp_path):
    db = str(tmp_path / "pd.db")
    paper_desk.init_schema(db)
    seen = []

    def llm(system, user):
        seen.append(system + user)
        return json.dumps({"direction": 1, "confidence": 0.5, "rationale": "ok"})

    now = dt.datetime(2026, 10, 5, 6, 0, tzinfo=UTC)
    rows = r.run_day("2026-10-05", FakeDuka(), llm, "deepseek-chat", db_target=db, now=now)
    assert len(rows) == 6 * 4                                     # 3 analysts + chief, 6 symbols
    stored = paper_desk.load_calls(db)
    assert len(stored) == 24 and {c["analyst"] for c in stored} == {
        f"{x}@deepseek-chat" for x in ("trend", "meanrev", "risk", "chief")}
    assert any("Other analysts:" in s for s in seen)               # the chief saw the others
    assert not any("sk-" in s for s in seen)                       # nothing like a key in any prompt


def test_run_day_after_entry_time_is_refused(tmp_path):
    db = str(tmp_path / "pd.db")
    paper_desk.init_schema(db)
    late = dt.datetime(2026, 10, 5, 7, 5, tzinfo=UTC)
    with pytest.raises(paper_desk.CallRefused):
        r.run_day("2026-10-05", FakeDuka(), lambda s, u: '{"direction": 0}', "m", db_target=db, now=late)
    assert paper_desk.load_calls(db) == []


def test_dry_run_records_nothing(tmp_path):
    db = str(tmp_path / "pd.db")
    paper_desk.init_schema(db)
    now = dt.datetime(2026, 10, 5, 6, 0, tzinfo=UTC)
    rows = r.run_day("2026-10-05", FakeDuka(), lambda s, u: '{"direction": 1}', "m", db_target=db, now=now,
                     dry_run=True)
    assert rows and paper_desk.load_calls(db) == []


def test_weekday_stepping():
    assert r.next_weekday(dt.date(2026, 10, 9)) == dt.date(2026, 10, 12)       # Friday -> Monday
    assert r.prev_weekday(dt.date(2026, 10, 12)) == dt.date(2026, 10, 9)


def test_price_at_takes_first_bar_within_two_hours():
    hours = synthetic_hours(dt.date(2026, 10, 5), 2)
    ts = dt.datetime(2026, 10, 5, 7, tzinfo=UTC)
    assert r.price_at(hours, ts) == pytest.approx(hours[7][1])
    gap = [b for i, b in enumerate(hours) if i not in (7, 8, 9)]
    assert r.price_at(gap, ts) is None


def test_dukascopy_parse_aggregates_minutes_to_hours():
    scale = 1e5
    recs = []
    for minute in range(120):                    # two hours of minutes; minute 5 has no volume (no trading)
        base = 100000 + minute
        recs.append(struct.pack(">5if", minute * 60, base, base + 1, base - 2, base + 3, 0.0 if minute == 5 else 1.5))
    raw = lzma.compress(b"".join(recs))
    out = Dukascopy.parse(raw, dt.date(2026, 10, 5), scale)
    assert len(out) == 2
    assert out[0][1] == pytest.approx(1.0) and out[0][4] == pytest.approx((100000 + 59 + 1) / scale)
    assert out[1][2] == pytest.approx((100000 + 119 + 3) / scale) and out[1][3] == pytest.approx((100000 + 60 - 2) / scale)
    assert out[1][0] - out[0][0] == 3600_000
    assert Dukascopy.parse(b"", dt.date(2026, 10, 5), scale) == []


def test_cache_keeps_finished_days_with_data_and_empty_saturdays_only(tmp_path):
    d = Dukascopy(tmp_path)
    calls = []
    today = dt.date(2026, 10, 12)

    def fake(instrument, day):
        calls.append(day)
        return LZMA_DAY if day == dt.date(2026, 10, 6) else b""
    d._download = fake                                                  # type: ignore[assignment]
    tue, mon, sat = dt.date(2026, 10, 6), dt.date(2026, 10, 5), dt.date(2026, 10, 3)
    for day in (tue, tue, mon, mon, sat, sat, today, today):
        d.day("EURUSD", day, today)
    # data day once; empty Monday (maybe a rate limit, not cached) twice; empty Saturday once; today every time
    assert calls == [tue, mon, mon, sat, today, today]


LZMA_DAY = lzma.compress(struct.pack(">5if", 0, 100000, 100001, 99999, 100002, 1.0))


def test_a_rerun_skips_symbols_already_recorded_and_fills_the_rest(tmp_path):
    class Flaky(FakeDuka):
        down = True
        def range(self, symbol, first, last):
            if symbol == "XAUUSD" and Flaky.down:
                raise RuntimeError("Dukascopy request failed")
            return super().range(symbol, first, last)
    db = str(tmp_path / "pd.db")
    paper_desk.init_schema(db)
    asked = []
    llm = lambda s, u: asked.append(u) or '{"direction": 0}'
    now = dt.datetime(2026, 10, 5, 6, 0, tzinfo=UTC)
    assert len(r.run_day("2026-10-05", Flaky(), llm, "m", db_target=db, now=now)) == 5 * 4
    first_pass = len(asked)
    Flaky.down = False
    second = r.run_day("2026-10-05", Flaky(), llm, "m", db_target=db, now=now)
    assert {x["symbol"] for x in second} == {"XAUUSD"} and len(asked) == first_pass + 4
    assert len(paper_desk.load_calls(db)) == 6 * 4
