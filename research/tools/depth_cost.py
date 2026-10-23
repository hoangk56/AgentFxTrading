"""Cost of a large GotobiBot market order at its minutes, from the order book cBot/DepthLoggerBot.cs records on IC.

The cTrader tick history has bid/ask only, so slippage at size can only come from the live book. The logger writes
depth_SYMBOL_yyyyMMdd.csv (ts_ms UTC, src, bids, asks; "price:units" levels joined by '|', best first) during short
windows around each event:

- 18:00 UTC: the long entry (buy, hits the asks). The real entry is jittered 17:00-19:00, so 18:00 stands for it.
- 00:55 UTC: the Tokyo fix. The long exit and the short entry both sell at once, so the bids take twice the lot.
- 02:55 UTC: the short exit (buy).

IC's book comes in tiers (0.1M, 0.5M, 1M, 3M, 5M, 10M, 20M), and the feed does not say whether a tier adds to the
ones above it or is a separate full-amount quote. Both readings are reported: `walk` sums the levels best first (a
VWAP), `tier` fills the whole order at the best level whose own size covers it (the pessimistic reading). Cost is in
pips beyond the best price on that side, so it excludes the spread, which is reported on its own.

A day's event cost is the worst snapshot from T to T + LAG_S seconds (the order's latency); the baseline is the median
of the window's snapshots at least BASELINE_GAP_S from T.

    rsync -a agentFx:/home/forge/ctrader/depth_logs/ /tmp/depth/      # root-owned: sudo tar over ssh works too
    research/.venv/bin/python -m research.tools.depth_cost /tmp/depth
"""
import argparse
import csv
import datetime as dt
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

from research.swing.swing_rules import gotobi_days

LOT = 100_000
SIZES = (1, 5, 10, 15, 20, 30)
LAG_S = 3
BASELINE_GAP_S = 60
# event -> (UTC time, book side the order takes, lot multiple: the fix sells the long's exit and the short's entry)
EVENTS = {
    "18:00 long entry (buy)": (dt.time(18, 0), "asks", 1),
    "00:55 fix: long exit + short entry (sell x2)": (dt.time(0, 55), "bids", 2),
    "02:55 short exit (buy)": (dt.time(2, 55), "asks", 1),
}
FILE_RE = re.compile(r"depth_([A-Z0-9]+)_(\d{8})\.csv$")


def parse_levels(text: str) -> list:
    out = []
    for part in filter(None, text.split("|")):
        price, units = part.split(":")
        out.append((float(price), float(units)))
    return out


def load(path: Path) -> list:
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            bids, asks = parse_levels(r["bids"]), parse_levels(r["asks"])
            if bids and asks:
                rows.append({"ts": int(r["ts_ms"]) / 1000.0, "bids": bids, "asks": asks})
    rows.sort(key=lambda r: r["ts"])
    return rows


