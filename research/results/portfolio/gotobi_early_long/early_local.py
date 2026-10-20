"""Run from the repo root: research/.venv/bin/python research/results/portfolio/gotobi_early_long/early_local.py
Gotobi long leg 17:00 vs 18:00 UTC entry on local m1 data, stops ignored: both legs exit at the same fix, so
B - A = ask(18:00) - ask(17:00) on d-1 (pips, 0.01 JPY). Dukascopy m1 <= 2015, IC m1 >= 2016."""
import datetime as dt
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from research.swing.swing_rules import gotobi_days
from research.tools.gotobi_holidays import no_fix_days

D = str(REPO / "research" / "data")


def load(sym):
    out = []
    for p, lo, hi in ((f"{D}/duka/m1/{sym}.npz", 2004, 2015), (f"{D}/m1/{sym}.npz", 2016, 2026)):
        z = np.load(p)
        t = z["ts"]
        y0 = int(dt.datetime(lo, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
        y1 = int(dt.datetime(hi + 1, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
        k = (t >= y0) & (t < y1)
        out.append((t[k], z["c"][k], z["ca"][k]))
    return tuple(np.concatenate(x) for x in zip(*out))


def px(t, c, ca, T, side):
    """Close of the last m1 bar ending at or before T (bar open < T), if it ended within 5 minutes of T."""
    i = int(np.searchsorted(t, T, side="left")) - 1
    if i < 0 or T - (t[i] + 60_000) > 5 * 60_000:
        return None
    return ca[i] if side == "ask" else (c[i] + ca[i]) / 2


def stats(xs):
    n = len(xs)
    if n < 3:
        return n, float("nan"), float("nan")
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return n, m, m / (sd / math.sqrt(n)) if sd else float("nan")


hol = no_fix_days(range(2004, 2027))
rows = defaultdict(list)                      # (sym, year) -> diffs
for sym in ("USDJPY", "EURJPY", "GBPJPY"):
    t, c, ca = load(sym)
    for d in gotobi_days(dt.date(2004, 1, 5), dt.date(2026, 9, 30)):
        if d in hol or d.weekday() == 0:      # holiday skipped by the bot; Monday: both enter at the weekend open
            continue
        base = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000) - 86_400_000
        a17, a18 = px(t, c, ca, base + 17 * 3_600_000, "ask"), px(t, c, ca, base + 18 * 3_600_000, "ask")
        if a17 is None or a18 is None:
            continue
        rows[(sym, d.year)].append((a18 - a17) * 100)

eras = {"2004-2013": range(2004, 2014), "2014-2019": range(2014, 2020), "2015-2019": range(2015, 2020),
        "2020-2026": range(2020, 2027), "all": range(2004, 2027)}
print("B - A (17:00 minus 18:00 entry), pips per long leg, + = 17:00 better")
for era, ys in eras.items():
    line = [era]
    pool = []
    for sym in ("USDJPY", "EURJPY", "GBPJPY"):
        xs = [x for y in ys for x in rows[(sym, y)]]
        pool += xs
        n, m, tt = stats(xs)
        line.append(f"{sym} n={n} {m:+.2f}p t={tt:+.2f}")
    n, m, tt = stats(pool)
    line.append(f"POOL n={n} {m:+.2f}p t={tt:+.2f}")
    print(" | ".join(line))
print("\nper year, pooled 3 pairs:")
for y in range(2004, 2027):
    xs = [x for s in ("USDJPY", "EURJPY", "GBPJPY") for x in rows[(s, y)]]
    n, m, tt = stats(xs)
    print(f"{y} n={n:3d} {m:+6.2f}p t={tt:+.2f}")
