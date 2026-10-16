# Python port of EcbWindowBot.Decide() on cBot/seeds/ecb_usd_top_seed.csv vs the registered F3 selector (f3_check.py's
# "ref") on IC data, for 2026-01-01..2026-09-24 (histories inside the seed).
import csv, math, datetime as dt, zoneinfo, runpy, sys
import numpy as np
NY = zoneinfo.ZoneInfo("America/New_York"); LON = zoneinfo.ZoneInfo("Europe/London")
Q = {}
for r in csv.DictReader(open("cBot/seeds/ecb_usd_top_seed.csv")):
    Q[(r["symbol"], r["time_utc"])] = (float(r["bid"]) + float(r["ask"])) / 2 if r["bid"] else None
def utc(d, h, tz):
    return dt.datetime(d.year, d.month, d.day, h, tzinfo=tz).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
def prev_wkd(d):
    p = d - dt.timedelta(days=1)
    while p.weekday() >= 5: p -= dt.timedelta(days=1)
    return p
def score(d):
    a, b = utc(prev_wkd(d), 18, NY), utc(d, 7, LON); s = 0
    for sym in ("USDJPY", "USDCHF"):
        pa, pb = Q.get((sym, a), "missing"), Q.get((sym, b), "missing")
        if pa in (None, "missing") or pb in (None, "missing"): return None
        s += math.log(pb / pa)
    return s / 2
def pct(v, q):
    s = sorted(v); pos = (len(s) - 1) * q / 100; lo = math.floor(pos); hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)
def decide(d):
    u = score(d); h = []; x = d
    for _ in range(250):
        x = prev_wkd(x); v = score(x)
        if v is not None: h.append(v)
    return u is not None and len(h) >= 60 and u >= pct(h, 67)
g = runpy.run_path(sys.argv[1], run_name="lib")
WKD, ref = g["WKD"], g["select"](g["U_series"]("ref"))
days = [d for d in WKD if dt.date(2026, 1, 1) <= d <= dt.date(2026, 9, 24)]
r = {d: s for d, s in zip(WKD, ref)}
port = {d: decide(d) for d in days}
diff = [d for d in days if port[d] != r[d]]
print(f"2026-01-01..09-24: {len(days)} weekdays, registered F3 days {sum(r[d] for d in days)}, port {sum(port.values())}, differing {diff}")
