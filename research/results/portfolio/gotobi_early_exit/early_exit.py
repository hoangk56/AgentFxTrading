"""Run from the repo root: research/.venv/bin/python research/results/portfolio/gotobi_early_exit/early_exit.py
Gotobi: does closing a leg earlier than the bot does pay? Local m1, stops ignored, written before any number was seen.

Bot (A): long from 18:00 UTC d-1 to the fix 00:55 UTC (closed at bid), short from 00:55 to 02:55 UTC (closed at ask).
Variant (B): the same leg closed at an earlier time T. Entry is unchanged, so per leg
  long:  B - A = bid(T) - bid(00:55)        short: B - A = ask(02:55) - ask(T)
Pips (0.01 JPY). Dukascopy m1 2004-2015, IC m1 2016-2026; Japanese holidays skipped like the bot.
Primary cells: long T = 00:45, 00:50; short T = 01:55, 02:25. Pass for a cell: B - A > 0 with t >= 2.5 (4 cells,
Bonferroni) on 2004-2019 per-pair-day pooled AND each pair > 0 there, AND B - A > 0 on 2020-2026. The other T are
descriptive only. Pooled t over-states (three JPY pairs on the same day); the day-clustered t (pairs averaged per day)
is the one the verdict uses."""
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

D = REPO / "research" / "data"
PAIRS = ("USDJPY", "EURJPY", "GBPJPY")
LONG_T = [(0, m) for m in (15, 25, 35, 40, 45, 50, 53, 54)]
SHORT_T = [(1, 0), (1, 15), (1, 30), (1, 45), (1, 55), (2, 10), (2, 25), (2, 40), (2, 45), (2, 50)]
PRIMARY = {("long", (0, 45)), ("long", (0, 50)), ("short", (1, 55)), ("short", (2, 25))}
ERAS = {"2004-2013": range(2004, 2014), "2014-2019": range(2014, 2020), "2004-2019": range(2004, 2020),
        "2020-2026": range(2020, 2027)}


def load(sym):
    out = []
    for p, lo, hi in ((D / "duka" / "m1" / f"{sym}.npz", 2004, 2015), (D / "m1" / f"{sym}.npz", 2016, 2026)):
        z = np.load(p)
        t = z["ts"]
        y0 = int(dt.datetime(lo, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
        y1 = int(dt.datetime(hi + 1, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
        k = (t >= y0) & (t < y1)
        out.append((t[k], z["c"][k], z["ca"][k]))
    return tuple(np.concatenate(x) for x in zip(*out))


def px(t, c, ca, T, side):
    """Bid or ask close of the last m1 bar ending at or before T, if it ended within 5 minutes of T."""
    i = int(np.searchsorted(t, T, side="left")) - 1
    if i < 0 or T - (t[i] + 60_000) > 5 * 60_000:
        return None
    return ca[i] if side == "ask" else c[i]


def mt(xs):
    n = len(xs)
    if n < 3:
        return n, float("nan"), float("nan")
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return n, m, (m / (sd / math.sqrt(n)) if sd else float("nan"))


hol = no_fix_days(range(2004, 2027))
diff = defaultdict(dict)          # (leg, T) -> {(sym, day): pips}
base = defaultdict(dict)          # leg -> {(sym, day): pips of the bot's leg}
for sym in PAIRS:
    t, c, ca = load(sym)
    for d in gotobi_days(dt.date(2004, 1, 5), dt.date(2026, 9, 30)):
        if d in hol:
            continue
        d0 = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
        at = lambda h, m, s: px(t, c, ca, d0 + (h * 60 + m) * 60_000, s)
        e_long = px(t, c, ca, d0 - 6 * 3_600_000, "ask")          # 18:00 UTC d-1 (Monday: stale, skipped)
        fix_b, fix_a, end_a = at(0, 55, "bid"), at(0, 55, "ask"), at(2, 55, "ask")
        if fix_b is None or fix_a is None or end_a is None:
            continue
        if e_long is not None:
            base["long"][(sym, d)] = (fix_b - e_long) * 100
        base["short"][(sym, d)] = (fix_b - end_a) * 100                    # short opened at bid at the fix
        for T in LONG_T:
            x = at(*T, "bid")
            if x is not None:
                diff[("long", T)][(sym, d)] = (x - fix_b) * 100
        for T in SHORT_T:
            x = at(*T, "ask")
            if x is not None:
                diff[("short", T)][(sym, d)] = (end_a - x) * 100


def era_stats(cells, ys):
    sel = {k: v for k, v in cells.items() if k[1].year in ys}
    per_day = defaultdict(list)
    for (s, d), v in sel.items():
        per_day[d].append(v)
    pair = {s: mt([v for (s2, _), v in sel.items() if s2 == s]) for s in PAIRS}
    return mt(list(sel.values())), mt([sum(v) / len(v) for v in per_day.values()]), pair


print("Bot legs (context), pips per leg, 3 pairs pooled:")
for leg in ("long", "short"):
    print(f"  {leg:5s} " + " | ".join(f"{e} {era_stats(base[leg], ys)[0][1]:+.2f}p (t {era_stats(base[leg], ys)[1][2]:+.1f})"
                                        for e, ys in ERAS.items()))
print("\nB - A = close the leg at T instead of the bot's time; pips per leg; + = earlier close better")
print("t_day = day-clustered (3 pairs averaged per day). * = primary cell")
verdicts = []
for leg, Ts in (("long", LONG_T), ("short", SHORT_T)):
    print(f"\n{leg.upper()} (bot closes at {'00:55' if leg == 'long' else '02:55'})")
    for T in Ts:
        cells = diff[(leg, T)]
        parts = []
        for e, ys in ERAS.items():
            (n, m, _), (_, _, td), pair = era_stats(cells, ys)
            parts.append(f"{e} {m:+5.2f}p t_day {td:+5.1f}")
        star = "*" if (leg, T) in PRIMARY else " "
        print(f" {star}{T[0]:02d}:{T[1]:02d}  " + " | ".join(parts))
        if (leg, T) in PRIMARY:
            (n, m, _), (_, _, td), pair = era_stats(cells, ERAS["2004-2019"])
            (_, m2, _), _, _ = era_stats(cells, ERAS["2020-2026"])
            ok = m > 0 and td >= 2.5 and all(p[1] > 0 for p in pair.values()) and m2 > 0
            verdicts.append(f"{leg} {T[0]:02d}:{T[1]:02d}: 2004-2019 {m:+.2f}p t_day {td:+.2f}, pairs "
                            + " ".join(f"{s[:3]} {p[1]:+.2f}" for s, p in pair.items())
                            + f"; 2020-2026 {m2:+.2f}p -> {'PASS' if ok else 'FAIL'}")
    print("   per year, primary cells, 3 pairs pooled:")
    for T in Ts:
        if (leg, T) not in PRIMARY:
            continue
        ys = defaultdict(list)
        for (s, d), v in diff[(leg, T)].items():
            ys[d.year].append(v)
        up = sum(sum(v) > 0 for v in ys.values())
        print(f"   {T[0]:02d}:{T[1]:02d} " + " ".join(f"{y % 100:02d}:{sum(v) / len(v):+.1f}" for y, v in sorted(ys.items()))
              + f"  -> {up}/{len(ys)} years > 0")
print("\nVERDICT (pre-registered cells)")
for v in verdicts:
    print("  " + v)
