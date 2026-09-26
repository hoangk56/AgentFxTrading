"""Pairs / stat-arb on bar closes: log spread s = ln X - beta ln Y with a rolling OLS beta over W past bars,
z = (s - rolling mean) / rolling sd (all from the past W bars). |z| > ZIN -> trade the spread back
(side = -sign z); exit at the first close with z back through ZOUT (toward 0), |z| >= ZSTOP, or after H bars.

Fills at the signal bar's closing bid/ask on each leg (the cBot would fill at the next tick). P&L in log
terms: side x (dlnX - beta dlnY) - costs, costs = per leg spread at entry and exit / 2 + commission, both
over price, leg Y weighted by |beta|, plus swaps. R = P&L / (sd of s at entry): 'spread sigmas'."""
from dataclasses import dataclass
from typing import List

import numpy as np

from research.scan.data import comm_price, resample
from research.scan.engine import period_of
from research.scan.m1 import load
from research.specs import SPECS, swap_usd

TFS = {"M15": 15, "M30": 30, "H1": 60, "H4": 240}


@dataclass
class PairTrade:
    t_in: int
    t_out: int
    side: int
    r: float
    why: str

    @property
    def period(self):
        return period_of(self.t_in)


def aligned_bars(x: str, y: str, tf: str, cache=None):
    cache = {} if cache is None else cache
    out = []
    for s in (x, y):
        key = (s, tf)
        if key not in cache:
            cache[key] = resample(load(s), TFS[tf])
        out.append(cache[key])
    bx, by = out
    t, ix, iy = np.intersect1d(bx.t, by.t, return_indices=True)
    return t, (bx.c[ix], bx.ca[ix]), (by.c[iy], by.ca[iy])


def _rolling(a: np.ndarray, W: int) -> np.ndarray:
    """Sum of the W values before i (excluding i); NaN for i < W."""
    cs = np.cumsum(np.r_[0.0, a])
    out = np.full(len(a), np.nan)
    out[W:] = cs[W:-1] - cs[:-W - 1]
    return out


def zscore(lx, ly, W):
    n = W
    sx, sy = _rolling(lx, W), _rolling(ly, W)
    sxx, syy, sxy = _rolling(lx * lx, W), _rolling(ly * ly, W), _rolling(lx * ly, W)
    mx, my = sx / n, sy / n
    vx, vy, cxy = sxx / n - mx * mx, syy / n - my * my, sxy / n - mx * my
    with np.errstate(invalid="ignore", divide="ignore"):
        beta = cxy / vy
        var_s = vx - cxy * cxy / vy
        sd = np.sqrt(np.maximum(var_s, 0))
        z = (lx - beta * ly - (mx - beta * my)) / sd
    return z, beta, sd


def run_pair(x, y, tf="M15", W=480, ZIN=2.0, ZOUT=0.0, ZSTOP=4.0, H=96, cache=None, max_gap_bars=4):
    t, (cx, ax), (cy, ay) = aligned_bars(x, y, tf, cache)
    lx, ly = np.log(cx), np.log(cy)
    z, beta, sd = zscore(lx, ly, W)
    span = TFS[tf] * 60_000
    gap = np.r_[False, np.diff(t) > max_gap_bars * span]    # session breaks / missing data
    sx, sy = SPECS[x], SPECS[y]
    kx, ky = comm_price(x), comm_price(y)
    trades: List[PairTrade] = []
    i, n = W + 1, len(t)
    while i < n - 1:
        zi = z[i]
        if not np.isfinite(zi) or abs(zi) <= ZIN or not np.isfinite(beta[i]) or sd[i] <= 0 or gap[i]:
            i += 1
            continue
        side = -1 if zi > 0 else 1          # +1 = long X / short beta Y
        b = beta[i]
        j = i + 1
        why = "time"
        while j < n - 1 and j - i < H:
            if gap[j]:
                why = "gap"
                break
            # z on the entry beta and entry mean/sd, so the exit tracks the traded spread
            zj = (lx[j] - b * ly[j] - (lx[i] - b * ly[i])) / sd[i] + zi
            if side * zj >= -ZOUT:
                why = "mean"
                break
            if abs(zj) >= ZSTOP and np.sign(zj) == np.sign(zi):
                why = "stop"
                break
            j += 1
        if why == "gap":
            j = j - 1
        pnl = side * ((lx[j] - lx[i]) - b * (ly[j] - ly[i]))
        cost = ((ax[i] - cx[i]) + (ax[j] - cx[j])) / 2 / cx[i] + kx / cx[i]
        cost += abs(b) * (((ay[i] - cy[i]) + (ay[j] - cy[j])) / 2 / cy[i] + ky / cy[i])
        sw = swap_usd(x, side, 1.0, int(t[i]), int(t[j]) + span) / sx.usd_per_quote / cx[i]
        sw += abs(b) * swap_usd(y, -side * int(np.sign(b) or 1), 1.0, int(t[i]), int(t[j]) + span) / sy.usd_per_quote / cy[i]
        trades.append(PairTrade(int(t[i]), int(t[j]), side, (pnl - cost + sw) / sd[i], why))
        i = j + 1
    return trades
