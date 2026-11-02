"""Tải nến tháng spot từ data.binance.vision (chỉ tới 2024-12), ghi requests.log.

Chạy: research/.venv/bin/python -I fetch.py <data_dir> <interval> SYM [SYM ...]
"""
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

BASE = "https://data.binance.vision/data/spot/monthly/klines"
GAP = 0.3


def log(data_dir, url, status, nbytes):
    with open(os.path.join(data_dir, "requests.log"), "a") as f:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        f.write(f"{ts}\t{url}\t{status}\t{nbytes}\n")


def get(data_dir, url):
    delay = 2.0
    for _ in range(6):
        time.sleep(GAP)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            log(data_dir, url, 200, len(body))
            return 200, body
        except urllib.error.HTTPError as e:
            log(data_dir, url, e.code, 0)
            if e.code in (418, 429, 503):
                time.sleep(delay)
                delay *= 2
                continue
            if e.code == 403:
                print("403: dừng", url)
                sys.exit(3)
            return e.code, None
        except Exception as e:  # mạng chập chờn: thử lại
            log(data_dir, url, "ERR " + type(e).__name__, 0)
            time.sleep(delay)
            delay *= 2
    return -1, None


def main():
    data_dir, interval, syms = sys.argv[1], sys.argv[2], sys.argv[3:]
    if not os.path.exists(os.path.join(data_dir, "requests.log")):
        with open(os.path.join(data_dir, "requests.log"), "w") as f:
            f.write("time\turl\tstatus\tbytes\n")
    for sym in syms:
        out = os.path.join(data_dir, "raw", interval, sym)
        os.makedirs(out, exist_ok=True)
        got = 0
        for y in range(2018, 2025):
            for m in range(1, 13):
                name = f"{sym}-{interval}-{y}-{m:02d}.zip"
                path = os.path.join(out, name)
                if os.path.exists(path):
                    got += 1
                    continue
                st, body = get(data_dir, f"{BASE}/{sym}/{interval}/{name}")
                if st == 200:
                    with open(path, "wb") as f:
                        f.write(body)
                    got += 1
        print(sym, interval, "months", got, flush=True)


if __name__ == "__main__":
    main()
