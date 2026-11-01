"""Pull OHLCVault monthly A-share shards 2015-09..2024-12 (HOLD closed: no 2025+ months requested).

data.ohlcvault.com: public CDN built for programmatic download by its MIT client; robots.txt has no
User-agent / Disallow lines (only Cloudflare's content-signal preamble, no signals set).
Run: research/.venv/bin/python -I pull_ov.py <ashare_dir>
"""
import os
import subprocess
import sys
import time

UA = "research-script/1.0"


def main(base):
    out = os.path.join(base, "ov", "daily")
    os.makedirs(out, exist_ok=True)
    months = [f"2015-{m:02d}" for m in range(9, 13)]  # lookback only
    months += [f"{y}-{m:02d}" for y in range(2016, 2025) for m in range(1, 13)]
    for p in months:
        if True:
            assert p <= "2024-12"
            fn = os.path.join(out, f"{p}.json.gz")
            if os.path.exists(fn) and os.path.getsize(fn) > 1000:
                continue
            url = f"https://data.ohlcvault.com/daily/cn/{p}.json.gz"
            for attempt in range(3):
                r = subprocess.run(["curl", "-s", "-A", UA, "-m", "180", "-o", fn, "-w", "%{http_code} %{size_download}",
                                    url], capture_output=True, text=True)
                st = r.stdout.split()[0] if r.stdout else "ERR"
                with open(os.path.join(base, "requests.log"), "a") as f:
                    f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {url} {r.stdout}\n")
                if st == "200":
                    break
                if st in ("403",):
                    sys.exit("403: stop")
                time.sleep(20 * (attempt + 1))
            time.sleep(1.2)
    print("done")


if __name__ == "__main__":
    main(sys.argv[1])
