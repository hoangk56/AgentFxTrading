"""Stream X grid run (declared in ../HYPOTHESES_X.md).
usage: python run.py h1 <split>    -> 1h pricing of the 6 cheap cells + 6 mirror cells, trades for the 1m pull
       python run.py m1 <split>    -> 1m pricing (entry T + 1 min primary), all bars, random, overlap with B
Outputs in ../out/."""
import csv
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xv  # noqa: E402
import basis  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out')
M1 = os.path.join(xv.XD, 'm1')
CELLS = [(k, Hh) for k in (30, 60, 100) for Hh in (6, 24)]
CRASH = [('2020-03-01', '2020-04-01'), ('2021-05-17', '2021-05-25'), ('2022-05-07', '2022-05-21'),
         ('2022-11-06', '2022-11-21')]
MIN = 60000
HOLD_YEARS = 1.83


def nm(k, Hh, sign):
    return f'k{k}_H{Hh}_{"cheap" if sign > 0 else "rich"}'


def crash_mask(t):
    m = np.zeros(len(t), bool)
    for a, b in CRASH:
        a = np.datetime64(a, 'ms').astype(np.int64)
        b = np.datetime64(b, 'ms').astype(np.int64)
        m |= (t >= a) & (t < b)
    return m


def load():
    t0 = time.time()
    coins = xv.attach_venues(basis.load())
    print('coins', len(coins), 'load s', round(time.time() - t0), flush=True)
    return coins


def b_rich_overlap(coins, T, k):
    """True if B's perp-spot deviation (b - trailing 168 h median) > k at the signal hour h, h-1 or h+1."""
    out = np.zeros(len(T['e']), bool)
    kk = k / 1e4
    for i, (ci, h) in enumerate(zip(T['ci'], T['h'])):
        c = coins[ci]
        d = c['b'][max(h - 1, 0):h + 2] - c['m'][max(h - 1, 0):h + 2]
        out[i] = bool(np.nanmax(d) > kk) if np.isfinite(d).any() else False
    return out


def venue_move(coins, T):
    """Binance spot log move vs the venue median log move from the signal close h to the close x-1 (bp)."""
    bs, vm = np.full(len(T['e']), np.nan), np.full(len(T['e']), np.nan)
    for i, (ci, h, x) in enumerate(zip(T['ci'], T['h'], T['x'])):
        c = coins[ci]
        lS = np.log(c['Sc'])
        y = x - 1
        if y <= h:
            continue
        lv0 = c['R'][:, h] + lS[h]
        lv1 = c['R'][:, y] + lS[y]
        d = lv1 - lv0
        if np.isfinite(d).any() and np.isfinite(lS[y] - lS[h]):
            vm[i] = np.nanmedian(d) * 1e4
            bs[i] = (lS[y] - lS[h]) * 1e4
    return bs, vm


