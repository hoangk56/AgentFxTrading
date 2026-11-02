"""Pick 6 random overlapping coins per undated venue (seed 65) to locate first candles; also Upbit-KRW share."""
import json, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perps import perp_starts
from overlap import venues
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
PS = perp_starts()
up = {m["market"].split("-")[1] for m in json.load(open(os.path.join(R, "upbit", "raw", "market_all.json"))) if m["market"].startswith("KRW-")}
FI = {"coinone": "KRW", "btcturk": "TRY", "coindcx": "INR", "bitvavo": "EUR", "bitbank": "JPY", "bitkub": "THB"}
V = venues()
out = {}
for v, q in FI.items():
    bases = sorted({r[0] for r in V[v] if r[1] == q and r[0] in PS and r[0] not in ("BTC", "ETH")})
    shu = sum(b in up for b in bases)
    pool = [b for b in bases if 1569888000000 <= PS[b][0] <= 1719792000000]
    random.seed(65); s = random.sample(pool, min(6, len(pool)))
    out[v] = s
    print(f"{v}: overlap {len(bases)} (also Upbit KRW now: {shu}, {shu/len(bases):.0%}); sample {s}")
json.dump(out, open(os.path.join(R, "retail_venues", "sample_coins.json"), "w"))
