"""Build a numpy panel from the jwigginton Yahoo-style daily parquet (run with a python that has duckdb, with -I).

usage: python -I build_panel.py <daily.parquet> <const.parquet> <out.npz>
Rows with date >= 2025-01-01 are dropped in the SQL (none exist; the file ends 2024-03-11).
"""
import sys
import duckdb
import numpy as np

src, const, out = sys.argv[1:4]
c = duckdb.connect()
rows = c.sql(f"""
    select symbol, date, open, high, low, close, adj_close, volume
    from '{src}' where date >= '2002-06-01' and date < '2025-01-01'
    order by symbol, date""").fetchnumpy()
syms = np.unique(rows["symbol"])
dates = np.unique(rows["date"])
si = np.searchsorted(syms, rows["symbol"])
di = np.searchsorted(dates, rows["date"])
S, D = len(syms), len(dates)
panel = {}
for f in ["open", "high", "low", "close", "adj_close", "volume"]:
    a = np.full((D, S), np.nan)
    a[di, si] = np.asarray(rows[f], dtype=float)
    panel[f] = a
cd = c.sql(f"select symbol, date_added from '{const}'").fetchnumpy()
added = {s: d for s, d in zip(cd["symbol"], cd["date_added"])}
date_added = np.array([added.get(s, "9999-12-31") or "9999-12-31" for s in syms])
np.savez_compressed(out, syms=syms.astype(str), dates=dates.astype(str), date_added=date_added.astype(str), **panel)
print(S, D, dates[0], dates[-1])
