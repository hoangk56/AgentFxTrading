import csv

from research.tools import usd_high_calendar_seed as seed


def _csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["utc_minute", "event", "source"])
        w.writerows([(m, e, "x") for m, e in rows])
    return path


def test_registered_rows_from_since_then_only_forward_rows_after_them(tmp_path):
    reg = seed.read(_csv(tmp_path / "reg.csv", [("2024-12-31T13:30", "CPI"), ("2025-01-03T13:30", "NFP"),
                                                ("2025-01-03T13:30", "AHE"), ("2026-09-30T12:30", "GDP")]))
    fwd = seed.read(_csv(tmp_path / "fwd.csv", [("2026-09-30T12:30", "GDP (forward copy)"),   # inside the registered span
                                                ("2026-10-02T12:30", "NFP"), ("2026-10-02T12:30", "NFP")]))
    rows = seed.merge(reg, fwd, "2025-01-01")
    assert rows == {"2025-01-03T13:30": ["AHE", "NFP"], "2026-09-30T12:30": ["GDP"], "2026-10-02T12:30": ["NFP"]}


def test_written_seed_has_one_valid_through_line_and_one_row_per_minute(tmp_path):
    out = tmp_path / "seed.csv"
    seed.write({"2026-10-02T12:30": ["NFP", "Unemployment"]}, "2026-12-31", out, ["a.csv"])
    lines = out.read_text().splitlines()
    assert [ln for ln in lines if "valid_through=" in ln] == ["# valid_through=2026-12-31"]
    body = [ln for ln in lines if not ln.startswith("#")]
    assert body == ["utc_minute,event", "2026-10-02T12:30,NFP + Unemployment"]
