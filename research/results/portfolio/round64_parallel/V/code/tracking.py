"""Venue spot vs Binance spot around B's 333 VAL 2022-24 entries (no B P&L computed). All series cut at ts < 2025.

Per event (signal close h, entry open e, exit open x from BX/out/events.csv lag 0):
- gap_h: ln(V close / B close) at h minus its median over h-24..h-1 (>= 12 bars): + = venue richer than Binance
  at the signal (venue lags Binance too).
- shortfall: (V open x / V open e) - (B open x / B open e) in log bp: + = a short on the venue gains less than a short
  on Binance spot would have (bad for B).
- hourly log-return correlation V vs B over h-24 .. x (pooled), and venue / Binance quote-volume ratio in the window.
"""
import csv
import glob
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coins  # noqa: E402

H = 3600000
CUT = coins.CUT
D = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data'
OUT = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round64_parallel/V/out'


def load_binance(spot):
    p = f'{D}/binance_basis/spot_1h/{spot}.csv'
    if not os.path.exists(p):
        return {}
    out = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            t = int(r['t'])
            if t < CUT:
                out[t] = (float(r['o']), float(r['c']), float(r['qvol']))
    return out


def load_venue(venue, coin):
    out = {}
    for p in glob.glob(f'{D}/margin_venues/{venue}/klines/{coin}_*.json'):
        j = json.load(open(p))
        if venue == 'bybit':
            rows = [(int(r[0]), float(r[1]), float(r[4]), float(r[6])) for r in j['result']['list']]
        elif venue == 'okx':
            rows = [(int(r[0]), float(r[1]), float(r[4]), float(r[7])) for r in j['data']]
        else:  # kucoin: [t s, open, close, high, low, vol, turnover]
            rows = [(int(r[0]) * 1000, float(r[1]), float(r[2]), float(r[6])) for r in j['data']]
        for t, o, c, q in rows:
            if t < CUT and o > 0 and c > 0:
                out[t] = (o, c, q)
    return out


def q(a, p):
    return float(np.percentile(a, p)) if len(a) else float('nan')


def run(venue):
    ev = coins.val_events()
    cacheB, cacheV = {}, {}
    rec = []
    rB, rV = [], []
    for perp, sp, h, e, x in ev:
        c = coins.base_of(sp)
        B = cacheB.setdefault(sp, load_binance(sp))
        V = cacheV.setdefault(c, load_venue(venue, c))
        r = dict(perp=perp, h=h, covered=False)
        if all(t in V and t in B for t in (h, e, x)):
            pre = [math.log(V[t][1] / B[t][1]) for t in range(h - 24 * H, h, H) if t in V and t in B]
            if len(pre) >= 12:
                med = float(np.median(pre))
                r.update(covered=True,
                         gap_h=1e4 * (math.log(V[h][1] / B[h][1]) - med),
                         gap_e=1e4 * (math.log(V[e][0] / B[e][0]) - med),
                         shortfall=1e4 * (math.log(V[x][0] / V[e][0]) - math.log(B[x][0] / B[e][0])),
                         b_ret=1e4 * math.log(B[x][0] / B[e][0]),
                         v_ret=1e4 * math.log(V[x][0] / V[e][0]),
                         volratio=(sum(V[t][2] for t in range(h - 24 * H, h + H, H) if t in V)
                                   / max(1e-9, sum(B[t][2] for t in range(h - 24 * H, h + H, H) if t in B))))
                for t in range(h - 23 * H, x + H, H):
                    if all(u in V and u in B for u in (t, t - H)):
                        rV.append(math.log(V[t][1] / V[t - H][1]))
                        rB.append(math.log(B[t][1] / B[t - H][1]))
        rec.append(r)
    cv = [r for r in rec if r['covered']]
    a = lambda k: np.array([r[k] for r in cv])  # noqa: E731
    s = dict(venue=venue, events=len(rec), covered=len(cv))
    if cv:
        g, ge, sf, br, vr = a('gap_h'), a('gap_e'), a('shortfall'), a('b_ret'), a('v_ret')
        rB_, rV_ = np.array(rB), np.array(rV)
        s.update(corr_hourly=float(np.corrcoef(rB_, rV_)[0, 1]), n_hours=len(rB_),
                 gap_h_med=float(np.median(g)), gap_h_p10=q(g, 10), gap_h_p90=q(g, 90), gap_h_mean=float(g.mean()),
                 gap_e_med=float(np.median(ge)), gap_e_mean=float(ge.mean()),
                 sf_mean=float(sf.mean()), sf_med=float(np.median(sf)), sf_p10=q(sf, 10), sf_p90=q(sf, 90),
                 sf_absmed=float(np.median(np.abs(sf))),
                 sf_mean_trim1=float(np.mean(np.sort(sf)[int(0.01 * len(sf)):len(sf) - int(0.01 * len(sf))])),
                 b_ret_mean=float(br.mean()), v_ret_mean=float(vr.mean()),
                 capture=float(vr.mean() / br.mean()) if br.mean() else float('nan'),
                 volratio_med=float(np.median(a('volratio'))),
                 share_abs_sf_gt50=float(np.mean(np.abs(sf) > 50)),
                 by_year={})
        for y in (2022, 2023, 2024):
            lo = int((np.datetime64(f'{y}-01-01') - np.datetime64('1970-01-01')) / np.timedelta64(1, 'ms'))
            hi = int((np.datetime64(f'{y + 1}-01-01') - np.datetime64('1970-01-01')) / np.timedelta64(1, 'ms'))
            m = np.array([lo <= r['h'] < hi for r in cv])
            n_all = sum(lo <= r['h'] < hi for r in rec)
            if m.any():
                s['by_year'][y] = dict(events=n_all, covered=int(m.sum()), sf_mean=float(sf[m].mean()),
                                       sf_med=float(np.median(sf[m])), gap_h_med=float(np.median(g[m])))
        worst = sorted(cv, key=lambda r: -abs(r['shortfall']))[:5]
        s['largest_abs_shortfall'] = [(r['perp'], str(np.datetime64(r['h'], 'ms'))[:13], round(r['shortfall']),
                                       round(r['gap_h'])) for r in worst]
    s['uncovered_coins'] = sorted({r['perp'] for r in rec if not r['covered']})
    return s


if __name__ == '__main__':
    res = {v: run(v) for v in ('bybit', 'okx', 'kucoin')}
    json.dump(res, open(f'{OUT}/tracking.json', 'w'), indent=1)
    for v, s in res.items():
        print(v, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in s.items() if k not in ('uncovered_coins',)})
        print()
