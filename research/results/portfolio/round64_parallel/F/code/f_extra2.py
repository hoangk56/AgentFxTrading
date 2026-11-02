"""Stream F: T5 idio H60 without 2021-05-19 (Binance futures outage day) and liquidity / per-coin checks (information)."""
import os, sys, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from f_extra import cellidx, g, f, cost, day, t, sym, syms, r, line  # noqa
import report as Rp  # noqa
out = []
for cell in ("T5 idio H60", "T5 all H60"):
    tn, fn, Hs = cell.split(); k = Rp.HS.index(int(Hs[1:]))
    idx = cellidx(tn, fn, k); net = g[idx, k] - f[idx, k] - cost[idx]; d = day[idx]
    q = t[idx] < Rp.VAL0
    bad = d == (1621382400000 // 86400000)  # 2021-05-19
    out.append(f"{cell} IS without 2021-05-19: " + line("", net[q & ~bad], d[q & ~bad]) + f" (that day n {int((q & bad).sum())}, sum {net[q & bad].sum()*1e4:+.0f} bp)")
    for e, qq in (("IS", q), ("VAL", ~q)):
        ss = sym[idx][qq]; u, c = np.unique(ss, return_counts=True)
        out.append(f"  {e}: {len(u)} coins, max events per coin {c.max()} ({syms[u[np.argmax(c)]]}), share of coins with mean net > 0 "
                   f"{np.mean([net[qq][ss == s].mean() > 0 for s in u])*100:.0f} %")
    # stop-free worst trade, drawdown in bp per $1 per trade sequence
    o = np.argsort(t[idx]); cs = np.cumsum(net[o]); dd = (np.maximum.accumulate(cs) - cs).max()
    out.append(f"  worst trade {net.min()*1e4:+.0f} bp, best {net.max()*1e4:+.0f} bp, max drawdown of the cumulative sum {dd*1e4:.0f} bp "
               f"(sum {cs[-1]*1e4:.0f})")
print("\n".join(out))
open(os.path.join(Rp.OUT, "extra2.txt"), "w").write("\n".join(out) + "\n")
