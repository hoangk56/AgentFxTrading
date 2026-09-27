"""Rules for research/swing/swing.py. The first block are rules published before 2016 with their published
parameters, so the whole 2016-2026 cache is out of sample for them; anything tuned here says so.

Every rule returns swing.Signals for one symbol's bars (decided on the bar close). Stops are wide ATR stops: the
published rules mostly have none, but the lot is sized off the stop (risk-based, capital-independent), so a
trade needs one; SLK x ATR(20) is a catastrophic stop, not a tuned exit.
"""
import datetime

import numpy as np

from research.indicators import atr_sma, ema, prior_max, prior_min, rsi, sma
from research.swing.swing import Signals, m1

NAN = np.nan


def _atr(b, n=20):
    return atr_sma(b.h, b.l, b.c, n)


def _prev(x, k=1, fill=np.nan):
    out = np.full(len(x), fill, dtype=float)
    out[k:] = x[:-k]
    return out


def _dates(b, symbol):
    """UTC date of each bar's last M1 row."""
    ts = m1(symbol)["ts"]
    return [datetime.datetime.fromtimestamp(int(ts[j]) / 1000, datetime.timezone.utc).date() for j in b.last]


# ---------------------------------------------------------------- Connors RSI(2) (Connors & Alvarez 2008/2009)
def rsi2(b, lo=10.0, hi=90.0, trend=200, exit_ma=5, shorts=False, slk=3.0, **_):
    """Long: close > SMA(trend) and RSI(2) < lo; exit on a close above SMA(exit_ma). Short (optional): mirror."""
    r = rsi(b.c, 2)
    st, ex = sma(b.c, trend), sma(b.c, exit_ma)
    a = _atr(b)
    with np.errstate(invalid="ignore"):
        le = (b.c > st) & (r < lo)
        se = (b.c < st) & (r > hi) if shorts else np.zeros(len(b), bool)
        lx = b.c > ex
        sx = b.c < ex
    strength = np.where(le, lo - r, np.where(se, r - hi, 0.0)) + 1.0
    return Signals(le, se, slk * a, np.nan_to_num(strength, nan=1.0), lx, sx)


def cum_rsi2(b, lo=35.0, trend=200, days=2, exit_rsi=65.0, slk=3.0, **_):
    """Connors 'Cumulative RSI': long when close > SMA(200) and the sum of RSI(2) over `days` days < lo;
    exit when RSI(2) > exit_rsi."""
    r = rsi(b.c, 2)
    cum = sum(_prev(r, k, np.nan) if k else r for k in range(days))
    st = sma(b.c, trend)
    with np.errstate(invalid="ignore"):
        le = (b.c > st) & (cum < lo)
        lx = r > exit_rsi
    return Signals(le, np.zeros(len(b), bool), slk * _atr(b), np.nan_to_num(lo - cum + 1, nan=1.0), lx, None)


def tps(b, trend=200, lo=25.0, exit_rsi=70.0, slk=3.0, **_):
    """Connors 'TPS' (trend, pullback, scale-in), capped at 3 units: close > SMA(200) and RSI(2) < lo two days
    running opens unit 1; each later close below the previous entry while still in the pullback adds a unit
    (1x, 1.5x, 2x of the default lot); exit all when RSI(2) > exit_rsi."""
    r = rsi(b.c, 2)
    st = sma(b.c, trend)
    n = len(b)
    le = np.zeros(n, bool)
    size = np.ones(n)
    units, last_px = 0, np.inf
    for i in range(1, n):
        if not np.isfinite(st[i]) or not np.isfinite(r[i]):
            continue
        if units and r[i] > exit_rsi:
            units, last_px = 0, np.inf
            continue
        if units == 0:
            if b.c[i] > st[i] and r[i] < lo and r[i - 1] < lo:
                le[i], size[i], units, last_px = True, 1.0, 1, b.c[i]
        elif units < 3 and b.c[i] < last_px:
            units += 1
            le[i], size[i], last_px = True, (1.0, 1.5, 2.0)[units - 1], b.c[i]
    with np.errstate(invalid="ignore"):
        lx = r > exit_rsi
    return Signals(le, np.zeros(n, bool), slk * _atr(b), None, lx, None, size=size)


