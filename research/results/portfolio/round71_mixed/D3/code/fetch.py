"""Polite GET for stream D3. Logs UTC time, URL, status, bytes to research/data/funding_formulas/requests.log.
Plain UA, no personal data; >= gap s between requests to one host; backs off on 418/429/503, stops on 403.
Usage as a script: python -I fetch.py URL OUTFILE"""
import time, datetime as dt, urllib.request, urllib.error, sys, os

ROOT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/funding_formulas"
LOG = os.path.join(ROOT, "requests.log")
UA = "research-script/1.0 (python-urllib)"
_last = {}


def get(url, gap=0.6, tries=6, timeout=90):
    host = url.split("/")[2]
    st = None
    for k in range(tries):
        w = _last.get(host, 0) + gap - time.time()
        if w > 0:
            time.sleep(w)
        st, data = None, b""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/plain, */*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read(); st = r.status
        except urllib.error.HTTPError as e:
            st = e.code
            try:
                data = e.read()
            except Exception:
                data = b""
        except Exception as e:
            st = "ERR " + type(e).__name__
        _last[host] = time.time()
        with open(LOG, "a") as fh:
            fh.write(f"{dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\t{url}\t{st}\t{len(data)}\n")
        if st == 200:
            return data
        if st == 403:
            sys.exit("403 stop: " + url)
        if st == 404:
            return None
        time.sleep(30 * (k + 1) if st in (418, 429, 503) else 5 * (k + 1))
    raise RuntimeError(f"failed {url} {st}")


if __name__ == "__main__":
    b = get(sys.argv[1])
    if b is not None:
        open(sys.argv[2], "wb").write(b)
        print(len(b))
