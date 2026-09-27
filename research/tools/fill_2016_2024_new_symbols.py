"""Queue the cTrader backtests that fill the 2016-2024 tick cache for the 11 new symbols (the h1-history
design's 26-symbol universe minus the 15 lab symbols: docs/superpowers/specs/2026-09-26-h1-history-data-design.md).
These symbols only had 2024-12-29 onward cached, unlike the 15 lab symbols which already had 2023-01 onward.
Requires the backtest-only bot configs registered first (research/../create_new_symbol_bots.py equivalent:
cbot-demo-demo-<symbol>-all-flowrsi for each). Live FlowRSI presets, $2000, ticks; the reports themselves are
not used. The API caps a run at 365 days: 2016/2020 are leap years so they end on 12-30; 2024 ends on 12-28
since 12-29..31 are already cached. Indices (US500, JP225, AUS200, HK50) go last: their conversion ticks
(USD/JPY/AUD/HKD) may load lazily inside the first order, so a cold run can abort once by timeout; the
Backtest page reruns it and the failed run still fills the cache.
Run on the VPS:  ssh forge@204.168.144.232 'python3 -' < research/tools/fill_2016_2024_new_symbols.py"""
import json
import urllib.request

API = "http://127.0.0.1:8000/api/backtests"
PAIRS = ["NZDUSD", "USDCHF", "XAGUSD", "XPTUSD", "XTIUSD", "XBRUSD", "XNGUSD",
         "US500", "JP225", "AUS200", "HK50"]
YEARS = [("2016-01-01", "2016-12-30"), ("2017-01-01", "2017-12-31"), ("2018-01-01", "2018-12-31"),
         ("2019-01-01", "2019-12-31"), ("2020-01-01", "2020-12-30"), ("2021-01-01", "2021-12-31"),
         ("2022-01-01", "2022-12-31"), ("2023-01-01", "2023-12-31"), ("2024-01-01", "2024-12-28")]

for symbol in PAIRS:
    for start, end in YEARS:
        body = {"bot_name": f"cbot-demo-demo-{symbol.lower()}-all-flowrsi", "start": start, "end": end,
                "data_mode": "ticks", "balance": 2000.0, "note": f"new-symbol history backfill {start[:4]}",
                "overrides": {}}
        req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            print(resp.status, resp.read().decode(), symbol, start[:4])
