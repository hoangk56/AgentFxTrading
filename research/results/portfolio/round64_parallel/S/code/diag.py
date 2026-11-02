"""Kiểm dội bid/ask: so giá đóng với giá xấu nhất trong nến, và độ rộng nến trước tín hiệu (proxy spread).

Chạy: research/.venv/bin/python -I diag.py <k> <H>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import peg  # noqa: E402


def main():
    k, H = int(sys.argv[1]), int(sys.argv[2])
    data = peg.load_pairs()
    for era in ("IS", "VAL"):
        rows = []
        for p, d in data.items():
            for tr in peg.simulate(p, d, k, H):
                if peg.era_of(tr) != era:
                    continue
                s = tr["sig"]
                lo = max(0, s - 1440)
                h, l, c, n = d["h"][lo:s], d["l"][lo:s], d["c"][lo:s], d["n"][lo:s]
                m = n >= 2
                rng = np.median((h[m] - l[m]) / c[m]) * 1e4 if m.sum() > 10 else np.nan
                g = (tr["px"] / tr["pe"] - 1) * 1e4
                gw = (tr["px_lo"] / tr["pe_hi"] - 1) * 1e4
                rows.append((p, peg.ymd(tr["te"]), tr["d_sig"] * 1e4, tr["d_e"] * 1e4, g, gw, tr["hold"] * 24 * 60,
                             int(d["n"][tr["e"]]), rng))
        if not rows:
            continue
        a = np.array([r[2:] for r in rows], dtype=float)
        print(f"== {era} k={k} H={H}: n {len(rows)}; gross close {a[:, 2].mean():+.1f} bp, gross worst-fill "
              f"{a[:, 3].mean():+.1f}; median entry discount {np.median(a[:, 1]):.1f} bp (signal {np.median(a[:, 0]):.1f}); "
              f"median hold {np.median(a[:, 4]):.0f} min; share hold <= 5 min {np.mean(a[:, 4] <= 5) * 100:.0f} %; "
              f"median prior-day bar range {np.nanmedian(a[:, 6]):.1f} bp")
        for lo_, hi_ in ((0, 5), (5, 60), (60, 1440), (1440, 1e9)):
            m = (a[:, 4] > lo_) & (a[:, 4] <= hi_) if lo_ else a[:, 4] <= hi_
            if m.sum():
                print(f"   hold ({lo_},{hi_}] min: n {m.sum()}, gross {a[m, 2].mean():+.1f}, worst {a[m, 3].mean():+.1f}")
        if len(sys.argv) > 3:
            for r in rows:
                print("   ", r[0], r[1], " ".join(f"{x:.1f}" for x in r[2:]))


if __name__ == "__main__":
    main()
