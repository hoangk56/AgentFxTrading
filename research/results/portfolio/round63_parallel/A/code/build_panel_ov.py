"""Parse OHLCVault monthly shards (untrusted) into a calendar x stock panel of main-board A-shares, cut at 2025-01-01.

Run: research/.venv/bin/python -I build_panel_ov.py <ashare_dir>
Writes <ashare_dir>/panel_ov.npz: dates, codes, ipo, O H L C (raw CNY), A (amount CNY), AF (back factor), NaN = no bar.
"""
import gzip
import json
import os
import sys

import numpy as np

PREFIX = ("sh.600", "sh.601", "sh.603", "sh.605", "sz.000", "sz.001", "sz.002", "sz.003")


def main(base):
    meta = json.load(open(os.path.join(base, "ov", "meta", "cn.json")))
    ipo = {}
    for e in meta["symbols"]:
        if e.get("type") == "stock" and e.get("board") == "main" and str(e.get("s", "")).startswith(PREFIX):
            ipo[e["s"]] = int(e["ipo"]) if e.get("ipo") else 0
    ddir = os.path.join(base, "ov", "daily")
    files = sorted(f for f in os.listdir(ddir) if f.endswith(".json.gz") and f[:7] <= "2024-12")
    rows = {}
    for fn in files:
        d = json.loads(gzip.decompress(open(os.path.join(ddir, fn), "rb").read()))
        assert d["adjust"] == "none" and d["price_scale"] == 1000 and d["period"] == fn[:7]
        afs = d.get("af_scale", 1000000)
        for b in d["symbols"]:
            s = b["s"]
            if s not in ipo:
                continue
            n = len(b["d"])
            assert all(len(b[k]) == n for k in ("o", "h", "l", "c"))
            af = b.get("af") or [None] * n
            a = b.get("a") or [None] * n
            for i in range(n):
                di = int(b["d"][i])
                if di >= 20250101:
                    continue
                o, h, l, c = b["o"][i], b["h"][i], b["l"][i], b["c"][i]
                if not (o and h and l and c) or min(o, h, l, c) <= 0:
                    continue
                rows.setdefault(s, []).append((di, o / 1000, h / 1000, l / 1000, c / 1000,
                                               np.nan if a[i] is None else float(a[i]),
                                               np.nan if af[i] is None else af[i] / afs))
    codes = np.array(sorted(rows))
    dates = np.array(sorted({r[0] for v in rows.values() for r in v}), dtype=np.int64)
    assert dates.max() < 20250101
    pos = {x: i for i, x in enumerate(dates)}
    shape = (len(dates), len(codes))
    arr = {k: np.full(shape, np.nan) for k in ("O", "H", "L", "C", "A", "AF")}
    for j, s in enumerate(codes):
        for di, o, h, l, c, a, af in rows[s]:
            i = pos[di]
            arr["O"][i, j], arr["H"][i, j], arr["L"][i, j], arr["C"][i, j] = o, h, l, c
            arr["A"][i, j], arr["AF"][i, j] = a, af
    ipo_arr = np.array([ipo[s] for s in codes], dtype=np.int64)
    np.savez_compressed(os.path.join(base, "panel_ov.npz"), dates=dates, codes=codes, ipo=ipo_arr, **arr)
    naf = np.isnan(arr["AF"][np.isfinite(arr["C"])]).mean()
    print("stocks", len(codes), "dates", len(dates), dates.min(), dates.max(), "af missing frac", round(naf, 4),
          "main-board meta entries", len(ipo))


if __name__ == "__main__":
    main(sys.argv[1])
