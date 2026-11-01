"""Round 63 stream M engine: IC M1 mid panel (2016-01-01 .. 2024-12-31, cut at load), quote convention of round 24
(price at X = close of the bar labelled X - 1 min, <= 10 min stale), venue cost model of HYPOTHESES_M.md.

HOLD safety: every series is cut at ts < 2025-01-01 when loaded; nothing later is ever read."""
import datetime as dt
import glob
import zoneinfo
from pathlib import Path

import numpy as np

from research.m1 import load as m1load

UTC = dt.timezone.utc
T0 = int(dt.datetime(2016, 1, 1, tzinfo=UTC).timestamp() * 1000)
T1 = int(dt.datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000)   # exclusive: HOLD never loaded
VAL0 = int(dt.datetime(2022, 1, 1, tzinfo=UTC).timestamp() * 1000)
NMIN = (T1 - T0) // 60000
TZ = {k: zoneinfo.ZoneInfo(v) for k, v in dict(NY="America/New_York", LON="Europe/London", SYD="Australia/Sydney",
                                                   TOK="Asia/Tokyo", HK="Asia/Hong_Kong", CET="Europe/Berlin",
                                                   UTC="UTC", SH="Asia/Shanghai").items()}
FXMET = {"EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "XAUUSD",
         "USDCNH"}

# ---------------------------------------------------------------- venue specs (HYPOTHESES_M section 1)
# ECN: commission 0.4 bp round trip, floor touch spread in price units
ECN_FLOOR = {"EURUSD": 1e-5, "USDJPY": 1e-3, "USDCHF": 1e-5, "GBPUSD": 1e-5, "USDCAD": 1e-5, "AUDUSD": 1e-5,
             "EURJPY": 3e-3, "GBPJPY": 3e-3, "USDCNH": 1e-4}
# futures: (tick price units, multiplier, commission per side in contract ccy, ccy->USD (IS, VAL))
FUT = {"XAUUSD": (.10, 100, 2.5, (1, 1)), "US30": (1.0, 5, 2.5, (1, 1)), "US500": (.25, 50, 2.5, (1, 1)),
       "USTEC": (.25, 20, 2.5, (1, 1)), "UK100": (.5, 10, 2.0, (1.30, 1.25)), "AUS200": (1.0, 25, 4.0, (.74, .67)),
       "HK50": (1.0, 50, 40.0, (1 / 7.8, 1 / 7.8)), "DE40": (1.0, 25, 2.5, (1.15, 1.08)),
       "XTIUSD": (.01, 1000, 2.5, (1, 1)), "BTCUSD": (5.0, 5, 11.0, (1, 1))}

_rows = {}


def _cnh():
    from research.bars import decode_zbars
    mid = np.full(NMIN, np.nan); spr = np.full(NMIN, np.nan)
    for f in sorted(glob.glob("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/USDCNH/m1/*.zbars")):
        if Path(f).name[:4] > "2024":
            continue
        a = decode_zbars(Path(f))
        a = a[(a[:, 0] >= T0) & (a[:, 0] < T1)]
        if a.size:
            k = (a[:, 0] - T0) // 60000
            mid[k] = a[:, 4] / 1e5 + 0.000293 / 2
            spr[k] = 0.000293
    return mid, spr


def row(sym):
    if sym not in _rows:
        if sym == "USDCNH":
            mid, spr = _cnh()
        else:
            z = m1load(sym)
            keep = (z["ts"] >= T0) & (z["ts"] < T1)
            ts = z["ts"][keep]; c = z["c"][keep]; ca = z["ca"][keep]
            k = (ts - T0) // 60000
            mid = np.full(NMIN, np.nan); spr = np.full(NMIN, np.nan)
            mid[k] = (c + ca) / 2; spr[k] = np.maximum(ca - c, 0)
            del z
        ok = ~np.isnan(mid)
        ff = np.maximum.accumulate(np.where(ok, np.arange(NMIN), -1))
        _rows[sym] = (mid, spr, ff)
    return _rows[sym]


def drop(sym):
    _rows.pop(sym, None)


def loc_ms(d, hh, mm=0, tz="NY"):
    return int(dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=TZ[tz]).timestamp() * 1000)


def quote_k(sym, ms, back=10):
    _, _, ff = row(sym)
    k = (np.asarray(ms, dtype=np.int64) - T0) // 60000 - 1
    out = np.full(k.shape, -1, dtype=np.int64)
    ok = (k >= 0) & (k < NMIN)
    j = np.full(k.shape, -1, dtype=np.int64); j[ok] = ff[k[ok]]
    good = ok & (j >= 0) & (k - j <= back)
    out[good] = j[good]
    return out


def price(sym, ms, back=10):
    mid = row(sym)[0]
    k = quote_k(sym, ms, back)
    return np.where(k >= 0, mid[np.maximum(k, 0)], np.nan)


def _fx_era(ms):
    return np.where(np.asarray(ms) >= VAL0, 1, 0)


