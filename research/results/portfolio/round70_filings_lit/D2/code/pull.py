"""Pull Deribit public data for stream D2, ending 2024-12-31 23:59:59 UTC (HOLD never requested).
- get_funding_rate_history (hourly interest_1h / interest_8h / index_price), one request per calendar month;
- get_tradingview_chart_data resolution 60 (trade OHLC), chunks of 200 days (API returns <= 5000 bars).
Raw bodies under research/data/deribit_funding/raw/; run with python -I."""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch

ROOT = fetch.ROOT
HOLD = os.environ.get("D2_HOLD") == "1"  # coordinator only, after registration
END = 1793318399000 if HOLD else 1735689599000  # 2026-10-29 23:59:59 / 2024-12-31 23:59:59 UTC
RAW = "raw_hold" if HOLD else "raw"
API = "https://www.deribit.com/api/v2/public/"


def ms(y, m, d=1):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


def months(y0, m0):
    y, m = y0, m0
    while ms(y, m) <= END:
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        yield y, m, ms(y, m), min(ms(ny, nm), END)
        y, m = ny, nm


def pull_funding(inst, y0, m0):
    d = os.path.join(ROOT, RAW, "funding", inst)
    os.makedirs(d, exist_ok=True)
    for y, m, a, b in months(y0, m0):
        p = os.path.join(d, f"{y}{m:02d}.json")
        if os.path.exists(p):
            continue
        body = fetch.get(f"{API}get_funding_rate_history?instrument_name={inst}&start_timestamp={a}&end_timestamp={b}")
        open(p, "wb").write(body if body is not None else b"{}")


def pull_chart(inst, start):
    d = os.path.join(ROOT, RAW, "chart", inst)
    os.makedirs(d, exist_ok=True)
    a = start
    step = 200 * 86400000
    while a <= END:
        b = min(a + step, END)
        p = os.path.join(d, f"{a}.json")
        if not os.path.exists(p):
            body = fetch.get(f"{API}get_tradingview_chart_data?instrument_name={inst}&start_timestamp={a}&end_timestamp={b}&resolution=60")
            open(p, "wb").write(body if body is not None else b"{}")
        a = b + 1


if __name__ == "__main__":
    for inst in ("BTC-PERPETUAL", "ETH-PERPETUAL"):
        pull_funding(inst, 2019, 12)
        pull_chart(inst, ms(2019, 12))
    for inst in ("BTC_USDC-PERPETUAL", "ETH_USDC-PERPETUAL"):
        pull_funding(inst, 2022, 1)
        pull_chart(inst, ms(2022, 1))
    print("done")
