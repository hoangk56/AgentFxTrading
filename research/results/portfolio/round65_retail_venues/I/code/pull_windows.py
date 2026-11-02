"""Pull one 1h window per example listing (first-day date D from the loc_* requests). All windows end < 2025-01-01."""
import os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch
H = 3600
EX = {
    "bitkub": [("SAND", "2021-10-28"), ("WLD", "2023-08-18"), ("CYBER", "2023-10-20"), ("ENA", "2024-04-30"), ("APT", "2024-11-21")],
    "coinone": [("INJ", None), ("AVAX", "2020-12-28w"), ("SUSHI", "2021-01-04w"), ("GRT", "2021-01-18w"), ("STX", "2023-06-12w")],
    "btcturk": [("ENJ", "2021-04-15"), ("ZRX", "2023-08-11"), ("FLOKI", "2023-08-17"), ("NEAR", "2024-08-08"), ("KAVA", "2024-09-12")],
    "bitvavo": [("GRT", "2021-08-18"), ("EDU", "2023-08-31"), ("ONDO", "2024-02-14"), ("MAV", "2024-04-30")],
    "coindcx": [("REN", "2023-03-28"), ("PEPE", "2024-05-09")],
    "indodax": [("HIGH", "2023-03-30"), ("JASMY", "2023-09-14"), ("PORTAL", "2024-08-29")],
}


def ts(d):
    return int(dt.datetime.strptime(d[:10], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())


for v, lst in EX.items():
    for coin, d in lst:
        if d is None:
            continue
        wk = d.endswith("w")
        a = ts(d) - (1 if wk else 2) * 86400
        b = ts(d) + (8 if wk else 3) * 86400
        b = min(b, 1735689599)
        if v == "bitkub":
            u = f"https://api.bitkub.com/tradingview/history?symbol={coin}_THB&resolution=60&from={a}&to={b}"
        elif v == "coinone":
            u = f"https://api.coinone.co.kr/public/v2/chart/KRW/{coin}?interval=1h&timestamp={b * 1000}&size={(b - a) // H}"
        elif v == "btcturk":
            u = f"https://graph-api.btcturk.com/v1/klines/history?symbol={coin}TRY&resolution=60&from={a}&to={b}"
        elif v == "bitvavo":
            u = f"https://api.bitvavo.com/v2/{coin}-EUR/candles?interval=1h&start={a * 1000}&end={b * 1000}&limit=1440"
        elif v == "coindcx":
            u = f"https://public.coindcx.com/market_data/candles?pair=I-{coin}_INR&interval=1h&startTime={a * 1000}&endTime={b * 1000}&limit=1000"
        elif v == "indodax":
            u = f"https://indodax.com/tradingview/history_v2?symbol={coin}IDR&tf=60&from={a}&to={b}"
        fetch.main(v, f"w1h_{coin}_{d[:10]}.json", u)
