"""Polite fetcher for stream P: plain UA, >= 1 s per host, every request logged, bodies saved under data/cny_fix/.

Usage: python -I fetch.py <url> <out_name> [POST-body]
"""
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

DATA = Path("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/cny_fix")
LOG = DATA / "requests.log"
STAMP = DATA / ".last_request"
UA = "research-script/1.0 (python-urllib; low volume)"


def _wait(host: str) -> None:
    f = STAMP.with_name(f".last_{host}")
    if f.exists():
        dt = time.time() - float(f.read_text() or 0)
        if dt < 1.5:
            time.sleep(1.5 - dt)
    f.write_text(str(time.time()))


def fetch(url: str, out_name: str, data: bytes | None = None, headers: dict | None = None) -> tuple[int, bytes]:
    host = urlparse(url).netloc
    _wait(host)
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h)
    t = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            status, body = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read() or b""
    except Exception as e:  # network error: log it
        status, body = -1, repr(e).encode()
    out = DATA / "raw" / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
    with LOG.open("a") as f:
        f.write(f"{t}\t{'POST' if data else 'GET'}\t{url}\t{status}\t{len(body)}\t{out.name}\n")
    return status, body


if __name__ == "__main__":
    body = sys.argv[3].encode() if len(sys.argv) > 3 else None
    s, b = fetch(sys.argv[1], sys.argv[2], body)
    print(s, len(b))
