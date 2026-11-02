"""Data check (no signed returns): tick activity and |mid change| per second around 01:15:00 UTC, by year.

Usage: python release_time.py  -> out/release_time.txt
"""
from datetime import date, timedelta

import numpy as np

from plib import OUT, load_window

T0, T1 = 1 * 3600 + 13 * 60, 1 * 3600 + 18 * 60  # 01:13:00 .. 01:18:00
N = T1 - T0


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lines = []
    for y in range(2016, 2025):
        cnt = np.zeros(N)
        absd = np.zeros(N)
        ndays = 0
        d = date(y, 1, 1)
        while d.year == y:
            if d.weekday() < 5:
                w = load_window(d, T0, T1)
                if w is not None and w[0].size > 20:
                    ts, b, a = w
                    mid = (b + a) / 2
                    sec = ts // 1000 - T0
                    ok = sec >= 0
                    np.add.at(cnt, sec[ok], 1)
                    dm = np.abs(np.diff(np.log(mid))) * 1e4
                    s2 = sec[1:]
                    ok2 = s2 >= 0
                    np.add.at(absd, s2[ok2], dm[ok2])
                    ndays += 1
            d += timedelta(days=1)
        cnt /= max(ndays, 1)
        absd /= max(ndays, 1)
        # seconds 01:14:50 .. 01:15:30
        lines.append(f"== {y} days {ndays}")
        base = 60 + 50  # index of 01:14:50
        lines.append("sec  " + " ".join(f"{s - 120:+4d}" for s in range(base, base + 45)))
        lines.append("tick " + " ".join(f"{cnt[s]:4.1f}" for s in range(base, base + 45)))
        lines.append("|dm| " + " ".join(f"{absd[s]:4.2f}" for s in range(base, base + 45)))
        pk = int(np.argmax(absd))
        lines.append(f"peak |dm| second: {pk - 120:+d} s from 01:15:00 ({absd[pk]:.2f} bp/day); "
                     f"pre median {np.median(absd[:110]):.3f}, minute 01:16-01:17 mean {absd[180:240].mean():.3f}")
        print(lines[-1], flush=True)
    (OUT / "release_time.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
