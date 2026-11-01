"""Rate-limited keyless GET with a requests.log (time, URL, status, bytes). No personal data in requests."""
import time, urllib.request, urllib.error, hashlib, os, threading
LOG = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/polymarket/requests.log"
UA = "research-script/1.0 (python urllib)"
_lock = threading.Lock()
_last = {}
MIN_GAP = {"gamma-api.polymarket.com": 0.25, "clob.polymarket.com": 0.05, "data-api.polymarket.com": 0.25}

class Stop(Exception):
    pass

def get(url, host_gap=None, retries=4):
    host = url.split("/")[2]
    gap = host_gap if host_gap is not None else MIN_GAP.get(host, 0.25)
    for attempt in range(retries):
        with _lock:
            w = _last.get(host, 0) + gap - time.time()
            if w > 0:
                time.sleep(w)
            _last[host] = time.time()
        status, body = None, b""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                status, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                body = e.read()
            except Exception:
                body = b""
        except Exception as e:
            status = "ERR " + type(e).__name__
        with _lock:
            with open(LOG, "a") as f:
                f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{status}\t{len(body)}\n")
        if status == 403:
            raise Stop("403 on " + url)
        if status in (418, 429, 503) or (isinstance(status, str)) or (isinstance(status, int) and status >= 500):
            time.sleep(2 * (attempt + 1) ** 2)
            continue
        return status, body
    return status, body
