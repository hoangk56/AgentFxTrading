"""Polite fetcher for stream IB (no e-mail, no contact header; every request logged).

Usage: python -I fetch.py <list_file>
Each line of list_file: "<name>\t<METHOD>\t<url>[\t<json body>]".
Body saved to research/data/scout_ib/raw/<host>/<name>.
Log (TSV): UTC time, method, URL, status, bytes, file.
>= 1.2 s between requests to the same host. A host that answers 403 is skipped for the rest of the list.
"""
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

UA = "research-script/1.0 (python-urllib)"
BASE = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/scout_ib"
LOG = os.path.join(BASE, "requests.log")
GAP = 1.2


def fetch(method, url, body, path):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data, st = b"", None
    headers = {"User-Agent": UA}
    payload = None
    if body:
        payload = body.encode()
        headers["Content-Type"] = "application/json"
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read() if method != "HEAD" else b""
            st = r.status
            if method == "HEAD":
                cl = r.headers.get("Content-Length")
                data = f"content-length={cl}\nlast-modified={r.headers.get('Last-Modified')}\n".encode()
    except urllib.error.HTTPError as e:
        st = e.code
        try:
            data = e.read()
        except Exception:
            data = b""
    except Exception as e:
        st = "ERR " + type(e).__name__
    if data:
        with open(path, "wb") as f:
            f.write(data)
    with open(LOG, "a") as f:
        f.write(f"{t}\t{method}\t{url}\t{st}\t{len(data)}\t{os.path.relpath(path, BASE)}\n")
    return st


def main():
    last, bad = {}, set()
    for line in open(sys.argv[1]):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        name, method, url = parts[0], parts[1], parts[2]
        body = parts[3] if len(parts) > 3 else None
        host = urllib.parse.urlparse(url).netloc
        if host in bad:
            print("skip (host stopped)", url)
            continue
        d = os.path.join(BASE, "raw", host)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            print("have", name)
            continue
        wait = GAP - (time.time() - last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        st = fetch(method, url, body, p)
        last[host] = time.time()
        print(st, url)
        if st == 403:
            bad.add(host)


if __name__ == "__main__":
    main()
