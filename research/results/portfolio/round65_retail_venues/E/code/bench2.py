"""Causal random benchmark (added after run.py; the declared one draws windows before 16:09 on days selected by r at
16:09, so it contains the selecting move): shuffled-signal days = random era days, same window, side = sign(r)."""
import numpy as np
from letf import panel, prev_ref, bigmask, trade, CELLS, hm
rng = np.random.default_rng(651)
days, yr, B, A = panel()
mid, P = prev_ref(B, A)
IS = (yr >= 2016) & (yr <= 2021); VAL = (yr >= 2022) & (yr <= 2024)
for name, (sig, dirn, en, ex, q) in CELLS.items():
    s, e, x = hm(sig), hm(en), hm(ex)
    r = np.log(mid[:, s] / P)
    big = bigmask(r, q)
    side_all = np.where(np.isfinite(r), np.sign(r) * dirn, 0).astype(float)
    net_all, _ = trade(B, A, side_all, e, x)
    out = []
    for lab, msk in (("IS", IS), ("VAL", VAL)):
        act = np.nanmean(net_all[msk & big])
        pool = np.flatnonzero(msk & np.isfinite(net_all))
        k = int(np.sum(msk & big & np.isfinite(net_all)))
        dr = np.array([np.nanmean(net_all[rng.choice(pool, k, replace=False)]) for _ in range(2000)])
        out.append(f"{lab} actual {act:+.2f} shuffled mean {dr.mean():+.2f} beats {np.mean(dr < act)*100:.1f} %")
    print(name, " | ".join(out))
