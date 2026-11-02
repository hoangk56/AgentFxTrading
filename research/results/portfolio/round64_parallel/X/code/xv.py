"""Stream X: cross-venue spot wedge (rule declared in ../HYPOTHESES_X.md).
Binance legs from B's loader (round63_parallel/B/code/basis.py, imported read-only); other venues' spot 1h from
research/data/xvenue_spot/<venue>/<BASE>.csv. Everything cut at ts < 2025-01-01 at load."""
import csv
import os
import sys

import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
from numpy.lib.stride_tricks import sliding_window_view

BCODE = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round63_parallel/B/code'
sys.path.insert(0, BCODE)
import basis  # noqa: E402
from basis import H, CUT, cl_t, trade_net  # noqa: E402,F401

XD = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/xvenue_spot'
VENUES = ('okx', 'kucoin', 'bybit', 'coinbase')
DAY = 86400000
WIN, WIN_MIN = 168, 120
MAX_ABS = 0.10
SPLITS = {'main': {'IS': (1577836800000, 1640995200000), 'VAL': (1640995200000, CUT)},
          'alt': {'IS': (1577836800000, 1672531200000), 'VAL': (1672531200000, CUT)}}


def _venue_csv(venue, base):
    p = os.path.join(XD, venue, base + '.csv')
    if not os.path.exists(p):
        return None
    with open(p) as f:
        r = csv.reader(f)
        next(r)
        a = np.array([x for x in r if x], dtype=float)
    if not len(a):
        return None
    return a[a[:, 0] < CUT]


