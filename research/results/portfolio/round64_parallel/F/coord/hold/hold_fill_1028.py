"""Fill the 2026-10-28 daily 1m klines that data.binance.vision does not have (404 for every symbol on 2026-11-01)
from the public keyless fapi /fapi/v1/klines (1,440 bars, limit 1500, one request per symbol). Same npz format as
hold_pull.py; replaces the .404 marker. Run with python -I; >= 0.3 s apart, stop on 403."""
import json, os, time, urllib.request, urllib.error, datetime as dt
import numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", ".."))
D = os.path.join(R, "data", "binance_1m_wicks_hold"); NPZ = os.path.join(D, "npz")
log = open(os.path.join(D, "requests.log"), "a")
S = 1793145600000  # 2026-10-28 00:00 UTC
for f in sorted(os.listdir(NPZ)):
    if not f.endswith("_2026-10-28.npz.404"):
        continue
    s = f.split("_")[0]
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1m&startTime={S}&endTime={S + 86400000 - 1}&limit=1500"
    time.sleep(0.3)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=30) as r:
            body = r.read()
        log.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{url},200,{len(body)}\n"); log.flush()
    except urllib.error.HTTPError as e:
        log.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()},{url},{e.code},0\n"); log.flush()
        if e.code == 403:
            raise SystemExit("403 stop")
        print(s, e.code); continue
    k = json.loads(body)
    if not k:
        print(s, "empty"); continue
    a = np.array([[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[7]), float(x[8])] for x in k])
    m = (a[:, 0] // 60000).astype(np.int64)
    np.savez_compressed(os.path.join(NPZ, f"{s}_2026-10-28.npz"), m=m.astype(np.int32), o=a[:, 1].astype(np.float32),
                        h=a[:, 2].astype(np.float32), l=a[:, 3].astype(np.float32), c=a[:, 4].astype(np.float32),
                        qv=a[:, 5].astype(np.float32), n=a[:, 6].astype(np.int32))
    os.remove(os.path.join(NPZ, f))
    print(s, len(m), flush=True)
