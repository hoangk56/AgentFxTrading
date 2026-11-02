"""Dukascopy USDTRY 06h tick files for every weekday 2016-01-01..2024-12-31 (month index 0-based in the URL).
Saved raw (.bi5, LZMA) under research/data/usdtry_premium/duka_06h/; empty body = no ticks that hour.
Resumable: days already saved are skipped. Stops if the host answers 403."""
import datetime as dt
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net  # noqa: E402

OUT = os.path.join(net.ROOT, "duka_06h")
os.makedirs(OUT, exist_ok=True)
hour = int(sys.argv[1]) if len(sys.argv) > 1 else 6
net.SPACING["datafeed.dukascopy.com"] = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
t0, n, fails, streak = time.time(), 0, [], 0
for pas in range(6):
  d, end = dt.date(2016, 1, 1), dt.date(2024, 12, 31)
  fails = []
  while d <= end:
    if d.weekday() < 5:
        p = os.path.join(OUT, f"{d:%Y%m%d}_{hour:02d}.bi5")
        if not os.path.exists(p):
            url = f"https://datafeed.dukascopy.com/datafeed/USDTRY/{d.year}/{d.month - 1:02d}/{d.day:02d}/{hour:02d}h_ticks.bi5"
            body, st = net.get(url, tries=1)
            if st == 403:
                print("403: stop"); sys.exit(1)
            if st == 200:
                with open(p, "wb") as f:
                    f.write(body)
                streak = 0
            elif st == 404:
                with open(p, "wb") as f:
                    pass
                streak = 0
            else:
                fails.append((d, st))
                streak += 1
                time.sleep(60 if streak >= 10 else 4)
                if streak >= 10:
                    streak = 0
            n += 1
            if n % 200 == 0:
                print(pas, d, n, f"{time.time() - t0:.0f}s", len(fails), flush=True)
            if time.time() - t0 > 2700:
                print("time cap 45 min", flush=True); sys.exit(0)
    d += dt.timedelta(days=1)
  print("pass", pas, "done", n, f"{time.time() - t0:.0f}s", "fails", len(fails), flush=True)
  if not fails:
      break
