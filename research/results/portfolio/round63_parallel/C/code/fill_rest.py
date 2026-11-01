"""Stream C: fill months listed in missing_months.csv from fapi /fapi/v1/klines (limit 1500, >= 0.5 s spacing, end
<= 2024-12-31 23:59:59 UTC). Merges into 1h/<SYM>.csv. Logs to requests.log."""
import csv, json, os, time, urllib.request, urllib.error
import datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
OUT = os.path.join(R, "data/binance_1h_full")
END = 1735689599999
logf = open(os.path.join(OUT, "requests.log"), "a")
HOUR = 3600000


def get(url):
    for a in range(5):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"}), timeout=60) as r:
                b, st = r.read(), r.status
        except urllib.error.HTTPError as e:
            b, st = b"", e.code
        except Exception:
            b, st = b"", 0
        logf.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{url},{st},{len(b)}\n"); logf.flush()
        if st == 200: return b
        if st in (400, 403, 404): return None
        if st in (418, 429): time.sleep(60)
        else: time.sleep(5)
    return None


done = set()
p = os.path.join(OUT, "filled_months.csv")
if os.path.exists(p):
    done = set(l.strip() for l in open(p))
fo = open(p, "a")
for line in open(os.path.join(OUT, "missing_months.csv")):
    sym, rest = line.strip().split(",", 1)
    path = os.path.join(OUT, "1h", sym + ".csv")
    rows = {int(r[0]): r for r in list(csv.reader(open(path)))[1:]}
    n0 = len(rows)
    for tok in rest.split(";"):
        ym = tok.split(":")[0]
        key = f"{sym},{ym}"
        if key in done: continue
        y, m = map(int, ym.split("-"))
        s = int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
        e = int(dt.datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000) - 1
        e = min(e, END)
        b = get(f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1h&startTime={s}&endTime={e}&limit=1500")
        got = 0
        if b:
            for k in json.loads(b.decode()):
                t = int(k[0])
                if t <= END and t not in rows:
                    rows[t] = [str(t), k[1], k[2], k[3], k[4], k[5], k[7], str(k[8])]; got += 1
        fo.write(key + "\n"); fo.flush()
        print(sym, ym, got, flush=True)
    if len(rows) != n0:
        with open(path + ".tmp", "w") as f:
            f.write("t,o,h,l,c,vol,qvol,n\n")
            for t in sorted(rows):
                f.write(",".join(map(str, rows[t])) + "\n")
        os.replace(path + ".tmp", path)
