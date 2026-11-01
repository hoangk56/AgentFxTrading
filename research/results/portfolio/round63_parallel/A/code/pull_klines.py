"""Pull unadjusted daily OHLCV (last 2000 bars up to 2024-12-31) per code from Tencent fqkline.

Seeded random order, one request at a time, >= 1.05 s apart, stops on 403 or at the time budget.
Raw JSON saved as research/data/ashare/raw_kline/<code>.json (untrusted; parsed later with python -I).
Run: research/.venv/bin/python -I pull_klines.py <ashare_dir> <budget_minutes>
"""
import os
import random
import sys
import time
import subprocess

UA = "research-script/1.0"
GAP = 1.05
END = "2024-12-31"


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


def main(base, budget_min):
    raw = os.path.join(base, "raw_kline")
    os.makedirs(raw, exist_ok=True)
    codes = [c.strip() for c in open(os.path.join(base, "codes.txt")) if c.strip()]
    random.Random(63).shuffle(codes)
    with open(os.path.join(base, "pull_order.txt"), "w") as f:
        f.write("\n".join(codes) + "\n")
    t0 = time.time()
    n = 0
    for code in codes:
        if time.time() - t0 > budget_min * 60:
            break
        out = os.path.join(raw, f"{code}.json")
        if os.path.exists(out):
            continue
        url = (f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,2016-01-01,{END},2000,")
        body, st = b"", "ERR"
        for attempt in range(3):
            try:
                body, st = fetch(url)
                if st != 200:
                    raise RuntimeError(st)
                break
            except Exception as e:  # noqa: BLE001
                st = e.args[0] if e.args else "ERR"
                log(base, url, st, 0)
                if st == 403:
                    sys.exit("403: stop")
                time.sleep(15 * (attempt + 1))
        log(base, url, st, len(body))
        if st == 200 and body:
            if b"captcha" in body.lower() or not body.startswith(b"{"):
                sys.exit("unexpected body (captcha?): stop")
            with open(out, "wb") as f:
                f.write(body)
            n += 1
        time.sleep(GAP)
    print("pulled", n, "in", round((time.time() - t0) / 60, 1), "min")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]))
