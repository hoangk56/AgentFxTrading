"""1m daily klines for binance_cm_hold/need_m1.txt (market sym day): data.binance.vision daily zip, else the public
fapi / dapi klines REST for that day (2 requests of 1,000 bars). Writes m1/<market>/<SYM>/<day>.csv (t,o,c,n) like
stream Q. Run with python -I. >= 0.3 s per request; back off on 418/429/503; stop on 403."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hold_pull as hp
done = 0
for line in open(os.path.join(hp.OUT, "need_m1.txt")):
    mk, sym, day = line.split()
    od = os.path.join(hp.OUT, "m1", mk, sym); os.makedirs(od, exist_ok=True)
    path = os.path.join(od, day + ".csv")
    if os.path.exists(path):
        continue
    rows = []
    b = hp.get(f"https://data.binance.vision/data/futures/{mk}/daily/klines/{sym}/1m/{sym}-1m-{day}.zip")
    if b:
        for x in hp.zrows(b):
            t = int(x[0]); t = t // 1000 if t > 10 ** 14 else t
            rows.append((t, x[1], x[4], x[8]))
    else:
        s0 = int(time.mktime(time.strptime(day, "%Y-%m-%d")) - time.timezone) * 1000
        api = "https://fapi.binance.com/fapi/v1/klines" if mk == "um" else "https://dapi.binance.com/dapi/v1/klines"
        for a in (s0, s0 + 1000 * 60000):
            j = hp.get(f"{api}?symbol={sym}&interval=1m&startTime={a}&endTime={min(a + 1000 * 60000, s0 + 86400000) - 1}&limit=1000")
            rows += [(int(x[0]), x[1], x[4], x[8]) for x in (json.loads(j) if j else [])]
    rows = sorted({r[0]: r for r in rows if r[0] < hp.END}.values())
    with open(path + ".tmp", "w") as f:
        f.write("t,o,c,n\n")
        for r in rows: f.write(",".join(map(str, r)) + "\n")
    os.replace(path + ".tmp", path)
    done += 1
print("finished", done)