# ---------------------------------------------------------------- Double 7s (Connors & Alvarez 2009)
def double7(b, n=7, trend=200, slk=3.0, **_):
    """Long: close > SMA(200) and the close is the lowest close of n days; exit on the highest close of n days."""
    st = sma(b.c, trend)
    lowc = prior_min(b.c, n - 1)
    highc = prior_max(b.c, n - 1)
    with np.errstate(invalid="ignore"):
        le = (b.c > st) & (b.c <= lowc)
        lx = b.c >= highc
    return Signals(le, np.zeros(len(b), bool), slk * _atr(b), None, lx, None)


# ---------------------------------------------------------------- IBS (internal bar strength)
def ibs(b, lo=0.2, hi=0.8, trend=0, shorts=False, slk=3.0, **_):
    """IBS = (C - L) / (H - L). Long when IBS < lo, exit on the next close with IBS > hi or after one bar
    (published version: hold to the next close). Optional SMA trend filter and short mirror."""
    rng = b.h - b.l
    with np.errstate(invalid="ignore", divide="ignore"):
        x = np.where(rng > 0, (b.c - b.l) / rng, 0.5)
    le = x < lo
    se = x > hi if shorts else np.zeros(len(b), bool)
    if trend:
        st = sma(b.c, trend)
        with np.errstate(invalid="ignore"):
            le &= b.c > st
            se &= b.c < st
    ones = np.ones(len(b), bool)
    return Signals(le, se, slk * _atr(b), np.nan_to_num(lo - x + 0.05, nan=0.05), ones, ones)


# ---------------------------------------------------------------- N down days
def down_days(b, n=3, trend=200, slk=3.0, **_):
    """Long after n consecutive lower closes above SMA(200); exit on the first higher close."""
    d = np.r_[False, b.c[1:] < b.c[:-1]]
    run = np.zeros(len(b), int)
    for i in range(1, len(b)):
        run[i] = run[i - 1] + 1 if d[i] else 0
    st = sma(b.c, trend)
    with np.errstate(invalid="ignore"):
        le = (run >= n) & (b.c > st)
    lx = np.r_[False, b.c[1:] > b.c[:-1]]
    return Signals(le, np.zeros(len(b), bool), slk * _atr(b), run.astype(float), lx, None)


# ---------------------------------------------------------------- turn of the month (Lakonishok & Smidt 1988)
def tom(b, symbol=None, before=1, after=3, slk=3.0, **_):
    """Long at the close `before`+1 trading days before month end (holding the last `before` trading day(s)),
    exit at the close of the `after`-th trading day of the new month."""
    dates = _dates(b, symbol)
    n = len(b)
    months = np.array([d.year * 12 + d.month for d in dates])
    first = np.flatnonzero(np.r_[True, months[1:] != months[:-1]])
    le, lx = np.zeros(n, bool), np.zeros(n, bool)
    for f in first[1:]:
        e = f - before - 1
        if e >= 0:
            le[e] = True
        x = f + after - 1
        if x < n:
            lx[x] = True
    return Signals(le, np.zeros(n, bool), slk * _atr(b), None, lx, None)


# ---------------------------------------------------------------- crypto time-series momentum
def tsmom(b, look=7, shorts=False, weekday=None, symbol=None, slk=3.0, **_):
    """Long when the close is above the close `look` bars ago (short below it when shorts). With weekday set,
    only enter on that weekday's bar (weekly rebalance); the 5-day cap is the exit."""
    past = _prev(b.c, look)
    with np.errstate(invalid="ignore"):
        le = b.c > past
        se = (b.c < past) if shorts else np.zeros(len(b), bool)
    if weekday is not None:
        wd = np.array([d.weekday() for d in _dates(b, symbol)])
        le &= wd == weekday
        se &= wd == weekday
    with np.errstate(invalid="ignore", divide="ignore"):
        strength = np.abs(b.c / past - 1)
    return Signals(le, se, slk * _atr(b), np.nan_to_num(strength, nan=0.0) + 1e-9, None, None)


def trend(b, look=28, flip_exit=True, shorts=False, slk=3.0, ma=0, **_):
    """Time-series trend: long while close > close[look] (and > SMA(ma) when ma), entered on every bar that
    qualifies (the bot's cap turns this into up to 3 staggered units); with flip_exit, all longs close on the
    first close back below close[look]. Shorts mirror it."""
    past = _prev(b.c, look)
    with np.errstate(invalid="ignore"):
        up, dn = b.c > past, b.c < past
        if ma:
            m = sma(b.c, ma)
            up &= b.c > m
            dn &= b.c < m
    se = dn if shorts else np.zeros(len(b), bool)
    with np.errstate(invalid="ignore", divide="ignore"):
        strength = np.nan_to_num(np.abs(b.c / past - 1), nan=0.0) + 1e-9
    return Signals(up, se, slk * _atr(b), strength, (~up) if flip_exit else None, (~dn) if flip_exit else None)


