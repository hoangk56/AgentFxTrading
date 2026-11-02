"""Market-list overlap with pre-2025 Binance perps, per venue (parse with python -I; bodies are data only)."""
import json, os, sys, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perps import perp_starts

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/retail_venues"
PS = perp_starts()


def load(v, f):
    return json.load(open(os.path.join(D, v, f)))


def venues():
    out = {}
    d = load("coinone", "markets_KRW.json")["markets"]
    out["coinone"] = [(m["target_currency"].upper(), "KRW", f'trade{m["trade_status"]}/maint{m["maintenance_status"]}', None) for m in d]
    d = load("bitbank", "spot_pairs.json")["data"]["pairs"]
    out["bitbank"] = [(m["base_asset"].upper(), m["quote_asset"].upper(), "enabled" if m.get("is_enabled") else "disabled", None) for m in d]
    d = load("btcturk", "exchangeinfo.json")["data"]["symbols"]
    out["btcturk"] = [(m["numerator"].upper(), m["denominator"].upper(), m["status"], m["id"]) for m in d]
    d = load("bitkub", "symbols_v3.json")["result"]
    out["bitkub"] = [(m["base_asset"].upper(), m["quote_asset"].upper(), m["status"], m["created_at"]) for m in d]
    d = load("coindcx", "markets_details.json")
    out["coindcx"] = [(m["target_currency_short_name"].upper(), m["base_currency_short_name"].upper(), m["status"], m["pair"]) for m in d]
    d = load("bitvavo", "markets.json")
    out["bitvavo"] = [(m["base"].upper(), m["quote"].upper(), m["status"], None) for m in d]
    d = load("bitflyer", "markets.json")
    out["bitflyer"] = [(m["product_code"].split("_")[0], m["product_code"].split("_")[-1], m.get("market_type"), None) for m in d]
    return out


if __name__ == "__main__":
    V = venues()
    for v, rows in V.items():
        st = collections.Counter(r[2] for r in rows)
        q = collections.Counter(r[1] for r in rows)
        fiat = {"KRW", "JPY", "TRY", "THB", "INR", "EUR", "IDR", "BRL"}
        loc = [r for r in rows if r[1] in fiat]
        bases = {r[0] for r in loc}
        ov = {b for b in bases if b in PS}
        print(f"{v}: {len(rows)} markets, quotes {dict(q.most_common(5))}, status {dict(st)}; local-fiat bases {len(bases)}, with pre-2025 perp {len(ov)}")
