"""Measured round-trip cost (bp) of the paper desk's 6 symbols: spread at the 07:00 UTC entry/exit minute,
commission, and the overnight swap, from the IC Markets M1 cache (research/data/m1) and research/specs.py.

    research/.venv/bin/python -m research.tools.paper_desk_costs [--write]

Spread: median over weekdays 2026-01-01..2026-09-24 of the mean tick spread in the minutes 06:55-07:05 UTC, taken
whole (one half paid on entry, one on exit). Commission: specs.comm_per_unit over the unit's USD notional at the
median price. Swap: the SPECS rate per unit and rollover over the notional, with the real number of 17:00 New York
rollovers between each weekday's 07:00 UTC entry and the next weekday's 07:00 UTC exit (Wednesday triple counted,
Friday-to-Monday included); a credit counts as 0 (conservative). Symbols without a calibrated swap fit count 0 (US500): that is
a disclosed gap, not a measured zero.
"""
import argparse
import datetime as dt
import statistics
from pathlib import Path

import numpy as np

from research import m1
from research.specs import SPECS, SWAPS, rollovers

SYMBOLS = ["EURUSD", "USDJPY", "GBPJPY", "XAUUSD", "US500", "BTCUSD"]
START = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
END = dt.datetime(2026, 9, 24, tzinfo=dt.timezone.utc)
OUT = Path(__file__).resolve().parents[1] / "results" / "portfolio" / "paper_desk_costs_2026-10-29.md"


def _utc_ms(d: dt.datetime) -> int:
    return int(d.timestamp() * 1000)


def next_weekday(d: dt.date) -> dt.date:
    d += dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def usd_per_unit(symbol: str, price: float, gbpusd: float) -> float:
    """USD notional of one unit of the traded instrument."""
    return {"EURUSD": price, "USDJPY": 1.0, "GBPJPY": gbpusd, "XAUUSD": price, "US500": price,
            "BTCUSD": price}[symbol]


def measure(symbol: str, gbpusd: float) -> dict:
    d = m1.load(symbol)
    ts = d["ts"]
    lo, hi = _utc_ms(START), _utc_ms(END)
    spreads, prices = [], []
    for day in range(int(lo // 86_400_000), int(hi // 86_400_000) + 1):
        date = dt.datetime.fromtimestamp(day * 86_400, dt.timezone.utc)
        if date.weekday() >= 5:
            continue
        a = day * 86_400_000 + (6 * 60 + 55) * 60_000
        i, j = np.searchsorted(ts, [a, a + 10 * 60_000])
        if j > i:
            spreads.append(float(np.mean(d["smean"][i:j])))
            prices.append(float(np.mean(d["c"][i:j])))
    price = statistics.median(prices)
    spread_bp = statistics.median(s / p for s, p in zip(spreads, prices)) * 1e4
    spec = SPECS.get(symbol)
    notional = usd_per_unit(symbol, price, gbpusd)
    comm_bp = (spec.comm_per_unit / notional * 1e4) if spec else 0.0
    long_rate, short_rate, triple = SWAPS.get(symbol, (0.0, 0.0, 2))
    rolls = []
    day = dt.date(2026, 1, 5)
    while day <= dt.date(2026, 9, 21):
        if day.weekday() < 5:
            e = dt.datetime(day.year, day.month, day.day, 7, tzinfo=dt.timezone.utc)
            x = next_weekday(day)
            x = dt.datetime(x.year, x.month, x.day, 7, tzinfo=dt.timezone.utc)
            rolls.append(rollovers(_utc_ms(e), _utc_ms(x), triple))
        day += dt.timedelta(days=1)
    mean_rolls = sum(rolls) / len(rolls)
    # swap rates are USD per unit per rollover; negative = paid, so cost = -rate
    # a credit is not counted (floored at 0): the fitted rates are constants and carry credits are not dependable
    swap_long = max(0.0, -long_rate * mean_rolls / notional * 1e4)
    swap_short = max(0.0, -short_rate * mean_rolls / notional * 1e4)
    return {"symbol": symbol, "days": len(spreads), "price": price, "spread_bp": spread_bp, "comm_bp": comm_bp,
            "rollovers": mean_rolls, "swap_long": swap_long, "swap_short": swap_short,
            "cost_long": spread_bp + comm_bp + swap_long, "cost_short": spread_bp + comm_bp + swap_short,
            "swap_fitted": symbol in SWAPS}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    g = m1.load("GBPUSD")
    gbpusd = float(np.median(g["c"][-500_000:]))
    rows = [measure(s, gbpusd) for s in SYMBOLS]
    lines = ["# Paper desk measured costs (2026-10-29)", "",
             "Source: `research/tools/paper_desk_costs.py` on `research/data/m1` (IC Markets, weekdays 2026-01-01 to "
             "2026-09-24, minutes 06:55-07:05 UTC) and `research/specs.py`. Basis points of notional, round trip "
             "(entry 07:00 UTC, exit 07:00 UTC next weekday). `cost_long` / `cost_short` are what a call in that "
             "direction pays: spread + commission + overnight swap (credits not counted).", "",
             "| symbol | days | spread bp | commission bp | mean rollovers | swap long bp | swap short bp | "
             "cost long bp | cost short bp | swap fitted |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['symbol']} | {r['days']} | {r['spread_bp']:.2f} | {r['comm_bp']:.2f} | "
                     f"{r['rollovers']:.2f} | {r['swap_long']:+.2f} | {r['swap_short']:+.2f} | "
                     f"{r['cost_long']:.2f} | {r['cost_short']:.2f} | {'yes' if r['swap_fitted'] else 'NO (0 assumed)'} |")
    lines += ["", "Caveats: spread is the mean tick spread in the minute, not the spread at an exact fill; the swap rates "
              "are the constant 2026 fit of `specs.SWAPS` (see its docstring); commission is the fitted "
              "`comm_per_unit` (metals commission is known to be overstated, see JOURNAL). The desk scores on "
              "Dukascopy bids, so the measured spread is the whole cost of crossing it.", "",
              "`COST_BP` in `app/paper_desk_runner.py` holds these `(cost_long, cost_short)` pairs:", "", "```"]
    for r in rows:
        lines.append(f'"{r["symbol"]}": ({r["cost_long"]:.2f}, {r["cost_short"]:.2f}),')
    lines.append("```")
    text = "\n".join(lines)
    print(text)
    if a.write:
        OUT.write_text(text + "\n")


if __name__ == "__main__":
    main()
