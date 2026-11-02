"""Stream L: first Coinbase Exchange candle of <COIN>-USD for every USD product whose base has a Binance USDT-M perp
that started before 2025. Daily candles first (window before the perp start, then forward 300-day windows, all ending
<= 2024-12-31 23:59:59 UTC), then one 1h request for the first day. Writes research/data/coinbase/listings.csv:
coin, product, status, sym, perp_first, first_day, L (first 1h candle start, ms), c_L1 (Coinbase close of the 1h
candle starting at L + 1 h, for the name-collision guard), pre (1 if the product traded before the perp start or before
2019-12-20). Prints only counts and dates (no returns). Usage: python -I pull_listings.py"""
import csv, json, os, sys, time, calendar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net

R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
DAY = 86400000
CUT = 1735689600000
END = CUT - 1000
G0 = 1576800000000  # 2019-12-20
SKIP = {"BTC", "USDT", "USDC", "DAI", "PAX", "PAXG", "BUSD", "GUSD", "PYUSD", "EURC", "WBTC", "CBETH", "MSOL",
        "LSETH", "JITOSOL", "GYEN", "MUSD", "RAI", "USD1"}
ALIAS = {"CGLD": "CELO", "COSMOSDYDX": "DYDX"}
OUT = os.path.join(net.DATA, "listings.csv")


def perp_first(sym):
    p = os.path.join(R, "binance", "perp_1d", sym + ".csv")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        f.readline()
        line = f.readline()
        return int(line.split(",")[0]) if line else None


def iso(ms):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ms / 1000))


def candles(pid, gran, a, b):
    js = net.get(f"https://api.exchange.coinbase.com/products/{pid}/candles?granularity={gran}&start={iso(a)}&end={iso(b)}")
    return sorted(int(x[0]) * 1000 for x in (js or []) if isinstance(x, list)), {int(x[0]) * 1000: x for x in (js or []) if isinstance(x, list)}


prods = json.load(open(os.path.join(net.DATA, "raw", "products.json")))
done = set()
if os.path.exists(OUT):
    with open(OUT) as f:
        done = {r["product"] for r in csv.DictReader(f)}
new = not os.path.exists(OUT)
fo = open(OUT, "a", newline="")
w = csv.writer(fo)
if new:
    w.writerow(["coin", "product", "status", "sym", "perp_first", "first_day", "L", "c_L1", "pre"])
todo = []
for p in sorted(prods, key=lambda x: x["id"]):
    if p["quote_currency"] != "USD" or p["base_currency"] in SKIP or p["id"] in done:
        continue
    b = ALIAS.get(p["base_currency"], p["base_currency"])
    for sym in (b + "USDT", "1000" + b + "USDT", "1000000" + b + "USDT"):
        pf = perp_first(sym)
        if pf is not None and pf < CUT:
            todo.append((p, sym, pf)); break
print(len(todo), "USD products with a pre-2025 Binance perp", flush=True)
for p, sym, pf in todo:
    pid = p["id"]
    lo = max(min(pf, G0) - 300 * DAY, 0)
    pre_end = max(pf, G0)
    pre = 0; first = None
    # anything between lo and max(perp start, 2019-12-20) -> listed too early to be an event
    a = lo
    while a < pre_end:
        b = min(a + 299 * DAY, pre_end)
        ts, _ = candles(pid, 86400, a, b)
        if ts:
            pre = 1; first = ts[0]; break
        a = b
    if not pre:
        a = pre_end
        while a < END:
            b = min(a + 299 * DAY, END)
            ts, _ = candles(pid, 86400, a, b)
            if ts:
                first = ts[0]; break
            a = b
    L = ""; c1 = ""
    if first is not None and not pre:
        hs, rows = candles(pid, 3600, first - DAY, min(first + 3 * DAY, END))
        hs = [h for h in hs if h >= first - DAY]
        if hs:
            L = hs[0]
            if L + 3600000 in rows:
                c1 = rows[L + 3600000][4]
    w.writerow([p["base_currency"], pid, p["status"], sym, pf, first if first is not None else "", L, c1, pre]); fo.flush()
    print(pid, p["status"], sym, "first", iso(first) if first else "-", "pre" if pre else "", "L", iso(L) if L else "-", flush=True)
print("done", flush=True)
