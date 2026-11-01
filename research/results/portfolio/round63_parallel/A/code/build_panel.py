"""Parse raw Tencent kline JSON (untrusted) into a calendar x stock panel, cut at 2025-01-01.

Run: research/.venv/bin/python -I build_panel.py <ashare_dir>
Writes <ashare_dir>/panel.npz with dates (YYYYMMDD int), codes, O H L C V (float64, NaN when no bar).
"""
import json
import os
import sys

import numpy as np

MAIN = ("sh600", "sh601", "sh603", "sh605", "sz000", "sz001", "sz002", "sz003")


def main(base):
    raw = os.path.join(base, "raw_kline")
    per = {}
    bad = 0
    for fn in sorted(os.listdir(raw)):
        if not fn.endswith(".json"):
            continue
        code = fn[:-5]
        if not code.startswith(MAIN):
            continue
        try:
            d = json.load(open(os.path.join(raw, fn)))
            node = d["data"][code]
            rows = node.get("day") or node.get("qfqday") or []
        except Exception:  # noqa: BLE001
            bad += 1
            continue
        out = []
        for r in rows:
            if not isinstance(r, list) or len(r) < 6:
                continue
            ds = str(r[0])
            if len(ds) != 10:
                continue
            di = int(ds.replace("-", ""))
            if di < 20160101 or di >= 20250101:  # HOLD stays closed
                continue
            try:
                o, c, h, l, v = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]))
            except ValueError:
                continue
            if not (o > 0 and c > 0 and h > 0 and l > 0):
                continue
            out.append((di, o, h, l, c, v))
        if len(out) >= 2:
            per[code] = out
    dates = np.array(sorted({r[0] for rows in per.values() for r in rows}), dtype=np.int64)
    assert dates.max() < 20250101
    codes = np.array(sorted(per))
    pos = {d: i for i, d in enumerate(dates)}
    shape = (len(dates), len(codes))
    arr = {k: np.full(shape, np.nan) for k in "OHLCV"}
    for j, code in enumerate(codes):
        for di, o, h, l, c, v in per[code]:
            i = pos[di]
            arr["O"][i, j], arr["H"][i, j], arr["L"][i, j], arr["C"][i, j], arr["V"][i, j] = o, h, l, c, v
    np.savez_compressed(os.path.join(base, "panel.npz"), dates=dates, codes=codes, **arr)
    print("stocks", len(codes), "dates", len(dates), dates.min(), dates.max(), "bad files", bad)


if __name__ == "__main__":
    main(sys.argv[1])
