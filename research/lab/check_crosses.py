"""Rebuild EURJPY, GBPJPY, AUDJPY from their USD legs and compare with the real ticks, one week per month of
2025-2026: median mid difference (bp) and mean spread (the cost actually paid; the legs' raw spreads are often
0, so medians are useless), real vs synthetic. The median of the three ratios real/synthetic becomes
universe.SYNTH_SPREAD_FACTOR.   python -m research.lab.check_crosses"""
from datetime import date, timedelta

import numpy as np

from research.lab.feed import cross_ticks
from research.lab.universe import CHECK_CROSSES
from research.ticks import load_ticks

WEEKS = [date(2025, m, 3) for m in range(1, 13)] + [date(2026, m, 2) for m in range(1, 10)]


def main() -> None:
    ratios = []
    for sym, (a, b, op) in CHECK_CROSSES.items():
        diffs, spreads_real, spreads_syn = [], [], []
        for d in WEEKS:
            e = d + timedelta(days=4)
            real = load_ticks(sym, d, e)
            syn = cross_ticks(load_ticks(a, d, e), load_ticks(b, d, e), op)
            if len(real) == 0 or len(syn) == 0:
                continue
            k = np.searchsorted(syn.ts, real.ts, "right") - 1
            ok = k >= 0
            rm = (real.bid[ok] + real.ask[ok]) / 2
            sm = (syn.bid[k[ok]] + syn.ask[k[ok]]) / 2
            diffs.append(float(np.median(np.abs(rm - sm) / rm)) * 1e4)
            spreads_real.append(float(np.mean(real.ask - real.bid)))
            spreads_syn.append(float(np.mean(syn.ask[k[ok]] - syn.bid[k[ok]])))
        ratio = float(np.mean(spreads_real) / np.mean(spreads_syn))
        ratios.append(ratio)
        print(f"{sym}: mid diff {np.median(diffs):.2f} bp | mean spread real {np.mean(spreads_real):.4f} "
              f"synthetic {np.mean(spreads_syn):.4f} | ratio {ratio:.2f}")
    print(f"SYNTH_SPREAD_FACTOR = {np.median(ratios):.2f}")


if __name__ == "__main__":
    main()
