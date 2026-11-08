"""Stream BD network helper (copy of round65 A2 net.py, own log): plain UA, >= 0.3 s per host, logs (UTC, URL,
status, bytes) to research/data/binance_delist_tg/requests.log, backs off on 418/429/503, stops on 403.
Refuses any URL whose date / time parameter reaches 2025."""
import os, re, time, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance_delist_tg"
os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
UA = {"User-Agent": "research-script"}
END_MS = 1735689600000
_last = {}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def log(url, status, nbytes, note=""):
    LOG.write(f"{now()}\t{url}\t{status}\t{nbytes}\t{note}\n")


def guard(url):
    for y in re.findall(r"(20\d\d)-\d\d-\d\d", url):
        assert int(y) <= 2024, url
    for v in re.findall(r"(?:endTime|end|startTime|start)=(\d{13})", url):
        assert int(v) < END_MS, url


def wait(host, gap=0.3):
    w = gap - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()


def opener(url, method="GET", tries=5):
    guard(url)
    host = url.split("/")[2]
    for att in range(tries):
        wait(host)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA, method=method), timeout=60)
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


def get(url):
    for att in range(4):
        r, s = opener(url)
        if r is None:
            return None, s
        try:
            b = r.read(); r.close(); log(url, s, len(b), "GET")
            return b, s
        except Exception as e:  # read timeout mid-body: log and retry
            log(url, "ERR:" + type(e).__name__, 0, "GET partial"); r.close(); time.sleep(5)
    return None, "fail"
