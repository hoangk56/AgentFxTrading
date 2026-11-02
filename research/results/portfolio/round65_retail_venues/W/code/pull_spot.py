"""Mechanism check M data: Binance spot SYM/BTC monthly 1h klines (data.binance.vision, files <= 2024-12 only)
for months covering [N - 40 d, N + 4 d] of W / D KRW events 2020-24. Saved under research/data/upbit_notices/spot1h/."""
import os, sys, csv, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from fetch import get, D
OUT = os.path.join(D, "spot1h"); os.makedirs(OUT, exist_ok=True)
DAY = 86400000
rows = list(csv.DictReader(open(os.path.join(os.path.dirname(__file__), "..", "events_all.csv"))))
need = set()
for r in rows:
    if r["cls"] not in ("W", "D") or (r["markets"] and "KRW" not in r["markets"]):
        continue
    t = int(r["t"])
    a = dt.datetime.fromtimestamp((t - 40 * DAY) / 1000, dt.timezone.utc); b = dt.datetime.fromtimestamp((t + 4 * DAY) / 1000, dt.timezone.utc)
    m = dt.date(a.year, a.month, 1)
    while m <= dt.date(b.year, b.month, 1):
        if m <= dt.date(2024, 12, 1):
            need.add((r["coin"], m.strftime("%Y-%m"), r["t"]))
        m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
miss = set()
for coin, ym, t in sorted(need, key=lambda x: (x[0], x[1])):
    s = coin + "BTC"
    fn = os.path.join(OUT, f"{s}-1h-{ym}.zip")
    if os.path.exists(fn) or (coin, t) in miss:
        continue
    b, c = get(f"https://data.binance.vision/data/spot/monthly/klines/{s}/1h/{s}-1h-{ym}.zip", accept="*/*")
    if c == 403:
        print("403 stop"); break
    if c == 200 and b:
        open(fn, "wb").write(b)
    else:
        miss.add((coin, t))
print("done", len(need), len(os.listdir(OUT)))
