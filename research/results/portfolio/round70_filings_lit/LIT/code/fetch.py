"""Polite fetcher for stream LIT (no e-mail, no mailto, logs every request).

Usage: python -I fetch.py <url_list_file> <delay_s>
Each line of url_list_file: "<name><TAB><url>". Body saved to research/data/lit_2025_26/raw/<host>/<name>.
Log line (TSV): UTC time, URL, status, bytes, file.
Stops after 3 consecutive 429 / 403 / 503 for a host (backs off 30 s after each 429/503).
"""
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

UA = "research-script/1.0 (python-urllib)"
BASE = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/lit_2025_26"
LOG = os.path.join(BASE, "requests.log")


def fetch(url, path):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body, st = b"", None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            st = r.status
    except urllib.error.HTTPError as e:
        st = e.code
        try:
            body = e.read()
        except Exception:
            body = b""
    except Exception as e:
        st = "ERR " + type(e).__name__
    if body:
        with open(path, "wb") as f:
            f.write(body)
    with open(LOG, "a") as f:
        f.write(f"{t}\t{url}\t{st}\t{len(body)}\t{os.path.relpath(path, BASE)}\n")
    return st


def main():
    lst, delay = sys.argv[1], float(sys.argv[2])
    bad = {}
    for line in open(lst):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        name, url = line.split("\t", 1)
        host = urllib.parse.urlparse(url).netloc
        if bad.get(host, 0) >= 3:
            continue
        d = os.path.join(BASE, "raw", host)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            continue
        st = fetch(url, p)
        print(st, name, flush=True)
        if st in (429, 403, 503):
            bad[host] = bad.get(host, 0) + 1
            if st != 403:
                time.sleep(30)
        else:
            bad[host] = 0
        time.sleep(delay)


if __name__ == "__main__":
    main()
