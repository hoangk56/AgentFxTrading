import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from udata import *
t0=time.time()
coins, hb, T = panel()
print(len(coins), "coins", round(time.time()-t0,1), "s")
for k in (2,4,8):
    for ru in (0,1):
        for hold in (24,72):
            ev = events(coins, T, k, ru, hold)
            tt = np.array([T[j] for _, j in ev])
            nis = ((tt>=ERAS["IS"][0])&(tt<ERAS["IS"][1])).sum(); nv=((tt>=ERAS["VAL"][0])&(tt<ERAS["VAL"][1])).sum()
            nc = len({ci for ci,_ in ev})
            print(f"k{k} ru{ru} H{hold} n {len(ev)} IS {nis} VAL {nv} coins {nc} days {len(np.unique(tt//DAY))}")
