"""Funding history (< 2025-01-01) from public fapi fundingRate for universe perps with no local funding file."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from udata import *
from fetch import get
for coin, sym in sorted(MAP.items()):
    if coin in SKIP or len(funding(sym)):
        continue
    rows = []; st = 1546300800000
    while True:
        js = get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={st}&endTime={CUT - 1}&limit=1000") or []
        rows += [(int(x["fundingTime"]), x["fundingRate"]) for x in js if int(x["fundingTime"]) < CUT]
        if len(js) < 1000:
            break
        st = int(js[-1]["fundingTime"]) + 1
    with open(os.path.join(UV, "funding", sym + ".csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "rate"]); w.writerows(rows)
    print(sym, len(rows), flush=True)