def donchian(b, n=20, exit_n=10, shorts=False, slk=3.0, **_):
    """Donchian breakout: long on a close above the prior n-bar high, exit on a close below the prior exit_n-bar
    low (turtle-style); shorts mirror."""
    hh, ll = prior_max(b.h, n), prior_min(b.l, n)
    xl, xh = prior_min(b.l, exit_n), prior_max(b.h, exit_n)
    with np.errstate(invalid="ignore"):
        le = b.c > hh
        se = (b.c < ll) if shorts else np.zeros(len(b), bool)
        lx = b.c < xl
        sx = b.c > xh
    a = _atr(b)
    with np.errstate(invalid="ignore", divide="ignore"):
        strength = np.nan_to_num(np.where(le, (b.c - hh) / a, (ll - b.c) / a), nan=0.0) + 1e-9
    return Signals(le, se, slk * a, strength, lx, sx)


def carry(b, symbol=None, thr=0.01, ma=50, trend=True, slk=3.0, **_):
    """FX carry (Lustig, Roussanov & Verdelhan 2011), optionally with a trend filter (Burnside et al.): long
    when the base rate exceeds the quote rate by more than thr (annual) [and close > SMA(ma)], short in the
    mirror case; with the filter, exit when the close crosses back through SMA(ma). Rates: research/swing/rates
    (FRED, as known on the bar's date)."""
    from research.swing.rates import FX_CCY, rate
    base, quote = FX_CCY[symbol]
    ts = m1(symbol)["ts"]
    diff = np.array([rate(base, int(ts[j])) - rate(quote, int(ts[j])) for j in b.last])
    n = len(b)
    le, se = diff > thr, diff < -thr
    lx = sx = None
    if trend:
        m = sma(b.c, ma)
        with np.errstate(invalid="ignore"):
            le &= b.c > m
            se &= b.c < m
            lx, sx = b.c < m, b.c > m
    return Signals(le, se, slk * _atr(b), np.abs(diff) + 1e-9, lx, sx)


# +1 = the pair rises when the non-USD currency strengthens (EURUSD), -1 = it falls (USDCHF).
FX_DIR = {"EURUSD": 1, "GBPUSD": 1, "AUDUSD": 1, "NZDUSD": 1, "USDCHF": -1, "USDCAD": -1, "USDJPY": -1}
HOME_SESSION = {"EUR": (7, 12), "GBP": (7, 12), "CHF": (7, 12)}


