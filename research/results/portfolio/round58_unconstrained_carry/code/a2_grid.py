"""A2 / A3 grid on IS, chosen cell checked on VAL (declared in HYPOTHESES_A.md)."""
import sys, json, os; sys.path.insert(0, '.')
import numpy as np, carry as C
syms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
only = None
if len(sys.argv) > 2 and sys.argv[2] == 'A3':
    only = {'BTCUSDT', 'ETHUSDT'}
P = C.load_panel(syms)
U, rank = C.universe(P, N=30)
rows = []
for era in ('IS',):
    d0, d1 = C.era_slice(P, era)
    for L in (3, 7, 14):
        for th in (0.10, 0.20, 0.30):
            for tho in (0.0, th / 2):
                b, eps = C.simulate(P, U, rank, L=L, th_in=th, th_out=tho, K=(2 if only else 10), only=only, d0=d0, d1=d1)
                st = C.stats(b)
                turn = len(eps)
                rows.append((L, th, tho, st['ann'], st['vol'], st['sharpe_a'], st['t_nw'], turn))
                print('L%2d in %.2f out %.2f  ann %6.2f%% vol %5.2f%% SRa %5.2f tNW %5.2f eps %4d' % (L, th, tho, 100*st['ann'], 100*st['vol'], st['sharpe_a'], st['t_nw'], turn), flush=True)
