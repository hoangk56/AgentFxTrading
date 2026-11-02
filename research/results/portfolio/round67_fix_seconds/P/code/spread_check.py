"""Data check (no returns): IC USDCNH spread (bp of mid) at the declared moments, by year, weekdays 2016-24."""
from datetime import date, timedelta

import numpy as np

from plib import OUT, load_window, quote_at_or_after, quote_before

T = 1 * 3600 + 15 * 60
MOMENTS = {"pre 01:14:59.9": ("b", 0), "+5s": ("a", 5), "+30s": ("a", 30), "+6min": ("a", 360),
           "+30min": ("a", 1800), "+31min": ("a", 1860)}


def main():
    lines = ["year n | median spread bp (mean) at: " + ", ".join(MOMENTS)]
    for y in range(2016, 2025):
        acc = {k: [] for k in MOMENTS}
        n = 0
        d = date(y, 1, 1)
        while d.year == y:
            if d.weekday() < 5:
                w = load_window(d, T - 120, T + 1900)
                if w is not None and w[0].size > 50:
                    ts, b, a = w
                    n += 1
                    for k, (kind, off) in MOMENTS.items():
                        q = quote_before(ts, b, a, (T + off) * 1000) if kind == "b" else \
                            quote_at_or_after(ts, b, a, (T + off) * 1000)
                        if q is not None:
                            acc[k].append((q[2] - q[1]) / ((q[2] + q[1]) / 2) * 1e4)
            d += timedelta(days=1)
        lines.append(f"{y} {n} | " + ", ".join(f"{np.median(v):.2f} ({np.mean(v):.2f})" for v in acc.values()))
        print(lines[-1], flush=True)
    (OUT / "spread_check.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
