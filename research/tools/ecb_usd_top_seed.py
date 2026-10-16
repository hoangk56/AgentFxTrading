"""Seed quotes for cBot/EcbWindowBot.cs's USD-TOP selector (rule F3, research/results/portfolio/round24_relaxed/).

The selector compares USDJPY and USDCHF mids at 18:00 New York (previous weekday) and 07:00 London. cTrader's bars are
bid-only, so the bot keeps its own quote log and reads its history from this seed until the log covers 250 weekdays.
A quote at minute X is the bid/ask close of the last M1 bar at most 10 bars before the bar labelled X - 1 min, i.e.
starting in [X - 11 min, X), as the research's panel priced it (clib.quote_k, back=10, in
research/results/portfolio/round24_relaxed/prereg_code/clib.py.txt); an empty bid/ask means none. Minutes on
a UTC day with no data at all are left out (unknown), never written as empty.

Sources: the IC M1 cache (research/data/m1) before --cut, Dukascopy M1 npz files (research/results/portfolio/
round24_relaxed/prereg_code/duka_dl.py.txt: ts, bci, aci, bv) from --cut on.

    research/.venv/bin/python -m research.tools.ecb_usd_top_seed --start 2025-01-01 --end 2026-10-16 \\
        --duka <dir> --out cBot/seeds/ecb_usd_top_seed.csv
"""
import argparse
import datetime as dt
import os
import zoneinfo

import numpy as np

SYMBOLS = ("USDJPY", "USDCHF")
DUKA_SCALE = {"USDJPY": 1e3, "USDCHF": 1e5}
NY = zoneinfo.ZoneInfo("America/New_York")
LONDON = zoneinfo.ZoneInfo("Europe/London")
MIN = 60_000
MAX_AGE_BARS = 10      # clib.quote_k's `back`


def ms(day: dt.date, hour: int, tz) -> int:
    return int(dt.datetime(day.year, day.month, day.day, hour, tzinfo=tz).timestamp() * 1000)


def selector_minutes(start: dt.date, end: dt.date):
    """18:00 New York and 07:00 London of every weekday in [start, end], as UTC ms, in time order."""
    out = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            out += [ms(d, 7, LONDON), ms(d, 18, NY)]
        d += dt.timedelta(days=1)
    return sorted(out)


def quote_at(ts, bid, ask, x):
    """(bid, ask) of the last bar starting in [x - 11 min, x), or None."""
    i = int(np.searchsorted(ts, x, "left")) - 1
    if i < 0 or ts[i] < x - (MAX_AGE_BARS + 1) * MIN:
        return None
    return float(bid[i]), float(ask[i])


def load(symbol: str, cut_ms: int, duka_dir):
    z = np.load(f"research/data/m1/{symbol}.npz")
    k = z["ts"] < cut_ms
    ts, bid, ask = [z["ts"][k]], [z["c"][k].astype(float)], [z["ca"][k].astype(float)]
    if duka_dir:
        for fn in sorted(os.listdir(duka_dir)):
            if fn.startswith(symbol + "_") and fn.endswith(".npz"):
                p = np.load(os.path.join(duka_dir, fn))
                q = (p["ts"] >= cut_ms) & (p["bv"] > 0) & (p["aci"] > 0)
                ts.append(p["ts"][q]); bid.append(p["bci"][q] / DUKA_SCALE[symbol]); ask.append(p["aci"][q] / DUKA_SCALE[symbol])
    ts, bid, ask = np.concatenate(ts), np.concatenate(bid), np.concatenate(ask)
    o = np.argsort(ts, kind="stable")
    return ts[o], bid[o], ask[o]


def seed_rows(start, end, cut_ms, duka_dir):
    rows = []
    data = {s: load(s, cut_ms, duka_dir) for s in SYMBOLS}
    days_with_data = {s: set((data[s][0] // 86_400_000).tolist()) for s in SYMBOLS}
    for x in selector_minutes(start, end):
        t = dt.datetime.fromtimestamp(x / 1000, dt.timezone.utc)
        for s in SYMBOLS:
            if x // 86_400_000 not in days_with_data[s]:
                continue
            q = quote_at(*data[s], x)
            rows.append(f"{t:%Y-%m-%dT%H:%M},{s}," + ("," if q is None else f"{q[0]!r},{q[1]!r}"))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--start", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--end", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--cut", default="2026-09-25", type=dt.date.fromisoformat,
                    help="first UTC day taken from Dukascopy instead of the IC cache")
    ap.add_argument("--duka", help="directory of Dukascopy <SYMBOL>_<year>.npz files")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cut_ms = int(dt.datetime(a.cut.year, a.cut.month, a.cut.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
    rows = seed_rows(a.start, a.end, cut_ms, a.duka)
    with open(a.out, "w") as fh:
        fh.write("time_utc,symbol,bid,ask\n" + "\n".join(rows) + "\n")
    print(f"{a.out}: {len(rows)} quotes, {sum(r.endswith(',,') for r in rows)} empty, {rows[0][:16]} .. {rows[-1][:16]}")


if __name__ == "__main__":
    main()
