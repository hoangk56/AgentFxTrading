"""Stream B2 network helper (copy of A2's net.py, own log): plain UA, no e-mail, >= 1 s per Bithumb host and
>= 0.3 s elsewhere, logs (UTC, URL, status, bytes, note) to research/data/bithumb_notice/requests.log,
backs off on 418/429/503, stops on 403."""
import os, time, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/bithumb_notice"
os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
UA = {"User-Agent": "research-script"}
_last = {}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def log(url, status, nbytes, note=""):
    LOG.write(f"{now()}\t{url}\t{status}\t{nbytes}\t{note}\n")


def wait(host):
    gap = 1.05 if "bithumb" in host else 0.3
    w = gap - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()


def opener(url, method="GET", tries=5, headers=None):
    """Returns an open response (caller reads / closes and logs the bytes) or (None, status)."""
    host = url.split("/")[2]
    h = dict(UA); h.update(headers or {})
    for att in range(tries):
        wait(host)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=h, method=method), timeout=60)
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


def get(url, save=None, note="GET"):
    """GET into bytes; logs; optionally saves raw bytes under raw/ (untrusted data, never executed)."""
    r, s = opener(url)
    if r is None:
        return s, b""
    b = r.read(); r.close()
    log(url, s, len(b), note)
    if save:
        p = os.path.join(D, "raw", save); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(b)
    return s, b
