"""The researched rules (research/results/strategy_search.md, strategy_prereg.md) as lab strategies.

Each function trades one chunk through run_intents. Stops and targets are distances from the fill unless a
rule names a price (range ends, previous close). D1 bars close at 17:00 New York and D1 entries and time
exits wait 2 h (engine.D1_ENTRY_DELAY_MS). Rules that need other symbols' history (X1, FXM1, MEF) read the
real M1 cache and are catalogued as real-data only."""
import math
import re
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache, reduce
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from research.indicators import atr_sma, ema, prior_max, prior_min, rsi
from research.lab.engine import D1_ENTRY_DELAY_MS, DAY_MS, NAN, Ctx, Intent, run_intents
from research.lab.universe import FX_REAL
from research.scan.data import atr as scan_atr, resample
from research.scan.engine import Order, simulate
from research.scan.m1 import load as load_m1
from research.sim import _first_hit

TF_MIN = {"M15": 15, "H1": 60, "H4": 240, "D1": 1440}


def _delay(b) -> int:
    return D1_ENTRY_DELAY_MS if b.minutes == 1440 else 0


def _intents(b, a, sig, H, SLK, TPK, warm) -> List[Intent]:
    n, d = len(b), _delay(b)
    out = []
    for i in np.flatnonzero(sig):
        if i < warm or not math.isfinite(a[i]) or a[i] <= 0:
            continue
        out.append(Intent(int(b.close_time[i]) + d, int(sig[i]), SLK * a[i], TPK * a[i] if TPK else NAN,
                          int(b.close_time[min(i + H, n - 1)]) + d))
    return out


def shock_follow(ctx: Ctx, tf: int = 15, Z: float = 2.5, H: int = 12, SLK: float = 2.0, TPK: float = 2.0) -> None:
    """BTC-S1: a bar whose close moved more than Z x ATR20 (SMA of TR) -> follow at the next tick; SL/TP x ATR
    from the fill; time exit at the first tick after bar i + H closes."""
    b = ctx.bars(tf)
    a = atr_sma(b.h, b.l, b.c, 20)
    with np.errstate(invalid="ignore", divide="ignore"):
        mv = np.r_[0.0, np.diff(b.c)] / a
    sig = np.where(mv > Z, 1, np.where(mv < -Z, -1, 0))
    run_intents(ctx, _intents(b, a, sig, H, SLK, TPK, 25))


def bank_rule(ctx: Ctx, kind: str, mode: int, tf: str, H: int, SLK: float, TPK=None, L: int = 1,
              Z: float = 1.0, N: int = 20, P: int = 14, lo: float = 30.0, warm: int = 25) -> None:
    """research/scan/bank.py's families: zmove (C - C[L] beyond Z x ATR20), donch (first close beyond the prior
    N-bar high/low), rsi (RSI(P) beyond 100 - lo / lo). mode +1 follows the move, -1 fades it."""
    b = ctx.bars(TF_MIN[tf])
    a = atr_sma(b.h, b.l, b.c, 20)
    n = len(b)
    with np.errstate(invalid="ignore", divide="ignore"):
        if kind == "zmove":
            z = np.zeros(n)
            z[L:] = (b.c[L:] - b.c[:-L]) / a[L:]
            raw = np.where(z > Z, 1, np.where(z < -Z, -1, 0))
        elif kind == "donch":
            up, dn = b.c > prior_max(b.h, N), b.c < prior_min(b.l, N)
            raw = np.where(up & ~np.r_[False, up[:-1]], 1, np.where(dn & ~np.r_[False, dn[:-1]], -1, 0))
        elif kind == "rsi":
            r = rsi(b.c, P)
            raw = np.where(r > 100 - lo, 1, np.where(r < lo, -1, 0))
        else:
            raise ValueError(kind)
    run_intents(ctx, _intents(b, a, raw * mode, H, SLK, TPK, warm))


_BANK = re.compile(r"(zmove|donch|rsi)([FR])_(M15|H1|H4|D1)_(.*)_H(\d+)_SL([\d.]+)_TP(None|[\d.]+)$")


def parse_bank(name: str) -> dict:
    """'zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0' -> bank_rule keyword arguments."""
    kind, fr, tf, mid, H, SL, TP = _BANK.match(name).groups()
    kw = dict(kind=kind, mode=1 if fr == "F" else -1, tf=tf, H=int(H), SLK=float(SL),
              TPK=None if TP == "None" else float(TP))
    for part in mid.split("_"):
        key = re.match(r"[A-Za-z]+", part).group()
        val = part[len(key):]
        kw[key] = float(val) if "." in val else int(val)
    if "lo" in kw:
        kw["lo"] = float(kw["lo"])
    return kw


