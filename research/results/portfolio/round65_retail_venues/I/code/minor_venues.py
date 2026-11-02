"""Overlap counts for minor venues' market lists (GMO Coin, BitoPro, BTC Markets, Coins.ph, Bitso)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perps import perp_starts
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/retail_venues"
PS = perp_starts()
def L(v, f): return json.load(open(os.path.join(D, v, f)))
g = L("gmocoin", "symbols.json"); print("gmocoin keys", list(g)[:4]); gs = [x["symbol"] for x in g.get("data", [])]
print(" symbols", len(gs), "spot (no _JPY) with perp", sum(s in PS for s in gs if "_" not in s))
b = L("bitopro", "trading_pairs.json"); bd = b.get("data", b); print("bitopro", len(bd), json.dumps(bd[0])[:200])
tw = {x["base"].upper() for x in bd if x.get("quote", "").upper() == "TWD"}; print(" TWD bases", len(tw), "with perp", len(tw & set(PS)))
m = L("btcmarkets", "markets.json"); au = {x["baseAssetName"].upper() for x in m if x["quoteAssetName"] == "AUD"}
print("btcmarkets AUD", len(au), "with perp", len(au & set(PS)))
c = L("coinsph", "exchangeInfo.json"); sy = c["symbols"]; ph = {x["baseAsset"].upper() for x in sy if x["quoteAsset"] == "PHP"}
print("coins.ph PHP", len(ph), "with perp", len(ph & set(PS)), "statuses", {x.get("status") for x in sy})
s = L("bitso", "available_books.json")["payload"]; mx = {x["book"].split("_")[0].upper() for x in s if x["book"].endswith("_mxn")}
print("bitso MXN", len(mx), "with perp", len(mx & set(PS)))
