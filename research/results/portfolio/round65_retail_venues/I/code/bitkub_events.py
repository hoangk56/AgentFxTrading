"""Bitkub THB listings dated by symbols_v3 created_at; events = base had a Binance perp >= 7 d before."""
import json, os, sys, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perps import perp_starts
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/retail_venues"
PS = perp_starts()
rows = json.load(open(os.path.join(D, "bitkub", "symbols_v3.json")))["result"]
ev = []
yr_all = collections.Counter()
for m in rows:
    if m["quote_asset"] != "THB":
        continue
    t = dt.datetime.fromisoformat(m["created_at"]).astimezone(dt.timezone.utc)
    ms = int(t.timestamp() * 1000)
    if ms >= 1735689600000:
        continue
    yr_all[t.year] += 1
    b = m["base_asset"].upper()
    if b in PS and PS[b][0] <= ms - 7 * 86400000 and t.year >= 2020:
        ev.append((ms, b, m["symbol"], m["status"], t.strftime("%Y-%m-%d %H:%M"), (ms - PS[b][0]) // 86400000))
ev.sort()
print("THB markets created per year (pre-2025):", dict(sorted(yr_all.items())))
print("events per year:", dict(sorted(collections.Counter(e[4][:4] for e in ev).items())), "total", len(ev),
      "stopped among events:", sum(e[3] == "stopped" for e in ev))
hh = collections.Counter(e[4][11:13] for e in ev); print("created_at UTC hour:", dict(sorted(hh.items())))
with open(os.path.join(D, "bitkub", "events_created_at.csv"), "w") as f:
    f.write("L_ms,coin,symbol,status,created_utc,perp_age_d\n")
    for e in ev: f.write(",".join(map(str, e)) + "\n")
for e in ev[:: max(1, len(ev) // 25)]: print(e)
