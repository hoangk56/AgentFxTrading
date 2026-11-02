"""Which of B's universe coins each venue lists today (spot vs USDT; Coinbase vs USD). Run with python -I."""
import csv, json, os
D = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/xvenue_spot/lists'
U60 = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round63_parallel/B/universe60.csv'
EXCL = {'BTCUSDT', 'ETHUSDT'}


def universe_rows():
    """(perp, spot, fac, first_ms, last_ms) of B's 2020-24 universe, BTC/ETH excluded."""
    return [(r[0], r[1], float(r[2]), int(r[3]), int(r[4])) for r in csv.reader(open(U60)) if r and r[0] not in EXCL]


def venue_symbols():
    j = json.load(open(f'{D}/okx_instruments_spot.json'))
    okx = {d['baseCcy']: d['instId'] for d in j['data'] if d['quoteCcy'] == 'USDT'}
    j = json.load(open(f'{D}/kucoin_symbols.json'))
    kc = {d['baseCurrency']: d['symbol'] for d in j['data'] if d['quoteCurrency'] == 'USDT'}
    j = json.load(open(f'{D}/coinbase_products.json'))
    cb = {d['base_currency']: d['id'] for d in j if d['quote_currency'] == 'USD'}
    j = json.load(open(f'{D}/bybit_instruments_spot.json'))
    by = {d['baseCoin']: d['symbol'] for d in j['result']['list'] if d['quoteCoin'] == 'USDT'}
    return dict(okx=okx, kucoin=kc, coinbase=cb, bybit=by)


if __name__ == '__main__':
    rows = universe_rows()
    V = venue_symbols()
    bases = sorted({r[1][:-4] for r in rows})
    print('universe coins', len(bases))
    for v, m in V.items():
        print(v, sum(b in m for b in bases))
    cnt = [sum(b in m for m in V.values()) for b in bases]
    for k in range(5):
        print('venues', k, cnt.count(k))
