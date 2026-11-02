"""Descriptive extras (not new cells): VAL without the longest episode, IS without 2018, episode-level medians and
win shares, HOLD power at VAL size (episode and trade level)."""
import datetime as dt
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest as B  # noqa: E402
import premium  # noqa: E402

YRS_HOLD = 1.83
for k, h in B.CELLS:
    sig = B.signal(k)
    ep = premium.episodes(sig)
    for era in ("IS", "VAL"):
        pool = np.flatnonzero(np.isfinite(B.D["p"]) & B.era_mask(np.arange(B.N), era))
        idx = pool[sig[pool]]
        T = B.trades(idx, h)
        g = ep[T[:, 0].astype(int)]
        u, cnt = np.unique(g, return_counts=True)
        em = np.array([T[g == x, 1].mean() for x in u])
        big = u[np.argmax(cnt)]
        keep = g != big
        if era == "IS":
            keep2 = np.array([B.DATES[int(i)].year > 2018 for i in T[:, 0]])
            alt = f"ex-2018 net {T[keep2, 1].mean():.1f} t_cl {B.cl_t(T[keep2, 1], g[keep2]):.2f}"
        else:
            alt = ""
        eps_yr = len(u) / (3.0 if era == "VAL" else 3.47)
        pw_ep = em.mean() / em.std(ddof=1) * np.sqrt(eps_yr * YRS_HOLD)
        pw_tr = T[:, 1].mean() / T[:, 1].std(ddof=1) * np.sqrt(len(T) / (3.0 if era == "VAL" else 3.47) * YRS_HOLD)
        print(f"k{int(k*100)}h{h} {era}: eps {len(u)} ep-mean {em.mean():.1f} ep-median {np.median(em):.1f} ep-win "
              f"{np.mean(em > 0):.2f} | longest ep ({cnt.max()} trades) mean {T[~keep, 1].mean():.1f}; without it "
              f"net {T[keep, 1].mean():.1f} t_cl {B.cl_t(T[keep, 1], g[keep]):.2f} | {alt} | power ep {pw_ep:.2f} tr {pw_tr:.2f}")
