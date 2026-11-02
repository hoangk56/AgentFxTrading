"""Stream O2 network helper (adapted from A2/code/net.py): plain UA (no e-mail, no browser disguise), >= 0.5 s per host,
logs (UTC, URL, status, bytes, note) to research/data/okx_bybit_notice/requests.log, backs off on 418/429/503, stops a
host on 403."""
import os, time, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/okx_bybit_notice"
os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
UA = {"User-Agent": "research-script"}
_last = {}
BLOCKED = set()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def log(url, status, nbytes, note=""):
    LOG.write(f"{now()}\t{url}\t{status}\t{nbytes}\t{note}\n")


def wait(host, gap=0.5):
    w = gap - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()


def opener(url, method="GET", tries=5, gap=0.5):
    """Returns (open response, status) (caller reads / closes and logs the bytes) or (None, status)."""
    host = url.split("/")[2]
    if host in BLOCKED:
        return None, "blocked"
    for att in range(tries):
        wait(host, gap)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA, method=method), timeout=60)
            return r, r.status
        except urllib.error.HTTPError as e:
            log(url, e.code, 0, method)
            if e.code == 403:
                BLOCKED.add(host)
                return None, 403
            if e.code in (418, 429, 503):
                time.sleep(30 * (att + 1)); continue
            return None, e.code
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0, method); time.sleep(5)
    return None, "fail"


def get(url, note="GET", gap=0.5):
    """Small GET: returns (bytes or None, status); logs it."""
    r, s = opener(url, gap=gap)
    if r is None:
        return None, s
    b = r.read(); r.close()
    log(url, s, len(b), note)
    return b, s
