"""Stream X: VIX-futures ETP roll (A1 / A2) and leveraged-ETP dose fade (B), cells declared in HYPOTHESES_X.md.
Run: research/.venv/bin/python -I run.py  (HOLD rows are dropped inside vxdata.load_raw)."""
import datetime as dt
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vxdata as V  # noqa: E402

RNG = np.random.default_rng(63)
TICK, COMM = 0.05, 0.002          # points; $2 per contract per side = 0.002 pt
SPREAD_RT = 2 * TICK + 4 * COMM   # 0.108
OUT_RT = TICK + 2 * COMM          # 0.054
NDRAW = 1000

P, RAW = V.build_panel()
D = P['dates']
ERA, YR = V.era(D)
n = len(D)


def px(e, d, field):
    """field 0 open, 1 settle of contract expiring e on date d (np.datetime64) or NaN."""
    r = RAW[e.astype(object)].get(d.astype(object))
    return np.nan if r is None else r[field]


def lead(k, field, contract):
    """price of the day-t contract (E1/E2) k trading days later."""
    E = P['E' + contract]
    out = np.full(n, np.nan)
    for i in range(n - k):
        out[i] = px(E[i], D[i + k], field)
    return out


def summ(x, idx, cost, nw=True):
    """per-era rows: n, gross mean, net mean, t, sd, positive years"""
    res = {}
    for e in ('PRE', 'IS', 'VAL'):
        m = idx & (ERA == e) & ~np.isnan(x)
        g = x[m]
        net = g - cost[m] if np.ndim(cost) else g - cost
        t = V.nw_t(net) if nw else V.tstat(net)
        ys = np.unique(YR[m])
        pos = sum(1 for y in ys if net[YR[m] == y].sum() > 0)
        res[e] = dict(n=int(m.sum()), gross=g.mean() if len(g) else np.nan, net=net.mean() if len(net) else np.nan,
                      t=t, sd=net.std(ddof=1) if len(net) > 2 else np.nan, sh=(net.mean() / net.std(ddof=1)) if len(net) > 2 else np.nan,
                      years='%d/%d' % (pos, len(ys)),
                      yearly={int(y): round(float(net[YR[m] == y].sum()), 3) for y in ys})
    return res


def fmt(name, r):
    s = []
    for e in ('PRE', 'IS', 'VAL'):
        x = r[e]
        s.append('%s %s n=%d gross=%+.4f net=%+.4f t=%+.2f sh/trade=%+.3f yrs=%s' % (
            name, e, x['n'], x['gross'], x['net'], x['t'], x['sh'], x['years']))
    return '\n'.join(s)


# ---------------- basic series ----------------
dS1 = P['nS1'] - P['S1']   # same contract t -> t+1
dS2 = P['nS2'] - P['S2']
dS3 = P['nS3'] - P['S3']
last_day = P['K'] == P['N']          # Tuesday before M1 expiry
first_day = P['K'] == 1
isd = ERA == 'IS'
ok = isd & ~np.isnan(dS1) & ~np.isnan(dS2) & ~last_day
h = float(np.cov(dS1[ok], dS2[ok])[0, 1] / np.var(dS2[ok], ddof=1))
ok3 = isd & ~np.isnan(dS2) & ~np.isnan(dS3) & ~last_day
h23 = float(np.cov(dS2[ok3], dS3[ok3])[0, 1] / np.var(dS3[ok3], ddof=1))
print('panel days', n, 'from', D[0], 'to', D[-1], 'max date < 2025:', D[-1] < np.datetime64('2025-01-01'))
print('IS hedge ratio h (dM1 on dM2) = %.3f ; control h23 (dM2 on dM3) = %.3f' % (h, h23))
for e in ('PRE', 'IS', 'VAL'):
    m = (ERA == e) & ~np.isnan(dS1) & ~np.isnan(dS2) & ~last_day
    so = (P['nO1'] - P['S1']) - (P['nO2'] - P['S2'])
    mm = m & ~np.isnan(so)
    print('%s sd dM1 %.3f dM2 %.3f d(M1-M2) %.3f, settle->open d(M1-M2) sd %.3f (n %d, open avail %.2f)' % (
        e, np.std(dS1[m]), np.std(dS2[m]), np.std(dS1[m] - dS2[m]), np.std(so[mm]), m.sum(), mm.sum() / m.sum()))

