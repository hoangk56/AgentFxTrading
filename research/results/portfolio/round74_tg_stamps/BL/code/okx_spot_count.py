"""Count only (no prices): for L1 coins without a perp venue and N >= 2021-09-03, does an OKX spot <COIN>-USDT daily
trade dump exist for day(N) - 2 (HEAD)? Writes okx_spot_avail.json."""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
V = json.load(open(os.path.join(net.D, "l1_venue.json")))
out = {}
for e in V:
    if e["venue"] is not None:
        continue
    d = dt.datetime.fromtimestamp(e["t"], dt.timezone.utc)
    if d < dt.datetime(2021, 9, 3, tzinfo=dt.timezone.utc):
        continue
    d2 = (d - dt.timedelta(days=2)).strftime("%Y-%m-%d"); d0 = d.strftime("%Y-%m-%d")
    sym = f"{e['coin']}-USDT"
    ok = True
    for dd in (d2, d0):
        u = f"https://static.okx.com/cdn/okex/traderecords/trades/daily/{dd.replace('-', '')}/{sym}-trades-{dd}.zip"
        r, s = net.opener(u, method="HEAD"); net.log(u, s, 0, "HEAD")
        ok = ok and s == 200
    out[f"{e['id']}_{e['coin']}"] = ok
    print(d0, e["coin"], ok, flush=True)
json.dump(out, open(os.path.join(net.D, "okx_spot_avail.json"), "w"))
