"""Round 62: Binance USDT-M 1h klines in +-4 day windows around stamps with |f_prev| >= 10 bp.
Usage: python -I pull_1h.py <symbols-file> <end_ms>   (IS / VAL: end 1735689599999)"""
import csv, json, os, sys, time, urllib.request, urllib.error
import numpy as np
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "binance")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
H = 3600000
def get(url, log):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                b = r.read(); log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{r.status}\t{len(b)}\n"); return json.loads(b)
        except urllib.error.HTTPError as e:
            log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{url}\t{e.code}\t0\n")
            if e.code == 400: return None
            time.sleep(60 if e.code in (418, 429) else 5)
        except Exception as ex:
            log.write(f"EXC {url} {ex}\n"); time.sleep(5)
    return None
def stamps(s, end):
    for sub in ("funding", "funding_window"):
        p = os.path.join(B, sub, s + ".csv")
        if os.path.exists(p):
            a = np.array([[float(x) for x in r] for r in list(csv.reader(open(p)))[1:]] or np.zeros((0, 2)))
            return a[a[:, 0] <= end] if len(a) else a
    return np.zeros((0, 2))
def main():
    symfile, end = sys.argv[1], int(sys.argv[2])
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    out_dir = os.path.join(B, "perp_1h"); os.makedirs(out_dir, exist_ok=True)
    log = open(os.path.join(out_dir, "requests.log"), "a", buffering=1)
    for k, s in enumerate(l.strip() for l in open(symfile) if l.strip()):
        out = os.path.join(out_dir, f"{s}_{end}.csv")
        if os.path.exists(out): continue
        a = stamps(s, end)
        if len(a) < 2: continue
        ev = a[1:, 0][np.abs(a[:-1, 1]) >= 0.001]
        ev = ev[ev >= start]
        if not len(ev): continue
        rng = sorted((int(t // H * H) - 96 * H, int(t // H * H) + 96 * H) for t in ev)
        merged = []
        for lo, hi in rng:
            if merged and lo <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], hi)
            else: merged.append([lo, hi])
        rows = {}
        for lo, hi in merged:
            t = lo
            while t < min(hi, end):
                d = get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&limit=1500&startTime={t}&endTime={min(hi, end)}", log)
                time.sleep(0.3)
                if not d: break
                for r in d: rows[r[0]] = (r[0], r[1], r[2], r[3], r[4], r[7])
                if len(d) < 1500: break
                t = d[-1][0] + H
        with open(out, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["t", "o", "h", "l", "c", "qvol"]); w.writerows(rows[x] for x in sorted(rows))
        print(k, s, len(merged), len(rows), flush=True)
main()
