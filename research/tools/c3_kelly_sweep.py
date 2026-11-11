"""C3 (Gotobi JPY basket) compounding at a fixed fraction of equity per leg.

Reads the registered C3 trade list, sums the six legs of each gotobi day into one day R, and compounds equity
by (1 + f x day R) for each risk fraction f, with the full edge and with the mean leg R halved. Also prints the
growth-optimal (Kelly) fraction mu / var of the day R. Run from the repo root:

    research/.venv/bin/python -m research.tools.c3_kelly_sweep
"""

import collections
import csv
import statistics
from pathlib import Path

TRADES = Path(__file__).resolve().parents[1] / "results/portfolio/trades_C3_gotobi_jpy_basket.csv"
FRACTIONS = (0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.15, 0.20)
LEGS_PER_DAY = 6


def load(path: Path = TRADES) -> tuple[list[float], dict[str, float]]:
    """Leg R list and the sum of R per gotobi day (the long dated by its exit at the fix, the short by its entry)."""
    legs: list[float] = []
    days: dict[str, float] = collections.defaultdict(float)
    with path.open() as fh:
        for row in csv.DictReader(fh):
            stamp = row["t_out_utc"] if row["side"] == "1" else row["t_in_utc"]
            legs.append(float(row["r"]))
            days[stamp[:10]] += legs[-1]
    return legs, dict(days)


def compound(days: list[float], f: float, days_per_year: float) -> tuple[float, float, float]:
    """CAGR, max drawdown and worst single day (as fractions of equity)."""
    equity, peak, max_dd, worst = 1.0, 1.0, 0.0, 0.0
    for r in days:
        step = f * r
        worst = min(worst, step)
        equity *= max(1 + step, 0.0)
        peak = max(peak, equity)
        max_dd = max(max_dd, 1 - equity / peak)
    years = len(days) / days_per_year
    cagr = equity ** (1 / years) - 1 if equity > 0 else -1.0
    return cagr, max_dd, worst


def main() -> None:
    legs, by_day = load()
    days = [by_day[d] for d in sorted(by_day)]
    mean_leg = statistics.mean(legs)
    days_per_year = len(days) / len({d[:4] for d in by_day})
    mu, sd = statistics.mean(days), statistics.pstdev(days)
    print(f"legs {len(legs)}, mean R/leg {mean_leg:+.4f}; days {len(days)} ({days_per_year:.1f}/yr), "
          f"day R mean {mu:+.3f} sd {sd:.3f}")
    print(f"Kelly per leg: full edge {mu / sd**2:.4f}, half edge {(mu / 2) / sd**2:.4f}")
    for label, cut in (("full", 0.0), ("half", 0.5)):
        shifted = [r - cut * LEGS_PER_DAY * mean_leg for r in days]
        for f in FRACTIONS:
            cagr, dd, worst = compound(shifted, f, days_per_year)
            print(f"{label} f={f:.2f} CAGR {cagr * 100:+7.1f}% maxDD {dd * 100:5.1f}% worst day {worst * 100:6.1f}%")


if __name__ == "__main__":
    main()
