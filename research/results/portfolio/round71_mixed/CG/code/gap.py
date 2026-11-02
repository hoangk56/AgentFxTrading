"""Stream CG: CME weekend-gap fade on Binance BTCUSDT / ETHUSDT perps (../HYPOTHESES_CG.md).

Minute axis: t = minutes since T0 = 2020-01-01 00:00 UTC. c[t], h[t], l[t] = close / high / low of the 1m bar opening at t.
Price at instant T (minutes) = c[T - 1] (forward fill <= 5 bars). Everything cut at ts < 2025-01-01 at load.
"""
import csv
import datetime as dt
import glob
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
D1M = os.path.join(R, "data", "binance_1m_wicks", "npz")
DF = os.path.join(R, "data", "binance", "funding")
T0 = 1577836800000            # 2020-01-01
END = 1735689600000           # 2025-01-01 exclusive (HOLD start)
MIN = 60000
NM = (END - T0) // MIN
UTC = dt.timezone.utc
ETH_START = dt.date(2021, 2, 12)   # first Friday close after CME Ether futures launch (2021-02-08)
COST_RT = 12.0                     # bp: taker 5 + half-spread 1, both sides

# Weekends excluded because the CME close / reopen is not the regular one (HYPOTHESES_CG.md), keyed by Friday date.
EXCL = {dt.date(*x) for x in [
    (2020, 4, 10), (2021, 4, 2), (2022, 4, 15), (2023, 4, 7), (2024, 3, 29),          # Good Friday
    (2020, 11, 27), (2021, 11, 26), (2022, 11, 25), (2023, 11, 24), (2024, 11, 29),   # day after Thanksgiving
    (2020, 7, 3), (2020, 12, 25), (2021, 1, 1), (2021, 7, 2), (2021, 12, 24), (2021, 12, 31),
    (2022, 12, 23), (2022, 12, 30), (2023, 12, 22), (2023, 12, 29)]}


