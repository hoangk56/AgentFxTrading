"""Tương quan P&L ngày của một ô với C3 (IS / VAL). Chạy: research/.venv/bin/python -I c3corr.py <k> <H>"""
import csv
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import peg  # noqa: E402


def main():
    k, H = int(sys.argv[1]), int(sys.argv[2])
    c3 = {}
    with open(os.path.join(peg.ROOT, "results/portfolio/trades_C3_gotobi_jpy_basket.csv")) as f:
        for row in csv.DictReader(f):
            if row["era"] not in ("IS", "VAL"):
                continue
            day = row["t_out_utc"][:10]
            c3[day] = c3.get(day, 0.0) + float(row["r"])
    data = peg.load_pairs()
    s = {}
    for p, d in data.items():
        for tr in peg.simulate(p, d, k, H):
            day = datetime.fromtimestamp(tr["tx"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            s[day] = s.get(day, 0.0) + peg.net(tr, fill="taker")
    for era, a, b in (("IS", "2018-01-01", "2021-12-31"), ("VAL", "2022-01-01", "2024-12-31")):
        days = np.arange(np.datetime64(a), np.datetime64(b) + np.timedelta64(1, "D"))
        days = [str(x) for x in days]
        x = np.array([s.get(dd, 0.0) for dd in days])
        y = np.array([c3.get(dd, 0.0) for dd in days])
        m = np.array([dd >= "2016-01-01" for dd in days])
        if x.std() > 0 and y.std() > 0:
            print(f"{era}: calendar days {m.sum()}, rule days {int((x != 0).sum())}, corr with C3 {np.corrcoef(x, y)[0, 1]:+.3f}")


if __name__ == "__main__":
    main()