def costs(sym, a, b, sa, sb, ms_in):
    """round-trip bp at quotes with mid a, b and IC spreads sa, sb -> (lower, upper, ic)."""
    ic_hs = 0.5 * (sa / a + sb / b) * 1e4
    ic = ic_hs + (0.6 if sym in FXMET else 0.0)
    if sym in FUT:
        tick, mult, comm, fx = FUT[sym]
        fxv = np.where(_fx_era(ms_in) == 1, fx[1], fx[0])
        comm_bp = 2 * comm * fxv / (mult * a) * 1e4
        lo = 0.5 * (tick / a + tick / b) * 1e4 + comm_bp
        ic_sa = sa; ic_sb = sb
        up = 0.5 * (np.maximum(tick, ic_sa) / a + np.maximum(tick, ic_sb) / b) * 1e4 + comm_bp
    else:
        fl = ECN_FLOOR[sym]
        lo = 0.5 * (fl / a + fl / b) * 1e4 + 0.4
        up = 0.5 * (np.maximum(fl, sa) / a + np.maximum(fl, sb) / b) * 1e4 + 0.4
    return lo, up, ic


def legs(sym, side, ms_in, ms_out, back=10):
    """gross bp (log, side-signed) and costs at (ms_in, ms_out); arrays."""
    mid, spr, _ = row(sym)
    ka = quote_k(sym, ms_in, back); kb = quote_k(sym, ms_out, back)
    ok = (ka >= 0) & (kb >= 0) & (kb > ka)
    a = mid[np.maximum(ka, 0)]; b = mid[np.maximum(kb, 0)]
    sa = spr[np.maximum(ka, 0)]; sb = spr[np.maximum(kb, 0)]
    g = np.asarray(side, float) * np.log(b / a) * 1e4
    lo, up, ic = costs(sym, a, b, sa, sb, ms_in)
    nan = lambda x: np.where(ok, x, np.nan)
    return dict(gross=nan(g), lo=nan(lo), up=nan(up), ic=nan(ic), ok=ok)


def trades(sym, side, ms_in, ms_out, back=10, carry=None):
    """dict: ms_in, ms_out, side, gross, lo, up, ic, gross1, up1 (+1 min both quotes), ok. carry: bp per trade
    subtracted from gross (futures carry for overnight holds)."""
    ms_in = np.asarray(ms_in, dtype=np.int64); ms_out = np.asarray(ms_out, dtype=np.int64)
    side = np.broadcast_to(np.asarray(side, float), ms_in.shape).copy()
    r0 = legs(sym, side, ms_in, ms_out, back)
    r1 = legs(sym, side, ms_in + 60000, ms_out + 60000, back)
    c = np.zeros(ms_in.shape) if carry is None else carry
    ok = r0["ok"] & r1["ok"] & ~np.isnan(side) & (side != 0)
    out = dict(sym=sym, ms_in=ms_in[ok], ms_out=ms_out[ok], side=side[ok], gross=r0["gross"][ok] - c[ok],
               lo=r0["lo"][ok], up=r0["up"][ok], ic=r0["ic"][ok], gross1=r1["gross"][ok] - c[ok], up1=r1["up"][ok])
    return out


def cat(ts):
    """concatenate trade dicts of several symbols (a pooled rule)."""
    keys = ["ms_in", "ms_out", "side", "gross", "lo", "up", "ic", "gross1", "up1"]
    out = {k: np.concatenate([t[k] for t in ts]) for k in keys}
    out["sym"] = np.concatenate([np.full(len(t["ms_in"]), t["sym"]) for t in ts])
    return out


# ---------------------------------------------------------------- statistics
def cl_t(x, g):
    x = np.asarray(x, float); g = np.asarray(g)
    keep = ~np.isnan(x); x = x[keep]; g = g[keep]
    n = x.size
    if n < 3:
        return (x.mean() if n else np.nan), np.nan
    m = x.mean(); u, inv = np.unique(g, return_inverse=True)
    s = np.bincount(inv, weights=x - m); G = u.size
    if G < 2:
        return m, np.nan
    se = np.sqrt((s ** 2).sum() * G / (G - 1)) / n
    return m, (m / se if se > 0 else np.nan)


def day_of(ms):
    return np.asarray(ms, dtype=np.int64) // 86400000


def year_of(ms):
    return np.array([dt.datetime.fromtimestamp(int(x) / 1000, UTC).year for x in np.atleast_1d(ms)], dtype=int)


def bdays(d0, d1):
    d = d0; out = []
    while d <= d1:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def xmas(d, last=1):
    """24 Dec .. `last` Jan."""
    return (d.month == 12 and d.day >= 24) or (d.month == 1 and d.day <= last)


_nyoff = {}


def ny_minute(ms):
    ms = np.asarray(ms, dtype=np.int64)
    days = ms // 86400000
    for d in np.unique(days):
        if d not in _nyoff:
            t = dt.datetime.fromtimestamp(int(d) * 86400 + 43200, UTC).astimezone(TZ["NY"])
            _nyoff[d] = int(t.utcoffset().total_seconds() // 60)
    off = np.array([_nyoff[d] for d in days.ravel()]).reshape(days.shape) if days.size else days
    return ((ms // 60000) + off) % 1440


def in_roll(ms_in, ms_out, lo=16 * 60 + 45, hi=18 * 60 + 15):
    ms_in = np.asarray(ms_in, dtype=np.int64); ms_out = np.asarray(ms_out, dtype=np.int64)
    bad = np.zeros(ms_in.shape, bool)
    span = int(np.max(ms_out - ms_in)) if ms_in.size else 0
    for step in range(0, span + 1, 15 * 60000):
        t = np.minimum(ms_in + step, ms_out)
        m = ny_minute(t); bad |= (m > lo) & (m < hi)
    m = ny_minute(ms_out); bad |= (m > lo) & (m < hi)
    return bad