def session_fx(b, symbol=None, eu=True, us=True, slk=4.0, eu_hours=(7, 12), us_hours=(13, 20), **_):
    """Home-hours depreciation (Ranaldo 2009; Breedon & Ranaldo 2013) on H1 bars (UTC): the European currency
    is sold against USD from eu_hours[0] to eu_hours[1] UTC and bought back / held long over US hours
    us_hours (USD weakens in its home hours). One position per window, flat outside the windows (no swap)."""
    d = FX_DIR[symbol]
    hour = ((b.t // 3_600_000) % 24).astype(int)          # hour at which each H1 bar opens
    close_hour = (hour + 1) % 24                           # decision time = bar close
    n = len(b)
    le, se = np.zeros(n, bool), np.zeros(n, bool)
    lx, sx = np.zeros(n, bool), np.zeros(n, bool)
    wd = ((b.t // 86_400_000 + 3) % 7)                     # 0 = Monday
    week = wd < 5
    if eu:
        start = (close_hour == eu_hours[0]) & week
        (se if d > 0 else le)[start] = True
        end = close_hour == eu_hours[1]
        (sx if d > 0 else lx)[end] = True
    if us:
        start = (close_hour == us_hours[0]) & week
        (le if d > 0 else se)[start] = True
        end = close_hour == us_hours[1]
        (lx if d > 0 else sx)[end] = True
    return Signals(le, se, slk * _atr(b), None, lx, sx)


def ny_offset_ms(ts: np.ndarray) -> np.ndarray:
    """New York's UTC offset in ms (negative) at each timestamp, resolved per UTC hour."""
    from zoneinfo import ZoneInfo
    ny, hour_ms = ZoneInfo("America/New_York"), 3_600_000
    h = np.asarray(ts, np.int64) // hour_ms
    h0 = int(h.min())
    offs = np.array([datetime.datetime.fromtimestamp(x * 3600, ny).utcoffset().total_seconds() * 1000
                     for x in range(h0, int(h.max()) + 1)], np.int64)
    return offs[h - h0]


def _ny_minutes(t_ms: np.ndarray) -> np.ndarray:
    """Minutes after New York midnight for each UTC ms timestamp (DST-aware)."""
    loc = np.asarray(t_ms, np.int64) + ny_offset_ms(np.asarray(t_ms, np.int64))
    return ((loc // 60_000) % 1440).astype(int), (loc // 86_400_000).astype(int)


def _daily_filter_on(b, symbol, ma):
    """close > SMA(ma) of the D1 bars, as known at each intraday bar (last D1 bar closed before it)."""
    from research.swing.swing import bars as _bars, D1
    d = _bars(symbol, *D1)
    ok = d.c > sma(d.c, ma)
    d_end = d.t + 86_400_000       # D1 bar closes 24h after it opens (stub-merged bars close later; conservative)
    k = np.searchsorted(d_end, b.t, side="right") - 1
    out = np.zeros(len(b), bool)
    valid = k >= 0
    out[valid] = ok[k[valid]]
    return out


def day_long(b, symbol=None, entry_ny=18 * 60 + 15, exit_ny=15 * 60 + 45, ma=200, slk=3.0, **_):
    """Long an index from entry_ny (after the 17:00 New York rollover and the reopen) to exit_ny the next day
    (before the rollover): no swap is ever charged. The exit also fires on the last bar before any market close
    (holiday early closes -- a bot knows them from the symbol's market hours), so no position crosses 17:00 NY.
    Optional D1 trend filter close > SMA(ma) (ma=0: none). Bars must be M15: decisions at a bar close."""
    mins, _ = _ny_minutes(b.t + 15 * 60_000)          # NY time at each bar's close
    le = mins == entry_ny
    gap_after = np.r_[(b.t[1:] - b.t[:-1]) > 35 * 60_000, True]
    lx = (mins == exit_ny) | (gap_after & (mins < entry_ny) & (mins > 9 * 60))
    wd = (((b.t + 15 * 60_000) // 86_400_000 + 3) % 7)
    le &= wd != 5                                      # no Saturday-UTC entries (none exist anyway)
    if ma:
        le &= _daily_filter_on(b, symbol, ma)
    a = atr_sma(b.h, b.l, b.c, 20 * 96) if len(b) > 20 * 96 else _atr(b)   # ~20-day ATR of M15 bars
    return Signals(le, np.zeros(len(b), bool), slk * a * np.sqrt(96), None, lx, None)


def gotobi_days(first, last):
    """The 5th/10th/15th/20th/25th and the month's last day in [first, last], a weekend day moved to the Friday
    before (Japanese holidays not modelled)."""
    out, y, m = set(), first.year, first.month
    while (y, m) <= (last.year, last.month):
        nxt = datetime.date(y + (m == 12), m % 12 + 1, 1)
        for d in [datetime.date(y, m, k) for k in (5, 10, 15, 20, 25)] + [nxt - datetime.timedelta(days=1)]:
            while d.weekday() >= 5:
                d -= datetime.timedelta(days=1)
            if first <= d <= last:
                out.add(d)
        y, m = nxt.year, nxt.month
    return sorted(out)


def _h1_atr_on(b, symbol, n=20):
    """ATR(n) of H1 bars as known at each bar of `b` (the last H1 bar closed at or before the bar's close)."""
    from research.swing.swing import bars as _bars, H1 as _H1
    h = _bars(symbol, *_H1)
    a = atr_sma(h.h, h.l, h.c, n)
    k = np.searchsorted(h.t + 3_600_000, b.t + (b.t[1] - b.t[0] if len(b) > 1 else 0), side="right") - 1
    out = np.full(len(b), np.nan)
    ok = k >= 0
    out[ok] = a[k[ok]]
    return out


def gotobi_nominal(first, last):
    """{moved gotobi date: nominal label} with labels "5", "10", "15", "20", "25", "last"."""
    import datetime as _dt
    out, y, m = {}, first.year, first.month
    while (y, m) <= (last.year, last.month):
        nxt = _dt.date(y + (m == 12), m % 12 + 1, 1)
        for lab, d in [(str(k), _dt.date(y, m, k)) for k in (5, 10, 15, 20, 25)] + [("last", nxt - _dt.timedelta(days=1))]:
            while d.weekday() >= 5:
                d -= _dt.timedelta(days=1)
            if first <= d <= last:
                out[d] = lab
        y, m = nxt.year, nxt.month
    return out


def gotobi(b, symbol=None, long_leg=True, short_leg=True, slk=3.0, entry_utc=18 * 60, fix_utc=55, end_utc=2 * 60 + 55,
           day_sizes=None, **_):
    """N2 gotobi (USDJPY), the removed lab's literature.gotobi on UTC M5 bars: on a gotobi day d, long from
    03:00 Tokyo (18:00 UTC on d-1; the first bar after the weekend open when that is closed) to the 09:55 Tokyo fix
    (00:55 UTC on d), then short from the fix to 11:55 Tokyo (02:55 UTC); stop 3 x ATR20(H1)."""
    import datetime as _dt
    step = 5 * 60_000
    close = b.t + step
    day0 = _dt.date.fromtimestamp(0)
    first = (_dt.datetime.fromtimestamp(int(b.t[0]) / 1000, _dt.timezone.utc) + _dt.timedelta(days=2)).date()
    last = _dt.datetime.fromtimestamp(int(b.t[-1]) / 1000, _dt.timezone.utc).date()
    n = len(b)
    le, se, lx, sx = (np.zeros(n, bool) for _ in range(4))
    size = np.ones(n) if day_sizes else None
    labels = gotobi_nominal(first, last) if day_sizes else {}
    for d in gotobi_days(first, last):
        dm = (d - day0).days * 86_400_000
        t_long, t_fix, t_end = dm - 86_400_000 + entry_utc * 60_000, dm + fix_utc * 60_000, dm + end_utc * 60_000
        i_long = int(np.searchsorted(close, t_long, side="left"))
        i_fix = int(np.searchsorted(close, t_fix, side="left"))
        i_end = int(np.searchsorted(close, t_end, side="left"))
        if i_end >= n or not (i_long < i_fix < i_end):
            continue
        if long_leg:
            le[i_long] = True
            lx[i_fix] = True
        if short_leg:
            se[i_fix] = True
            sx[i_end] = True
        if day_sizes:
            size[i_long] = size[i_fix] = day_sizes.get(labels.get(d, ""), 1.0)
    return Signals(le, se, slk * _h1_atr_on(b, symbol), None, lx, sx, size=size)


def _local_minutes(t_ms, tz_name):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(tz_name)
    t_ms = np.asarray(t_ms, np.int64)
    h = t_ms // 3_600_000
    hu, inv = np.unique(h, return_inverse=True)
    off = np.array([int(datetime.datetime.fromtimestamp(int(x) * 3600, tz).utcoffset().total_seconds() * 1000) for x in hu])
    return ((t_ms + off[inv]) // 60_000 % 1440).astype(int)


def fix_window(b, symbol=None, windows=((690, 720),), side=-1, tz="Europe/London", slk=3.0, **_):
    """Trade `side` over fixed local-time windows [start, end) minutes after local midnight (default: short the
    30 minutes into the 12:00 London silver auction). M5 bars; weekdays only; stop slk x ATR20(H1)."""
    step = 5 * 60_000
    mins = _local_minutes(b.t + step, tz)          # local time at each bar's close
    wd = ((b.t + step) // 86_400_000 + 3) % 7
    n = len(b)
    ent, ex = np.zeros(n, bool), np.zeros(n, bool)
    for a, e in windows:
        ent |= (mins == a) & (wd < 5)
        ex |= mins == e
    z = np.zeros(n, bool)
    le, se = (ent, z) if side > 0 else (z, ent)
    lx, sx = (ex, None) if side > 0 else (None, ex)
    return Signals(le, se, slk * _h1_atr_on(b, symbol), None, lx, sx)


C4_DAY_SIZES = {"20": 2.0, "25": 2.0, "15": 1.0, "5": 0.5, "10": 0.5, "last": 0.5}

RULES = {"rsi2": rsi2, "cum_rsi2": cum_rsi2, "tps": tps, "double7": double7, "ibs": ibs, "down_days": down_days,
         "tom": tom, "tsmom": tsmom}

