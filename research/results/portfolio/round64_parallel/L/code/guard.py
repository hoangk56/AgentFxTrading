"""Declared guards (HYPOTHESES_L.md), applied before any return is computed; prints no returns.
(1) Name collision: Binance perp price at L + 2 h (1m close, 1000x scale removed) vs the Coinbase <COIN>-USD close of
    the 1h candle starting at L + 1 h; ratio outside [0.5, 2] -> excluded.
(2) Ticker migrations: a <COIN>-USD product that is a rename of an asset already trading on Coinbase (argv list,
    from Coinbase's product list: old and new tickers both present) -> excluded.
(3) Other-quote flag (robustness only, not an exclusion): another quote product of the base traded >= 1 d before L.
Writes research/data/coinbase/exclusions.json {coin: reason} and otherquote_flag.json [coin...].
Usage: python -I guard.py RENAMED1,RENAMED2,..."""
import csv, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l2, fills
from kdata import H, DAY

ren = [x for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else []) if x]
ev = l2.load_events(1 * DAY, guard=False)
excl = {}
for e in ev:
    sc = 1000.0 if e["sym"].startswith("1000") and not e["sym"].startswith("1000000") else (1e6 if e["sym"].startswith("1000000") else 1.0)
    b = fills.price_at(l2.cache(e["sym"]), e["L"] + 2 * H) / sc
    c = e["c_L1"]
    ratio = b / c if np.isfinite(b) and np.isfinite(c) and c > 0 else np.nan
    if not np.isfinite(ratio):
        print(e["coin"], "no price for guard (kept; trade needs fills anyway)")
    elif not 0.5 <= ratio <= 2.0:
        excl[e["coin"]] = f"price collision ratio {ratio:.3g}"
    if e["coin"] in ren:
        excl[e["coin"]] = "ticker migration"
flag = []
p = os.path.join(l2.CB, "otherquotes.csv")
if os.path.exists(p):
    for r in csv.DictReader(open(p)):
        if r["first_before"]:
            flag.append(r["coin"])
json.dump(excl, open(os.path.join(l2.CB, "exclusions.json"), "w"), indent=1)
json.dump(sorted(set(flag)), open(os.path.join(l2.CB, "otherquote_flag.json"), "w"))
print("excluded:", excl)
print("other-quote earlier:", sorted(set(flag)))
