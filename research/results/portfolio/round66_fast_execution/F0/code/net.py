"""Round 66 F0: polite HTTP to data.binance.vision with a request log (UTC time, URL, status, bytes)."""
import datetime as dt
import os
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
DATA = os.path.join(R, "data", "wick_aggtrades")
LOG = os.path.join(DATA, "requests.log")
UA = {"User-Agent": "research-script/1.0 (python-urllib)"}
_lock = threading.Lock()
_last = [0.0]
GAP = 0.3


class Stop403(Exception):
    pass


def log(url, status, nbytes, note=""):
    os.makedirs(DATA, exist_ok=True)
    with _lock:
        with open(LOG, "a") as f:
            f.write(f"{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}\t{url}\t{status}\t{nbytes}\t{note}\n")


def pace():
    with _lock:
        w = _last[0] + GAP - time.time()
        if w > 0:
            time.sleep(w)
        _last[0] = time.time()


def open_url(url, method="GET", timeout=60, tries=5):
    """returns an open response (caller reads / closes) or None on 404. Backs off on 418 / 429 / 503 and network errors."""
    back = 5.0
    for k in range(tries):
        pace()
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA, method=method), timeout=timeout)
            return r
        except urllib.error.HTTPError as e:
            log(url, e.code, 0, method)
            if e.code == 403:
                raise Stop403(url)
            if e.code == 404:
                return None
            if e.code in (418, 429, 503):
                ra = e.headers.get("Retry-After")
                time.sleep(float(ra) if ra and ra.isdigit() else back); back *= 2
                continue
            time.sleep(back); back *= 2
        except Exception as e:  # timeouts, resets
            log(url, "ERR", 0, f"{method} {type(e).__name__}")
            time.sleep(back); back *= 2
    return None
