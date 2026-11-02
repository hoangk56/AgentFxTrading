"""Round 71 FS: polite HTTP to data.binance.vision with a request log (UTC time, URL, status, bytes).

Global pacing >= 0.3 s between request starts (all threads), back off on 418 / 429 / 503, stop on 403.
"""
import datetime as dt
import os
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))  # research/
DATA = os.path.join(R, "data", "spot_wicks")
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
    while True:
        with _lock:
            w = _last[0] + GAP - time.time()
            if w <= 0:
                _last[0] = time.time()
                return
        time.sleep(min(w, 0.1))


def get(url, timeout=40, tries=5):
    """full body bytes, or None on 404. Raises Stop403."""
    back = 5.0
    for k in range(tries):
        pace()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                data = r.read()
            log(url, 200, len(data))
            return data
        except urllib.error.HTTPError as e:
            log(url, e.code, 0)
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
            log(url, "ERR", 0, type(e).__name__)
            time.sleep(back); back *= 2
    log(url, "FAIL", 0, f"after {tries} tries")
    return "FAIL"


def open_url(url, timeout=20, tries=5):
    """open streaming response or None on 404 (caller closes)."""
    back = 5.0
    for k in range(tries):
        pace()
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
        except urllib.error.HTTPError as e:
            log(url, e.code, 0, "stream")
            if e.code == 403:
                raise Stop403(url)
            if e.code == 404:
                return None
            if e.code in (418, 429, 503):
                ra = e.headers.get("Retry-After")
                time.sleep(float(ra) if ra and ra.isdigit() else back); back *= 2
                continue
            time.sleep(back); back *= 2
        except Exception as e:
            log(url, "ERR", 0, f"stream {type(e).__name__}")
            time.sleep(back); back *= 2
    return None
