"""Stream D: event counts per era / year from event_dates.csv (dates only, no prices). HOLD-era events are not listed.

Usage: python -I tabulate.py
"""
import calendar, csv, os, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "..", "..", "..", "..", "data", "binance_announcements", "event_dates.csv")
DAY = 86400000
CUT = 1735689600000


def ms(d):
    return calendar.timegm(time.strptime(d, "%Y-%m-%d")) * 1000


def era(t):
    return "pre" if t < 1577836800000 else "IS" if t < 1640995200000 else "VAL" if t < CUT else "HOLD"


rows = list(csv.DictReader(open(P)))
S, Sy, P_, Py = Counter(), Counter(), Counter(), Counter()
s_list = []
for r in rows:
    p0 = int(r["perp_first"])
    d0 = r["spot_first_day"]
    if d0 and d0[0].isdigit():
        t = ms(d0)
        if t >= p0 + 7 * DAY and t < CUT:
            S[era(t)] += 1; Sy[d0[:4]] += 1
            s_list.append((d0, r["perp"], r["spot_pair"], round((t - p0) / DAY)))
    last = int(r["perp_last_pre2025"]) if r["perp_last_pre2025"] not in ("", "None") else None
    if last is not None and r["perp_last_any_flag"] == "0" and last < CUT - 2 * DAY:
        P_[era(last)] += 1; Py[time.strftime("%Y", time.gmtime(last / 1000))] += 1
print("perps listed before 2025 (rows):", len(rows))
print("S spot listing of a perp coin (>= 7 d after perp), by era:", dict(S), "by year:", dict(sorted(Sy.items())))
for x in sorted(s_list):
    print("  ", *x)
print("P perp delisted before 2025, by era:", dict(P_), "by year:", dict(sorted(Py.items())))
print("no spot pair ever:", sum(1 for r in rows if not r["spot_pair"]))
