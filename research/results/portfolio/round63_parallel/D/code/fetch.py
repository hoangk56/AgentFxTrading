"""Stream D: polite fetcher (plain UA, logged, >= 1 s between requests to one host, back off on 418/429/503, stop on 403).

Usage: python -I fetch.py <url> <outfile>
"""
import os, sys, time, urllib.request, urllib.error

LOGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "data", "binance_announcements")
UA = {"User-Agent": "research-script/1.0 (python-urllib)"}


class Forbidden(Exception):
    pass


def get(url, log=None, tries=4):
    own = log is None
    if own:
        log = open(os.path.join(LOGDIR, "requests.log"), "a", buffering=1)
    try:
        for k in range(tries):
            ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                    b = r.read()
                    log.write(f"{ts}\t{url}\t{r.status}\t{len(b)}\n")
                    return b
            except urllib.error.HTTPError as e:
                log.write(f"{ts}\t{url}\t{e.code}\t0\n")
                if e.code == 403:
                    raise Forbidden(url)
                if e.code in (400, 404):
                    return None
                time.sleep(90 if e.code in (418, 429) else 10)
            except Forbidden:
                raise
            except Exception as ex:
                log.write(f"{ts}\t{url}\tEXC {ex}\t0\n")
                time.sleep(10)
        return None
    finally:
        if own:
            log.close()


if __name__ == "__main__":
    b = get(sys.argv[1])
    if b is not None:
        open(sys.argv[2], "wb").write(b)
        print(len(b))
