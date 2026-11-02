"""Polite GET with logging for stream TRY. Log: research/data/usdtry_premium/requests.log
(UTC time, URL, status, bytes). Plain UA, no e-mail, no key. Per-host minimum spacing; 403 stops the host;
418 / 429 / 503 back off (exponential, up to 4 tries)."""
import os
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

ROOT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/usdtry_premium"
LOG = os.path.join(ROOT, "requests.log")
UA = "research-scout/1.0"  # "(python urllib)" in the UA gets 429 from Dukascopy; still a plain non-browser UA
SPACING = {"graph-api.btcturk.com": 1.05, "datafeed.dukascopy.com": 0.5}
_last = {}
_blocked = set()
_lock = threading.Lock()


def log(url, status, n):
    with open(LOG, "a") as f:
        f.write(f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}\t{url}\t{status}\t{n}\n")


def get(url, timeout=30, tries=4):
    host = urlparse(url).netloc
    if host in _blocked:
        log(url, "SKIPPED_403_HOST", 0)
        return None, 403
    for attempt in range(tries):
        with _lock:  # request starts to one host are spaced >= SPACING even with several threads
            wait = SPACING.get(host, 1.0) - (time.time() - _last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            _last[host] = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        status, body = None, b""
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                status, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                body = e.read()
            except Exception:  # noqa: BLE001
                body = b""
        except Exception as e:  # noqa: BLE001
            status = f"ERR_{type(e).__name__}"
        with _lock:
            log(url, status, len(body))
        if status == 403:
            _blocked.add(host)
            return None, 403
        if status in (418, 429, 503) or (isinstance(status, str) and status.startswith("ERR")):
            time.sleep(min(60, 2 * 2 ** attempt))
            continue
        return body, status
    return None, status
