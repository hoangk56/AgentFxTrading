"""Daily premium p = BtcTurk USDTTRY price at 06:00 UTC / Dukascopy USDTRY mid at the first tick >= 06:00 - 1, and
the day table used by the backtest. LABEL_START: True if a BtcTurk candle label is its start (set from align.py).
Output: research/data/usdtry_premium/days.npz (kept out of results/). No strategy return here."""
import datetime as dt
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load  # noqa: E402

LABEL_START = True  # set from align_h1.py (see STREAM_TRY.md)
START = dt.date(2018, 7, 10)


def build():
    t, o, h, l, c, v = load.btcturk_1h()
    end_of = t + 3600 if LABEL_START else t  # time at which the candle's close is printed
    rows = []
    d = START
    while d < dt.date(2025, 1, 1):
        if d.weekday() < 5:
            r = load.duka_hour(d)
            if r is not None and len(r[0]):
                ms, a, b = r
                f0, f1, f2 = load.first_at(ms, a, b, 0), load.first_at(ms, a, b, 60), load.first_at(ms, a, b, 120)
                if f0 is not None and f1 is not None:
                    six = int(dt.datetime(d.year, d.month, d.day, 6, tzinfo=dt.UTC).timestamp())
                    k = int(np.searchsorted(end_of, six, side="right")) - 1
                    btc = c[k] if k >= 0 and end_of[k] >= six - 3 * 3600 else np.nan
                    mid0 = (f0[0] + f0[1]) / 2
                    rows.append((d.toordinal(), mid0, f1[0], f1[1], f2[0] if f2 else np.nan, f2[1] if f2 else np.nan,
                                 btc, btc / mid0 - 1 if btc == btc else np.nan))
        d += dt.timedelta(days=1)
    a = np.array(rows)
    return dict(day=a[:, 0].astype(int), mid0=a[:, 1], ask1=a[:, 2], bid1=a[:, 3], ask2=a[:, 4], bid2=a[:, 5],
                btc=a[:, 6], p=a[:, 7])


def btc_at(t, c, end_of, ts):
    k = int(np.searchsorted(end_of, ts, side="right")) - 1
    return c[k] if k >= 0 and end_of[k] >= ts - 3 * 3600 else np.nan


def build_h1():
    """Amendment A price model: Dukascopy hourly candles. mid0 = 06:00 candle open mid; ask1 / bid1 = 07:00 candle
    open (entry / exit prices); ask2 / bid2 = 08:00 candle open (one step late). Amendment B: months without an ASK
    file use ask = bid x (1 + median 07:00 relative spread of that year's ASK months, else the previous year's)."""
    t, o, h, l, c, v = load.btcturk_1h()
    end_of = t + 3600 if LABEL_START else t
    H = load.duka_h1()
    tb, ob, vb = H["BID"][0], H["BID"][1], H["BID"][5]
    ta, oa = (H["ASK"][0], H["ASK"][1]) if "ASK" in H else (np.empty(0, int), np.empty(0))
    ia = {int(x): i for i, x in enumerate(ta)}
    ib = {int(x): i for i, x in enumerate(tb)}
    # median relative spread at 07:00 per year from real ASK data
    sp = {}
    for x, i in ib.items():
        if (x % 86400) == 7 * 3600 and x in ia and vb[i] > 0:
            sp.setdefault(dt.datetime.fromtimestamp(x, dt.UTC).year, []).append(oa[ia[x]] / ob[i] - 1)
    med = {y: float(np.median(v_)) for y, v_ in sp.items()}

    def ask_of(ts, j):
        if ts in ia:
            return oa[ia[ts]], 0
        y = dt.datetime.fromtimestamp(ts, dt.UTC).year
        s_ = med.get(y, med.get(y - 1, np.nan))
        return ob[j] * (1 + s_), 1

    rows = []
    d = START
    while d < dt.date(2025, 1, 1):
        if d.weekday() < 5:
            six = int(dt.datetime(d.year, d.month, d.day, 6, tzinfo=dt.UTC).timestamp())
            j0, j1, j2 = ib.get(six), ib.get(six + 3600), ib.get(six + 7200)
            if j0 is not None and j1 is not None and vb[j0] > 0 and vb[j1] > 0:
                a0, f0 = ask_of(six, j0)
                a1, f1 = ask_of(six + 3600, j1)
                a2, b2 = (ask_of(six + 7200, j2)[0], ob[j2]) if j2 is not None and vb[j2] > 0 else (np.nan, np.nan)
                mid0 = (ob[j0] + a0) / 2
                btc = btc_at(t, c, end_of, six)
                rows.append((d.toordinal(), mid0, a1, ob[j1], a2, b2, btc,
                             btc / mid0 - 1 if btc == btc else np.nan, f1))
        d += dt.timedelta(days=1)
    a = np.array(rows)
    return dict(day=a[:, 0].astype(int), mid0=a[:, 1], ask1=a[:, 2], bid1=a[:, 3], ask2=a[:, 4], bid2=a[:, 5],
                btc=a[:, 6], p=a[:, 7], ask_fallback=a[:, 8].astype(int), med_spread=np.array(sorted(med.items())))


def episodes(sig, gap=5):
    """Episode id per trading-day index (-1 where no signal): runs of signal days, gaps <= `gap` trading days merged."""
    ep = -np.ones(len(sig), int)
    cur, last = -1, -10**9
    for i in np.flatnonzero(sig):
        if i - last - 1 > gap:  # more than `gap` non-signal trading days in between -> new episode
            cur += 1
        ep[i] = cur
        last = i
    return ep


if __name__ == "__main__":
    D = build_h1()
    np.savez(os.path.join(load.ROOT, "days.npz"), **D)
    print("days", len(D["day"]), "with premium", np.isfinite(D["p"]).sum())