# The 552-config bank's best cell per (kind, direction, timeframe) by pooled 2025 mean R with n >= 30
# (research/results/bank_stats.csv, P1), frozen 2026-09-25 for the lab. The 2025 means are in the catalog.
BANK_CONFIGS = (
    "donchF_D1_N55_H6_SL1.0_TP1.5", "donchF_H1_N10_H24_SL2.5_TPNone", "donchF_H4_N55_H6_SL1.0_TP1.5",
    "donchF_M15_N55_H24_SL2.5_TPNone", "donchR_D1_N10_H6_SL1.5_TPNone", "donchR_H1_N20_H6_SL1.5_TPNone",
    "donchR_H4_N55_H24_SL2.5_TPNone", "donchR_M15_N55_H24_SL2.5_TPNone", "rsiF_D1_P14_lo30_H6_SL1.0_TP1.0",
    "rsiF_H1_P14_lo20_H12_SL2.0_TPNone", "rsiF_H4_P2_lo10_H12_SL2.0_TPNone", "rsiF_M15_P14_lo20_H12_SL2.0_TPNone",
    "rsiR_D1_P2_lo5_H3_SL1.5_TPNone", "rsiR_H1_P2_lo5_H3_SL1.5_TPNone", "rsiR_H4_P14_lo20_H12_SL2.0_TPNone",
    "rsiR_M15_P2_lo5_H12_SL2.0_TPNone", "zmoveF_D1_L3_Z3.0_H3_SL1.0_TP1.0", "zmoveF_H1_L3_Z3.0_H3_SL1.0_TP1.0",
    "zmoveF_H4_L1_Z3.0_H12_SL2.0_TPNone", "zmoveF_M15_L1_Z3.0_H12_SL2.0_TPNone", "zmoveR_D1_L3_Z3.0_H12_SL2.0_TPNone",
    "zmoveR_H1_L1_Z3.0_H12_SL2.0_TPNone", "zmoveR_H4_L3_Z3.0_H12_SL2.0_TPNone", "zmoveR_M15_L1_Z1.0_H12_SL2.0_TPNone",
)
# 2025 pooled mean R of each, same order (for the catalog's findings).
BANK_2025_R = (-0.051, -0.012, -0.018, -0.063, +0.099, -0.023, +0.113, -0.049, -0.047, +0.026, -0.014, -0.013,
               +0.063, -0.043, +0.124, -0.067, +0.107, +0.023, +0.246, -0.047, +0.137, -0.025, +0.092, -0.063)


# ---------------------------------------------------------------- index cash sessions
SESSIONS = {"US30": ("America/New_York", time(9, 30), time(16, 0)),
            "USTEC": ("America/New_York", time(9, 30), time(16, 0)),
            "DE40": ("Europe/Berlin", time(9, 0), time(17, 30)),
            "UK100": ("Europe/London", time(8, 0), time(16, 30))}
OPEN_TOLERANCE_MS = 5 * 60_000


def session_days(ctx: Ctx, tz_name: str, t_open: time, t_close: time):
    """[(date, open_ms, close_ms)] for the weekdays from two weeks before the chunk's year (look-backs) whose
    open has a tick within 5 minutes; a holiday has none."""
    tz, t = ZoneInfo(tz_name), ctx.t
    d = datetime.fromtimestamp(ctx.ch.lo_ms / 1000, timezone.utc).date() - timedelta(days=14)
    last = datetime.fromtimestamp(ctx.ch.hi_ms / 1000, timezone.utc).date()
    out = []
    while d <= last:
        if d.weekday() < 5:
            o = int(datetime.combine(d, t_open, tz).timestamp() * 1000)
            e = ctx.tick_at(o)
            if e < len(t) and t.ts[e] < o + OPEN_TOLERANCE_MS:
                out.append((d, o, int(datetime.combine(d, t_close, tz).timestamp() * 1000)))
        d += timedelta(days=1)
    return out


def _index_days(ctx: Ctx):
    return session_days(ctx, *SESSIONS[ctx.ch.symbol])


def _bid_at(ctx: Ctx, ms: int) -> float:
    e = ctx.tick_at(ms)
    return float(ctx.t.bid[e]) if e < len(ctx.t) else NAN


