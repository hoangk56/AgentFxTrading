"""Confirmation of the pre-registered candidates on 2023-2024 (results/strategy_prereg.md), parameters unchanged.

  python -m research.scan.confirm [btc] [xau] [tom]"""
import sys
from datetime import date

import numpy as np

from research.indicators import prior_max, prior_min
from research.scan.data import atr, resample
from research.scan.engine import Order, simulate, stats
from research.scan.m1 import load
from research.scan.sessions import session_days
from research.scan.ticksim import run as tick_run
from research.ticks import day_ms

YEARS = {2023: (date(2023, 1, 1), date(2023, 12, 31)), 2024: (date(2024, 1, 1), date(2024, 12, 31)),
         2025: (date(2025, 1, 1), date(2025, 12, 31)), 2026: (date(2026, 1, 1), date(2026, 9, 24))}


def _year(ms):
    for y, (a, b) in YEARS.items():
        if day_ms(a) <= ms < day_ms(b) + 86_400_000:
            return y
    return None


def _line(label, rs):
    n, mu, t = stats(rs)
    return f"{label}: n {n:4d} mean R {mu:+.3f} t {t:+.1f}"


def btc():
    print("== BTC-S1 (tick level, $2000 start per year)")
    pooled = []
    for y in (2023, 2024, 2025, 2026):
        a, b = YEARS[y]
        pos, refused, eq = tick_run("BTCUSD", a, b)
        if not pos:
            print(f"  {y}: no positions (data missing?)")
            continue
        r = [x.r for x in pos]
        curve = np.cumsum([x.net for x in pos])
        dd = float(np.max(np.maximum.accumulate(np.r_[0, curve]) - np.r_[0, curve]))
        print("  " + _line(str(y), r) + f" | net ${eq - 2000:+.0f} ({(eq / 2000 - 1) * 100:+.1f} %) max DD ${dd:.0f} refused {refused}")
        if y in (2023, 2024):
            pooled += r
    print("  " + _line("2023-2024 pooled", pooled))


def xau_orders(b, a, N=30, H=12, SLK=1.5):
    hh, ll = prior_max(b.h, N), prior_min(b.l, N)
    with np.errstate(invalid="ignore"):
        up, dn = b.c > hh, b.c < ll
    sig = np.where(up & ~np.r_[False, up[:-1]], 1, np.where(dn & ~np.r_[False, dn[:-1]], -1, 0))
    out = []
    for i in np.flatnonzero(sig):
        if i < max(N, 20) + 1 or i >= len(b) - 1 or not np.isfinite(a[i]):
            continue
        s = int(sig[i]); j = min(i + H, len(b) - 1)
        out.append(Order(int(b.last[i]) + 1, s, b.c[i] - s * SLK * a[i], int(b.last[j])))
    return out


def xau():
    print("== XAU-T1 (H4 Donchian 30, SL 1.5 ATR, exit after 12 bars; M1 engine)")
    m = load("XAUUSD")
    b = resample(m, 240)
    f = simulate(m, "XAUUSD", xau_orders(b, atr(b, 20)))
    for y in (2023, 2024, 2025, 2026):
        fy = [x for x in f if _year(x.t_in) == y]
        print("  " + _line(str(y), [x.r for x in fy]) + " | " + _line("long", [x.r for x in fy if x.side > 0])
              + " | " + _line("short", [x.r for x in fy if x.side < 0]))
    p = [x for x in f if _year(x.t_in) in (2023, 2024)]
    print("  " + _line("2023-2024 pooled", [x.r for x in p]) + " | " + _line("short", [x.r for x in p if x.side < 0]))


def _tom_days(days):
    days = sorted(days)
    out = set()
    by_month = {}
    for d in days:
        by_month.setdefault((d.year, d.month), []).append(d)
    months = sorted(by_month)
    for k, key in enumerate(months):
        ds = by_month[key]
        out.update(ds[:3])
        if k + 1 < len(months):          # the last day only counts once the next month has started
            out.add(ds[-1])
    return out


def tom():
    print("== TOM (long US30/USTEC/DE40 over the cash session; R = 3 %)")
    fills = {"TOM": [], "REST": []}
    for s in ("US30", "USTEC", "DE40"):
        m = load(s)
        sd = session_days(m, s)
        tom_set = _tom_days([d for d, _, _ in sd])
        for key in fills:
            orders = [Order(ka, 1, m["o"][ka] * 0.97, kb) for d, ka, kb in sd if (d in tom_set) == (key == "TOM")]
            fills[key] += simulate(m, s, orders)
    for y in (2023, 2024, 2025, 2026):
        print("  " + " | ".join(_line(f"{y} {k}", [x.r for x in v if _year(x.t_in) == y]) for k, v in fills.items()))
    print("  " + " | ".join(_line(f"2023-2024 {k}", [x.r for x in v if _year(x.t_in) in (2023, 2024)])
                            for k, v in fills.items()))


if __name__ == "__main__":
    which = sys.argv[1:] or ["btc", "xau", "tom"]
    for w in which:
        {"btc": btc, "xau": xau, "tom": tom}[w]()
