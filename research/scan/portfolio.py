"""Portfolio-cap swing lab: a single bot trading up to `CAP` symbols at once, max hold 5 days.

Every family scores all 15 real symbols at every shared bar-close epoch (D1/H4 buckets align across symbols).
A bot with free slots admits the strongest fresh signals first (causal: only the current epoch's scores are
used, no lookahead), never doubles up on a symbol it already holds, and force-exits at the earliest of SL, TP
or 5 calendar days.

Sizing is capital-independent but not frozen: every trade risks BASE_RISK_USD (a constant dollar amount, never
a function of account equity) times a 0.5x-2x multiplier off the *default* lot, set by how strong this signal
is relative to this same rule's own past signals on this symbol (a causal expanding median -- only strengths
seen strictly before this trade, so there is no lookahead). $ = r-multiple x that trade's risk-in-USD.

  research/.venv/bin/python -m research.scan.portfolio [mom|brk|mrv|trd|sqz|all] [--cap N]
"""
import argparse
import csv
import datetime
import math
from dataclasses import dataclass
from functools import lru_cache
from itertools import groupby
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from numpy.lib.stride_tricks import sliding_window_view

from research.indicators import atr_sma, rsi, prior_max, prior_min, ema, bollinger, adx
from research.m1bars import resample
from research.scan.engine import Order, simulate, period_of, PERIODS
from research.m1 import load as _load_m1

_load = lru_cache(maxsize=None)(_load_m1)


def load(symbol: str) -> dict:
    return _load(symbol)


@lru_cache(maxsize=None)
def _bars(symbol: str, tf: int, offset: int):
    m = load(symbol)
    b = resample(m, tf, offset)
    a = atr_sma(b.h, b.l, b.c, 20)
    return b, a

DAY_MS = 86_400_000
HOLD_MS = 5 * DAY_MS
CAP = 3
BASE_RISK_USD = 100.0          # the "default lot": $ risked per trade at scale 1.0x, never a function of equity
SCALE_MIN, SCALE_MAX = 0.5, 2.0
SCALE_MIN_HISTORY = 10          # signals needed before scaling kicks in; before that every trade is 1.0x
SYMBOLS = ["AUDJPY", "AUDUSD", "BTCUSD", "DE40", "ETHUSD", "EURJPY", "EURUSD", "GBPJPY", "GBPUSD",
           "UK100", "US30", "USDCAD", "USDJPY", "USTEC", "XAUUSD",
           "NZDUSD", "USDCHF", "US500", "JP225", "AUS200", "HK50",
           "XAGUSD", "XPTUSD", "XTIUSD", "XBRUSD", "XNGUSD"]
YEARS = tuple(range(2016, 2027))
RNG_SEEDS = 20


@dataclass
class Cand:
    symbol: str
    k: int
    ts: int
    side: int
    sl: float
    tp: Optional[float]
    k_end: int
    strength: float
    risk_usd: float


def _year(ms: int) -> int:
    import datetime
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).year


def _causal_scale(strengths: List[float]) -> List[float]:
    """Size multiplier vs. the default lot: strength / the expanding median of this same signal's own earlier
    occurrences (>= SCALE_MIN_HISTORY samples; 1.0x before that), clipped to [SCALE_MIN, SCALE_MAX]. Only ever
    looks at strengths that occurred strictly earlier in this list -- no lookahead, no dependence on equity."""
    out = []
    hist: List[float] = []
    for s in strengths:
        scale = 1.0
        if len(hist) >= SCALE_MIN_HISTORY:
            ref = float(np.median(hist))
            if ref > 0:
                scale = float(np.clip(s / ref, SCALE_MIN, SCALE_MAX))
        out.append(scale)
        hist.append(float(s))
    return out


