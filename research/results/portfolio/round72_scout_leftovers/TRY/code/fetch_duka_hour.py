"""Dukascopy USDTRY hourly candles, one file per month and side: datafeed/USDTRY/YYYY/MM-1/{BID,ASK}_candles_hour_1.bi5,
2018-06..2024-12 (the BtcTurk premium exists from 2018-07-10). Resumable; passes until complete; 403 = stop; 45-min cap."""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net  # noqa: E402

OUT = os.path.join(net.ROOT, "duka_h1")
os.makedirs(OUT, exist_ok=True)
net.SPACING["datafeed.dukascopy.com"] = 1.0
THREADS = 3  # the host takes ~12 s per file (also from a VPS), so 3 in flight; starts stay >= 1 s apart
t0 = time.time()
STOP = 1793562300  # 2026-11-01 19:45 UTC: hard end of the pull budget
jobs = [(y, m, s) for s in ("BID", "ASK") for y in range(2018, 2025) for m in range(12) if (y, m) >= (2018, 5)]  # BID first
for pas in range(8):
    left = [j for j in jobs if not os.path.exists(os.path.join(OUT, f"{j[0]}{j[1] + 1:02d}_{j[2]}.bi5"))]
    if not left:
        break
    def one(job):
        y, m, s = job
        if 403 in net._blocked or time.time() - t0 > 2700:
            return
        url = f"https://datafeed.dukascopy.com/datafeed/USDTRY/{y}/{m:02d}/{s}_candles_hour_1.bi5"
        body, st = net.get(url, tries=1, timeout=90)
        if st == 200:
            with open(os.path.join(OUT, f"{y}{m + 1:02d}_{s}.bi5"), "wb") as f:
                f.write(body)
        else:
            time.sleep(5)
    with ThreadPoolExecutor(THREADS) as ex:
        list(ex.map(one, left))
    if net._blocked:
        print("403 stop"); sys.exit(1)
    if time.time() > STOP:
        print("time cap"); sys.exit(0)
    print("pass", pas, "left", len(left), f"{time.time() - t0:.0f}s", flush=True)
print("done", f"{time.time() - t0:.0f}s", flush=True)
