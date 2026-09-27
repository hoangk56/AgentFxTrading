"""Tick chunks for the lab: real ticks, synthetic crosses from USD legs, mirrored prices and week-shuffled
histories. A chunk is one calendar year plus a warm-up before it and a tail after it; entries are allowed only
inside the year, the tail only finishes positions opened in it."""
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache
from typing import Optional

import numpy as np

from research.lab.universe import SYNTH_SPREAD_FACTOR, Instrument, instrument
from research.m1 import load as load_m1
from research.ticks import Ticks, day_ms, load_ticks

DATA_START, DATA_END = date(2023, 1, 1), date(2026, 9, 24)
YEARS = (2023, 2024, 2025, 2026)
WARMUP_DAYS, TAIL_DAYS = 190, 45
DAY_MS, WEEK_MS = 86_400_000, 7 * 86_400_000
SAT0_MS = 2 * DAY_MS                   # 1970-01-03 00:00 UTC is a Saturday: lab weeks run Sat -> Sat


def year_span(year: int):
    return date(year, 1, 1), min(date(year, 12, 31), DATA_END)


@dataclass
class Chunk:
    symbol: str
    variant: str
    year: int
    t: Ticks
    lo_ms: int          # entries allowed from ...
    hi_ms: int          # ... until (exclusive)
    inst: Instrument


def _empty() -> Ticks:
    return Ticks(np.empty(0, np.int64), np.empty(0), np.empty(0))


def cross_ticks(ta: Ticks, tb: Ticks, op: str, spread_factor: float = 1.0) -> Ticks:
    """As-of join of two legs on the union of their tick times. mul: bid = bidA x bidB, ask = askA x askB;
    div: bid = bidA / askB, ask = askA / bidB. spread_factor scales the half-spread around the mid."""
    if len(ta) == 0 or len(tb) == 0:
        return _empty()
    ts = np.union1d(ta.ts, tb.ts)
    ia = np.searchsorted(ta.ts, ts, side="right") - 1
    ib = np.searchsorted(tb.ts, ts, side="right") - 1
    ok = (ia >= 0) & (ib >= 0)
    ts, ia, ib = ts[ok], ia[ok], ib[ok]
    if op == "mul":
        bid, ask = ta.bid[ia] * tb.bid[ib], ta.ask[ia] * tb.ask[ib]
    else:
        bid, ask = ta.bid[ia] / tb.ask[ib], ta.ask[ia] / tb.bid[ib]
    if spread_factor != 1.0:
        mid, half = (bid + ask) / 2.0, (ask - bid) / 2.0 * spread_factor
        bid, ask = mid - half, mid + half
    return Ticks(ts, bid, ask)


def real_ticks(symbol: str, a: date, b: date) -> Ticks:
    inst = instrument(symbol)
    if not inst.synthetic:
        return load_ticks(symbol, a, b)
    leg_a, leg_b, op = inst.cross
    return cross_ticks(load_ticks(leg_a, a, b), load_ticks(leg_b, a, b), op, SYNTH_SPREAD_FACTOR)


@lru_cache(maxsize=None)
def mirror_k(symbol: str) -> float:
    """K of p' = K / p: the square of the symbol's first M1 close, so the mirror starts at the real level."""
    return float(load_m1(symbol)["c"][0]) ** 2


def mirror(t: Ticks, k: float) -> Ticks:
    """Prices reflected in log space: up-moves become down-moves; the new bid is K / ask."""
    return Ticks(t.ts, k / t.ask, k / t.bid)


def week_of(ms):
    return (np.asarray(ms) - SAT0_MS) // WEEK_MS


class WeekShuffle:
    """The symbol's weeks (Sat 00:00 UTC -> Sat) permuted with a seed. Target slot k (the k-th week with data)
    receives source week src[k], shifted by whole weeks into the slot (weekday and hour kept) and scaled so
    that it opens at the previous slot's close times the source week's own weekend gap."""

    def __init__(self, symbol: str, seed: int):
        m = load_m1(symbol)
        w = week_of(m["ts"])
        starts = np.flatnonzero(np.r_[True, w[1:] != w[:-1]])
        ends = np.r_[starts[1:], len(w)] - 1
        first, last = m["o"][starts], m["c"][ends]
        gap = np.r_[1.0, first[1:] / last[:-1]]
        self.symbol = symbol
        self.weeks = w[starts]
        self.src = np.random.default_rng(seed).permutation(len(self.weeks))
        self.scale = np.empty(len(self.src))
        self.scale[0] = first[0] / first[self.src[0]]
        for k in range(1, len(self.src)):
            opening = self.scale[k - 1] * last[self.src[k - 1]] * gap[self.src[k]]
            self.scale[k] = opening / first[self.src[k]]

    def ticks(self, a: date, b: date) -> Ticks:
        lo, hi = day_ms(a), day_ms(b) + DAY_MS
        parts = []
        for k in np.flatnonzero((self.weeks >= week_of(lo)) & (self.weeks <= week_of(hi - 1))):
            s = int(self.weeks[self.src[k]])
            s0 = date(1970, 1, 3) + timedelta(weeks=s)
            t = load_ticks(self.symbol, s0, s0 + timedelta(days=6))
            if len(t):
                parts.append((t.ts + (int(self.weeks[k]) - s) * WEEK_MS, t.bid * self.scale[k], t.ask * self.scale[k]))
        if not parts:
            return _empty()
        ts = np.concatenate([p[0] for p in parts])
        keep = (ts >= lo) & (ts < hi)
        return Ticks(ts[keep], np.concatenate([p[1] for p in parts])[keep], np.concatenate([p[2] for p in parts])[keep])


@lru_cache(maxsize=32)
def shuffler(symbol: str, seed: int) -> WeekShuffle:
    return WeekShuffle(symbol, seed)


def load_chunk(symbol: str, variant: str, year: int, warmup_days: int = WARMUP_DAYS,
               tail_days: int = TAIL_DAYS) -> Optional[Chunk]:
    """None when the symbol has no tick inside the year."""
    a0, b0 = year_span(year)
    a, b = a0 - timedelta(days=warmup_days), min(b0 + timedelta(days=tail_days), DATA_END)
    inst = instrument(symbol)
    if variant == "real":
        t = real_ticks(symbol, a, b)
    elif variant == "mirror":
        t, inst = mirror(real_ticks(symbol, a, b), mirror_k(symbol)), inst.mirrored()
    elif variant.startswith("shuffle:"):
        t = shuffler(symbol, int(variant.split(":", 1)[1])).ticks(a, b)
    else:
        raise ValueError(f"unknown variant {variant}")
    lo, hi = day_ms(a0), day_ms(b0) + DAY_MS
    if len(t) == 0 or not np.any((t.ts >= lo) & (t.ts < hi)):
        return None
    return Chunk(symbol, variant, year, t, lo, hi, inst)
