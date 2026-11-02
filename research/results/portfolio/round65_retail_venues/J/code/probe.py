"""Stream J reachability probes: robots.txt first, then one request per source. Logged to
research/data/scout_j/requests.log (UTC time, method, URL, status, bytes); bodies saved under research/data/scout_j/<host>/.
Plain UA, no e-mail, no key; >= 0.3 s between requests; stops a host after a 403.
"""
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

OUT = sys.argv[1]
UA = "research-scout/1.0 (python urllib)"
LOG = os.path.join(OUT, "requests.log")

PROBES = [
    ("GET", "https://api-manager.upbit.com/robots.txt"),
    ("GET", "https://api-manager.upbit.com/api/v1/announcements?os=web&page=200&per_page=20&category=all"),
    ("GET", "https://www.hkex.com.hk/robots.txt"),
    ("GET", "https://www.hkex.com.hk/eng/ods/historicalData.aspx"),
    ("GET", "https://nextfunds.jp/robots.txt"),
    ("GET", "https://graph-api.btcturk.com/robots.txt"),
    ("GET", "https://graph-api.btcturk.com/v1/klines/history?symbol=USDTTRY&resolution=60&from=1733011200&to=1733097600"),
    ("GET", "https://datafeed.dukascopy.com/robots.txt"),
    ("GET", "https://datafeed.dukascopy.com/datafeed/USDTRY/2024/00/02/10h_ticks.bi5"),
    ("GET", "https://www.coinbase.com/robots.txt"),
    ("GET", "https://en.wikipedia.org/robots.txt"),
    ("GET", "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=List_of_S%26P_500_companies"
            "&rvlimit=1&rvstart=2024-12-31T23:59:59Z&rvdir=older&rvprop=ids%7Ctimestamp%7Csize&format=json"),
    ("GET", "https://data.binance.vision/robots.txt"),
    ("HEAD", "https://data.binance.vision/data/spot/monthly/klines/BTCUPUSDT/1h/BTCUPUSDT-1h-2021-05.zip"),
]


def log(line):
    with open(LOG, "a") as f:
        f.write(line + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    blocked = set()
    last = {}
    for i, (method, url) in enumerate(PROBES):
        host = urlparse(url).netloc
        if host in blocked:
            log(f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}\t{method}\t{url}\tSKIPPED (host 403 earlier)\t0")
            continue
        wait = 0.3 - (time.time() - last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        body, status = b"", None
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                status = r.status
                body = r.read() if method == "GET" else b""
                if method == "HEAD":
                    body_len = r.headers.get("Content-Length", "0")
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                body = e.read()
            except Exception:
                body = b""
        except Exception as e:  # noqa: BLE001
            status = f"ERR {type(e).__name__}"
        last[host] = time.time()
        if status == 403:
            blocked.add(host)
        n = body_len if method == "HEAD" and status == 200 else len(body)
        log(f"{ts}\t{method}\t{url}\t{status}\t{n}")
        d = os.path.join(OUT, host)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"probe{i:02d}.bin"), "wb") as f:
            f.write(body)
        print(ts, method, status, n, url)


if __name__ == "__main__":
    main()
