"""Venue spot 1h klines for B's universe windows (out/windows.json), requested with end <= 2024-12-31 23:59:59 UTC.
Walks each window backward from its end (all four APIs return newest first) and stops at the listing start.
Writes research/data/xvenue_spot/<venue>/<BASE>.csv (t_ms,o,h,l,c,vol) and <BASE>.done.
usage: XGAP=0.15 python -I pull.py okx|kucoin|coinbase|bybit [coin ...]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch  # noqa: E402
import lists  # noqa: E402

H = 3600000
CUT = 1735689600000
HERE = os.path.dirname(os.path.abspath(__file__))
STEP = dict(okx=100, kucoin=1500, coinbase=300, bybit=1000)
RATE_CODES = {'50011', '10006', '429000'}


def iso(ms):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ms / 1000))


def request(venue, sym, a, b):
    """Bars with a <= t <= b (ms). Returns list of (t,o,h,l,c,vol) or None on error."""
    if venue == 'okx':
        url = f'https://www.okx.com/api/v5/market/history-candles?instId={sym}&bar=1H&after={b + 1}&limit=100'
    elif venue == 'kucoin':
        url = (f'https://api.kucoin.com/api/v1/market/candles?type=1hour&symbol={sym}'
               f'&startAt={a // 1000}&endAt={b // 1000}')
    elif venue == 'coinbase':
        url = (f'https://api.exchange.coinbase.com/products/{sym}/candles?granularity=3600'
               f'&start={iso(a)}&end={iso(b)}')
    else:
        url = (f'https://api.bybit.com/v5/market/kline?category=spot&symbol={sym}&interval=60'
               f'&start={a}&end={b}&limit=1000')
    for attempt in range(4):
        st, body = fetch.get(url)
        if st in (403, 'blocked'):
            sys.exit('403: host stopped')
        if st != 200:
            if st == 400 or st == 404:
                return None
            time.sleep(5)
            continue
        try:
            j = json.loads(body)
        except Exception:
            time.sleep(3)
            continue
        if venue == 'okx':
            if j.get('code') != '0':
                if j.get('code') in RATE_CODES:
                    time.sleep(5); continue
                return None
            rows = [(int(x[0]), x[1], x[2], x[3], x[4], x[5]) for x in j['data']]
        elif venue == 'kucoin':
            if j.get('code') != '200000':
                if j.get('code') in RATE_CODES:
                    time.sleep(10); continue
                return None
            rows = [(int(x[0]) * 1000, x[1], x[3], x[4], x[2], x[5]) for x in j['data']]  # t,o,c,h,l -> t,o,h,l,c
        elif venue == 'coinbase':
            if not isinstance(j, list):
                return None
            rows = [(int(x[0]) * 1000, x[3], x[2], x[1], x[4], x[5]) for x in j]  # t,low,high,open,close,vol
        else:
            if j.get('retCode') != 0:
                if str(j.get('retCode')) in RATE_CODES:
                    time.sleep(5); continue
                return None
            rows = [(int(x[0]), x[1], x[2], x[3], x[4], x[5]) for x in j['result']['list']]
        return [r for r in rows if a <= r[0] <= b and r[0] < CUT]
    return None


def pull_coin(venue, base, sym, wins, D):
    out = {}
    nreq = 0
    for a, b in wins:
        end = min(b, CUT - 1)
        end = end - end % H
        while end >= a:
            lo = max(a, end - (STEP[venue] - 1) * H)
            rows = request(venue, sym, lo, end)
            nreq += 1
            if rows is None:
                return out, nreq, 'error'
            for r in rows:
                out[r[0]] = r
            if not rows:   # before the listing start (or a gap longer than one request)
                break
            end = lo - H
    return out, nreq, 'ok'


def main(venue, only=None):
    D = f'{fetch.ROOT}/{venue}'
    os.makedirs(D, exist_ok=True)
    W = json.load(open(os.path.join(HERE, '..', 'out', 'windows.json')))
    sym_map = lists.venue_symbols()[venue]
    if venue == 'coinbase':   # USDT-USD for the USD -> USDT conversion
        W['USDT'] = dict(win=[(1577836800000 - 8 * 86400000, CUT - 1)])
        sym_map = dict(sym_map, USDT='USDT-USD')
    todo = [c for c in sorted(W) if c in sym_map and (not only or c in only)]
    tot = 0
    t0 = time.time()
    for i, c in enumerate(todo):
        if os.path.exists(f'{D}/{c}.done'):
            continue
        rows, n, status = pull_coin(venue, c, sym_map[c], W[c]['win'], D)
        tot += n
        with open(f'{D}/{c}.csv.tmp', 'w') as f:
            f.write('t,o,h,l,c,vol\n')
            for t in sorted(rows):
                f.write(','.join(map(str, rows[t])) + '\n')
        os.replace(f'{D}/{c}.csv.tmp', f'{D}/{c}.csv')
        open(f'{D}/{c}.done', 'w').write(f'{status} {len(rows)} {n}\n')
        print(time.strftime('%H:%M:%S'), venue, i + 1, '/', len(todo), c, status, len(rows), 'bars', n, 'req',
              round(time.time() - t0), 's', flush=True)
    print('finished', venue, 'requests', tot, flush=True)


if __name__ == '__main__':
    main(sys.argv[1], set(sys.argv[2:]) or None)
