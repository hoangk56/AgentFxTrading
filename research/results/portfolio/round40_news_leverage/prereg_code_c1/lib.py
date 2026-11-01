"""Stream C common code: prices (HOLD cut at load), fills, costs, t statistics. Adapted from round 37 N lib.py."""
import sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading")
import datetime as dt
import json
import glob
import numpy as np

from research import m1
from research.specs import rollovers
from research.swing.rates import swap_frac_at

S = "/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r40/C"
CNH = ("/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/"
       "scratchpad/r37/N/USDCNH_m1.npz")  # built by round 37 N from IC ticks 2016-24 only
HOLD_MS = 1735689600000  # 2025-01-01
CUT = dt.date(2024, 12, 31)
FX = {"USDCNH", "AUDUSD", "USDJPY"}
TRIPLE = {"HK50": 4, "JP225": 4, "US500": 4, "XAUUSD": 2}
_P = {}


def load(sym):
    if sym in _P:
        return _P[sym]
    if sym == "USDCNH":
        z = np.load(CNH)
        d = {k: z[k] for k in z.files}
    else:
        d = m1.load(sym)
    k = d["ts"] < HOLD_MS
    d = {kk: v[k] for kk, v in d.items()}
    assert d["ts"].max() < HOLD_MS
    _P[sym] = d
    return d


def ms(date, hh, mm):
    return int(dt.datetime(date.year, date.month, date.day, hh, mm, tzinfo=dt.timezone.utc).timestamp() * 1000)


def bar_at(sym, t, tol_min=10):
    d = load(sym)
    i = np.searchsorted(d["ts"], t)
    if i < len(d["ts"]) and d["ts"][i] - t <= tol_min * 60000:
        return i
    return -1


def trade(sym, side, t_in, t_out, sx=1.0, lat=0, tol=10):
    """signal known at t_in; fill at close of the bar starting t_in (+lat min). Exit at close of bar t_out (+lat).
    Buy at ask close, sell at bid close. Returns (mid bp, net bp) or None."""
    d = load(sym)
    i = bar_at(sym, t_in + 60000 * lat, tol)
    j = bar_at(sym, t_out + 60000 * lat, tol)
    if i < 0 or j < 0 or j <= i:
        return None
    bi, ai, bj, aj = d["c"][i], d["ca"][i], d["c"][j], d["ca"][j]
    mi, mj = (bi + ai) / 2, (bj + aj) / 2
    mid = side * (mj - mi) / mi * 1e4
    cost = sx * ((ai - bi) / 2 / mi + (aj - bj) / 2 / mj) * 1e4
    if sym in FX:
        cost += 0.6
    nroll = rollovers(int(d["ts"][i]), int(d["ts"][j]), TRIPLE.get(sym, 2))
    if not nroll:
        sw = 0.0
    elif sym == "USDCNH":
        sw = cnh_swap(side, int(d["ts"][i])) * nroll * 1e4
    else:
        sw = swap_frac_at(sym, side, int(d["ts"][i])) * nroll * 1e4
    return mid, mid - cost + sw


_HIB = None


def cnh_swap(side, t):
    """USDCNH swap: (r_USD - 2.5 %)/360 minus the mean calibrated FX markup (round 37 N approximation)."""
    from research.swing.rates import rate, markups, CALIBRATED_FX
    global _HIB
    if _HIB is None:
        mk = [markups(p) for p in CALIBRATED_FX]
        _HIB = (float(np.mean([m[0] for m in mk])), float(np.mean([m[1] for m in mk])))
    ml, msh = _HIB
    d = (rate("USD", t) - 0.025) / 360.0
    return d - ml if side > 0 else -d - msh


def tstat(x):
    x = np.asarray(x, float)
    if len(x) < 3:
        return np.nan
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))


def cluster_t(x, g):
    """t of the mean with cluster-robust variance (clusters g)."""
    x = np.asarray(x, float); g = np.asarray(g)
    n = len(x)
    if n < 3:
        return np.nan
    e = x - x.mean()
    us = np.unique(g)
    if len(us) < 3:
        return np.nan
    s = np.array([e[g == u].sum() for u in us])
    v = (s @ s) / n ** 2 * len(us) / (len(us) - 1)
    return x.mean() / np.sqrt(v)


def era(date):
    y = date.year
    return "PRE" if y < 2016 else "IS" if y <= 2021 else "VAL" if y <= 2024 else "HOLD"


def load_margin():
    """Eastmoney RPTA_RZRQ_LSHJ (SSE + SZSE total) -> list of dict sorted by date; rows after 2024-12-31 dropped."""
    rows = {}
    for f in sorted(glob.glob(f"{S}/web/em_lshj/*.json")):
        for r in json.load(open(f))["result"]["data"]:
            d = dt.date.fromisoformat(r["DIM_DATE"][:10])
            if d > CUT:
                continue
            rows[d] = r
    return [rows[d] | {"date": d} for d in sorted(rows)]
