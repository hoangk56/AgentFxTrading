"""Loader for the Cboe VX daily files + ProShares AUM. HOLD hygiene: every row with date >= 2025-01-01 is dropped
at parse, before anything else touches it.

Panel (numpy, one row per trading day):
  dates (datetime64[D]), and for the ETP pair (M1 = earliest expiry > t, M2 = next) and M3:
  S1 S2 S3 (settle), O1 O2 (open, NaN if 0), OI1 OI2, E1 E2 (expiry), next-day opens are read by index.
  Roll period of a pair (E_a, E_b): trading days t with E_prev <= t < E_a; N = its length, k = 1..N its day number.
"""
import csv
import datetime as dt
import os

import numpy as np

ROOT = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/cboe_vx'
CUT = dt.date(2025, 1, 1)


def _f(x):
    try:
        v = float(x)
    except Exception:
        return np.nan
    return v if v > 0 else np.nan


def load_raw():
    """{expiry(date): {date: (open, settle, close, oi, vol)}}"""
    out = {}
    raw = os.path.join(ROOT, 'raw')
    for fn in sorted(os.listdir(raw)):
        if not (fn.startswith('VX_') and fn.endswith('.csv')):
            continue
        exp = dt.date.fromisoformat(fn[3:13])
        rows = {}
        with open(os.path.join(raw, fn), newline='') as f:
            for r in csv.DictReader(f):
                try:
                    d = dt.date.fromisoformat(r['Trade Date'].strip())
                except Exception:
                    continue
                if d >= CUT:
                    continue  # HOLD never loaded
                s = _f(r.get('Settle'))
                if np.isnan(s):
                    # files before 2013-05-17 carry Settle = 0: fall back to the last trade (Close); PRE era only
                    s = _f(r.get('Close'))
                if np.isnan(s):
                    continue
                rows[d] = (_f(r.get('Open')), s, _f(r.get('Close')), _f(r.get('Open Interest')) if r.get('Open Interest') else np.nan,
                           _f(r.get('Total Volume')))
        out[exp] = rows
    return out


def load_proshares():
    """{ticker: (dates datetime64[D], aum float)}"""
    out = {}
    for t in ('UVXY', 'SVXY', 'VIXY'):
        d, a = [], []
        with open(os.path.join(ROOT, 'proshares', t + '.csv')) as f:
            next(f)
            for line in f:
                x = line.strip().split(',')
                dd = dt.date.fromisoformat(x[0])
                if dd >= CUT:
                    continue
                d.append(np.datetime64(dd))
                a.append(float(x[3]))
        out[t] = (np.array(d), np.array(a))
    return out


def lev(ticker, d):
    """Daily leverage of the ProShares VIX funds (change effective 2018-02-28)."""
    post = d >= np.datetime64('2018-02-28')
    if ticker == 'UVXY':
        return np.where(post, 1.5, 2.0)
    if ticker == 'SVXY':
        return np.where(post, -0.5, -1.0)
    return np.ones(len(d))


def build_panel(first=dt.date(2013, 1, 1)):
    raw = load_raw()
    exps = sorted(raw)
    # trading days = days on which the nearest unexpired contract has a settle
    alld = sorted({d for e in exps for d in raw[e]})
    alld = [d for d in alld if d >= first - dt.timedelta(days=40)]
    rec = []
    for d in alld:
        fut = [e for e in exps if e > d]
        if len(fut) < 3:
            continue
        e1, e2, e3 = fut[:3]
        r1, r2, r3 = raw[e1].get(d), raw[e2].get(d), raw[e3].get(d)
        if r1 is None or r2 is None or r3 is None:
            continue
        prev = [e for e in exps if e <= d]
        eprev = prev[-1] if prev else None
        rec.append((d, e1, e2, e3, eprev, r1, r2, r3))
    n = len(rec)
    P = {
        'dates': np.array([np.datetime64(r[0]) for r in rec]),
        'E1': np.array([np.datetime64(r[1]) for r in rec]),
        'E2': np.array([np.datetime64(r[2]) for r in rec]),
        'E3': np.array([np.datetime64(r[3]) for r in rec]),
    }
    for j, k in ((5, '1'), (6, '2'), (7, '3')):
        P['O' + k] = np.array([r[j][0] for r in rec])
        P['S' + k] = np.array([r[j][1] for r in rec])
        P['OI' + k] = np.array([r[j][3] for r in rec])
        P['V' + k] = np.array([r[j][4] for r in rec])
    # the same contracts' next-day settle / open (contract identity kept across the roll)
    for k, ek in (('1', 1), ('2', 2), ('3', 3)):
        nO, nS = np.full(n, np.nan), np.full(n, np.nan)
        for i in range(n - 1):
            e = rec[i][ek]
            nxt = raw[e].get(rec[i + 1][0])
            if nxt is not None:
                nO[i], nS[i] = nxt[0], nxt[1]
        P['nO' + k], P['nS' + k] = nO, nS
    # roll period day number k and length N
    E1 = P['E1']
    N = np.zeros(n, int)
    K = np.zeros(n, int)
    for e in np.unique(E1):
        idx = np.flatnonzero(E1 == e)
        N[idx] = len(idx)
        K[idx] = np.arange(1, len(idx) + 1)
    P['N'], P['K'] = N, K
    # index weights at the close of t: w1 = 1 - K/N
    P['w1'] = 1.0 - K / N
    keep = P['dates'] >= np.datetime64(first)
    # first period may be truncated by `first`; N/K were computed before the cut on purpose
    return {k: v[keep] for k, v in P.items()}, raw


def era(dates):
    y = dates.astype('datetime64[Y]').astype(int) + 1970
    e = np.full(len(dates), '', dtype=object)
    e[(y >= 2013) & (y <= 2015)] = 'PRE'
    e[(y >= 2016) & (y <= 2021)] = 'IS'
    e[(y >= 2022) & (y <= 2024)] = 'VAL'
    return e, y


def nw_t(x, lags=None):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 3:
        return np.nan
    if lags is None:
        lags = int(np.floor(4 * (n / 100) ** (2 / 9)))
    u = x - x.mean()
    g0 = (u @ u) / n
    s = g0
    for L in range(1, lags + 1):
        g = (u[L:] @ u[:-L]) / n
        s += 2 * (1 - L / (lags + 1)) * g
    return x.mean() / np.sqrt(s / n) if s > 0 else np.nan


def tstat(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 3 or x.std(ddof=1) == 0:
        return np.nan
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