def _make_cands(symbol: str, m: dict, b, a: np.ndarray, side: np.ndarray, strength: np.ndarray,
                 SLK: float, TPK: Optional[float], warm: int = 25) -> List[Cand]:
    n = len(b)
    ts_arr = m["ts"]
    idxs = []
    for i in np.flatnonzero(side != 0):
        if i < warm or i >= n or not np.isfinite(a[i]) or a[i] <= 0:
            continue
        k = int(b.last[i]) + 1
        if k <= 0 or k >= len(ts_arr) - 1:
            continue
        idxs.append((i, k))
    scales = _causal_scale([float(strength[i]) for i, _ in idxs])
    out = []
    for (i, k), scale in zip(idxs, scales):
        s = int(side[i])
        ref = float(b.c[i])
        sl = ref - s * SLK * a[i]
        tp = ref + s * TPK * a[i] if TPK else None
        deadline = int(ts_arr[k]) + HOLD_MS
        j = int(np.searchsorted(ts_arr, deadline, side="right")) - 1
        j = max(k, min(j, len(ts_arr) - 1))
        out.append(Cand(symbol, k, int(ts_arr[k]), s, sl, tp, j, float(strength[i]), BASE_RISK_USD * scale))
    return out


def _fills_for(m: dict, symbol: str, cands: List[Cand]) -> Dict[int, "object"]:
    orders = [Order(c.k, c.side, c.sl, c.k_end, tp=c.tp) for c in cands]
    fs = simulate(m, symbol, orders, one_at_a_time=False)
    return {f.t_in: f for f in fs}   # t_in is unique per (symbol, k) since k -> one M1 timestamp


def admit(cands_by_symbol: Dict[str, Tuple[dict, List[Cand]]], cap: int = CAP):
    """Causal admission: process shared epochs in time order, free expired slots, rank fresh signals by
    strength, fill up to `cap` free slots, never two open positions in the same symbol."""
    fills_by_key: Dict[Tuple[str, int], object] = {}
    all_c: List[Cand] = []
    for sym, (m, cands) in cands_by_symbol.items():
        fmap = _fills_for(m, sym, cands)
        for c in cands:
            f = fmap.get(int(m["ts"][c.k]))
            if f is None:
                continue
            fills_by_key[(sym, c.k)] = f
            all_c.append(c)
    all_c.sort(key=lambda c: c.ts)

    active: Dict[str, int] = {}   # symbol -> exit ts
    admitted = []
    for ts, group in groupby(all_c, key=lambda c: c.ts):
        for sym in [s for s, t in active.items() if t <= ts]:
            del active[sym]
        avail = cap - len(active)
        if avail <= 0:
            continue
        grp = sorted((c for c in group if c.symbol not in active), key=lambda c: -c.strength)
        for c in grp[:avail]:
            f = fills_by_key[(sym := c.symbol, c.k)]
            active[sym] = f.t_out
            admitted.append((c, f))
    return admitted


def usd(c: Cand, f) -> float:
    return f.r * c.risk_usd


