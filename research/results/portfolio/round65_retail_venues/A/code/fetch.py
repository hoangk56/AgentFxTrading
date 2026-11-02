"""Polite fetcher for stream A (copy of W/code/fetch.py, own folder, 1.5 s gap): logs every request to research/data/upbit_announce/requests.log, >= 0.3 s per host,
backs off on 418/429/503, stops a host on 403. Saves raw bodies under research/data/upbit_announce/raw/ (untrusted)."""
import os, sys, time, hashlib, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_announce"
RAW = os.path.join(D, "raw"); os.makedirs(RAW, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
UA = "research-script"
_last = {}
BLOCKED = set()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def get(url, accept="application/json", tries=5, save=None):
    host = url.split("/")[2]
    if host in BLOCKED:
        return None, "blocked"
    for att in range(tries):
        w = float(os.environ.get("GAP", "1.5")) - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read(); code = r.status
            LOG.write(f"{now()}\t{url}\t{code}\t{len(body)}\n")
            if save:
                open(os.path.join(RAW, save), "wb").write(body)
            return body, code
        except urllib.error.HTTPError as e:
            body = e.read() if hasattr(e, "read") else b""
            LOG.write(f"{now()}\t{url}\t{e.code}\t{len(body)}\n")
            if e.code == 403:
                BLOCKED.add(host); return None, 403
            if e.code in (418, 429, 503):
                time.sleep(20 * (att + 1)); continue
            return body, e.code
        except Exception as e:
            LOG.write(f"{now()}\t{url}\tERR:{type(e).__name__}\t0\n"); time.sleep(5)
    return None, "fail"


if __name__ == "__main__":
    for u in sys.argv[1:]:
        name = hashlib.md5(u.encode()).hexdigest()[:10] + ".txt"
        b, c = get(u, accept="*/*", save=name)
        print(u, c, len(b or b""), name)
