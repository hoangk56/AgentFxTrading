"""Per venue: which of B's coins can be borrowed today, rate (no-VIP), cap in USDT. Parses saved bodies only.

Units (from docs / sanity checks, see STREAM_V.md): Bybit hourlyBorrowRate = per hour, maxBorrowingAmount = coin;
OKX basic rate = per day, quota = coin (regular Lv1 loanQuotaCoef 1); Gate history_loan_rate = per hour (one point per
hour), user_max_borrow_amount = USDT; KuCoin / Binance: no public rate or cap.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coins  # noqa: E402

D = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/margin_venues'
OUT = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round64_parallel/V/out'
os.makedirs(OUT, exist_ok=True)
J = lambda p: json.load(open(f'{D}/{p}'))  # noqa: E731
ALIAS = {}  # venue-specific names filled below


def bybit():
    vip = {x['vipLevel']: x['list'] for x in J('bybit/vip_margin_all.json')['result']['vipCoinList']}['No VIP']
    px = {t['symbol']: float(t['lastPrice'] or 0) for t in J('bybit/tickers_spot.json')['result']['list']}
    pairs = {i['baseCoin']: i for i in J('bybit/spot_instruments.json')['result']['list'] if i['quoteCoin'] == 'USDT'}
    out = {}
    for c in vip:
        cc = c['currency']
        ok = c['borrowable'] and cc in pairs and pairs[cc]['marginTrading'] != 'none' and pairs[cc]['status'] == 'Trading'
        if not ok:
            continue
        p = px.get(cc + 'USDT', 0)
        out[cc] = dict(rate_yr=float(c['hourlyBorrowRate'] or 'nan') * 8760,
                       cap_usdt=float(c['maxBorrowingAmount'] or 0) * p)
    return out


def okx():
    d = J('okx/interest_rate_loan_quota.json')['data'][0]
    coef = float([x for x in d['regular'] if x['level'] == 'Lv1'][0]['loanQuotaCoef'])
    px = {t['instId']: float(t['last'] or 0) for t in J('okx/tickers_spot.json')['data']}
    pairs = {i['baseCcy'] for i in J('okx/instruments_margin.json')['data'] if i['quoteCcy'] == 'USDT' and i['state'] == 'live'}
    out = {}
    for x in d['basic']:
        c = x['ccy']
        if c not in pairs:
            continue
        out[c] = dict(rate_yr=float(x['rate']) * 365, cap_usdt=float(x['quota']) * coef * px.get(c + '-USDT', 0))
    return out


def gate():
    uc = {c['name']: c for c in J('gate/unified_currencies.json')}
    pairs = {p['currency_pair'][:-5] for p in J('gate/uni_currency_pairs.json')
             if p['currency_pair'].endswith('_USDT') and p['status'] == 'enabled'}
    out = {}
    for c, u in uc.items():
        if u.get('loan_status') != 'enable' or c not in pairs:
            continue
        r = np.nan
        p = f'{D}/gate/hlr/{c}.json'
        if os.path.exists(p):
            rs = [float(x['rate']) for x in J(f'gate/hlr/{c}.json').get('rates', []) if x.get('rate')]
            if rs:
                r = rs[0] * 8760  # most recent hour first
        out[c] = dict(rate_yr=r, cap_usdt=float(u['user_max_borrow_amount'] or 0))
    return out


def kucoin():
    iso = {s['baseCurrency'] for s in J('kucoin/isolated_symbols.json')['data']
           if s['quoteCurrency'] == 'USDT' and s['baseBorrowEnable'] and s['tradeEnable']}
    cross = set(J('kucoin/margin_config.json')['data']['currencyList'])
    return {c: dict(rate_yr=np.nan, cap_usdt=np.nan, mode=('cross+iso' if c in cross and c in iso else
                                                         'cross' if c in cross else 'iso'))
            for c in iso | cross}


def binance():
    s = J('binance/exchangeinfo_margin.json')['symbols']
    return {x['baseAsset']: dict(rate_yr=np.nan, cap_usdt=np.nan) for x in s
            if x['quoteAsset'] == 'USDT' and x['status'] == 'TRADING' and x.get('isMarginTradingAllowed')}


def names(venue_coins, c):
    """Match B's spot base name to a venue coin (venue may list 1000-unit or renamed tickers)."""
    for k in (c, '1000' + c, c + '1000'):
        if k in venue_coins:
            return k
    return None


def summarize(tab, lst):
    hit = [(c, tab[names(tab, c)]) for c in lst if names(tab, c)]
    rates = np.array([v['rate_yr'] for _, v in hit], float)
    caps = np.array([v['cap_usdt'] for _, v in hit], float)
    fr = rates[np.isfinite(rates)]
    fc = caps[np.isfinite(caps)]
    return dict(n=len(lst), covered=len(hit), share=len(hit) / len(lst),
                rate_med=float(np.median(fr)) if len(fr) else None,
                rate_p90=float(np.percentile(fr, 90)) if len(fr) else None,
                rate_le40=float(np.mean(fr <= 0.40)) if len(fr) else None,
                n_rate=int(len(fr)),
                cap_med=float(np.median(fc)) if len(fc) else None,
                cap_ge1k=float(np.mean(fc >= 1000)) if len(fc) else None,
                cap_ge10k=float(np.mean(fc >= 10000)) if len(fc) else None,
                missing=[c for c in lst if not names(tab, c)])


if __name__ == '__main__':
    V = dict(bybit=bybit(), okx=okx(), gate=gate(), kucoin=kucoin(), binance_flag=binance())
    sets = dict(current=coins.current_universe(), val_event=coins.val_event_coins(), all=coins.all_names())
    res = {}
    for v, tab in V.items():
        res[v] = {s: summarize(tab, lst) for s, lst in sets.items()}
        res[v]['per_coin_current'] = {c: tab[names(tab, c)] for c in sets['current'] if names(tab, c)}
    union = {c for c in sets['current'] if any(names(V[v], c) for v in ('bybit', 'okx', 'gate', 'kucoin'))}
    res['union_lenders_current'] = dict(covered=len(union), missing=[c for c in sets['current'] if c not in union])
    json.dump(res, open(f'{OUT}/coverage.json', 'w'), indent=1, default=float)
    for v in V:
        for s in sets:
            r = res[v][s]
            f = lambda x, m=1, d=1: 'na' if x is None else f'{x * m:.{d}f}'  # noqa: E731
            print(f"{v:12s} {s:9s} {r['covered']:3d}/{r['n']:3d} ({100 * r['share']:.0f}%)  rate med {f(r['rate_med'], 100)} %/yr"
                  f" p90 {f(r['rate_p90'], 100)}  <=40% {f(r['rate_le40'], 100, 0)}% (n {r['n_rate']})  cap med {f(r['cap_med'], 1, 0)}"
                  f" >=1k {f(r['cap_ge1k'], 100, 0)}% >=10k {f(r['cap_ge10k'], 100, 0)}%")
        print('   missing current:', res[v]['current']['missing'])
    print('union of lenders, current:', res['union_lenders_current'])
