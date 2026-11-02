"""Stream KO network helper: plain UA, >= 1.5 s per host, logs (UTC, URL, status, bytes) to
research/data/ko_notices/requests.log, backs off on 418/429/503, stops a host on 403.
Usage: python -I net.py <url> <outfile>  (saves body into research/data/ko_notices/raw/)"""
import os, sys, time, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/ko_notices"
RAW = os.path.join(D, "raw")
os.makedirs(RAW, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
BLOCK = os.path.join(D, "blocked_hosts.txt")
UA = {"User-Agent": "research-script"}
_last = {}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(url, status, nbytes, note=""):
    LOG.write(f"{now()}\t{url}\t{status}\t{nbytes}\t{note}\n")


def blocked(host):
    return os.path.exists(BLOCK) and host in open(BLOCK).read().split()


def wait(host, gap=1.5):
    w = gap - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()


def get(url, tries=3, note=""):
    host = url.split("/")[2]
    if blocked(host):
        return None, "blocked"
    for att in range(tries):
        wait(host)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30)
            b = r.read(); log(url, r.status, len(b), note); return b, r.status
        except urllib.error.HTTPError as e:
            b = e.read() if hasattr(e, "read") else b""
            log(url, e.code, len(b), note)
            if e.code == 403:
                open(BLOCK, "a").write(host + "\n"); return b, 403
            if e.code in (418, 429, 503):
                time.sleep(20 * (att + 1)); continue
            return b, e.code
        except Exception as e:
            log(url, "ERR:" + type(e).__name__, 0, note); time.sleep(5)
    return None, "fail"


if __name__ == "__main__":
    url, out = sys.argv[1], sys.argv[2]
    b, st = get(url)
    print(st, 0 if b is None else len(b))
    if b is not None:
        open(os.path.join(RAW, out), "wb").write(b)
