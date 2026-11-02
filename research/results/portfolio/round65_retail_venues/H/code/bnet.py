"""Stream H network helper for api.bithumb.com: >= 0.3 s per host, logs time/URL/status/bytes to
research/data/bithumb/requests.log, 403 = stop, back off on 418/429/503. Plain UA, no e-mail."""
import json, os, time, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/bithumb"
os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
_last = {}


def raw(url, accept="application/json"):
    host = url.split("/")[2]
    for att in range(6):
        w = 0.3 - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script", "Accept": accept}), timeout=30) as r:
                body = r.read()
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\t200\t{len(body)}\n")
            return 200, body
        except urllib.error.HTTPError as e:
            body = e.read() if hasattr(e, "read") else b""
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\t{e.code}\t{len(body)}\n")
            if e.code == 403:
                raise SystemExit("403 stop")
            if e.code in (418, 429, 503):
                time.sleep(20 * (att + 1)); continue
            return e.code, body
        except Exception as e:
            LOG.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{url}\tERR:{type(e).__name__}\t0\n"); time.sleep(5)
    return None, b""


def get(url):
    st, b = raw(url)
    if st != 200:
        return None
    try:
        return json.loads(b)
    except Exception:
        return None
