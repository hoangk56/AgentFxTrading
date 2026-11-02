"""Probes: robots.txt of both hosts, BtcTurk USDTTRY 1D history (to find the listing start) and the 1h range limit."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net  # noqa: E402

OUT = os.path.join(net.ROOT, "raw_probe")
os.makedirs(OUT, exist_ok=True)
END = 1735689599  # 2024-12-31 23:59:59 UTC
for i, url in enumerate([
        "https://graph-api.btcturk.com/robots.txt",
        "https://datafeed.dukascopy.com/robots.txt",
        f"https://graph-api.btcturk.com/v1/klines/history?symbol=USDTTRY&resolution=1D&from=1388534400&to={END}",
        "https://graph-api.btcturk.com/v1/klines/history?symbol=USDTTRY&resolution=60&from=1640995200&to=1672531199"]):
    body, st = net.get(url)
    with open(os.path.join(OUT, f"p{i}.bin"), "wb") as f:
        f.write(body or b"")
    print(st, len(body or b""), url)