def _bid_before(ctx: Ctx, ms: int) -> float:
    e = ctx.tick_at(ms) - 1
    return float(ctx.t.bid[e]) if e >= 0 else NAN


def _hl(ctx: Ctx, a_ms: int, b_ms: int):
    m = ctx.bars(1)
    i0, i1 = np.searchsorted(m.open_time, [a_ms, b_ms], side="left")
    if i1 <= i0:
        return NAN, NAN
    return float(m.h[i0:i1].max()), float(m.l[i0:i1].min())


def _tom_days(days):
    """The last trading day of each month (once the next month has started) and its first three."""
    by_month = {}
    for d in sorted(days):
        by_month.setdefault((d.year, d.month), []).append(d)
    months = sorted(by_month)
    out = set()
    for k, key in enumerate(months):
        out.update(by_month[key][:3])
        if k + 1 < len(months):
            out.add(by_month[key][-1])
    return out


def turn_of_month(ctx: Ctx, sl_pct: float = 0.03) -> None:
    """TOM: long over the cash session on the last and the first three trading days of each month; SL 3 %."""
    days = _index_days(ctx)
    tom = _tom_days([d for d, _, _ in days])
    run_intents(ctx, [Intent(o, 1, sl_px=_bid_at(ctx, o) * (1 - sl_pct), exit_ms=c)
                      for d, o, c in days if d in tom])


def opening_range(ctx: Ctx, minutes: int = 60) -> None:
    """K2: direction of the first `minutes` of the cash session, entered at its end, stop at the other end of
    the range, exit at the session close."""
    its = []
    for _, o, c in _index_days(ctx):
        end = o + minutes * 60_000
        hi, lo = _hl(ctx, o, end)
        first, last = _bid_at(ctx, o), _bid_before(ctx, end)
        if not math.isfinite(hi) or not math.isfinite(last) or last == first:
            continue
        side = 1 if last > first else -1
        its.append(Intent(end, side, sl_px=lo if side > 0 else hi, exit_ms=c))
    run_intents(ctx, its)


def vol_breakout(ctx: Ctx, k: float = 0.35, lookback: int = 5) -> None:
    """VB1: stop entries at the open +/- k x the mean range of the last sessions; the first side touched
    trades, SL at the open, exit at the session close."""
    t, ranges, its = ctx.t, [], []
    for _, o, c in _index_days(ctx):
        hi, lo = _hl(ctx, o, c)
        if len(ranges) >= lookback:
            rng = float(np.mean(ranges[-lookback:]))
            e0, e1 = ctx.tick_at(o), ctx.tick_at(c)
            op = float(t.bid[e0])
            jb = _first_hit(t.ask[:e1], e0, -np.inf, op + k * rng)
            js = _first_hit(t.bid[:e1], e0, op - k * rng, np.inf)
            if min(jb, js) < e1:
                its.append(Intent(int(t.ts[min(jb, js)]), 1 if jb <= js else -1, sl_px=op, exit_ms=c))
        if math.isfinite(hi):
            ranges.append(hi - lo)
    run_intents(ctx, its)


def last30_fade(ctx: Ctx) -> None:
    """LC1 (US30, USTEC): fade C(15:30) - C(10:00) New York from 15:30 to the 16:00 close; SL 2 x ATR20(30 min)."""
    b = ctx.bars(30)
    a = atr_sma(b.h, b.l, b.c, 20)
    its = []
    for _, o, c in session_days(ctx, "America/New_York", time(9, 30), time(16, 0)):
        t10, t1530 = o + 30 * 60_000, c - 30 * 60_000
        mid = _bid_before(ctx, t1530) - _bid_before(ctx, t10)
        k = int(np.searchsorted(b.close_time, t1530, side="right")) - 1
        if math.isfinite(mid) and mid != 0 and k >= 20 and math.isfinite(a[k]):
            its.append(Intent(t1530, -1 if mid > 0 else 1, 2.0 * a[k], exit_ms=c))
    run_intents(ctx, its)


