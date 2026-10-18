"""The release calendar cBot/GoldLevelBot.cs reads: cBot/seeds/usd_high_calendar.csv.

The gold rule (research/results/portfolio/round27_levels_opens/PREREG_G_gold_round50_cascade.md) does not arm within 15
minutes of a High-impact USD release minute. Its registered calendar rule is the official-schedule list
(round27_levels_opens/prereg_code/usd_high_2024_2026.csv, 2024-01-01 .. 2026-09-30) for every time from 2024 on. The
bot needs the same list for the days it trades, so the seed is that list from --since on, followed by the same event
types built from the publishers' schedules for later days (research/results/portfolio/gold_level_cbot/usd_high_fwd.csv
and its coverage.txt).

Each minute appears once (events at the same minute are joined with " + "). `# valid_through=YYYY-MM-DD` is the last
New York day for which every scheduled type is known; the bot stops arming after it, so rebuild the seed with a newer
forward file before then.

    research/.venv/bin/python -m research.tools.usd_high_calendar_seed --valid-through 2026-12-31 \\
        --forward research/results/portfolio/gold_level_cbot/usd_high_fwd.csv --out cBot/seeds/usd_high_calendar.csv
"""
import argparse
import csv
import datetime as dt
from pathlib import Path

REGISTERED = Path("research/results/portfolio/round27_levels_opens/prereg_code/usd_high_2024_2026.csv")


def read(path):
    """[(utc_minute, event)] from a utc_minute,event[,source] CSV."""
    with open(path, newline="") as f:
        return [(r["utc_minute"], r["event"]) for r in csv.DictReader(f)]


def merge(registered, forward, since: str):
    """Registered rows from `since` up to their last minute, then forward rows after it. {minute: [events]}."""
    last = max(m for m, _ in registered)
    out = {}
    for m, e in registered:
        if m >= since:
            out.setdefault(m, []).append(e)
    for m, e in forward:
        if m > last:
            out.setdefault(m, []).append(e)
    return {m: sorted(set(es)) for m, es in sorted(out.items())}


def write(rows, valid_through: str, out, sources):
    with open(out, "w", newline="") as f:
        f.write("# High-impact USD release minutes (UTC) for cBot/GoldLevelBot.cs: the registered calendar rule of\n")
        f.write("# PREREG_G_gold_round50_cascade.md (official schedules). Built by research/tools/usd_high_calendar_seed.py from\n")
        for s in sources:
            f.write(f"# {s}\n")
        f.write(f"# valid_through={valid_through}\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["utc_minute", "event"])
        for m, es in rows.items():
            w.writerow([m, " + ".join(es)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registered", default=str(REGISTERED))
    ap.add_argument("--forward", action="append", default=[], help="later rows (same columns); repeatable")
    ap.add_argument("--since", default="2025-01-01", help="first day kept from the registered list")
    ap.add_argument("--valid-through", required=True, help="last New York day all scheduled types are known for")
    ap.add_argument("--out", default="cBot/seeds/usd_high_calendar.csv")
    a = ap.parse_args()
    dt.date.fromisoformat(a.valid_through)
    reg = read(a.registered)
    fwd = [r for p in a.forward for r in read(p)]
    rows = merge(reg, fwd, a.since)
    assert a.valid_through >= max(m for m, _ in reg)[:10], "valid_through is before the end of the registered list"
    write(rows, a.valid_through, a.out, [a.registered] + a.forward)
    print(f"{a.out}: {len(rows)} minutes {min(rows)} .. {max(rows)}, valid through {a.valid_through}")


if __name__ == "__main__":
    main()