def _nth_sunday(y, m, n):
    d = dt.date(y, m, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(days=7 * (n - 1))


def chicago_to_utc(d, hour):
    """Local Chicago wall time (date d, hour) -> UTC datetime, US DST rule (2nd Sun Mar 02:00 .. 1st Sun Nov 02:00)."""
    a = dt.datetime.combine(_nth_sunday(d.year, 3, 2), dt.time(2))
    b = dt.datetime.combine(_nth_sunday(d.year, 11, 1), dt.time(2))
    loc = dt.datetime.combine(d, dt.time(hour))
    off = 5 if a <= loc < b else 6
    return (loc + dt.timedelta(hours=off)).replace(tzinfo=UTC)


def to_min(x):
    return int((x.timestamp() * 1000 - T0) // MIN)


def load(sym):
    c = np.full(NM, np.nan); h = np.full(NM, np.nan); lo = np.full(NM, np.nan)
    files = sorted(glob.glob(os.path.join(D1M, f"{sym}_*.npz")))
    for f in files:
        if os.path.basename(f).split("_")[1][:4] >= "2025":
            continue
        z = np.load(f)
        t = z["m"].astype(np.int64) - T0 // MIN
        k = (t >= 0) & (t < NM)
        t = t[k]
        c[t] = z["c"][k]; h[t] = z["h"][k]; lo[t] = z["l"][k]
    idx = np.where(~np.isnan(c), np.arange(NM), -1)
    np.maximum.accumulate(idx, out=idx)
    fr = np.zeros(NM + 1)
    with open(os.path.join(DF, sym + ".csv")) as fh:
        rows = list(csv.reader(fh))[1:]
    a = np.array(rows, dtype=float)
    a = a[(a[:, 0] >= T0) & (a[:, 0] < END)]
    tm = np.round((a[:, 0] - T0) / MIN).astype(np.int64)
    np.add.at(fr, tm, a[:, 1])
    cum = np.concatenate([[0.0], np.cumsum(fr)])    # cum[k] = sum fr[:k]
    return dict(c=c, h=h, l=lo, last=idx, cum=cum, nfiles=len(files))


def px(S, T):
    """price at instant T (minutes): close of bar T-1, forward-filled <= 5 bars."""
    j = T - 1
    if j < 0 or j >= NM:
        return np.nan
    k = S["last"][j]
    return S["c"][k] if k >= 0 and j - k <= 5 else np.nan


def fund(S, te, tx):
    """sum of stamps with te < t_stamp <= tx (minutes)."""
    return S["cum"][min(tx, NM) + 1] - S["cum"][min(te, NM) + 1]


def trade(S, C, Rm, Hmax=4320):
    """One anchor. Returns dict of m and, for H in (1440, 4320) and late in (0, 1), (net-before-cost gross bp, fund bp,
    hit flag) or None. Entry at instant Rm+6 (Rm+7 late)."""
    pc, pr = px(S, C), px(S, Rm)
    if not (np.isfinite(pc) and np.isfinite(pr)):
        return None
    m = np.log(pr / pc)
    s = -1.0 if m > 0 else 1.0
    out = {"m": m, "s": s}
    for late in (0, 1):
        te = Rm + 6 + late
        pe = px(S, te)
        if not np.isfinite(pe) or te + Hmax + 2 > NM:
            return None
        if (s < 0 and pe <= pc) or (s > 0 and pe >= pc):
            out[late] = "closed"
            continue
        seg = S["l"][te:te + Hmax] if s < 0 else S["h"][te:te + Hmax]
        hit = (seg <= pc) if s < 0 else (seg >= pc)
        j = int(np.argmax(hit)) if hit.any() else -1
        res = {}
        for H in (1440, 4320):
            if 0 <= j < H:
                if late:
                    tx = te + j + 2
                    pxit = px(S, tx)
                else:
                    tx = te + j + 1
                    pxit = pc
                hf = 1
            else:
                tx = te + H + late
                pxit = px(S, tx)
                hf = 0
            if not np.isfinite(pxit):
                return None
            g = s * np.log(pxit / pe) * 1e4
            f = -s * fund(S, te, tx) * 1e4
            res[H] = (g, f, hf, (tx - te) / 60.0)
        out[late] = res
    return out


def fridays():
    d = dt.date(2020, 1, 3)
    while d <= dt.date(2024, 12, 27):
        yield d
        d += dt.timedelta(days=7)


def real_anchors():
    """(friday, C_min, R_min) for regular weekends."""
    out = []
    for f in fridays():
        if f in EXCL:
            continue
        C = chicago_to_utc(f, 16)
        Rr = chicago_to_utc(f + dt.timedelta(days=2), 17)
        out.append((f, to_min(C), to_min(Rr)))
    return out


def weekday_anchors(wd):
    """brief benchmark: weekday wd (0 = Mon .. 3 = Thu) 16:00 CT, pseudo reopen 49 h later."""
    out = []
    for f in fridays():
        d = f - dt.timedelta(days=4 - wd)
        C = chicago_to_utc(d, 16)
        out.append((f, to_min(C), to_min(C) + 49 * 60))
    return out


def how_anchors(a):
    """hour-of-week placebo: UTC hour a after Monday 00:00 UTC, pseudo reopen 49 h later; keyed by that week's Friday."""
    out = []
    for f in fridays():
        mon = dt.datetime.combine(f - dt.timedelta(days=4), dt.time(0), tzinfo=UTC)
        C = to_min(mon + dt.timedelta(hours=a))
        out.append((f, C, C + 49 * 60))
    return out


def era(f):
    return "IS" if f.year <= 2021 else "VAL"


def cl_t(x, g):
    x = np.asarray(x, float); n = len(x)
    if n < 3:
        return np.nan
    mu = x.mean()
    u, inv = np.unique(g, return_inverse=True)
    s = np.bincount(inv, weights=x - mu)
    G = len(u)
    var = (s ** 2).sum() / n ** 2 * G / max(G - 1, 1)
    return mu / np.sqrt(var) if var > 0 else np.nan


def run(S_by, anchors, eth_gate=True):
    """rows: one per (anchor, coin) with all variants; independent of k (filter later)."""
    rows = []
    for sym, S in S_by.items():
        for f, C, Rm in anchors:
            if sym == "ETHUSDT" and eth_gate and f < ETH_START:
                continue
            r = trade(S, C, Rm)
            if r is None:
                continue
            rows.append((sym, f, r))
    return rows


def cell(rows, k, H, late=0, cmult=1.0, era_=None):
    """net bp per trade + clusters + years for one cell."""
    x, g, yr, hits, hrs, gross, fu = [], [], [], [], [], [], []
    nclosed = 0
    for sym, f, r in rows:
        if abs(r["m"]) < k:
            continue
        if era_ and era(f) != era_:
            continue
        v = r[late]
        if v == "closed":
            nclosed += 1
            continue
        gb, fb, hf, hh = v[H]
        x.append(gb + fb - COST_RT * cmult); g.append(f.toordinal()); yr.append(f.year)
        hits.append(hf); hrs.append(hh); gross.append(gb); fu.append(fb)
    return dict(x=np.array(x), g=np.array(g), yr=np.array(yr), hit=np.array(hits), hrs=np.array(hrs),
                gross=np.array(gross), fund=np.array(fu), nclosed=nclosed)
