"""Round 60: funding for the first ~70 days after each perp listing, and each spot pair's first 1d kline.

Usage: python -I pull_listing.py funding|spotfirst <symbols-file>
"""
import csv, json, os, sys, time, urllib.request, urllib.error

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "binance")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
DAY = 86400000


def get(url, log):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                b = r.read()
                log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{r.status}\t{len(b)}\n")
                return json.loads(b)
        except urllib.error.HTTPError as e:
            log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{e.code}\t0\n")
            if e.code == 400:
                return None
            time.sleep(60 if e.code in (418, 429) else 5)
        except Exception as ex:
            log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\tEXC {ex}\n")
            time.sleep(5)
    return None


def first_kline(sym):
    p = os.path.join(R, "perp_1d", sym + ".csv")
    with open(p) as f:
        next(f)
        line = f.readline()
    return int(float(line.split(",")[0])) if line else None


def main():
    kind, symfile = sys.argv[1:3]
    syms = [s.strip() for s in open(symfile) if s.strip()]
    if kind == "funding":
        outdir = os.path.join(R, "funding_window")
        os.makedirs(outdir, exist_ok=True)
        log = open(os.path.join(outdir, "requests.log"), "a", buffering=1)
        for i, s in enumerate(syms):
            out = os.path.join(outdir, s + ".csv")
            if os.path.exists(out) or os.path.exists(os.path.join(R, "funding", s + ".csv")):
                continue
            t0 = first_kline(s)
            if t0 is None:
                continue
            rows, t = [], t0
            while t < t0 + 75 * DAY:
                d = get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={s}&limit=1000&startTime={t}&endTime={t0 + 75 * DAY}", log)
                time.sleep(0.7)
                if not d:
                    break
                rows += d
                if len(d) < 1000:
                    break
                t = d[-1]["fundingTime"] + 1
            with open(out, "w", newline="") as f:
                w = csv.writer(f); w.writerow(["t", "rate"])
                w.writerows((r["fundingTime"], r["fundingRate"]) for r in rows)
            print(i, s, len(rows), flush=True)
    else:
        out = os.path.join(R, "spot_first.csv")
        done = set()
        if os.path.exists(out):
            done = {l.split(",")[0] for l in open(out)}
        log = open(os.path.join(R, "spot_first_requests.log"), "a", buffering=1)
        with open(out, "a") as f:
            for s in syms:
                if s in done:
                    continue
                d = get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval=1d&limit=1&startTime=0", log)
                time.sleep(0.25)
                f.write(f"{s},{d[0][0] if d else ''}\n"); f.flush()


if __name__ == "__main__":
    main()
