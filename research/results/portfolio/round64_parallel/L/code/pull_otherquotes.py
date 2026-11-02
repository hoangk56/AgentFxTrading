"""Stream L robustness input (declared in HYPOTHESES_L.md): for every candidate event (secondary set, perp >= 1 d),
did another quote product of the same base (BTC, USDT, USDC, EUR, GBP, ETH) print a daily candle in the 300 days
before L - 1 d? Writes research/data/coinbase/otherquotes.csv (coin, product, first_ms_or_empty). Requests end
<= 2024-12-31 23:59:59 UTC. Prints only dates. Usage: python -I pull_otherquotes.py"""
import csv, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import net
import l2

DAY = 86400000


def iso(ms):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ms / 1000))


prods = json.load(open(os.path.join(net.DATA, "raw", "products.json")))
by = {}
for p in prods:
    by.setdefault(p["base_currency"], []).append(p["id"])
ev = l2.load_events(1 * DAY, guard=False)
with open(os.path.join(net.DATA, "otherquotes.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["coin", "product", "first_before"])
    for e in ev:
        for pid in by.get(e["coin"], []):
            if pid == e["product"] or pid.split("-")[1] not in ("BTC", "USDT", "USDC", "EUR", "GBP", "ETH"):
                continue
            a, b = e["L"] - 300 * DAY, e["L"] - DAY
            js = net.get(f"https://api.exchange.coinbase.com/products/{pid}/candles?granularity=86400&start={iso(a)}&end={iso(b)}")
            ts = sorted(int(x[0]) * 1000 for x in (js or []) if isinstance(x, list))
            w.writerow([e["coin"], pid, ts[0] if ts else ""]); f.flush()
            print(e["coin"], pid, iso(ts[0]) if ts else "-", flush=True)
print("done")