def gap_fade(ctx: Ctx, k: float = 0.1, lookback: int = 5) -> None:
    """GF1 (US30, USTEC): an opening gap larger than k x the mean session range is faded at 9:31, TP at the
    previous close, SL the gap's size beyond the open, exit at the close."""
    ranges, prev_c, its = [], None, []
    for _, o, c in session_days(ctx, "America/New_York", time(9, 30), time(16, 0)):
        hi, lo = _hl(ctx, o, c)
        if prev_c is not None and len(ranges) >= lookback:
            op, pc = _bid_at(ctx, o), _bid_before(ctx, prev_c)
            gap = op - pc
            if math.isfinite(gap) and abs(gap) > k * float(np.mean(ranges[-lookback:])):
                side = -1 if gap > 0 else 1
                its.append(Intent(o + 60_000, side, sl_px=op - side * abs(gap), tp_px=pc, exit_ms=c))
        if math.isfinite(hi):
            ranges.append(hi - lo)
        prev_c = c
    run_intents(ctx, its)


def overnight_drift(ctx: Ctx) -> None:
    """OD1 (US30, USTEC): long 02:00 -> 03:00 New York on weekdays; SL 2 x ATR20(H1)."""
    b = ctx.bars(60)
    a = atr_sma(b.h, b.l, b.c, 20)
    its = []
    for _, o, c in session_days(ctx, "America/New_York", time(2, 0), time(3, 0)):
        k = int(np.searchsorted(b.close_time, o, side="right")) - 1
        if k >= 20 and math.isfinite(a[k]):
            its.append(Intent(o, 1, 2.0 * a[k], exit_ms=c))
    run_intents(ctx, its)


# ---------------------------------------------------------------- FX D1 / H4 and cross-symbol rules
_m1 = lru_cache(maxsize=None)(load_m1)


