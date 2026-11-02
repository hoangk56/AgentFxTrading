"""Stream M polite fetcher for api.upbit.com (quotation API, no key): >= 0.26 s per request, backs off on 418/429/503,
stops on 403, logs every request (time, URL, status, bytes) to research/data/upbit_nonkrw/requests.log. Raw bodies are
saved under research/data/upbit_nonkrw/raw/ (untrusted, parsed as JSON only)."""
import os, time, json, hashlib, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_nonkrw"
RAW = os.path.join(D, "raw"); os.makedirs(RAW, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
_last = [0.0]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def get(url, raw_ok=False):
    fn = os.path.join(RAW, hashlib.md5(url.encode()).hexdigest() + ".json")
    if os.path.exists(fn):
        return json.load(open(fn))
    for att in range(6):
        w = 0.3 - (time.time() - _last[0]); time.sleep(max(w, 0)); _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script", "Accept": "application/json"}), timeout=30) as r:
                body = r.read(); code = r.status
            LOG.write(f"{now()}\t{url}\t{code}\t{len(body)}\n")
            if raw_ok:
                return body
            js = json.loads(body)
            json.dump(js, open(fn, "w"))
            return js
        except urllib.error.HTTPError as e:
            body = e.read() if hasattr(e, "read") else b""
            LOG.write(f"{now()}\t{url}\t{e.code}\t{len(body)}\n")
            if e.code == 403:
                raise SystemExit("403 stop")
            if e.code in (418, 429, 503):
                time.sleep(10 * (att + 1)); continue
            if e.code == 404 and not raw_ok:
                json.dump(None, open(fn, "w"))
            return None
        except Exception as e:
            LOG.write(f"{now()}\t{url}\tERR:{type(e).__name__}\t0\n"); time.sleep(5)
    return None
