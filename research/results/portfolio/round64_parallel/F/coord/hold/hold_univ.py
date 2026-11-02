"""HOLD universe: xs.daily_universe (N 40, min_age 60) on daily quote volume of ALL Binance USDT-M perps in
research/data/binance/perp_1d (886 incl. delisted), days 2019-11-01..2026-10-29. Uses no prices.
Sanity: on 2020-2024 days it must equal stream F's univ.npz (built from the 212 ever-top-60 symbols)."""
import csv, os, sys, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rule
sys.path.insert(0, os.path.join(rule.R, "results/portfolio/round63_parallel/C/code"))
import xs  # noqa
sys.path.insert(0, os.path.join(rule.R, "results/portfolio/round60_new_listings/code"))
import listings as Lm  # noqa  (EXCL_BASE: stablecoins, index and TradFi perps, as stream C select_syms.py)
B = os.path.join(rule.R, "data", "binance", "perp_1d")
OUT = os.path.join(rule.R, "data", "binance_1m_wicks_hold")
END = 1793318400000  # 2026-10-30 00:00 UTC exclusive
DAY = 86400000
syms = sorted(f[:-4] for f in os.listdir(B) if f.endswith("USDT.csv"))
syms = [s for s in syms if Lm.base_of(s) not in Lm.EXCL_BASE]
# HOLD-era TradFi perps (equity / ETF / commodity / FX / index / premarket) are not altcoins: drop every symbol whose
# current fapi exchangeInfo underlyingType is not COIN (fetched 2026-11-01, before any HOLD price was read).
import json
_ex = json.load(open(os.path.join(rule.R, "data", "binance_1m_wicks_hold", "exinfo", "exchangeInfo.json")))
NONCOIN = {x["symbol"] for x in _ex["symbols"] if x.get("underlyingType") != "COIN"}
syms = [s for s in syms if s not in NONCOIN]
nd = (END - xs.H0) // DAY
QD = np.full((len(syms), nd), np.nan); first = np.zeros(len(syms), np.int64)
for i, s in enumerate(syms):
    rows = list(csv.reader(open(os.path.join(B, s + ".csv"))))[1:]
    d = np.array(rows, dtype=float) if rows else np.zeros((0, 8))
    d = d[d[:, 0] < END]
    first[i] = int((d[0, 0] - xs.H0) // DAY) if len(d) else 10 ** 6
    dd = ((d[:, 0] - xs.H0) // DAY).astype(np.int64); m = dd >= 0
    QD[i, dd[m]] = d[m, 6]
U, rk = xs.daily_universe({"QD": QD, "first_day": first}, N=40, min_age=60)
os.makedirs(OUT, exist_ok=True)
np.savez(os.path.join(OUT, "univ_full.npz"), U=U, rank=rk, syms=np.array(syms), day0=xs.H0)
# sanity vs stream F (2020-01-01..2024-12-31)
u = np.load(os.path.join(rule.R, "data", "binance_1m_wicks", "univ.npz")); fs = list(u["syms"])
d0, d1 = (1577836800000 - xs.H0) // DAY, (1735689600000 - xs.H0) // DAY
mism = 0
for d in range(d0, d1):
    a = {syms[i] for i in np.where(U[:, d])[0]}; b = {fs[i] for i in np.where(u["U"][:, d])[0]}
    mism += a != b
print("pre-2025 days with a different top-40 set:", mism, "of", d1 - d0)
days = xs.H0 + DAY * np.arange(nd); ym = np.array([dt.datetime.fromtimestamp(x / 1000, dt.timezone.utc).strftime("%Y-%m") for x in days])
sel = days >= 1735689600000
pairs = {("BTCUSDT", m) for m in np.unique(ym[sel])}
for i, s in enumerate(syms):
    for m in np.unique(ym[sel & U[i]]):
        pairs.add((s, m))
with open(os.path.join(OUT, "pull_list.csv"), "w") as f:
    f.write("sym,month\n")
    for s, m in sorted(pairs, key=lambda p: (p[1], p[0])):
        f.write(f"{s},{m}\n")
print("HOLD symbol-months", len(pairs), "symbols", len({s for s, _ in pairs}))