def _d1_z(b, L):
    a = atr_sma(b.h, b.l, b.c, 20)
    z = np.full(len(b), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        z[L:] = (b.c[L:] - b.c[:-L]) / a[L:]
    return a, z


def weekly_fade(ctx: Ctx, L: int = 5, Z: float = 1.5, H: int = 5, SLK: float = 3.0) -> None:
    """K1 / K1b: a 5-day move beyond Z x ATR20(D1) is faded 2 h after the New York close; SL SLK x ATR from
    the signal close, no target, time exit H D1 bars later."""
    b = ctx.bars(1440)
    a, z = _d1_z(b, L)
    n, d, its = len(b), _delay(b), []
    for i in range(25, n):
        if math.isfinite(z[i]) and abs(z[i]) > Z and math.isfinite(a[i]):
            side = -1 if z[i] > 0 else 1
            its.append(Intent(int(b.close_time[i]) + d, side, sl_px=b.c[i] - side * SLK * a[i],
                              exit_ms=int(b.close_time[min(i + H, n - 1)]) + d))
    run_intents(ctx, its)


@lru_cache(maxsize=1)
def _fx_fade_log() -> np.ndarray:
    """(exit ms, R) of K1's base fade trades on the 8 real FX pairs, M1 engine, D1 cut at 00:00 UTC (FXM1's
    regime input, as pre-registered)."""
    rows = []
    for s in FX_REAL:
        m = _m1(s)
        b = resample(m, 1440)
        a = scan_atr(b, 20)
        n = len(b)
        z = np.full(n, np.nan)
        with np.errstate(invalid="ignore", divide="ignore"):
            z[5:] = (b.c[5:] - b.c[:-5]) / a[5:]
        orders = []
        for i in range(25, n - 1):
            if math.isfinite(z[i]) and abs(z[i]) > 1.5 and math.isfinite(a[i]):
                side = -1 if z[i] > 0 else 1
                orders.append(Order(int(b.last[i]) + 1, side, b.c[i] - side * 3.0 * a[i], int(b.last[min(i + 5, n - 1)])))
        rows += [(f.t_out, f.r) for f in simulate(m, s, orders)]
    return np.array(sorted(rows), float).reshape(-1, 2)


def regime_fade(ctx: Ctx, window_days: int = 120) -> None:
    """FXM1: K1's fade, traded in the direction the base fade earned over the last 120 days on the 8 pairs
    (sum of R > 0 -> fade, < 0 -> follow)."""
    log = _fx_fade_log()
    b = ctx.bars(1440)
    a, z = _d1_z(b, 5)
    n, d, its = len(b), _delay(b), []
    for i in range(25, n):
        if not (math.isfinite(z[i]) and abs(z[i]) > 1.5 and math.isfinite(a[i])):
            continue
        T = int(b.close_time[i])
        sel = (log[:, 0] < T) & (log[:, 0] >= T - window_days * DAY_MS)
        regime = np.sign(log[sel, 1].sum())
        if regime == 0:
            continue
        side = int((-1 if z[i] > 0 else 1) * regime)
        its.append(Intent(T + d, side, sl_px=b.c[i] - side * 3.0 * a[i], exit_ms=int(b.close_time[min(i + 5, n - 1)]) + d))
    run_intents(ctx, its)


@lru_cache(maxsize=1)
def _x1_schedule(L: int = 30, hold: int = 30, top: int = 3):
    """X1: currency strengths = least-squares fit of the 8 pairs' 30-bar H4 log returns (6 currencies, sum 0);
    pair score = (strength base - strength quote) / (ATR20 / price). Every 30 H4 bars the 3 largest |score|
    are traded against the score for 30 bars, no stop."""
    ccys = ("AUD", "CAD", "EUR", "GBP", "JPY", "USD")
    bars = {s: resample(_m1(s), 240) for s in FX_REAL}
    common = reduce(np.intersect1d, [b.t for b in bars.values()])
    idx = {s: np.searchsorted(bars[s].t, common) for s in FX_REAL}
    logc = np.column_stack([np.log(bars[s].c[idx[s]]) for s in FX_REAL])
    atr_rel = np.column_stack([scan_atr(bars[s], 20)[idx[s]] / bars[s].c[idx[s]] for s in FX_REAL])
    A = np.zeros((len(FX_REAL), len(ccys)))
    for p, s in enumerate(FX_REAL):
        A[p, ccys.index(s[:3])], A[p, ccys.index(s[3:])] = 1.0, -1.0
    M = np.vstack([A, np.ones(len(ccys))])
    close = common + 240 * 60_000
    sched = {s: [] for s in FX_REAL}
    for k in range(L + 20, len(common) - 1, hold):
        r, ar = logc[k] - logc[k - L], atr_rel[k]
        if not (np.all(np.isfinite(r)) and np.all(np.isfinite(ar)) and np.all(ar > 0)):
            continue
        score = (A @ np.linalg.lstsq(M, np.r_[r, 0.0], rcond=None)[0]) / ar
        for p in np.argsort(-np.abs(score))[:top]:
            sched[FX_REAL[p]].append((int(close[k]), -int(np.sign(score[p])),
                                      int(close[min(k + hold, len(common) - 1)])))
    return sched


def cross_sectional_reversal(ctx: Ctx) -> None:
    run_intents(ctx, [Intent(at, side, exit_ms=ex) for at, side, ex in _x1_schedule().get(ctx.ch.symbol, []) if side])


MEF_SIDE = {"EURUSD": 1, "GBPUSD": 1, "AUDUSD": 1, "USDCAD": -1, "USDJPY": -1}   # the side that sells USD
LONDON = ZoneInfo("Europe/London")


def _m1_close_before(symbol: str, ms: int) -> float:
    m = _m1(symbol)
    k = int(np.searchsorted(m["ts"], ms, side="left")) - 1
    return float(m["c"][k]) if k >= 0 else NAN


def month_end_fix(ctx: Ctx) -> None:
    """MEF: on the last business day of the month, 10:00 -> 16:00 London, sell USD if US30 beat DE40 (in USD)
    over the month to date, else buy it; SL 2 x ATR20(H1)."""
    b = ctx.bars(60)
    a = atr_sma(b.h, b.l, b.c, 20)
    side0 = MEF_SIDE[ctx.ch.symbol]
    d0 = datetime.fromtimestamp(ctx.ch.lo_ms / 1000, timezone.utc).date() - timedelta(days=40)
    d1 = datetime.fromtimestamp(ctx.ch.hi_ms / 1000, timezone.utc).date()
    y, m, its = d0.year, d0.month, []
    while (y, m) <= (d1.year, d1.month):
        nxt = date(y + (m == 12), m % 12 + 1, 1)
        d = nxt - timedelta(days=1)
        while d.weekday() >= 5:
            d -= timedelta(days=1)
        at = int(datetime.combine(d, time(10, 0), LONDON).timestamp() * 1000)
        ex = int(datetime.combine(d, time(16, 0), LONDON).timestamp() * 1000)
        start = int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000)
        us = _m1_close_before("US30", at) / _m1_close_before("US30", start) - 1
        de = (_m1_close_before("DE40", at) * _m1_close_before("EURUSD", at)
              / (_m1_close_before("DE40", start) * _m1_close_before("EURUSD", start)) - 1)
        k = int(np.searchsorted(b.close_time, at, side="right")) - 1
        if math.isfinite(us) and math.isfinite(de) and us != de and k >= 20 and math.isfinite(a[k]):
            its.append(Intent(at, side0 if us > de else -side0, 2.0 * a[k], exit_ms=ex))
        y, m = nxt.year, nxt.month
    run_intents(ctx, its)


