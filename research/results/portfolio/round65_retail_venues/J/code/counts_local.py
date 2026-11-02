"""Stream J: event counts from local files only (no prices read, no returns).

J1: Binance spot listing of a coin whose USDT-M perp is >= 7 days older (first spot kline vs first perp kline).
J5: funding-interval switches in local funding files (gap between stamps changes from 8 h to 4 h / 2 h / 1 h).
Everything is cut at ts < 2025-01-01 before counting.
"""
import csv
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = sys.argv[1]  # research/data/binance
CUT = 1735689600000  # 2025-01-01 00:00 UTC
DAY = 86400000


def yr(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).year


def first_ts(path):
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            return int(row[0])
    return None


def main():
    perp_first = {}
    for fn in os.listdir(os.path.join(ROOT, "perp_1d")):
        if fn.endswith(".csv"):
            t = first_ts(os.path.join(ROOT, "perp_1d", fn))
            if t is not None:
                perp_first[fn[:-4]] = t
    spot_first = {}
    with open(os.path.join(ROOT, "spot_first.csv")) as f:
        for row in csv.reader(f):
            if len(row) == 2 and row[1].isdigit():
                spot_first[row[0]] = int(row[1])

    # perp symbols like 1000PEPEUSDT map to spot PEPEUSDT
    def spot_name(p):
        for pre in ("1000000", "10000", "1000", "1M"):
            if p.startswith(pre) and p[len(pre):] in spot_first:
                return p[len(pre):]
        return p if p in spot_first else None

    ev = Counter()
    same = Counter()
    lag_days = defaultdict(list)
    names = defaultdict(list)
    for p, tp in perp_first.items():
        s = spot_name(p)
        if s is None:
            continue
        ts = spot_first[s]
        if ts >= CUT or tp >= CUT:
            continue
        if ts >= tp + 7 * DAY:
            ev[yr(ts)] += 1
            lag_days[yr(ts)].append((ts - tp) / DAY)
            names[yr(ts)].append(s)
        elif abs(ts - tp) < 7 * DAY:
            same[yr(ts)] += 1
    print("J1 perp-first coins later listed on Binance spot (spot first >= perp first + 7 d), by spot-listing year")
    for y in sorted(ev):
        lg = sorted(lag_days[y])
        print(f"  {y}: n {ev[y]}, median lag {lg[len(lg)//2]:.0f} d, e.g. {', '.join(sorted(names[y])[:8])}")
    print("  spot and perp within 7 d of each other (not events):", dict(sorted(same.items())))

    # J5 funding interval switches
    sw = Counter()
    sym_sw = Counter()
    kinds = Counter()
    nsym = 0
    for fn in os.listdir(os.path.join(ROOT, "funding")):
        if not fn.endswith(".csv"):
            continue
        nsym += 1
        ts = []
        with open(os.path.join(ROOT, "funding", fn)) as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                t = int(row[0])
                if t < CUT:
                    ts.append(t)
        prev_gap = None
        for a, b in zip(ts, ts[1:]):
            gap = round((b - a) / 3600000)
            if gap not in (1, 2, 4, 8):
                prev_gap = None
                continue
            if prev_gap == 8 and gap < 8:
                sw[yr(b)] += 1
                sym_sw[fn[:-4]] += 1
                kinds[gap] += 1
            prev_gap = gap
    print(f"J5 funding-interval switches 8h -> shorter, {nsym} symbols with full funding history, by year:",
          dict(sorted(sw.items())), "new gap:", dict(kinds), "symbols:", len(sym_sw))


if __name__ == "__main__":
    main()
