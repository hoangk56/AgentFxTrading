"""Round 59: pull Bybit linear and Hyperliquid funding + 1d candles (public, no key).

Usage: python -I pull_venues.py bybit|hl <binance-symbols-file> <out-dir>
Writes <out>/funding/<BINANCE_SYMBOL>.csv (t,rate) and <out>/perp_1d/<BINANCE_SYMBOL>.csv (t,o,h,l,c,vol,qvol,n).
"""
import csv, json, os, sys, time, urllib.request, urllib.error

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", "Content-Type": "application/json"}
START = 1590969600000  # 2020-06-01
END = 1793404800000    # 2026-10-31
LOG = None


def fetch(url, body=None):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(), headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                b = r.read()
                LOG.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{json.dumps(body) if body else ''}\t{r.status}\t{len(b)}\n")
                return json.loads(b)
        except urllib.error.HTTPError as e:
            LOG.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{json.dumps(body) if body else ''}\t{e.code}\t0\n")
            time.sleep(30 * (attempt + 1) if e.code in (403, 429) else 3)
        except Exception as ex:
            LOG.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\tEXC {ex}\n")
            time.sleep(5)
    return None


def hl_coin(sym):
    base = sym[:-4]
    if base.startswith("1000") and not base[4].isdigit():
        return "k" + base[4:]
    return base


def bybit(sym, outdir):
    fr, end = [], END
    while True:
        d = fetch(f"https://api.bybit.com/v5/market/funding/history?category=linear&symbol={sym}&limit=200&endTime={end}")
        time.sleep(0.1)
        if not d or d.get("retCode") != 0:
            return None
        lst = d["result"]["list"]
        if not lst:
            break
        fr += [(int(x["fundingRateTimestamp"]), x["fundingRate"]) for x in lst]
        end = int(lst[-1]["fundingRateTimestamp"]) - 1
        if end < START or len(lst) < 200:
            break
    kl, end = [], END
    while True:
        d = fetch(f"https://api.bybit.com/v5/market/kline?category=linear&symbol={sym}&interval=D&limit=1000&end={end}")
        time.sleep(0.1)
        if not d or d.get("retCode") != 0:
            break
        lst = d["result"]["list"]
        if not lst:
            break
        kl += [(int(x[0]), x[1], x[2], x[3], x[4], x[5], x[6], 0) for x in lst]
        end = int(lst[-1][0]) - 1
        if end < START or len(lst) < 1000:
            break
    return sorted(set(fr)), sorted(set(kl))


def hl(sym, outdir):
    coin = hl_coin(sym)
    fr, t = [], START
    while t < END:
        d = fetch("https://api.hyperliquid.xyz/info", {"type": "fundingHistory", "coin": coin, "startTime": t, "endTime": END})
        time.sleep(2.4)
        if not d:
            break
        fr += [(int(x["time"]), x["fundingRate"]) for x in d]
        if len(d) < 500:
            break
        t = int(d[-1]["time"]) + 1
    if not fr:
        return None
    d = fetch("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": coin, "interval": "1d", "startTime": START, "endTime": END}})
    time.sleep(2.4)
    kl = [(int(x["t"]), x["o"], x["h"], x["l"], x["c"], x["v"], float(x["v"]) * float(x["c"]), x["n"]) for x in (d or [])]
    return sorted(set(fr)), sorted(set(kl))


def main():
    global LOG
    venue, symfile, outdir = sys.argv[1:4]
    for sub in ("funding", "perp_1d"):
        os.makedirs(os.path.join(outdir, sub), exist_ok=True)
    LOG = open(os.path.join(outdir, "requests.log"), "a", buffering=1)
    for i, s in enumerate(l.strip() for l in open(symfile) if l.strip()):
        fo = os.path.join(outdir, "funding", s + ".csv")
        if os.path.exists(fo):
            continue
        res = (bybit if venue == "bybit" else hl)(s, outdir)
        if res is None:
            open(fo + ".missing", "w").close()
            print(i, s, "missing", flush=True)
            continue
        fr, kl = res
        with open(fo, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["t", "rate"]); w.writerows(fr)
        with open(os.path.join(outdir, "perp_1d", s + ".csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["t", "o", "h", "l", "c", "vol", "qvol", "n"]); w.writerows(kl)
        print(i, s, len(fr), len(kl), flush=True)


if __name__ == "__main__":
    main()
