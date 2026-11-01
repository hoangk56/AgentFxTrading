"""Stream O pull: data.binance.vision USDT-M daily metrics for the Tier A / Tier B coin-days (HYPOTHESES_O.md).
Only days <= 2024-12-31. <= 4 request starts per second (one token bucket shared by 4 threads), back off on 418/429/503,
stop on 403. Writes raw zips to research/data/binance_metrics/raw/<SYM>/ and requests.log."""
import csv, os, sys, threading, time, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import univ  # noqa: E402
from univ import xs  # noqa: E402

OUT = os.path.join(xs.R, "data", "binance_metrics")
RAW = os.path.join(OUT, "raw")
LOG = os.path.join(OUT, "requests.log")
K = 16
URL = "https://data.binance.vision/data/futures/um/daily/metrics/{s}/{s}-metrics-{d}.zip"


def day_str(d):
    return (datetime(2019, 11, 1, tzinfo=timezone.utc) + timedelta(days=int(d))).strftime("%Y-%m-%d")


def build_list():
    Pn = xs.load()
    A, rk = univ.alt_universe(Pn, K)
    P = Pn["P"]
    syms = Pn["syms"]
    rows = []
    for d in range(univ.D0, univ.D1):
        tierA = (d - univ.D0) % 2 == 0
        for i in np.where(A[:, d])[0]:
            if tierA:
                rows.append((syms[i], d, "A"))
                continue
            h = d * 24 + np.arange(2, 24)          # instants 02:00..23:00 of day d
            with np.errstate(invalid="ignore"):
                r = P[i, h] / P[i, h - 1] - 1
            if np.nanmin(np.where(np.isnan(r), 0.0, r)) <= -0.03:
                rows.append((syms[i], d, "B"))
    assert max(r[1] for r in rows) < univ.D1
    with open(os.path.join(OUT, "pull_list.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sym", "day", "date", "tier"])
        for s, d, t in rows:
            w.writerow([s, d, day_str(d), t])
    return rows


class Bucket:
    def __init__(self, gap):
        self.gap, self.t, self.lock = gap, 0.0, threading.Lock()
        self.pause_until = 0.0

    def take(self):
        with self.lock:
            now = time.time()
            start = max(now, self.t + self.gap, self.pause_until)
            self.t = start
        time.sleep(max(0.0, start - time.time()))


def worker(jobs, bucket, loglock, stop):
    while jobs and not stop.is_set():
        try:
            s, date = jobs.pop()
        except IndexError:
            return
        path = os.path.join(RAW, s, f"{s}-metrics-{date}.zip")
        if os.path.exists(path) or os.path.exists(path + ".404"):
            continue
        url = URL.format(s=s, d=date)
        for attempt in range(5):
            bucket.take()
            code, n = 0, 0
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=30) as r:
                    data = r.read()
                    code, n = r.status, len(data)
            except urllib.error.HTTPError as e:
                code = e.code
            except Exception as e:  # timeout etc.
                code = -1
            with loglock:
                with open(LOG, "a") as f:
                    f.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}\t{url}\t{code}\t{n}\n")
            if code == 200:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(data)
                break
            if code == 404:
                open(path + ".404", "w").close()
                break
            if code == 403:
                stop.set()
                print("403, stopping", url, flush=True)
                return
            if code in (418, 429, 503):
                bucket.pause_until = time.time() + 60 * (attempt + 1)
                print("backoff", code, url, flush=True)
            else:
                time.sleep(2)


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    rows = build_list()
    print("rows", len(rows), "A", sum(r[2] == "A" for r in rows), "B", sum(r[2] == "B" for r in rows),
          "symbols", len({r[0] for r in rows}), flush=True)
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        sys.exit(0)
    # order: Tier A first in date order, then B (jobs.pop takes from the end)
    jobs = [(s, day_str(d)) for s, d, t in sorted(rows, key=lambda r: (r[2] != "A", r[1]), reverse=True)]
    bucket, loglock, stop = Bucket(0.25), threading.Lock(), threading.Event()
    th = [threading.Thread(target=worker, args=(jobs, bucket, loglock, stop)) for _ in range(4)]
    t0 = time.time()
    for t in th:
        t.start()
    while any(t.is_alive() for t in th):
        time.sleep(60)
        print(f"{time.time() - t0:.0f}s left {len(jobs)}", flush=True)
    print("done", flush=True)
