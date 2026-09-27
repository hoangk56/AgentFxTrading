"""Queue the cTrader backtests that fill the 2023-2024 tick cache for the ten symbols that only had 2025+
(strategy lab, docs/superpowers/specs/2026-09-25-strategy-lab-design.md). Live FlowRSI presets, $2000, ticks;
the reports themselves are not used. The API caps a run at 365 days, so 2024 ends on 12-30 (12-29..31 are
cached). Cross pairs go last: their conversion-symbol ticks load lazily inside the first order, so a cold run
can abort once by timeout; the Backtest page reruns it and the failed run still fills the cache.
Run on the VPS:  ssh forge@204.168.144.232 'python3 -' < research/tools/fill_2023_2024_rest.py"""
import json
import urllib.request

API = "http://127.0.0.1:8000/api/backtests"
PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD", "ETHUSD", "UK100", "EURJPY", "GBPJPY", "AUDJPY"]
YEARS = [("2023-01-01", "2023-12-31"), ("2024-01-01", "2024-12-30")]

for symbol in PAIRS:
    for start, end in YEARS:
        body = {"bot_name": f"cbot-demo-demo-{symbol.lower()}-all-flowrsi", "start": start, "end": end,
                "data_mode": "ticks", "balance": 2000.0, "note": f"lab cache fill {start[:4]}", "overrides": {}}
        req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            print(resp.status, resp.read().decode(), symbol, start[:4])
