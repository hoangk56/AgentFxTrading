"""OKX 1H swap-trade and index candles for the funding reconstruction (amendment 18:09 UTC).
All 10 coins 2020-01-01..2022-01-16; BTC / ETH also to 2022-12-31 (VAL fit check). Cut < 2025."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import get
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/funding_formulas/okx"
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "LTC", "LINK", "BCH", "DOT"]
START = 1577836800000
for c in COINS:
    end = 1672531200000 if c in ("BTC", "ETH") else 1642377600000
    for ep, inst, tag in [("history-candles", c + "-USDT-SWAP", "trade"), ("history-index-candles", c + "-USDT", "index")]:
        rows = {}
        after = end
        while after > START:
            d = json.loads(get("https://www.okx.com/api/v5/market/%s?instId=%s&bar=1H&after=%d&limit=100"
                               % (ep, inst, after), gap=0.25, tries=4))["data"]
            if not d:
                break
            for k in d:
                t = int(k[0])
                if START <= t < end:
                    rows[t] = k[:5]
            after = min(int(k[0]) for k in d)
        with open(os.path.join(OUT, "%s_%s_1h.csv" % (c, tag)), "w") as f:
            f.write("t,o,h,l,c\n")
            for t in sorted(rows):
                f.write(",".join(rows[t]) + "\n")
        print(c, tag, len(rows), min(rows) if rows else None, flush=True)
