"""Extra example picks: Indodax (sitemap market list), more Coinone / CoinDCX coins (seed 66)."""
import json, os, re, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perps import perp_starts
from overlap import venues
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/retail_venues"
PS = perp_starts()
txt = open(os.path.join(D, "indodax", "sitemap_market.xml")).read()
mk = [m.split("/")[-1] for m in re.findall(r"<loc>([^<]*)</loc>", txt)]
idr = sorted({m[:-3] for m in mk if m.endswith("IDR") and "OTC" not in m})
ov = [b for b in idr if b in PS]
print("indodax markets", len(mk), "IDR bases", len(idr), "with pre-2025 perp", len(ov))
first = json.load(open(os.path.join(D, "sample_coins.json")))
random.seed(66)
pool = [b for b in ov if 1569888000000 <= PS[b][0] <= 1719792000000 and b not in ("BTC", "ETH")]
print("indodax sample", random.sample(pool, 6))
V = venues()
for v, q in (("coinone", "KRW"), ("coindcx", "INR")):
    pool = sorted({r[0] for r in V[v] if r[1] == q and r[0] in PS and 1569888000000 <= PS[r[0]][0] <= 1719792000000} - set(first[v]) - {"BTC", "ETH"})
    random.seed(66); print(v, "extra sample", random.sample(pool, 4))
