"""Round 62: 1m klines [T, T+62m) for every stamp with |f_prev| >= 30 bp. Usage: python -I pull_1m.py syms end_ms start_ms"""
import csv, json, os, sys, time, urllib.request, urllib.error
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capture as K
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
end, start = int(sys.argv[2]), int(sys.argv[3])
od = os.path.join(K.B, "perp_1m_stamps"); os.makedirs(od, exist_ok=True)
log = open(os.path.join(od, "requests.log"), "a", buffering=1)
def get(url):
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
for n, s in enumerate(syms):
    out = os.path.join(od, f"{s}_{end}.csv")
    if os.path.exists(out): continue
    a = K.stamps(s, end)
    if len(a) < 2: continue
    Ts = [int(a[j, 0] // K.H * K.H) for j in range(1, len(a)) if abs(a[j - 1, 1]) >= 0.003 and a[j, 0] >= start]
    rows = []
    for T in Ts:
        d = get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1m&limit=62&startTime={T}")
        time.sleep(0.2)
        for r in d or []: rows.append((T, r[0], r[1], r[4]))
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["T", "t", "o", "c"]); w.writerows(rows)
    print(n, s, len(Ts), flush=True)
