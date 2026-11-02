"""Stream W7 network helper: plain UA (no e-mail, no contact header), >= 0.25 s per host (0.5 s for Bybit),
logs (UTC, URL, status, bytes, note) to research/data/listing_window/requests.log, backs off on 418/429/503,
stops on 403. Never requests anything dated 2025 or later (callers assert it)."""
import os, time, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/listing_window"
os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
UA = {"User-Agent": "research-script"}
_last = {}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(url, status, nbytes, note=""):
    LOG.write(f"{now()}\t{url}\t{status}\t{nbytes}\t{note}\n")


def wait(host):
    gap = 0.5 if "bybit" in host else 0.27
    w = gap - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()


def opener(url, method="GET", tries=5):
    """Open response (caller reads / closes and logs bytes) or (None, status)."""
    host = url.split("/")[2]
    for att in range(tries):
        wait(host)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA, method=method), timeout=90)
            return r, r.status
        except urllib.error.HTTPError as e:
            log(url, e.code, 0, method)
            if e.code == 403:
                raise SystemExit("403 stop: " + url)
            if e.code in (418, 429, 503):
                time.sleep(30 * (att + 1)); continue
            return None, e.code
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0, method); time.sleep(5)
    return None, "fail"


def get(url, note=""):
    """Small GET: returns (bytes or None, status)."""
    r, s = opener(url)
    if r is None:
        return None, s
    try:
        b = r.read(); r.close()
    except Exception as e:
        log(url, "ERR:" + type(e).__name__, 0, note); return None, "err"
    log(url, s, len(b), note)
    return b, s
