"""BtcTurk USDTTRY 1h candles 2018-07-01..2024-12-31 22:59:59 UTC, one request per calendar year (<= ~8,800 rows)."""
import calendar
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net  # noqa: E402

OUT = os.path.join(net.ROOT, "btcturk_1h")
os.makedirs(OUT, exist_ok=True)
for y in range(2018, 2025):
    a = calendar.timegm((y, 1, 1, 0, 0, 0))
    b = calendar.timegm((y + 1, 1, 1, 0, 0, 0)) - 3601  # stop an hour early: the API also returns the boundary candle
    url = f"https://graph-api.btcturk.com/v1/klines/history?symbol=USDTTRY&resolution=60&from={a}&to={b}"
    body, st = net.get(url)
    print(y, st, len(body or b""))
    if st == 200:
        with open(os.path.join(OUT, f"{y}.json"), "wb") as f:
            f.write(body)
