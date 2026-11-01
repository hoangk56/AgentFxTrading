"""Pull full ISD station-years from the public AWS bucket noaa-isd-pds (2005-2024)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import get
OUT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/kalshi_weather/isd_raw"
ST = ["725053-94728", "725340-14819", "722540-13904", "722020-12839"]
for y in range(2005, 2025):
    for s in ST:
        p = f"{OUT}/{s}-{y}.gz"
        if os.path.exists(p) and os.path.getsize(p) > 1000: continue
        print(s, y, get(f"https://noaa-isd-pds.s3.amazonaws.com/data/{y}/{s}-{y}.gz", p), flush=True)
