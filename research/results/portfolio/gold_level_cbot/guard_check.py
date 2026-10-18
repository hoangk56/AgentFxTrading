"""How far would a broker guard stop have to sit so the G1-XAU50 trades almost never touch it? (Not part of the rule:
a far stop for a bot or VPS that dies with a position open.) For every IS / VAL / HOLD trade of the registered runs:
entry = the 250 ms model fill (first tick >= trigger + 250 ms; ask for a buy, bid for a sell), then the worst exit-side
quote (bid for a long, ask for a short) until the 30-minute exit, in $ and in % of the entry. Then, per guard distance
G in $, the share of trades touched and the net per trade if a touched trade had been closed at the guard (exit at the
guard price, no slippage) instead of at 30 minutes.
usage (repo root): research/.venv/bin/python guard_check.py TRADES.csv [...]   (the IS, VAL and HOLD runs' trade files;
the HOLD one is prereg_code/trades_HOLD.csv)"""
import csv
import gzip
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

DATA = Path('research/data/XAUUSD/t1')   # run from the repo root
COMM = 0.6
cache = {}


def day(d):
    if d in cache:
        return cache[d]
    p = DATA / f'{d:%Y%m%d}.zticks'
    raw = np.frombuffer(gzip.decompress(p.read_bytes()), dtype='<i8').reshape(-1, 3) if p.exists() else np.zeros((0, 3), np.int64)
    cache[d] = raw
    return raw


def window(t0, t1):
    """ticks with t0 <= ts <= t1 (ms), sides forward-filled within the loaded days (one day of look-back)."""
    d0 = datetime.fromtimestamp(t0 / 1000, timezone.utc).date() - timedelta(days=1)
    d1 = datetime.fromtimestamp(t1 / 1000, timezone.utc).date()
    parts = []
    d = d0
    while d <= d1:
        parts.append(day(d))
        d += timedelta(days=1)
    raw = np.concatenate(parts)
    ts, b, a = raw[:, 0].copy(), raw[:, 1].copy(), raw[:, 2].copy()
    for col in (b, a):
        idx = np.where(col != 0, np.arange(col.size), 0)
        np.maximum.accumulate(idx, out=idx)
        col[:] = col[idx]
    k = (b != 0) & (a != 0) & (a >= b)
    ts, b, a = ts[k], b[k] / 1e5, a[k] / 1e5
    i0, i1 = np.searchsorted(ts, t0, 'left'), np.searchsorted(ts, t1, 'right')
    return ts[i0:i1], b[i0:i1], a[i0:i1]


rows = []
for fn in sys.argv[1:]:
    for r in csv.DictReader(open(fn)):
        rows.append(r)
mae, net, era, entry_px = [], [], [], []
for r in rows:
    t = int(r['trigger_ms'])
    side = int(r['side'])
    ts, b, a = window(t + 250, t + 30 * 60000 + 600000)
    if len(ts) == 0:
        continue
    e = a[0] if side > 0 else b[0]
    stop_idx = np.searchsorted(ts, t + 30 * 60000, 'left')
    path = b[:stop_idx + 1] if side > 0 else a[:stop_idx + 1]
    worst = (e - path.min()) if side > 0 else (path.max() - e)
    mae.append(max(worst, 0.0))
    net.append(float(r['net_250']))
    era.append(r['era'])
    entry_px.append(e)
mae, net, era, entry_px = map(np.array, (mae, net, era, entry_px))
print(f'trades {len(mae)} (by era: ' + ', '.join(f'{e} {int((era == e).sum())}' for e in ('IS', 'VAL', 'HOLD')) + ')')
for e in ('IS', 'VAL', 'HOLD', 'all'):
    m = (era == e) if e != 'all' else np.ones(len(era), bool)
    q = np.quantile(mae[m], [0.5, 0.9, 0.99, 0.999]) if m.sum() else []
    pct = mae[m] / entry_px[m] * 100
    print(f'{e:4s} MAE $ median {q[0]:.2f}  p90 {q[1]:.2f}  p99 {q[2]:.2f}  p99.9 {q[3]:.2f}  max {mae[m].max():.2f}; '
          f'% of price p99 {np.quantile(pct, 0.99):.3f} max {pct.max():.3f}')
print('\nguard $  touched (all / HOLD)  net per trade if touched trades exit at the guard (all / HOLD)  vs no guard')
for G in (10, 15, 20, 25, 30, 40, 50, 75, 100):
    hit = mae >= G
    alt = net.copy()
    # a touched trade exits at the guard: -G in bp of the entry, minus commission
    alt[hit] = -G / entry_px[hit] * 1e4 - COMM
    h = era == 'HOLD'
    print(f'{G:5d}   {hit.sum():4d} ({hit.mean() * 100:.2f} %) / {hit[h].sum():3d}      '
          f'{alt.mean():+.3f} / {alt[h].mean():+.3f}   vs {net.mean():+.3f} / {net[h].mean():+.3f}')