# ---------------- ProShares exposure / doses ----------------
PS = V.load_proshares()


def asof(tk, shift_days=1):
    """AUM of ticker on the trading day before t (last available date < t)."""
    d, a = PS[tk]
    j = np.searchsorted(d, D, side='left') - 1
    out = np.where(j >= 0, a[np.clip(j, 0, None)], 0.0)
    out[j < 0] = 0.0
    return out


A_U, A_S, A_V = asof('UVXY'), asof('SVXY'), asof('VIXY')
L_U, L_S = V.lev('UVXY', D), V.lev('SVXY', D)
w1 = P['w1']
# weights held over t-1 -> t are those set at the close of t-1; index price at close t
mix = w1 * P['S1'] + (1 - w1) * P['S2']
net_expo = A_U * L_U + A_V + A_S * L_S          # $ of index exposure, ProShares only
contracts = net_expo / (1000 * mix)
roll_dose = contracts / P['N'] / (P['OI1'] + P['OI2'])
# day-t index return: weights at close t-1 on the t-1 pair, same contracts to t
r = np.full(n, np.nan)
w1p = np.r_[np.nan, w1[:-1]]
r[1:] = (w1[:-1] * dS1[:-1] + (1 - w1[:-1]) * dS2[:-1]) / mix[:-1]
gam = A_U * L_U * (L_U - 1) + A_S * L_S * (L_S - 1)
doi = 1000 * (P['S1'] * P['OI1'] + P['S2'] * P['OI2'])
letf_dose = gam * r / doi
for e in ('PRE', 'IS', 'VAL'):
    m = ERA == e
    print('%s ProShares net expo median $%.0fm, ETP contracts/OI(M1+M2) median %.3f, roll dose median %.4f, |LETF dose| p90 %.5f' % (
        e, np.nanmedian(net_expo[m]) / 1e6, np.nanmedian(contracts[m] / (P['OI1'][m] + P['OI2'][m])),
        np.nanmedian(roll_dose[m]), np.nanpercentile(np.abs(letf_dose[m]), 90)))

results = {}
nulls = {}

# ---------------- A1: short M1 / long M2 over the roll period ----------------
groups = [np.flatnonzero(P['E1'] == e) for e in np.unique(P['E1'])]


def a1_windows(hr, late=0, c1='1', c2='2', hctl=None):
    rows = []
    for g in groups:
        if len(g) < 5 or P['K'][g[0]] != 1:
            continue
        i0, i1 = g[0] + late, g[-1]
        f1 = -(P['S' + c1][i1] - P['S' + c1][i0])
        f2 = hr * (P['S' + c2][i1] - P['S' + c2][i0])
        rows.append((i0, f1 + f2, ERA[i0], YR[i0], i1))
    return rows


def a1_eval(hr, name, late=0, c1='1', c2='2', costmul=1.0):
    rows = a1_windows(hr, late, c1, c2)
    x = np.array([r[1] for r in rows])
    idx0 = np.array([r[0] for r in rows])
    cost = costmul * (1 + hr) * (TICK + 2 * COMM)
    out = {}
    for e in ('PRE', 'IS', 'VAL'):
        m = np.array([r[2] == e for r in rows])
        net = x[m] - cost
        ys = np.unique([r[3] for r in np.array(rows, dtype=object)[m]])
        yv = np.array([r[3] for r in rows])[m]
        pos = sum(1 for y in ys if net[yv == y].sum() > 0)
        out[e] = dict(n=int(m.sum()), gross=x[m].mean(), net=net.mean(), t=V.tstat(net),
                      sh=net.mean() / net.std(ddof=1), years='%d/%d' % (pos, len(ys)),
                      yearly={int(y): round(float(net[yv == y].sum()), 2) for y in ys}, maxloss=net.min())
    return out, rows, x, cost


