import csv
import gzip
from datetime import date

import pytest

np = pytest.importorskip("numpy")

from lab_helpers import bar_ticks, make_chunk  # noqa: E402
from research.lab import feed  # noqa: E402
from research.lab.run import TRADE_FIELDS, _job_strategies, merge, run_job  # noqa: E402
from research.ticks import day_ms  # noqa: E402

QUIET, SHOCK = (1.1000, 1.1005, 1.0995, 1.1000), (1.1000, 1.1045, 1.0995, 1.1040)
AFTER = (1.1040, 1.1045, 1.1035, 1.1040)


def test_job_strategies_respect_symbols_and_variants():
    ids = ["TOM", "BTC-S1", "X1"]
    assert _job_strategies("US30", "real", ids) == ["TOM", "BTC-S1"]
    assert _job_strategies("EURUSD", "mirror", ids) == ["BTC-S1"]
    assert _job_strategies("EURGBP", "mirror", ids) == []                       # synthetic: real data only
    assert _job_strategies("EURUSD", "shuffle:3", ["BTC-S1", "X1"]) == ["BTC-S1"]


def test_run_job_writes_parts_and_merge_adds_headers(tmp_path, monkeypatch):
    def fake_chunk(symbol, variant, year, *a, **k):
        if year == 2026:
            return None
        ts, px = bar_ticks(day_ms(date(year, 3, 10)), 15, [QUIET] * 30 + [SHOCK] + [AFTER] * 20)
        return make_chunk(ts, px * 60_000, spread=5.0, symbol="BTCUSD", year=year)

    monkeypatch.setattr(feed, "load_chunk", fake_chunk)
    out = run_job("BTCUSD", "real", ["BTC-S1"], [2025, 2026], 2, str(tmp_path))
    assert out["trades"] == 1 and out["errors"] == 0
    parts = tmp_path / "parts"
    rows = list(csv.reader(open(parts / "BTCUSD_real.trades.csv")))
    assert len(rows) == 1 and rows[0][:4] == ["BTC-S1", "BTCUSD", "real", "2025"]
    assert len(list(csv.reader(open(parts / "BTCUSD_real.control.csv")))) == 2
    assert [r[3] for r in csv.reader(open(parts / "BTCUSD_real.coverage.csv"))] == ["ok", "no data"]
    merge(tmp_path)
    with gzip.open(tmp_path / "trades.csv.gz", "rt") as fh:
        assert next(csv.reader(fh)) == TRADE_FIELDS
    assert (tmp_path / "control.csv").read_text().startswith("strategy,symbol,year,seed")
