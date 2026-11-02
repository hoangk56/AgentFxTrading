"""Binance 1m klines around each X trade: windows [T - 3 min, T + 20 min] (entry) and [X - 3 min, X + 20 min] (exit),
T = entry hour start (= signal close), X = exit hour start. Adapted from round63 BM/code/pull1m.py.
Spot from data-api.binance.vision (api.binance.com robots.txt is Disallow: /), perp from fapi.binance.com.
Delisted spot pairs (HTTP 400) fall back to data.binance.vision daily 1m zips (only dates <= 2024-12-31).
usage: python -I pull1m.py perp|spot <trades.csv>     (columns perp, spot, T, X)
Writes research/data/xvenue_spot/m1/<kind>/<SYM>_<start>.csv (t,o,h,l,c,vol,n)."""
import csv
import io
import json
import os
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch  # noqa: E402

M = 60000
CUT = 1735689600000
kind, tfile = sys.argv[1], sys.argv[2]
OUT = os.path.join(fetch.ROOT, 'm1', kind)
VIS = os.path.join(fetch.ROOT, 'm1', 'vision')
os.makedirs(OUT, exist_ok=True)
os.makedirs(VIS, exist_ok=True)


def vision(sym, a, b):
    out = []
    d = a // 86400000
    while d * 86400000 < b:
        day = time.strftime('%Y-%m-%d', time.gmtime(d * 86400))
        p = os.path.join(VIS, f'{sym}-1m-{day}.zip')
        if d * 86400000 >= CUT:
            break
        if not os.path.exists(p):
            st, body = fetch.get(f'https://data.binance.vision/data/spot/daily/klines/{sym}/1m/{sym}-1m-{day}.zip')
            if st != 200:
                d += 1
                continue
            open(p, 'wb').write(body)
        with zipfile.ZipFile(p) as z:
            for nm in z.namelist():
                for x in csv.reader(io.TextIOWrapper(z.open(nm))):
                    if not x or not x[0].isdigit():
                        continue
                    t = int(x[0])
                    if t > 10 ** 14:
                        t //= 1000
                    if a <= t < b:
                        out.append((t, x[1], x[2], x[3], x[4], x[5], x[8]))
        d += 1
    return out


def window(sym, a, b):
    path = os.path.join(OUT, f'{sym}_{a}.csv')
    if os.path.exists(path):
        return 0
    b = min(b, CUT)
    n = (b - a) // M
    if kind == 'perp':
        url = f'https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1m&startTime={a}&endTime={b - 1}&limit={n}'
    else:
        url = f'https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1m&startTime={a}&endTime={b - 1}&limit={n}'
    st, body = fetch.get(url)
    if st in (403, 'blocked'):
        sys.exit('403: host stopped')
    res = []
    if st == 200:
        try:
            res = [(int(x[0]), x[1], x[2], x[3], x[4], x[5], x[8]) for x in json.loads(body)]
        except Exception:
            res = []
    elif kind == 'spot' and st == 400:
        res = vision(sym, a, b)
    elif st != 200:
        return 1   # not written, retried on the next run
    res = [r for r in res if r[0] < CUT]
    with open(path + '.tmp', 'w') as f:
        f.write('t,o,h,l,c,vol,n\n')
        for x in res:
            f.write(','.join(map(str, x)) + '\n')
    os.replace(path + '.tmp', path)
    return 1


rows = list(csv.DictReader(open(tfile)))
done = 0
for i, r in enumerate(rows):
    sym = r['perp'] if kind == 'perp' else r['spot']
    for t0 in (int(r['T']), int(r['X'])):
        done += window(sym, t0 - 3 * M, t0 + 20 * M)
    if (i + 1) % 200 == 0:
        print(time.strftime('%H:%M:%S'), kind, i + 1, '/', len(rows), done, flush=True)
print('finished', kind, len(rows), done, flush=True)
