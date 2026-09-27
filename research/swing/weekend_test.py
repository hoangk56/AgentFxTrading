"""C1 Crypto Donchian vs the weekend closure (research/results/portfolio/crypto_donchian_weekend_2026-09-27.md).

IC's crypto was closed from Friday 17:00 to Sunday 17:05 New York time until April 2024 and trades 24/7 since.
T1 runs C1 unchanged on the 24/7 era twice: on the real M1 data and with that old closure cut out of it. T2 splits
the closed-weekend era's trades by whether the signal bar holds the weekend gap; T3 splits the 24/7 era's trades by
whether the signal bar closes on a weekend.

    python -m research.swing.weekend_test
"""
import datetime
from contextlib import contextmanager
from functools import lru_cache
from zoneinfo import ZoneInfo

import numpy as np

from research.swing import swing as S
from research.swing.swing_rules import donchian

SYMBOLS = ("BTCUSD", "ETHUSD")
C1 = dict(n=55, exit_n=20, shorts=True, slk=3.0)
ERA_247 = S._ms(2024, 5, 1)          # signal bars from here on: 24/7 market
ERA_CLOSED_END = S._ms(2024, 4, 1)   # signal bars before this: closed weekends
PHASES_MIN = (0, 60, 120, 180)
NY = ZoneInfo("America/New_York")
CLOSE_MIN, OPEN_MIN = 17 * 60, 17 * 60 + 5   # Friday 17:00 .. Sunday 17:05, New York
_m1_real = S.m1                              # weekends_closed() swaps S.m1 out


def ny_offset_ms(ts_ms: np.ndarray) -> np.ndarray:
    """UTC offset of New York (ms, negative) at each timestamp."""
    hours = ts_ms // S.HOUR_MS
    uniq, inv = np.unique(hours, return_inverse=True)
    off = np.array([datetime.datetime.fromtimestamp(int(h) * 3600, NY).utcoffset().total_seconds() * 1000
                    for h in uniq], dtype=np.int64)
    return off[inv]


def weekend_closed_mask(ts_ms: np.ndarray) -> np.ndarray:
    """True for the minutes inside the old weekend closure (Friday 17:00 .. Sunday 17:05 New York)."""
    local = ts_ms + ny_offset_ms(ts_ms)
    wd = (local // S.DAY_MS + 3) % 7                 # 0 = Monday
    mod = (local % S.DAY_MS) // S.MIN
    return ((wd == 4) & (mod >= CLOSE_MIN)) | (wd == 5) | ((wd == 6) & (mod < OPEN_MIN))


@lru_cache(maxsize=None)
def m1_closed(symbol: str) -> dict:
    m = _m1_real(symbol)
    keep = ~weekend_closed_mask(m["ts"])
    return {k: v[keep] for k, v in m.items()}


@contextmanager
def weekends_closed():
    """Makes research.swing.swing read the M1 data with the old weekend closure cut out."""
    orig_m1, orig_bars = S.m1, S.bars

    @lru_cache(maxsize=None)
    def bars(symbol, minutes, offset_min=0):
        return S.resample_merged(m1_closed(symbol), minutes, offset_min)

    S.m1, S.bars = m1_closed, bars
    try:
        yield
    finally:
        S.m1, S.bars = orig_m1, orig_bars


def run_c1(phase_min: int = 0):
    return S.run_bots(donchian, SYMBOLS, tf=(240, phase_min), cap=3, per_symbol=3, **C1)


def stats(trades):
    n, mu, t = S.tstat([x.r for x in trades])
    return dict(n=n, r=mu, t=t, usd=sum(x.usd for x in trades))


def row(label, s):
    return f"| {label} | {s['n']} | {s['r']:+.3f} | {s['t']:+.1f} | {s['usd']:+,.0f} |"


def gap_bars(symbol: str, tf) -> np.ndarray:
    """Per H4 bar: True if it holds a gap of more than 24 h (inside it, or since the previous bar's last row)."""
    b, ts = S.bars(symbol, *tf), _m1_real(symbol)["ts"]
    out = np.zeros(len(b.t), bool)
    for i in range(len(b.t)):
        lo = int(b.first[i]) - (1 if i else 0)
        out[i] = np.any(np.diff(ts[lo:int(b.last[i]) + 1]) > S.DAY_MS)
    return out


def main():
    print("## T1: 24/7 era (signal bars 2024-05-01 .. 2026-09-24)\n")
    print("| phase | variant | n | mean R | t | net $ |\n|---|---|---|---|---|---|")
    diffs = {}
    for ph in PHASES_MIN:
        real = [t for t in run_c1(ph) if t.t_sig >= ERA_247]
        with weekends_closed():
            closed = [t for t in run_c1(ph) if t.t_sig >= ERA_247]
        diffs[ph] = {}
        for sym in (None,) + SYMBOLS:
            a = stats([t for t in real if sym in (None, t.symbol)])
            b = stats([t for t in closed if sym in (None, t.symbol)])
            diffs[ph][sym] = b["r"] - a["r"]
            name = sym or "pooled"
            print(row(f"{ph // 60} h | {name} (a) real", a))
            print(row(f"{ph // 60} h | {name} (b) weekends cut", b))
    print("\n| phase | (b) - (a) pooled | BTCUSD | ETHUSD |\n|---|---|---|---|")
    for ph in PHASES_MIN:
        d = diffs[ph]
        print(f"| {ph // 60} h | {d[None]:+.3f} | {d['BTCUSD']:+.3f} | {d['ETHUSD']:+.3f} |")

    base = run_c1(0)
    print("\n## T2: closed-weekend era (signal bars 2018-01 .. 2024-03), registered phase\n")
    print("| signal bar | n | mean R | t | net $ |\n|---|---|---|---|---|")
    old = [t for t in base if t.t_sig < ERA_CLOSED_END]
    gaps = {s: gap_bars(s, S.H4) for s in SYMBOLS}
    print(row("holds the weekend gap", stats([t for t in old if gaps[t.symbol][t.bar]])))
    print(row("other", stats([t for t in old if not gaps[t.symbol][t.bar]])))

    print("\n## T3: 24/7 era, registered phase\n")
    print("| signal bar closes | n | mean R | t | net $ |\n|---|---|---|---|---|")
    new = [t for t in base if t.t_sig >= ERA_247]
    close_wd = {id(t): ((t.t_sig + 4 * S.HOUR_MS) // S.DAY_MS + 3) % 7 for t in new}
    print(row("Saturday/Sunday UTC", stats([t for t in new if close_wd[id(t)] >= 5])))
    print(row("Monday-Friday UTC", stats([t for t in new if close_wd[id(t)] < 5])))


if __name__ == "__main__":
    main()
