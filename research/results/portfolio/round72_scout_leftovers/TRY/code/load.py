"""Loaders (numpy only). Every series is cut at ts < 2025-01-01 UTC."""
import datetime as dt
import glob
import json
import lzma
import os

import numpy as np

ROOT = "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/usdtry_premium"
CUT = 1735689600  # 2025-01-01 00:00 UTC (s)


def btcturk_1h():
    """(t s, o, h, l, c, v) arrays sorted, unique, t < CUT. t is the API label (alignment checked in align.py)."""
    rows = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "btcturk_1h", "*.json"))):
        d = json.load(open(p))
        for i, t in enumerate(d["t"]):
            if t < CUT:
                rows[t] = (d["o"][i], d["h"][i], d["l"][i], d["c"][i], d["v"][i])
    t = np.array(sorted(rows))
    a = np.array([rows[x] for x in t], dtype=float)
    return t, a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]


def duka_hour(day, hour=6):
    """Ticks of one UTC hour: (ms of day offset from hour start, ask, bid) or None if the file is missing; empty arrays if
    no ticks. Price scale 1e5 (checked: 2024-01-02 06:00 ask 29.67879 / bid 29.66726)."""
    p = os.path.join(ROOT, "duka_06h", f"{day:%Y%m%d}_{hour:02d}.bi5")
    if not os.path.exists(p):
        return None
    b = open(p, "rb").read()
    if not b:
        return np.empty(0, np.int64), np.empty(0), np.empty(0)
    r = np.frombuffer(lzma.decompress(b), dtype=">u4").reshape(-1, 5)
    return r[:, 0].astype(np.int64), r[:, 1] / 1e5, r[:, 2] / 1e5


def first_at(ms, ask, bid, sec):
    """(ask, bid, ms) of the first tick at or after `sec` seconds into the hour, within 10 minutes; None if none."""
    k = int(np.searchsorted(ms, sec * 1000))
    if k >= len(ms) or ms[k] > (sec + 600) * 1000:
        return None
    return float(ask[k]), float(bid[k]), int(ms[k])


def duka_h1():
    """Hourly candles from the monthly files: dict side -> (t s UTC, open, close, low, high, vol), t < CUT.
    Record '>5if' = seconds from month start, open, close, low, high (x1e5), volume (checked in check_h1)."""
    out = {}
    for side in ("BID", "ASK"):
        ts, rows = [], []
        for p in sorted(glob.glob(os.path.join(ROOT, "duka_h1", f"*_{side}.bi5"))):
            y, m = int(os.path.basename(p)[:4]), int(os.path.basename(p)[4:6])
            b = open(p, "rb").read()
            if not b:
                continue
            raw = lzma.decompress(b)
            a = np.frombuffer(raw, dtype=np.dtype([("t", ">i4"), ("o", ">i4"), ("c", ">i4"), ("l", ">i4"), ("h", ">i4"),
                                                   ("v", ">f4")]))
            base = int(dt.datetime(y, m, 1, tzinfo=dt.UTC).timestamp())
            ts.append(base + a["t"].astype(np.int64))
            rows.append(np.stack([a["o"] / 1e5, a["c"] / 1e5, a["l"] / 1e5, a["h"] / 1e5, a["v"].astype(float)], 1))
        if not ts:
            continue
        t = np.concatenate(ts)
        r = np.concatenate(rows)
        k = t < CUT
        out[side] = (t[k], r[k, 0], r[k, 1], r[k, 2], r[k, 3], r[k, 4])
    return out
