"""Shared polite fetcher for stream L (copy of K/code/net.py, data path changed). Logs every request to research/data/coinbase/requests.log
(time UTC, URL, status, bytes). >= 0.25 s between requests per host (0.26 used, shared lock across threads); backs off on 418 / 429 / 503;
exits on 403. Plain UA, no personal data in any request."""
import json, os, sys, threading, time, urllib.request, urllib.error

DATA = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/coinbase"
UA = {"User-Agent": "agentfx-research-script/1.0", "Accept": "application/json"}
LOG = open(os.path.join(DATA, "requests.log"), "a", buffering=1)
_last = {}
_lock = threading.Lock()
GAP = 0.26


def get(url, raw=False, tries=6):
    host = url.split("/")[2]
    for attempt in range(tries):
        with _lock:  # request starts on one host are >= GAP apart, across threads
            dt = time.time() - _last.get(host, 0.0)
            if dt < GAP:
                time.sleep(GAP - dt)
            _last[host] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                body = r.read()
                LOG.write(f"{ts}\t{url}\t{r.status}\t{len(body)}\n")
                rem = r.headers.get("Remaining-Req") or ""
                # Upbit: "group=candles; min=..; sec=N" -> pause when sec budget is nearly used
                if "sec=" in rem:
                    try:
                        if int(rem.split("sec=")[1].split(";")[0]) <= 1:
                            time.sleep(1.0)
                    except ValueError:
                        pass
                return body if raw else json.loads(body)
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403:
                sys.exit("403: stop")
            if e.code in (418, 429, 503):
                ra = e.headers.get("Retry-After")
                time.sleep(int(ra) if ra and ra.isdigit() else 5 * (attempt + 1) ** 2)
                continue
            if e.code in (400, 404):
                return None
            time.sleep(5)
        except Exception as e:  # network hiccup
            LOG.write(f"{ts}\t{url}\tERR {type(e).__name__}\t0\n")
            time.sleep(5)
    return None
