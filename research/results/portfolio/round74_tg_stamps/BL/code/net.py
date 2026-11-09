"""Stream BL network helper (copy of round65 A2/code/net.py, own folder): plain UA, >= 0.3 s per host (0.5 s Bybit / OKX),
logs (UTC, URL, status, bytes) to research/data/binance_tg_listing/requests.log, backs off on 418/429/503, stops on 403.
No key, no e-mail, no contact header. Never used for t.me (that goes through coord/tg.py)."""
import os, time, urllib.request, urllib.error, datetime as dt
D = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/binance_tg_listing"
os.makedirs(D, exist_ok=True)
LOG = open(os.path.join(D, "requests.log"), "a", buffering=1)
UA = {"User-Agent": "research-script"}
_last = {}
END_MS = 1735689600000  # 2025-01-01 UTC: no price request may cover anything on or after it


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def log(url, status, nbytes, note=""):
    LOG.write(f"{now()}\t{url}\t{status}\t{nbytes}\t{note}\n")


def wait(host):
    gap = 0.5 if ("bybit" in host or "okx" in host) else 0.3
    w = gap - (time.time() - _last.get(host, 0)); time.sleep(max(w, 0)); _last[host] = time.time()


def opener(url, method="GET", tries=5):
    host = url.split("/")[2]
    assert "t.me" not in host and "/bapi/" not in url
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


def get_small(url):
    r, s = opener(url)
    if r is None:
        return None, s
    b = r.read(); r.close(); log(url, s, len(b), "GET"); return b, s