def stage_h1(split):
    coins = load()
    res, rows = {}, []
    rng = np.random.default_rng(64)
    for sign in (+1, -1):
        for k, Hh in CELLS:
            name = nm(k, Hh, sign)
            T = xv.price_1h(coins, xv.simulate(coins, k, Hh, sign), sign)
            T15 = xv.price_1h(coins, xv.simulate(coins, k, Hh, sign), sign, cost_mult=1.5)
            TL = xv.price_1h(coins, xv.simulate(coins, k, Hh, sign, lag=1), sign)
            T['ovB'] = b_rich_overlap(coins, T, k) if sign > 0 else np.zeros(len(T['e']), bool)
            T['bs'], T['vm'] = venue_move(coins, T)
            r = {}
            for era in ('IS', 'VAL'):
                m = xv.era_mask(T['t'], split, era)
                r[era] = xv.stats(T['net'][m], T['t'][m])
                if r[era]['n'] < 2:
                    continue
                m15 = xv.era_mask(T15['t'], split, era)
                mL = xv.era_mask(TL['t'], split, era)
                r[era].update(x15=xv.stats(T15['net'][m15], T15['t'][m15]).get('net'),
                              late1h=xv.stats(TL['net'][mL], TL['t'][mL]),
                              gross=float(T['price'][m].mean() * 1e4), fund=float(T['fund'][m].mean() * 1e4),
                              cost=float(T['cost'][m].mean() * 1e4), carry=float(T['carry'][m].mean() * 1e4),
                              spot=float(T['spot'][m].mean() * 1e4), perp=float(T['perp'][m].mean() * 1e4),
                              hold=float((T['x'][m] - T['e'][m]).mean()), g=float(np.mean(T['g'][m]) * 1e4),
                              bin_move=float(np.nanmean(T['bs'][m])), venue_move=float(np.nanmean(T['vm'][m])),
                              ovB=float(T['ovB'][m].mean()),
                              exB=xv.stats(T['net'][m & ~T['ovB']], T['t'][m & ~T['ovB']]),
                              excrash=xv.stats(T['net'][m & ~crash_mask(T['t'])], T['t'][m & ~crash_mask(T['t'])]))
                if sign > 0:
                    means, ts = xv.random_null(coins, T, sign, split, era, 1000, rng)
                    r[era]['rand_mean'] = float(np.nanmean(means) * 1e4)
                    r[era]['beats_random'] = float(np.nanmean(means < T['net'][m].mean()))
                    r[era]['rand_t'] = ts.tolist()
            yr = xv.year_of(T['t'])
            r['years'] = {int(y): (int((yr == y).sum()), float(T['net'][yr == y].mean() * 1e4)) for y in np.unique(yr)}
            res[name] = r
            np.savez(os.path.join(OUT, f'trades_{split}_{name}.npz'), **T)
            print(name, json.dumps({e: {kk: (round(v, 2) if isinstance(v, float) else v)
                                        for kk, v in r[e].items() if kk in ('n', 'days', 'net', 'med', 't', 'win', 'x15')}
                                    for e in ('IS', 'VAL')}), flush=True)
            if sign > 0:
                for i in range(len(T['e'])):
                    c = coins[T['ci'][i]]
                    rows.append((name, c['perp'], c['spot'], int(c['hours'][T['e'][i]]), int(c['hours'][T['x'][i]])))
    # max-over-6-cells null of t (cheap side), matched replications
    for era in ('IS', 'VAL'):
        mx = np.nanmax(np.array([res[nm(k, Hh, 1)][era].get('rand_t', [np.nan] * 1000) for k, Hh in CELLS]), axis=0)
        res[f'maxnull_{era}'] = dict(p95=float(np.nanpercentile(mx, 95)), p90=float(np.nanpercentile(mx, 90)))
    for v in res.values():
        for era in ('IS', 'VAL'):
            if isinstance(v, dict) and era in v:
                v[era].pop('rand_t', None)
    json.dump(res, open(os.path.join(OUT, f'h1_{split}.json'), 'w'), indent=1)
    # trades for the 1m pull: all k60 / k100 trades, seed-0 subsample <= 1500 per era for k30 cells
    rng0 = np.random.default_rng(0)
    pick = []
    for name in sorted({r[0] for r in rows}):
        rr = [r for r in rows if r[0] == name]
        if name.startswith('k30'):
            for era in ('IS', 'VAL'):
                a, b = xv.SPLITS[split][era]
                e_ = [r for r in rr if a <= r[3] < b]
                if len(e_) > 1500:
                    e_ = [e_[i] for i in sorted(rng0.choice(len(e_), 1500, replace=False))]
                pick += e_
        else:
            pick += rr
    uniq = sorted({(r[1], r[2], r[3], r[4]) for r in pick})
    with open(os.path.join(OUT, f'trades_1m_{split}.csv'), 'w') as f:
        w = csv.writer(f)
        w.writerow(['perp', 'spot', 'T', 'X'])
        w.writerows(uniq)
    with open(os.path.join(OUT, f'trades_1m_{split}_cells.csv'), 'w') as f:
        w = csv.writer(f)
        w.writerow(['cell', 'perp', 'spot', 'T', 'X'])
        w.writerows(pick)
    print('1m trade windows', len(uniq), flush=True)


_cache = {}


def m1_open(kind, sym, t0, at):
    """Open of the first 1m bar starting at or after `at` within 5 min, from the window file starting t0 - 3 min."""
    key = (kind, sym, t0)
    if key not in _cache:
        p = os.path.join(M1, kind, f'{sym}_{t0 - 3 * MIN}.csv')
        if not os.path.exists(p):
            _cache[key] = None
        else:
            with open(p) as f:
                r = csv.reader(f)
                next(r)
                a = np.array([[float(x[0]), float(x[1])] for x in r if x], dtype=float)
            _cache[key] = a if len(a) else None
    a = _cache[key]
    if a is None:
        return np.nan
    i = np.searchsorted(a[:, 0], at)
    if i < len(a) and a[i, 0] < at + 5 * MIN:
        return a[i, 1]
    return np.nan