WF_HORIZON = 4


def _wf_features(b):
    """research/scan/wf.py's 14 causal features at each bar close and the target (C[i+4] - C[i]) / ATR20."""
    c = b.c
    a20, a5 = atr_sma(b.h, b.l, c, 20), atr_sma(b.h, b.l, c, 5)
    n_ticks = (b.event_tick - b.first_tick).astype(float)
    F = {}
    for k in (1, 4, 16, 64):
        r = np.full(len(c), np.nan)
        r[k:] = (c[k:] - c[:-k]) / a20[k:]
        F[f"r{k}"] = r
    hh, ll = np.full(len(c), np.nan), np.full(len(c), np.nan)
    if len(c) >= 20:
        hh[19:], ll[19:] = sliding_window_view(b.h, 20).max(axis=1), sliding_window_view(b.l, 20).min(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        F["rangepos"] = (c - ll) / (hh - ll) - 0.5
        F["volratio"] = a5 / a20 - 1
        F["body"] = (c - b.o) / (b.h - b.l)
        F["ema"] = (c - ema(c, 50)) / a20
        F["rsi"] = rsi(c, 14) / 50 - 1
        act = n_ticks / np.convolve(np.r_[np.full(95, n_ticks[:96].mean()), n_ticks], np.ones(96) / 96, "valid") - 1
    F["act"] = act
    F["r1xact"] = F["r1"] * act
    F["shock"] = np.sign(F["r1"]) * (np.abs(F["r1"]) > 2)
    hour = (b.open_time // 3_600_000) % 24
    F["sinh"], F["cosh"] = np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)
    y = np.full(len(c), np.nan)
    y[:-WF_HORIZON] = (c[WF_HORIZON:] - c[:-WF_HORIZON]) / a20[:-WF_HORIZON]
    return np.column_stack(list(F.values())), y, a20


def _month(ms) -> np.ndarray:
    return np.asarray(ms, np.int64).astype("datetime64[ms]").astype("datetime64[M]").astype(np.int64)


def walk_forward_ridge(ctx: Ctx, tf: int = 15, train_months: int = 6, lam: float = 0.1, q: float = 0.9,
                       SLK: float = 2.0) -> None:
    """WF1: ridge on the standardized features, refit every month on the 6 months before it; trade |pred|
    above the training months' q-quantile in the direction of the prediction, SL 2 x ATR20, exit after 4 bars."""
    b = ctx.bars(tf)
    X, y, a = _wf_features(b)
    mon = _month(b.open_time)
    finite = np.all(np.isfinite(X), axis=1)
    pred, thr = np.full(len(y), np.nan), np.full(len(y), np.nan)
    for M in range(int(_month(ctx.ch.lo_ms)), int(_month(ctx.ch.hi_ms - 1)) + 1):
        tr = (mon >= M - train_months) & (mon < M)
        idx = np.flatnonzero(tr)
        if idx.size:
            tr[idx[-WF_HORIZON:]] = False              # their labels reach into month M
        ok = tr & finite & np.isfinite(y)
        if ok.sum() < 500:
            continue
        mu, sd = X[ok].mean(0), X[ok].std(0) + 1e-12
        Z = (X[ok] - mu) / sd
        yt = np.clip(y[ok], -5, 5)
        w = np.linalg.solve(Z.T @ Z + lam * ok.sum() * np.eye(Z.shape[1]), Z.T @ (yt - yt.mean()))
        te = (mon == M) & finite
        pred[te] = ((X[te] - mu) / sd) @ w + yt.mean()
        thr[te] = np.quantile(np.abs(Z @ w + yt.mean()), q)
    with np.errstate(invalid="ignore"):
        sig = np.where(np.abs(pred) > thr, np.sign(pred), 0).astype(int)
    n = len(b)
    run_intents(ctx, [Intent(int(b.close_time[i]), int(sig[i]), SLK * a[i], NAN,
                             int(b.close_time[min(i + WF_HORIZON, n - 1)]))
                      for i in np.flatnonzero(sig) if math.isfinite(a[i]) and a[i] > 0])
