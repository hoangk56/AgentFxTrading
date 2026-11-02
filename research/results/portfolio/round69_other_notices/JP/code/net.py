"""Stream JP network helper (pattern of A2 / B2 net.py, own log): plain UA, no e-mail, >= 1.5 s per host,
logs (UTC, URL, status, bytes, note) to research/data/jp_notices/requests.log, backs off on 418/429/503,
stops a host on 403 (host added to blocked_hosts.txt, never retried)."""
import os, time, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/jp_notices"
os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
BLK = os.path.join(D, "blocked_hosts.txt")
UA = {"User-Agent": "research-script"}
_last = {}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def log(url, status, nbytes, note=""):
    LOG.write(f"{now()}\t{url}\t{status}\t{nbytes}\t{note}\n")


def blocked():
    return set(open(BLK).read().split()) if os.path.exists(BLK) else set()


def wait(host, gap=None):
    gap = gap or (0.3 if host == "data.binance.vision" else 1.5)  # notice hosts 1.5 s (brief); binance.vision 0.3 s
    w = gap - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()


def get(url, save=None, note="GET", tries=4, timeout=40):
    """GET into bytes; logs; saves raw bytes under raw/ (untrusted data, never executed)."""
    host = url.split("/")[2]
    if host in blocked():
        log(url, "SKIP-blocked", 0, note); return "blocked", b""
    for att in range(tries):
        wait(host)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            b = r.read(); s = r.status; r.close()
            log(url, s, len(b), note)
            if save:
                p = os.path.join(D, "raw", save); os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "wb").write(b)
            return s, b
        except urllib.error.HTTPError as e:
            log(url, e.code, 0, note)
            if e.code == 403:
                open(BLK, "a").write(host + "\n"); return 403, b""
            if e.code in (418, 429, 503):
                time.sleep(20 * (att + 1)); continue
            return e.code, b""
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0, note); time.sleep(5)
    return "fail", b""


def stream(url, path, tries=4):
    """Stream a (large) file to path; returns status. Logs bytes. 403 stops the host."""
    host = url.split("/")[2]
    for att in range(tries):
        wait(host)
        n = 0
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)
            with open(path, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b); n += len(b)
            s = r.status; r.close(); log(url, s, n, "GET stream"); return s
        except urllib.error.HTTPError as e:
            log(url, e.code, 0, "GET stream")
            if e.code == 403:
                open(BLK, "a").write(host + "\n"); return 403
            if e.code in (418, 429, 503):
                time.sleep(20 * (att + 1)); continue
            return e.code
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, n, "GET stream partial")
            if os.path.exists(path):
                os.remove(path)
            time.sleep(10 * (att + 1))
    return "fail"
