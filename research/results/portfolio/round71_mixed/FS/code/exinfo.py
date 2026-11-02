"""Round 71 FS: data-api.binance.vision robots.txt + spot exchangeInfo (symbol list only)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
P = os.path.join(net.DATA, "exinfo"); os.makedirs(P, exist_ok=True)
b = net.get("https://data-api.binance.vision/robots.txt", tries=2)
print("robots", b if not isinstance(b, bytes) else b[:300])
if isinstance(b, bytes):
    open(os.path.join(P, "robots_data_api.txt"), "wb").write(b)
b = net.get("https://data-api.binance.vision/api/v3/exchangeInfo", tries=3, timeout=60)
open(os.path.join(P, "exchangeInfo.json"), "wb").write(b)
j = json.loads(b)
rows = [(s["symbol"], s["baseAsset"], s["quoteAsset"], s["status"]) for s in j["symbols"]]
u = [r for r in rows if r[2] == "USDT"]
from collections import Counter
print(len(rows), "symbols;", len(u), "USDT;", Counter(r[3] for r in u))
with open(os.path.join(net.DATA, "spot_usdt_symbols.csv"), "w") as f:
    f.write("symbol,base,status\n")
    for r in sorted(u):
        f.write(f"{r[0]},{r[1]},{r[3]}\n")
