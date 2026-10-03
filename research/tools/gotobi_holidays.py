"""GotobiBot on Japanese holidays: its cTrader backtest trades split by whether the gotobi day had a Tokyo fix, and
the coming holiday gotobi days for the presets' --SkipDates (app/cbot_presets.GOTOBI_SKIP_DATES).

No fix: a Japanese public holiday (the `holidays` package, which research/requirements.txt does not carry:
`research/.venv/bin/pip install holidays`) or a bank holiday (31/12, 2/1, 3/1). A trade's gotobi day is the date in
its leg tag ("GOTOBI-L 2016-01-05"), the one the bot decided on.

    research/.venv/bin/python -m research.tools.gotobi_holidays research/results/portfolio/gotobi_cbot_trades.csv
    research/.venv/bin/python -m research.tools.gotobi_holidays --upcoming 2026-09-29:2027-12-31
"""
import argparse
import csv
import datetime
import math
import statistics

from research.swing.swing_rules import gotobi_days

BANK_HOLIDAYS = {(12, 31): "Bank holiday", (1, 2): "Bank holiday", (1, 3): "Bank holiday"}
# The swing lab's eras (swing_lab_v2_2026-09-27.md), by the gotobi day's year.
ERAS = {"IS 2016-21": (2016, 2021), "VAL 2022-24": (2022, 2024), "HOLD 2025-26": (2025, 2026)}


def no_fix_days(years) -> dict:
    """date -> name of every day in `years` with no Tokyo fix: Japanese public and bank holidays."""
    import holidays
    out = dict(holidays.Japan(years=years, language="en_US"))
    for year in years:
        for (month, day), name in BANK_HOLIDAYS.items():
            out.setdefault(datetime.date(year, month, day), name)
    return out


def load_trades(path) -> list:
    """The combined trade CSV of ~/gotobi-build/combine.py: gotobi day, leg and net $ per trade."""
    trades = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            tag, day = row["leg"].split()
            trades.append({"day": datetime.date.fromisoformat(day), "leg": "long" if tag.endswith("-L") else "short",
                           "symbol": row["symbol"], "net": float(row["net"])})
    return trades


def stats(trades, risk: float) -> dict:
    """Mean R per trade (net / default risk), its t, win rate and net $ of a set of trades."""
    r = [t["net"] / risk for t in trades]
    mean = statistics.mean(r) if r else math.nan
    t = mean / (statistics.stdev(r) / math.sqrt(len(r))) if len(r) > 1 else math.nan
    return {"days": len({x["day"] for x in trades}), "trades": len(r), "mean_r": mean, "t": t,
            "win": sum(x > 0 for x in r) / len(r) if r else math.nan, "net": sum(x["net"] for x in trades)}


def max_drawdown(trades) -> float:
    """Largest peak-to-trough fall of cumulative net $, in file (close time) order."""
    equity = peak = worst = 0.0
    for t in trades:
        equity += t["net"]
        peak = max(peak, equity)
        worst = max(worst, peak - equity)
    return worst


def split(trades, no_fix: dict) -> dict:
    """label -> trades, for the report's table."""
    normal = [t for t in trades if t["day"] not in no_fix]
    holiday = [t for t in trades if t["day"] in no_fix]
    bank = [t for t in holiday if no_fix[t["day"]] == "Bank holiday"]
    return {
        "normal gotobi days": normal,
        "holiday gotobi days": holiday,
        "  normal, long leg": [t for t in normal if t["leg"] == "long"],
        "  holiday, long leg": [t for t in holiday if t["leg"] == "long"],
        "  normal, short leg": [t for t in normal if t["leg"] == "short"],
        "  holiday, short leg": [t for t in holiday if t["leg"] == "short"],
        "  public holidays only": [t for t in holiday if no_fix[t["day"]] != "Bank holiday"],
        "  bank holidays only": bank,
    }


def upcoming(first: datetime.date, last: datetime.date) -> list:
    """(date, name) of the gotobi days in [first, last] with no Tokyo fix."""
    no_fix = no_fix_days(range(first.year, last.year + 1))
    return [(d, no_fix[d]) for d in gotobi_days(first, last) if d in no_fix]


def report(path, risk: float) -> str:
    trades = load_trades(path)
    years = range(min(t["day"] for t in trades).year, max(t["day"] for t in trades).year + 1)
    no_fix = no_fix_days(years)
    lines = [f"| trades at ${risk:g} risk | days | trades | mean R | t | win | net $ |", "|---|---|---|---|---|---|---|"]
    for label, subset in split(trades, no_fix).items():
        s = stats(subset, risk)
        lines.append(f"| {label.strip()} | {s['days']} | {s['trades']} | {s['mean_r']:+.3f} | {s['t']:+.1f} | "
                     f"{100 * s['win']:.0f} % | {s['net']:+,.0f} |")
    lines += ["", "| era | holiday days | holiday mean R | holiday net $ | normal mean R |", "|---|---|---|---|---|"]
    for era, (lo, hi) in ERAS.items():
        inside = [t for t in trades if lo <= t["day"].year <= hi]
        h = stats([t for t in inside if t["day"] in no_fix], risk)
        n = stats([t for t in inside if t["day"] not in no_fix], risk)
        lines.append(f"| {era} | {h['days']} | {h['mean_r']:+.3f} | {h['net']:+,.0f} | {n['mean_r']:+.3f} |")
    kept = [t for t in trades if t["day"] not in no_fix]
    lines += ["", f"max drawdown, all days ${max_drawdown(trades):,.0f}; holidays skipped ${max_drawdown(kept):,.0f}",
              "", "| holiday gotobi day | holiday | net $ |", "|---|---|---|"]
    by_day = {}
    for t in trades:
        if t["day"] in no_fix:
            by_day[t["day"]] = by_day.get(t["day"], 0.0) + t["net"]
    lines += [f"| {d} | {no_fix[d]} | {net:+,.0f} |" for d, net in sorted(by_day.items())]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("trades", nargs="?", help="gotobi_cbot_trades.csv")
    ap.add_argument("--risk", type=float, default=50.0, help="default $ risk the backtest ran at (R = net / risk)")
    ap.add_argument("--upcoming", metavar="FIRST:LAST", help="list holiday gotobi days in a date range instead")
    args = ap.parse_args(argv)
    if args.upcoming:
        first, last = (datetime.date.fromisoformat(x) for x in args.upcoming.split(":"))
        days = upcoming(first, last)
        for d, name in days:
            print(f"{d} {name}")
        print(",".join(d.isoformat() for d, _ in days))
    elif args.trades:
        print(report(args.trades, args.risk))
    else:
        ap.error("give the trades CSV or --upcoming")


if __name__ == "__main__":
    main()