def show_a1(name, out):
    for e in ('PRE', 'IS', 'VAL'):
        x = out[e]
        print('%s %s n=%d gross=%+.3f net=%+.3f pt/window t=%+.2f sh/win=%+.3f yrs=%s worst=%+.2f' % (
            name, e, x['n'], x['gross'], x['net'], x['t'], x['sh'], x['years'], x['maxloss']))
    print('   yearly net (pts):', {**out['PRE']['yearly'], **out['IS']['yearly'], **out['VAL']['yearly']})


print('\n=== A1 short M1 / long M2 over the roll window ===')
for name, hr in (('A1a 1:1', 1.0), ('A1b h=%.2f' % h, h)):
    out, rows, x, cost = a1_eval(hr, name)
    results[name.split()[0]] = out
    show_a1(name, out)
    o15, *_ = a1_eval(hr, name, costmul=1.5)
    ol, *_ = a1_eval(hr, name, late=1)
    print('   costs x1.5: IS net %+.3f t %+.2f | VAL net %+.3f t %+.2f' % (o15['IS']['net'], o15['IS']['t'], o15['VAL']['net'], o15['VAL']['t']))
    print('   one step late: IS net %+.3f t %+.2f | VAL net %+.3f t %+.2f' % (ol['IS']['net'], ol['IS']['t'], ol['VAL']['net'], ol['VAL']['t']))
    # random-start windows: continuous daily pnl of the same position on the day's ETP pair
    c = -dS1 + hr * dS2
    c[last_day] = np.nan  # the pair changes over Tue->Wed: the rule is flat that day
    for e in ('IS', 'VAL'):
        m = np.array([rr[2] == e for rr in rows])
        lens = np.array([rr[4] - rr[0] for rr in rows])[m]
        target = x[m].mean()
        cand = np.flatnonzero(ERA == e)
        draws = []
        for _ in range(500):
            s = RNG.choice(cand, size=m.sum())
            tot = [np.nansum(c[si:si + L]) for si, L in zip(s, lens)]
            draws.append(np.mean(tot))
        draws = np.array(draws)
        print('   random-start windows %s: rule gross %+.3f beats %.1f %% of 500 draws (draw p50 %+.3f)' % (
            e, target, 100 * (draws < target).mean(), np.median(draws)))
        results[name.split()[0]][e]['rand'] = 100 * (draws < target).mean()
    # ProShares share split
    share = contracts / (P['OI1'] + P['OI2'])
    sh0 = np.array([share[rr[0]] for rr in rows])
    med = np.nanmedian(sh0[np.array([rr[2] == 'IS' for rr in rows])])
    for e in ('IS', 'VAL'):
        m = np.array([rr[2] == e for rr in rows])
        hi, lo = m & (sh0 > med), m & (sh0 <= med)
        print('   ETP-share split %s: high %+.3f (n %d) low %+.3f (n %d)' % (e, x[hi].mean() - cost, hi.sum(), x[lo].mean() - cost, lo.sum()))

# post-hoc control: the same carry on M2/M3 (not traded by short-term ETPs)
print('\n--- post-hoc control (labelled, not declared): short M2 / long M3, h23 ---')
for nm, hr in (('C23 1:1', 1.0), ('C23 h23=%.2f' % h23, h23)):
    out, rows, x, cost = a1_eval(hr, nm, c1='2', c2='3')
    show_a1(nm, out)

