"""Gộp zip nến tháng thành npz mỗi mã (cắt ts < 2025-01-01 ngay khi đọc).

Chạy: research/.venv/bin/python -I parse.py <data_dir> <interval>
"""
import io
import os
import sys
import zipfile

import numpy as np

CUT = 1735689600000  # 2025-01-01 00:00 UTC, ms


def read_zip(path):
    rows = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.endswith(".csv"):
                continue
            text = z.read(name).decode("ascii", "replace")
            for line in io.StringIO(text):
                p = line.strip().split(",")
                if len(p) < 9 or not p[0].isdigit():
                    continue  # dòng header
                t = int(p[0])
                if t > 10**14:  # micro giây
                    t //= 1000
                if t >= CUT:
                    continue
                rows.append((t, float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[7]), int(p[8]), float(p[5]),
                             float(p[9]), float(p[10])))
    return rows


def main():
    data_dir, interval = sys.argv[1], sys.argv[2]
    src = os.path.join(data_dir, "raw", interval)
    dst = os.path.join(data_dir, "npz", interval)
    os.makedirs(dst, exist_ok=True)
    for sym in sorted(os.listdir(src)):
        rows = []
        for f in sorted(os.listdir(os.path.join(src, sym))):
            if f.endswith(".zip"):
                rows.extend(read_zip(os.path.join(src, sym, f)))
        if not rows:
            print(sym, "empty")
            continue
        a = np.array(rows, dtype=np.float64)
        a = a[np.argsort(a[:, 0], kind="stable")]
        keep = np.r_[True, np.diff(a[:, 0]) > 0]
        a = a[keep]
        np.savez_compressed(os.path.join(dst, sym + ".npz"), t=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2],
                            l=a[:, 3], c=a[:, 4], qv=a[:, 5], n=a[:, 6].astype(np.int64), v=a[:, 7], tbb=a[:, 8],
                            tbq=a[:, 9])
        print(sym, len(a), "first", int(a[0, 0]), "last", int(a[-1, 0]))


if __name__ == "__main__":
    main()
