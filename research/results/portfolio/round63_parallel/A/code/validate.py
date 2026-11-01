"""Cross-check the OHLCVault panel against the 137 Tencent kline files (both untrusted; agreement = evidence).

Run: research/.venv/bin/python -I validate.py <ashare_dir>
"""
import json
import os
import sys

import numpy as np


def main(base):
    z = dict(np.load(os.path.join(base, "panel_ov.npz")))
    dates, codes = z["dates"], list(z["codes"])
    pos = {d: i for i, d in enumerate(dates)}
    col = {c.replace(".", ""): j for j, c in enumerate(codes)}
    raw = os.path.join(base, "raw_kline")
    n = agree = 0
    miss_ov = miss_tx = 0
    worst = []
    nstock = 0
    for fn in sorted(os.listdir(raw)):
        code = fn[:-5]
        if code not in col:
            continue
        nstock += 1
        j = col[code]
        rows = json.load(open(os.path.join(raw, fn)))["data"][code].get("day", [])
        txd = set()
        for r in rows:
            di = int(r[0].replace("-", ""))
            if di < 20161101 or di >= 20250101:
                continue
            txd.add(di)
            if di not in pos or not np.isfinite(z["C"][pos[di], j]):
                miss_ov += 1
                continue
            i = pos[di]
            tx = np.array([float(r[1]), float(r[3]), float(r[4]), float(r[2])])  # o h l c
            ov = np.array([z["O"][i, j], z["H"][i, j], z["L"][i, j], z["C"][i, j]])
            n += 1
            d = np.abs(tx - ov).max()
            if d < 0.0051:
                agree += 1
            else:
                worst.append((d, code, di, tx.tolist(), ov.tolist()))
        ovd = {dates[i] for i in np.where(np.isfinite(z["C"][:, j]))[0] if 20161101 <= dates[i] < 20250101}
        miss_tx += len(ovd - txd)
    worst.sort(reverse=True)
    print(f"stocks compared {nstock}; bars compared {n}; OHLC agree within 0.005: {agree} ({agree / max(n, 1):.4%})")
    print(f"bars in Tencent missing from OV: {miss_ov}; bars in OV missing from Tencent: {miss_tx}")
    for w in worst[:8]:
        print("  diff", w)


if __name__ == "__main__":
    main(sys.argv[1])