# ---------------- US500 beta of A1 windows ----------------
try:
    sys.path.insert(0, '/Users/hoangbk/00.code_base/105.AgentFxTrading')
    from zoneinfo import ZoneInfo
    z = np.load('/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/m1/US500.npz')
    ts = z[z.files[0]] if 't' not in z.files else z['t']
    keys = z.files
    tkey = [k for k in keys if k in ('t', 'ts', 'time', 'minute')]
    ts = z[tkey[0]] if tkey else z[keys[0]]
    cl = z['c']
    cut = ts < 1735689600000
    ts, cl = ts[cut], cl[cut]
    ny = ZoneInfo('America/New_York')
    spx = np.full(n, np.nan)
    for i, d in enumerate(D):
        dd = d.astype(object)
        if dd < dt.date(2016, 1, 5):
            continue
        t0 = dt.datetime(dd.year, dd.month, dd.day, 16, 14, tzinfo=ny).timestamp() * 1000
        j = np.searchsorted(ts, t0, side='right') - 1
        if j >= 0 and t0 - ts[j] < 3600_000:
            spx[i] = cl[j]
    for name, hr in (('A1a', 1.0), ('A1b', h)):
        _, rows, x, cost = a1_eval(hr, name)
        for e in ('IS', 'VAL'):
            sel = [(rr, xx) for rr, xx in zip(rows, x) if rr[2] == e]
            y = np.array([xx - cost for rr, xx in sel])
            xr = np.array([np.log(spx[rr[4]] / spx[rr[0]]) for rr, xx in sel])
            m = ~np.isnan(xr)
            X = np.column_stack([np.ones(m.sum()), xr[m]])
            b, *_ = np.linalg.lstsq(X, y[m], rcond=None)
            res = y[m] - X @ b
            se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * (res @ res) / (m.sum() - 2))
            print('   %s %s vs US500 window log-return: alpha %+.3f pt (t %+.2f), beta %+.2f pt per 100%% (t %+.2f), R2 %.2f' % (
                name, e, b[0], b[0] / se[0], b[1], b[1] / se[1], 1 - (res @ res) / ((y[m] - y[m].mean()) @ (y[m] - y[m].mean()))))
except Exception as ex:  # noqa
    print('US500 beta check failed:', repr(ex))

# ---------------- A2: long M1 / short M2 settle -> next open ----------------
print('\n=== A2 long M1 / short M2, settle t -> open t+1 ===')
so = (P['nO1'] - P['S1']) - (P['nO2'] - P['S2'])
O1_2, O2_2 = lead(2, 0, '1'), lead(2, 0, '2')
so_late = (O1_2 - P['S1']) - (O2_2 - P['S2'])
elig = ~last_day & ~np.isnan(so)
thr_roll = np.nanpercentile(roll_dose[elig & isd], 200 / 3)
cells_A2 = {'A2a': elig, 'A2b': elig & (roll_dose > thr_roll)}
print('roll-dose top-tercile threshold (IS) %.5f' % thr_roll)
for nm, m in cells_A2.items():
    rr = summ(so, m, SPREAD_RT)
    results[nm] = rr
    print(fmt(nm, rr))
    r15 = summ(so, m, 1.5 * SPREAD_RT)
    rt = summ(so, m, TICK + 4 * COMM)
    rl = summ(so_late, m, SPREAD_RT)
    print('   x1.5: IS %+.4f VAL %+.4f | TAS-entry cost 0.058: IS %+.4f (t %+.2f) VAL %+.4f (t %+.2f) | late (open t+2): IS %+.4f VAL %+.4f' % (
        r15['IS']['net'], r15['VAL']['net'], rt['IS']['net'], rt['IS']['t'], rt['VAL']['net'], rt['VAL']['t'], rl['IS']['net'], rl['VAL']['net']))
    print('   yearly net:', {**rr['PRE']['yearly'], **rr['IS']['yearly'], **rr['VAL']['yearly']})
    for e in ('IS', 'VAL'):
        me = m & (ERA == e)
        base = elig & (ERA == e)
        target = so[me].mean()
        if nm == 'A2b':
            draws = np.array([so[RNG.choice(np.flatnonzero(base), me.sum())].mean() for _ in range(NDRAW)])
        else:
            v = so[me]
            draws = np.array([(v * RNG.choice([-1, 1], len(v))).mean() for _ in range(NDRAW)])
        rr[e]['rand'] = 100 * (draws < target).mean()
        print('   random %s: beats %.1f %%' % (e, rr[e]['rand']))

