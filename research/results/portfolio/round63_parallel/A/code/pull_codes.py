"""Enumerate main-board A-share codes that exist (listed or delisted) via Tencent batch quotes.

Only existence is used (not the 2026 quote values). Writes research/data/ashare/codes.txt.
Run: research/.venv/bin/python -I pull_codes.py <ashare_dir>
"""
import os
import sys
import time
import subprocess

UA = "research-script/1.0"
GAP = 1.05


def fetch(url):
    """curl (urllib hung ~60 s per call on keep-alive); returns (body, status)."""
    p = subprocess.run(["curl", "-s", "-A", UA, "-m", "40", "-w", "\n%{http_code}", url],
                       capture_output=True)
    out = p.stdout
    body, _, code = out.rpartition(b"\n")
    try:
        return body, int(code)
    except ValueError:
        return b"", "ERR"


def log(base, url, status, nbytes):
    with open(os.path.join(base, "requests.log"), "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {url} {status} {nbytes}\n")


def main(base):
    raw = os.path.join(base, "raw_quote")
    os.makedirs(raw, exist_ok=True)
    codes = []
    for pre, lo, hi in [("sh", 600000, 602000), ("sh", 603000, 604000), ("sh", 605000, 606000),
                        ("sz", 1, 4000)]:
        codes += [f"{pre}{i:06d}" for i in range(lo, hi)]
    found = []
    for k in range(0, len(codes), 50):
        chunk = codes[k:k + 50]
        url = "https://qt.gtimg.cn/q=" + ",".join(chunk)
        for attempt in range(3):
            try:
                body, st = fetch(url)
                if st != 200:
                    raise RuntimeError(st)
                break
            except Exception as e:  # noqa: BLE001
                st, body = (e.args[0] if e.args else "ERR"), b""
                log(base, url, st, 0)
                if st == 403:
                    sys.exit("403: stop")
                time.sleep(10)
        log(base, url, st, len(body))
        with open(os.path.join(raw, f"q_{k:05d}.txt"), "wb") as f:
            f.write(body)
        txt = body.decode("gbk", errors="replace")
        for line in txt.split(";"):
            line = line.strip()
            if not line.startswith("v_") or "none_match" in line:
                continue
            code = line[2:line.index("=")]
            if code in chunk:
                found.append(code)
        time.sleep(GAP)
    with open(os.path.join(base, "codes.txt"), "w") as f:
        f.write("\n".join(found) + "\n")
    print(len(codes), "probed", len(found), "exist")


if __name__ == "__main__":
    main(sys.argv[1])
