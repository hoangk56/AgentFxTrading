import datetime as dt
import math

from research.tools import depth_cost as dc

PIP = 0.01
ASKS = [(150.000, 100_000), (150.002, 500_000), (150.004, 1_000_000), (150.010, 3_000_000)]


def test_walk_cost_is_the_vwap_beyond_the_best_level():
    # 0.6M: 0.1M at +0 and 0.5M at +0.2 pip -> VWAP +0.1667 pip
    assert math.isclose(dc.walk_cost(ASKS, 600_000, PIP), 0.5 / 0.6 * 0.2)
    assert dc.walk_cost(ASKS, 100_000, PIP) == 0


def test_tier_cost_takes_the_first_level_that_covers_the_order():
    assert math.isclose(dc.tier_cost(ASKS, 600_000, PIP), 0.4)
    assert math.isclose(dc.tier_cost(ASKS, 1_500_000, PIP), 1.0)


def test_a_book_too_thin_is_nan():
    assert math.isnan(dc.walk_cost(ASKS, 5_000_000, PIP))
    assert math.isnan(dc.tier_cost(ASKS, 5_000_000, PIP))


def test_bids_cost_is_measured_downwards():
    bids = [(149.990, 100_000), (149.985, 1_000_000)]
    assert math.isclose(dc.tier_cost(bids, 1_000_000, PIP), 0.5)


def test_the_18_00_long_entry_serves_the_next_gotobi_day():
    assert dc.gotobi_for(dt.date(2026, 10, 29), dt.time(18, 0)) == dt.date(2026, 10, 30)
    assert dc.gotobi_for(dt.date(2026, 10, 30), dt.time(0, 55)) == dt.date(2026, 10, 30)


def _write(path, rows):
    with open(path, "w") as f:
        f.write("ts_ms,src,bids,asks\n")
        for ts, bids, asks in rows:
            fmt = lambda lv: "|".join(f"{p}:{u}" for p, u in lv)
            f.write(f"{int(ts * 1000)},U,{fmt(bids)},{fmt(asks)}\n")


def test_measure_takes_the_worst_snapshot_after_the_fix_and_doubles_the_lots(tmp_path):
    fix = dt.datetime(2026, 10, 30, 0, 55, tzinfo=dt.timezone.utc).timestamp()
    calm = [(149.99, 100_000), (149.98, 2_000_000)]
    thin = [(149.99, 100_000), (149.95, 2_000_000)]
    asks = [(150.0, 3_000_000)]
    _write(tmp_path / "depth_USDJPY_20261030.csv",
           [(fix - 120, calm, asks), (fix + 0.5, calm, asks), (fix + 2, thin, asks), (fix + 10, calm, asks)])
    rec = [r for r in dc.measure(tmp_path) if r["event"].startswith("00:55") and r["reading"] == "tier"]
    five = next(r for r in rec if r["lots"] == 5)
    assert five["gotobi"] is True
    assert math.isclose(five["cost"], 4.0)        # the thin snapshot 2 s after the fix, 1M sold = 2 x 5 lots
    assert math.isclose(five["baseline"], 1.0)    # the calm snapshot 2 minutes before
    assert math.isnan(next(r for r in rec if r["lots"] == 15)["cost"])   # 3M sold: the book holds 2.1M
    assert "USDJPY" in dc.report(dc.measure(tmp_path))
