"""Information only: at X's cheap signals, is the Binance perp also cheap vs the other venues? Mean B basis deviation
(perp-spot basis minus its 168 h median) at the signal hour, and the share of the gap closed by Binance spot vs venues."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xv, basis  # noqa
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out')
coins = xv.attach_venues(basis.load())
lines = []
for k in (30, 60, 100):
    for Hh in (6, 24):
        nm = f'k{k}_H{Hh}_cheap'
        T = dict(np.load(os.path.join(OUT, f'trades_main_{nm}.npz')))
        dB = np.array([coins[ci]['b'][h] - coins[ci]['m'][h] for ci, h in zip(T['ci'], T['h'])]) * 1e4
        nv = np.array([coins[ci]['nv'][h] for ci, h in zip(T['ci'], T['h'])])
        for era in ('IS', 'VAL'):
            m = xv.era_mask(T['t'], 'main', era)
            g = T['g'][m] * 1e4
            lines.append(f'{nm} {era}: n {m.sum()}, G mean {g.mean():.1f} bp, B basis dev at signal mean {np.nanmean(dB[m]):.1f} '
                         f'median {np.nanmedian(dB[m]):.1f} bp (perp-vs-venues dev = G + basis dev: {np.nanmean(g + dB[m]):.1f}), '
                         f'venues used mean {nv[m].mean():.2f}, Binance spot move {np.nanmean(T["bs"][m]):.1f}, '
                         f'venue median move {np.nanmean(T["vm"][m]):.1f}, hedged price leg {T["price"][m].mean() * 1e4:.1f} bp')
txt = '\n'.join(lines)
print(txt)
open(os.path.join(OUT, 'diag.txt'), 'w').write(txt + '\n')