def _usdt_usd():
    a = _venue_csv('coinbase', 'USDT')
    return {} if a is None else dict(zip((a[:, 0] // H).astype(int), a[:, 4]))


def trailing_median(x):
    n = len(x)
    med = np.full(n, np.nan)
    if n > WIN:
        W = sliding_window_view(x[:-1], WIN)
        cnt = (~np.isnan(W)).sum(1)
        with np.errstate(all='ignore'):
            mm = np.nanmedian(W, axis=1)
        mm[cnt < WIN_MIN] = np.nan
        med[WIN:] = mm
    return med


def year_of(ms):
    return np.asarray(ms, dtype='datetime64[ms]').astype('datetime64[Y]').astype(int) + 1970


def attach_venues(coins, verbose=False):
    """Adds c['R'] (venue x hour log ratio ln(venue/Binance), valid only), c['M'] (trailing medians), c['G'] (signal),
    c['nv'] (usable venues) and c['vinfo']."""
    usd = _usdt_usd()
    for c in coins:
        base = c['spot'][:-4]
        n, j0 = c['n'], c['j0']
        S = c['Sc']
        sval = (c['tickS'] <= basis.MAX_TICK) & (c['Sn'] >= basis.MIN_TRADES) & (c['Sc'] > 0)
        Rs, Ms, info = [], [], {}
        lS = np.log(np.where(sval, S, np.nan))
        for v in VENUES:
            A = _venue_csv(v, base)
            if A is None or len(A) < 500:
                continue
            jj = (A[:, 0] // H).astype(int) - j0
            k = (jj >= 0) & (jj < n)
            A, jj = A[k], jj[k]
            P = np.full(n, np.nan)
            ok = (A[:, 4] > 0) & (A[:, 5] > 0)
            px = A[:, 4].copy()
            if v == 'coinbase':
                conv = np.array([usd.get(int(j + j0), 1.0) for j in jj])
                px = px / np.where(conv > 0, conv, 1.0)
            P[jj[ok]] = px[ok]
            both = ~np.isnan(P) & sval
            if both.sum() < 500:
                continue
            scale = 10.0 ** np.round(np.log10(np.median(P[both] / S[both])))
            r = np.log(P / scale) - lS
            r[np.abs(r) > MAX_ABS] = np.nan
            # ticker-reuse guard: hourly return correlation with Binance spot per calendar year >= 0.5, >= 500 hours
            lv = np.log(P / scale)
            dv, ds = np.diff(lv), np.diff(lS)
            yrs = year_of(c['hours'][1:])
            keep = np.zeros(n, bool)
            ystat = {}
            for y in np.unique(yrs):
                w = (yrs == y) & ~np.isnan(dv) & ~np.isnan(ds)
                if w.sum() >= 500:
                    cc = np.corrcoef(dv[w], ds[w])[0, 1]
                    ystat[int(y)] = (int(w.sum()), round(float(cc), 3))
                    if cc >= 0.5:
                        keep[1:][yrs == y] = True
                else:
                    ystat[int(y)] = (int(w.sum()), None)
            r[~keep] = np.nan
            if np.isfinite(r).sum() < 500:
                continue
            Rs.append(r)
            Ms.append(trailing_median(r))
            info[v] = dict(scale=scale, years=ystat, valid=int(np.isfinite(r).sum()))
        c['vinfo'] = info
        c['venues'] = list(info)
        if Rs:
            R, M = np.array(Rs), np.array(Ms)
            Dv = R - M
            nv = (~np.isnan(Dv)).sum(0)
            with np.errstate(all='ignore'):
                Dm = np.nanmedian(Dv, axis=0)
            G = np.where(nv >= 2, -Dm, np.nan)
        else:
            R = M = np.zeros((0, n))
            nv = np.zeros(n, int)
            G = np.full(n, np.nan)
        c['R'], c['M'], c['nv'], c['G'] = R, M, nv, G
        if verbose:
            print(base, info.keys(), int((nv >= 2).sum()), flush=True)
    return coins


def simulate(coins, k, Hh, sign, lag=0):
    """sign +1: cheap Binance spot (G < -k) -> long spot / short perp (B side +1).
    sign -1 (mirror, info): rich Binance spot (G > k) -> short spot / long perp (B side -1, borrow 40 %/yr).
    Exit: first close c in [e, e+H) with sign * G_c >= sign * G_h / 2 using entry-hour references, at open c+1."""
    out = {f: [] for f in ('ci', 'h', 'e', 'x', 'forced', 't', 'g')}
    kk = k / 1e4
    for ci, c in enumerate(coins):
        G, n = c['G'], c['n']
        with np.errstate(invalid='ignore'):
            ev = np.where(c['inU'] & ~np.isnan(G) & (-sign * G > kk))[0]
        busy = -1
        for h in ev:
            e = h + 1 + lag
            if e <= busy or e >= n or np.isnan(c['Fo'][e]) or np.isnan(c['So'][e]):
                continue
            tgt = G[h] / 2
            x = None
            last = min(e + Hh, n - 1)
            Mh = c['M'][:, h]
            for cc in range(e, last):
                dv = c['R'][:, cc] - Mh
                if np.isnan(dv).all():
                    continue
                gc = -np.nanmedian(dv)
                if sign * gc >= sign * tgt:
                    x = cc + 1
                    break
            if x is None:
                x = e + Hh
            forced = 0
            if x >= n or np.isnan(c['Fo'][min(x, n - 1)]) or np.isnan(c['So'][min(x, n - 1)]):
                y = x
                while y < min(n, x + 24) and (np.isnan(c['Fo'][y]) or np.isnan(c['So'][y])):
                    y += 1
                if y < n and y < x + 24:
                    x = y
                else:
                    ok = np.where(~np.isnan(c['Fo'][e + 1:min(x, n)]) & ~np.isnan(c['So'][e + 1:min(x, n)]))[0]
                    if not len(ok):
                        continue
                    x = e + 1 + ok[-1]
                    forced = 1
            busy = x - 1
            for f, v in (('ci', ci), ('h', h), ('e', e), ('x', x), ('forced', forced), ('t', c['hours'][e]),
                         ('g', G[h])):
                out[f].append(v)
    return {f: np.array(v) for f, v in out.items()}


def price_1h(coins, T, sign, cost_mult=1.0):
    """1h-open pricing with B's trade_net (B side = sign)."""
    n = len(T['e'])
    for f in ('price', 'fund', 'cost', 'carry', 'net', 'spot', 'perp'):
        T[f] = np.zeros(n)
    for ci in np.unique(T['ci']) if n else []:
        w = np.where(T['ci'] == ci)[0]
        c = coins[ci]
        e, x = T['e'][w], T['x'][w]
        p, f, co, ca = trade_net(c, e, x, sign, c['rank'][T['h'][w]], cost_mult)
        T['price'][w], T['fund'][w], T['cost'][w], T['carry'][w] = p, f, co, ca
        T['spot'][w] = sign * (c['So'][x] / c['So'][e] - 1)
        T['perp'][w] = -sign * (c['Fo'][x] / c['Fo'][e] - 1)
    T['net'] = T['price'] + T['fund'] - T['cost'] - T['carry']
    return T


def era_mask(t, split, era):
    a, b = SPLITS[split][era]
    return (t >= a) & (t < b)


def stats(x, t):
    x = np.asarray(x)
    if len(x) < 2:
        return dict(n=int(len(x)))
    day = t // DAY
    u, inv = np.unique(day, return_inverse=True)
    dsum = np.bincount(inv, weights=x)
    return dict(n=int(len(x)), days=int(len(u)), net=float(x.mean() * 1e4), med=float(np.median(x) * 1e4),
                t=float(cl_t(x, day)), win=float((x > 0).mean()), sr=float(x.mean() / x.std(ddof=1)),
                sr_day=float(dsum.mean() / dsum.std(ddof=1)) if len(dsum) > 1 else float('nan'))


def random_null(coins, T, sign, split, era, reps, rng, net_key='net'):
    """B's matched random entries (same coin, era, hold length, side), priced at 1h opens. Returns (means, ts)."""
    a, b = SPLITS[split][era]
    m = (T['t'] >= a) & (T['t'] < b)
    ci, L = T['ci'][m], (T['x'] - T['e'])[m]
    means, ts = np.full(reps, np.nan), np.full(reps, np.nan)
    if m.sum() < 3:
        return means, ts
    nets = np.full((reps, len(ci)), np.nan)
    days = np.zeros((reps, len(ci)), np.int64)
    for c_ in np.unique(ci):
        c = coins[c_]
        ok = c['inU'] & ~np.isnan(c['Fo']) & ~np.isnan(c['So']) & (c['hours'] >= a) & (c['hours'] < b)
        pool = np.where(ok)[0]
        pool = pool[pool < c['n'] - 2]
        w = np.where(ci == c_)[0]
        if not len(pool):
            continue
        e = pool[rng.integers(0, len(pool), size=(reps, len(w)))]
        x = np.minimum(e + L[w][None, :], c['n'] - 1)
        p, f, co, ca = trade_net(c, e.ravel(), x.ravel(), sign, c['rank'][e.ravel()])
        v = (p + f - co - ca).reshape(e.shape)
        nets[:, w] = v
        days[:, w] = c['hours'][e] // DAY
    for r in range(reps):
        ok = ~np.isnan(nets[r])
        means[r] = nets[r, ok].mean()
        ts[r] = cl_t(nets[r, ok], days[r, ok])
    return means, ts