def pip_size(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


def walk_cost(levels: list, units: float, pip: float) -> float:
    """Pips the VWAP of `units` lies beyond the best level, summing levels best first; NaN if the book is too thin."""
    best, left, paid = levels[0][0], units, 0.0
    for price, size in levels:
        take = min(left, size)
        paid += take * abs(price - best)
        left -= take
        if left <= 0:
            return paid / units / pip
    return math.nan


def tier_cost(levels: list, units: float, pip: float) -> float:
    """Pips beyond the best level of the first level whose own size covers `units`; NaN if none does."""
    best = levels[0][0]
    for price, size in levels:
        if size >= units:
            return abs(price - best) / pip
    return math.nan


def spread_pips(row: dict, pip: float) -> float:
    return (row["asks"][0][0] - row["bids"][0][0]) / pip


def event_rows(rows: list, day: dt.date, at: dt.time) -> tuple:
    """(rows from T to T + LAG_S, baseline rows of that window at least BASELINE_GAP_S away from T)."""
    t = dt.datetime.combine(day, at, tzinfo=dt.timezone.utc).timestamp()
    near = [r for r in rows if t <= r["ts"] <= t + LAG_S]
    base = [r for r in rows if abs(r["ts"] - t) >= BASELINE_GAP_S and abs(r["ts"] - t) <= 600]
    return near, base


def gotobi_for(event_day: dt.date, at: dt.time) -> dt.date:
    """The gotobi day an event serves: the 18:00 long entry is for the next day."""
    return event_day + dt.timedelta(days=1) if at.hour >= 12 else event_day


def measure(depth_dir: Path) -> list:
    """One record per symbol, UTC day, event, size and reading."""
    files = defaultdict(list)
    for p in sorted(Path(depth_dir).glob("depth_*.csv")):
        m = FILE_RE.search(p.name)
        if m:
            files[m.group(1)].append((dt.datetime.strptime(m.group(2), "%Y%m%d").date(), p))
    days_all = [d for v in files.values() for d, _ in v]
    if not days_all:
        return []
    gotobi = set(gotobi_days(min(days_all), max(days_all) + dt.timedelta(days=1)))
    out = []
    for symbol, day_files in files.items():
        pip = pip_size(symbol)
        for day, path in day_files:
            rows = load(path)
            for name, (at, side, mult) in EVENTS.items():
                near, base = event_rows(rows, day, at)
                if not near:
                    continue
                for lots in SIZES:
                    units = lots * mult * LOT
                    for reading, fn in (("walk", walk_cost), ("tier", tier_cost)):
                        costs = [fn(r[side], units, pip) for r in near]
                        base_costs = [c for c in (fn(r[side], units, pip) for r in base) if not math.isnan(c)]
                        out.append({
                            "symbol": symbol, "day": day, "event": name, "lots": lots, "reading": reading,
                            "gotobi": gotobi_for(day, at) in gotobi,
                            "cost": math.nan if any(math.isnan(c) for c in costs) else max(costs),
                            "baseline": statistics.median(base_costs) if base_costs else math.nan,
                            "spread": max(spread_pips(r, pip) for r in near),
                        })
    return out


def _q(values: list, p: float) -> float:
    v = sorted(values)
    return v[min(len(v) - 1, int(p * len(v)))] if v else math.nan


def report(records: list) -> str:
    if not records:
        return "no depth files with snapshots at the event minutes"
    lines = ["cost beyond the best price, pips (spread excluded); per day the worst snapshot in the first "
             f"{LAG_S} s; lots per leg (the fix sells 2x); n = days, thin = days the book could not fill the order"]
    groups = defaultdict(list)
    for r in records:
        groups[(r["symbol"], r["event"], r["gotobi"], r["reading"], r["lots"])].append(r)
    for symbol in sorted({r["symbol"] for r in records}):
        for event in EVENTS:
            for is_gotobi in (True, False):
                spreads = [r["spread"] for r in records if r["symbol"] == symbol and r["event"] == event
                           and r["gotobi"] == is_gotobi and r["reading"] == "walk" and r["lots"] == SIZES[0]]
                if not spreads:
                    continue
                lines.append(f"\n{symbol} | {event} | {'gotobi' if is_gotobi else 'other'} days | "
                             f"spread median {statistics.median(spreads):.2f} max {max(spreads):.2f}")
                lines.append("  lots | walk median / p90 / max (baseline) | tier median / p90 / max (baseline) | n thin")
                for lots in SIZES:
                    cells = []
                    for reading in ("walk", "tier"):
                        g = groups[(symbol, event, is_gotobi, reading, lots)]
                        ok = [r["cost"] for r in g if not math.isnan(r["cost"])]
                        base = [r["baseline"] for r in g if not math.isnan(r["baseline"])]
                        cells.append(f"{_q(ok, .5):.2f} / {_q(ok, .9):.2f} / {max(ok, default=math.nan):.2f} "
                                     f"({statistics.median(base) if base else math.nan:.2f})")
                        thin = len(g) - len(ok)
                    lines.append(f"  {lots:>4} | {cells[0]} | {cells[1]} | {len(g)} {thin}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("depth_dir", type=Path)
    print(report(measure(ap.parse_args(argv).depth_dir)))


if __name__ == "__main__":
    main()
