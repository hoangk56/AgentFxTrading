"""Stream O information (not cells): H1 by half-year, without the LUNA (2022-05) and FTX (2022-11) months, per-coin
concentration; H2 trade counts per year (top-position coverage)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E  # noqa: E402
import importlib.util as _u; _s = _u.spec_from_file_location("o_run", os.path.join(HERE, "run.py")); R = _u.module_from_spec(_s); _s.loader.exec_module(R)
from engine import xs  # noqa: E402
import warnings
warnings.simplefilter("ignore")
D = E.Data()
from datetime import datetime, timezone
def ms(y, m):
    return datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000
edges = [ms(2022, 1), ms(2022, 7), ms(2023, 1), ms(2023, 7), ms(2024, 1), ms(2024, 7), ms(2025, 1)]
for q, p, H in ((0.02, 0.03, 4), (0.02, 0.03, 24), (0.02, 0.05, 4), (0.04, 0.03, 24)):
    I, T = R.h1_signals(D, q, p)
    tr = R.trades(D, I, T, np.ones(len(I)), H)
    tm = xs.H0 + tr["t"] * xs.HOUR
    row = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (tm >= a) & (tm < b)
        row.append(f"{tr['r'][m].mean()*1e4:+.0f} (n {m.sum()}, t {E.tclust(tr['r'][m], tr['t'][m]//24):+.2f})")
    bad = ((tm >= ms(2022, 5)) & (tm < ms(2022, 6))) | ((tm >= ms(2022, 11)) & (tm < ms(2022, 12)))
    m = (tm < edges[3]) & ~bad
    print(f"H1 q{q} p{p} H{H} half-years:", " | ".join(row))
    print(f"   DISC without 2022-05 and 2022-11: {tr['r'][m].mean()*1e4:+.1f} bp n {m.sum()} t {E.tclust(tr['r'][m], tr['t'][m]//24):+.2f}")
    v = tm >= edges[3]
    ii, cnt = np.unique(tr["i"][v], return_counts=True)
    s = np.array([tr["r"][v][tr["i"][v] == i].sum() for i in ii])
    top = np.argsort(-s)[:3]
    print("   VAL top-3 coins by summed net:", [(D.syms[ii[k]], int(cnt[k]), round(s[k] * 1e4)) for k in top],
          "VAL total", round(tr["r"][v].sum() * 1e4), "without top-3", round((tr["r"][v].sum() - s[top].sum()) * 1e4))
