"""Post-hoc check (chooses nothing): is L a real trading start? First Bithumb KRW day value vs the median of days
2-8. Writes research/data/bithumb/burst.csv. Usage: python -I burst.py"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from pull_events import candles, kst, ts, BD, DAY, CUT
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ev = [x for x in csv.DictReader(open(os.path.join(OUT, "h_events.csv"))) if not x["drop"]]
fc = {x["coin"]: x for x in csv.DictReader(open(os.path.join(BD, "first_candles.csv")))}
rows = []
for e in ev:
    d0 = int(fc[e["coin"]]["d0"])
    d = candles("days", e["coin"], kst(min(d0 + 9 * DAY - 1000, CUT - 1000)), 9)
    if isinstance(d, dict) or not d:
        continue
    v = {ts(x["candle_date_time_utc"]): x["candle_acc_trade_price"] for x in d}
    first = v.get(d0, np.nan); rest = [v[t] for t in sorted(v) if t > d0]
    rows.append((e["coin"], first, float(np.median(rest)) if rest else np.nan, first / np.median(rest) if rest else np.nan))
    print(*rows[-1], flush=True)
with open(os.path.join(BD, "burst.csv"), "w", newline="") as f:
    csv.writer(f).writerows([("coin", "d0_krw", "med_d2_8", "ratio")] + rows)
