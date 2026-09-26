"""Tick-level check of a shock-bar follow rule with the live sizing guardrails at a $2000 start.

Bars are the bid M15 bars cTrader builds; the order fills at the first tick after the bar close (OnBarClosed),
SL/TP sit SLK/TPK x ATR20 (SMA of TR) from the fill, and a position still open H bars later is closed at the
first tick after that bar's close. Sizing: research.specs.size_units (0.5 % of equity, $50 cap, 1.5x min-lot
guard). Commission and swaps as in research.sim."""
import argparse
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np

from research.bars import build_bars
from research.indicators import atr_sma
from research.sim import _first_hit
from research.specs import SPECS, size_units, swap_usd
from research.ticks import day_ms, load_ticks

PARAMS = {"RiskPercentage": 0.5, "MaxRiskPerTradeMoney": 50.0, "MaxMinLotRiskMultiple": 1.5}


@dataclass
class Pos:
    side: int
    t_in: int
    entry: float
    units: float
    risk_usd: float
    t_out: int = 0
    net: float = 0.0
    why: str = ""
    sl_usd: float = 0.0   # money lost if the initial SL is hit (before costs)

    @property
    def r(self):
        return self.net / self.risk_usd


def run(symbol, start, end, Z=2.5, H=12, SLK=2.0, TPK=2.0, tf=15, balance=2000.0, p=PARAMS, delay_ms=0, fixed_units=None):
    spec = SPECS[symbol]
    t = load_ticks(symbol, start - timedelta(days=3), end)
    if len(t) == 0:
        return [], 0, balance
    b = build_bars(t, tf)
    a = atr_sma(b.h, b.l, b.c, 20)
    mv = np.r_[0.0, np.diff(b.c)] / a
    sig = np.where(mv > Z, 1, np.where(mv < -Z, -1, 0))
    start_ms = day_ms(start)
    equity, busy, out, refused = balance, -1, [], 0
    for i in np.flatnonzero(sig):
        e = int(b.event_tick[i])
        if delay_ms and e < len(t):
            e = int(np.searchsorted(t.ts, t.ts[e] + delay_ms))   # order reaches the broker delay_ms later
        if i < 25 or e >= len(t) or e <= busy or t.ts[e] < start_ms or not np.isfinite(a[i]):
            continue
        s = int(sig[i])
        bid, ask = float(t.bid[e]), float(t.ask[e])
        entry = ask if s > 0 else bid
        dist = SLK * a[i]
        # fixed_units: the same volume on every trade, no equity-based sizing and no min-lot guard
        units = fixed_units if fixed_units else size_units(equity, dist / spec.pip, spec, p)
        if units <= 0:
            refused += 1
            continue
        sl, tp = entry - s * dist, entry + s * TPK * a[i]
        k_end = min(i + H, len(b) - 1)
        j_end = min(int(b.event_tick[k_end]), len(t) - 1)
        seg_end = j_end + 1
        if s > 0:
            j = _first_hit(t.bid[:seg_end], e + 1, sl, tp)
        else:
            j = _first_hit(t.ask[:seg_end], e + 1, tp, sl)
        if j >= seg_end:
            j, why = j_end, "time"
        else:
            px_ = t.bid[j] if s > 0 else t.ask[j]
            why = "sl" if (px_ - sl) * s <= 0 else "tp"
        px = float(t.bid[j] if s > 0 else t.ask[j])
        net = (px - entry) * s * units * spec.usd_per_quote - spec.comm_per_unit * units
        net += swap_usd(symbol, s, units, int(t.ts[e]), int(t.ts[j]))
        pos = Pos(s, int(t.ts[e]), entry, units, equity * p["RiskPercentage"] / 100.0, int(t.ts[j]), net, why,
                  dist * units * spec.usd_per_quote)
        equity += net
        busy = j
        out.append(pos)
    return out, refused, equity


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol")
    ap.add_argument("--z", type=float, default=2.5)
    ap.add_argument("--h", type=int, default=12)
    ap.add_argument("--sl", type=float, default=2.0)
    ap.add_argument("--tp", type=float, default=2.0)
    args = ap.parse_args(argv)
    for label, a_, b_ in (("2025", date(2025, 1, 1), date(2025, 12, 31)), ("2026", date(2026, 1, 1), date(2026, 9, 24))):
        pos, refused, eq = run(args.symbol, a_, b_, args.z, args.h, args.sl, args.tp)
        r = np.array([x.r for x in pos])
        why = {w: sum(1 for x in pos if x.why == w) for w in ("sl", "tp", "time")}
        curve = np.cumsum([x.net for x in pos])
        dd = float(np.max(np.maximum.accumulate(np.r_[0, curve]) - np.r_[0, curve])) if len(pos) else 0.0
        t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else 0.0
        print(f"{args.symbol} {label}: n {len(r)} mean R {r.mean():+.3f} t {t:+.1f} | net ${eq - 2000:+.0f} "
              f"({(eq / 2000 - 1) * 100:+.1f} %) max DD ${dd:.0f} | refused {refused} | exits {why} "
              f"| units {sorted(set(round(x.units, 2) for x in pos))[:6]}")
        for P, lo, hi in (("P2", day_ms(date(2026, 1, 1)), day_ms(date(2026, 6, 1))), ("P3", day_ms(date(2026, 6, 1)), 1 << 62)):
            if label == "2026":
                rr = np.array([x.r for x in pos if lo <= x.t_in < hi])
                if len(rr) > 1:
                    print(f"   {P}: n {len(rr)} mean R {rr.mean():+.3f} t {rr.mean() / (rr.std(ddof=1) / np.sqrt(len(rr))):+.1f}")


if __name__ == "__main__":
    main()
