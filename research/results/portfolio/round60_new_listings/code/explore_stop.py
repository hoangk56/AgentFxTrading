"""POST-HOC exploration (after N1's IS / VAL were seen): stop on the alt's daily high. Not a registered rule."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, listings as Lm
C = Lm.C
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
nd = int((C.HOLD_START - C.T0) // C.DAY)
def hi(s):
    _, a = C._read(os.path.join(Lm.B, 'perp_1d', s + '.csv')); H = np.full(nd, np.nan)
    d = C.day_of(a[:, 0]); m = (d >= 0) & (d < nd); H[d[m]] = a[m, 2]; return H
Fb, _, fb = Lm.load_series('BTCUSDT', False)
days = C.T0 + C.DAY * np.arange(nd, dtype=np.int64); months = days.astype('datetime64[ms]').astype('datetime64[M]').astype(int)
EV = Lm.events(syms)
for stop in (None, 0.3, 0.5, 1.0):
    for era, (a, b) in (('IS', Lm.ERAS['IS']), ('VAL', Lm.ERAS['VAL'])):
        R, K = [], []
        for s, L0 in EV:
            if s == 'BTCUSDT': continue
            e = L0 + 1
            if e >= nd - 1 or not (a <= days[e] < b): continue
            Fa, _, fa = Lm.load_series(s, False); Ha = hi(s)
            H = 30
            if stop is not None:
                lvl = Fa[e] * (1 + stop)
                w = np.where(Ha[e + 1:e + 31] >= lvl)[0]
                if len(w):
                    x = e + 1 + int(w[0])
                    d = np.arange(e + 1, x + 1)
                    alt = -stop - 0.002 + np.nansum(fa[d] * Fa[d - 1] / Fa[e])   # fill at the stop + 0.2 % slippage
                    btc = (Fb[x] / Fb[e] - 1) - np.nansum(fb[d] * Fb[d - 1] / Fb[e])
                    R.append(alt - 2 * 0.0015 + btc - 2 * 0.0006); K.append(months[e]); continue
            o = Lm.episode(Fa, fa, Fb, fb, e, H)
            if o is None or o[2] - e < 3: continue
            R.append(o[0]); K.append(months[e])
        R = np.array(R)
        print('stop', stop, era, 'n %d mean %+.2f%% sd %.1f%% SR/ep %.3f t_cl %.2f' % (len(R), 100 * R.mean(), 100 * R.std(ddof=1), R.mean() / R.std(ddof=1), Lm.cluster_t(R, K)))
