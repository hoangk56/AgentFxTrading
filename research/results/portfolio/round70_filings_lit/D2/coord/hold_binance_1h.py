"""Coordinator: BTCUSDT / ETHUSDT USDT-M perp 1h klines 2025-01..2026-10-29 for PREREG D2-ON's HOLD run.
Copies the 2019-2024 rows of research/data/binance_1h_full/1h/<SYM>.csv unchanged and appends data.binance.vision
monthly 1h (2025-01..2026-09) + daily (2026-10-01..29; missing days from public fapi klines). Same columns
(t,o,h,l,c,vol,qvol,n). Writes research/data/deribit_funding/hold_binance_1h/. Run with python -I."""
import csv, io, json, os, time, zipfile, urllib.request, urllib.error, datetime as dt
R = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data"
OUT = os.path.join(R, "deribit_funding", "hold_binance_1h"); os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(R, "deribit_funding", "requests.log"), "a", buffering=1)
END = 1793318400000


def get(url):
    for att in range(5):
        time.sleep(0.3)
        ts = dt.datetime.now(dt.timezone.utc).isoformat()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=60) as r:
                b = r.read(); LOG.write(f"{ts}\t{url}\t{r.status}\t{len(b)}\n"); return b
        except urllib.error.HTTPError as e:
            LOG.write(f"{ts}\t{url}\t{e.code}\t0\n")
            if e.code == 403: raise SystemExit("403 stop")
            if e.code in (400, 404): return None
            time.sleep(20 * (att + 1))
        except Exception as e:
            LOG.write(f"{ts}\t{url}\tERR:{type(e).__name__}\t0\n"); time.sleep(5)
    return None


def rows_zip(b):
    out = []
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))):
            if x and x[0].isdigit():
                t = int(x[0]); t = t // 1000 if t > 10 ** 14 else t
                out.append([t, x[1], x[2], x[3], x[4], x[5], x[7], x[8]])
    return out


for s in ("BTCUSDT", "ETHUSDT"):
    old = list(csv.reader(open(os.path.join(R, "binance_1h_full", "1h", s + ".csv"))))
    head, body = old[0], [r for r in old[1:] if int(float(r[0])) < 1735689600000]
    new = {}
    for y, m in [(y, m) for y in (2025, 2026) for m in range(1, 13) if (y, m) <= (2026, 9)]:
        b = get(f"https://data.binance.vision/data/futures/um/monthly/klines/{s}/1h/{s}-1h-{y}-{m:02d}.zip")
        for r in (rows_zip(b) if b else []): new[r[0]] = r
    for d in range(1, 30):
        day = f"2026-10-{d:02d}"
        b = get(f"https://data.binance.vision/data/futures/um/daily/klines/{s}/1h/{s}-1h-{day}.zip")
        if b:
            for r in rows_zip(b): new[r[0]] = r
        else:
            s0 = int(dt.datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
            j = get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&startTime={s0}&endTime={s0 + 86400000 - 1}&limit=30")
            for x in (json.loads(j) if j else []): new[int(x[0])] = [int(x[0]), x[1], x[2], x[3], x[4], x[5], x[7], x[8]]
    with open(os.path.join(OUT, s + ".csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(head); w.writerows(body)
        for t in sorted(new):
            if 1735689600000 <= t < END: w.writerow(new[t])
    print(s, len(body), "old rows,", sum(1 for t in new if 1735689600000 <= t < END), "new rows")
