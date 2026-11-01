"""
Basis B demo: the registered rule k100_H24_cheap, as pure functions (no I/O). The runner (app/basis_b_runner.py) feeds
it Binance klines, books and borrow data; app/basis_b_store.py keeps the trades. docs/basis-b-demo.md has the rule,
the demo terms and what differs from the research code.

Registered in research/results/portfolio/round63_parallel/B/PREREG_B_cheap_basis.md (frozen 2026-10-31 15:25 UTC),
research code research/results/portfolio/round63_parallel/B/code/{universe.py,basis.py}:
- Universe of day D: top-60 Binance USDT-M perps by mean perp quote volume over the 30 UTC days ending D-1, perp
  listed >= 60 days, Binance spot pair trading, stablecoins / BTCDOM / PAXG excluded before ranking; BTC and ETH keep
  their rank but are not traded. An hour of day D uses the universe of day D-1.
- Hourly basis b = ln(perp close / (factor x spot close)) on a valid bar (>= 20 trades on both legs, relative tick
  <= 5 bp on both legs); reference m_h = median of b over the previous 168 hours (>= 120 valid).
- Event: b_h - m_h < -100 bp at the close of hour h -> long perp, short spot (margin borrow) at the open of h+1, one
  open trade per coin. Exit at the open after the first close c >= h+1 with b_c - m_h >= (b_h - m_h) / 2, else at
  the open of h+25.
- Net per unit notional: perp return - spot return - funding paid on stamps in (entry, exit] - 30 bp fees
  - 4 x half-spread (3 bp for universe rank < 10, else 5 bp) - borrow 40 %/yr - cash rate, both pro rata.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

H_MS = 3_600_000
DAY_MS = 86_400_000

TOP_N = 60
MIN_AGE_DAYS = 60
VOLUME_DAYS = 30
STABLE = {"USDC", "BUSD", "TUSD", "USDP", "FDUSD", "DAI", "EUR", "GBP", "AEUR", "USDE", "PAXG", "BTCDOM"}
NOT_TRADED = {"BTCUSDT", "ETHUSDT"}

MIN_TRADES = 20
MAX_TICK = 0.0005
WIN, WIN_MIN = 168, 120
K = 0.0100                      # entry threshold, 100 bp below the reference
MAX_HOLD_H = 24

FEES = 0.0030                   # round trip, both legs, taker
BORROW_Y = 0.40                 # registered borrow assumption, per year
HOURS_PER_YEAR = 8760.0


def spot_name(perp: str) -> Tuple[str, float]:
    """Perp symbol -> (spot symbol, factor) with perp price = factor x spot price (1000PEPEUSDT -> PEPEUSDT, 1000)."""
    for pre, fac in (("1000000", 1e6), ("1000", 1e3), ("1M", 1e6)):
        rest = perp[len(pre):]
        if perp.startswith(pre) and rest and not rest[0].isdigit():
            return rest, fac
    return perp, 1.0


def half_spread(rank: int) -> float:
    return 0.0003 if rank < 10 else 0.0005


# ---------------------------------------------------------------------------------------------------------- universe

@dataclass(frozen=True)
class Listing:
    perp: str
    spot: str
    factor: float
    onboard_ms: int                     # perp listing time (exchangeInfo onboardDate)


def eligible(perp: str, spot_trading: Iterable[str]) -> Optional[Tuple[str, float]]:
    """(spot, factor) when the perp can enter the ranking: USDT-quoted, not a stablecoin, spot pair trading."""
    if not perp.endswith("USDT"):
        return None
    spot, fac = spot_name(perp)
    if spot[:-4] in STABLE or perp[:-4] in STABLE or spot not in set(spot_trading):
        return None
    return spot, fac


def rank_universe(day_ms: int, listings: Sequence[Listing], daily_qv: Dict[str, Dict[int, float]]
                  ) -> List[Tuple[Listing, int]]:
    """Universe of day `day_ms` (UTC midnight): [(listing, rank)] for the top 60, best first. `daily_qv[perp]` maps
    a UTC day start (ms) to that day's perp quote volume. Ranked on days D-30..D-1; D-1 must have traded (as in
    universe.py, which ranks day D-1 with the trailing mean including that day and needs >= 15 valid days)."""
    last = day_ms - DAY_MS
    scored = []
    for li in listings:
        q = daily_qv.get(li.perp, {})
        if last not in q:
            continue
        if (last - li.onboard_ms) < MIN_AGE_DAYS * DAY_MS:
            continue
        vals = [q[d] for d in range(last - (VOLUME_DAYS - 1) * DAY_MS, last + 1, DAY_MS) if d in q]
        if len(vals) < VOLUME_DAYS / 2:
            continue
        scored.append((sum(vals) / len(vals), li.perp, li))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [(li, r) for r, (_, _, li) in enumerate(scored[:TOP_N])]


# ------------------------------------------------------------------------------------------------------------ basis

@dataclass(frozen=True)
class Bar:
    open_ms: int
    open: float
    close: float
    trades: int


def basis_series(perp: Sequence[Bar], spot: Sequence[Bar], factor: float, tick_perp: float, tick_spot: float
                 ) -> Dict[int, Optional[float]]:
    """{hour open ms: b or None} over the hours both legs have a bar. tick_* = price tick / recent price (the live
    stand-in for the research's inferred 30-day relative tick)."""
    sp = {b.open_ms: b for b in spot}
    out: Dict[int, Optional[float]] = {}
    tick_ok = tick_perp <= MAX_TICK and tick_spot <= MAX_TICK
    for f in perp:
        s = sp.get(f.open_ms)
        if s is None:
            continue
        ok = tick_ok and f.trades >= MIN_TRADES and s.trades >= MIN_TRADES and f.close > 0 and s.close > 0
        out[f.open_ms] = math.log(f.close / (factor * s.close)) if ok else None
    return out


def reference(b: Dict[int, Optional[float]], hour_ms: int) -> Optional[float]:
    """m for hour `hour_ms`: median of the valid b over the previous 168 hours, None with fewer than 120."""
    vals = sorted(v for v in (b.get(hour_ms - k * H_MS) for k in range(1, WIN + 1)) if v is not None)
    if len(vals) < WIN_MIN:
        return None
    n = len(vals)
    return vals[n // 2] if n % 2 else 0.5 * (vals[n // 2 - 1] + vals[n // 2])


def deviation(b: Dict[int, Optional[float]], hour_ms: int) -> Optional[Tuple[float, float, float]]:
    """(b_h, m_h, d_h) at the close of hour `hour_ms`, None if either is missing."""
    bh = b.get(hour_ms)
    if bh is None:
        return None
    m = reference(b, hour_ms)
    if m is None:
        return None
    return bh, m, bh - m


def is_event(d: float) -> bool:
    return d < -K


def exit_due(b: Dict[int, Optional[float]], entry_ms: int, m_h: float, d_h: float, closed_through_ms: int
             ) -> Optional[Tuple[int, str]]:
    """(exit hour open ms, reason) once known from the bars closed through `closed_through_ms` (an hour open), else
    None. Reason 'half': first close c >= entry hour with b_c - m_h >= d_h / 2, exit at the open of c+1; '24h':
    no such close in the 24 hours, exit at the open of entry + 24 h."""
    last = min(closed_through_ms, entry_ms + (MAX_HOLD_H - 1) * H_MS)
    c = entry_ms
    while c <= last:
        v = b.get(c)
        if v is not None and v - m_h >= d_h / 2:
            return c + H_MS, "half"
        c += H_MS
    if closed_through_ms >= entry_ms + (MAX_HOLD_H - 1) * H_MS:
        return entry_ms + MAX_HOLD_H * H_MS, "24h"
    return None


# ------------------------------------------------------------------------------------------------------------ fills

def book_vwap(levels: Sequence[Tuple[float, float]], notional: float) -> Optional[Tuple[float, float]]:
    """(average price, filled share) for `notional` quote currency taken from book levels [(price, qty)] best first.
    Filled share < 1 when the shown book is too thin; None for an empty book."""
    if not levels or notional <= 0:
        return None
    left, cost, qty = notional, 0.0, 0.0
    for p, q in levels:
        take = min(left, p * q)
        cost += take
        qty += take / p
        left -= take
        if left <= 1e-12:
            break
    if qty <= 0:
        return None
    return cost / qty, (notional - max(left, 0.0)) / notional


def spread_bp(bids: Sequence[Tuple[float, float]], asks: Sequence[Tuple[float, float]]) -> Optional[float]:
    if not bids or not asks:
        return None
    mid = 0.5 * (bids[0][0] + asks[0][0])
    return (asks[0][0] - bids[0][0]) / mid * 1e4 if mid > 0 else None


# -------------------------------------------------------------------------------------------------------------- net

def funding_paid(stamps: Iterable[Tuple[int, float]], entry_ms: int, exit_ms: int) -> float:
    """Sum of funding rates the long perp pays on stamps whose hour falls in (entry, exit] (the research rounds each
    stamp to the hour). Negative = received."""
    tot = 0.0
    for t, r in stamps:
        hour = int(round(t / H_MS)) * H_MS
        if entry_ms < hour <= exit_ms:
            tot += r
    return tot


def net(perp_in: float, perp_out: float, spot_in: float, spot_out: float, funding: float, hours: float,
        cash_y: float, borrow_y: float = BORROW_Y, spread_cost: float = 0.0) -> Dict[str, float]:
    """Components per unit notional of a long-perp / short-spot trade. Spot prices may be raw (the factor cancels).
    `spread_cost` is the registered 4 x half-spread for open prices; 0 for book prices, which already pay it."""
    price = (perp_out / perp_in - 1.0) - (spot_out / spot_in - 1.0)
    carry = (cash_y + borrow_y) * hours / HOURS_PER_YEAR
    cost = FEES + spread_cost
    return {"price": price, "fund": -funding, "cost": cost, "carry": carry,
            "net": price - funding - cost - carry}


# ----------------------------------------------------------------------------------------------- status arithmetic

def sd_from_t(mean: float, n: int, t: float) -> float:
    return abs(mean) * math.sqrt(n) / t


def pooled_t(n0: int, mean0: float, sd0: float, xs: Sequence[float]) -> Optional[float]:
    """t of the mean of a sample known by (n0, mean0, sd0) joined with the trades xs (independent trades)."""
    n1 = len(xs)
    n = n0 + n1
    if n < 3:
        return None
    s1 = sum(xs)
    mean = (n0 * mean0 + s1) / n
    ss = (n0 - 1) * sd0 ** 2 + n0 * (mean0 - mean) ** 2 + sum((x - mean) ** 2 for x in xs)
    sd = math.sqrt(ss / (n - 1))
    return mean / (sd / math.sqrt(n)) if sd > 0 else None
