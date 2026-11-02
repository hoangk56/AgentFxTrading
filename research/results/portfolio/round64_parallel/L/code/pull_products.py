"""Stream L: robots.txt + Coinbase Exchange product list. Saves raw/robots.txt, raw/products.json.
Usage: python -I pull_products.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net
RAW = os.path.join(net.DATA, "raw")
b = net.get("https://api.exchange.coinbase.com/robots.txt", raw=True)
open(os.path.join(RAW, "robots.txt"), "wb").write(b or b"<none>")
print("robots:", (b or b"<none>")[:500])
p = net.get("https://api.exchange.coinbase.com/products", raw=True)
open(os.path.join(RAW, "products.json"), "wb").write(p or b"")
js = json.loads(p)
print(len(js), "products")
from collections import Counter
print(Counter(x.get("status") for x in js))
print(Counter(x.get("quote_currency") for x in js).most_common(10))
print(sorted(js[0].keys()))