def stage_m1(split):
    coins = load()
    picked = {}
    for r in csv.DictReader(open(os.path.join(OUT, f'trades_1m_{split}_cells.csv'))):
        picked.setdefault(r['cell'], set()).add((r['perp'], int(r['T'])))
    res = {}
    h1 = json.load(open(os.path.join(OUT, f'h1_{split}.json')))
    for k, Hh in CELLS:
        name = nm(k, Hh, 1)
        T = dict(np.load(os.path.join(OUT, f'trades_{split}_{name}.npz')))
        keep = np.array([(coins[ci]['perp'], int(coins[ci]['hours'][e])) in picked.get(name, ())
                         for ci, e in zip(T['ci'], T['e'])], bool)
        r = {'priced_share': float(keep.mean()) if len(keep) else 0.0}
        nets = {}
        for L in (1, 2, 5, 15):
            pr = np.full(len(T['e']), np.nan)
            sl, pl = np.full(len(T['e']), np.nan), np.full(len(T['e']), np.nan)
            for i in np.where(keep)[0]:
                c = coins[T['ci'][i]]
                Te, Tx = int(c['hours'][T['e'][i]]), int(c['hours'][T['x'][i]])
                fac = c['fac']
                se = m1_open('spot', c['spot'], Te, Te + L * MIN)
                fe = m1_open('perp', c['perp'], Te, Te + L * MIN)
                sx = m1_open('spot', c['spot'], Tx, Tx + MIN)
                fx = m1_open('perp', c['perp'], Tx, Tx + MIN)
                if np.isfinite([se, fe, sx, fx]).all() and min(se, fe, sx, fx) > 0:
                    sl[i] = sx / se - 1
                    pl[i] = -(fx / fe - 1)
                    pr[i] = sl[i] + pl[i]
                del fac
            for cm in (1.0, 1.5):
                net = pr + T['fund'] - cm * T['cost'] - T['carry']
                nets[(L, cm)] = net
            if L == 1:
                T['spot1m'], T['perp1m'] = sl, pl
        T['net1m'] = nets[(1, 1.0)]
        for era in ('IS', 'VAL'):
            m = xv.era_mask(T['t'], split, era) & np.isfinite(T['net1m'])
            if m.sum() < 2:
                r[era] = dict(n=int(m.sum()))
                continue
            st = xv.stats(T['net1m'][m], T['t'][m])
            st['x15'] = xv.stats(nets[(1, 1.5)][m], T['t'][m])
            for L in (2, 5, 15):
                mm = xv.era_mask(T['t'], split, era) & np.isfinite(nets[(L, 1.0)])
                st[f'late{L}'] = xv.stats(nets[(L, 1.0)][mm], T['t'][mm])
            st['h1_same'] = xv.stats(T['net'][m], T['t'][m])
            st['spot'] = float(np.nanmean(T['spot1m'][m]) * 1e4)
            st['perp'] = float(np.nanmean(T['perp1m'][m]) * 1e4)
            st['fund'] = float(T['fund'][m].mean() * 1e4)
            st['cost'] = float(T['cost'][m].mean() * 1e4)
            st['carry'] = float(T['carry'][m].mean() * 1e4)
            ov = T['ovB'][m].astype(bool)
            st['ovB'] = float(ov.mean())
            st['exB'] = xv.stats(T['net1m'][m][~ov], T['t'][m][~ov])
            cr = crash_mask(T['t'][m])
            st['excrash'] = xv.stats(T['net1m'][m][~cr], T['t'][m][~cr])
            yr = xv.year_of(T['t'][m])
            st['years'] = {int(y): (int((yr == y).sum()), float(T['net1m'][m][yr == y].mean() * 1e4))
                           for y in np.unique(yr)}
            st['beats_random_h1'] = h1[name][era].get('beats_random')
            st['rand_mean_h1'] = h1[name][era].get('rand_mean')
            r[era] = st
        if r['VAL'].get('n', 0) > 2:
            a, b = xv.SPLITS[split]['VAL']
            per_year = r['VAL']['n'] / ((b - a) / (365.25 * 86400000)) / max(r['priced_share'], 1e-9)
            r['power_val'] = float(r['VAL']['sr'] * np.sqrt(HOLD_YEARS * per_year))
            r['val_trades_per_year'] = float(per_year)
        res[name] = r
        np.savez(os.path.join(OUT, f'trades1m_{split}_{name}.npz'), **T)
        print(name, 'priced', round(r['priced_share'], 3),
              {e: {kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in r[e].items()
                   if kk in ('n', 'days', 'net', 'med', 't', 'win')} for e in ('IS', 'VAL')},
              'power', round(r.get('power_val', float('nan')), 2), flush=True)
    json.dump(res, open(os.path.join(OUT, f'm1_{split}.json'), 'w'), indent=1)


if __name__ == '__main__':
    {'h1': stage_h1, 'm1': stage_m1}[sys.argv[1]](sys.argv[2])