# ---------------------------------------------------------------- strategy families
def sig_mom(b, a, N=20, Zmin=1.0):
    """Cross-sectional momentum: N-bar return / ATR20, follow when beyond Zmin."""
    n = len(b)
    z = np.full(n, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        z[N:] = (b.c[N:] - b.c[:-N]) / a[N:]
    side = np.where(z > Zmin, 1, np.where(z < -Zmin, -1, 0))
    return side, np.nan_to_num(np.abs(z))


def sig_brk(b, a, N=20):
    """Donchian(N) breakout, strength = overshoot beyond the level in ATR units."""
    hh, ll = prior_max(b.h, N), prior_min(b.l, N)
    with np.errstate(invalid="ignore"):
        up, dn = b.c > hh, b.c < ll
    prev_up, prev_dn = np.r_[False, up[:-1]], np.r_[False, dn[:-1]]
    side = np.where(up & ~prev_up, 1, np.where(dn & ~prev_dn, -1, 0))
    with np.errstate(invalid="ignore"):
        strength = np.where(side > 0, (b.c - hh) / a, np.where(side < 0, (ll - b.c) / a, 0.0))
    return side, np.nan_to_num(np.abs(strength))


def sig_mrv(b, a, P=2, lo=5.0):
    """RSI(P) extreme fade, strength = distance past the extreme."""
    r = rsi(b.c, P)
    side = np.where(r < lo, 1, np.where(r > 100 - lo, -1, 0))
    strength = np.where(r < lo, lo - r, np.where(r > 100 - lo, r - (100 - lo), 0.0))
    return side, np.nan_to_num(strength)


def sig_trd(b, a, fast=20, slow=100, pull=10):
    """Trend (EMA fast vs slow) + pullback to the fast EMA, strength = trend separation in ATR."""
    ef, es = ema(b.c, fast), ema(b.c, slow)
    ep = ema(b.c, pull)
    up_trend, dn_trend = ef > es, ef < es
    cross_up = (b.c > ep) & (np.r_[True, b.c[:-1] <= ep[:-1]])
    cross_dn = (b.c < ep) & (np.r_[True, b.c[:-1] >= ep[:-1]])
    side = np.where(up_trend & cross_up, 1, np.where(dn_trend & cross_dn, -1, 0))
    with np.errstate(invalid="ignore"):
        strength = np.abs(ef - es) / a
    return side, np.nan_to_num(strength)


def sig_sqz(b, a, N=20, K=2.0, look=100, pct=20.0):
    """Bollinger(N, K) width at a `pct`-percentile `look`-bar low (a squeeze), then a close beyond the band."""
    lo, mid, hi = bollinger(b.c, N, K)
    n = len(b)
    with np.errstate(invalid="ignore", divide="ignore"):
        width = (hi - lo) / mid
    thresh = np.full(n, np.nan)
    if n > look:
        windows = sliding_window_view(width, look)[:-1]
        with np.errstate(invalid="ignore"):
            thresh[look:] = np.nanpercentile(windows, pct, axis=1)
    squeezed = width <= thresh
    with np.errstate(invalid="ignore"):
        up, dn = b.c > hi, b.c < lo
    prev_up, prev_dn = np.r_[False, up[:-1]], np.r_[False, dn[:-1]]
    prev_sqz = np.r_[False, squeezed[:-1]]
    side = np.where(up & ~prev_up & prev_sqz, 1, np.where(dn & ~prev_dn & prev_sqz, -1, 0))
    with np.errstate(invalid="ignore"):
        strength = np.abs((b.c - mid) / a)
    return side, np.nan_to_num(strength)


def sig_trendbrk(b, a, N=20, ema_fast=20, ema_slow=100):
    """Donchian(N) breakout (as sig_brk) taken only in the direction of the EMA(fast) vs EMA(slow) trend --
    meant to cut the whipsaws a bare breakout takes in a range."""
    hh, ll = prior_max(b.h, N), prior_min(b.l, N)
    ef, es = ema(b.c, ema_fast), ema(b.c, ema_slow)
    with np.errstate(invalid="ignore"):
        up, dn = b.c > hh, b.c < ll
    prev_up, prev_dn = np.r_[False, up[:-1]], np.r_[False, dn[:-1]]
    trend_up, trend_dn = ef > es, ef < es
    side = np.where(up & ~prev_up & trend_up, 1, np.where(dn & ~prev_dn & trend_dn, -1, 0))
    with np.errstate(invalid="ignore"):
        strength = np.where(side > 0, (b.c - hh) / a, np.where(side < 0, (ll - b.c) / a, 0.0))
    return side, np.nan_to_num(np.abs(strength))


def sig_sqz_trend(b, a, N=20, K=2.0, look=100, pct=20.0, ema_fast=20, ema_slow=100):
    """Bollinger squeeze breakout (as sig_sqz) taken only with the EMA(fast) vs EMA(slow) trend."""
    lo, mid, hi = bollinger(b.c, N, K)
    n = len(b)
    with np.errstate(invalid="ignore", divide="ignore"):
        width = (hi - lo) / mid
    thresh = np.full(n, np.nan)
    if n > look:
        windows = sliding_window_view(width, look)[:-1]
        with np.errstate(invalid="ignore"):
            thresh[look:] = np.nanpercentile(windows, pct, axis=1)
    squeezed = width <= thresh
    with np.errstate(invalid="ignore"):
        up, dn = b.c > hi, b.c < lo
    prev_up, prev_dn = np.r_[False, up[:-1]], np.r_[False, dn[:-1]]
    prev_sqz = np.r_[False, squeezed[:-1]]
    ef, es = ema(b.c, ema_fast), ema(b.c, ema_slow)
    trend_up, trend_dn = ef > es, ef < es
    side = np.where(up & ~prev_up & prev_sqz & trend_up, 1,
                     np.where(dn & ~prev_dn & prev_sqz & trend_dn, -1, 0))
    with np.errstate(invalid="ignore"):
        strength = np.abs((b.c - mid) / a)
    return side, np.nan_to_num(strength)


def sig_range_fade(b, a, N=20, zmax=1.0, adx_max=20.0):
    """Fade a pullback from EMA(N) (|z| > zmax, z = distance in ATR) only when ADX says the market is NOT
    trending (adx < adx_max) -- a regime-filtered mean reversion, distinct from the RSI(2) fade of sig_mrv."""
    e = ema(b.c, N)
    ad = adx(b.h, b.l, b.c, 14)
    with np.errstate(invalid="ignore"):
        z = (b.c - e) / a
    long_ok = (z < -zmax) & (ad < adx_max)
    short_ok = (z > zmax) & (ad < adx_max)
    side = np.where(long_ok, 1, np.where(short_ok, -1, 0))
    return side, np.nan_to_num(np.abs(z))


def sig_tom(b, a, before=1):
    """Turn-of-month: one long entry `before` trading days ahead of each month end (classic equity-index
    seasonal drift); the exit is the family's usual SL/TP/5-day cap, not a fixed calendar exit."""
    n = len(b)
    dt = [datetime.datetime.fromtimestamp(int(x) / 1000, datetime.timezone.utc) for x in b.t]
    month = np.array([d.month for d in dt])
    is_new_month = np.r_[True, month[1:] != month[:-1]]
    start_idx = np.flatnonzero(is_new_month)
    side = np.zeros(n, dtype=int)
    for si in start_idx:
        i = max(si - before, 0)
        if i < n:
            side[i] = 1
    return side, np.where(side != 0, 1.0, 0.0)


FAMILIES = {
    "mom": dict(tf=1440, offset=120, fn=sig_mom, SLK=2.5, TPK=None, kw=dict(N=20, Zmin=1.0)),
    "brk": dict(tf=240, offset=0, fn=sig_brk, SLK=1.5, TPK=2.5, kw=dict(N=20)),
    "mrv": dict(tf=1440, offset=120, fn=sig_mrv, SLK=1.5, TPK=1.0, kw=dict(P=2, lo=5.0)),
    "trd": dict(tf=1440, offset=120, fn=sig_trd, SLK=2.0, TPK=None, kw=dict(fast=20, slow=100, pull=10)),
    "sqz": dict(tf=240, offset=0, fn=sig_sqz, SLK=1.5, TPK=2.5, kw=dict(N=20, K=2.0, look=100, pct=20.0)),
    "trendbrk": dict(tf=240, offset=0, fn=sig_trendbrk, SLK=1.5, TPK=2.5, kw=dict(N=20, ema_fast=20, ema_slow=100)),
    "sqztrend": dict(tf=240, offset=0, fn=sig_sqz_trend, SLK=1.5, TPK=2.5,
                     kw=dict(N=20, K=2.0, look=100, pct=20.0, ema_fast=20, ema_slow=100)),
    "rangefade": dict(tf=1440, offset=120, fn=sig_range_fade, SLK=1.5, TPK=2.0, kw=dict(N=20, zmax=1.0, adx_max=20.0)),
    "tom": dict(tf=1440, offset=120, fn=sig_tom, SLK=2.5, TPK=None, kw=dict(before=1)),
}

# Symbol subsets for families whose theory only applies to a slice of the universe.
INDICES = ["DE40", "UK100", "US30", "USTEC", "US500", "JP225", "AUS200", "HK50"]
FAMILY_SYMBOLS: Dict[str, List[str]] = {"tom": INDICES}


def build_real_candidates(fam: dict, symbols=SYMBOLS) -> Dict[str, Tuple[dict, List[Cand]]]:
    out = {}
    for sym in symbols:
        m = load(sym)
        b, a = _bars(sym, fam["tf"], fam["offset"])
        side, strength = fam["fn"](b, a, **fam["kw"])
        out[sym] = (m, _make_cands(sym, m, b, a, side, strength, fam["SLK"], fam["TPK"]))
    return out


def build_random_candidates(fam: dict, n_by_symbol: Dict[str, int], rng: np.random.Generator,
                             symbols=SYMBOLS) -> Dict[str, Tuple[dict, List[Cand]]]:
    out = {}
    for sym in symbols:
        m = load(sym)
        b, a = _bars(sym, fam["tf"], fam["offset"])
        n_need = n_by_symbol.get(sym, 0)
        valid = np.flatnonzero(np.isfinite(a) & (a > 0))
        valid = valid[valid >= 25]
        if n_need <= 0 or len(valid) == 0:
            out[sym] = (m, [])
            continue
        idx = rng.choice(valid, size=min(n_need, len(valid)), replace=False)
        side = np.zeros(len(b), dtype=int)
        side[idx] = rng.choice([-1, 1], size=len(idx))
        strength = np.zeros(len(b))
        strength[idx] = rng.random(len(idx))
        out[sym] = (m, _make_cands(sym, m, b, a, side, strength, fam["SLK"], fam["TPK"]))
    return out


# ---------------------------------------------------------------- reporting
# In-sample / out-of-sample split for parameter selection (2026-09-27 26-symbol refresh): IS picks a config,
# OOS (never used to pick) confirms it. Independent of scan.engine.PERIODS, which is sized for the 2023-2026
# lab and would put nearly everything in one bucket over 2016-2026.
CUTOFF_MS = int(datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)


def era_of(ms: int) -> str:
    return "IS" if ms < CUTOFF_MS else "OOS"


def split_stats(rows: List[Tuple["Cand", "object", float]]) -> Dict[str, dict]:
    out = {}
    for era in ("IS", "OOS"):
        era_rows = [(c, f, u) for c, f, u in rows if era_of(f.t_in) == era]
        n, mu, t = _stats([f.r for _, f, _ in era_rows])
        net = sum(u for *_, u in era_rows)
        by_year: Dict[int, float] = {}
        for c, f, u in era_rows:
            by_year[_year(f.t_in)] = by_year.get(_year(f.t_in), 0.0) + u
        pos_years = sum(1 for v in by_year.values() if v > 0)
        out[era] = dict(n=n, mean_r=mu, t=t, net=net, years=len(by_year), pos_years=pos_years)
    return out


def _stats(rs: List[float]) -> Tuple[int, float, float]:
    n = len(rs)
    if n < 2:
        return n, (float(rs[0]) if n else 0.0), 0.0
    a = np.asarray(rs, float)
    sd = a.std(ddof=1)
    return n, float(a.mean()), float(a.mean() / (sd / math.sqrt(n))) if sd > 0 else 0.0


def report(name: str, admitted, cap: int) -> str:
    lines = [f"## {name} (cap {cap}, max hold 5 days, risk-scaled lots (0.5x-2x of $100 default))", ""]
    if not admitted:
        return "\n".join(lines + ["- no trades", ""]), dict(net=0.0, n=0, pos_every_year=False, strict_bar=False,
                                                              mean_r=float("nan"), t=0.0, max_dd=0.0, by_symbol={})
    rows = [(c, f, usd(c, f)) for c, f in admitted]
    rows.sort(key=lambda x: x[1].t_out)
    net_by_year = {y: 0.0 for y in YEARS}
    n_by_year = {y: 0 for y in YEARS}
    for c, f, u in rows:
        y = _year(f.t_in)
        if y in net_by_year:
            net_by_year[y] += u
            n_by_year[y] += 1
    total_net = sum(u for *_, u in rows)
    rs = [f.r for _, f, _ in rows]
    n, mu, t = _stats(rs)
    curve = np.cumsum([u for *_, u in rows])
    dd = float(np.max(np.maximum.accumulate(np.r_[0.0, curve]) - np.r_[0.0, curve]))
    wins = sum(1 for *_, u in rows if u > 0)
    win_rate = wins / n if n else float("nan")
    by_symbol: Dict[str, float] = {}
    for c, f, u in rows:
        by_symbol[c.symbol] = by_symbol.get(c.symbol, 0.0) + u
    lines.append(f"- trades {n}, net ${total_net:+,.0f}, win rate {win_rate:.0%}, mean R {mu:+.3f}, t {t:+.1f}, "
                 f"max DD ${dd:,.0f}")
    lines.append("- by year: " + ", ".join(f"{y} n{n_by_year[y]} ${net_by_year[y]:+,.0f}" for y in YEARS
                                            if n_by_year[y]))
    years_with_trades = [y for y in YEARS if n_by_year[y] > 0]
    pos_every_year = len(years_with_trades) >= 2 and all(net_by_year[y] > 0 for y in years_with_trades)
    per_period = {}
    for P in PERIODS:
        rr = [f.r for _, f, _ in rows if period_of(f.t_in) == P]
        pn, pmu, pt = _stats(rr)
        per_period[P] = (pn, pmu, pt)
    lines.append("- periods: " + " | ".join(f"{P} n{pn} R{pmu:+.3f} t{pt:+.1f}" for P, (pn, pmu, pt) in per_period.items()))
    strict_bar = all(pn >= 5 and pt >= 2.0 for pn, pmu, pt in per_period.values())
    lines.append(f"- by symbol net $: " + ", ".join(f"{s}:{v:+,.0f}" for s, v in sorted(by_symbol.items(), key=lambda kv: -kv[1])))
    lines.append(f"- flags: E(positive every year, >=2 yrs)={pos_every_year}  "
                 f"strict-t(t>=2 in every period with n>=5)={strict_bar}")
    return "\n".join(lines), dict(net=total_net, n=n, pos_every_year=pos_every_year, strict_bar=strict_bar,
                                   mean_r=mu, t=t, max_dd=dd, by_symbol=by_symbol)


def run_one(fam_name: str, cap: int = CAP, seeds: int = RNG_SEEDS, symbols=None) -> str:
    symbols = symbols or FAMILY_SYMBOLS.get(fam_name, SYMBOLS)
    fam = FAMILIES[fam_name]
    real_cands = build_real_candidates(fam, symbols)
    admitted = admit(real_cands, cap)
    text, summary = report(fam_name, admitted, cap)
    rows = [(c, f, usd(c, f)) for c, f in admitted]
    split = split_stats(rows)
    text += "\n- " + " | ".join(
        f"{era} n{d['n']} net${d['net']:+,.0f} R{d['mean_r']:+.3f} t{d['t']:+.1f} "
        f"pos-yrs {d['pos_years']}/{d['years']}" for era, d in split.items())
    n_by_symbol = {}
    for sym, (m, cands) in real_cands.items():
        n_by_symbol[sym] = sum(1 for c, f in admitted if c.symbol == sym)
    controls = []
    rng = np.random.default_rng(0)
    for _ in range(seeds):
        rc = build_random_candidates(fam, n_by_symbol, rng, symbols)
        a = admit(rc, cap)
        controls.append(sum(usd(c, f) for c, f in a))
    ctrl = np.asarray(controls)
    pct = float(np.mean(ctrl < summary["net"])) * 100.0 if len(ctrl) else float("nan")
    text += (f"\n- random-entry control ({seeds} seeds, same trade count/symbol, random side): "
             f"mean ${ctrl.mean():+,.0f}, real beats {pct:.0f}% of seeds "
             f"(pass bar >=95%): {'PASS' if pct >= 95 else 'fail'}")
    return text


def quick_eval(base_fam: str, cap: int = CAP, symbols=None, **overrides) -> dict:
    """Real-data only (no control), pooled + IS/OOS stats -- cheap enough to grid-search. IS (2016-2021) is
    for picking a config; OOS (2022-2026, `split_stats`) must never be used for that."""
    symbols = symbols or FAMILY_SYMBOLS.get(base_fam, SYMBOLS)
    fam = dict(FAMILIES[base_fam])
    fam["kw"] = dict(fam["kw"])
    for k, v in overrides.items():
        if k in ("SLK", "TPK"):
            fam[k] = v
        else:
            fam["kw"][k] = v
    real_cands = build_real_candidates(fam, symbols)
    admitted = admit(real_cands, cap)
    empty_split = dict(n=0, mean_r=float("nan"), t=0.0, net=0.0, years=0, pos_years=0)
    if not admitted:
        return dict(n=0, net=0.0, mean_r=float("nan"), t=0.0, pos_every_year=False, strict_bar=False,
                    IS=dict(empty_split), OOS=dict(empty_split))
    rows = [(c, f, usd(c, f)) for c, f in admitted]
    net = sum(u for *_, u in rows)
    n, mu, t = _stats([f.r for _, f, _ in rows])
    net_by_year: Dict[int, float] = {}
    for c, f, u in rows:
        net_by_year[_year(f.t_in)] = net_by_year.get(_year(f.t_in), 0.0) + u
    pos_every_year = len(net_by_year) >= 2 and all(v > 0 for v in net_by_year.values())
    per_period_t = []
    for P in PERIODS:
        rr = [f.r for _, f, _ in rows if period_of(f.t_in) == P]
        pn, _, pt = _stats(rr)
        per_period_t.append((pn, pt))
    strict_bar = all(pn >= 5 and pt >= 2.0 for pn, pt in per_period_t)
    split = split_stats(rows)
    return dict(n=n, net=net, mean_r=mu, t=t, pos_every_year=pos_every_year, strict_bar=strict_bar, **split)


def sweep(fam_name: str, grid: List[dict], cap: int = CAP, symbols=None, out_csv=None) -> List[dict]:
    """Prints IS-only columns (the ones a config should be picked on); OOS is in the returned rows for a
    separate, single confirmation look at whichever config IS picked -- never for picking itself."""
    rows = []
    for params in grid:
        r = quick_eval(fam_name, cap, symbols, **params)
        r = {**params, **r}
        rows.append(r)
        isr, oos = r["IS"], r["OOS"]
        print(f"  {params} -> IS n{isr['n']} net${isr['net']:+,.0f} R{isr['mean_r']:+.3f} t{isr['t']:+.1f} "
              f"yrs{isr['pos_years']}/{isr['years']}  ||  OOS n{oos['n']} net${oos['net']:+,.0f} "
              f"R{oos['mean_r']:+.3f} t{oos['t']:+.1f} yrs{oos['pos_years']}/{oos['years']}", flush=True)
    rows.sort(key=lambda r: -r["IS"]["net"])
    if out_csv:
        flat = [{**{k: v for k, v in r.items() if k not in ("IS", "OOS")},
                 **{f"IS_{k}": v for k, v in r["IS"].items()}, **{f"OOS_{k}": v for k, v in r["OOS"].items()}}
                for r in rows]
        with open(out_csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, list(flat[0].keys()))
            w.writeheader()
            w.writerows(flat)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("families", nargs="*", default=["all"])
    ap.add_argument("--cap", type=int, default=CAP)
    ap.add_argument("--seeds", type=int, default=RNG_SEEDS)
    args = ap.parse_args(argv)
    names = list(FAMILIES) if "all" in args.families else args.families
    out = [f"# Portfolio-cap swing lab (cap {args.cap}, hold <= 5 days, risk-scaled lots (0.5x-2x of $100 default))", ""]
    for name in names:
        print(f"== {name} ==", flush=True)
        text = run_one(name, args.cap, args.seeds)
        print(text, flush=True)
        out.append(text)
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    main()
