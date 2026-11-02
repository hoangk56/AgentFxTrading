"""Q1 HOLD data (coordinator): for every COIN-M perpetual listed in the data.binance.vision bucket (futures/cm monthly
klines, *_PERP) and its USDT-M perp <COIN>USDT: 1h klines 2024-12..2026-09 (monthly) + 2026-10-01..29 (daily), COIN-M
fundingRate monthly 2024-12..2026-09 + dapi fundingRate for 2026-10; missing daily files are filled from the public
fapi / dapi klines REST. Same CSV layout as stream Q (t,o,h,l,c,vol,bvol,n; t,rate) under research/data/binance_cm_hold/.
Run with python -I. >= 0.3 s per request, back off on 418/429/503, stop on 403."""
import csv, io, json, os, re, sys, time, urllib.request, urllib.error, zipfile
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", ".."))
OUT = os.path.join(R, "data", "binance_cm_hold")
LOG = open(os.path.join(OUT, "requests.log"), "a", buffering=1)
UA = {"User-Agent": "research-script"}
END = 1793318400000
last = [0.0]
MONTHS = [f"{y}-{m:02d}" for y in (2024, 2025, 2026) for m in range(1, 13) if "2024-12" <= f"{y}-{m:02d}" <= "2026-09"]
DAYS = [f"2026-10-{d:02d}" for d in range(1, 30)]


def get(url):
    for att in range(6):
        w = 0.3 - (time.time() - last[0]); time.sleep(max(0, w)); last[0] = time.time()
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                b = r.read(); LOG.write(f"{ts}\t{url}\t{r.status}\t{len(b)}\n"); return b
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403: sys.exit("403 stop")
            if e.code in (418, 429, 503): time.sleep(30 * (att + 1)); continue
            if e.code in (400, 404): return None  # 400: symbol not on the REST API (delisted)
            time.sleep(5)
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR {type(e).__name__}\t0\n"); time.sleep(5)
    return None


def zrows(body):
    out = []
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        for nm in z.namelist():
            for x in csv.reader(io.TextIOWrapper(z.open(nm), encoding="utf-8", errors="replace")):
                if x and x[0].strip().isdigit():
                    out.append(x)
    return out


def kl(x):
    t = int(x[0]); t = t // 1000 if t > 10 ** 14 else t
    return (t, x[1], x[2], x[3], x[4], x[5], x[7], x[8])


def klines(market, sym):
    rows = {}
    base = f"https://data.binance.vision/data/futures/{market}"
    for m in MONTHS:
        b = get(f"{base}/monthly/klines/{sym}/1h/{sym}-1h-{m}.zip")
        for x in (zrows(b) if b else []):
            r = kl(x); rows[r[0]] = r
    for d in DAYS:
        b = get(f"{base}/daily/klines/{sym}/1h/{sym}-1h-{d}.zip")
        if b:
            for x in zrows(b):
                r = kl(x); rows[r[0]] = r
        else:
            s0 = int(time.mktime(time.strptime(d, "%Y-%m-%d")) - time.timezone) * 1000
            api = "https://fapi.binance.com/fapi/v1/klines" if market == "um" else "https://dapi.binance.com/dapi/v1/klines"
            j = get(f"{api}?symbol={sym}&interval=1h&startTime={s0}&endTime={s0 + 86400000 - 1}&limit=30")
            for x in (json.loads(j) if j else []):
                r = (int(x[0]), x[1], x[2], x[3], x[4], x[5], x[7], x[8]); rows[r[0]] = r
    return [rows[t] for t in sorted(rows) if t < END]


def cm_funding(sym):
    rows = {}
    for m in MONTHS:
        b = get(f"https://data.binance.vision/data/futures/cm/monthly/fundingRate/{sym}/{sym}-fundingRate-{m}.zip")
        for x in (zrows(b) if b else []):
            rows[int(x[0])] = x[-1]
    j = get(f"https://dapi.binance.com/dapi/v1/fundingRate?symbol={sym}&startTime=1790812800000&endTime={END - 1}&limit=1000")
    for x in (json.loads(j) if j else []):
        rows[int(x["fundingTime"])] = x["fundingRate"]
    return [(t, rows[t]) for t in sorted(rows) if t < END]


def write(path, head, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w") as f:
        f.write(head + "\n")
        for r in rows: f.write(",".join(map(str, r)) + "\n")
    os.replace(path + ".tmp", path)


if __name__ == "__main__":
    b = get("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/futures/cm/monthly/klines/&delimiter=/")
    syms = sorted({s for s in re.findall(r"klines/([A-Z0-9]+_PERP)/", b.decode())})
    print(len(syms), "COIN-M perps", flush=True)
    for s in syms:
        coin = s.split("USD_")[0]
        for market, sym, d in (("cm", s, "cm_klines_1h"), ("um", coin + "USDT", "um_klines_1h")):
            p = os.path.join(OUT, d, sym + ".csv")
            if not os.path.exists(p):
                write(p, "t,o,h,l,c,vol,bvol,n", klines(market, sym))
        p = os.path.join(OUT, "cm_fundingRate_-", s + ".csv")
        if not os.path.exists(p):
            write(p, "t,rate", cm_funding(s))
        print(s, flush=True)
