"""Round 58 A: pull Binance USDT-M perp 1d klines, funding, spot 1d klines (public REST, no key).

Usage: python -I pull_binance.py perp|funding|spot <symbols-file> <out-dir>
Writes one CSV per symbol; skips files already complete. ~4 requests/s, backs off on 418/429.
"""
import csv, json, os, sys, time, urllib.request, urllib.error

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
START = 1567296000000  # 2019-09-01
END = 1793404800000    # 2026-10-31 00:00 UTC
LOG = None


def get(url):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
                LOG.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{r.status}\t{len(body)}\n")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            LOG.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{e.code}\t0\n")
            if e.code in (418, 429):
                time.sleep(60 * (attempt + 1))
                continue
            if e.code == 400:
                return None
            time.sleep(5)
        except Exception:
            time.sleep(5)
    return None


def klines(base, sym, out):
    rows, t = [], START
    while t < END:
        d = get(f"{base}?symbol={sym}&interval=1d&limit=1000&startTime={t}&endTime={END - 1}")
        time.sleep(0.25)
        if not d:
            break
        rows += d
        if len(d) < 1000:
            break
        t = d[-1][0] + 86400000
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "o", "h", "l", "c", "vol", "qvol", "n"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8]])
    return len(rows)


def funding(sym, out):
    rows, t = [], START
    while t < END:
        d = get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&limit=1000&startTime={t}&endTime={END - 1}")
        time.sleep(0.7)  # endpoint limit 500 / 5 min / IP
        if not d:
            break
        rows += d
        if len(d) < 1000:
            break
        t = d[-1]["fundingTime"] + 1
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "rate"])
        for r in rows:
            w.writerow([r["fundingTime"], r["fundingRate"]])
    return len(rows)


def main():
    global LOG
    kind, symfile, outdir = sys.argv[1:4]
    os.makedirs(outdir, exist_ok=True)
    LOG = open(os.path.join(outdir, "requests.log"), "a", buffering=1)
    syms = [s.strip() for s in open(symfile) if s.strip()]
    for i, s in enumerate(syms):
        out = os.path.join(outdir, s + ".csv")
        if os.path.exists(out):
            continue
        if kind == "perp":
            n = klines("https://fapi.binance.com/fapi/v1/klines", s, out)
        elif kind == "spot":
            n = klines("https://api.binance.com/api/v3/klines", s, out)
        else:
            n = funding(s, out)
        print(i, s, n, flush=True)


if __name__ == "__main__":
    main()
