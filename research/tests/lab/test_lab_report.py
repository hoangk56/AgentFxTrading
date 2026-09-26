import csv
import gzip
from datetime import datetime, timezone

import pytest

np = pytest.importorskip("numpy")

from research.lab.report import build, write  # noqa: E402
from research.lab.run import CONTROL_FIELDS, TRADE_FIELDS  # noqa: E402


def _ms(y, m):
    return int(datetime(y, m, 15, tzinfo=timezone.utc).timestamp() * 1000)


def _write_run(tmp):
    rows = []

    def tr(s, sym, v, y, t_out, net):
        rows.append([s, sym, v, y, 1, t_out - 1000, t_out, 1, 1, 1, 1, "nan", net, 0, 0, net, 100, net / 100, "time"])

    tr("A", "EURUSD", "real", 2023, _ms(2023, 3), 100.0)
    tr("A", "EURUSD", "real", 2023, _ms(2023, 4), -30.0)
    tr("A", "EURUSD", "real", 2024, _ms(2024, 5), 50.0)
    tr("A", "EURUSD", "mirror", 2023, _ms(2023, 3), 10.0)
    for k in range(20):
        tr("A", "EURUSD", f"shuffle:{k}", 2023, _ms(2023, 3), float(k) - 10)
    tr("B", "EURUSD", "real", 2023, _ms(2023, 3), -20000.0)
    with gzip.open(tmp / "trades.csv.gz", "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(TRADE_FIELDS)
        w.writerows(rows)
    with open(tmp / "control.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CONTROL_FIELDS)
        w.writerows(["A", "EURUSD", 2023, k, 3, k - 30.0, 0, 0] for k in range(20))
    return tmp


def test_cell_statistics_and_flags(tmp_path):
    cells = {(c["strategy"], c["symbol"]): c for c in build(_write_run(tmp_path))}
    a = cells[("A", "EURUSD")]
    assert a["n"] == 3 and a["net"] == pytest.approx(120.0) and a["max_dd"] == pytest.approx(30.0)
    assert a["worst_month"] == pytest.approx(-30.0) and a["pf"] == pytest.approx(5.0)
    assert a["net_2023"] == pytest.approx(70.0) and a["net_2024"] == pytest.approx(50.0) and a["n_2025"] == 0
    assert a["pos_every_year"] and a["control_pct"] == 100.0 and a["beats_control"]
    assert a["shuffles"] == 20 and a["shuffle_ok"] and a["mirror_ok"] and a["all_flags"]
    b = cells[("B", "EURUSD")]
    assert b["blown"] == "2023-03-15" and not b["pos_every_year"] and not b["beats_control"] and not b["all_flags"]


def test_report_files(tmp_path):
    run = _write_run(tmp_path)
    write(run, build(run))
    assert (run / "cells.csv").exists() and (run / "matrix.csv").exists()
    md = (run / "report.md").read_text()
    assert "| A | EURUSD |" in md and "Cells with all four flags: 1" in md
