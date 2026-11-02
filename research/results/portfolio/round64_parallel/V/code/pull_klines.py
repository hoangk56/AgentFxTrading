"""Venue spot 1h klines around B's VAL 2022-24 entries (window h-24 h .. exit), requested with end < 2025-01-01.

usage: python -I pull_klines.py bybit|okx|kucoin
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coins  # noqa: E402
import fetch  # noqa: E402

H = 3600000
CUT = coins.CUT
MAXBARS = dict(bybit=1000, okx=100, kucoin=1500)


def spans():
    """Merged windows per spot base coin: {coin: [(start_ms, end_ms)]} with end < CUT."""
    w = {}
    for _, sp, h, e, x in coins.val_events():
        w.setdefault(coins.base_of(sp), []).append((h - 24 * H, min(x, CUT - H)))
    out = {}
    for c, lst in w.items():
        lst.sort()
        m = [list(lst[0])]
        for a, b in lst[1:]:
            if a <= m[-1][1] + H:
                m[-1][1] = max(m[-1][1], b)
            else:
                m.append([a, b])
        out[c] = [(a, b) for a, b in m]
    return out


def url(venue, coin, a, b):
    if venue == 'bybit':
        return (f'https://api.bybit.com/v5/market/kline?category=spot&symbol={coin}USDT&interval=60'
                f'&start={a}&end={b}&limit=1000')
    if venue == 'okx':  # returns up to 100 bars with ts < after
        return f'https://www.okx.com/api/v5/market/history-candles?instId={coin}-USDT&bar=1H&after={min(b + H, CUT)}&limit=100'
    if venue == 'kucoin':
        return (f'https://api.kucoin.com/api/v1/market/candles?type=1hour&symbol={coin}-USDT'
                f'&startAt={a // 1000}&endAt={(b + H) // 1000}')


def ok_body(venue, body):
    try:
        j = json.loads(body)
    except Exception:
        return False
    if venue == 'bybit':
        return j.get('retCode') == 0
    if venue == 'okx':
        return j.get('code') == '0'
    return j.get('code') == '200000'


def main(venue):
    D = f'{fetch.ROOT}/{venue}/klines'
    os.makedirs(D, exist_ok=True)
    nreq = 0
    status = {}
    for coin, sp in sorted(spans().items()):
        chunks = []
        for a, b in sp:
            step = (MAXBARS[venue] - 2) * H
            t = a
            while t <= b:
                chunks.append((t, min(b, t + step)))
                t += step + H
        bad = False
        for a, b in chunks:
            p = f'{D}/{coin}_{a}.json'
            if os.path.exists(p):
                continue
            st, body = fetch.get(url(venue, coin, a, b))
            nreq += 1
            if st in (403, 'blocked'):
                print('403: stopping host')
                return
            if st != 200 or not ok_body(venue, body):
                status[coin] = f'{st} {body[:120]!r}'
                bad = True
                break
            with open(p, 'wb') as f:
                f.write(body)
        if not bad:
            status[coin] = 'ok'
    json.dump(status, open(f'{D}/_status.json', 'w'), indent=1)
    print(venue, 'requests', nreq, 'coins ok', sum(v == 'ok' for v in status.values()), '/', len(status))


if __name__ == '__main__':
    main(sys.argv[1])
