import csv
import gzip

import pytest

np = pytest.importorskip("numpy")

from research.lab.verdict import evaluate, load, render  # noqa: E402


def _rows(sid, n, r, year, sym="EURUSD", variant="real"):
    return [dict(strategy=sid, symbol=sym, variant=variant, year=str(year), r=str(r), net=str(10.0 * r))
            for _ in range(n)]


def _good(sid):
    rows = []
    for y in (2023, 2024, 2025, 2026):
        rows += _rows(sid, 60, 1.0, y) + _rows(sid, 40, -1.0, y)
    return rows + _rows(sid, 10, 1.0, 2025, variant="mirror")


def test_a_strategy_meeting_every_condition_passes():
    v = evaluate(_good("T1-ORB"), {s: -100.0 for s in range(20)}, "T1-ORB")
    assert v["passed"], v["checks"]
    assert v["n"] == 200 and v["mean_r"] == pytest.approx(0.2) and v["breadth"] == 1.0


def test_each_condition_can_fail_on_its_own():
    ctrl = {s: -100.0 for s in range(20)}
    no_mirror = [r for r in _good("T1-ORB") if r["variant"] == "real"]
    assert not evaluate(no_mirror, ctrl, "T1-ORB")["checks"]["mirror net > 0"]
    assert evaluate([dict(r, strategy="N1-FIX") for r in no_mirror], ctrl, "N1-FIX")["passed"]
    assert not evaluate(_good("T1-ORB"), {s: 1e6 for s in range(20)}, "T1-ORB")["passed"]
    bad_2026 = [r for r in _good("T1-ORB") if not (r["year"] == "2026" and float(r["r"]) > 0)]
    assert not evaluate(bad_2026, ctrl, "T1-ORB")["checks"]["2025 > 0 and 2026 > 0"]
    losers = _good("T1-ORB") + _rows("T1-ORB", 5, -1.0, 2025, sym="GBPUSD") + _rows("T1-ORB", 5, -1.0, 2025, sym="USDJPY")
    assert not evaluate(losers, ctrl, "T1-ORB")["checks"]["breadth >= 60 %"]


def test_load_and_render_a_run_dir(tmp_path):
    fields = ["strategy", "symbol", "variant", "year", "side", "t_in", "t_out", "entry", "exit", "units", "sl0", "tp0",
              "gross", "comm", "swap", "net", "risk_usd", "r", "why"]
    with gzip.open(tmp_path / "trades.csv.gz", "wt", newline="") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore", restval="0")
        w.writeheader()
        w.writerows(_good("T1-ORB") + _rows("OTHER", 3, 1.0, 2025))
    (tmp_path / "control.csv").write_text("strategy,symbol,year,seed,n,net,sum_r,n_r\n"
                                          "T1-ORB,EURUSD,2025,0,5,-3,-1,5\nT1-ORB,EURUSD,2026,0,5,-4,-1,5\n"
                                          "T1-ORB,EURUSD,2023,0,5,99,1,5\n")
    rows, ctrl = load(tmp_path, ["T1-ORB"])
    assert len(rows["T1-ORB"]) == 410 and ctrl["T1-ORB"] == {0: -7.0}
    md = render([evaluate(rows["T1-ORB"], ctrl["T1-ORB"], "T1-ORB")])
    assert "| T1-ORB |" in md and "PASS" in md
