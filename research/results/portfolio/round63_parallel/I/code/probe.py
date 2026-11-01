"""Reachability probe: one GET per URL, logs time, URL, status, bytes; saves body to a scratch folder.

Usage: python -I probe.py <out_dir> <log_file> <url> [<url> ...]
No e-mail or contact header is sent. >= 0.5 s between requests.
"""
import hashlib
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

UA = "research-script/1.0 (python-urllib)"


def main():
    out_dir, log_file, urls = sys.argv[1], sys.argv[2], sys.argv[3:]
    for url in urls:
        t = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        status, body = None, b""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                status, body = r.status, r.read(400_000)
        except urllib.error.HTTPError as e:
            status, body = e.code, e.read(20_000) if hasattr(e, "read") else b""
        except Exception as e:  # network error
            status, body = f"ERR {type(e).__name__}: {e}", b""
        name = hashlib.sha1(url.encode()).hexdigest()[:12]
        with open(f"{out_dir}/{name}.body", "wb") as f:
            f.write(body)
        line = f"{t}\t{url}\t{status}\t{len(body)}\t{name}"
        with open(log_file, "a") as f:
            f.write(line + "\n")
        print(line)
        time.sleep(0.6)


if __name__ == "__main__":
    main()
