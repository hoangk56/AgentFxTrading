"""Stream M8 network helper. Plain UA without any e-mail or name, >= 0.3 s per host (one process, sequential),
logs (UTC time, URL, status, bytes) to research/data/btc_treasury_8k/requests.log, backs off on 418/429/503,
stops on 403."""
import os, time, urllib.request, urllib.error, datetime as dt

D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/btc_treasury_8k"
os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
UA_SEC = {"User-Agent": "Mozilla/5.0 (compatible; offline-market-research/1.0; aggregate filing timestamps)"}
UA_BIN = {"User-Agent": "research-script"}
_last = {}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def log(url, status, nbytes, note=""):
    LOG.write(f"{now()}\t{url}\t{status}\t{nbytes}\t{note}\n")


def wait(host, gap=0.3):
    w = gap - (time.time() - _last.get(host, 0))
    time.sleep(max(w, 0))
    _last[host] = time.time()


def opener(url, method="GET", tries=5):
    """Open response (caller reads, closes and logs bytes) or (None, status)."""
    host = url.split("/")[2]
    hdr = UA_SEC if "sec.gov" in host else UA_BIN
    for att in range(tries):
        wait(host)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=hdr, method=method), timeout=60)
            return r, r.status
        except urllib.error.HTTPError as e:
            log(url, e.code, 0, method)
            if e.code == 403:
                raise SystemExit("403 stop: " + url)
            if e.code in (418, 429, 503):
                time.sleep(30 * (att + 1))
                continue
            return None, e.code
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0, method)
            time.sleep(5)
    return None, "fail"


def get(url, path=None):
    """GET whole body (small files). Saves to path if given. Returns bytes or None."""
    r, s = opener(url)
    if r is None:
        return None
    b = r.read()
    r.close()
    log(url, s, len(b), "GET")
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(b)
    return b