# ---------------- B: fade the LETF dose ----------------
print('\n=== B fade the day\'s move on high LETF-dose days ===')
sg = -np.sign(r)
b1 = sg * (w1 * (P['nO1'] - P['S1']) + (1 - w1) * (P['nO2'] - P['S2']))
b2 = sg * (w1 * dS1 + (1 - w1) * dS2)
S1_2, S2_2 = lead(2, 1, '1'), lead(2, 1, '2')
b1l = sg * (w1 * (O1_2 - P['S1']) + (1 - w1) * (O2_2 - P['S2']))
b2l = sg * (w1 * (S1_2 - P['S1']) + (1 - w1) * (S2_2 - P['S2']))
eligB = ~last_day & ~np.isnan(letf_dose) & (r != 0)
ad = np.abs(letf_dose)
q90 = np.nanpercentile(ad[eligB & isd], 90)
q80 = np.nanpercentile(ad[eligB & isd], 80)
print('IS |dose| thresholds p80 %.5f p90 %.5f (fraction of M1+M2 dollar OI per day)' % (q80, q90))
for nm, x, xl, q in (('B1a', b1, b1l, q90), ('B1b', b1, b1l, q80), ('B2a', b2, b2l, q90), ('B2b', b2, b2l, q80)):
    m = eligB & (ad > q) & ~np.isnan(x)
    rr = summ(x, m, OUT_RT)
    results[nm] = rr
    print(fmt(nm, rr))
    r15 = summ(x, m, 1.5 * OUT_RT)
    rl = summ(xl, m, OUT_RT)
    print('   x1.5: IS %+.4f VAL %+.4f | late: IS %+.4f VAL %+.4f' % (r15['IS']['net'], r15['VAL']['net'], rl['IS']['net'], rl['VAL']['net']))
    print('   yearly net:', {**rr['PRE']['yearly'], **rr['IS']['yearly'], **rr['VAL']['yearly']})
    for e in ('IS', 'VAL'):
        me = m & (ERA == e)
        base = eligB & (ERA == e) & ~np.isnan(x)
        target = x[me].mean()
        draws = np.array([x[RNG.choice(np.flatnonzero(base), me.sum())].mean() for _ in range(NDRAW)])
        rr[e]['rand'] = 100 * (draws < target).mean()
        allfade = x[base].mean()
        print('   random %s: beats %.1f %% (all-days fade gross %+.4f, cell gross %+.4f)' % (e, rr[e]['rand'], allfade, target))

# ---------------- max-over-cells null (IS t) ----------------
print('\n=== max-over-8-cells null of IS t ===')
best = []
a1rows = {k: a1_eval(hr, k) for k, hr in (('A1a', 1.0), ('A1b', h))}
for _ in range(300):
    ts_ = []
    for k, (out, rows, x, cost) in a1rows.items():
        m = np.array([rr[2] == 'IS' for rr in rows])
        v = (x[m] - x[m].mean()) * RNG.choice([-1, 1], m.sum())
        ts_.append(V.tstat(v))
    for nm, m in cells_A2.items():
        me = m & isd
        v = (so[me] - so[me].mean()) * RNG.choice([-1, 1], me.sum())
        ts_.append(V.nw_t(v))
    for x, q in ((b1, q90), (b1, q80), (b2, q90), (b2, q80)):
        base = np.flatnonzero(eligB & isd & ~np.isnan(x))
        cnt = int((eligB & isd & (ad > q) & ~np.isnan(x)).sum())
        v = x[RNG.choice(base, cnt)] - OUT_RT
        ts_.append(V.nw_t(v))
    best.append(np.nanmax(ts_))
best = np.array(best)
print('null max IS t p50 %.2f p95 %.2f' % (np.percentile(best, 50), np.percentile(best, 95)))
print('observed IS t:', {k: round(float(v['IS']['t']), 2) for k, v in results.items()})

# ---------------- power at VAL size ----------------
print('\n=== power at VAL size over ~1.8 HOLD years ===')
for k, v in results.items():
    nval_per_yr = v['VAL']['n'] / 3
    pw = v['VAL']['sh'] * np.sqrt(1.8 * nval_per_yr) if not np.isnan(v['VAL']['sh']) else np.nan
    print('%s VAL sh/trade %+.3f trades/yr %.0f -> HOLD power %+.2f' % (k, v['VAL']['sh'], nval_per_yr, pw))
